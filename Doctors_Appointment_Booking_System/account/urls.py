from django.urls import path
from .views import login_view

urlpatterns = [
    path("login/", login_view, name="login"),
    # path("register/", register_view, name="register"),
    # path("logout/", auth_views.LogoutView.as_view(template_name="logout.html"), name="logout", )
]