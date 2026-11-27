from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone

from .models import Appointment, Availability


def free_slots(doctor, day):
    """Return a sorted list of (start, end) bookable slots for `doctor` on `day`."""
    today = timezone.localdate()
    max_days = getattr(settings, "APPOINTMENT_MAX_DAYS_AHEAD", 60)
    if day < today or day > today + timedelta(days=max_days):
        return []

    day_start = timezone.make_aware(datetime.combine(day, datetime.min.time()))
    day_end = day_start + timedelta(days=1)

    taken = set(
        Appointment.objects.filter(
            doctor=doctor,
            status=Appointment.Status.BOOKED,
            start__gte=day_start,
            start__lt=day_end,
        ).values_list("start", flat=True)
    )

    now = timezone.now()
    slots = []
    for window in Availability.objects.filter(doctor=doctor, weekday=day.weekday()):
        step = timedelta(minutes=window.slot_minutes)
        cursor = datetime.combine(day, window.start_time)
        limit = datetime.combine(day, window.end_time)
        while cursor + step <= limit:
            start = timezone.make_aware(cursor)
            if start > now and start not in taken:
                slots.append((start, timezone.make_aware(cursor + step)))
            cursor += step

    slots.sort()
    return slots