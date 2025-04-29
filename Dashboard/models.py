from django.db import models

# Create your models here.
class Categorie(models.Model):
    categorie_name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.categorie_name


class Product(models.Model):
    product_name = models.CharField(max_length=100, unique=True)
    product_brand = models.CharField(max_length=30, blank=True, null=True)
    product_description = models.TextField(null=True, blank=True)
    product_categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_image1 = models.ImageField(upload_to='products_images/', blank=True, null=True)
    product_image2 = models.ImageField(upload_to='products_images/', blank=True, null=True)
    product_image3 = models.ImageField(upload_to='products_images/', blank=True, null=True)
    product_image4 = models.ImageField(upload_to='products_images/', blank=True, null=True)
    stripe_id = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.product_name