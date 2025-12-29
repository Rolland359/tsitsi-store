from django.shortcuts import render, redirect
from django.contrib import messages
from cart.models import Cart, CartItem
from .models import Order, OrderItem
from store.models import Product
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from .forms import OrderForm
from django.contrib.auth.decorators import login_required
from users.models import UserProfile
from django.db import transaction
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
import datetime

# --- FONCTION D'ENVOI D'EMAIL ---
def send_order_confirmation_email(order):
    """Envoie l'email de confirmation après la création de la commande."""
    try:
        current_site = Site.objects.get_current()
        domain = current_site.domain
        protocol = 'https' # 'http' en développement local
        
        order_items = OrderItem.objects.filter(order=order)
        sub_total = order.order_total - order.tax
        
        context = {
            'order': order,
            'order_items': order_items,
            'sub_total': sub_total,
            'domain': domain,
            'protocol': protocol,
        }
        
        html_content = render_to_string('emails/order_confirmation_email.html', context)
        text_content = render_to_string('emails/order_confirmation_email.txt', context)

        subject = f'Confirmation de commande n°{order.order_number}'
        to = order.email
        
        email = EmailMultiAlternatives(subject, text_content, to=[to])
        email.attach_alternative(html_content, "text/html")
        email.send()
    except Exception as e:
        print(f"Erreur Email: {e}")

# --- FONCTIONS UTILITAIRES ---

def _cart_id(request):
    return request.session.get('cart_id')

def calculate_totals(request):
    """Calcule les montants financiers du panier."""
    sub_total = 0
    tax = 0
    grand_total = 0
    TAX_RATE = 0.18 # Exemple: 18% (Ajustez selon votre pays)
    
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for item in cart_items:
            sub_total += item.sub_total()
        
        tax = sub_total * TAX_RATE
        grand_total = sub_total + tax
    except ObjectDoesNotExist:
        cart_items = None

    return sub_total, tax, grand_total, cart_items

# --- VUES ---

def checkout(request):
    """Affiche le formulaire de paiement et le récapitulatif."""
    sub_total, tax, grand_total, cart_items = calculate_totals(request)

    if not cart_items or cart_items.count() <= 0:
        return redirect('store:catalogue')

    # Pré-remplissage des données pour utilisateurs connectés
    initial_data = {}
    if request.user.is_authenticated:
        initial_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'phone': getattr(request.user, 'phone_number', ''),
        }
        try:
            profile = request.user.profile
            initial_data.update({
                'address_line_1': profile.address_line_1,
                'address_line_2': profile.address_line_2,
                'city': profile.city,
                'state': profile.state,
                'country': profile.country,
            })
        except: pass

    form = OrderForm(initial=initial_data)
    
    context = {
        'sub_total': sub_total,
        'tax': tax,
        'grand_total': grand_total,
        'cart_items': cart_items,
        'order_form': form,
    }
    return render(request, 'orders/checkout.html', context)

@transaction.atomic
def place_order(request):
    """Traitement de la commande et décompte des stocks."""
    sub_total, tax, grand_total, cart_items = calculate_totals(request)

    if not cart_items:
        return redirect('cart:cart_detail')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # 1. Création de la commande
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                address_line_1=form.cleaned_data['address_line_1'],
                address_line_2=form.cleaned_data['address_line_2'],
                city=form.cleaned_data['city'],
                state=form.cleaned_data['state'],
                country=form.cleaned_data['country'],
                order_total=grand_total,
                tax=tax,
                ip=request.META.get('REMOTE_ADDR'),
            )
            
            # Génération numéro de commande
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            order.order_number = f"{yr}{mt}{dt}{order.id}"
            order.save()

            # 2. Création OrderItems et Décompte Stock
            for item in cart_items:
                # TRANSFERT DE LA TAILLE DE CARTITEM VERS ORDERITEM
                order_item = OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    product_price=item.product.price,
                    size=item.size, # On garde la trace de la taille achetée !
                    is_ordered=True
                )

                # DÉCOMPTE DU STOCK RÉEL
                product = Product.objects.get(id=item.product.id)
                if product.stock >= item.quantity:
                    product.stock -= item.quantity
                    product.save()
                else:
                    # Sécurité si le stock est devenu insuffisant entre temps
                    messages.error(request, f"Désolé, le stock de {product.product_name} est insuffisant.")
                    raise Exception("Stock insuffisant") # Annule toute la transaction

            # 3. Nettoyage
            CartItem.objects.filter(cart__cart_id=_cart_id(request)).delete()

            # 4. Email
            send_order_confirmation_email(order)

            messages.success(request, "Commande validée !")
            return redirect('orders:order_complete', order_number=order.order_number)
        else:
            messages.error(request, "Veuillez vérifier vos informations.")
            return redirect('orders:checkout')

    return redirect('orders:checkout')

def order_complete(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number)
        order_items = OrderItem.objects.filter(order=order)
        sub_total = order.order_total - order.tax
        
        context = {
            'order': order,
            'order_items': order_items,
            'sub_total': sub_total,
        }
        return render(request, 'orders/order_complete.html', context)
    except:
        return redirect('store:catalogue')

@login_required
def user_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created')
    return render(request, 'orders/user_orders.html', {'orders': orders})

@login_required
def order_detail(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    order_items = OrderItem.objects.filter(order=order)
    sub_total = order.order_total - order.tax
    return render(request, 'orders/order_detail.html', {
        'order': order, 
        'order_items': order_items, 
        'sub_total': sub_total
    })