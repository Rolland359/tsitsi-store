from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models.signals import post_save 
from django.dispatch import receiver

class CustomUser(AbstractUser):
    # info clients:
    phone_number = models.CharField(max_length=15, blank=True, null=True)


    # Rendre l'email unique et obligatoire
    email = models.EmailField(unique=True) 

    # Les autres champs (first_name, last_name, username) sont gérés par AbstractUser.

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.email

class UserProfile(models.Model):
    """
    Modèle de profil lié 1-à-1 à CustomUser pour stocker les adresses par défaut
    et permettre une extension facile sans modifier CustomUser.
    """
    # Lien 1-à-1 vers l'utilisateur
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='profile',
        verbose_name="Utilisateur"
    )
    
    # Informations d'Adresse de Livraison/Facturation par Défaut
    address_line_1 = models.CharField(max_length=50, blank=True, verbose_name="Adresse Ligne 1")
    address_line_2 = models.CharField(max_length=50, blank=True, verbose_name="Adresse Ligne 2 (Optionnel)")
    city = models.CharField(max_length=50, blank=True, verbose_name="Ville")
    state = models.CharField(max_length=50, blank=True, verbose_name="État/Province")
    country = models.CharField(max_length=50, blank=True, verbose_name="Pays")
    
    # Image de profil (optionnel)
    profile_picture = models.ImageField(upload_to='users/profile_pics/', blank=True, null=True, verbose_name="Photo de Profil")
    
    def __str__(self):
        return f"Profil de {self.user.username}"

    def full_address(self):
        """Retourne l'adresse complète pour affichage."""
        # On utilise une vérification simple pour éviter d'afficher des virgules en trop
        parts = [self.address_line_1, self.city, self.country]
        return ", ".join(filter(None, parts))


# --- SIGNALS pour la création automatique du profil ---

# Crée le profil lorsqu'un CustomUser est créé
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

# Sauvegarde le profil lorsque l'utilisateur est sauvegardé
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)