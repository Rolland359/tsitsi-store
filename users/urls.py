from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'users'

urlpatterns = [
    # 1. INSCRIPTION
    path('register/', views.register, name='register'),

    # 2. CONNEXION (Utilisation de la vue intégrée de Django)
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    
    # 3. DÉCONNEXION
    path('logout/', views.user_logout, name='logout'),
    
    # 4. MON COMPTE (Espace Client - Voir Section 2)
    path('account/', views.my_account, name='my_account'),

    path('profile/', views.profile_management, name='profile_management'),

    path('account/edit/', views.edit_profile, name='edit_profile'),
]