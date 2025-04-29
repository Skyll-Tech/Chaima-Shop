# Ce fichier permet de creer des formulaires basés sur des models crées dans le fichier models.
# Avec cette methode, on crée des formulaires directement liés aux models

from django import forms
from .models import Product, Categorie


class Categorie_form(forms.ModelForm):
    class Meta:
        model = Categorie
        fields = '__all__'
        widgets = {
            'categorie_name': forms.TextInput(attrs={
                'class': 'form-control',  # Retirer le placeholder
            }),
        }

class Product_form(forms.ModelForm):
    # Sous-classe Meta qui permet de configurer le comportement du formulaire
    class Meta:
        model = Product # Pour spécifie le modèle associé à ce formulaire
        fields = '__all__'  
        # Définition des widgets personnalisés pour les champs du formulaire
        widgets = {
            'product_name': forms.TextInput(attrs={
                'class': 'form-control',  # Classe CSS pour le style Bootstrap
            }),
            'product_brand': forms.TextInput(attrs={
                'class': 'form-control',  
            }),
            'product_description': forms.Textarea(attrs={
                'class': 'form-control',  
            }),
            'product_price': forms.NumberInput(attrs={
                'class': 'form-control',  
            }),
            'product_categorie': forms.Select(attrs={
                'class': 'form-select',  
            }),
            # Vous pouvez ajouter des widgets pour d'autres champs si nécessaire
        }