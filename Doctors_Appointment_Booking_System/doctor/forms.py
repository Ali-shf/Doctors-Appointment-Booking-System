from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet

from doctor.models import Comment,Clinic , ClinicOpeningHour
from cities_light.models import Country,Region,City






class ClinicForm(forms.ModelForm):
    country = forms.ModelChoiceField(queryset=Country.objects.all(), widget=forms.Select(attrs={'class':'form-select'}))
    region  = forms.ModelChoiceField(queryset=Region.objects.all(), widget=forms.Select(attrs={'class':'form-select'}))
    city    = forms.ModelChoiceField(queryset=City.objects.all(),   widget=forms.Select(attrs={'class':'form-select'}))


    class Meta:
        model = Clinic
        fields = ["name", "founded_date", "address", "description"]# "country", "region", "city"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "founded_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "address": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
            "country": forms.Select(attrs={"class": "form-select"}),
            "region": forms.Select(attrs={"class": "form-select"}),
            "city": forms.Select(attrs={"class": "form-select"}),
        }

class OpeningHourForm(forms.ModelForm):
    class Meta:
        model = ClinicOpeningHour
        fields = ["weekday", "start", "end"]
        widgets = {
            "weekday": forms.Select(attrs={"class": "form-select"}),
            "start": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "end": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
        }

class BaseOpeningHourFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        slots = {choice[0]: [] for choice in ClinicOpeningHour.Weekday.choices}
        for form in self.forms:
            if getattr(form, "cleaned_data", None) is None:
                continue
            if form.cleaned_data.get("DELETE"):
                continue

            wd = form.cleaned_data.get("weekday")
            start = form.cleaned_data.get("start")
            end = form.cleaned_data.get("end")

            if not wd or not start or not end:
                # اجازهٔ سطر ناقص نمی‌دهیم؛ اگر می‌خواهی بدهی، این بخش را نرم‌تر کن
                form.add_error(None, "Weekday, start and end are required.")
                continue

            if end <= start:
                form.add_error("end", "End time must be after start time.")
                continue

            # overlap check
            for s, e in slots.get(wd, []):
                # اگر نه (end <= s یا start >= e) => همپوشانی دارد
                if not (end <= s or start >= e):
                    form.add_error(None, "Time range overlaps another range for this weekday.")
                    break
            else:
                slots.setdefault(wd, []).append((start, end))

OpeningHourFormSet = inlineformset_factory(
    Clinic,
    ClinicOpeningHour,
    form=OpeningHourForm,
    formset=BaseOpeningHourFormSet,
    fields=["weekday", "start", "end"],
    extra=1,            # می‌تونی 7 بذاری تا برای هر روز یک ردیف خالی نشان دهد
    can_delete=True,
)

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["doctor_id", "clinic_id", "rate", "comment"]  # patient_id عمداً نیست
        widgets = {
            "doctor_id": forms.Select(attrs={"class": "form-select"}),
            "clinic_id": forms.Select(attrs={"class": "form-select"}),
            "rate": forms.NumberInput(attrs={"min": 0, "max": 5, "class": "form-control"}),
            "comment": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        }
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        if self.initial.get("clinic_id"):
            self.fields["clinic_id"].widget = forms.HiddenInput()
        if self.initial.get("doctor_id"):
            self.fields["doctor_id"].widget = forms.HiddenInput()
