from django.db import models
from store.models import Product # Importe le modèle Product que nous avons créé
from users.models import CustomUser # Importe votre modèle d'utilisateur personnalisé (si vous en avez un)

# --- Modèle 1 : Cart (Panier) ---
class Cart(models.Model):
    """
    Représente le panier d'achat. Il est lié soit à un utilisateur (si connecté),
    soit à une session.
    """
    # 1. Lien vers l'utilisateur (si connecté). Null=True permet les paniers anonymes.
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        verbose_name="Utilisateur"
    )
    
    # 2. Lien vers la clé de session (pour les utilisateurs anonymes)
    cart_id = models.CharField(
        max_length=250, 
        blank=True, 
        unique=True,
        verbose_name="ID de Session du Panier"
    )
    
    date_added = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Date de Création"
    )

    class Meta:
        verbose_name = 'Panier'
        verbose_name_plural = 'Paniers'
        ordering = ('-date_added',)

    def __str__(self):
        # Affiche l'ID de session ou le nom de l'utilisateur
        return f'Panier de {self.user.username if self.user else self.cart_id}'


# --- Modèle 2 : CartItem (Article du Panier) ---
class CartItem(models.Model):
    """
    Représente un produit et sa quantité dans un panier spécifique.
    """
    # Clé étrangère vers le Panier
    cart = models.ForeignKey(
        Cart, 
        on_delete=models.CASCADE, 
        related_name='items', 
        verbose_name="Panier"
    )
    
    # Clé étrangère vers le Produit de la Boutique
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        verbose_name="Produit"
    )

    size = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        verbose_name="Taille"
    )
    
    quantity = models.IntegerField(
        default=1, 
        verbose_name="Quantité"
    )
    
    # Prix total de cet article (utile pour capturer le prix au moment de l'ajout)
    line_total = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        verbose_name="Total de la Ligne"
    )
    
    is_active = models.BooleanField(
        default=True
    )

    class Meta:
        verbose_name = 'Article du Panier'
        verbose_name_plural = 'Articles du Panier'
        # Contrainte pour éviter d'avoir le même produit plusieurs fois dans le même panier (on augmente la quantité à la place)
        #unique_together = ('cart', 'product')

    def sub_total(self):
        """ Calcule le sous-total : Prix du produit * Quantité """
        return float(self.product.price) * float(self.quantity)

    def __str__(self):
        size_info = f" ({self.size})" if self.size else ""
        return f'{self.quantity} x {self.product.product_name}{size_info} dans le Panier {self.cart.id}'