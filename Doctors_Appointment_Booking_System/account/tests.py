from django.test import TestCase, tag
from django.urls import reverse
from django.contrib.auth import get_user_model
from pandas.core.generic import make_doc

from .models import Doctor, Patient, Specialty
User = get_user_model()


def make_user(username='test', first_name='test',
              last_name='test', phone='09125350828', email='test@gmail.com', password='12345'
              ):
    return User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                    phone=phone, email=email, password=password)


def make_patient(user):
    return Patient.objects.create(user=user)


def make_specialty(code):
    return Specialty.objects.create(code=code)


def make_doctor(user, medical_id='12345', specs=None):
    doctor = Doctor.objects.create(user=user, medical_id=medical_id)
    if specs:
        doctor.specialties.add(*specs)
    return doctor

class DoctorListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.u1 = make_user(
            username='ali_mohamadi', first_name='ali', last_name='mohamadi', phone='09125350828',
            email='ali@gmial.com', password='12345',
        )
        cls.u2= make_user(
            username='sara_ahmadi', first_name='sara', last_name='ahmadi', phone='09190908057',
            email='sara@gmail.com', password='12345',
        )
        cls.u3 = make_user(
            username='amir_akbari', first_name='amir', last_name='akbari', phone='09123245173',
            email='amir@gmail.com', password='12345',
        )
        cls.s1 = make_specialty("CARD")
        cls.s2 = make_specialty("DERM")
        cls.d1 = make_doctor(user=cls.u1, medical_id='1234', specs=[cls.s1])
        cls.d2 = make_doctor(user=cls.u2, medical_id='12345', specs=[cls.s1, cls.s2])
        cls.p1 = make_patient(user=cls.u3)

    @tag("basic")
    def test_basic_200_user_template(self):
        url = reverse('doctors_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'doctors_list.html')
        self.assertContains(response, self.d1.user.get_full_name())
        self.assertContains(response, self.d2.user.get_full_name())

    @tag("search")
    def test_search_by_q_filter(self):
        url = reverse('doctors_list')
        response = self.client.get(url, {'q': 'ali',})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'doctors_list.html')
        self.assertContains(response, self.d1.user.get_full_name())
        self.assertNotContains(response, self.d2.user.get_full_name())

    @tag("filter")
    def test_filter_by_specialty_codes(self):
        url = reverse("doctors_list")
        resp = self.client.get(url, {"specialty": [self.s1.code]})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, self.d1.user.get_full_name())
        self.assertContains(resp, self.d2.user.get_full_name())

        resp = self.client.get(url, {"specialty": [self.s2.code]})
        self.assertNotContains(resp, self.d1.user.get_full_name())
        self.assertContains(resp, self.d2.user.get_full_name())

    # def test_pagination_page_2(self):
    #     url = reverse("doctor_list")
    #     for i in range(15):
    #         u = make_user(username=f'user{i}', first_name='user{i}', last_name='user{i}', phone='09125350828',
    #                       email='user{i}@gmail.com', password='12345'
    #         )
    #
    #         make_doctor(user=u, medical_id=f'12345{i}')
    #
    #     resp_page1 = self.client.get(url, {"page": 1})
    #     self.assertEqual(resp_page1.status_code, 200)
    #
    #     resp_page2 = self.client.get(url, {"page": 2})
    #     self.assertEqual(resp_page2.status_code, 200)

