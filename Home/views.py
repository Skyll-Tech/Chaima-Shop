from pprint import pprint
import environ
from django.forms import modelformset_factory
from django.shortcuts import redirect, render, HttpResponse, get_object_or_404
from Account.models import ShippingAddress, Shopper
from Dashboard.models import Product, Categorie
import random
from django.urls import reverse
from django.utils import timezone
import uuid      #bibliothèque utile pour créer des identifiants uniques qui évitent les conflits et améliorent la gestion des données 

from Home.forms import OrderForm
from Home.models import Cart, Order

from chacha import settings
from django.views.decorators.csrf import csrf_exempt
from chacha.settings import BASE_DIR

import stripe   ### à demander
stripe.api_key = settings.STRIPE_API_KEY
environ.Env.read_env(BASE_DIR / ".env")
env = environ.Env()



YOUR_DOMAIN = 'http://localhost:8000'  #### a demander

# Create your views here.
"""
def testpage(request):
    return render(request, "pagetest.html")
"""
def Index(request):
    product = list(Product.objects.all()) #recupere tout les produits et met dans une liste
    random_product = random.sample(product, min(len(product),3)) # Sélectionne 3 produits au hasard (random.sample permet de selectionner un nombre d'élément specifique dans une liste)
    return render(request, "home/index.html",{'product':random_product}) 

def Shop(request):
    product = Product.objects.all()
    categorie = Categorie.objects.all()
    context={'product':product, 'active_categorie': None, 'categorie':categorie}
    return render(request, 'home/shop.html', context)

def Product_details(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'home/product_details.html',{'product':product})

def Product_cat(request, id):
    categorie_id = get_object_or_404(Categorie, id = id)
    product = Product.objects.filter(product_categorie = categorie_id)
    categorie = Categorie.objects.all()
    context = {'categorie':categorie, 'active_categorie':id, 'product':product}
    return render(request, 'home/shop.html', context)

def Checkout(request,id):
    product = get_object_or_404(Product, id=id)
    return render(request,'home/checkout.html', {'product': product})


def cart(request):
    """
    Vue qui affiche le contenu du panier et gère le cas des utilisateurs authentifiés et non connectés.
    
    Pour un utilisateur authentifié :
      - Le panier est récupéré via le champ 'user'.
      - Les commandes sont récupérées en filtrant sur 'user'.
      
    Pour un utilisateur non connecté :
      - On s'assure qu'un identifiant de panier ('cart_id') est stocké dans la session.
      - Le panier est récupéré via le champ 'anonymous_id'.
      - Les commandes sont récupérées en filtrant sur 'anonymous_id'.
    """
    if request.user.is_authenticated:
        # --- Utilisateur connecté ---
        cart = get_object_or_404(Cart, user=request.user)
        orders = Order.objects.filter(user=request.user, ordered=False)
    else:
        # --- Utilisateur non connecté ---
        # Récupération de l'identifiant du panier stocké en session
        cart_id = request.session.get("cart_id", None)
        if not cart_id:
            # S'il n'existe pas d'identifiant dans la session, l'utilisateur n'a pas encore ajouté de produit.
            return redirect('chaima_shop:index')
        
        # Récupération du panier via l'identifiant anonyme
        cart = get_object_or_404(Cart, anonymous_id=cart_id)
        orders = Order.objects.filter(anonymous_id=cart_id, ordered=False)

    # Si aucune commande n'est en cours, redirection vers la page d'accueil
    if orders.count() == 0:
        return redirect('chaima_shop:index')
    
    # Création du formset pour gérer les commandes de l'utilisateur
    OrderFormSet = modelformset_factory(Order, form=OrderForm, extra=0)
    formset = OrderFormSet(queryset=orders)
    
    # Le contexte inclut le panier complet avec ses commandes et le total net
    return render(request, 'home/cart.html', context={
        'orders': cart.orders.all(),
        "forms": formset,
        "net_total": cart.net_total
    })

### Cette vue est utilisé pour affiché le panier des utilisateurs, qu'ils soient connectés ou pas
def cart_context_processor(request):
    """
    Ce context processor place la variable `cart` dans le contexte pour tous les utilisateurs.
    Pour un utilisateur connecté, on récupère son panier via user.cart.
    Pour un utilisateur non connecté, on récupère le panier via la clé de session "cart_id".
    """
    if request.user.is_authenticated:
        cart = getattr(request.user, 'cart', None)
    else:
        cart = None
        cart_id = request.session.get("cart_id")
        if cart_id:
            # On suppose que Cart possède un champ anonymous_id
            from .models import Cart
            cart = Cart.objects.filter(anonymous_id=cart_id, ordered=False).first()
    return {'cart': cart}



