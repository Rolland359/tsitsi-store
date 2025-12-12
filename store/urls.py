from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('submit_review/<int:product_id>/', views.submit_review, name='submit_review'),
    path('search/', views.search, name='search'),
    path("low_stock_report/", views.low_stock_report, name="low_stock_report"),
    path('categories/', views.category_list_view, name='category_list'),

    # 1. Page Catalogue Principale (http://127.0.0.1:8000/boutique/)
    # Cette vue affiche tous les produits.
    path('', views.products_list_view, name='catalogue'),
    # 2. Page Produit par Catégorie (http://127.0.0.1:8000/boutique/vetements/)
    # Le slug permet d'identifier la catégorie à filtrer.
    path('<slug:category_slug>/', 
         views.products_list_view, 
         name='products_by_category'),
         
    # 3. Page Détail Produit (http://127.0.0.1:8000/boutique/vetements/t-shirt-coton/)
    # Elle a besoin du slug de la catégorie et du slug du produit pour être unique et propre.
    path('<slug:category_slug>/<slug:product_slug>/', 
         views.product_detail_view, 
         name='product_detail'),
         
    # 4. Rapport de Stock Critique (Page d'Administration/Interne)
    # L'accès à cette URL devrait être restreint aux super-utilisateurs dans la vue.
    path('rapport/stock-critique/', 
         views.low_stock_report, 
         name='low_stock_report'),
     
     

    
    
]