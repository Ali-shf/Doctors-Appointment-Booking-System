from django.db import models
from django.contrib.auth.models import AbstractUser
from cities_light.models import Country, Region, City
from django.conf import settings


class User(AbstractUser):
    GENDER_CHOICES = [
        ("M", "Male"),
        ("F", "Female"),
        ("O", "Other"),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    national_code = models.CharField(max_length=10, blank=True, null=True)

    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    province = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)

    address = models.TextField(blank=True, null=True)

    def is_doctor(self) -> bool:
        return hasattr(self, "doctor_profile")


class Specialty(models.Model):
    class Code(models.TextChoices):
        GP          = "GP",   "General Practice"
        CARDIOLOGY  = "CARD", "Cardiology"
        DERMATOLOGY = "DERM", "Dermatology"
        ENDOCRINO   = "ENDO", "Endocrinology"
        NEUROLOGY   = "NEUR", "Neurology"
        ORTHOPEDIC  = "ORTH", "Orthopedics"
        PEDIATRICS  = "PED",  "Pediatrics"
        PSYCHIATRY  = "PSY",  "Psychiatry"
        RADIOLOGY   = "RAD",  "Radiology"
        OTHER       = "OTHER","Other"

    code = models.CharField(
        max_length=5,
        choices=Code.choices,
        unique=True,
    )

    def __str__(self):
        return self.get_code_display()


class Doctor(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="doctor_profile",
    )
    university = models.CharField(max_length=50, blank=True, null=True)
    contract_started = models.DateTimeField(blank=True, null=True)
    contract_end = models.DateTimeField(blank=True, null=True)
    medical_id = models.CharField(max_length=20, unique=True)
    rate = models.FloatField(blank=True, null=True)
    specialties = models.ManyToManyField(Specialty, related_name="doctors", blank=True)

    def __str__(self):
        n = self.user.get_full_name() or self.user.username
        return f"Dr. {n}"

    def get_specialties(self):
        return ", ".join(specialty for specialty in self.specialties.all())