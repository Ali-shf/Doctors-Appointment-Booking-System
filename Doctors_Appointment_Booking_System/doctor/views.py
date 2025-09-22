from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView, CreateView , UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404 , redirect
from .models import Comment, Doctor, Patient , Clinic
from .forms import CommentForm
from doctor.models import Clinic
from django.db.models import Avg
from doctor.forms import ClinicForm




# views.py
from django.db.models import Avg, Count, F, FloatField, ExpressionWrapper
from django.views.generic import ListView
from .models import Clinic

class ClinicListView(ListView):
    model = Clinic
    paginate_by = 20
    template_name = "clinic/clinic_list.html"
    context_object_name = "clinics"

    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .select_related("city", "city__region")  # جلوگیری از N+1
            .annotate(
                avg_rate=Avg("comments_received__rate"),
                ratings_count=Count("comments_received__rate"),
            )
            .annotate( 
                rating_pct=ExpressionWrapper(
                    100.0 * F("avg_rate") / 5.0, output_field=FloatField()
                )
            )
            .order_by("name")
        )
        return qs


# views.py
from django.db.models import Avg, Count
from django.views.generic import DetailView

class ClinicDetailView(DetailView):
    model = Clinic
    template_name = "doctor/clinic_detail.html"
    context_object_name = "clinic"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(
                avg_rate=Avg("comments_received__rate"),
                rate_count=Count("comments_received"),
            )
            .order_by("name")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["comments"] = (
            self.object.comments_received
                .select_related("patient_id__user", "doctor_id", "clinic_id")
                .order_by("-created_at")
        )
        return ctx


class ClinicCreateView(LoginRequiredMixin, PermissionRequiredMixin , CreateView):
    permission_required = "app.add_clinic"
    model = Clinic
    form_class = ClinicForm
    template_name = "doctor/clinic_form.html"


class ClinicUpdateView(LoginRequiredMixin, PermissionRequiredMixin ,UpdateView):
    permission_required = "app.change_clinic"
    model = Clinic
    form_class = ClinicForm
    template_name = "doctor/clinic_form.html"

class ClinicDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = "app.delete_clinic"
    model = Clinic
    template_name = "doctor/clinic_confirm_delete.html"
    success_url = reverse_lazy("clinic:list")




class CommentClinicListView(ListView):
    model = Comment
    paginate_by = 20
    template_name = "doctor/comment_clinic_list.html"
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
    template_name = "doctor/comment_doctor_list.html"
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





from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from .models import Comment, Clinic, Doctor, Patient   # طبق پروژه‌ات
from .forms import CommentForm




class add_comment_view(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = "doctor/comment_form.html"

    def dispatch(self, request, *args, **kwargs):
        # کلینیک/دکترِ دریافتی از URL را برای initial نگه می‌داریم
        self._clinic = None
        self._doctor = None
        clinic_pk = request.GET.get("clinic") or kwargs.get("clinic_pk")
        doctor_pk = request.GET.get("doctor") or kwargs.get("doctor_pk")
        if clinic_pk:
            self._clinic = get_object_or_404(Clinic, pk=clinic_pk)
        if doctor_pk:
            self._doctor = get_object_or_404(Doctor, pk=doctor_pk)
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        if self._clinic:
            initial["clinic_id"] = self._clinic
        if self._doctor:
            initial["doctor_id"] = self._doctor
        return initial

    def form_valid(self, form):
        try:
            patient = Patient.objects.get(user=self.request.user)
        except Patient.DoesNotExist:
            form.add_error(None, "هیچ پروفایل بیماری برای حساب شما ثبت نشده است.")
            return self.form_invalid(form)
        form.instance.patient_id = patient

        # 2) اگر کاربر فیلدهای کلینیک/دکتر را در فرم نداشت، از URL ست کن
        if self._clinic and not form.instance.clinic_id:
            form.instance.clinic_id = self._clinic
        if self._doctor and not form.instance.doctor_id:
            form.instance.doctor_id = self._doctor

        self.object = form.save()

        # 3) برگشت
        next_url = self.request.GET.get("next")
        if next_url:
            return redirect(next_url)
        if self.object.clinic_id_id:
            return redirect("doctor:clinic_detail", self.object.clinic_id_id)
        if self.object.doctor_id_id:
            return redirect("doctor:doctor_public_detail", self.object.doctor_id_id)
        return redirect("doctor:doctors_list")


class detail_comment_view(DetailView):
    model = Comment
    template_name = "doctor/comment_detail.html"
    context_object_name = "comment"
    def get_queryset(self):
        return (
            Comment.objects.all())
    




class edit_comment_view(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = "doctor/comment_form.html"

    def get_success_url(self):
        next_url = self.request.GET.get("next")
        if next_url:
            return next_url
        return reverse("doctor:detail", args=[self.object.pk])



class delete_comment_view(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = "doctor/comment_confirm_delete.html"
    success_url = reverse_lazy("comment:list")


class clinic_rating_summary_view():
    model = Clinic
    template_name = 'clinic/clinic_rates_summeru.html'
    context_object_name = 'clinics'

    def get_queryset(self):
        return (
            Clinic.objects.annotate(avg_rate=Avg('comments_recieved__rate'))
        )
    