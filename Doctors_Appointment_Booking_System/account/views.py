from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db import transaction
from .forms import RegisterForm, PrettyAuthenticationForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from kavenegar import KavenegarAPI, APIException, HTTPException
from .otp import gen_otp, save_otp, verify_otp, can_resend
from django.contrib.auth.decorators import login_required
from django.views.generic import DetailView, UpdateView
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from .models import Doctor, Patient
from .forms import UserProfileForm, DoctorForm, PatientForm
from django.contrib.auth.mixins import LoginRequiredMixin



User = get_user_model()

# <--- Login, Logout, Register --->
def login_view(request):
    if request.user.is_authenticated:
        pass
        #return redirect("dashboard")
    form = PrettyAuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, f"Welcome back, {user.username}!")
        if user.is_superuser:
            return redirect("admin:index")
        next_url = request.GET.get("next") or reverse("dashboard")
        return redirect(next_url)
    return render(request, "login.html", {"form": form})
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
    return render(request, "register.html", {"form": form})\

# <--- OTP --->
API = KavenegarAPI('6A6E2B65653743652F36637775654B5948685A6156524C466F32734D7A78494A4E316A64337275725849513D')
PURPOSE = "login"
def otp_login_page(request):
    return render(request, "otp_login.html")
@require_POST
def send_code(request):
    phone = request.POST.get("phone")
    if not phone:
        return JsonResponse({"ok": False, "error": "phone required"}, status=400)

    if not can_resend(phone, PURPOSE, settings.OTP_RESEND_COOLDOWN):
        return JsonResponse({"ok": False, "error": "cooldown"}, status=429)

    otp = gen_otp(6)
    save_otp(phone, PURPOSE, otp)

    try:
        params = { "sender" : "2000660110", "receptor": phone, "message": f"Verification Code : {otp}"}
        API.sms_send(params)
    except (APIException, HTTPException) as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=502)

    return JsonResponse({"ok": True, "message" : "OTP sent successfully"})
@require_POST
def verify_code(request):
    phone = request.POST.get("phone")
    code  = request.POST.get("code")
    if not phone or not code:
        return JsonResponse({"ok": False, "error": "phone & code required"}, status=400)

    if not verify_otp(phone, PURPOSE, code):
        return JsonResponse({"ok": False, "error": "invalid or expired"}, status=400)

    try:
        user = User.objects.get(phone=phone)
    except User.DoesNotExist:
        return JsonResponse({"ok": False, "error": "user not found"}, status=404)

    if not user.is_active:
        return JsonResponse({"ok": False, "error": "user not active"}, status=404)

    if user.is_superuser:
        return redirect("admin:index")

    return redirect(reverse("dashboard"))

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
    template_name = "doctor_profile.html"
    model = Doctor
    context_object_name = "doctor"

    def get_object(self, queryset=None):
        return self.request.user.doctor_profile

class PatientProfileDetail(LoginRequiredMixin, DetailView):
    template_name = "patient_profile.html"
    model = Patient
    context_object_name = "patient"

    def get_object(self, queryset=None):
        return self.request.user.patient_profile


# <---- Update ---->
class DoctorProfileUpdate(LoginRequiredMixin, UpdateView):
    template_name = "doctor_edit.html"
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
    template_name = "patient_edit.html"
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
