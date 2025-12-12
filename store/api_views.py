from rest_framework import viewsets
from rest_framework import permissions
from .models import Product, Category, ReviewAndRating
from .serializers import ProductSerializer, CategorySerializer, ReviewSerializer
from rest_framework.permissions import AllowAny 
from rest_framework.decorators import action
from rest_framework.response import Response

# ViewSet pour lister et récupérer les détails des produits (Lecture Seule)
class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(is_available=True).order_by('product_name')
    serializer_class = ProductSerializer
    permission_classes = [AllowAny] # Autoriser l'accès à tous pour la lecture

# ViewSet pour lister et récupérer les détails des catégories (Lecture Seule)
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


class ReviewViewSet(viewsets.ModelViewSet):
    # Par défaut, n'affiche que les avis actifs
    queryset = ReviewAndRating.objects.filter(is_active=True).order_by('-created_at')
    serializer_class = ReviewSerializer
    
    # Permission: Les utilisateurs doivent être authentifiés pour créer/modifier/supprimer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] 

    def perform_create(self, serializer):
        """ Assure que l'utilisateur connecté est assigné à l'avis. """
        # La validation pour l'unicité (un seul avis par utilisateur/produit)
        # doit être gérée soit dans les contraintes du modèle, soit dans le serializer.
        
        # Vérifiez si l'utilisateur a déjà soumis un avis pour ce produit
        product = serializer.validated_data['product']
        user = self.request.user
        
        existing_review = ReviewAndRating.objects.filter(user=user, product=product).first()
        
        if existing_review:
            # Si l'avis existe, nous le mettons à jour au lieu d'en créer un nouveau
            serializer.instance = existing_review
            serializer.save(user=user)
        else:
            # Sinon, nous créons un nouvel avis
            serializer.save(user=user)

    # OPTIONNEL: Ajout d'une action pour lister les avis par produit
    @action(detail=False, methods=['get'])
    def by_product(self, request, pk=None):
        """ Récupère les avis pour un produit donné (passé en query_params 'product_id'). """
        product_id = request.query_params.get('product_id')
        if product_id:
            reviews = self.queryset.filter(product_id=product_id)
            serializer = self.get_serializer(reviews, many=True)
            return Response(serializer.data)
        return Response({"detail": "Veuillez fournir un product_id."}, status=400)