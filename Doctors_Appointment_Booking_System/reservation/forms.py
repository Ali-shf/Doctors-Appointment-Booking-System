from django import forms
from .models import TimeSheet, Visit, EmailMessage

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

class VisitForm(forms.ModelForm):
    class Meta:
        model = Visit
        fields = ["doctor", "patient", "clinic", "date", "start_meet", "end_meet", "price"]
        widgets = {
            "doctor": forms.Select(attrs={"class": "form-select"}),
            "patient": forms.Select(attrs={"class": "form-select"}),
            "clinic": forms.Select(attrs={"class": "form-select"}),
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "start_meet": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
            "end_meet": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
            "price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
        }

class EmailMessageForm(forms.ModelForm):
    class Meta:
        model = EmailMessage
        fields = ["visit", "description"]
        widgets = {
            "visit": forms.Select(attrs={"class": "form-select"}),
            "description": forms.Textarea(attrs={"rows": 4, "class": "form-control", "placeholder": "Enter your message here..."}),
        }