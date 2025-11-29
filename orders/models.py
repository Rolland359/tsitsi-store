from django.db import models
from django.conf import settings

class Order(models.Model):
    #info de l'user qui a passer la commande
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    first_name = models.CharField(max_length=50)
    #information clients :
    
    #information commande :
    created = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)