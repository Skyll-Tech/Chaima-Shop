from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from iso3166 import countries
from chacha.settings import STRIPE_API_KEY
import stripe



# Create your models here.


class CustomUserManager(BaseUserManager):
    # kwargs si prénom nom de famille etc...
    def create_user(self, email, password, **kwargs):
        if not email:
            raise ValueError("Vous devez renseigner un email")

        user = self.model(email=self.normalize_email(email), **kwargs)
        user.set_password(password)  #permet de encrypter un mdp
        user.save()
        return user

    def create_superuser(self, email, password, **kwargs):
        kwargs['is_staff'] = True
        kwargs['is_superuser'] = True   
        kwargs['is_active'] = True

        return self.create_user(email=email, password=password, **kwargs)


class Shopper(AbstractUser):  ## compte client
    username = None
    stripe_id = models.CharField(max_length=90, blank=True)
    email = models.EmailField(max_length=240, unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()


class ShippingAddress(models.Model):
    # comme je peux avoir plusieurs adresses pour un user pas de one mais une foreign
    # je peux ajouter une annotation de type afin d'avoir l'auto complétion user: Shopper
    # ainsi on précise que user va être un objet de type Shopper
    user: Shopper = models.ForeignKey(Shopper, on_delete=models.CASCADE, related_name="addresses")
    name = models.CharField(max_length=240)
    address_1 = models.CharField(max_length=1024, help_text="Adresse de voirie et numéro de rue")
    address_2 = models.CharField(max_length=1024, help_text="Bâtiment, étage, lieu-dit...", blank=True)
    city = models.CharField(max_length=1024)
    zip_code = models.CharField(max_length=32)
    # liste de tuple avec en 1er deux lettres (bd) et après le pays
    country = models.CharField(max_length=2, choices=[(c.alpha2.lower(), c.name) for c in countries])
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.name

"""

    def __str__(self):
        # __dict__ : un dico avec les attributs de l'instance en clé et en valeur les valeurs des attributs
        # c'est ici que j'utilise l'unpacking, on évite le name=self.name, address_1=self.address_1 ... etc
        # le strip pour enlever les sauts de ligne du début et de fin de mon address_format
        # je récupère dict dans une var et je copie pour créer un autre dico en mémoire
        # puis j'attribue le display à country pour ne pas afficher le fr de la BDD
        data = self.__dict__.copy()
        data.update(country=self.get_country_display())
        return ADDRESS_FORMAT.format(**data).strip("\n")

    # changer l'adresse par défaut stripe
    # https://stripe.com/docs/api/customers/update
    def set_default(self):
        stripe.api_key = STRIPE_API_KEY
        # vérifier si on a déjà un client stripe
        if not self.user.stripe_id:
            raise ValueError(f"User {self.user.email} n'a pas de customer id")

        # récupérer toutes les adresses de l'utilisateur (related_name), queryset de toutes que l'on False avc update
        self.user.addresses.update(default=False)
        # puis sur l'adresse en cours True
        self.default = True
        self.save()

        stripe.Customer.modify(
            # "cus_NZJ296BoT4SGlF", on remplace par
            self.user.stripe_id,
            shipping={"name": self.name,
                      "address": self.as_dict()},
            address=self.as_dict(),
        )

    # je vais attribuer le dictionnaire à une méthode que j'avais initialement passé à address = {}
    def as_dict(self):
        return {"city": self.city,
                "country": self.country,
                "line1": self.address_1,
                "line2": self.address_2,
                "postal_code": self.zip_code}

            
                """