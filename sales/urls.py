from django.urls import path
from .views import (
    MonthlySalesVolume, MonthlyRevenue, OrderListView, SummaryMetricsAPI,
    DataImportAPI
)

urlpatterns = [
    path(
        'import-data/',
        DataImportAPI.as_view(),
        name='import-data'
    ),
    path(
        'monthly-sales-volume/',
        MonthlySalesVolume.as_view(),
        name='monthly-sales-volume'
    ),
    path(
        'monthly-revenue/',
        MonthlyRevenue.as_view(),
        name='monthly-revenue'
    ),
    path(
        'orders/',
        OrderListView.as_view(),
        name='orders'
    ),
    path(
        'summary-metrics/',
        SummaryMetricsAPI.as_view(),
        name='summary-metrics'
    ),
]
