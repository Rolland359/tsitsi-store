from django import forms
from .models import ReviewAndRating, ReviewImage

class ReviewForm(forms.ModelForm):
    
    #rating = forms.IntegerField(widget=forms.HiddenInput()) 
    
    class Meta:
        model = ReviewAndRating
        fields = ['review'] # L'utilisateur et le produit seront ajoutés dans la vue
        
        widgets = {
            'review': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Votre avis détaillé...'}),
        }

# Formulaire pour uploader des images pour l'avis
class ReviewImageForm(forms.ModelForm):
    class Meta:
        model = ReviewImage
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }