from pprint import pprint
from django.forms import modelformset_factory
from django.shortcuts import redirect, render, HttpResponse, get_object_or_404
from Account.models import ShippingAddress, Shopper
from Dashboard.models import Product, Categorie
import random
from django.urls import reverse
from django.utils import timezone


from Home.forms import OrderForm
from Home.models import Cart, Order

from chacha import settings
import stripe   ### à demander
from django.views.decorators.csrf import csrf_exempt

stripe.api_key = settings.STRIPE_API_KEY

YOUR_DOMAIN = 'http://localhost:8000'  #### a demander

# Create your views here.

def testpage(request):
    return render(request, "pagetest.html")

def Index(request):
    product = list(Product.objects.all()) #recupere tout les produits et met dans une liste
    random_product = random.sample(product, min(len(product),3)) # Sélectionne 3 produits au hasard (random.sample permet de selectionner un nombre d'élément specifique dans une liste)
    return render(request, "home/index.html",{'product':random_product}) 

def Shop(request):
    product = Product.objects.all()
    categorie = Categorie.objects.all()
    context={'product':product, 'categorie':categorie}
    return render(request, 'home/shop.html', context)

def Product_details(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'home/product_details.html',{'product':product})

def Product_cat(request, id):
    categorie_id = get_object_or_404(Categorie, id = id)
    product = Product.objects.filter(product_categorie = categorie_id)
    categorie = Categorie.objects.all()
    context = {'categorie':categorie, 'product':product}
    return render(request, 'home/shop.html', context)

def Checkout(request,id):
    product = get_object_or_404(Product, id=id)
    return render(request,'home/checkout.html', {'product': product})

def Add_to_cart(request, id):
    user = request.user
    product = get_object_or_404(Product, id = id)
    cart, _ = Cart.objects.get_or_create(user = user)
    order, created = Order.objects.get_or_create(user = user,ordered = False, product = product)

    if created:
        cart.orders.add(order)
        cart.save()
    else:
        order.quantity += 1
        order.save()

    return redirect(reverse("chaima_shop:product_details",kwargs={"id":id}))

def cart(request):
    cart = get_object_or_404(Cart, user=request.user)
   #    # if request.user.is_anonymous:
    #     return redirect('index')

    orders = Order.objects.filter(user=request.user, ordered=False)
    # si je n'ai pas d'articles en cours de commande
    if orders.count() == 0:
        return redirect('index')
    # formset auquel on précise le modele et le formulaire. extra 0 car je ne veux pas afficher des formulaires vierge
    # un formset car on a potentiellement plusieurs forms sur la mm page car peut-être plusieurs articles
    # je l'attribue à une variable ce qui me permet de créer une class.
    OrderFormSet = modelformset_factory(Order, form=OrderForm, extra=0)
    # puis on va créer une instance
    # je veux récupérer uniquement les articles dans le panier de l'utilisateur
    formset = OrderFormSet(queryset=orders)
    return render(request, 'home/cart.html', context={'orders': cart.orders.all(),
                                                      "forms": formset})  #{'orders': cart.orders.all()}

def Update_quantities(request):
    # Récupérer les commandes de l'utilisateur
    queryset = Order.objects.filter(user=request.user, ordered=False)
    print("Ordres trouvés :", queryset.count())  # Debug

    OrderFormSet = modelformset_factory(Order, form=OrderForm, extra=0)
    formset = OrderFormSet(request.POST or None, queryset=queryset)

    if request.method == 'POST':
        print("Données POST reçues:", request.POST)  # Debug
        if formset.is_valid():
            formset.save()
            return redirect('chaima_shop:cart')
        else:
            print("Erreurs de formulaire:", formset.errors)  # Debug

    return render(request, 'pagetest.html', {'forms': formset})

