from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.db import transaction
from .forms import RegistrationForm

from .forms import UserUpdateForm, ProfileUpdateForm
from .models import UserProfile # Assurez-vous d'importer UserProfile

@login_required
@transaction.atomic # S'assure que si une erreur survient, aucune modification n'est sauvegardée
def profile_management(request):
    """
    Vue pour gérer la mise à jour des informations de l'utilisateur (CustomUser) 
    et des détails de son profil (UserProfile) sur une seule page.
    """
    
    # Si le formulaire est soumis (POST)
    if request.method == 'POST':
        # Instancier les formulaires avec les données POST et les instances actuelles
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(
            request.POST, 
            request.FILES, # Nécessaire pour gérer l'upload de photo de profil
            instance=request.user.profile
        )
        
        # Vérification et sauvegarde si les deux formulaires sont valides
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            
            messages.success(request, 'Votre profil a été mis à jour avec succès !')
            return redirect('users:profile_management') # Rediriger pour éviter la soumission multiple
            
        else:
            # Si les formulaires ne sont pas valides, afficher un message d'erreur général
            messages.error(request, 'Erreur lors de la mise à jour du profil. Veuillez vérifier les champs.')
            
    # Si la page est chargée (GET)
    else:
        # Instancier les formulaires avec les données de l'utilisateur actuel
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
        
    context = {
        'u_form': u_form, # Formulaire CustomUser
        'p_form': p_form, # Formulaire UserProfile
        'title': 'Gestion de Profil',
    }
    
    return render(request, 'users/profile_management.html', context)


# --- 1. Inscription (Registration) ---

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Connexion automatique après l'inscription (optionnel)
            login(request, user)
            messages.success(request, 'Inscription réussie ! Bienvenue chez Tsitsi Store.')
            return redirect('home') # Rediriger vers la page d'accueil
    else:
        # Initialiser un formulaire vide
        form = RegistrationForm() 
        
    context = {'form': form, 'title': 'Inscription'}
    return render(request, 'users/register.html', context)


# --- 2. Déconnexion (Logout) ---

def user_logout(request):
    logout(request)
    messages.info(request, "Vous êtes déconnecté. À bientôt !")
    return redirect('home') # Rediriger vers l'accueil


@login_required # S'assure que seul un utilisateur connecté peut accéder
def my_account(request):
    """
    Affiche le tableau de bord de l'utilisateur (Historique des commandes, infos).
    """
    # Vous devez importer Order depuis l'application orders
    from orders.models import Order 
    
    # Récupérer l'historique des commandes de l'utilisateur
    orders = Order.objects.filter(user=request.user).order_by('-created')
    
    context = {
        'orders': orders,
        'title': 'Mon Compte',
    }
    return render(request, 'users/my_account.html', context)


@login_required
def edit_profile(request):
    """
    Permet à l'utilisateur de modifier ses informations (UserUpdateForm) 
    et son profil (ProfileUpdateForm).
    """
    
    # Récupérer l'objet UserProfile ou en créer un s'il n'existe pas
    # Note: On utilise get_or_create pour s'assurer qu'un profil existe, même s'il est vide.
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Instancier les deux formulaires avec les données POST et les instances existantes
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            
            messages.success(request, 'Votre profil a été mis à jour avec succès !')
            return redirect('users:my_account')
        else:
            # Afficher les messages d'erreurs génériques pour les formulaires non valides
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')

    else:
        # Afficher les formulaires pré-remplis
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)
        
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'title': 'Modifier mon Profil',
    }
    return render(request, 'users/edit_profile.html', context)