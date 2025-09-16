from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.validators import RegexValidator
from .models import Country, Region, City, Doctor, Patient, Specialty
from django.contrib.auth import get_user_model

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
        help_text="مثال: 09123456789 یا +989123456789"
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
