from django.contrib import admin
from .models import Timesheet,Visit,EmailMessage

@admin.register(Timesheet)
class TimesheetAdmin(admin.ModelAdmin):
    
    list_display = ("doctor","clinic","end")
    search_fields = ("doctor__user__username", "clinic__name")
    
@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ("doctor", "patient", "clinic", "date", "start_meet", "price")
    list_filter = ("clinic", "doctor")  
    search_fields = ("doctor__user__username", "patient__username")  

@admin.register(EmailMessage)
class EmailMessageAdmin(admin.ModelAdmin):
    list_display = ("visit", "description")
    search_fields = ("visit__doctor__user__username", "visit__patient__username")