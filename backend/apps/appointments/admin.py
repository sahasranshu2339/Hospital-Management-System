from django.contrib import admin

from .models import Appointment, Availability


@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ("doctor", "weekday", "start_time", "end_time", "slot_minutes")
    list_filter = ("weekday",)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("patient", "doctor", "start", "status")
    list_filter = ("status", "doctor")
    date_hierarchy = "start"