def Add_to_cart(request, id):
    """
    Vue permettant d'ajouter un produit au panier.
    
    Pour un utilisateur connecté :
      - Le panier est lié au champ 'user'.
      - On récupère ou crée une commande associée au produit.
    
    Pour un utilisateur non connecté :
      - On vérifie si un identifiant de panier ('cart_id') existe dans la session ;
        sinon, on en crée un nouveau via uuid4.
      - On récupère ou crée un panier anonyme basé sur cet 'anonymous_id'.
      - On récupère ou crée une commande basée sur cet 'anonymous_id'.
    """
    # Récupération du produit à ajouter
    product = get_object_or_404(Product, id=id)
    
    if request.user.is_authenticated:
        # --- Utilisateur connecté ---
        # Récupération ou création du panier lié à l'utilisateur
        cart, _ = Cart.objects.get_or_create(user=request.user)
        # Récupération ou création d'une commande non validée pour ce produit et cet utilisateur
        order, created = Order.objects.get_or_create(user=request.user, ordered=False, product=product)
    else:
        # --- Utilisateur non connecté ---
        # Vérifier la présence d'un identifiant de panier dans la session (sinon, en créer un)
        cart_id = request.session.get("cart_id")
        if not cart_id:
            cart_id = str(uuid.uuid4())
            request.session["cart_id"] = cart_id
        
        # Récupération ou création d'un panier basé sur l'identifiant anonyme (stocké dans la session)
        cart, _ = Cart.objects.get_or_create(anonymous_id=cart_id)
        
        # Récupération ou création d'une commande non validée pour ce produit en utilisant 'anonymous_id'
        order, created = Order.objects.get_or_create(anonymous_id=cart_id, ordered=False, product=product)
    
    if created:
        # Si la commande vient d'être créée, on l'ajoute au panier et on sauvegarde
        cart.orders.add(order)
        cart.save()
    else:
        # Si la commande existe déjà, on incrémente simplement la quantité
        order.quantity += 1
        order.save()

    # Redirection vers la page de détails du produit ajouté
    return redirect(reverse("chaima_shop:product_details", kwargs={"id": id}))



def Update_quantities(request):
    # Pour un utilisateur connecté, on filtre par le champ 'user'
    if request.user.is_authenticated:
        queryset = Order.objects.filter(user=request.user, ordered=False)
    else:
        # Pour un utilisateur anonyme, on récupère l'identifiant stocké dans la session
        cart_id = request.session.get("cart_id")
        if cart_id:
            # On filtre avec le champ 'anonymous_id' que tu devras avoir ajouté dans ton modèle Order
            queryset = Order.objects.filter(anonymous_id=cart_id, ordered=False)
        else:
            # Si aucune cart_id n'est disponible, on ne récupère aucune commande
            queryset = Order.objects.none()

    # Création du formset à partir de la requête
    OrderFormSet = modelformset_factory(Order, form=OrderForm, extra=0)
    formset = OrderFormSet(request.POST or None, queryset=queryset)

    if request.method == 'POST':
        if formset.is_valid():
            formset.save()
            return redirect('chaima_shop:cart')
        else:
            print("Erreurs de formulaire:", formset.errors)

    # Calcul du total net de tous les articles
    net_total = sum(order.total_price for order in queryset)
    return render(request, 'pagetest.html', {'forms': formset, 'net_total': net_total})

def Delete_cart(request):
    # Pour un utilisateur connecté, on récupère le panier via 'user'
    if request.user.is_authenticated:
        cart = getattr(request.user, 'cart', None)
    else:
        # Pour un utilisateur non connecté, on cherche l'identifiant dans la session
        cart_id = request.session.get("cart_id")
        cart = Cart.objects.filter(anonymous_id=cart_id).first() if cart_id else None

    # Si un panier est trouvé, on le supprime
    if cart:
        cart.delete()
    
    # Redirige vers la page shop après suppression
    return redirect('chaima_shop:shop')


