from django import forms
from .models import TimeSheet, Visit, VisitLog

class TimesheetForm(forms.ModelForm):
    class Meta:
        model = TimeSheet
        fields = ["doctor", "clinic", "end", "visit_time"]
        widgets = {
            "doctor": forms.Select(attrs={"class": "form-select"}),
            "clinic": forms.Select(attrs={"class": "form-select"}),
            "end": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
            "visit_time": forms.TextInput(attrs={"class": "form-control", "placeholder": '["09:00", "10:00", "11:00"]'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        doctor = None
        if self.instance and getattr(self.instance, "doctor_id", None):
            doctor = self.instance.doctor
        else:
            doctor = self.initial.get("doctor") or self.data.get("doctor")
            try:
                from account.models import Doctor as AccountDoctor
                if doctor and not isinstance(doctor, AccountDoctor):
                    doctor = AccountDoctor.objects.filter(pk=doctor).first()
            except Exception:
                doctor = None
        if doctor is not None:
            try:
                self.fields["clinic"].queryset = doctor.clinics.all()
            except Exception:
                pass


class VisitForm(forms.ModelForm):
    class Meta:
        model = Visit
        fields = ["doctor", "patient", "clinic", "date", "start_meet", "end_meet", "price", "status"]
        widgets = {
            "doctor": forms.Select(attrs={"class": "form-select"}),
            "patient": forms.Select(attrs={"class": "form-select"}),
            "clinic": forms.Select(attrs={"class": "form-select"}),
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "start_meet": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
            "end_meet": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
            "price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }

class VisitLogForm(forms.ModelForm):
    class Meta:
        model = VisitLog
        fields = ["visit", "description", "support_code"]
        widgets = {
            "visit": forms.Select(attrs={"class": "form-select"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "support_code": forms.TextInput(attrs={"class": "form-control", "placeholder": "کد پیگیری اتوماتیک"}),
        }
        readonly_fields = ("support_code", "description")
