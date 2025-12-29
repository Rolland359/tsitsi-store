from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    # Page de détail du panier
    path('', views.cart_detail, name='cart_detail'), 
    
    # 1. Ajouter depuis la page produit (via formulaire POST)
    path('add/<int:product_id>/', views.add_cart, name='add_cart'),
    
    # 2. Incrémenter (+1) DEPUIS le panier (via lien GET)
    path('add_item/<int:product_id>/<int:cart_item_id>/', 
         views.add_cart_from_cart_page, name='add_cart_from_cart_page'),
    
    # 3. Décrémenter (-1) une unité d'une ligne spécifique
    path('remove/<int:product_id>/<int:cart_item_id>/', 
         views.remove_cart, name='remove_cart'),
    
    # 4. Supprimer complètement une ligne (la poubelle)
    path('full_remove/<int:product_id>/<int:cart_item_id>/', 
         views.full_remove, name='full_remove'),
]