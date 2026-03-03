from django import forms
from users.models import CustomUser

class UserForm(forms.ModelForm):
    """Formulaire pour créer/modifier un utilisateur via le dashboard."""
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=False,
        help_text="Laissez vide pour conserver le mot de passe actuel"
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput,
        required=False,
        label="Confirmer le mot de passe"
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'is_active', 'is_staff']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+(261) XXX XX XXX'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        # Vérifier que les mots de passe correspondent s'ils sont fournis
        if password or password_confirm:
            if password != password_confirm:
                raise forms.ValidationError("Les mots de passe ne correspondent pas.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Si un nouveau mot de passe est fourni, le définir
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        
        if commit:
            user.save()
        return user
