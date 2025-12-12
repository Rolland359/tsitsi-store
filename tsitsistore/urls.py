"""tsitsistore URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from store import views as store_views
from rest_framework.routers import DefaultRouter


# Créer un routeur DRF
router = DefaultRouter()


urlpatterns = [
    path('admin/', admin.site.urls),
    # 1. PAGE D'ACCUEIL : Le chemin vide (/) pointe vers la vue home
    path('', store_views.home, name='home'), 
    
    # 2. Inclusions des applications
    path('cart/', include('cart.urls', namespace='cart')),
    path('aboutus/', include('aboutus.urls')),
    path('store/', include('store.urls', namespace='store')),
    path('contact/', include('contact.urls')),
    path('orders/', include('orders.urls', namespace='orders')),
    path('users/', include('users.urls', namespace='users')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    path('notifications/', include('notification.urls')),

    # AJOUTER LE CHEMIN POUR L'API
    path('api/', include('store.api_urls')),

]

# --------------------------------------------------------------------------
# SERVIR LES FICHIERS STATIQUES ET MÉDIA EN MODE DÉVELOPPEMENT
# --------------------------------------------------------------------------

# Ajoutez ces lignes à la fin du fichier:
if settings.DEBUG:
    # Permet à Django de servir les images statiques (CSS, JS, logos, etc.)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Permet à Django de servir les images uploadées (Images Produits)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
