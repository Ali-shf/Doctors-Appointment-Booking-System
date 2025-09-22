from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db import transaction
from .forms import RegisterForm, PrettyAuthenticationForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from .otp import gen_otp, save_otp, verify_otp, can_resend
from django.contrib.auth.decorators import login_required
from django.views.generic import DetailView, UpdateView
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from .models import Doctor, Patient
from .forms import UserProfileForm, DoctorForm, PatientForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from .otp import gen_otp, save_otp, verify_otp, can_resend, send_email_otp




User = get_user_model()

# <--- Login, Logout, Register --->
def login_view(request):
    if request.user.is_authenticated:
        return redirect("doctors_list")
    form = PrettyAuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, f"Welcome back, {user.username}!")
        if user.is_superuser:
            return redirect("admin:index")
        next_url = request.GET.get("next") or reverse("doctors_list")
        return redirect(next_url)
    return render(request, "account/login.html", {"form": form})
def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "You have been logged out.")
    return redirect("login")
@transaction.atomic
def register_view(request):
    if request.user.is_authenticated:
        pass
        #return redirect("dashboard")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Create the user
            user: User = form.save(commit=False)
            user.email = form.cleaned_data["email"]
            user.gender = form.cleaned_data.get("gender")
            user.phone = form.cleaned_data.get("phone")
            user.national_code = form.cleaned_data.get("national_code")
            user.country = form.cleaned_data.get("country")
            user.province = form.cleaned_data.get("province")
            user.city = form.cleaned_data.get("city")
            user.address = form.cleaned_data.get("address")
            user.save()

            role = form.cleaned_data["role"]
            if role == "doctor":
                # create Doctor profile
                doctor = Doctor.objects.create(
                    user=user,
                    medical_id=form.cleaned_data["medical_id"],
                )
                specialties = form.cleaned_data.get("specialties")
                if specialties:
                    doctor.specialties.set(specialties)
            else:
                # create Patient profile
                Patient.objects.create(user=user)

            messages.success(request, "Account created successfully. You can log in now.")
            return redirect("login")
        # invalid => fallthrough
    else:
        form = RegisterForm()
    return render(request, "account/register.html", {"form": form})\

# <--- OTP --->
PURPOSE = "login_email"
def _norm_email(value: str) -> str:
    return (value or "").strip().lower()
def otp_login_page(request):
    return render(request, "account/otp_login.html")
@require_POST
def send_code(request):
    email = _norm_email(request.POST.get("email"))
    if not email:
        return JsonResponse({"ok": False, "error": "email required"}, status=400)

    if not can_resend(email, PURPOSE, settings.OTP_RESEND_COOLDOWN):
        return JsonResponse({"ok": False, "error": "cooldown"}, status=429)

    otp = gen_otp(6)
    save_otp(email, PURPOSE, otp)

    # try:
    #     send_email_otp(email, otp, subject="Verification Code")
    # except Exception as e:
    #     return JsonResponse({"ok": False, "error": "email send failed"}, status=502)

    import logging
    logger = logging.getLogger(__name__)

    try:
        send_email_otp(email, otp, subject="Verification Code")
    except Exception as e:
        logger.exception("Email send failed")  # full traceback in console
        return JsonResponse(
            {"ok": False, "error": f"{e.__class__.__name__}: {e}"},
            status=502
        )

    return JsonResponse({"ok": True, "message": "OTP sent to email"})
@require_POST
def verify_code(request):
    email = (request.POST.get("email") or "").strip().lower()
    code  = (request.POST.get("code") or "").strip()

    if not email or not code:
        return JsonResponse({"ok": False, "error": "email & code required"}, status=400)

    if not verify_otp(email, PURPOSE, code):
        return JsonResponse({"ok": False, "error": "invalid or expired"}, status=400)

    try:
        user = User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        return JsonResponse({"ok": False, "error": "user not found"}, status=404)

    if not user.is_active:
        return JsonResponse({"ok": False, "error": "user not active"}, status=403)

    backend = "django.contrib.auth.backends.ModelBackend"
    login(request, user, backend=backend)

    if user.is_superuser:
        return JsonResponse({"ok": True, "redirect": reverse("admin:index")})
    return JsonResponse({"ok": True, "redirect": reverse("dashboard")})

# <--- Profile Redirect --->
@login_required
def me_redirect(request):
    if hasattr(request.user, "doctor_profile"):
        return redirect("doctor_profile")
    if hasattr(request.user, "patient_profile"):
        return redirect("patient_profile")
    messages.info(request, "You don’t have a role yet.")
    return redirect("/")
