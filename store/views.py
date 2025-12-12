from django.db.models import F
from django.contrib.auth.decorators import user_passes_test
from django.urls import path, include
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
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
    Affiche la liste des produits dont le stock actuel est
    inférieur ou égal au seuil critique (reorder_point).
    """
    products_to_order = Product.object.filter(stock__lte=models.F('reorder_point'), is_avaible=True).select_related('category').order_by('stock')

    if not products_to_order.exists():
        messages.success(request, "Bonne nouvelle ! Aucun produit n'a atteint son seuil critique.")

    context = { 'products_to_order' : products_to_order, 
                'products_count' : products_to_order.count(),
                'title': 'Rapport de Stock Critique'
                }
    return render(request, 'low_stock_report.html', context)

# --- 1. Vue du Catalogue et Filtrage par Catégorie ---
def products_list_view(request, category_slug=None):
    """
    Affiche tous les produits ou filtre par catégorie (si category_slug est fourni).
    Gère également la pagination.
    """
    categories = Category.objects.all() # Liste de toutes les catégories pour le menu latéral
    
    # Gérer le filtrage par catégorie
    if category_slug:
        # Tente de récupérer la catégorie par son slug, ou renvoie 404
        current_category = get_object_or_404(Category, slug=category_slug)
        # Filtre les produits : seulement ceux qui sont disponibles ET qui appartiennent à la catégorie courante
        products = Product.objects.filter(
            category=current_category, 
            is_available=True
        ).order_by('product_name')
        title = current_category.name
    else:
        # Affiche tous les produits disponibles
        products = Product.objects.filter(is_available=True).order_by('product_name')
        current_category = None
        title = "Tous les Produits"
    
    # Gérer la pagination (ex: 12 produits par page)
    paginator = Paginator(products, 12) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': title,
        'current_category': current_category,
        'categories': categories,
        'page_obj': page_obj,          # Le set de produits pour la page courante
        'products_count': products.count(),
    }
    
    # Utilise le template catalogue.html que nous avons discuté précédemment
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


def search(request):
    """
    Gère la recherche de produits basée sur un terme saisi (mot-clé).
    """
    products = []
    product_count = 0
    keyword = ''
    
    # Vérifier si la requête contient le terme 'keyword' (généralement envoyé par la barre de recherche en GET)
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        
        # S'assurer que le mot-clé n'est pas vide
        if keyword:
            # Utilisation de l'objet Q pour créer une requête complexe (OR)
            # ie. chercher le mot-clé dans le nom OU la description du produit.
            # icontains est insensible à la casse (i pour insensitive)
            products = Product.objects.order_by('-created_date').filter(
                Q(description__icontains=keyword) | Q(product_name__icontains=keyword),
                is_available=True # Ne montrer que les produits disponibles
            )
            product_count = products.count()

    context = {
        'products': products,
        'products_count': product_count,
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

def submit_review(request, product_id):
    """
    Vue pour gérer la soumission d'un avis (note, commentaire, images) pour un produit spécifique.
    """
    url = request.META.get('HTTP_REFERER') # Pour rediriger l'utilisateur vers la page précédente

    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        
        # 1. Vérifier si l'utilisateur a déjà soumis un avis pour ce produit
        try:
            # Tente de récupérer l'avis existant (pour modification)
            review_object = ReviewAndRating.objects.get(user=request.user, product=product)
            form = ReviewForm(request.POST, instance=review_object) # Utilise l'instance existante
        except ReviewAndRating.DoesNotExist:
            # Si aucun avis n'existe, créer une nouvelle instance
            form = ReviewForm(request.POST)

        # 2. Validation et Sauvegarde du formulaire principal
        if form.is_valid():
            data = ReviewAndRating()
            if 'instance' in locals():
                 data = review

            # Gérer le champ de note : Il est toujours 0 si l'utilisateur ne l'a pas défini.
            # Même si le rating était soumis (depuis le template), cette ligne l'ignorerait.
            data.rating = 0 
            
            # Si vous voulez permettre à l'utilisateur de cliquer sur les étoiles quand même, 
            # et si le champ rating est présent dans request.POST :
            if 'rating' in request.POST and request.POST['rating'].isdigit():
                 data.rating = int(request.POST['rating'])
            else:
                 data.rating = 0 # Par défaut à 0

            data.review = form.cleaned_data['review']
            data.product_id = product_id
            data.user_id = request.user.id
            data.is_active = True
            data.save()
            
            # 3. Gestion des images jointes
            for i in range(1, 4): # On s'attend à 3 champs d'image dans le formulaire
                image_key = f'image_{i}'
                if request.FILES.get(image_key):
                    ReviewImage.objects.create(
                        review=data,
                        image=request.FILES.get(image_key)
                    )

            messages.success(request, 'Merci ! Votre avis a été soumis avec succès.')
            return redirect(url)
        else:
            # En cas d'erreur de validation (ex: note manquante)
            messages.error(request, 'Erreur lors de la soumission de l\'avis. Veuillez corriger le formulaire.')
            return redirect(url)
            
    # Si la méthode n'est pas POST, rediriger simplement
    return redirect(url)