# from django.core.management.base import BaseCommand
# from faker import Faker
# import random
# from doctor.models import Clinic,Comment
# from account.models import Patient,Doctor
# from cities_light.models import Country, Region, City

# from django.utils import timezone


# fake = Faker()

# class Command(BaseCommand):
#     help = "to creat some fake clinic and comments."


#     def handle(self, *args, **options):

#         cities = list(City.objects.values_list('id', flat=True))

#         def pick_random_city():
#             cid = random.choice(cities)
#             c = City.objects.select_related('region', 'country').get(id=cid)
#             return c

#         self.stdout.write(self.style.WARNING("Seeding started..."))
#         patients = list(Patient.objects.all())
#         doctors = list(Doctor.objects.all())

#         if not patients and not doctors :
#             self.stdout.write(self.style.ERROR("Please complete account first."))
#             return
        
#         clinics = []
#         for _ in range(100):
#             city_detail = pick_random_city()
#             clinic = Clinic.objects.create(
#                 name = fake.company(),
#                 founded_date=fake.date_between(start_date='-20y' , end_date='today'),
#                 address = fake.address(),
#                 city = city_detail,
#                 region = city_detail.region,
#                 country = city_detail.country,
#                 description=fake.paragraph(nb_sentences = 3)

#             )
#             clinics.append(clinic)

#         for clinic in clinics:
#             for _ in range(random.randint(1,5)):
#                 Comment.objects.create(
#                     patient_id=random.choice(patients),
#                     doctor_id = random.choice(doctors),
#                     clinic_id = clinic,
#                     comment=fake.sentence(nb_words=15),
#                     created_at=timezone.now(),
#                     rate = random.randint(0,5)
#                 )
#         self.stdout.write(self.style.SUCCESS("Seeding completed"))


from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from faker import Faker
import random

from doctor.models import Clinic, ClinicDoctor, Comment
from account.models import Patient, Doctor
from cities_light.models import City

fake = Faker()


class Command(BaseCommand):
    help = "Create fake Clinics, link Doctors via ClinicDoctor, and generate Comments."

    def add_arguments(self, parser):
        parser.add_argument("--clinics", type=int, default=100, help="Number of clinics to create")
        parser.add_argument("--min-doctors", type=int, default=1, help="Min doctors per clinic")
        parser.add_argument("--max-doctors", type=int, default=5, help="Max doctors per clinic")
        parser.add_argument("--min-comments", type=int, default=1, help="Min comments per clinic")
        parser.add_argument("--max-comments", type=int, default=5, help="Max comments per clinic")
        parser.add_argument(
            "--purge",
            action="store_true",
            help="Delete existing Clinics/ClinicDoctor/Comments before seeding (⚠️ destructive).",
        )

    def pick_random_city(self, city_ids):
        cid = random.choice(city_ids)
        # select_related برای کاهش N+1 هنگام دسترسی به region/country
        return City.objects.select_related("region", "country").get(id=cid)

    @transaction.atomic
    def handle(self, *args, **options):
        n_clinics = options["clinics"]
        min_doctors = options["min_doctors"]
        max_doctors = options["max_doctors"]
        min_comments = options["min_comments"]
        max_comments = options["max_comments"]
        do_purge = options["purge"]

        # پیش‌نیازها
        patients = list(Patient.objects.all())
        doctors = list(Doctor.objects.all())
        if not patients or not doctors:
            self.stdout.write(self.style.ERROR("Please ensure you have Patients and Doctors first."))
            return

        city_ids = list(City.objects.values_list("id", flat=True))
        if not city_ids:
            self.stdout.write(self.style.ERROR("No cities found in cities_light. Seed/import them first."))
            return

        if do_purge:
            self.stdout.write(self.style.WARNING("Purging existing data..."))
            Comment.objects.all().delete()
            ClinicDoctor.objects.all().delete()
            Clinic.objects.all().delete()

        self.stdout.write(self.style.WARNING("Seeding started..."))

        # 1) ساخت کلینیک‌ها
        clinics = []
        for _ in range(n_clinics):
            city_obj = self.pick_random_city(city_ids)
            clinics.append(
                Clinic(
                    name=fake.company(),
                    founded_date=fake.date_between(start_date="-20y", end_date="today"),
                    address=fake.address(),
                    description=fake.paragraph(nb_sentences=3),
                    city=city_obj,
                    region=city_obj.region,
                    country=city_obj.country,
                )
            )
        Clinic.objects.bulk_create(clinics, batch_size=500)
        clinics = list(Clinic.objects.all())  # refresh with pks

        # 2) اتصال دکترها به کلینیک‌ها از طریق ClinicDoctor (بدون duplicate)
        link_rows = []
        for clinic in clinics:
            k = random.randint(min_doctors, max_doctors)
            chosen_doctors = random.sample(doctors, k=min(k, len(doctors)))
            for d in chosen_doctors:
                link_rows.append(ClinicDoctor(clinic=clinic, doctor=d))
        # unique_together رعایت می‌شود؛ اگر قبلاً purge نکرده‌ایم، بهتر است از try/except عبور کنیم
        ClinicDoctor.objects.bulk_create(link_rows, ignore_conflicts=True, batch_size=1000)

        # برای انتساب کامنتِ دکتر به کلینیکی که واقعاً لینک دارد، یک map بسازیم
        clinic_to_doctors = {
            c.id: list(Doctor.objects.filter(doctor_links__clinic=c).only("id"))
            for c in clinics
        }

        # 3) ساخت کامنت‌ها
        comments = []
        now = timezone.now()

        for clinic in clinics:
            num_comments = random.randint(min_comments, max_comments)
            linked_docs = clinic_to_doctors.get(clinic.id, [])

            for _ in range(num_comments):
                patient = random.choice(patients)
                # تقسیم‌بندی رندوم نوع کامنت:
                # 70%: برای کلینیک + یکی از دکترهای همان کلینیک
                # 20%: فقط برای کلینیک (بدون دکتر)
                # 10%: فقط برای دکتر (بدون کلینیک)
                roll = random.random()
                doctor = None
                clinic_fk = None

                if roll < 0.7 and linked_docs:
                    clinic_fk = clinic
                    doctor = random.choice(linked_docs)
                elif roll < 0.9:
                    clinic_fk = clinic
                    doctor = None
                else:
                    clinic_fk = None
                    doctor = random.choice(doctors)

                comments.append(
                    Comment(
                        patient_id=patient,
                        doctor_id=doctor,
                        clinic_id=clinic_fk,
                        comment=fake.sentence(nb_words=15),
                        created_at=fake.date_time_between(start_date="-2y", end_date="now", tzinfo=timezone.get_current_timezone())
                        if hasattr(timezone, "get_current_timezone")
                        else now,
                        rate=random.randint(0, 5),
                    )
                )

        Comment.objects.bulk_create(comments, batch_size=1000)

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeding completed ✅  Clinics: {len(clinics)}, Links: {len(link_rows)}, Comments: {len(comments)}"
            )
        )
