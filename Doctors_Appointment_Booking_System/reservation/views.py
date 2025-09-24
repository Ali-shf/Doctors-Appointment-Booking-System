from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.views import View
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from decimal import Decimal
from datetime import datetime, timedelta, time as dtime
import re
import uuid
import random

from .models import TimeSheet, Visit, VisitLog
from .forms import TimesheetForm, VisitForm, VisitLogForm
from account.models import Doctor as AccountDoctor
from doctor.models import Clinic
from wallet.models import Cart


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
        qs = super().get_queryset().select_related("doctor__user", "patient", "clinic")
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



class VisitLogListView(LoginRequiredMixin, ListView):
    model = VisitLog
    template_name = "reservation/emailmessage_list.html"
    context_object_name = "logs"

    def get_queryset(self):
        qs = super().get_queryset().select_related("visit__doctor__user", "visit__patient")
        u = self.request.user
        if hasattr(u, "doctor"):
            qs = qs.filter(visit__doctor=u.doctor)
        else:
            qs = qs.filter(visit__patient=u)
        return qs



class VisitLogCreateView(LoginRequiredMixin, CreateView):
    model = VisitLog
    form_class = VisitLogForm
    template_name = "reservation/emailmessage_form.html"
    success_url = reverse_lazy("reservation:emailmessage-list")


class VisitLogUpdateView(LoginRequiredMixin, UpdateView):
    model = VisitLog
    form_class = VisitLogForm
    template_name = "reservation/emailmessage_form.html"
    success_url = reverse_lazy("reservation:emailmessage-list")


class VisitLogDeleteView(LoginRequiredMixin, DeleteView):
    model = VisitLog
    template_name = "reservation/visitlog_confirm_delete.html"
    success_url = reverse_lazy("reservation:emailmessage-list")


class DoctorListForReservationView(ListView):
    model = AccountDoctor
    template_name = "reservation/doctor_list.html"
    context_object_name = "doctors"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("user")
            .order_by("user__first_name", "user__last_name", "user__username")
        )


class DoctorReservationView(View):
    template_name = "reservation/doctor_reserve.html"

    def get(self, request, clinic_id, doctor_id):
        doctor = get_object_or_404(AccountDoctor, pk=doctor_id)
        clinic = get_object_or_404(Clinic, pk=clinic_id)
        timesheets = (
            TimeSheet.objects
            .filter(doctor=doctor, clinic=clinic)
            .select_related("doctor__user", "clinic")
            .order_by("end")
        )
        context = {"doctor": doctor, "clinic": clinic, "timesheets": timesheets}
        return render(request, self.template_name, context)

    def post(self, request, clinic_id, doctor_id):
        if not request.user.is_authenticated:
            return redirect(f"/accounts/login/?next={request.path}")

        doctor = get_object_or_404(AccountDoctor, pk=doctor_id)
        clinic = get_object_or_404(Clinic, pk=clinic_id)
        timesheet_id = request.POST.get("timesheet_id")
        slot_time_str = request.POST.get("slot")
        if not timesheet_id or not slot_time_str:
            messages.error(request, "لطفاً یک بازه زمانی را انتخاب کنید.")
            return redirect(request.path)

        timesheet = get_object_or_404(TimeSheet, pk=timesheet_id, doctor=doctor, clinic=clinic)

        # Parse slot time
        def parse_slot_time(raw: str) -> dtime:
            text = (raw or "").strip()
            digit_map = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
            text = text.translate(digit_map)
            m_any = re.search(r"(\d{1,2}:\d{2}(?::\d{2})?)\s*(AM|PM|am|pm)?", text)
            if m_any:
                time_part = m_any.group(1)
                ampm_part = m_any.group(2) or ""
                text = (time_part + (" " + ampm_part if ampm_part else "")).strip()
            match = re.match(r"^(\d{1,2}):(\d{2})(?::(\d{2}))?\s*(AM|PM|am|pm)?$", text)
            if not match:
                raise ValueError("invalid time format")
            hour = int(match.group(1))
            minute = int(match.group(2))
            second = int(match.group(3) or 0)
            ampm = match.group(4)
            if ampm:
                ampm = ampm.lower()
                if hour == 12: hour = 0
                if ampm == "pm": hour += 12
            return dtime(hour, minute, second)

        try:
            slot_time = parse_slot_time(slot_time_str)
        except ValueError:
            slot_time = dtime(9, 0, 0)

        visit_date = timesheet.end.date()
        start_meet = datetime.combine(visit_date, slot_time)
        end_meet = start_meet + timedelta(minutes=30)
        price = Decimal("200000.00")

        cart = Cart.objects.create(pay_price=price)

        # در این مرحله رزرو را ایجاد می‌کنیم؛ جلوگیری از تداخل به مرحله پرداخت موفق موکول می‌شود

        visit = Visit.objects.create(
            doctor=doctor,
            patient=request.user,
            clinic=timesheet.clinic,
            date=visit_date,
            start_meet=start_meet,
            end_meet=end_meet,
            price=price,
            cart=cart,
        )

        return redirect(reverse("reservation:payment-start", kwargs={"visit_id": visit.id}))


