from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.db import IntegrityError
from .models import Categorie, Product
from .forms import Categorie_form, Product_form
from Account.models import  ShippingAddress

# Create your views here.

def superuser_check(user):
    return user.is_active and user.is_superuser

@login_required(login_url='login')
def Dashboard(request):
    if not request.user.is_superuser:
        # 403 – Accès interdit pour les utilisateurs authentifiés
        raise PermissionDenied

    shipping_addresses = ShippingAddress.objects.all()
    return render(request, 'dashboard/index.html', {
        'shipping_addresses': shipping_addresses
    })

@login_required(login_url='login')
def Show_categories(request):

    if not request.user.is_superuser:
        # 403 – Accès interdit pour les utilisateurs authentifiés
        raise PermissionDenied

    categorie = Categorie.objects.all()
    product = Product.objects.all()
    context = {'categorie':categorie, 'product':product}
    return render(request, 'dashboard/affichage/categories.html', context)

@login_required(login_url='login')
def Create_categorie(request):
    if not request.user.is_superuser:
        # 403 – Accès interdit pour les utilisateurs authentifiés
        raise PermissionDenied

    if request.method == 'POST': 
        form = Categorie_form(request.POST)  # Instancier le formulaire avec les données soumises
        if form.is_valid():
            form.save()  
            messages.success(request, "Catégorie créée avec succès")  # Afficher un message de succès
            return redirect("create_categorie")  

    else: 
        form = Categorie_form()  # Instancier un nouveau formulaire vide pour une requête GET
    return render(request, "dashboard/creation/create_categorie.html", {'form': form}) # Rendre le template avec le formulaire (et les erreurs le cas échéant)

@login_required(login_url='login')
def Update_categorie(request, id):
    if not request.user.is_superuser:
        # 403 – Accès interdit pour les utilisateurs authentifiés
        raise PermissionDenied

    categorie = get_object_or_404(Categorie, id=id)
    if request.method == 'POST': 
        form = Categorie_form(request.POST, instance=categorie)
        if form.is_valid():
            form.save()
            messages.success(request, "Catégorie modifiée avec succès")
            # Redirigez ou affichez un message de succès ici
    else:
        form = Categorie_form(instance=categorie)  # Instanciez le formulaire pour un GET
    return render(request, 'dashboard/creation/update_categorie.html', {'form': form, 'categorie': categorie})

@login_required(login_url='login')
def Delete_categorie(request, id):
    if not request.user.is_superuser:
        # 403 – Accès interdit pour les utilisateurs authentifiés
        raise PermissionDenied
    
    categorie = get_object_or_404(Categorie, id=id)  
    if request.method == 'POST':  
        categorie.delete()  
        messages.success(request, 'La catégorie a été supprimée avec succès !')  
        return redirect('show_categories')  
    return render(request, 'dashboard/creation/delete_categorie.html', {'categorie': categorie}) 

@login_required(login_url='login')
def Show_product(request):
    if not request.user.is_superuser:
        # 403 – Accès interdit pour les utilisateurs authentifiés
        raise PermissionDenied
    
    product = Product.objects.all()
    categorie = Categorie.objects.all()
    context = {'product':product, 'categorie':categorie}
    return render(request, ('dashboard/affichage/show_product.html'), context)

@login_required(login_url='login')
def Create_product(request):
    if not request.user.is_superuser:
        # 403 – Accès interdit pour les utilisateurs authentifiés
        raise PermissionDenied
    
    categorie = Categorie.objects.all()
    if request.method == 'POST':
        form = Product_form(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Le produit a été créé avec succès")
            return redirect('create_product')
    else:
        form = Product_form()
    return render(request, 'dashboard/creation/create_product.html', {'categorie': categorie, 'form': form})


@login_required(login_url='login')
def Update_product(request, id):
    if not request.user.is_superuser:
        # 403 – Accès interdit pour les utilisateurs authentifiés
        raise PermissionDenied
    
    # Récupérer le produit à modifier ou afficher une 404 si non trouvé
    product = get_object_or_404(Product, id=id)
    categorie = Categorie.objects.all()  # Récupérer toutes les catégories

    if request.method == 'POST':
        form = Product_form(request.POST, request.FILES, instance=product) # Instancier le formulaire avec les données soumises et l'instance du produit
        if form.is_valid():
            form.save()  
            messages.success(request, "Le produit a été mis à jour avec succès") 
            return redirect('show_product') 
    else:  
        form = Product_form(instance=product) # Si la méthode n'est pas POST, instancier le formulaire avec les données du produit

    # Rendre le template avec le formulaire et les catégories
    return render(request, 'dashboard/creation/update_product.html', {
        'categorie': categorie,
        'form': form,
        'product': product  # Passer le produit pour l'affichage si nécessaire
    })

@login_required(login_url='login')
def Delete_product(request, id):
    if not request.user.is_superuser:
        # 403 – Accès interdit pour les utilisateurs authentifiés
        raise PermissionDenied
    
    product = get_object_or_404(Product, id = id)
    if request.method == 'POST':
        product.delete()
        messages.success(request,'Produit supprimé avec succès')
        return redirect('show_product')
    
    return render(request, 'dashboard/creation/delete_product.html')