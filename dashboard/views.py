from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Avg, Count, F
from django.db import models
from django.utils import timezone
from django.db.models.functions import TruncMonth, TruncDay
from datetime import timedelta

import json
from orders.models import Order, OrderItem
from store.models import Product  
from users.models import CustomUser 

def is_staff_member(user):
    return user.is_active and user.is_staff
    
@login_required 
@user_passes_test(is_staff_member)
def dashboard(request):
    # --- LOGIQUE DE FILTRE PAR PÉRIODE ---
    period = request.GET.get('period', 'this_month') # Par défaut : ce mois-ci
    now = timezone.now()
    start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0) # Début du mois par défaut

    if period == 'today':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == '7days':
        start_date = now - timedelta(days=7)
    elif period == '30days':
        start_date = now - timedelta(days=30)
    elif period == 'this_year':
        start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

    # Filtrage de base des commandes
    orders_base = Order.objects.filter(status__in=['Completed', 'Accepted', 'New'])
    # Filtrage par période pour les KPIs
    orders_filtered = orders_base.filter(created__gte=start_date)

    # --- 1. KPIs (Période sélectionnée) ---
    total_orders = orders_filtered.count()
    total_revenue = round(orders_filtered.aggregate(Sum('order_total'))['order_total__sum'] or 0, 2)
    average_order_value = round(orders_filtered.aggregate(Avg('order_total'))['order_total__avg'] or 0, 2)
    
    # --- 2. STATS GLOBALES (Indépendantes de la période) ---
    recent_orders = Order.objects.all().order_by('-created')[:5]
    total_products = Product.objects.filter(is_available=True).count()
    low_stock_products = Product.objects.filter(stock__lte=F('reorder_point'), is_available=True).order_by('stock')[:10]
    total_users = CustomUser.objects.filter(is_active=True, is_staff=False).count()

    # --- 3. GRAPHIQUES ---
    # Top Produits sur la période
    top_products_data = Product.objects.filter(is_available=True)\
        .annotate(total_sold=Sum('orderitem__quantity', filter=models.Q(orderitem__order__created__gte=start_date)))\
        .filter(total_sold__gt=0)\
        .order_by('-total_sold')[:5]
        
    top_labels = [p.product_name for p in top_products_data]
    top_quantities = [p.total_sold or 0 for p in top_products_data]
    
    # Tendance des ventes (Groupement par jour si période courte, par mois sinon)
    if period in ['today', '7days']:
        trunc_func = TruncDay('created')
        date_format = '%d %b'
    else:
        trunc_func = TruncMonth('created')
        date_format = '%b %Y'

    sales_by_period = orders_filtered.annotate(period_label=trunc_func)\
        .values('period_label')\
        .annotate(total=Sum('order_total'), count=Count('id'))\
        .order_by('period_label')

    sales_labels = [data['period_label'].strftime(date_format) for data in sales_by_period]
    sales_data = [float(data['total']) for data in sales_by_period]
    orders_chart_data = [data['count'] for data in sales_by_period]

    context = {
        'period': period,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'average_order_value': average_order_value,
        'total_products': total_products,
        'low_stock_count': low_stock_products.count(),
        'low_stock_products': low_stock_products,
        'total_users': total_users,
        'recent_orders': recent_orders,
        'top_products_labels_json': json.dumps(top_labels),
        'top_products_data_json': json.dumps(top_quantities),
        'sales_labels_json': json.dumps(sales_labels),
        'sales_data_json': json.dumps(sales_data),
        'orders_data_json': json.dumps(orders_chart_data),
        'title': 'Tableau de Bord Dynamique',
    }
    return render(request, 'dashboard/main_dashboard.html', context)