class ClinicListForReservationView(ListView):
    model = Clinic
    template_name = "reservation/clinic_list.html"
    context_object_name = "clinics"


class DoctorListByClinicView(ListView):
    model = AccountDoctor
    template_name = "reservation/doctor_list_by_clinic.html"
    context_object_name = "doctors"

    def get_queryset(self):
        clinic_id = self.kwargs.get("clinic_id")
        clinic = get_object_or_404(Clinic, pk=clinic_id)
        # Doctors that have at least one timesheet in this clinic
        return (
            AccountDoctor.objects
            .filter(time_sheets__clinic=clinic)
            .select_related("user")
            .distinct()
            .order_by("user__first_name", "user__last_name", "user__username")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["clinic"] = get_object_or_404(Clinic, pk=self.kwargs.get("clinic_id"))
        return ctx



class PaymentStartView(LoginRequiredMixin, View):
    template_name = "reservation/payment_start.html"

    def get(self, request, visit_id):
        visit = get_object_or_404(Visit.objects.select_related("doctor__user", "patient", "clinic", "cart"), pk=visit_id, patient=request.user)
        return render(request, self.template_name, {"visit": visit})

    def post(self, request, visit_id):
        visit = get_object_or_404(Visit.objects.select_related("cart"), pk=visit_id, patient=request.user)
        cart = visit.cart
        if not cart:
            messages.error(request, "سبد پرداخت یافت نشد.")
            return redirect("reservation:doctor-list")
        cart.payment_status = "PAID"
        # Generate 8-digit numeric tracking code
        cart.support_code = "".join(str(random.randint(0,9)) for _ in range(8))
        cart.save(update_fields=["payment_status", "support_code", "updated_at"])
        # بعد از پرداخت، ویزیت را completed می‌کنیم تا سیگنال VisitLog فعال شود
        # اگر به هر دلیل دیگری کسی همزمان رزرو کرده بود، اینجا خطا را مدیریت کنیم
        if Visit.objects.filter(
            doctor=visit.doctor,
            clinic=visit.clinic,
            date=visit.date,
            start_meet=visit.start_meet,
            status="completed",
        ).exclude(pk=visit.pk).exists():
            messages.error(request, "این بازه زمانی به‌تازگی رزرو شده است. مبلغ شما ثبت شد ولی ویزیت جایگزین نیاز است.")
            return redirect("reservation:doctor-list")
        visit.status = "completed"
        visit.save(update_fields=["status"])
        # حذف بازه زمانی از تایم‌شیت مرتبط تا دوباره قابل رزرو نباشد
        try:
            slot_variants = {
                visit.start_meet.strftime("%H:%M"),
                visit.start_meet.strftime("%H:%M:%S"),
            }
            related_timesheets = (
                TimeSheet.objects
                .filter(doctor=visit.doctor, clinic=visit.clinic, end__date=visit.date)
                .order_by("end")
            )
            for ts in related_timesheets:
                if isinstance(ts.visit_time, list) and ts.visit_time:
                    original = list(ts.visit_time)
                    updated = [t for t in original if str(t) not in slot_variants]
                    if updated != original:
                        ts.visit_time = updated
                        ts.save(update_fields=["visit_time", "updated_at"])
                        break
        except Exception:
            pass
        return redirect(reverse("reservation:payment-success") + f"?support_code={cart.support_code}&visit_id={visit.id}")


class PaymentSuccessView(LoginRequiredMixin, View):
    template_name = "reservation/payment_success.html"

    def get(self, request):
        support_code = request.GET.get("support_code")
        visit_id = request.GET.get("visit_id")
        visit = None
        if visit_id:
            visit = get_object_or_404(Visit.objects.select_related("doctor__user", "patient", "clinic"), pk=visit_id)
        context = {"support_code": support_code, "visit": visit}
        return render(request, self.template_name, context)
