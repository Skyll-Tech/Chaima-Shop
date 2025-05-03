from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager


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


class Shopper(AbstractUser):
    username = None
    email = models.EmailField(max_length=240, unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()