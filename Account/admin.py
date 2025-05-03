from django.contrib import admin
from .models import Shopper, ShippingAddress
# Register your models here.

admin.site.register(Shopper)
admin.site.register(ShippingAddress)
