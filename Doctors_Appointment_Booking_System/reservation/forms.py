from django import forms
from .models import TimeSheet, Visit, EmailMessage

class TimesheetForm(forms.ModelForm):
    class Meta:
        model = TimeSheet
        fields = ["doctor", "clinic", "end", "visit_time"]
        widgets = {
            "end": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

class VisitForm(forms.ModelForm):
    class Meta:
        model = Visit
        fields = ["doctor", "patient", "clinic", "date", "start_meet", "end_meet", "price"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "start_meet": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end_meet": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

class EmailMessageForm(forms.ModelForm):
    class Meta:
        model = EmailMessage
        fields = ["visit", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }
