# orders/api_urls.py

from rest_framework.routers import DefaultRouter
from .api_views import OrderViewSet
from django.urls import path, include

router = DefaultRouter()

# Enregistrement du ViewSet pour générer /api/orders/
router.register('orders', OrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
]