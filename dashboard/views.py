from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Avg, Count
from django.db import models

from orders.models import Order # Pour les statistiques de commandes
from store.models import Product  # Pour les statistiques de stock
from users.models import CustomUser # Pour les statistiques utilisateurs

# Assurez-vous que seuls les super-utilisateurs (administrateurs) ou le staff peuvent accéder
@login_required 
def dashboard(request):
    """
    Vue principale du Tableau de Bord, affichant les statistiques clés de la boutique.
    """
    # ------------------------------------
    # 1. Statistiques des COMMANDES
    # ------------------------------------
    
    # Nombre total de commandes passées (y compris celles en attente/annulées)
    total_orders = Order.objects.all().count()
    
    # Commandes complétées (en supposant 'Completed' est le statut final)
    completed_orders = Order.objects.filter(status='Completed').count()
    
    # Revenu total (calculé uniquement sur les commandes marquées comme payées/complétées)
    total_revenue = Order.objects.filter(
        status__in=['Completed', 'Accepted'] # Ajustez les statuts de paiement réel
    ).aggregate(Sum('order_total'))['order_total__sum'] or 0.0
    
    # ------------------------------------
    # 2. Statistiques des PRODUITS/STOCKS
    # ------------------------------------
    
    # Nombre total de produits disponibles (is_available=True)
    total_products = Product.objects.filter(is_available=True).count()
    
    # Produits en stock faible (stock <= reorder_point)
    low_stock_products = Product.objects.filter(
        stock__lte=models.F('reorder_point'), # Utilisation de F pour comparer le stock au seuil
        is_available=True
    ).order_by('stock')
    
    low_stock_count = low_stock_products.count()
    
    # ------------------------------------
    # 3. Statistiques des UTILISATEURS
    # ------------------------------------
    
    # Nombre total d'utilisateurs enregistrés (hors staff et superutilisateurs)
    total_users = CustomUser.objects.filter(is_active=True, is_staff=False).count()

    context = {
        # KPI Commande / Revenu
        'total_orders': total_orders,
        'completed_orders': completed_orders,
        'total_revenue': total_revenue,
        
        # KPI Stock
        'total_products': total_products,
        'low_stock_count': low_stock_count,
        'low_stock_products': low_stock_products[:5], # Afficher les 5 plus critiques
        
        # KPI Utilisateur
        'total_users': total_users,
        
        'title': 'Tableau de Bord Administrateur',
    }
    return render(request, 'dashboard/main_dashboard.html', context)