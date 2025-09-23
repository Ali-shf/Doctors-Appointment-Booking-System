from django.urls import path
from .views import (
    TimeSheetListView, TimeSheetCreateView, TimeSheetUpdateView, TimeSheetDeleteView,
    VisitListView, VisitCreateView, VisitUpdateView, VisitDeleteView,
    EmailMessageListView, EmailMessageCreateView, EmailMessageUpdateView, EmailMessageDeleteView
)

app_name = "reservation"

urlpatterns = [
    # TimeSheet
    path("timesheets/", TimeSheetListView.as_view(), name="timesheet-list"),
    path("timesheets/add/", TimeSheetCreateView.as_view(), name="timesheet-add"),
    path("timesheets/<int:pk>/edit/", TimeSheetUpdateView.as_view(), name="timesheet-edit"),
    path("timesheets/<int:pk>/delete/", TimeSheetDeleteView.as_view(), name="timesheet-delete"),

    # Visit
    path("visits/", VisitListView.as_view(), name="visit-list"),
    path("visits/add/", VisitCreateView.as_view(), name="visit-add"),
    path("visits/<int:pk>/edit/", VisitUpdateView.as_view(), name="visit-edit"),
    path("visits/<int:pk>/delete/", VisitDeleteView.as_view(), name="visit-delete"),

    # EmailMessage
    path("emails/", EmailMessageListView.as_view(), name="emailmessage-list"),
    path("emails/add/", EmailMessageCreateView.as_view(), name="emailmessage-add"),
    path("emails/<int:pk>/edit/", EmailMessageUpdateView.as_view(), name="emailmessage-edit"),
    path("emails/<int:pk>/delete/", EmailMessageDeleteView.as_view(), name="emailmessage-delete"),
]
