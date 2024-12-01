from django.contrib import admin
from sales.models import Order, OrderItem, Delivery, Platform, Customer, Product

# Register your models here.
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Delivery)
admin.site.register(Platform)
admin.site.register(Customer)
admin.site.register(Product)
