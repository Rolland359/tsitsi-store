from django import forms
from .models import ReviewAndRating, ReviewImage

class ReviewForm(forms.ModelForm):
    
    # 1. Définition du champ 'rating'
    # Nous le définissons ici pour que Django sache qu'il doit le valider.
    # Puisque nous gérons l'affichage des étoiles dans le template avec du JS/HTML, 
    # nous n'avons pas besoin d'un widget visible ici.
    rating = forms.IntegerField(
        required=True, # Rendre la note obligatoire (à ajuster selon votre besoin)
        min_value=1,     # Minimum 1 étoile
        max_value=7      # Maximum 7 étoiles (selon votre système 1-7)
    )
    
    class Meta:
        model = ReviewAndRating
        # 2. INCLURE 'rating' dans la liste des champs
        fields = ['rating', 'review'] 
        
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