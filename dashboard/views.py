from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Avg, Count, F, Q
from django.db import models
from django.utils import timezone
from django.db.models.functions import TruncMonth, TruncDay
from datetime import timedelta
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.views.decorators.http import require_POST

import json
from orders.models import Order, OrderItem
from store.models import Category, Product  
from users.models import CustomUser 
from django.contrib.admin.views.decorators import staff_member_required

# --- FONCTIONS DE SÉCURITÉ ---
def is_staff_member(user):
    return user.is_active and user.is_staff
    
@login_required 
@user_passes_test(is_staff_member)
def dashboard(request):
    # --- LOGIQUE DE FILTRE PAR PÉRIODE ---
    period = request.GET.get('period', 'this_month')
    now = timezone.now()
    start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    if period == 'today':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == '7days':
        start_date = now - timedelta(days=7)
    elif period == '30days':
        start_date = now - timedelta(days=30)
    elif period == 'this_year':
        start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

    orders_base = Order.objects.filter(status__in=['Completed', 'Accepted', 'New'])
    orders_filtered = orders_base.filter(created__gte=start_date)

    # KPIs
    total_orders = orders_filtered.count()
    total_revenue = round(orders_filtered.aggregate(Sum('order_total'))['order_total__sum'] or 0, 2)
    average_order_value = round(orders_filtered.aggregate(Avg('order_total'))['order_total__avg'] or 0, 2)
    
    # STATS GLOBALES
    recent_orders = Order.objects.all().select_related('user').order_by('-created')[:5]
    total_products = Product.objects.filter(is_available=True).count()
    low_stock_products = Product.objects.filter(stock__lte=F('reorder_point'), is_available=True).order_by('stock')[:10]
    total_users = CustomUser.objects.filter(is_active=True, is_staff=False).count()

    # GRAPHIQUES
    top_products_data = Product.objects.filter(is_available=True)\
        .annotate(total_sold=Sum('orderitem__quantity', filter=models.Q(orderitem__order__created__gte=start_date)))\
        .filter(total_sold__gt=0)\
        .order_by('-total_sold')[:5]
        
    top_labels = [p.product_name for p in top_products_data]
    top_quantities = [p.total_sold or 0 for p in top_products_data]
    
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

# --- GESTION DES PRODUITS ---

@staff_member_required
def dashboard_products(request):
    keyword = request.GET.get('keyword', '')
    
    # Optimisation select_related pour éviter les requêtes N+1 sur les catégories
    products = Product.objects.select_related('category').all().order_by('-created_date')
    categories = Category.objects.all()
    
    if keyword:
        products = products.filter(
            Q(product_name__icontains=keyword) | 
            Q(category__name__icontains=keyword) |
            Q(description__icontains=keyword)
        )
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # FIX : On passe categories dans le render_to_string pour que le select s'affiche en AJAX
        html = render_to_string('dashboard/partials/product_table_results.html', {
            'products': products,
            'categories': categories
        })
        return JsonResponse({
            'html': html,
            'count': products.count()
        })

    context = {
        'products': products,
        'active_menu': 'products',
        'categories': categories,
        'title': 'Gestion des Produits',
    }
    return render(request, 'dashboard/products.html', context)

@require_POST
@staff_member_required
def update_product_inline(request, pk):
    try:
        product = get_object_or_404(Product, pk=pk)
        
        product.product_name = request.POST.get('product_name', product.product_name)
        product.price = request.POST.get('price', product.price)
        product.stock = request.POST.get('stock', product.stock)
        product.is_available = request.POST.get('is_available') == 'True'
        
        cat_id = request.POST.get('category')
        if cat_id:
            # Plus efficace : assignation par ID
            product.category_id = cat_id
        
        if request.FILES.get('images'):
            product.images = request.FILES.get('images')
            
        product.save()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@require_POST
@staff_member_required
def delete_product_inline(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    return JsonResponse({'status': 'success'})

@staff_member_required
def stock_dashboard(request):
    # On récupère les produits simplement pour éviter l'erreur de prefetch
    products = Product.objects.all().select_related('category')
    
    # Calculs des compteurs
    # On s'assure d'avoir 0 si le résultat est None
    total_stock_sum = products.aggregate(Sum('stock'))['stock__sum'] or 0
    out_of_stock_count = products.filter(stock__lte=0).count()
    low_stock_count = products.filter(stock__gt=0, stock__lt=5).count()
    
    context = {
        'products': products,
        'total_stock_sum': total_stock_sum,
        'out_of_stock_count': out_of_stock_count,
        'low_stock_count': low_stock_count,
    }
    return render(request, 'dashboard/stock.html', context)

@require_POST
def update_stock_ajax(request):
    data = json.loads(request.body)
    product_id = data.get('id')
    new_stock = data.get('new_stock')
    
    try:
        product = Product.objects.get(id=product_id)
        product.stock = new_stock
        product.save()
        return JsonResponse({'success': True})
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Produit non trouvé'})