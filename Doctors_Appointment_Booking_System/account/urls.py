from django.urls import path
from .views import login_view, logout_view, register_view
from .views import send_code, verify_code, otp_login_page


urlpatterns = [
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("register/", register_view, name="register"),
    path("login/otp/", otp_login_page, name="otp-login-page"),
    path("api/login/otp/send/", send_code, name="otp-send"),
    path("api/login/otp/verify/", verify_code, name="otp-verify"),
]
