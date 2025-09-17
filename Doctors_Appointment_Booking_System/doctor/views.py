from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView, CreateView , UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404
from .models import Comment, Doctor, Patient
from .forms import CommentForm
from doctor.models import Clinic
from doctor.forms import ClinicForm



class ClinicListView(ListView):
    model = Clinic
    paginate_by = 20
    template_name = "clinic/clinic_list.html"
    context_object_name = "clinics"

class ClinicDetailView(DetailView):
    model = Clinic
    template_name = "clinic/clinic_detail.html"
    context_object_name = "clinic"

class ClinicCreateView(LoginRequiredMixin, PermissionRequiredMixin , CreateView):
    permission_required = "app.add_clinic"
    model = Clinic
    form_class = ClinicForm
    template_name = "clinic/clinic_form.html"


class ClinicUpdateView(LoginRequiredMixin, PermissionRequiredMixin ,UpdateView):
    permission_required = "app.change_clinic"
    model = Clinic
    form_class = ClinicForm
    template_name = "clinic/clinic_form.html"

class ClinicDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = "app.delete_clinic"
    model = Clinic
    template_name = "clinic/clinic_confirm_delete.html"
    success_url = reverse_lazy("clinic:list")




class CommentClinicListView(ListView):
    model = Comment
    paginate_by = 20
    template_name = "comment/comment_clinic_list.html"
    context_object_name = "clinic_comments"

    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .select_related("patient_id", "clinic_id")
            .order_by("-created_at")
        )

        patient = self.request.GET.get("patient")
        clinic  = self.request.GET.get("clinic")


        if patient:
            qs = qs.filter(patient_id=patient)    
        if clinic:
            qs = qs.filter(clinic_id=clinic)   

        return qs

class CommentDoctorListView(ListView):
    model = Comment
    paginate_by = 20
    template_name = "comment/comment_doctor_list.html"
    context_object_name = "doctor_comments"

    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .select_related("patient_id", "doctor_id")
            .order_by("-created_at")
        )

        patient = self.request.GET.get("patient")
        doctor  = self.request.GET.get("doctor")


        if patient:
            qs = qs.filter(patient_id=patient)    
        if doctor:
            qs = qs.filter(doctor_id=doctor)   

        return qs

class CommentDetailView(DetailView):
    model = Comment
    template_name = "comment/comment_detail.html"
    context_object_name = "comment"


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = "comment/comment_form.html"

    def get_initial(self):
        initial = super().get_initial()

        doctor_pk  = self.kwargs.get("doctor_pk")
        patient_pk = self.kwargs.get("patient_pk")
        clinic_pk  = self.kwargs.get("clinic_pk")

        doctor_qs  = self.request.GET.get("doctor")
        patient_qs = self.request.GET.get("patient")
        clinic_qs  = self.request.GET.get("clinic")

        if doctor_pk or doctor_qs:
            initial["doctor_id"] = get_object_or_404(Doctor, pk=doctor_pk or doctor_qs)

        initial["patient_id"] = patient_pk or patient_qs

        if clinic_pk or clinic_qs:
            initial["clinic_id"] = get_object_or_404(Patient, pk=clinic_pk or clinic_qs)

        return initial

    def get_success_url(self):
        return self.request.GET.get("next") or reverse("comment:detail", args=[self.object.pk])


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = "comment/comment_form.html"

    def get_success_url(self):
        return self.request.GET.get("next") or reverse("comment:detail", args=[self.object.pk])


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = "comment/comment_confirm_delete.html"
    success_url = reverse_lazy("comment:list")
