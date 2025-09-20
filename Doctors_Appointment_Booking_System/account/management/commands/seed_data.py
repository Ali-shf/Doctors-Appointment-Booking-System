from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker
from account.models import User, Doctor, Patient, Specialty

SEED_PREFIX = "seed_"

class Command(BaseCommand):
    help = "Seed or clean fake data. Usage: seed_data [--number N] [--clean] [--reset]"

    def add_arguments(self, parser):
        parser.add_argument("--number", type=int, default=30,
                            help="Number of users to create")
        parser.add_argument("--clean", action="store_true",
                            help="Delete previously seeded fake data (by prefix)")
        parser.add_argument("--reset", action="store_true",
                            help="Clean then seed again")
        parser.add_argument("--doctors-ratio", type=float, default=0.4,
                            help="Ratio of users to be doctors (0..1)")

    @transaction.atomic
    def handle(self, *args, **opts):
        n = opts["number"]
        is_clean = opts["clean"]
        is_reset = opts["reset"]
        doctors_ratio = min(max(opts["doctors_ratio"], 0.0), 1.0)
        fake = Faker()

        if is_clean or is_reset:
            self._clean()
            if is_clean and not is_reset:
                self.stdout.write(self.style.SUCCESS("✅ Clean complete"))
                return

        # 1) تضمین وجود تخصص‌ها
        self._ensure_specialties()

        # 2) ساخت یوزر/دکتر/بیمار با پیشوند
        self._seed(fake, n, doctors_ratio)
        self.stdout.write(self.style.SUCCESS("Seeding complete"))

    def _clean(self):
        # حذف وابسته‌ها با CASCADE: اول Doctor/Patient بعد User
        doctors = Doctor.objects.filter(user__username__startswith=SEED_PREFIX)
        patients = Patient.objects.filter(user__username__startswith=SEED_PREFIX)
        users = User.objects.filter(username__startswith=SEED_PREFIX)

        d_count = doctors.count()
        p_count = patients.count()
        u_count = users.count()

        doctors.delete()
        patients.delete()
        users.delete()

        self.stdout.write(f"Deleted: Doctors={d_count}, Patients={p_count}, Users={u_count}")

    def _ensure_specialties(self):
        codes = ["GP","CARD","DERM","ENDO","NEUR","ORTH","PED","PSY","RAD","OTHER"]
        for c in codes:
            Specialty.objects.get_or_create(code=c)

    def _seed(self, fake, n, doctors_ratio):
        specs = list(Specialty.objects.all())
        import math, random

        num_doctors = math.floor(n * doctors_ratio)
        num_patients = n - num_doctors

        # Users for doctors
        for i in range(num_doctors):
            uname = f"{SEED_PREFIX}doc{i}"
            phone = "09" + str(100000000 + i)  # یکتا و معتبر
            user = User.objects.create_user(
                username=uname,
                email=f"{uname}@example.com",
                password="TestPassword123",
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                phone=phone,
            )
            doc = Doctor.objects.create(
                user=user,
                university=fake.company(),
                medical_id=f"MED{100000 + i}",
                rate=round(random.uniform(2.5, 5.0), 2),
            )
            if specs:
                doc.specialties.add(*random.sample(specs, k=min(2, len(specs))))

        # Users for patients
        for i in range(num_patients):
            idx = i + num_doctors
            uname = f"{SEED_PREFIX}pat{idx}"
            phone = "09" + str(100000000 + idx)
            user = User.objects.create_user(
                username=uname,
                email=f"{uname}@example.com",
                password="TestPassword123",
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                phone=phone,
            )
            Patient.objects.create(user=user)
