from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Avg, Count, F
from django.db import models
from django.http import HttpResponseForbidden
from django.utils import timezone

import json # Nécessaire pour passer les données à Chart.js

from orders.models import Order, OrderItem # Ajout de orderitem pour le Top Produits
from store.models import Product  
from users.models import CustomUser 


# Assurez-vous que seuls les super-utilisateurs (administrateurs) ou le staff peuvent accéder


# Fonction de vérification personnalisée pour le staff
def is_staff_member(user):
    return user.is_active and user.is_staff
    
    
@login_required 
@user_passes_test(is_staff_member) # Limite l'accès aux membres du staff
def dashboard(request):
    """
    Vue principale du Tableau de Bord, affichant les statistiques clés de la boutique.
    """
    # ------------------------------------
    # 1. Statistiques de COMMANDES & REVENU (KPIs)
    # ------------------------------------
    
    completed_orders_qs = Order.objects.filter(status__in=['Completed', 'Accepted'])
    
    total_orders = Order.objects.all().count()
    completed_orders = completed_orders_qs.count()
    
    # Revenu total
    total_revenue = completed_orders_qs.aggregate(Sum('order_total'))['order_total__sum'] or 0.0
    
    # Panier Moyen (Average Order Value)
    average_order_value = completed_orders_qs.aggregate(Avg('order_total'))['order_total__avg'] or 0.0
    
    # Commandes Récentes (pour la table d'activité)
    recent_orders = Order.objects.all().order_by('-created')[:5]

    # ------------------------------------
    # 2. Statistiques des PRODUITS/STOCKS
    # ------------------------------------
    
    total_products = Product.objects.filter(is_available=True).count()
    
    # Produits en stock faible (stock <= reorder_point)
    # Nous limitons à 10 pour le template, mais gardons la query
    low_stock_products = Product.objects.filter(
        stock__lte=models.F('reorder_point'), 
        is_available=True
    ).order_by('stock')[:10]
    
    low_stock_count = low_stock_products.count()
    
    # ------------------------------------
    # 3. Statistiques des UTILISATEURS
    # ------------------------------------
    
    total_users = CustomUser.objects.filter(is_active=True, is_staff=False).count()

    # ------------------------------------
    # 4. Données pour les GRAPHIQUES (Chart.js)
    # ------------------------------------
    
    # A. Top 5 Produits (Basé sur la quantité vendue)
    top_products_data = Product.objects.filter(is_available=True)\
        .annotate(total_sold=Sum('orderitem__quantity'))\
        .order_by('-total_sold')[:5]
        
    # Préparation des données pour Chart.js
    top_labels = [p.product_name for p in top_products_data]
    top_quantities = [p.total_sold or 0 for p in top_products_data]
    
    # B. Graphique des Tendances (Ventes/Commandes par Mois - Simplifié)
    # Pour un graphique réel, vous devriez utiliser des agrégations par mois/jour.
    # Ici, nous allons simuler les données ou utiliser une agrégation simple sur les 6 derniers mois.
    
    # Calcul des 6 derniers mois
    end_date = timezone.now()
    start_date = end_date - timezone.timedelta(days=180) 
    
    # Données statiques/simulées si l'agrégation complexe n'est pas encore faite
    sales_labels = ['Déc', 'Jan', 'Fév', 'Mar', 'Avr', 'Mai'] 
    sales_data = [2500000, 3000000, 3500000, 4200000, 4800000, 5500000]
    orders_data = [25, 30, 40, 45, 50, 60]

    # --- Fin de la préparation des données ---
    
    context = {
        # KPI Commande / Revenu
        'total_orders': total_orders,
        'completed_orders': completed_orders,
        'total_revenue': total_revenue,
        'average_order_value': average_order_value, # Nouveau KPI
        
        # KPI Stock
        'total_products': total_products,
        'low_stock_count': low_stock_products.count(),
        'low_stock_products': low_stock_products,
        
        # KPI Utilisateur
        'total_users': total_users,
        
        # Activité Récente
        'recent_orders': recent_orders,
        
        # Données JSON pour Chart.js (IMPORTANT !)
        # Nous utilisons json.dumps() pour rendre les listes Python lisibles par JavaScript
        'top_products_labels_json': json.dumps(top_labels),
        'top_products_data_json': json.dumps(top_quantities),
        'sales_labels_json': json.dumps(sales_labels),
        'sales_data_json': json.dumps(sales_data),
        'orders_data_json': json.dumps(orders_data),
        
        'title': 'Tableau de Bord Administrateur',
    }
    return render(request, 'dashboard/main_dashboard.html', context)
