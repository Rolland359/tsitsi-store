from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser, UserProfile # Assurez-vous d'importer UserProfile

# -----------------
# 1. Gestion du Profil Utilisateur (Inline)
# -----------------

# Ceci permet d'éditer le UserProfile directement sur la page de CustomUser
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profil'
    # Ajouter des champs pour l'édition rapide
    fieldsets = (
        (None, {
            'fields': (
                'address_line_1', 
                'address_line_2', 
                'city', 
                'state', 
                'country'
            )
        }),
    )

# -----------------
# 2. Gestion de l'Utilisateur Personnalisé (CustomUser)
# -----------------

@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    # Ajouter l'édition du profil
    inlines = (UserProfileInline,)
    
    # Définir l'ordre et le contenu des champs dans la page d'édition
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Informations Personnelles', {'fields': ('first_name', 'last_name', 'phone_number')}),
        ('Permissions', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            ),
        }),
        ('Dates Importantes', {'fields': ('last_login', 'date_joined')}),
    )
    
    # Affichage dans la liste des utilisateurs
    list_display = (
        'email', 
        'first_name', 
        'last_name', 
        'is_staff', 
        'is_active'
    )
    
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

# Note: UserProfile n'a pas besoin d'être enregistré séparément car il est géré via CustomUserAdmin.