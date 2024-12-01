import csv
import logging

from django.core.files.storage import default_storage
from django.db.models import Prefetch, Sum
from django.db.models.functions import TruncMonth
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from sales.filters import OrderFilter
from sales.models import Order, OrderItem
from sales.serializers import OrderSerializer
from sales.tasks import import_data_task

logger = logging.getLogger(__name__)


class DataImportAPI(APIView):
    """
    API endpoint to initiate data import task with file upload.
    """
    def post(self, request, *args, **kwargs):
        try:
            platform = request.data.get('platform')
            uploaded_file = request.FILES.get('file')  # Get the uploaded file

            if not platform or not uploaded_file:
                return Response(
                    {"error": "Platform and a file must be provided."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Save the file temporarily
            file_path = default_storage.save('tmp/' + uploaded_file.name, uploaded_file)

            # Trigger the Celery task
            import_data_task.delay(platform, file_path)
            response = {
                "message": "Data import task has been initiated with the uploaded file."
            }

        except Exception as e:
            error_message = f"Error importing data: {str(e)}"
            logger.error(error_message)
            response = {
                "error": error_message
            }
        return Response(response)


class MonthlySalesVolume(APIView):
    def get(self, request):
        try:
            response = OrderItem.objects.annotate(
                month=TruncMonth('order__order_date')).values(
                'month').annotate(
                total_quantity=Sum('quantity_sold')).order_by(
                'month'
            )
        except Exception as e:
            error_message = f"Error fetching monthly sales volume: {str(e)}"
            logger.error(error_message)
            response = {
                "error": error_message
            }
        return Response(response)


class MonthlyRevenue(APIView):
    def get(self, request):
        try:
            response = OrderItem.objects.annotate(
                month=TruncMonth('order__order_date')).values(
                'month').annotate(
                total_revenue=Sum('total_sale_value')).order_by(
                'month'
            )
        except Exception as e:
            error_message = f"Error fetching monthly revenue: {str(e)}"
            logger.error(error_message)
            response = {
                "error": error_message
            }
        return Response(response)


class OrderListView(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = OrderFilter

    def get_queryset(self):
        # Using select_related for single-depth relationships
        # Using prefetch_related for deeper relationships or many-to-many relationships
        queryset =  Order.objects.select_related(
            'customer', 'platform').prefetch_related(
            Prefetch(
                'order_items',
                queryset=OrderItem.objects.select_related('product')
            ),
            'delivery').order_by(
            'order_id'
        )
        return queryset

    def export_to_csv(self):
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="orders.csv"'},
        )
        fieldnames = [
            'order_id', 'order_date', 'customer_id', 'platform_id',
            'product_id', 'product_name', 'category', 'quantity_sold',
            'selling_price', 'total_sale_value', 'delivery_id',
            'delivery_address', 'delivery_date', 'delivery_status',
            'delivery_partner'  # base fields
        ]

        # Dynamically determine additional field names from data
        dynamic_fields = set()
        queryset = self.filter_queryset(self.get_queryset())
        for order in queryset:
            platform_order_fields = order.platform.platform_config.get(
                'platform_data_field_mapping', {}).values()
            platform_delivery_fields = order.platform.platform_config.get(
                'delivery_data_field_mapping', {}).values()
            dynamic_fields.update(platform_order_fields)
            dynamic_fields.update(platform_delivery_fields)

        # Update fieldnames list
        fieldnames.extend(dynamic_fields)

        writer = csv.DictWriter(response, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()

        # Reset the query to iterate for writing rows
        queryset = self.filter_queryset(self.get_queryset())
        for order in queryset:
            for item in order.order_items.all():
                row_data = {
                    'order_id': order.order_id,
                    'order_date': order.order_date,
                    'customer_id': order.customer.customer_id,
                    'platform_id': order.platform.platform_id,
                    'product_id': item.product.product_id,
                    'product_name': item.product.product_name,
                    'category': item.product.category,
                    'quantity_sold': item.quantity_sold,
                    'selling_price': item.selling_price,
                    'total_sale_value': item.total_sale_value,
                    'delivery_id': order.delivery.delivery_id,
                    'delivery_address': order.delivery.delivery_address,
                    'delivery_date': order.delivery.delivery_date,
                    'delivery_status': order.delivery.delivery_status,
                    'delivery_partner': order.delivery.delivery_partner,
                }
                # Append dynamic data
                row_data.update(order.platform_data)
                row_data.update(order.delivery.delivery_data)
                writer.writerow(row_data)

        return response

    def list(self, request, *args, **kwargs):
        try:
            export = request.query_params.get('export', False)
            export = True if export == 'true' else False
            if export:
                response = self.export_to_csv()
            else:
                response = super().list(request, *args, **kwargs)
        except Exception as e:
            error_message = f"Error fetching orders: {str(e)}"
            logger.error(error_message)
            response = Response({
                "error": error_message
            })
        return response


class SummaryMetricsAPI(APIView):
    def get(self, request):
        try:
            total_revenue = OrderItem.objects.aggregate(Sum('total_sale_value'))
            total_orders = Order.objects.count()
            total_products_sold = OrderItem.objects.aggregate(
                total_sold=Sum('quantity_sold'))
            canceled_orders_percentage = (
                Order.objects.filter(delivery__delivery_status='Cancelled').count() /
                float(Order.objects.count()) * 100
            )

            response = {
                'total_revenue': total_revenue,
                'total_orders': total_orders,
                'total_products_sold': total_products_sold['total_sold'],
                'canceled_order_percentage': canceled_orders_percentage
            }
        except Exception as e:
            error_message = f"Error fetching summary metrics: {str(e)}"
            logger.error(error_message)
            response = {
                "error": error_message
            }
        return Response(response)
