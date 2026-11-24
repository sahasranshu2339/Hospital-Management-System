from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", User.Role.ADMIN)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    class Role(models.TextChoices):
        PATIENT = "PATIENT", "Patient"
        DOCTOR = "DOCTOR", "Doctor"
        ADMIN = "ADMIN", "Admin"

    username = None  # we don't use usernames
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.PATIENT)
    phone = models.CharField(max_length=20, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # email and password are asked for by default

    objects = UserManager()

    def __str__(self):
        return f"{self.email} ({self.role})"