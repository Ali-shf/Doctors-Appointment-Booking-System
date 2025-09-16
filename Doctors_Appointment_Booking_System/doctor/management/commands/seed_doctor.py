from django.core.management.base import BaseCommand
from faker import Faker
import random
from doctor.models import Clinic,Comment
from account.models import Patient,Doctor

from django.utils import timezone


faker = Faker()

class Command(BaseCommand):
    help = "to creat some fake clinic and comments."

    def handle(self, *args, **options):

        self.stdout.write(self.style.WARNING("Seeding started..."))
        patients = list(Patient.objects.all)
        doctors = list(Doctor.objects.all)

        if not patients and not doctors :
            self.stdout.write(self.style.ERROR("Please complete account first."))
            return
        
        clinics = []
        for _ in range(100):
            clinic = Clinic.objects.create(
                name = faker.company(),
                founded_date=faker.date_between(start_date='-20y' , end_date='today'),
                address = faker.address(),
                working_hours={"sat": "09:00-17:00",
                    "sun": "09:00-17:00",
                    "mon": "09:00-17:00",
                    "tue": "09:00-17:00",
                    "wed": "09:00-17:00",
                    "thu": "09:00-17:00",
                    "fri": "closed",
                }, description=faker.paragraph(nb_sentences = 3)

            )
            clinics.append(clinic)

        for clinic in clinics:
            for _ in range(random.randint(1,5)):
                Comment.objects.create(
                    patient_id=random.choice(patients),
                    doctor_id = random.choice(doctors),
                    clinic_id = clinic,
                    Comment=faker.sentence(nb_words=15),
                    created_at=timezone.now(),
                    rate = random.randint(0,5)
                )
        self.stdout.write(self.style.SUCCESS("Seeding completed"))