def Create_checkout_session(request):
        # récupère le panier
    cart = request.user.cart
    # compréhension de liste avec un dictionnaire (id + qté)
    line_items = [{"price": order.product.stripe_id,
                   "quantity": order.quantity} for order in cart.orders.all()]

    checkout_data = {
        "locale": "fr",
        "line_items": line_items,
        "mode": 'payment',
        # voir ds la doc. On passe un dico avec une liste de pays autorisés
        "shipping_address_collection": {"allowed_countries": ["FR", "BE", "CM"]},
        # il faut une url absolue car je suis sur Stripe à ce moment-là
        "success_url": request.build_absolute_uri(reverse('chaima_shop:checkout_success')),
        "cancel_url": 'http://127.0.0.1:8000',
    }
    # une condition pour savoir si on a déjà un stripe_id pour notre user
    if request.user.stripe_id:
        checkout_data["customer"] = request.user.stripe_id
    else:
        checkout_data["customer_email"] = request.user.email
        # créer le client dans stripe la première fois
        checkout_data["customer_creation"] = "always"
    # tout ce que j'avais ici je l'ai passé à checkout_data en dictionnaire
    # on va utiliser l'unpacking
    session = stripe.checkout.Session.create(**checkout_data)

    return redirect(session.url, code=303)

"""
    try:
        cart = request.user.cart
        # Construire correctement les line_items en respectant le format attendu par Stripe
        line_items = [
            {
                'price': order.product.stripe_id,  # Utilise 'stripe_id' comme identifiant de prix
                'quantity': order.quantity,
            } 
            for order in cart.orders.all()
            if order.product.stripe_id  # Vérifie que 'stripe_id' est non vide
        ]
        
        # Vérification des line_items avant d'appeler Stripe
        if not line_items:
            return HttpResponse("Aucun produit valide avec un identifiant Stripe disponible dans le panier.", status=400)
        
        # Créer une session de checkout
        checkout_session = stripe.checkout.Session.create(
            locale="fr",
            customer_email=request.user.email,
            shipping_address_collection={'allowed_countries':["FR","CA","CM"]},
            line_items=line_items,  # Transmet les objets construits correctement
            mode='payment',
            success_url=YOUR_DOMAIN + reverse('checkout_success'),  # Chemin relatif vers la page de succès
            cancel_url=YOUR_DOMAIN + '/cancel/',    # Chemin relatif vers la page d'annulation
        )
    except Exception as e:
        return HttpResponse(f"Une erreur est survenue : {str(e)}", status=400)
    
    return redirect(checkout_session.url, code=303)

"""


def Checkout_success(request):
    return render(request, 'home/success.html/')



def Delete_cart(request):
    if cart := request.user.cart:
        cart.delete()
    
    return redirect('chaima_shop:shop')


@csrf_exempt
def Stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = "whsec_0b7d1a182b025920a7a064b6da33abef21598795b16ff42bf62e0fb4a6a639ba"
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # on veut récupérer l'évènement checkout.session.completed, il s'agit d'un dico
    if event['type'] == "checkout.session.completed":
        # dans event on a un objet qui permet de récup mail user produits acheté etc ds data object
        data = event['data']['object']
        pprint(data)
        try:
            user = get_object_or_404(Shopper, email=data['customer_details']['email'])
            # dans object (voir var data) on a l'email
        except KeyError:
            return HttpResponse("Invalid user email", status=404)

        # deux fonctions du dessous
        complete_order(data=data, user=user)
        save_shipping_adress(data=data, user=user)


        return HttpResponse(status=200)

    # Passed signature verification
    return HttpResponse(status=200)

# pas de requête ici on créer une fonction qui sera retournée dans la vue stripe_webhook
def complete_order(data, user):
    user.stripe_id = data['customer']
    user.cart.delete()
    # user.cart.order_ok()
    # faire un save pour le stripe_id
    user.save()

    # 200 pour indiquer que le paiement a été procéssé correctement
    return HttpResponse(status=200)

def save_shipping_adress(data, user):
    try:
        # Extraction depuis "customer_details" (d'après le log)
        customer_details = data["customer_details"]
        address = customer_details["address"]
        name = customer_details["name"]
        city = address.get("city", "")
        country = address.get("country", "")
        line1 = address.get("line1", "")
        # Si line2 est None, on remplace par une chaîne vide
        line2 = address.get("line2") or ""
        # On utilise 'or ""' pour s'assurer que postal_code n'est pas None
        zip_code = address.get("postal_code") or ""
    except KeyError:
        return HttpResponse(status=400)

    ShippingAddress.objects.get_or_create(
        user=user,
        name=name,
        city=city,
        country=country.lower(),
        address_1=line1,
        address_2=line2,
        zip_code=zip_code
    )
    return HttpResponse(status=200)


        
def Mention_legale(request):
    return render(request, 'conditions_gene/mention_legale.html')




