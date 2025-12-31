from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard, name='main_dashboard'),
    path('products/', views.dashboard_products, name='products'),
    path('products/update/<int:pk>/', views.update_product_inline, name='update_product_inline'),
    path('products/delete/<int:pk>/', views.delete_product_inline, name='delete_product_inline'),
]