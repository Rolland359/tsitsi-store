from rest_framework.routers import DefaultRouter
from .api_views import ProductViewSet, CategoryViewSet, ReviewViewSet
from django.urls import path, include

# Créer un routeur DRF
router = DefaultRouter()

# Enregistrer les ViewSets (ceci crée les chemins /api/products/ et /api/categories/)
router.register('products', ProductViewSet)
router.register('categories', CategoryViewSet)
router.register('reviews', ReviewViewSet)

urlpatterns = [
    # Inclure toutes les URLs générées par le routeur
    path('', include(router.urls)),
]