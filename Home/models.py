from django.db import models

from Dashboard.models import Product
from chacha.settings import AUTH_USER_MODEL
from django.utils import timezone

# Create your models here.

# Article(order)

class Order(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)
    ordered_date = models.DateTimeField(blank=True, null=True)


    def __str__(self):
        return f"{self.product.product_name} ({self.quantity})" 
    

class Cart(models.Model):
    user = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.CASCADE)
    orders = models.ManyToManyField(Order)

    def __str__(self):
        return self.user.username
    
    def delete(self, *args, **kwargs):
        for order in self.orders.all():
            order.ordered=True
            order.ordered_date = timezone.now()
            order.save()

        self.orders.clear()    
        super().delete(*args, **kwargs)