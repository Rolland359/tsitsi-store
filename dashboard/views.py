from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Avg, Count, F, Q
from django.db import models
from django.utils import timezone
from django.db.models.functions import TruncMonth, TruncDay
from datetime import timedelta
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST

import json
from orders.models import Order, OrderItem
from store.models import Category, Product  
from users.models import CustomUser 
from django.contrib.admin.views.decorators import staff_member_required
import datetime
from django.template.loader import get_template
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

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
    # Calcul du top produits basé sur les OrderItem (plus fiable sur les relations)
    top_items_qs = OrderItem.objects.filter(
        order__created__gte=start_date,
        product__is_available=True
    ).values('product__id', 'product__product_name')\
     .annotate(total_sold=Sum('quantity'))\
     .order_by('-total_sold')[:5]

    top_labels = [item['product__product_name'] for item in top_items_qs]
    top_quantities = [int(item['total_sold']) for item in top_items_qs]
    
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
    

@staff_member_required
def order_dashboard(request):
    orders = Order.objects.all().order_by('-created')
    
    # Logique de recherche AJAX
    query = request.GET.get('q', '')
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        orders = orders.filter(
            Q(order_number__icontains=query) | 
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query)
        )
        html = render_to_string('dashboard/order_list_partial.html', {'orders': orders})
        return JsonResponse({'html': html})

    # Statistiques pour KPIs
    total_orders = orders.count()
    pending_orders = orders.filter(status='New').count()
    cancelled_orders = orders.filter(status='Cancelled').count()
    daily_rev = orders.filter(status='Completed').aggregate(Sum('order_total'))['order_total__sum'] or 0

    # Données Graphique Radar (Besoin de min 3 points pour un radar)
    top_items = OrderItem.objects.values('product__product_name').annotate(total=Sum('quantity')).order_by('-total')[:5]
    top_names = [item['product__product_name'] for item in top_items]
    top_counts = [item['total'] for item in top_items]

    context = {
        'orders': orders,
        'total_orders_count': total_orders,
        'orders_pending_count': pending_orders,
        'orders_cancelled_count': cancelled_orders,
        'daily_revenue': daily_rev,
        'top_product_names': top_names,
        'top_product_counts': top_counts,
    }
    return render(request, 'dashboard/order_dashboard.html', context)

@staff_member_required
@require_POST
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    new_status = request.POST.get('status')
    
    valid_statuses = dict(Order._meta.get_field('status').choices).keys()
    
    if new_status in valid_statuses:
        order.status = new_status
        order.save()
        return JsonResponse({'status': 'success', 'message': f'Commande #{order.order_number} mise à jour.'})
    
    return JsonResponse({'status': 'error', 'message': 'Statut invalide.'}, status=400)


def generate_invoice_pdf(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    order_items = OrderItem.objects.filter(order=order)

    # Créer la réponse HTTP avec le type PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="facture_{order_number}.pdf"'

    # Créer le canevas PDF
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # --- Header ---
    p.setFont("Helvetica-Bold", 20)
    p.drawString(50, height - 50, "TSITSI STORE")
    
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 80, f"Facture N°: {order.order_number}")
    p.drawString(50, height - 100, f"Date: {order.created.strftime('%d/%m/%Y')}")
    p.drawString(50, height - 120, f"Client: {order.full_name()}")

    # --- Tableau des produits ---
    y = height - 160
    p.line(50, y, 550, y) # Ligne de séparation
    y -= 20
    
    p.setFont("Helvetica-Bold", 11)
    p.drawString(50, y, "Produit")
    p.drawString(300, y, "Qté")
    p.drawString(400, y, "Prix Unit.")
    p.drawString(500, y, "Total")
    
    y -= 20
    p.setFont("Helvetica", 10)
    
    for item in order_items:
        product_name = item.product.product_name if item.product else 'Produit supprimé'
        p.drawString(50, y, product_name[:40])
        p.drawString(300, y, str(item.quantity))
        p.drawString(400, y, f"{item.product_price} Ar")
        p.drawString(500, y, f"{item.sub_total()} Ar")
        y -= 20
        if y < 50: # Nouvelle page si nécessaire
            p.showPage()
            y = height - 50

    # --- Total Final ---
    y -= 20
    p.line(50, y + 15, 550, y + 15)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(350, y, f"TOTAL GENERAL: {order.order_total} Ar")

    p.showPage()
    p.save()
    return response