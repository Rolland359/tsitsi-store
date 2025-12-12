# store/serializers.py

from rest_framework import serializers
from .models import Product, Category, ReviewAndRating, ReviewImage
# Assurez-vous d'importer vos modèles Product et Category

# Serializer pour la Catégorie (si nécessaire pour le produit)
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug')

# Serializer pour le Produit
class ProductSerializer(serializers.ModelSerializer):
    # Affiche la catégorie en utilisant le Serializer CategorySerializer
    category = CategorySerializer(read_only=True) 
    
    # Optionnel: Si vous avez un champ 'price' ou 'stock'
    
    class Meta:
        model = Product
        # Liste des champs que vous voulez exposer via l'API
        fields = (
            'id', 
            'product_name', 
            'slug', 
            'description', 
            'price', 
            'stock', 
            'category', 
            'is_available',
            'created_date'
        )
        
        # Rend certains champs en lecture seule si vous voulez seulement les afficher (GET)
        read_only_fields = ('slug', 'created_date')

# Serializer pour les images jointes à un avis
class ReviewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewImage
        fields = ('id', 'image') # Exposer l'URL de l'image

# Serializer pour l'Avis et la Note
class ReviewSerializer(serializers.ModelSerializer):
    # Affiche le nom d'utilisateur (lecture seule)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True) 
    
    # Affiche l'image de profil de l'utilisateur (lecture seule)
    profile_picture = serializers.ImageField(source='user.profile_picture', read_only=True)
    
    # Intégrer les images d'avis associées (lecture seule)
    images = ReviewImageSerializer(many=True, read_only=True, source='reviewimage_set')
    
    class Meta:
        model = ReviewAndRating
        fields = (
            'id', 
            'product', 
            'user',      # Champ obligatoire pour la création, mais souvent masqué
            'user_name', 
            'profile_picture',
            'review', 
            'rating', 
            'created_at', 
            'images',
        )
        # Ces champs sont automatiques ou gérés par la vue, donc lecture seule
        read_only_fields = ('id', 'user', 'user_name', 'profile_picture', 'created_date', 'images')