# Generated by Django 5.1.7 on 2025-03-25 13:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('minimal_ecom_base', '0002_product_bought_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_visible',
            field=models.BooleanField(default=True),
        ),
    ]
