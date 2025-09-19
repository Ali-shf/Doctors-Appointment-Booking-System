from django.contrib import admin
from .models import TimeSheet, Visit, EmailMessage


@admin.register(TimeSheet)
class TimesheetAdmin(admin.ModelAdmin):
    list_display = ("doctor", "clinic", "end")
    search_fields = ("doctor__user__username", "clinic__name")
    list_select_related = ("doctor__user", "clinic")  


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ("doctor", "patient", "clinic", "date", "start_meet", "price")
    list_filter = ("clinic", "doctor", "date")     
    search_fields = ("doctor__user__username", "patient__username")
    date_hierarchy = "date"
    list_select_related = ("doctor__user", "patient", "clinic")


@admin.register(EmailMessage)
class EmailMessageAdmin(admin.ModelAdmin):
   
    def short_description(self, obj):
        return (obj.description[:40] + "...") if obj.description else ""
    short_description.short_description = "Description"

    list_display = ("visit", "short_description")
    search_fields = (
        "visit__doctor__user__username",
        "visit__patient__username",
    )
    list_select_related = ("visit__doctor__user", "visit__patient")
