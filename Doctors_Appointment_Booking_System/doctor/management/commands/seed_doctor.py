from django.core.management.base import BaseCommand
from faker import Faker
import random
from doctor.models import Clinic,Comment
from account.models import Patient,Doctor
from cities_light.models import Country, Region, City

from django.utils import timezone


fake = Faker()

class Command(BaseCommand):
    help = "to creat some fake clinic and comments."


    def handle(self, *args, **options):

        cities = list(City.objects.values_list('id', flat=True))

        def pick_random_city():
            cid = random.choice(cities)
            c = City.objects.select_related('region', 'country').get(id=cid)
            return c

        self.stdout.write(self.style.WARNING("Seeding started..."))
        patients = list(Patient.objects.all())
        doctors = list(Doctor.objects.all())

        if not patients and not doctors :
            self.stdout.write(self.style.ERROR("Please complete account first."))
            return
        
        clinics = []
        for _ in range(100):
            city_detail = pick_random_city()
            clinic = Clinic.objects.create(
                name = fake.company(),
                founded_date=fake.date_between(start_date='-20y' , end_date='today'),
                address = fake.address(),
                city = city_detail,
                region = city_detail.region,
                country = city_detail.country,
                # working_hours={"sat": "09:00-17:00",
                #     "sun": "09:00-17:00",
                #     "mon": "09:00-17:00",
                #     "tue": "09:00-17:00",
                #     "wed": "09:00-17:00",
                #     "thu": "09:00-17:00",
                #     "fri": "closed",
                # },
                description=fake.paragraph(nb_sentences = 3)

            )
            clinics.append(clinic)

        for clinic in clinics:
            for _ in range(random.randint(1,5)):
                Comment.objects.create(
                    patient_id=random.choice(patients),
                    doctor_id = random.choice(doctors),
                    clinic_id = clinic,
                    comment=fake.sentence(nb_words=15),
                    created_at=timezone.now(),
                    rate = random.randint(0,5)
                )
        self.stdout.write(self.style.SUCCESS("Seeding completed"))
