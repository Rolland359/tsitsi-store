from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    """
    Formulaire utilisé pour capturer les informations de livraison et de facturation
    lors du processus de paiement.
    """
    class Meta:
        model = Order
        # Liste des champs que le client doit remplir pour la livraison/contact
        fields = [
            'first_name', 'last_name', 'phone', 'email', 
            'address_line_1', 'address_line_2', 'country', 'state', 'city'
        ]
        
        # Ajoutez des classes Bootstrap pour la mise en forme (CSS)
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 034 xx xxx xx'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'votre.email@exemple.com'}),
            'address_line_1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Adresse (N° et rue)'}),
            'address_line_2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Appartement, bâtiment (Optionnel)'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pays'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Région / Province'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ville'}),
        }