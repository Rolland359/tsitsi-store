from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    # --- 1. PLACER LES ROUTES FIXES EN PREMIER ---
    path('low-stock/', views.low_stock_report, name='low_stock_report'),
    path('update-stock-ajax/', views.update_stock_ajax, name='update_stock_ajax'),
    path('search/', views.search, name='search'),
    path('categories/', views.category_list_view, name='category_list'),
    path('submit_review/<int:product_id>/', views.submit_review, name='submit_review'),

    # --- 2. LE CATALOGUE ---
    path('', views.products_list_view, name='catalogue'),

    # --- 3. LES SLUGS EN DERNIER (LES "ATTRAPE-TOUT") ---
    # Cette route attrape n'importe quel mot unique après /store/
    path('<slug:category_slug>/', 
         views.products_list_view, 
         name='products_by_category'),
         
    # Cette route attrape n'importe quel duo de mots après /store/
    path('<slug:category_slug>/<slug:product_slug>/', 
         views.product_detail_view, 
         name='product_detail'),
]