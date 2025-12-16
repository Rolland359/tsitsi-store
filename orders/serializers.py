# orders/serializers.py

from rest_framework import serializers
from .models import Order, OrderProduct
from store.models import Product # Assurez-vous d'importer le modèle Product
from store.serializers import ProductSerializer # Réutilisons le Serializer du produit

# Serializer pour un article de commande individuel (OrderProduct)
class OrderProductSerializer(serializers.ModelSerializer):
    # Affiche les détails du produit au lieu de l'ID
    product = ProductSerializer(read_only=True) 
    
    # Champ calculé pour le sous-total de l'article dans la commande
    sub_total = serializers.SerializerMethodField()

    class Meta:
        model = OrderProduct
        fields = ('product', 'quantity', 'product_price', 'sub_total')
        
    def get_sub_total(self, obj):
        # Utilise le prix enregistré au moment de la commande
        return obj.quantity * obj.product_price

# Serializer principal pour la Commande (Order)
class OrderSerializer(serializers.ModelSerializer):
    # Liste des articles dans la commande
    order_products = OrderProductSerializer(many=True, read_only=True, source='orderproduct_set')
    
    # Champ pour indiquer la méthode de paiement (utilisé pour le POST)
    payment_method_input = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Order
        fields = (
            'id', 
            'order_number', 
            'full_name', 
            'phone', 
            'email',
            'order_total', 
            'tax', 
            'status', 
            'is_ordered', 
            'created_at',
            'order_products', 
            'payment_method_input' # Champ d'entrée
        )
        read_only_fields = ('order_number', 'order_total', 'tax', 'status', 'is_ordered', 'created_at')

    # Note: La méthode `create` est complexe et sera gérée dans le ViewSet, 
    # car elle nécessite la conversion des CartItems en OrderProducts et la mise à jour des stocks.