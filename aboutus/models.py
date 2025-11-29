from django.db import models

# Create your models here.
class AboutPage(models.Model):
    title = models.CharField(max_length=200)
    story = models.TextField()
    mission = models.TextField()
    vision = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    banner_image = models.ImageField(upload_to='about_banners/', null=True, blank=True)
    photo_image = models.ImageField(upload_to='about_photos/', null=True, blank=True)

    class Meta:
        verbose_name_plural = "Information de la Boutique"
        
    def __str__(self):
        return self.title