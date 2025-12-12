from django.contrib import admin
from .models import Cart, CartItem

# Ceci permet de voir les articles d'un panier directement sur la page du panier
class CartItemInline(admin.TabularInline):
    model = CartItem
    readonly_fields = ('product', 'quantity', 'is_active')
    can_delete = False
    extra = 0

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('cart_id', 'date_added')
    inlines = [CartItemInline]
    search_fields = ('cart_id',)


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'cart', 'quantity', 'is_active')