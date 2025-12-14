from django.shortcuts import render, redirect
from django.contrib import messages
from cart.models import Cart, CartItem
from orders.models import Order, OrderItem
from store.models import Product
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from .forms import OrderForm # NOUVEL IMPORT
from django.contrib.auth.decorators import login_required
from users.models import UserProfile
from django.template.loader import render_to_string # NOUVEL IMPORT
from django.core.mail import EmailMultiAlternatives # NOUVEL IMPORT


# --- NOUVELLE FONCTION D'ENVOI D'EMAIL ---
def send_order_confirmation_email(order):
    """
    Construit et envoie l'email de confirmation de commande.
    """
    # Récupérer le site courant (où self est la requête si disponible)
    current_site = Site.objects.get_current() # Ou Site.objects.get(pk=settings.SITE_ID)
    domain = current_site.domain
    
    # Déterminez le protocole (utilisez 'https' pour la production)
    protocol = 'https'
    try:
        order_items = OrderItem.objects.filter(order=order)
        sub_total = order.order_total - order.tax
        
        context = {
            'order': order,
            'order_items': order_items,
            'sub_total': sub_total,
            'domain': domain,
            'protocol': protocol,
        }
        
        # Rendu des templates
        html_content = render_to_string('emails/order_confirmation_email.html', context)
        text_content = render_to_string('emails/order_confirmation_email.txt', context)

        # Envoi de l'email
        subject = f'Votre commande n°{order.order_number} est confirmée'
        to = order.email
        
        email = EmailMultiAlternatives(subject, text_content, to=[to])
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        print(f"Email de confirmation envoyé à {to} pour la commande {order.order_number}") # Pour le débogage
        
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email de confirmation pour la commande {order.order_number}: {e}")
        # Gérer l'échec de l'envoi sans bloquer l'utilisateur


# Fonctions utilitaires du Panier (nous les copions/réutilisons ici pour la clarté)
def _cart_id(request):
    """Récupère l'ID de session du panier."""
    return request.session.get('cart_id')

def calculate_totals(request):
    """Calcule le sous-total, la taxe (si applicable) et le total final."""
    sub_total = 0
    tax = 0
    grand_total = 0
    
    # Supposons 18% de TVA/Taxe
    TAX_RATE = 0.18 
    
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        
        for item in cart_items:
            sub_total += item.sub_total()
        
        tax = sub_total * TAX_RATE
        grand_total = sub_total + tax
        
    except ObjectDoesNotExist:
        # Si le panier n'existe pas ou est vide
        pass

    return sub_total, tax, grand_total, cart_items

# --- VUES DE COMMANDE ---

def checkout(request):
    """
    1. Affiche le formulaire de livraison/paiement.
    2. Affiche le récapitulatif de commande basé sur le panier.
    """
    
    # Récupérer les totaux et les articles du panier
    sub_total, tax, grand_total, cart_items = calculate_totals(request)

    # Si le panier est vide
    if not cart_items:
        messages.error(request, "Votre panier est vide. Ajoutez des produits avant de passer à la caisse.")
        return redirect('store:catalogue')

    # 1. Initialisation du dictionnaire des données initiales
    initial_data = {}
    
    # 2. Pré-remplissage si l'utilisateur est connecté
    if request.user.is_authenticated:
        
        # Données de CustomUser (Utilisateur)
        initial_data['first_name'] = request.user.first_name
        initial_data['last_name'] = request.user.last_name
        initial_data['email'] = request.user.email
        # Note: 'phone' dans OrderForm correspond à 'phone_number' dans CustomUser
        initial_data['phone'] = request.user.phone_number 

        # Données de UserProfile (Adresse par défaut)
        try:
            profile = request.user.profile
            initial_data['address_line_1'] = profile.address_line_1
            initial_data['address_line_2'] = profile.address_line_2
            initial_data['city'] = profile.city
            initial_data['state'] = profile.state
            initial_data['country'] = profile.country
        except UserProfile.DoesNotExist:
             # Optionnel: gérer le cas où le profil n'existe pas encore (très rare grâce aux signals)
             pass 

        # Si le formulaire a déjà été soumis mais n'était pas valide, on utilise request.POST
        if request.method == 'POST':
            order_form = OrderForm(request.POST)
        else:
            # Sinon, on l'initialise avec les données récupérées
            order_form = OrderForm(initial=initial_data)
    else:
        # Pour les utilisateurs anonymes, on initialise le formulaire vide
        order_form = OrderForm(request.POST or None)

    context = {
        'sub_total': sub_total,
        'tax': tax,
        'grand_total': grand_total,
        'cart_items': cart_items,
        'order_form': order_form, # Le formulaire Django est passé ici
    }
    
    # Le template 'orders/checkout.html' est utilisé
    return render(request, 'orders/checkout.html', context)


