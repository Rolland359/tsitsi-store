# orders/api_views.py

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.db import transaction

from .models import Order, OrderProduct
from .serializers import OrderSerializer, OrderProductSerializer
from cart.models import CartItem # Pour convertir le panier
from store.models import Product # Pour déduire le stock

class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour la liste et le détail des commandes.
    Utilise ReadOnlyModelViewSet car la création est gérée par la méthode `create_order`.
    """
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated] # Seuls les utilisateurs connectés peuvent voir leurs commandes

    def get_queryset(self):
        """ Filtre les commandes pour n'afficher que celles de l'utilisateur connecté. """
        return self.queryset.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """ Gère la création d'une commande à partir du panier actif. """
        user = request.user
        cart_items = CartItem.objects.filter(user=user, is_active=True) 
        
        # 1. Vérification de l'existence du panier
        if not cart_items:
            return Response({"detail": "Le panier est vide. Impossible de créer la commande."}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Les données postées ne sont que des informations supplémentaires (comme payment_method_input)
        payment_method = serializer.validated_data.pop('payment_method_input', 'Non spécifié')
        
        # 2. Logique de Création de la Commande (Transaction Atomique)
        try:
            with transaction.atomic():
                # Création de l'objet Order (sans le statut 'is_ordered' à True pour l'instant)
                order = Order.objects.create(
                    user=user,
                    # ... (Copiez ici les champs d'adresse de livraison/facturation depuis request.data ou le profil utilisateur) ...
                    # Exemple:
                    full_name=request.data.get('full_name', user.get_full_name()),
                    email=user.email,
                    phone=request.data.get('phone'),
                    
                    order_total=request.data.get('order_total'), # Doit être envoyé par le client (ou recalculé ici)
                    tax=request.data.get('tax', 0),
                    payment_method=payment_method,
                    status='NEW' # Statut initial
                )
                
                # Générer le numéro de commande et le sauvegarder (selon votre méthode)
                # order.order_number = generate_order_number() 
                # order.save()

                # 3. Transfert des CartItems vers OrderProducts et mise à jour du stock
                for item in cart_items:
                    OrderProduct.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        product_price=item.product.price, # Capture le prix au moment de l'achat
                        # ... (gestion des variantes ici si nécessaire) ...
                    )
                    
                    # Déduction du stock
                    product = item.product
                    product.stock -= item.quantity
                    product.save()
                    
                    # Suppression de l'article du panier
                    item.delete()

                # 4. Redirection vers le paiement ou confirmation
                # On retourne les détails de la commande créée.
                # L'application front-end peut ensuite appeler initiate_mobile_money_payment
                
                return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

        except Exception as e:
            # Si une erreur se produit (ex: stock négatif, DB error), la transaction est annulée
            return Response({"detail": f"Erreur lors de la finalisation de la commande: {e}"}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)