from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import CustomUser

# Create your models here.
class Category(models.Model):
    """
    Modele pour les catégories de produits (ex:vêtements, Accessoires, Maison).
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom de la Categorie")
    # Le slug est utilisé pour créer des URLs propres (ex : boutiques/vetements/)
    slug = models.SlugField(max_length = 100, unique = True)
    description = models.TextField(blank=True, verbose_name = "Description")
    class Meta:
        verbose_name = 'Categorie'
        verbose_name_plural = 'Categories'
        ordering = ('name',)

    def __str__(self):
        return self.name
    
    def get_url(self):
        return reverse('store:products_by_category', args=[self.slug])


class Product(models.Model):
    """
    Modele pour un produit unique vendu sur Tsitsi Store.
    """
    #Clé étrangère vers la catégorie. CASCADE signifie que si la catégorie est supprimée, le prooduit l'est aussi.
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Catégorie', related_name='products')
    product_name = models.CharField(max_length=200, unique=True, verbose_name="Nom du Produit")
    # Le slug est utilisé pour l'URL du détail du produit (ex: /produit/t-shirt-coton-bio/)
    slug = models.SlugField(
        max_length=200, 
        unique=True
    )
    description = models.TextField(
        max_length=500, 
        blank=True, 
        verbose_name="Description Détaillée"
    )
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Prix (MGA)"
    )
    images = models.ImageField(
        upload_to='photos/products', 
        verbose_name="Image Principale"
    )
    stock = models.IntegerField(
        verbose_name="Quantité en Stock"
    )
    # is_available permet de retirer le produit de la vente sans le supprimer
    is_available = models.BooleanField(
        default=True, 
        verbose_name="Disponible à la vente"
    )
    # NOUVEAU CHAMP : Seuil qui déclenche une alerte de commande
    reorder_point = models.IntegerField(
        default=5,  # Exemple : Commencer à commander quand il reste 10 unités
        verbose_name="Seuil Critique de Commande"
    )
    created_date = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Date de Création"
    )
    modified_date = models.DateTimeField(
        auto_now=True, 
        verbose_name="Dernière Modification"
    )

    class Meta:
        verbose_name = 'Produit'
        verbose_name_plural = 'Produits'
        # Ordonner du plus récent au plus ancien par défaut
        ordering = ('-created_date',)

    def __str__(self):
        return self.product_name

    def get_times_purchased(self):
        """Retourne le nombre de commandes uniques dans lesquelles ce produit apparaît."""
        # Ceci nécessite l'importation de OrderItem au début du fichier
        from orders.models import OrderItem 
        return OrderItem.objects.filter(product=self, is_ordered=True).count()
        
    def get_average_rating(self):
        """Calcule la note moyenne sur 7 pour ce produit."""
        # Agrégation de Django pour calculer la moyenne des notes (rating)
        from django.db.models import Avg
        return self.reviewandrating_set.filter(is_active=True).aggregate(average=Avg('rating'))['average'] or 0

    # Méthode pour obtenir l'URL d'un produit
    def get_url(self):
        # Assurez-vous d'avoir une URL nommée 'store:product_detail'
        return reverse('store:product_detail', args=[self.category.slug, self.slug])


# -----------------------------------
# NOUVEAU MODÈLE : Images Secondaires
# -----------------------------------
class ProductImage(models.Model):
    """
    Modèle pour les images supplémentaires d'un produit (galerie).
    """
    # Clé étrangère vers le Produit. Si le produit est supprimé, toutes ses images le sont.
    product = models.ForeignKey(
        'Product', 
        on_delete=models.CASCADE, 
        related_name='gallery' # Permet d'accéder aux images via product.gallery.all()
    )
    image = models.ImageField(
        upload_to='photos/product_gallery', 
        verbose_name="Image Additionnelle"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Image de la Galerie'
        verbose_name_plural = 'Images de la Galerie'
        
    def __str__(self):
        return f"Image pour {self.product.product_name}"

class ReviewAndRating(models.Model):
    # Clé étrangère vers le produit évalué
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    # Clé étrangère vers l'utilisateur qui a laissé l'avis
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE) 
    
    # Champ de note (rating) de 1 à 7
    rating = models.IntegerField(
        blank=True,
        null=True,
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(7)],
        verbose_name='Note (sur 7 étoiles)'
    )
    
    # Champ pour le commentaire
    review = models.TextField(max_length=500, blank=True, verbose_name='Commentaire')
    
    # Meta-données
    is_active = models.BooleanField(default=True) # Pour modérer les avis si nécessaire
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Avis et Note"
        verbose_name_plural = "Avis et Notes"
        # Contrainte pour s'assurer qu'un utilisateur ne laisse qu'un seul avis par produit
        unique_together = ('user', 'product') 
    
    def __str__(self):
        return f"{self.rating} étoiles pour {self.product.product_name}"


class ReviewImage(models.Model):
    review = models.ForeignKey(ReviewAndRating, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='photos/reviews/%Y/%m/%d/', verbose_name="Image jointe")
    
    class Meta:
        verbose_name = "Image d'Avis"
        verbose_name_plural = "Images d'Avis"
        
    def __str__(self):
        return f"Image pour l'avis #{self.review.id}"