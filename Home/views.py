from pprint import pprint
from django.shortcuts import redirect, render, HttpResponse, get_object_or_404
from Account.models import Shopper
from Dashboard.models import Product, Categorie
import random
from django.urls import reverse
from django.utils import timezone


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

    return redirect(reverse("product_details",kwargs={"id":id}))

def cart(request):
    cart = get_object_or_404(Cart, user=request.user)

    return render(request, 'home/cart.html', {'orders': cart.orders.all()})

def Create_checkout_session(request):
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
            line_items=line_items,  # Transmet les objets construits correctement
            mode='payment',
            success_url=YOUR_DOMAIN + reverse('checkout_success'),  # Chemin relatif vers la page de succès
            cancel_url=YOUR_DOMAIN + '/cancel/',    # Chemin relatif vers la page d'annulation
        )
    except Exception as e:
        return HttpResponse(f"Une erreur est survenue : {str(e)}", status=400)
    
    return redirect(checkout_session.url, code=303)


def Checkout_success(request):
    return render(request, 'home/success.html/')



def Delete_cart(request):
    if cart := request.user.cart:
        cart.delete()
    
    return redirect('shop')


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

        return HttpResponse(status=200)

    # Passed signature verification
    return HttpResponse(status=200)

# pas de requête ici on créer une fonction qui sera retournée dans la vue stripe_webhook
def complete_order(data, user):
    user.stripe_id = data['customer']
    user.cart.order_ok()
    # faire un save pour le stripe_id
    user.save()

    # 200 pour indiquer que le paiement a été procéssé correctement
    return HttpResponse(status=200)
        
def Mention_legale(request):
    return render(request, 'conditions_gene/mention_legale.html')




