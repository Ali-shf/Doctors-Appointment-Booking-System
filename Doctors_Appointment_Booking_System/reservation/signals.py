from django.db.models.signals import post_save
from django.dispatch import receiver
import random

from .models import Visit, VisitLog

@receiver(post_save, sender=Visit)
def create_visit_log(sender, instance, created, **kwargs):
    if not created:
        if instance.status == "completed":
            if not instance.logs.exists():
                VisitLog.objects.create(
                    visit=instance,
                    support_code="".join(str(random.randint(0,9)) for _ in range(8)),
                    description="ویزیت شما با موفقیت انجام شد."
                )
        elif instance.status == "cancelled":
            if not instance.logs.exists():
                VisitLog.objects.create(
                    visit=instance,
                    support_code="".join(str(random.randint(0,9)) for _ in range(8)),
                    description="ویزیت شما انجام نشد یا پرداخت موفق نبود."
                )
