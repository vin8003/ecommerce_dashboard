from uuid import uuid4
from django.db import models
from django.contrib.postgres.indexes import GinIndex


class Customer(models.Model):
    customer_id = models.CharField(max_length=50, primary_key=True)
    customer_name = models.CharField(max_length=255)
    contact_email = models.EmailField()
    phone_number = models.CharField(max_length=20)

    class Meta:
        db_table = 'customers'

    def __str__(self):
        return self.customer_name


class Product(models.Model):
    product_id = models.CharField(max_length=50, primary_key=True)
    product_name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)

    class Meta:
        db_table = 'products'
        indexes = [
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return self.product_name


class Platform(models.Model):
    platform_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    platform_name = models.CharField(max_length=100)
    platform_config = models.JSONField(default=dict)

    class Meta:
        db_table = 'platforms'
        indexes = [
            models.Index(fields=['platform_name']),
        ]

    def __str__(self):
        return self.platform_name


class Order(models.Model):
    order_id = models.CharField(max_length=50, primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE)
    order_date = models.DateField()
    platform_data = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = 'orders'
        indexes = [
            models.Index(fields=['order_date']),
            GinIndex(fields=['platform_data']),
        ]

    def __str__(self):
        return self.order_id

class OrderItem(models.Model):
    order_item_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity_sold = models.PositiveIntegerField()
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_sale_value = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = 'order_items'
        indexes = [
            models.Index(fields=['product']),
        ]
        unique_together = ('order', 'product', 'selling_price')

    def __str__(self):
        return f'{self.order.order_id} - {self.product.product_name}'


class Delivery(models.Model):
    delivery_id = models.AutoField(primary_key=True)
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    delivery_address = models.CharField(max_length=255)
    delivery_date = models.DateField()
    delivery_status = models.CharField(max_length=50)
    delivery_partner = models.CharField(max_length=100, null=True, blank=True)
    delivery_data = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = 'deliveries'
        indexes = [
            models.Index(fields=['delivery_status']),
            GinIndex(fields=['delivery_data']),
        ]
        unique_together = ('order', 'delivery_status', 'delivery_address')

    def __str__(self):
        return f'Delivery for Order {self.order.order_id}'