def remove_from_cart(request, order_id):
    # Récupérer le panier selon le type d'utilisateur
    if request.user.is_authenticated:
        cart = get_object_or_404(Cart, user=request.user)
        # Pour un utilisateur connecté, on récupère la commande en se basant sur son identifiant
        order = get_object_or_404(Order, id=order_id)
    else:
        # Pour un utilisateur non connecté, récupérer l'identifiant du panier stocké dans la session
        cart_id = request.session.get("cart_id")
        # Si aucun identifiant n'est trouvé, on redirige
        if not cart_id:
            return redirect('chaima_shop:cart')
        cart = get_object_or_404(Cart, anonymous_id=cart_id)
        # On recherche la commande liée à ce panier anonyme
        order = get_object_or_404(Order, id=order_id, anonymous_id=cart_id)

    # Si la commande est bien présente dans le panier, on la retire et on la supprime
    if order in cart.orders.all():
        cart.orders.remove(order)
        order.delete()  # Supprime définitivement l'ordre si non nécessaire
    
    # Redirection vers la vue du panier
    return redirect('chaima_shop:cart')




import stripe
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from .models import Cart, Order

def Create_checkout_session(request):
    """
    Crée une session de paiement Stripe pour le panier de l'utilisateur.
    
    Pour un utilisateur connecté :
      - Le panier est récupéré via request.user.cart.
      - On utilise l'email de l'utilisateur (et éventuellement son stripe_id) pour créer le client sur Stripe.
    
    Pour un utilisateur non connecté :
      - Le panier est récupéré via l'identifiant anonyme stocké dans la session (cart_id et le champ anonymous_id dans Cart).
      - On ajoute dans les métadonnées de Stripe l'identifiant anonyme pour pouvoir ensuite retrouver et vider le panier.
      - Aucune information client (customer_email) n'est envoyée, afin que Stripe demande l'email sur la page de paiement.
    """
    
    # Vérification si l'utilisateur est authentifié
    if request.user.is_authenticated:
        # Pour les utilisateurs connectés : récupérer le panier lié à l'utilisateur
        cart = getattr(request.user, 'cart', None)
        if not cart:
            # S'il n'y a pas de panier, rediriger vers la page du panier
            return redirect('chaima_shop:cart')
        
        # Récupérer l'email de l'utilisateur et son identifiant Stripe (s'il existe)
        customer_email = request.user.email
        stripe_customer = getattr(request.user, 'stripe_id', None)
        
        # Pas besoin d'ajouter des métadonnées spécifiques pour un utilisateur connecté
        metadata = {}
    
    else:
        # Pour un utilisateur non connecté : récupérer l'identifiant anonyme stocké en session
        cart_id = request.session.get("cart_id")
        if not cart_id:
            # S'il n'y a pas d'identifiant en session, on redirige vers la page du panier
            return redirect('chaima_shop:cart')
        
        # Récupérer le panier anonyme qui n'est pas encore validé (ordered=False)
        cart = Cart.objects.filter(anonymous_id=cart_id, ordered=False).first()
        if not cart:
            return redirect('chaima_shop:cart')
        
        # Pour les utilisateurs non connectés, on ajoute l'identifiant anonyme dans les metadata
        metadata = {"anonymous_id": cart.anonymous_id}
        # On ne dispose pas d'email ni de stripe_id pour les anonymes
        customer_email = None
        stripe_customer = None

    # Construction de la liste des articles à envoyer à Stripe pour la session de checkout
    line_items = [
        {
            "price": order.product.stripe_id,  # L'ID Stripe du produit
            "quantity": order.quantity           # La quantité commandée
        } for order in cart.orders.all()
    ]

    # Préparation du dictionnaire des données pour Stripe
    checkout_data = {
        "locale": "fr",
        "line_items": line_items,
        "mode": "payment",
        "shipping_address_collection": {"allowed_countries": ["FR", "BE", "CM"]},
        # Les URLs de succès et d'annulation doivent être des URLs absolues pour Stripe
        "success_url": request.build_absolute_uri(reverse('chaima_shop:checkout_success')),
        "cancel_url": "http://127.0.0.1:8000",
        "metadata": metadata,  # Transmission des métadonnées (notamment pour le panier anonyme)
    }

    # Pour un utilisateur connecté, fournir les informations client nécessaires
    if request.user.is_authenticated:
        if stripe_customer:
            # Si l'utilisateur possède déjà un stripe_id, on le transmet pour associer la session au client existant
            checkout_data["customer"] = stripe_customer
        else:
            # Sinon, fournir l'email et laisser Stripe créer le client automatiquement
            checkout_data["customer_email"] = customer_email
            checkout_data["customer_creation"] = "always"
    # Pour un utilisateur non connecté, nous n'ajoutons pas de customer_email
    # Ainsi, Stripe demandera à l'utilisateur de renseigner son email sur la page de paiement

    # Création de la session de paiement sur Stripe en utilisant l'unpacking du dictionnaire
    session = stripe.checkout.Session.create(**checkout_data)

    # Redirection vers l'URL de la session Stripe (avec le code de redirection approprié)
    return redirect(session.url, code=303)


