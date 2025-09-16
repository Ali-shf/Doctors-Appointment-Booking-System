from django.contrib import admin
from .models import User, Doctor, Specialty, Patient
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin


@admin.register(User)
class UserAdmin(DjangoUserAdmin):

    list_select_related = ("doctor_profile",)

    @admin.display(boolean=True, description="Doctor")
    def is_doctor_flag(self, obj):
        return obj.is_doctor()

    @admin.display(boolean=True, description="Patient")
    def is_patient_flag(self, obj):
        return obj.is_patient()

    list_display = (
        "username", "id","first_name", "last_name", "phone",
        "gender", "national_code",
        "country", "province", "city",
        "is_doctor_flag", "is_patient_flag","is_staff", "is_active",
    )

    list_filter = (
        "is_staff", "is_superuser", "is_active",
        "gender",
    )

    search_fields = ("username", "first_name", "last_name", "phone","email", "national_code")
    ordering = ("username",)

    autocomplete_fields = ("country", "province", "city")

    fieldsets = DjangoUserAdmin.fieldsets + (
        (("Profile"), {
            "fields": (
                "gender", "phone", "national_code",
                "country", "province", "city",
                "address",
            )
        }),
    )

    # fields shown when you click “Add user”
    add_fieldsets = DjangoUserAdmin.add_fieldsets

@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ("code", "__str__")
    search_fields = ("code",)


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    @admin.display(ordering="user__username", description="User")
    def user_display(self, obj):
        return obj.user.get_full_name() or obj.user.username

    @admin.display(description="City")
    def city(self, obj):
        return getattr(obj.user.city, "name", "")

    @admin.display(description="Mobile")
    def mobile(self, obj):
        return getattr(obj.user, "phone", "")

    @admin.display(description="Specialties")
    def specialties_list(self, obj):
        return ", ".join(str(s) for s in obj.specialties.all())

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("user", "user__city").prefetch_related("specialties")

    list_display = ("user_display", "id","mobile","medical_id", "specialties_list","city")
    search_fields = (
        "medical_id", "specialties__code","user__phone",
        "user__username", "user__first_name", "user__last_name", "user__email",
    )
    filter_horizontal = ("specialties",)
    list_filter = ("specialties",)

    autocomplete_fields = ("user",)


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    @admin.display(ordering="user__username", description="User")
    def user_display(self, obj):
        return obj.user.get_full_name() or obj.user.username

    @admin.display(description="City")
    def city(self, obj):
        return getattr(obj.user.city, "name", "")

    @admin.display(description="Mobile")
    def mobile(self, obj):
        return getattr(obj.user.phone)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related("user", "user__city")

    list_display = ("user_display", "id", "mobile","city")
    search_fields = (
        "user__username", "user__first_name", "user__phone","user__last_name", "user__email",
    )

    autocomplete_fields = ("user",)