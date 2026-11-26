from rest_framework.permissions import BasePermission

from .models import User


class HasRole(BasePermission):
    allowed_roles = ()

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.role in self.allowed_roles)


class IsAdminRole(HasRole):
    allowed_roles = (User.Role.ADMIN,)


class IsDoctorRole(HasRole):
    allowed_roles = (User.Role.DOCTOR,)


class IsPatientRole(HasRole):
    allowed_roles = (User.Role.PATIENT,)


class IsAdminOrDoctor(HasRole):
    allowed_roles = (User.Role.ADMIN, User.Role.DOCTOR)