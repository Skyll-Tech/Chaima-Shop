from .models import Cart

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
            cart = Cart.objects.filter(anonymous_id=cart_id, ordered=False).first()
    return {'cart': cart}