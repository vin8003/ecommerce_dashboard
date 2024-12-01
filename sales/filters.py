from sales.models import Order
from django_filters import rest_framework as filters

class OrderFilter(filters.FilterSet):
    start_date = filters.DateFilter(field_name="order_date", lookup_expr='gte')
    end_date = filters.DateFilter(field_name="order_date", lookup_expr='lte')
    category = filters.CharFilter(field_name="order_items__product__category", lookup_expr='iexact')
    delivery_status = filters.CharFilter(field_name="delivery__delivery_status")
    platform = filters.CharFilter(field_name="platform__platform_name", lookup_expr='iexact')
    state = filters.CharFilter(field_name="delivery__delivery_address", method='filter_by_state')

    class Meta:
        model = Order
        fields = []

    def filter_by_state(self, queryset, name, value):
        return queryset.filter(delivery__delivery_address__icontains=value)
