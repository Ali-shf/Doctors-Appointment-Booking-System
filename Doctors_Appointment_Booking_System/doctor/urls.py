from django.urls import path
from . import views

app_name = "doctor"

urlpatterns = [
    path("comment/", views.CommentClinicListView.as_view(), name="list"),#?
    path("comment/<int:pk>/", views.detail_comment_view.as_view(), name="detail"),
    path("comment/new/", views.add_comment_view.as_view(), name="comment_create"),
    path("comment/<int:pk>/edit/", views.edit_comment_view.as_view(), name="comment_update"),
    path("comment/<int:pk>/delete/", views.delete_comment_view.as_view(), name="delete"),

    path("clinics/", views.ClinicListView.as_view(), name="clinics_list"),#OK
    path("clinics/<int:pk>/", views.ClinicDetailView.as_view(), name="clinic_detail"),
    path("clinics/new/", views.ClinicCreateView.as_view(), name="clinic_create"),
    path("clinics/<int:pk>/edit/", views.ClinicUpdateView.as_view(), name="clinic_update"),
]
