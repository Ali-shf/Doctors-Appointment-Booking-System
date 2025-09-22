from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet

from doctor.models import Comment,Clinic 
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
