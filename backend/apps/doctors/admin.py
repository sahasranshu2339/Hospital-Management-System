from django.contrib import admin

from .models import Doctor


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("user", "specialization", "consultation_fee", "is_listed")
    list_filter = ("is_listed", "specialization")
    search_fields = ("user__email", "user__first_name", "user__last_name", "specialization")