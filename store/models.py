from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import CustomUser
from django.db.models import Avg

# Import pour le redimensionnement automatique
from django_resized import ResizedImageField

class Category(models.Model):
    """Modele pour les catégories de produits."""
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom de la Categorie")
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, verbose_name="Description")

    class Meta:
        verbose_name = 'Categorie'
        verbose_name_plural = 'Categories'
        ordering = ('name',)

    def __str__(self):
        return self.name
    
    def get_url(self):
        return reverse('store:products_by_category', args=[self.slug])


class Product(models.Model):
    """Modele pour un produit unique vendu sur Tsitsi Store."""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Catégorie', related_name='products')
    product_name = models.CharField(max_length=200, unique=True, verbose_name="Nom du Produit")
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(max_length=500, blank=True, verbose_name="Description Détaillée")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix (MGA)")
    
    # CORRECTION : Utilisation de ResizedImageField pour éviter les erreurs PIL/S20
    # force le format JPG, compresse à 75% et limite à 800px
    images = ResizedImageField(
        size=[800, 800], 
        quality=75, 
        crop=['middle', 'center'],
        upload_to='photos/products', 
        force_format='JPEG',
        verbose_name="Image Principale"
    )
    
    stock = models.IntegerField(verbose_name="Quantité en Stock")
    is_available = models.BooleanField(default=True, verbose_name="Disponible à la vente")
    reorder_point = models.IntegerField(default=5, verbose_name="Seuil Critique de Commande")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Date de Création")
    modified_date = models.DateTimeField(auto_now=True, verbose_name="Dernière Modification")

    class Meta:
        verbose_name = 'Produit'
        verbose_name_plural = 'Produits'
        ordering = ('-created_date',)

    def __str__(self):
        return self.product_name

    def get_times_purchased(self):
        from orders.models import OrderItem 
        return OrderItem.objects.filter(product=self, is_ordered=True).count()
        
    def get_average_rating(self):
        # Utilisation de l'import global fait en haut du fichier
        return self.reviewandrating_set.filter(is_active=True).aggregate(average=Avg('rating'))['average'] or 0

    def get_url(self):
        return reverse('store:product_detail', args=[self.category.slug, self.slug])


class ProductImage(models.Model):
    """Galerie d'images redimensionnées."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='gallery')
    # CORRECTION : Aussi sur la galerie pour les photos du téléphone
    image = ResizedImageField(
        size=[800, 800], 
        quality=75, 
        upload_to='photos/product_gallery',
        force_format='JPEG',
        verbose_name="Image Additionnelle"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Image de la Galerie'
        verbose_name_plural = 'Images de la Galerie'

    def __str__(self):
        return f"Image pour {self.product.product_name}"


class ReviewAndRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE) 
    rating = models.IntegerField(
        blank=True, null=True, default=3,
        validators=[MinValueValidator(1), MaxValueValidator(7)],
        verbose_name='Note (sur 7 étoiles)'
    )
    review = models.TextField(max_length=500, blank=True, verbose_name='Commentaire')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Avis et Note"
        verbose_name_plural = "Avis et Notes"
        unique_together = ('user', 'product') 
    
    def __str__(self):
        return f"{self.rating} étoiles pour {self.product.product_name}"


class ReviewImage(models.Model):
    review = models.ForeignKey(ReviewAndRating, on_delete=models.CASCADE, related_name='images')
    # CORRECTION : Redimensionnement aussi pour les avis clients (souvent des photos mobiles)
    image = ResizedImageField(
        size=[600, 600], 
        quality=70, 
        upload_to='photos/reviews/%Y/%m/%d/',
        force_format='JPEG',
        verbose_name="Image jointe"
    )
    
    class Meta:
        verbose_name = "Image d'Avis"
        verbose_name_plural = "Images d'Avis"
        
    def __str__(self):
        return f"Image pour l'avis #{self.review.id}"