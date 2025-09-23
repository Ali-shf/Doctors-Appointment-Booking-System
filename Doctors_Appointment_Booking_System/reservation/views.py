from django.shortcuts import render


from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView
)
from django.urls import reverse_lazy
from .models import TimeSheet, Visit, EmailMessage
from .forms import TimesheetForm, VisitForm, EmailMessageForm



class TimeSheetListView(LoginRequiredMixin, ListView):
    model = TimeSheet
    template_name = "reservation/timesheet_list.html"
    context_object_name = "timesheets"

    def get_queryset(self):
        qs = super().get_queryset().select_related("doctor__user", "clinic")
     
        if hasattr(self.request.user, "doctor"):
            qs = qs.filter(doctor=self.request.user.doctor)
        return qs


class TimeSheetCreateView(LoginRequiredMixin, CreateView):
    model = TimeSheet
    form_class = TimesheetForm
    template_name = "reservation/timesheet_form.html"
    success_url = reverse_lazy("reservation:timesheet-list")


class TimeSheetUpdateView(LoginRequiredMixin, UpdateView):
    model = TimeSheet
    form_class = TimesheetForm
    template_name = "reservation/timesheet_form.html"
    success_url = reverse_lazy("reservation:timesheet-list")


class TimeSheetDeleteView(LoginRequiredMixin, DeleteView):
    model = TimeSheet
    template_name = "reservation/timesheet_confirm_delete.html"
    success_url = reverse_lazy("reservation:timesheet-list")



class VisitListView(LoginRequiredMixin, ListView):
    
    model = Visit
    template_name = "reservation/visit_list.html"
    context_object_name = "visits"

    def get_queryset(self):
        qs = super().get_queryset().select_related(
            "doctor__user", "patient", "clinic"
        )
        u = self.request.user
        if hasattr(u, "doctor"):
            qs = qs.filter(doctor=u.doctor)
        else:
            qs = qs.filter(patient=u)
        return qs


class VisitCreateView(LoginRequiredMixin, CreateView):
    model = Visit
    form_class = VisitForm
    template_name = "reservation/visit_form.html"
    success_url = reverse_lazy("reservation:visit-list")


class VisitUpdateView(LoginRequiredMixin, UpdateView):
    model = Visit
    form_class = VisitForm
    template_name = "reservation/visit_form.html"
    success_url = reverse_lazy("reservation:visit-list")


class VisitDeleteView(LoginRequiredMixin, DeleteView):
    model = Visit
    template_name = "reservation/visit_confirm_delete.html"
    success_url = reverse_lazy("reservation:visit-list")



class EmailMessageListView(LoginRequiredMixin, ListView):
    model = EmailMessage
    template_name = "reservation/emailmessage_list.html"
    context_object_name = "emails"

    def get_queryset(self):
        return super().get_queryset().select_related(
            "visit__doctor__user", "visit__patient"
        )


class EmailMessageCreateView(LoginRequiredMixin, CreateView):
    model = EmailMessage
    form_class = EmailMessageForm
    template_name = "reservation/emailmessage_form.html"
    success_url = reverse_lazy("reservation:emailmessage-list")


class EmailMessageUpdateView(LoginRequiredMixin, UpdateView):
    model = EmailMessage
    form_class = EmailMessageForm
    template_name = "reservation/emailmessage_form.html"
    success_url = reverse_lazy("reservation:emailmessage-list")


class EmailMessageDeleteView(LoginRequiredMixin, DeleteView):
    model = EmailMessage
    template_name = "reservation/emailmessage_confirm_delete.html"
    success_url = reverse_lazy("reservation:emailmessage-list")