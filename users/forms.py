from django import forms
# Importez les formulaires de base de Django pour l'authentification
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
# Importez vos modèles personnalisés
from .models import CustomUser, UserProfile


# -----------------------------------------------------------
# --- 1. Formulaire d'INSCRIPTION (RegistrationForm) ---
# -----------------------------------------------------------

class RegistrationForm(UserCreationForm):
    """
    Formulaire d'inscription qui étend UserCreationForm de Django 
    pour utiliser le modèle CustomUser et ajouter des champs spécifiques.
    """
    # Ajout des champs personnalisés
    first_name = forms.CharField(max_length=50, required=True, label="Prénom")
    last_name = forms.CharField(max_length=50, required=True, label="Nom")
    phone_number = forms.CharField(max_length=15, required=False, label="Téléphone")
    email = forms.EmailField(max_length=100, required=True, label="Email") # Ajout d'Email car il n'est pas requis par défaut dans UserCreationForm

    class Meta:
        model = CustomUser
        # Champs requis pour la création du compte
        fields = (
            'first_name', 
            'last_name', 
            'phone_number', 
            'email',
            'username', # Laissez le username si vous l'utilisez toujours
        )
        
    # Cette méthode permet d'appliquer les classes Bootstrap à tous les champs
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        
        # S'assurer que le champ email est unique
        self.fields['email'].widget.attrs.update({'placeholder': 'Adresse e-mail'})
        
        # Ajout des classes Bootstrap aux champs
        for field_name, field in self.fields.items():
            if field_name != 'password2': # Exclure la vérification du mot de passe
                 field.widget.attrs.update({'class': 'form-control'})
    
    # Validation personnalisée pour s'assurer que l'email est unique (si non géré dans le modèle)
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet e-mail est déjà utilisé.")
        return email


# -----------------------------------------------------------
# --- 2. Formulaire de Mise à Jour de l'Utilisateur (UserUpdateForm) ---
# -----------------------------------------------------------

class UserUpdateForm(UserChangeForm):
    """
    Formulaire pour mettre à jour les informations de base de l'utilisateur.
    """
    # Nous devons redéfinir email car il est unique et pourrait causer des conflits lors de la mise à jour si on ne le gère pas.
    email = forms.EmailField(max_length=100) 
    
    # Nous utilisons UserChangeForm mais nous devons exclure le mot de passe
    password = None 
    
    class Meta:
        model = CustomUser
        # Champs que l'utilisateur peut éditer
        fields = [
            'first_name', 
            'last_name', 
            'email', 
            'phone_number'
        ]
        
        # Ajout des classes Bootstrap pour la mise en forme
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre prénom'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre nom'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'votre.email@exemple.com'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Téléphone'}),
        }
    
    # Méthode pour éviter l'erreur "Email déjà utilisé" lors de la mise à jour
    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = CustomUser.objects.filter(email=email)
        # Permet à l'utilisateur de conserver son propre email sans erreur d'unicité
        if qs.exists() and qs.first() != self.instance:
            raise forms.ValidationError("Cet e-mail est déjà utilisé par un autre compte.")
        return email


# -----------------------------------------------------------
# --- 3. Formulaire de Mise à Jour de l'Adresse (ProfileUpdateForm) ---
# -----------------------------------------------------------

class ProfileUpdateForm(forms.ModelForm):
    """
    Formulaire pour mettre à jour l'adresse de livraison par défaut stockée dans UserProfile.
    """
    class Meta:
        model = UserProfile
        # Champs que l'utilisateur peut éditer (tous les champs d'adresse du profil)
        fields = [
            'address_line_1', 
            'address_line_2', 
            'city', 
            'state', 
            'country', 
            'profile_picture' 
        ]
        
        # Ajout des classes Bootstrap
        widgets = {
            'address_line_1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Adresse (N° et rue)'}),
            'address_line_2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Appartement, Bâtiment (Optionnel)'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ville'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Région / Province'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pays'}),
        }