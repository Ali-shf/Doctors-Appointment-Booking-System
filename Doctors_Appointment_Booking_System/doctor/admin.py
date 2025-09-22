from django.contrib import admin
from django.db.models import Avg,Count
from django.utils.html import format_html

from doctor.models import Comment,Clinic


@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = (
    "name","founded_date","address","working_hours")
    search_fields = ("name" , "address")
    fieldsets = ((None, {"fields": ("name", "founded_date", "address", "description")}),("Working hours (JSON)", {"fields": ("working_hours",)}))



@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "clinic_id", "doctor_id", "patient_id", "rate", "created_at", "comment")
    autocomplete_fields = ("doctor_id", "patient_id", "clinic_id")  # corrected
    readonly_fields = ("id", "clinic_id", "doctor_id", "patient_id", "rate", "created_at", "comment")


#TODO: CSV export
