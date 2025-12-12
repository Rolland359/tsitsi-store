from django.contrib import admin
from .models import Order, OrderItem

# -----------------
# 1. Gestion des articles de commande (Inline)
# -----------------

# Ceci permet d'afficher les OrderItems directement sur la page de détail de l'Order
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    # Rend les champs non modifiables dans l'interface d'édition de l'Order
    readonly_fields = ('product', 'quantity', 'product_price', 'sub_total') 
    can_delete = False
    # N'affiche pas de ligne vide pour ajouter un nouvel OrderItem
    extra = 0 


# -----------------
# 2. Gestion de la Commande (Order)
# -----------------

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Champs affichés dans la liste des commandes
    list_display = (
        'order_number', 
        'full_name', 
        'phone', 
        'email', 
        'city', 
        'order_total', 
        'tax',
        'status',
        'created',
        'is_ordered_status',
    )
    def is_ordered_status(self, obj):
        # Cette logique est un exemple ; adaptez-la à la façon dont vous déterminez le statut
        return obj.status == 'Completed' # Exemple : si vous avez un champ 'status'
        
    is_ordered_status.boolean = True # Affiche une icône verte/rouge dans l'admin
    is_ordered_status.short_description = 'Commandé'
    
    # Filtres latéraux (pour trier par statut, date, etc.)
    list_filter = ('status', 'created')
    # Liens cliquables vers la page de détail
    list_display_links = ('order_number', 'full_name')
    # Champs de recherche
    search_fields = ('order_number', 'full_name', 'email')
    # Tri par défaut (du plus récent au plus ancien)
    ordering = ('-created',)

    # Champs en lecture seule
    readonly_fields = (
        'order_number',
        'order_total', 
        'tax',
        'created',
        'updated'
    )

    # Regroupement des champs dans la page de détail
    fieldsets = (
        (None, {
            'fields': ('user', 'order_number', 'order_total', 'tax', 'status')
        }),
        ('Informations de Livraison', {
            'fields': ('full_name', 'phone', 'email', 'address_line_1', 'address_line_2', 'city', 'state', 'country'),
        }),
        ('Dates', {
            'fields': ('created', 'updated'),
        }),
    )

    # Ajouter l'affichage des articles de commande (OrderItemInline)
    inlines = [OrderItemInline]

# Le modèle OrderItem peut ne pas être enregistré seul, car il est géré via OrderAdmin.
# Si vous vouliez le gérer séparément :
# @admin.register(OrderItem)
# class OrderItemAdmin(admin.ModelAdmin):
#     list_display = ('order', 'product', 'quantity', 'product_price', 'is_ordered')