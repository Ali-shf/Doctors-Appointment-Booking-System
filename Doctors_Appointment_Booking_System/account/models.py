from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    GENDER_CHOICES = [
        ("M", "Male"),
        ("F", "Female")
        ("O", "Other"),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    updated_at = models.DateTimeField()
    national_code = models.CharField(max_length=10, blank=True, null=True)