def Checkout_success(request):
    return render(request, 'home/success.html/')


@csrf_exempt
def Stripe_webhook(request):
    # Récupération du payload et de l'en-tête de signature Stripe
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = env("endpoint_secret")
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Payload invalide
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Signature invalide
        return HttpResponse(status=400)

    if event['type'] == "checkout.session.completed":
        data = event['data']['object']
        pprint(data)
        
        # Récupérer l'email du client contenu dans l'objet Stripe
        email = data.get('customer_details', {}).get('email')
        if not email:
            return HttpResponse("Invalid user email", status=404)
        
        # Pour gérer également le cas des utilisateurs non connectés, 
        # nous créons ou récupérons un utilisateur associé à cet email.
        user, created = Shopper.objects.get_or_create(email=email)
        
        # Appel des fonctions pour compléter la commande et sauvegarder l'adresse
        complete_order(data=data, user=user)
        save_shipping_adress(data=data, user=user)
        
        return HttpResponse(status=200)

    return HttpResponse(status=200)

# pas de requête ici on créer une fonction qui sera retournée dans la vue stripe_webhook
from django.http import HttpResponse
from .models import Cart

def complete_order(data, user):
    """
    Finalise la commande en mettant à jour le stripe_id de l'utilisateur et en vidant automatiquement son panier.

    Pour un utilisateur connecté, on recherche dans la base de données un panier lié à cet utilisateur
    (c'est-à-dire avec `user=user` et `ordered=False`).

    Pour un utilisateur non connecté, l'identifiant anonyme est transmis dans data['metadata']
    et permet de retrouver le panier correspondant pour le supprimer.

    Des impressions de débogage sont ajoutées pour vérifier que le code passe bien par la suppression.
    """
    # Mis à jour du stripe_id si présent dans les données Stripe
    if data.get('customer'):
        user.stripe_id = data['customer']
        print(f"Stripe ID mis à jour pour l'utilisateur : {user.stripe_id}")

    # Cas utilisateur connecté
    if user.is_authenticated:
        # Recherche du panier non commandé lié à l'utilisateur
        cart = Cart.objects.filter(user=user, ordered=False).first()
        if cart:
            print(f"Suppression du panier de l'utilisateur connecté : {user.email}")
            cart.delete()
        else:
            print("Aucun panier trouvé pour l'utilisateur connecté.")
    else:
        # Cas utilisateur non connecté
        # Récupération de l'identifiant anonyme depuis les metadata envoyées par Stripe
        anonymous_id = data.get('metadata', {}).get('anonymous_id')
        if anonymous_id:
            try:
                # Recherche du panier correspondant à cet anonymous_id
                cart = Cart.objects.get(anonymous_id=anonymous_id, ordered=False)
                print(f"Suppression du panier anonyme avec anonymous_id : {anonymous_id}")
                cart.delete()
            except Cart.DoesNotExist:
                print(f"Aucun panier trouvé pour anonymous_id: {anonymous_id}")
        else:
            print("Aucune metadata 'anonymous_id' reçue pour utilisateur non connecté.")

    # Sauvegarde de l'utilisateur pour enregistrer les modifications (par exemple, le stripe_id)
    user.save()

    # Retourne un status HTTP 200 pour indiquer que le traitement a réussi
    return HttpResponse(status=200)


def save_shipping_adress(data, user):
    try:
        # Extraction depuis "customer_details" des données Stripe
        customer_details = data["customer_details"]
        address = customer_details["address"]
        name = customer_details["name"]
        city = address.get("city", "")
        country = address.get("country", "")
        line1 = address.get("line1", "")
        # Remplacer une éventuelle valeur None par une chaîne vide pour line2
        line2 = address.get("line2") or ""
        # On s'assure que postal_code n'est pas None
        zip_code = address.get("postal_code") or ""
    except KeyError:
        return HttpResponse(status=400)

    # Si l'utilisateur n'est pas connecté, on utilisera None pour le champ user.
    # REMARQUE : Assurez-vous que la relation dans ShippingAddress autorise null (i.e. null=True et blank=True).
    if not user.is_authenticated:
        user_instance = None
    else:
        user_instance = user

    ShippingAddress.objects.get_or_create(
        user=user_instance,
        name=name,
        city=city,
        country=country.lower(),
        address_1=line1,
        address_2=line2,
        zip_code=zip_code
    )
    return HttpResponse(status=200)


def Contact(request):
    return render(request, 'home/contact.html')

def Mention_legale(request):
    return render(request, 'conditions_gene/mention_legale.html')




