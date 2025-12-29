from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from store.models import Product 
from .models import Cart, CartItem

# Fonction utilitaire pour récupérer ou créer l'ID de session
def _cart_id(request):
    """Récupère l'ID de session ou en crée un nouveau si inexistant."""
    cart_id = request.session.get('cart_id')
    if not cart_id:
        request.session.create()
        request.session['cart_id'] = request.session.session_key
    return request.session['cart_id']

def add_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_id = _cart_id(request)
    cart, _ = Cart.objects.get_or_create(cart_id=cart_id)

    # Récupération des données du formulaire
    quantity_to_add = int(request.POST.get('quantity', 1))
    size = request.POST.get('size', '').strip()

    # Si l'utilisateur n'a pas choisi de taille ou si c'est la valeur par défaut
    if size == "Sélectionner" or not size:
        size = "Unique" # Ou None, selon votre modèle

    # On cherche un article avec le MÊME produit ET la MÊME taille
    try:
        # Note : Assurez-vous d'avoir un champ 'size' dans votre modèle CartItem
        cart_item = CartItem.objects.get(product=product, cart=cart, size=size)
        cart_item.quantity += quantity_to_add
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product=product,
            quantity=quantity_to_add,
            cart=cart,
            size=size
        )
    
    return redirect('cart:cart_detail')

def cart_detail(request, total=0, counter=0, cart_items=None):
    """Affiche le contenu du panier, calcule le total et le nombre d'articles."""
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.sub_total()) # Utilise la méthode sub_total du modèle
            counter += cart_item.quantity
    except ObjectDoesNotExist:
        pass
    
    return render(request, 'cart/cart_detail.html', 
                  dict(cart_items=cart_items, total=total, counter=counter))

# Implémentations pour retirer les produits
def remove_cart(request, product_id):
    """Décrémente la quantité d'un produit. Supprime l'article si la quantité est 0."""
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart:cart_detail')

def full_remove(request, product_id):
    """Supprime complètement le CartItem du panier."""
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    return redirect('cart:cart_detail')