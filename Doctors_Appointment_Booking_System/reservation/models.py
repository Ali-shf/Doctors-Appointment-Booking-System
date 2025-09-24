from decimal import Decimal
from django.conf import settings
from django.db import models

from doctor.models import Clinic
from account.models import Doctor, User


class TimeSheet(models.Model):
    doctor = models.ForeignKey(
        "user_account.Doctor",
        on_delete=models.CASCADE,
        related_name="time_sheets",
    )
    clinic = models.ForeignKey(
        "doctor.Clinic",
        on_delete=models.CASCADE,
        related_name="time_sheets",
    )
    end = models.DateTimeField()
    visit_time = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Time Sheet"
        verbose_name_plural = "Time Sheets"
        ordering = ["doctor", "clinic", "end"]

    def __str__(self) -> str:
        return f"{self.doctor} @ {self.clinic} until {self.end}"

    @property
    def booked_slots(self):
        from .models import Visit
        visit_qs = Visit.objects.filter(
            doctor=self.doctor,
            clinic=self.clinic,
            date=self.end.date(),
            status="completed",
        ).only("start_meet")
        slots = set()
        for v in visit_qs:
            try:
                slots.add(v.start_meet.strftime("%H:%M"))
                slots.add(v.start_meet.strftime("%H:%M:%S"))
            except Exception:
                pass
        return list(slots)


class Visit(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    doctor = models.ForeignKey(
        "user_account.Doctor",
        on_delete=models.CASCADE,
        related_name="visits",
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="patient_visits",
    )
    clinic = models.ForeignKey(
        "doctor.Clinic",
        on_delete=models.CASCADE,
        related_name="visits",
    )
    date = models.DateField()
    start_meet = models.DateTimeField()
    end_meet = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    cart = models.OneToOneField(
        "wallet.Cart",
        on_delete=models.CASCADE,
        related_name="visit",
        null=True,
        blank=True,
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Visit"
        verbose_name_plural = "Visits"
        ordering = ["date", "start_meet"]
        constraints = [
            models.UniqueConstraint(
                fields=["doctor", "clinic", "date", "start_meet"],
                name="unique_visit_per_completed_slot",
                condition=models.Q(status="completed"),
            )
        ]

    def __str__(self) -> str:
        return f"Visit {self.pk} - {self.doctor} with {self.patient} on {self.date}"



class VisitLog(models.Model):
    visit = models.ForeignKey(
        Visit,
        on_delete=models.CASCADE,
        related_name="logs"
    )
    description = models.TextField()  
    support_code = models.CharField(max_length=64, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"VisitLog for Visit {self.visit_id} - {self.support_code}"
