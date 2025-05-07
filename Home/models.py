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
    
    def total_price(self):
        return self.product.product_price * self.quantity
    
    

    def __str__(self):
        return f"{self.product.product_name} ({self.quantity})" 
    
    @property
    def total_price(self):
        return self.product.product_price * self.quantity
    


class Cart(models.Model):
    # one to one car l'utilisateur ne peut avoir qu'un seul panier. Si j'utilise Foreign als unique=True
    user = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.CASCADE)
    # plusieurs articles peuvent être ajoutés donc ManytoMany
    orders = models.ManyToManyField(Order)
    ordered = models.BooleanField(default=False)
    ordered_date = models.DateTimeField(blank=True, null=True)

    
    @property
    def net_total(self):
        return sum(order.total_price for order in self.orders.all())


    def __str__(self):
        return self.user.email

    def order_ok(self):
        for order in self.orders.all():
            order.ordered = True
            order.ordered_date = timezone.now()
            order.save()

        self.orders.clear()
        self.delete()

    def delete(self, *args, **kwargs):
        orders = self.orders.all()

        for order in orders:
            order.delete()
        super().delete(*args, **kwargs)