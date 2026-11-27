from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.accounts.models import User

from .models import Doctor


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def ensure_doctor_profile(sender, instance, **kwargs):
    if instance.role == User.Role.DOCTOR:
        Doctor.objects.get_or_create(user=instance)