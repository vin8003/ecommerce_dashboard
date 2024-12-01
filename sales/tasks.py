import csv
from celery import shared_task
from sales.models import Customer, Product, Order, OrderItem, Delivery, Platform
from datetime import datetime
from django.db import transaction
from django.conf import settings
from django.core.files.storage import default_storage

@shared_task(bind=True, max_retries=3)
def import_data_task(self, platform, file_path):
    """
    Celery task to import data from CSV files for different platforms.
    """
    try:
        platform_instance = Platform.objects.get(platform_name__iexact=platform)
    except Platform.DoesNotExist:
        raise Exception(f"Platform '{platform}' not configured.")

    try:
        import_platform_data(platform_instance, file_path)
    except Exception as e:
        self.retry(exc=e, max_retries=3)

def import_platform_data(platform, file_path):
    """
    Imports data for a specific platform from a CSV file using optimized bulk operations.
    """
    platform_name = platform.platform_name
    platform_config = platform.platform_config

    try:
        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            batch_size = platform_config.get('batch_size', 1000)

            # Initialize data collections
            customers_data = {}
            products_data = {}
            orders_data = []
            order_items_data = []
            deliveries_data = []

            count = 0

            for row in reader:
                field_mapping = platform_config.get('field_mapping', {})
                customer_id = row.get(field_mapping.get('customer_id'))
                product_id = row.get(field_mapping.get('product_id'))

                # Collect customer data
                customers_data[customer_id] = {
                    'customer_id': customer_id,
                    'customer_name': row.get(field_mapping.get('customer_name')),
                    'contact_email': row.get(field_mapping.get('contact_email')),
                    'phone_number': row.get(field_mapping.get('phone_number')),
                }

                # Collect product data
                products_data[product_id] = {
                    'product_id': product_id,
                    'product_name': row.get(field_mapping.get('product_name')),
                    'category': row.get(field_mapping.get('product_category')),
                }

                # Parse dates
                order_date = parse_date(
                    row.get(field_mapping.get('order_date')),
                    platform_config.get('order_date_format')
                )
                delivery_date = parse_date(
                    row.get(field_mapping.get('delivery_date')),
                    platform_config.get('delivery_date_format')
                )

                # Collect order data
                orders_data.append({
                    'order_id': row.get(field_mapping.get('order_id')),
                    'customer_id': customer_id,
                    'platform_id': platform.platform_id,
                    'order_date': order_date,
                    'platform_data': extract_platform_data(platform_config, row),
                })

                # Collect order item data
                item_quantity = float(row.get(field_mapping.get('item_quantity'), 0))
                item_selling_price = float(row.get(field_mapping.get('item_selling_price'), 0))
                item_total_value = item_quantity * item_selling_price

                order_items_data.append({
                    'order_id': row.get(field_mapping.get('order_id')),
                    'product_id': product_id,
                    'quantity_sold': item_quantity,
                    'selling_price': item_selling_price,
                    'total_sale_value': item_total_value,
                })

                # Collect delivery data
                deliveries_data.append({
                    'order_id': row.get(field_mapping.get('order_id')),
                    'delivery_address': row.get(field_mapping.get('delivery_address')),
                    'delivery_date': delivery_date,
                    'delivery_status': row.get(field_mapping.get('delivery_status')),
                    'delivery_partner': row.get(field_mapping.get('delivery_partner')),
                    'delivery_data': extract_delivery_data(platform_config, row),
                })

                count += 1

                if count % batch_size == 0:
                    # Process batch
                    process_batch(customers_data, products_data, orders_data, order_items_data, deliveries_data)
                    # Reset data collections
                    customers_data = {}
                    products_data = {}
                    orders_data = []
                    order_items_data = []
                    deliveries_data = []

            # Process any remaining data
            if orders_data:
                process_batch(customers_data, products_data, orders_data, order_items_data, deliveries_data)

            print(f'Data imported for {platform_name.capitalize()}.')

    except Exception as e:
        # Handle exceptions and optionally log them
        print(f'Error importing data for {platform_name.capitalize()}: {e}')
    finally:
        default_storage.delete(file_path)

def process_batch(customers_data, products_data, orders_data, order_items_data, deliveries_data):
    """
    Processes a batch of data, performing bulk operations for customers, products, orders, order items, and deliveries.
    """
    with transaction.atomic():
        # Process customers
        customer_ids = list(customers_data.keys())
        existing_customers = {
            customer.customer_id: customer for customer in Customer.objects.filter(
                customer_id__in=customer_ids)
        }

        new_customers = []

        for cid, data in customers_data.items():
            if cid not in existing_customers:
                new_customers.append(Customer(**data))

        Customer.objects.bulk_create(new_customers)

        # Process products
        product_ids = list(products_data.keys())
        existing_products = {
            product.product_id: product for product in Product.objects.filter(
                product_id__in=product_ids)
        }

        new_products = []

        for pid, data in products_data.items():
            if pid not in existing_products:
                new_products.append(Product(**data))

        Product.objects.bulk_create(new_products)

        # Bulk create orders
        order_objects = [Order(
            order_id=data['order_id'],
            customer_id=data['customer_id'],
            platform_id=data['platform_id'],
            order_date=data['order_date'],
            platform_data=data['platform_data'],
        ) for data in orders_data]

        Order.objects.bulk_create(order_objects, ignore_conflicts=True)

        # Bulk create order items
        order_item_objects = [OrderItem(
            order_id=data['order_id'],
            product_id=data['product_id'],
            quantity_sold=data['quantity_sold'],
            selling_price=data['selling_price'],
            total_sale_value=data['total_sale_value'],
        ) for data in order_items_data]

        OrderItem.objects.bulk_create(order_item_objects, ignore_conflicts=True)

        # Bulk create deliveries
        delivery_objects = [Delivery(
            order_id=data['order_id'],
            delivery_address=data['delivery_address'],
            delivery_date=data['delivery_date'],
            delivery_status=data['delivery_status'],
            delivery_partner=data['delivery_partner'],
            delivery_data=data['delivery_data'],
        ) for data in deliveries_data]

        Delivery.objects.bulk_create(delivery_objects, ignore_conflicts=True)

def extract_platform_data(platform_config, row):
    """
    Extracts platform-specific data from a row.
    """
    platform_data_field_mapping = platform_config.get('platform_data_field_mapping', {})
    return {k: row.get(v) for k, v in platform_data_field_mapping.items()}

def extract_delivery_data(platform_config, row):
    """
    Extracts platform-specific delivery data from a row.
    """
    delivery_data_field_mapping = platform_config.get('delivery_data_field_mapping', {})
    return {k: row.get(v) for k, v in delivery_data_field_mapping.items()}

def parse_date(date_str, date_format):
    """
    Parses a date string into a date object using the provided format.
    """
    if date_str:
        return datetime.strptime(date_str, date_format).date()
    return None
