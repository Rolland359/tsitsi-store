from django.db import models
from django.conf import settings
from store.models import Product # Importe le modèle Product

# --- Modèle 1 : Order (La Commande) ---
class Order(models.Model):
    """
    Conteneur principal d'une commande, intégrant les informations de l'utilisateur
    et les détails de livraison/statut.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        related_name='orders',
        null=True, 
        blank=True,
        verbose_name="Utilisateur"
    )
    
    first_name = models.CharField(max_length=50, verbose_name="Prénom")
    last_name = models.CharField(max_length=50, verbose_name="Nom")
    email = models.EmailField(max_length=50, verbose_name="Email")
    phone = models.CharField(max_length=15, verbose_name="Téléphone")
    
    address_line_1 = models.CharField(max_length=50, verbose_name="Adresse Ligne 1")
    address_line_2 = models.CharField(max_length=50, blank=True, verbose_name="Adresse Ligne 2 (Optionnel)")
    city = models.CharField(max_length=50, verbose_name="Ville")
    state = models.CharField(max_length=50, verbose_name="État/Province")
    country = models.CharField(max_length=50, verbose_name="Pays")
    
    order_number = models.CharField(max_length=20, unique=True, blank=True, verbose_name="Numéro de Commande")
    order_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Total Commande")
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Taxes")
    
    paid = models.BooleanField(default=False, verbose_name="Payée") 
    
    status = models.CharField(
        max_length=10, 
        choices=[
            ('New', 'Nouvelle'), 
            ('Accepted', 'Acceptée'), 
            ('Completed', 'Terminée'), 
            ('Cancelled', 'Annulée')
        ],
        default='New',
        verbose_name="Statut"
    )
    
    created = models.DateTimeField(auto_now_add=True, verbose_name="Date de Création")
    updated = models.DateTimeField(auto_now=True, verbose_name="Dernière Mise à Jour")
    
    cart_id_at_order = models.CharField(max_length=100, blank=True, null=True)
    
    # AJOUT DU CHAMP IP (pour éviter l'erreur précédente)
    ip = models.CharField(max_length=20, blank=True, verbose_name="Adresse IP")


    class Meta:
        verbose_name = 'Commande'
        verbose_name_plural = 'Commandes'
        ordering = ('-created',)

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return self.order_number or f'Order ID: {self.id}'


# --- Modèle 2 : OrderItem (Article d'une Commande) ---
class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='items', 
        verbose_name="Commande"
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.SET_NULL, 
        null=True, 
        verbose_name="Produit"
    )
    quantity = models.IntegerField(verbose_name="Quantité")
    product_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix unitaire payé")
    
    # AJOUT DU CHAMP SIZE (pour corriger l'erreur actuelle)
    size = models.CharField(max_length=50, blank=True, null=True, verbose_name="Taille")
    
    # On garde variant pour ne rien supprimer
    variant = models.CharField(max_length=100, blank=True, verbose_name="Variante") 

    is_ordered = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Article de Commande'
        verbose_name_plural = 'Articles de Commande'

    def sub_total(self):
        # Sécurité pour éviter l'erreur "NoneType * NoneType"
        if self.product_price is not None and self.quantity is not None:
            return self.product_price * self.quantity
        return 0

    def __str__(self):
        return self.product.product_name if self.product else f'Deleted Product ({self.quantity} x {self.product_price}MGA)'