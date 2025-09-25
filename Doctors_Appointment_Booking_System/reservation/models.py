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
#complete slot reserve 
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
        print(f"Found {visit_qs.count()} completed visits for timesheet {self.id}")
    # svae every format time
        for v in visit_qs:
            try:
                time_obj = v.start_meet.time()
               
                formats = [
                    time_obj.strftime("%H:%M"),
                    time_obj.strftime("%H:%M:%S"),
                    str(time_obj),
                    str(time_obj.strftime("%H:%M")),
                    v.start_meet.strftime("%H:%M"),
                    v.start_meet.strftime("%H:%M:%S"),
                ]
                
                for fmt in formats:
                    slots.add(fmt)
                    print(f"Added booked slot format: {fmt}")
                    
            except Exception as e:
                print(f"Error processing visit {v.id}: {e}")
                
        result = list(slots)
        print(f"Total booked slots for timesheet {self.id}: {result}")
        return result
# free slot
    @property
    def available_slots(self):
        """Get available time slots (not booked)"""
        if not isinstance(self.visit_time, list):
            return []
        
        booked = set(self.booked_slots)
        available = []
        
        print(f"Checking available slots for timesheet {self.id}")
        print(f"Original slots: {self.visit_time}")
        print(f"Booked slots: {booked}")
        
        for slot in self.visit_time:
            slot_str = str(slot)
            is_booked = False
            
           
            for booked_slot in booked:
                if (slot_str == booked_slot or 
                    slot_str == booked_slot.replace(":", "") or
                    booked_slot in slot_str or
                    slot_str in booked_slot):
                    is_booked = True
                    print(f"Slot {slot_str} is booked (matched with {booked_slot})")
                    break
            
            if not is_booked:
                available.append(slot)
                print(f"Slot {slot_str} is available")
        
        print(f"Final available slots: {available}")
        return available
    
    def get_timesheet_data(self):
        """Get structured timesheet data for templates"""
        booked = self.booked_slots
        available = self.available_slots
        
        
        print(f"Timesheet {self.id} Debug:")
        print(f"  Original slots: {self.visit_time}")
        print(f"  Booked slots: {booked}")
        print(f"  Available slots: {available}")
        print(f"  Total original: {len(self.visit_time) if isinstance(self.visit_time, list) else 0}")
        print(f"  Total booked: {len(booked)}")
        print(f"  Total available: {len(available)}")
        
        total_slots = len(booked) + len(available)
        original_count = len(self.visit_time) if isinstance(self.visit_time, list) else 0
        if total_slots != original_count:
            print(f"  WARNING: Slot count mismatch! Booked({len(booked)}) + Available({len(available)}) = {total_slots}, but original = {original_count}")
        
        return {
            'id': self.id,
            'doctor': self.doctor,
            'clinic': self.clinic,
            'end': self.end,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'booked_slots': booked,
            'available_slots': available,
            'total_slots': len(self.visit_time) if isinstance(self.visit_time, list) else 0,
        }
    # when propery is reserve clean cash
    def refresh_slots(self):
        
        try:
            from django.core.cache import cache
            cache_key = f"timesheet_{self.doctor.id}_{self.clinic.id}_{self.end.date()}"
            cache.delete(cache_key)
            print(f"Cleared cache for timesheet {self.id}")
        except Exception as e:
            print(f"Error clearing cache for timesheet {self.id}: {e}")
    # refresh cash
    def force_refresh(self):
        
        self._booked_slots = None
        self._available_slots = None
        return self.get_timesheet_data()


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
    price = models.DecimalField(max_digits=10, decimal_places=3, default=Decimal("0.00"))
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
