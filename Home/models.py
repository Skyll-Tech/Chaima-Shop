from django.db import models
import uuid

from Dashboard.models import Product
from chacha.settings import AUTH_USER_MODEL
from django.utils import timezone

# Create your models here.

# Article(order)

class Order(models.Model):
    # Pour un utilisateur connecté, on utilise le champ 'user'
    # Pour un utilisateur non connecté, le champ 'anonymous_id' identifiera la commande
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    anonymous_id = models.CharField(max_length=255, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)
    ordered_date = models.DateTimeField(blank=True, null=True)

    # Retourne une représentation lisible de la commande
    def __str__(self):
        return f"{self.product.product_name} ({self.quantity})"
    
    # Propriété pour calculer le prix total de la commande 
    @property
    def total_price(self):
        return self.product.product_price * self.quantity
    


class Cart(models.Model):
    # Le panier est lié à l'utilisateur connecté s'il existe
    user = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    # Pour un utilisateur non connecté, on utilisera un identifiant unique stocké en session
    anonymous_id = models.CharField(max_length=255, null=True, blank=True, unique=True)
    # Plusieurs commandes (Order) peuvent être ajoutées dans le panier
    orders = models.ManyToManyField(Order)
    ordered = models.BooleanField(default=False)
    ordered_date = models.DateTimeField(blank=True, null=True)

    # Propriété pour calculer le total net du panier en sommant les prix totaux de chaque commande
    @property
    def net_total(self):
        return sum(order.total_price for order in self.orders.all())

    # Méthode pour afficher le panier par l'email de l'utilisateur connecté
    # ou par l'identifiant anonyme si l'utilisateur n'est pas connecté
    def __str__(self):
        if self.user:
            return self.user.email
        return f"Panier anonyme ({self.anonymous_id})"

    # Méthode pour marquer toutes les commandes comme validées, puis vider et supprimer le panier
    def order_ok(self):
        for order in self.orders.all():
            order.ordered = True
            order.ordered_date = timezone.now()
            order.save()
        self.orders.clear()
        self.delete()

    # On surcharge la méthode delete pour supprimer également les commandes associées au panier
    def delete(self, *args, **kwargs):
        orders = self.orders.all()
        for order in orders:
            order.delete()
        super().delete(*args, **kwargs)