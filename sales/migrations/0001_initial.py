# Generated by Django 5.1.3 on 2024-12-01 11:45

import django.contrib.postgres.indexes
import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('customer_id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('customer_name', models.CharField(max_length=255)),
                ('contact_email', models.EmailField(max_length=254)),
                ('phone_number', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'customers',
            },
        ),
        migrations.CreateModel(
            name='Platform',
            fields=[
                ('platform_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('platform_name', models.CharField(max_length=100)),
                ('platform_config', models.JSONField(default=dict)),
            ],
            options={
                'db_table': 'platforms',
                'indexes': [models.Index(fields=['platform_name'], name='platforms_platfor_0c264e_idx')],
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('order_id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('order_date', models.DateField()),
                ('platform_data', models.JSONField(blank=True, null=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sales.customer')),
                ('platform', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sales.platform')),
            ],
            options={
                'db_table': 'orders',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('product_id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('product_name', models.CharField(max_length=255)),
                ('category', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'products',
                'indexes': [models.Index(fields=['category'], name='products_categor_fce6e6_idx')],
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('order_item_id', models.AutoField(primary_key=True, serialize=False)),
                ('quantity_sold', models.PositiveIntegerField()),
                ('selling_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_sale_value', models.DecimalField(decimal_places=2, max_digits=12)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='sales.order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sales.product')),
            ],
            options={
                'db_table': 'order_items',
            },
        ),
        migrations.CreateModel(
            name='Delivery',
            fields=[
                ('delivery_id', models.AutoField(primary_key=True, serialize=False)),
                ('delivery_address', models.CharField(max_length=255)),
                ('delivery_date', models.DateField()),
                ('delivery_status', models.CharField(max_length=50)),
                ('delivery_partner', models.CharField(blank=True, max_length=100, null=True)),
                ('delivery_data', models.JSONField(blank=True, null=True)),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='sales.order')),
            ],
            options={
                'db_table': 'deliveries',
                'indexes': [models.Index(fields=['delivery_status'], name='deliveries_deliver_db2090_idx'), django.contrib.postgres.indexes.GinIndex(fields=['delivery_data'], name='deliveries_deliver_749590_gin')],
                'unique_together': {('order', 'delivery_status', 'delivery_address')},
            },
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['order_date'], name='orders_order_d_6e39a9_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=django.contrib.postgres.indexes.GinIndex(fields=['platform_data'], name='orders_platfor_474023_gin'),
        ),
        migrations.AddIndex(
            model_name='orderitem',
            index=models.Index(fields=['product'], name='order_items_product_a53db1_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='orderitem',
            unique_together={('order', 'product', 'selling_price')},
        ),
    ]