def place_order(request):
    """
    Traite la soumission du formulaire de checkout, crée la Commande (Order).
    """
    sub_total, tax, grand_total, cart_items = calculate_totals(request)

    if not cart_items:
         messages.error(request, "Panier vide. Impossible de placer la commande.")
         return redirect('cart:cart_detail')

    if request.method == 'POST':
        form = OrderForm(request.POST) # Récupération des données via le formulaire
        
        if form.is_valid():
            
            # 1. Récupérer les données validées
            data = form.cleaned_data
            
            # 2. Créer la Commande (Order)
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],
                phone=data['phone'],
                address_line_1=data['address_line_1'],
                address_line_2=data['address_line_2'],
                city=data['city'],
                state=data['state'],
                country=data['country'],
                order_total=grand_total,
                tax=tax,
                cart_id_at_order=_cart_id(request)
            )
            
            # Générer un numéro de commande unique
            order.order_number = f"TSITI-{order.id}-{order.created.strftime('%Y%m%d')}"
            order.save()
            
            # 3. Déplacer les articles du Panier vers les OrderItems (même logique qu'avant)
            for item in cart_items:
                # 3a. Créer l'OrderItem
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    product_price=item.product.price,
                    is_ordered=True
                )
                # 3b. DÉCRÉMENTATION DU STOCK (NOUVELLE LOGIQUE)
                product = item.product
                
                # S'assurer que le produit existe avant de modifier le stock
                if product: 
                    # Soustraire la quantité du stock disponible
                    product.stock -= item.quantity 
                    # Assurer que le stock ne devient pas négatif (bonne pratique)
                    if product.stock < 0:
                        product.stock = 0 
                        
                    product.save()
                
            # 4. Vider le Panier et Supprimer les CartItems
            CartItem.objects.filter(cart__cart_id=_cart_id(request)).delete()

            # 5. ENVOYER L'EMAIL DE CONFIRMATIONr
            send_order_confirmation_email(order)

            # 6. Rediriger
            messages.success(request, f"Votre commande {order.order_number} a été enregistrée avec succès.")
            return redirect('orders:order_complete', order_number=order.order_number)
            
        else:
            # Si le formulaire n'est pas valide, afficher un message d'erreur
            messages.error(request, "Erreur dans les informations de livraison. Veuillez vérifier les champs.")
            # Rediriger vers checkout pour réafficher le formulaire (le formulaire non valide sera perdu, il faudra le gérer dans la vue)
            return redirect('orders:checkout')
        
    return redirect('orders:checkout')

def order_complete(request, order_number):
    """
    Affiche la page de confirmation de commande après un paiement réussi.
    """
    
    # 1. Récupérer la commande
    try:
        order = Order.objects.get(order_number=order_number)
        order_items = OrderItem.objects.filter(order=order)
        
        # Le paiement est supposé validé pour cette page
        if not order.paid:
             # Si le paiement n'est pas marqué comme réussi (simulé ou réel),
             # on pourrait rediriger vers une page d'échec ou d'attente.
             # Pour l'instant, on affiche quand même les détails.
             pass 

        # 2. Calculer le sous-total (car Order.order_total inclut déjà la taxe)
        sub_total = order.order_total - order.tax
        
    except Order.DoesNotExist:
        messages.error(request, "Désolé, cette commande est introuvable.")
        return redirect('store:catalogue')

    context = {
        'order': order,
        'order_items': order_items,
        'sub_total': sub_total,
    }
    
    return render(request, 'orders/order_complete.html', context)


@login_required
def user_orders(request):
    """
    Affiche la liste de toutes les commandes passées par l'utilisateur connecté.
    """
    # Récupérer toutes les commandes qui appartiennent à l'utilisateur
    orders = Order.objects.filter(
        user=request.user
    ).order_by('-created') # Trier par la plus récente en premier

    context = {
        'orders': orders,
        'title': 'Mon Historique de Commandes',
    }
    
    return render(request, 'orders/user_orders.html', context)


@login_required
def order_detail(request, order_number):
    """
    Affiche les détails d'une commande spécifique pour l'utilisateur.
    """
    try:
        # Récupérer la commande, mais s'assurer qu'elle appartient à l'utilisateur connecté
        order = Order.objects.get(
            order_number=order_number, 
            user=request.user
        )
        # Récupérer les articles associés
        order_items = OrderItem.objects.filter(order=order)
        
        # Calculer le sous-total pour l'affichage
        sub_total = order.order_total - order.tax
        
    except Order.DoesNotExist:
        messages.error(request, "Désolé, cette commande est introuvable ou vous n'avez pas l'autorisation de la consulter.")
        return redirect('orders:user_orders') # Rediriger vers l'historique

    context = {
        'order': order,
        'order_items': order_items,
        'sub_total': sub_total,
        'title': f'Détails de la commande {order_number}',
    }
    
    return render(request, 'orders/order_detail.html', context)


