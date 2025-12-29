from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages  # Import manquant
from django.contrib.auth.decorators import user_passes_test  # Import manquant
from django.http import HttpRequest, HttpResponseRedirect  # Imports pour le typage
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
    # Recherche d'un article existant avec EXACTEMENT ce produit et cette taille
    cart_item, created = CartItem.objects.get_or_create(
        product=product, 
        cart=cart, 
        size=size,
        defaults={'quantity': quantity_to_add}
    )

    if not created:
        # Si la ligne existait déjà, on incrémente la quantité demandée
        cart_item.quantity += quantity_to_add
        
    # Mise à jour du line_total pour la BDD
    cart_item.line_total = float(product.price) * cart_item.quantity
    cart_item.save()
    
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
    
    context = {
        'cart_items': cart_items,
        'total': total,
        'counter': counter,
    }

    return render(request, 'cart/cart_detail.html', context)

# Implémentations pour retirer les produits
def remove_cart(request, product_id, cart_item_id):
    cart = get_object_or_404(Cart, cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    
    try:
        # On cible la ligne précise par son ID unique
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.line_total = float(product.price) * cart_item.quantity
            cart_item.save()
        else:
            cart_item.delete()
    except CartItem.DoesNotExist:
        pass
        
    return redirect('cart:cart_detail')


def full_remove(request, product_id):
    """Supprime complètement le CartItem du panier."""
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        cart_item.delete()
    except CartItem.DoesNotExist:
        pass
    return redirect('cart:cart_detail')

@user_passes_test(lambda u: True) # Ou votre décorateur habituel
def add_cart_from_cart_page(request: HttpRequest, product_id: int, cart_item_id: int) -> HttpResponseRedirect:
    """
    Incrémente la quantité d'un article spécifique directement depuis la page du panier.
    Utilise l'ID de la ligne (cart_item_id) pour gérer correctement les tailles.
    """
    cart = get_object_or_404(Cart, cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    
    try:
        # On cible précisément la ligne (le CartItem)
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        
        # Vérification optionnelle du stock réel
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.line_total = float(product.price) * cart_item.quantity
            cart_item.save()
            messages.success(request, f"Quantité mise à jour pour {product.product_name}.")
        else:
            messages.warning(request, f"Désolé, seul {product.stock} articles sont disponibles en stock.")
            
    except CartItem.DoesNotExist:
        messages.error(request, "Cet article n'est plus dans votre panier.")
        
    return redirect('cart:cart_detail')