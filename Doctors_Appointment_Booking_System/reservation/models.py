from django.db import models
from doctor.models import Clinic
from account.models import Doctor,User



class TimeSheet(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='time_sheets')
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='time_sheets')
    end = models.DateTimeField()
    visit_time = models.JSONField(help_text="List of available visit times")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Time Sheet"
        verbose_name_plural = "Time Sheets"
        ordering = ['doctor', 'clinic', 'end']

    def __str__(self):
        return f"{self.doctor.user.username} @ {self.clinic.name} until {self.end}"


class Visit(models.Model):
    doctor = models.ForeignKey(
        Doctor, on_delete=models.CASCADE, related_name="visits"
    )
    patient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="patient_visits"
    )
    clinic = models.ForeignKey(
        Clinic, on_delete=models.CASCADE, related_name="visits"
    )
    date = models.DateField()
    start_meet = models.DateTimeField()
    end_meet = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Visit"
        verbose_name_plural = "Visits"
        ordering = ['date', 'start_meet']

    def __str__(self):
        return f"Visit {self.id}: Dr.{self.doctor.user.username} with {self.patient.username}"



class EmailMessage(models.Model):
    visit = models.ForeignKey(
        Visit, on_delete=models.CASCADE, related_name="emails"
    )
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Email Message"
        verbose_name_plural = "Email Messages"
        ordering = ['created_at']

    def __str__(self):
        return f"Email for Visit {self.visit.id}"
