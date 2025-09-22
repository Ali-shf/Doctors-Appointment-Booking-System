from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from cities_light.models import Country, Region, City
from django.utils import timezone
from account.models import Doctor, Patient

class Clinic(models.Model):
    name = models.CharField(max_length=255)
    founded_date = models.DateField(null=True,blank=True)
    address = models.CharField(max_length=500 , blank=True)
    # working_hours = models.JSONField(default=dict , blank=False)
    description = models.TextField(blank=True)
    country = models.ForeignKey(
        Country, on_delete=models.SET_NULL, null=True, blank=True, related_name="clinics"
    )
    region = models.ForeignKey(
        Region, on_delete=models.SET_NULL, null=True, blank=True, related_name="clinics"
    )
    city = models.ForeignKey(
        City, on_delete=models.SET_NULL, null=True, blank=True, related_name="clinics"
    )

    def is_open(self, dt=None):
        dt = timezone.localtime(dt) if dt else timezone.localtime()
        wd, t = dt.weekday(), dt.time()
        return self.opening_hours.filter(weekday=wd, start__lte=t, end__gt=t).exists()

    def todays_hours(self, dt=None):
        dt = timezone.localtime(dt) if dt else timezone.localtime()
        return list(self.opening_hours.filter(weekday=dt.weekday()).values("start","end"))
    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("doctor:clinic_detail", kwargs={"pk": self.pk})
    


class ClinicOpeningHour(models.Model):
    class Weekday(models.IntegerChoices):
        MONDAY = 0, "Mon"
        TUESDAY = 1, "Tue"
        WEDNESDAY = 2, "Wed"
        THURSDAY = 3, "Thu"
        FRIDAY = 4, "Fri"
        SATURDAY = 5, "Sat"
        SUNDAY = 6, "Sun"

    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name="opening_hours")
    weekday = models.PositiveSmallIntegerField(choices=Weekday.choices) 
    start = models.TimeField() 
    end = models.TimeField()   

    class Meta:
        unique_together = [("clinic", "weekday", "start", "end")]
        constraints = [
            models.CheckConstraint(check=models.Q(end__gt=models.F("start")), name="end_after_start"),
        ]
        ordering = ["clinic", "weekday", "start"]

    def __str__(self):
        return f"{self.clinic.name} {self.get_weekday_display()} {self.start}-{self.end}"





class Comment(models.Model):
    patient_id = models.ForeignKey(Patient, related_name=("comments"), on_delete=models.CASCADE)
    doctor_id = models.ForeignKey(Doctor, related_name=("comments_received"), on_delete=models.CASCADE , null=True, blank=True)
    clinic_id = models.ForeignKey("doctor.Clinic", related_name=("comments_received"), on_delete=models.CASCADE , null=True, blank=True)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    rate = models.IntegerField(validators=[MinValueValidator(0) , MaxValueValidator(5)])

def __str__(self):
    if self.doctor_id and self.clinik_id:
        return f"{self.patient_id} | {self.doctor_id} |  {self.clinic_id} ({self.rate})"
    
    elif self.doctor_id :
        return f"{self.patient_id} | {self.doctor_id} |  'no clinic' ({self.rate})"
    else:
        return f"{self.patient_id} | 'no doctor' |  {self.clinic_id} ({self.rate})"
    

def get_absolute_url(self):
    return reverse("doctor:comment_detail", args=[self.pk])





