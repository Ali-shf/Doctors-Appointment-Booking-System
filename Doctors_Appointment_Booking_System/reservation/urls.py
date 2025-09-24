from django.urls import path
from .views import (
    TimeSheetListView, TimeSheetCreateView, TimeSheetUpdateView, TimeSheetDeleteView,
    VisitListView, DoctorListForReservationView,
    ClinicListForReservationView, DoctorListByClinicView,
    DoctorReservationView, PaymentSuccessView, PaymentStartView,
    VisitLogListView, VisitLogCreateView, VisitLogUpdateView, VisitLogDeleteView,
)

app_name = "reservation"

urlpatterns = [
    # لیست کلینیک‌ها و سپس دکترهای هر کلینیک
    path("clinics/", ClinicListForReservationView.as_view(), name="clinic-list"),
    path("clinics/<int:clinic_id>/doctors/", DoctorListByClinicView.as_view(), name="clinic-doctor-list"),
    # لیست همه دکترها (اختیاری)
    path("doctors/", DoctorListForReservationView.as_view(), name="doctor-list"),

    # مدیریت تایم‌شیت‌ها (برای دکترها/ادمین)
    path("timesheets/", TimeSheetListView.as_view(), name="timesheet-list"),
    path("timesheets/add/", TimeSheetCreateView.as_view(), name="timesheet-add"),
    path("timesheets/<int:pk>/edit/", TimeSheetUpdateView.as_view(), name="timesheet-edit"),
    path("timesheets/<int:pk>/delete/", TimeSheetDeleteView.as_view(), name="timesheet-delete"),

    # لیست ویزیت‌ها (برای کاربر/دکتر)
    path("visits/", VisitListView.as_view(), name="visit-list"),

    # صفحه رزرو دکتر در کلینیک مشخص
    path("reserve/clinic/<int:clinic_id>/doctor/<int:doctor_id>/", DoctorReservationView.as_view(), name="doctor-reserve"),

    # پرداخت موفق (نمایش کد پیگیری)
    path("reserve/payment/success/", PaymentSuccessView.as_view(), name="payment-success"),
    # شروع پرداخت (شبیه‌ساز درگاه)
    path("reserve/payment/start/<int:visit_id>/", PaymentStartView.as_view(), name="payment-start"),

]
