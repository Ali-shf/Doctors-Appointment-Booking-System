from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.validators import RegexValidator
from .models import Country, Region, City, Doctor, Patient, Specialty
from django.contrib.auth import get_user_model
import re

User = get_user_model()

ROLE_CHOICES = [
    ("patient", "Patient"),
    ("doctor", "Doctor"),
]

iran_phone_regex = RegexValidator(
    regex=r'^(?:\+98|0)?9\d{9}$',
    message="شماره موبایل باید با 09XXXXXXXXX یا +989XXXXXXXXX باشد."
)

class PrettyMixin:
    """Add Bootstrap classes + placeholders automatically."""
    def _beautify(self):
        for name, field in self.fields.items():
            css = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (css + " form-control").strip()
            if not field.widget.attrs.get("placeholder"):
                field.widget.attrs["placeholder"] = field.label or name.replace("_", " ").title()

class RegisterForm(PrettyMixin, UserCreationForm):
    username = forms.CharField(label="Username", max_length=150)
    email = forms.EmailField(label="Email", required=True)

    phone = forms.CharField(
        label="Phone",
        max_length=13,
        required=True,
        validators=[iran_phone_regex],
        help_text="example: 09123456789 or +989123456789"
    )

    gender = forms.ChoiceField(choices=User.GENDER_CHOICES, required=False)
    national_code = forms.CharField(max_length=10, required=False, label="National Code")

    country = forms.ModelChoiceField(queryset=None, required=False)
    province = forms.ModelChoiceField(queryset=None, required=False)
    city = forms.ModelChoiceField(queryset=None, required=False)

    address = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), required=False)

    role = forms.ChoiceField(choices=ROLE_CHOICES, label="I am a")

    specialties = forms.ModelMultipleChoiceField(
        queryset=Specialty.objects.all(), required=False,
        widget=forms.SelectMultiple(attrs={"size": 6})
    )
    medical_id = forms.CharField(max_length=20, required=False, help_text="Required for doctors.")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = [
            "username", "email", "phone", "password1", "password2",
            "gender", "national_code",
            "country", "province", "city",
            "address",
            "role", "specialties", "medical_id",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["country"].queryset = Country.objects.all()
        self.fields["province"].queryset = Region.objects.all()
        self.fields["city"].queryset = City.objects.all()
        self._beautify()

    def clean(self):
        data = super().clean()
        role = data.get("role")
        medical_id = data.get("medical_id")
        if role == "doctor" and not medical_id:
            self.add_error("medical_id", "Medical ID is required for doctor accounts.")
        return data

class PrettyAuthenticationForm(PrettyMixin, AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=request, *args, **kwargs)
        self._beautify()

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone",
                  "gender", "national_code", "country", "province", "city", "address"]
        widgets = {f: forms.TextInput(attrs={"class": "form-control"}) for f in
                   ["first_name", "last_name", "email", "phone", "national_code"]}
        widgets.update({
            "gender": forms.Select(attrs={"class": "form-select"}),
            "country": forms.Select(attrs={"class": "form-select"}),
            "province": forms.Select(attrs={"class": "form-select"}),
            "city": forms.Select(attrs={"class": "form-select"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        })

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if not phone:
            return phone
        # Normalize to 09xxxxxxxxx (Iran local) to fit max_length=11
        phone = phone.strip()
        if phone.startswith("+98"):
            phone = "0" + phone[3:]
        phone = re.sub(r"\D", "", phone)
        if not re.fullmatch(r"09\d{9}", phone):
            raise forms.ValidationError("Use 09xxxxxxxxx or +98 format.")
        return phone

class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ["university",
                  "medical_id", "specialties"]
        widgets = {
            "university": forms.TextInput(attrs={"class": "form-control"}),
            # "contract_started": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
            # "contract_end": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
            "medical_id": forms.TextInput(attrs={"class": "form-control"}),
            # "rate": forms.NumberInput(attrs={"class": "form-control", "step": "0.1"}),
            "specialties": forms.SelectMultiple(attrs={"class": "form-select", "size": 8}),
        }


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = []
