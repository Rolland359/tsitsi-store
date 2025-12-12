from django import forms

class ContactForm(forms.Form):
    # Les classes Bootstrap 'form-control' restent les mêmes
    nom = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre Nom Complet'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Votre Email'})
    )
    sujet = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sujet de votre message'})
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Votre Message...'})
    )