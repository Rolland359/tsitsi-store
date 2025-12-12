from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist

# Fonction utilitaire pour récupérer ou créer l'ID de session (similaire à _cart_id dans views.py)
def get_cart_id(request):
    """Récupère l'ID de session ou en crée un nouveau si inexistant."""
    cart_id = request.session.get('cart_id')
    if not cart_id:
        request.session.create()
        request.session['cart_id'] = request.session.session_key
    return request.session['cart_id']


def counter(request):
    """
    Retourne le nombre total d'articles dans le panier.
    Cette fonction est appelée à chaque requête.
    """
    cart_count = 0
    
    # Exclure l'interface d'administration pour éviter des erreurs inutiles
    if 'admin' in request.path:
        return {}

    try:
        # 1. Récupérer le panier (Cart) lié à la session
        cart = Cart.objects.filter(cart_id=get_cart_id(request)).first()
        
        if cart:
            # 2. Compter la quantité de tous les articles actifs dans ce panier
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
            for cart_item in cart_items:
                cart_count += cart_item.quantity
                
    except ObjectDoesNotExist:
        # Si la table Cart n'est pas encore créée (première migration), on ignore
        pass
        
    # Retourne un dictionnaire qui sera fusionné dans le contexte de tous les templates
    return dict(cart_count=cart_count)