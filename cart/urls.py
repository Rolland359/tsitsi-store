from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    # Page de détail du panier (URL: /cart/)
    path('', views.cart_detail, name='cart_detail'), 
    
    # Ajouter un produit au panier (URL: /cart/add/123/)
    path('add/<int:product_id>/', views.add_cart, name='add_cart'),
    
    # Retirer une unité d'un produit (URL: /cart/remove/123/)
    path('remove/<int:product_id>/', views.remove_cart, name='remove_cart'),
    
    # Supprimer complètement l'article (toutes les quantités) (URL: /cart/full_remove/123/)
    path('full_remove/<int:product_id>/', views.full_remove, name='full_remove'),
]
