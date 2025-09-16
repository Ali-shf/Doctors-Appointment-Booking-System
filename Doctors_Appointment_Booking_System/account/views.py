from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db import transaction
from django.contrib.auth import get_user_model
from sqlalchemy.sql.coercions import expect

from .forms import RegisterForm, PrettyAuthenticationForm
from .models import Doctor, Patient

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from kavenegar import KavenegarAPI, APIException, HTTPException
from .otp import gen_otp, save_otp, verify_otp, can_resend

User = get_user_model()

def login_view(request):
    if request.user.is_authenticated:
        pass
        #return redirect("dashboard")
    form = PrettyAuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, f"Welcome back, {user.username}!")
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

    return JsonResponse({"ok": True})

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

    login(request, user)

    return JsonResponse({"ok": True})