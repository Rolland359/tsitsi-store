from django.contrib import admin
from .models import Order, OrderItem

# -----------------
# 1. Gestion des articles de commande (Inline)
# -----------------

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('product', 'quantity', 'product_price', 'sub_total') 
    can_delete = False
    extra = 0 


# -----------------
# 2. Gestion de la Commande (Order)
# -----------------

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number', 
        'full_name', # Utilisable ici car list_display accepte les méthodes
        'phone', 
        'email', 
        'city', 
        'order_total', 
        'status',
        'created',
        'is_ordered_status',
    )
    
    def is_ordered_status(self, obj):
        return obj.status == 'Completed'
        
    is_ordered_status.boolean = True 
    is_ordered_status.short_description = 'Commandé'
    
    list_filter = ('status', 'created')
    list_display_links = ('order_number', 'full_name')
    search_fields = ('order_number', 'email', 'first_name', 'last_name') # On cherche sur les vrais champs
    ordering = ('-created',)

    # --- CRUCIAL : full_name doit être en lecture seule ---
    readonly_fields = (
        'full_name', # On l'ajoute ici pour qu'il apparaisse dans les fieldsets
        'order_number',
        'order_total', 
        'tax',
        'created',
        'updated'
    )

    fieldsets = (
        (None, {
            'fields': ('user', 'order_number', 'order_total', 'tax', 'status')
        }),
        ('Informations de Livraison', {
            # REMARQUE : On affiche 'full_name' (readonly) 
            # MAIS on doit aussi garder les vrais champs pour pouvoir les éditer
            'fields': (
                'full_name', 
                'first_name', 'last_name', # Ajoute ces champs s'ils existent dans ton modèle
                'phone', 'email', 'address_line_1', 'address_line_2', 'city', 'state', 'country'
            ),
        }),
        ('Dates', {
            'fields': ('created', 'updated'),
        }),
    )

    inlines = [OrderItemInline]