from django.urls import path
from .views import login_view, logout_view, register_view
from .views import send_code, verify_code, otp_login_page
from . import views
from django.contrib.auth import views as auth_views




urlpatterns = [
#   <--- Login, Logout, Register --->
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("register/", register_view, name="register"),
    path("login/otp/", otp_login_page, name="otp-login-page"),
    path("api/login/otp/send/", send_code, name="otp-send"),
    path("api/login/otp/verify/", verify_code, name="otp-verify"),

#   <--- Profile --->
    path("me/", views.me_redirect, name="me"),
    path("me/patient/", views.PatientProfileDetail.as_view(), name="patient_profile"),
    path("me/doctor/", views.DoctorProfileDetail.as_view(), name="doctor_profile"),

    path("me/patient/edit/", views.PatientProfileUpdate.as_view(), name="patient_edit"),
    path("me/doctor/edit/", views.DoctorProfileUpdate.as_view(), name="doctor_edit"),
    path("password/change/", auth_views.PasswordChangeView.as_view(
            template_name="password_change.html",
            success_url="/account/password/change/done/",
        ),
        name="password_change"
    ),
    path("password/change/done/", auth_views.PasswordChangeDoneView.as_view(
             template_name="password_change_done.html"
         ),
         name="password_change_done"
    ),
]
