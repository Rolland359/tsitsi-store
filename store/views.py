# Django core imports
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from django.db.models import F, Q
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import path, include

# Local apps imports
from .models import Product, Category, ProductImage, ReviewAndRating, ReviewImage
from .forms import ReviewForm, ReviewImageForm



def is_superuser_or_staff(user):
    """
    Vérifie si l'utilisateur est un super-utilisateur ou fait partie du staff.
    """
    return user.is_active and (user.is_superuser or user.is_staff)


@user_passes_test(is_superuser_or_staff)
def low_stock_report(request):
    """
    Affiche les produits en stock critique.
    """
    products_to_order = Product.objects.filter(
        stock__lte=F('reorder_point'), 
        is_available=True
    ).select_related('category').order_by('stock')

    if not products_to_order.exists():
        messages.success(request, "Bonne nouvelle ! Aucun produit n'a atteint son seuil critique.")

    context = { 
        'products_to_order' : products_to_order, 
        'products_count' : products_to_order.count(),
        'title': 'Rapport de Stock Critique'
    }
    return render(request, 'store/low_stock_report.html', context)

@user_passes_test(is_superuser_or_staff)
def update_stock_ajax(request):
    """
    Traite la mise à jour rapide du stock depuis la modale.
    """
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        new_quantity = request.POST.get('new_quantity')
        
        try:
            product = get_object_or_404(Product, id=product_id)
            product.stock = int(new_quantity)
            product.save()
            
            messages.success(request, f"Le stock de '{product.product_name}' a été mis à jour avec succès.")
        except (ValueError, TypeError):
            messages.error(request, "Quantité invalide. Veuillez entrer un nombre entier.")
            
    # Redirige vers le rapport pour voir les changements
    return redirect('dashboard:low_stock_report')

# --- 1. Vue du Catalogue (Optimisée avec Tri) ---
def products_list_view(request, category_slug=None):
    categories = Category.objects.all()
    sort = request.GET.get('sort') # Récupération du paramètre de tri
    
    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=current_category, is_available=True)
        title = current_category.name
    else:
        products = Product.objects.filter(is_available=True)
        current_category = None
        title = "Tous les Produits"

    # --- LOGIQUE DE TRI ---
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'latest':
        products = products.order_by('-created_date')
    else:
        products = products.order_by('product_name') # Par défaut
    
    paginator = Paginator(products, 12) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': title,
        'current_category': current_category,
        'categories': categories,
        'page_obj': page_obj,
        'products_count': products.count(),
    }
    return render(request, 'store/catalogue.html', context)


# --- 2. Vue du Détail Produit ---
def product_detail_view(request, category_slug, product_slug):
    """
    Affiche la page de détail d'un produit spécifique.
    """
    try:
        # 1. Récupérer le produit
        product = get_object_or_404(Product, category__slug=category_slug, slug=product_slug)
        
        # 2. Récupérer les images secondaires (la "galerie")
        # Grâce au related_name='gallery' que nous avons défini dans ProductImage
        product_gallery = ProductImage.objects.filter(product=product)

        # 2. Récupérer les avis existants (pour la liste)
        reviews = ReviewAndRating.objects.filter(product=product, is_active=True).order_by('-created_at')
        
        # 3. Créer une instance du formulaire d'avis (pour la soumission)
        review_form = ReviewForm()
        
        # 4. Créer une instance du formulaire d'image (pour l'upload d'images)
        review_image_form = ReviewImageForm()

    except Exception as e:
        # Si le produit n'existe pas ou n'est pas disponible, renvoie 404
        raise e 
        
    context = {
        'product': product,
        'title': product.product_name,
        'product_gallery': product_gallery,
        'reviews': reviews,
        'review_form': review_form, # <-- ASSUREZ-VOUS QUE CE FORMULAIRE EST INCLUS
        'review_image_form': review_image_form,
        # Ici, vous pourriez ajouter des produits similaires, des avis, etc.
    }
    
    # Le template pour la page de détail
    return render(request, 'store/product_detail.html', context)


def category_list_view(request):
    """
    Affiche la liste de toutes les catégories disponibles.
    Nous trions par nom et utilisons .prefetch_related pour optimiser le compte des produits.
    """
    
    # 1. Récupérer toutes les catégories, triées par nom
    # Nous utilisons prefetch_related pour que le compte des produits soit efficace
    categories = Category.objects.all().order_by('name').prefetch_related('products')
    
    context = {
        'title': 'Parcourir les Catégories',
        'categories': categories,
        'total_categories': categories.count(),
    }
    
    return render(request, 'store/category_list_view.html', context)


# --- 2. Recherche (Optimisée avec Tri) ---
def search(request):
    keyword = request.GET.get('keyword', '')
    sort = request.GET.get('sort')
    products = Product.objects.filter(is_available=True)
    
    if keyword:
        products = products.filter(
            Q(description__icontains=keyword) | Q(product_name__icontains=keyword)
        )

    # Appliquer le tri même sur les résultats de recherche
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    else:
        products = products.order_by('-created_date')

    context = {
        'products': products,
        'products_count': products.count(),
        'keyword': keyword,
        'title': f'Résultats pour "{keyword}"',
    }
    return render(request, 'store/search_results.html', context)


def home(request):
    """
    Affiche la page d'accueil avec les produits les plus récents (ou en vedette).
    """
    # Récupérer 8 produits les plus récents ou les plus vendus pour la section "Nouveautés"
    products = Product.objects.filter(is_available=True).order_by('-created_date')[:8]
    
    # Vous pouvez également filtrer par un champ "is_featured" si vous l'ajoutez plus tard:
    # featured_products = Product.objects.filter(is_featured=True, is_available=True)
    
    context = {
        'products': products,
        'title': 'Accueil - Tsitsi Store',
    }
    return render(request, 'store/home.html', context)

# --- 3. Soumission d'Avis (Simplifiée) ---
def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER') 
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        
        # On essaie de récupérer un avis existant pour le mettre à jour, sinon on crée
        try:
            review_instance = ReviewAndRating.objects.get(user=request.user, product=product)
            form = ReviewForm(request.POST, request.FILES, instance=review_instance)
        except ReviewAndRating.DoesNotExist:
            form = ReviewForm(request.POST, request.FILES)

        if form.is_valid():
            data = form.save(commit=False)
            data.product = product
            data.user = request.user
            data.save()

            # Gestion des images (boucle optimisée)
            for i in range(1, 4):
                image_file = request.FILES.get(f'image_{i}')
                if image_file:
                    ReviewImage.objects.create(review=data, image=image_file)

            messages.success(request, 'Merci ! Votre avis a été enregistré.')
    return redirect(url)