from django.contrib import admin
from .models import TimeSheet, Visit, VisitLog


@admin.register(TimeSheet)
class TimesheetAdmin(admin.ModelAdmin):
    list_display = ("doctor", "clinic", "end")
    search_fields = ("doctor__user__username", "clinic__name")
    list_select_related = ("doctor__user", "clinic")  



@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ("doctor", "patient", "clinic", "date", "start_meet", "price", "status")
    list_filter = ("clinic", "doctor", "date", "status")     
    search_fields = ("doctor__user__username", "patient__username")
    date_hierarchy = "date"
    list_select_related = ("doctor__user", "patient", "clinic")



@admin.register(VisitLog)
class VisitLogAdmin(admin.ModelAdmin):

    @admin.display(description="Description")
    def description_preview(self, obj):
        return (obj.description[:40] + "...") if obj.description else ""

    list_display = ("visit", "support_code", "description_preview", "created_at")
    search_fields = (
        "visit__doctor__user__username",
        "visit__patient__username",
        "support_code",
    )
    list_select_related = ("visit__doctor__user", "visit__patient")
    readonly_fields = ("support_code", "description", "created_at")
