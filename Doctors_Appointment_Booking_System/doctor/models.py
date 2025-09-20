from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from cities_light.models import Country, Region, City
from account.models import Doctor, Patient

class Clinic(models.Model):
    name = models.CharField(max_length=255)
    founded_date = models.DateField(null=True,blank=True)
    address = models.CharField(max_length=500 , blank=True)
    working_hours = models.JSONField(default=dict , blank=False)
    description = models.TextField(blank=True)
    country = models.ForeignKey(
        Country, on_delete=models.SET_NULL, null=True, blank=False, related_name="clinics"
    )
    region = models.ForeignKey(
        Region, on_delete=models.SET_NULL, null=True, blank=False, related_name="clinics"
    )
    city = models.ForeignKey(
        City, on_delete=models.SET_NULL, null=True, blank=False, related_name="clinics"
    )
    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("clinic:detail", kwargs={"pk": self.pk})
    


class Comment(models.Model):
    patient_id = models.ForeignKey(Patient, related_name=("comments"), on_delete=models.CASCADE)
    doctor_id = models.ForeignKey(Doctor, related_name=("comments_received"), on_delete=models.CASCADE , null=True, blank=True)
    clinic_id = models.ForeignKey("doctor.Clinic", related_name=("comments_received"), on_delete=models.CASCADE , null=True, blank=True)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_created=True)
    rate = models.IntegerField(validators=[MinValueValidator(0) , MaxValueValidator(5)])

def __str__(self):
    if self.doctor_id and self.clinik_id:
        return f"{self.patient_id} | {self.doctor_id} |  {self.clinic_id} ({self.rate})"
    
    elif self.doctor_id :
        return f"{self.patient_id} | {self.doctor_id} |  'no clinic' ({self.rate})"
    else:
        return f"{self.patient_id} | 'no doctor' |  {self.clinic_id} ({self.rate})"
    
def get_absolute_url(self):
    return reverse("comment:detail", kwargs={"pk": self.pk})






