# Generated by Django 5.2 on 2025-05-01 06:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Home', '0007_remove_cart_ordered_remove_cart_ordered_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='ordered',
            field=models.BooleanField(default=False),
        ),
    ]
