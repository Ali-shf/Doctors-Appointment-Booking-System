from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
import random
from .models import Visit, VisitLog, TimeSheet

@receiver(post_save, sender=Visit)
def visit_post_save(sender, instance, created, **kwargs):
    
    if created:
        return

    if instance.status == "completed":
        # 1. ایجاد لاگ (در صورت نبود)
        if not instance.logs.exists():
            VisitLog.objects.create(
                visit=instance,
                support_code="".join(str(random.randint(0, 9)) for _ in range(8)),
                description="ویزیت شما با موفقیت انجام شد."
            )

        # 2. حذف اسلات از تایم‌شیت
        try:
            with transaction.atomic():
                related_ts = TimeSheet.objects.filter(
                    doctor=instance.doctor,
                    clinic=instance.clinic,
                    end__date=instance.date
                )
                for ts in related_ts:
                    if isinstance(ts.visit_time, list) and instance.start_meet:
                        time_str = instance.start_meet.strftime("%H:%M")
                        updated = [t for t in ts.visit_time if t != time_str]
                        if updated != ts.visit_time:
                            ts.visit_time = updated
                            ts.save(update_fields=["visit_time", "updated_at"])
                            print(f"[Timesheet] Slot {time_str} removed from {ts.id}")
        except Exception as e:
            print(f"Error updating timesheet after visit completion: {e}")

    elif instance.status == "cancelled":
        if not instance.logs.exists():
            VisitLog.objects.create(
                visit=instance,
                support_code="".join(str(random.randint(0, 9)) for _ in range(8)),
                description="ویزیت شما انجام نشد یا پرداخت موفق نبود."
            )
