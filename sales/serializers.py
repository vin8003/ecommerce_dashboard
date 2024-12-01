from rest_framework import serializers
from .models import OrderItem, Order, Delivery, Product, Platform


class PlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = Platform
        fields = ('platform_id', 'platform_name')


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = '__all__'


class DeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    platform_data = serializers.JSONField()
    delivery = DeliverySerializer(read_only=True)
    platform = PlatformSerializer(read_only=True)

    class Meta:
        model = Order
        fields = '__all__'
