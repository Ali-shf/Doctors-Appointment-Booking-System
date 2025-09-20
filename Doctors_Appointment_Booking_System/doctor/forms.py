from django import forms
from doctor.models import Comment,Clinic

class ClinicForm(forms.ModelForm):

    class Meta:
        model = Clinic
        fields = ["name" ,"founded_date", "address" , "working_hours" , "description" ,"country","region","city" ]
        widget = {
            "founded_date" : forms.DateInput(attrs={"type" : "datetime-local"}),
            "description" : forms.Textarea(attrs={"rows": 4})
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["patient", "doctor", "visit", "rate", "comment"]
        widgets = {
            "rate": forms.NumberInput(attrs={"min": 0, "max": 5}),
            "comment": forms.Textarea(attrs={"rows": 3}),
        }