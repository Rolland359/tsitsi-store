from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # 1. Page de paiement / Adresses (URL: /orders/checkout/)
    path('checkout/', views.checkout, name='checkout'), 
    
    # 2. Finalisation de la commande (Transfert du panier vers le modèle Order)
    # C'est la vue qui s'occupe de l'enregistrement final de la commande
    path('place_order/', views.place_order, name='place_order'),
    
    # 3. Confirmation de commande (Page d'atterrissage après paiement)
    path('order_complete/<str:order_number>/', views.order_complete, name='order_complete'), # À implémenter plus tard

    path('user_orders/', views.user_orders, name='user_orders'), # Liste des commandes
    path('order_detail/<str:order_number>/', views.order_detail, name='order_detail'), # Détail d'une commande
]