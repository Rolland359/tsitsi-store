from django.contrib import admin
from .models import Category, Product, ProductImage, ReviewAndRating, ReviewImage

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Configuration de l'interface d'administration pour le modèle Category.
    """
    list_display = ('name', 'slug', 'description')
    prepopulated_fields = { 'slug' : ('name', )}
    search_fields = ('name', )

# -----------------------------------
# 1. Image Inline
# -----------------------------------

class ProductImageInline(admin.TabularInline):
    """
    Permet d'ajouter des ProductImages sur la page d'édition du Product.
    """
    model = ProductImage
    # Afficher le champ image et la date de création
    fields = ('image', 'created_at') 
    readonly_fields = ('created_at',)
    # Afficher 3 champs vides par défaut pour l'ajout (pour correspondre à votre design)
    extra = 3 

# -----------------------------------
# 2. Product Admin (Ajouter l'Inline)
# -----------------------------------

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Configuration de l'interface d'administration pour le modèle Product.
    Permet une gestion rapide des stocks et des disponibilités.
    """
    list_display = (
        'product_name', 
        'price',
        'stock', # Rendre visible le stock dans la liste
        'reorder_point', # Rendre visible le seuil critique
        'category',
        'modified_date',
        'is_available', # Rendre visible la disponibilité
    )

    # AJOUTER L'INLINE ICI
    inlines = [ProductImageInline]

    list_display_links = (
        'product_name',
    )
    list_editable = (
        'price',        # Permet de modifier le prix directement dans la liste
        'stock',        # Permet de modifier le stock directement dans la liste
        'is_available', # Permet de changer la disponibilité directement dans la liste
    )
    
    # Le slug sera automatiquement rempli à partir du champ 'product_name'
    prepopulated_fields = {
        'slug': ('product_name',)
    }
    
    # Options de recherche rapide
    search_fields = (
        'product_name', 
        'description',
    )
    
    # Filtres pour une navigation rapide
    list_filter = (
        'is_available', 
        'category', 
        'created_date',
        ('stock', admin.DateFieldListFilter), # Peut ajouter des filtres basés sur le stock si besoin
    )
    
    # Organisation des champs sur la page d'édition/création
    fieldsets = (
        ('Détails du Produit', {
            'fields': (
                ('product_name', 'slug'), 
                'category', 
                'description',
                'images',
            ),
        }),
        ('Prix et Gestion de Stock', {
            # Les champs critiques sont groupés
            'fields': (
                'price', 
                'stock', 
                'reorder_point', 
                'is_available'
            ),
        }),
    )
    
# Admin pour les images d'avis (comme inline dans l'admin de l'avis)
class ReviewImageInline(admin.TabularInline):
    model = ReviewImage
    extra = 1

@admin.register(ReviewAndRating)
class ReviewAndRatingAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'is_active', 'created_at')
    list_filter = ('is_active', 'rating', 'created_at')
    inlines = [ReviewImageInline] # Intégration des images directement dans le formulaire d'avis