from django.db import models
from django.db.models import F, Q

from apps.doctors.models import Doctor
from apps.patients.models import Patient


class Availability(models.Model):
    """One weekly working window for a doctor, e.g. Monday 09:00-12:00."""

    class Weekday(models.IntegerChoices):
        MONDAY = 0, "Monday"
        TUESDAY = 1, "Tuesday"
        WEDNESDAY = 2, "Wednesday"
        THURSDAY = 3, "Thursday"
        FRIDAY = 4, "Friday"
        SATURDAY = 5, "Saturday"
        SUNDAY = 6, "Sunday"

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="availability")
    weekday = models.PositiveSmallIntegerField(choices=Weekday.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    slot_minutes = models.PositiveSmallIntegerField(default=30)

    class Meta:
        ordering = ["weekday", "start_time"]
        verbose_name_plural = "availability"
        constraints = [
            models.CheckConstraint(
                condition=Q(end_time__gt=F("start_time")),
                name="availability_end_after_start",
            ),
        ]

    def __str__(self):
        return f"{self.doctor} - {self.get_weekday_display()} {self.start_time}-{self.end_time}"


class Appointment(models.Model):
    class Status(models.TextChoices):
        BOOKED = "BOOKED", "Booked"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    doctor = models.ForeignKey(Doctor, on_delete=models.PROTECT, related_name="appointments")
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="appointments")
    start = models.DateTimeField(db_index=True)
    end = models.DateTimeField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.BOOKED)
    reason = models.CharField(max_length=500, blank=True)
    doctor_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["start"]
        constraints = [
            # The database refuses two BOOKED appointments for the same doctor
            # at the same time. Cancelled ones don't count, so a slot frees up.
            models.UniqueConstraint(
                fields=["doctor", "start"],
                condition=Q(status="BOOKED"),
                name="unique_booked_slot_per_doctor",
            ),
            models.UniqueConstraint(
                fields=["patient", "start"],
                condition=Q(status="BOOKED"),
                name="unique_booked_slot_per_patient",
            ),
        ]

    def __str__(self):
        return f"{self.patient} with {self.doctor} at {self.start:%Y-%m-%d %H:%M}"