# <--- Profile Detail Views --->
class DoctorProfileDetail(LoginRequiredMixin, DetailView):
    template_name = "account/doctor_profile.html"
    model = Doctor
    context_object_name = "doctor"

    def get_object(self, queryset=None):
        return self.request.user.doctor_profile
class PatientProfileDetail(LoginRequiredMixin, DetailView):
    template_name = "account/patient_profile.html"
    model = Patient
    context_object_name = "patient"

    def get_object(self, queryset=None):
        return self.request.user.patient_profile
# <---- Update ---->
class DoctorProfileUpdate(LoginRequiredMixin, UpdateView):
    template_name = "account/doctor_edit.html"
    form_class = DoctorForm
    second_form_class = UserProfileForm
    success_url = reverse_lazy("doctor_profile")

    def get_object(self, queryset=None):
        return self.request.user.doctor_profile

    def get_contextDataForms(self):
        doctor = self.get_object()
        if self.request.method == "POST":
            return (self.second_form_class(self.request.POST, instance=self.request.user),
                    self.form_class(self.request.POST, instance=doctor))
        return (self.second_form_class(instance=self.request.user),
                self.form_class(instance=doctor))

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user_form, doctor_form = self.get_contextDataForms()
        ctx["user_form"] = user_form
        ctx["doctor_form"] = doctor_form
        return ctx

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        user_form, doctor_form = self.get_contextDataForms()
        if user_form.is_valid() and doctor_form.is_valid():
            user_form.save()
            doctor_form.save()
            messages.success(request, "Profile updated.")
            return redirect(self.success_url)
        return self.render_to_response(self.get_context_data())
class PatientProfileUpdate(LoginRequiredMixin, UpdateView):
    template_name = "account/patient_edit.html"
    form_class = PatientForm
    second_form_class = UserProfileForm
    success_url = reverse_lazy("patient_profile")

    def get_object(self, queryset=None):
        return self.request.user.patient_profile

    def get_contextDataForms(self):
        patient = self.get_object()
        if self.request.method == "POST":
            return (self.second_form_class(self.request.POST, instance=self.request.user),
                    self.form_class(self.request.POST, instance=patient))
        return (self.second_form_class(instance=self.request.user),
                self.form_class(instance=patient))

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user_form, patient_form = self.get_contextDataForms()
        ctx["user_form"] = user_form
        ctx["patient_form"] = patient_form
        return ctx

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        user_form, patient_form = self.get_contextDataForms()
        if user_form.is_valid() and patient_form.is_valid():
            user_form.save()
            patient_form.save()
            messages.success(request, "Profile updated.")
            return redirect(self.success_url)
        return self.render_to_response(self.get_context_data())
# <--- Public Profile --->
from django.views.generic import ListView, DetailView
from .models import Doctor, Specialty

class DoctorPublicList(ListView):
    template_name = "account/doctors_list.html"
    model = Doctor
    context_object_name = "doctors"
    paginate_by = 12

    def get_queryset(self):
        qs = (Doctor.objects
              .select_related("user")
              .prefetch_related("specialties")
              .order_by("user__last_name", "user__first_name"))

        q = self.request.GET.get("q", "").strip()
        specs = self.request.GET.getlist("specialty")

        if q:
            qs = qs.filter(
                Q(user__first_name__icontains=q) |
                Q(user__last_name__icontains=q) |
                Q(user__username__icontains=q) |
                Q(university__icontains=q) |
                Q(medical_id__icontains=q)
            )
        if specs:
            qs = qs.filter(specialties__code__in=specs)

        return qs.distinct()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        q = self.request.GET.get("q", "")
        selected_specs = self.request.GET.getlist("specialty")

        # build querystring for pagination without the page param
        querydict = self.request.GET.copy()
        querydict.pop("page", None)
        ctx["query_string"] = querydict.urlencode()
        ctx["q"] = q
        ctx["specialties_selected"] = set(selected_specs)
        ctx["specialties"] = Specialty.objects.all().order_by("code")
        ctx["num_match"] = self.object_list.count()
        return ctx

class DoctorPublicDetail(DetailView):
    template_name = "account/doctor_public_detail.html"
    model = Doctor
    context_object_name = "doctor"

    def get_queryset(self):
        return (Doctor.objects
                .select_related("user")
                .prefetch_related("specialties"))

