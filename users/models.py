from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    # info clients:
    phone_number = models.CharField(max_length=15, blank=True, null=True)


    def __str__(self):
        return self.email