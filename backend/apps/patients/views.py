from django.db.models import Q
from rest_framework import generics, viewsets

from apps.accounts.permissions import IsAdminRole, IsPatientRole,IsDoctorRole

from .models import Patient
from .serializers import PatientSerializer


class PatientMeView(generics.RetrieveUpdateAPIView):
    """A patient reads and edits only their own profile."""

    serializer_class = PatientSerializer
    permission_classes = [IsPatientRole]
    http_method_names = ["get", "patch", "head", "options"]

    def get_object(self):
        patient, _ = Patient.objects.select_related("user").get_or_create(user=self.request.user)
        return patient


class PatientViewSet(viewsets.ReadOnlyModelViewSet):
    """Admin-only list of all patients."""

    serializer_class = PatientSerializer
    permission_classes = [IsAdminRole]

    def get_queryset(self):
        queryset = Patient.objects.select_related("user").order_by("-created_at", "-id")
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(user__email__icontains=search)
                | Q(user__first_name__icontains=search)
                | Q(user__last_name__icontains=search)
            )
        return queryset



class MyPatientsView(generics.ListAPIView):
    """A doctor sees only patients who have booked with them."""

    serializer_class = PatientSerializer
    permission_classes = [IsDoctorRole]

    def get_queryset(self):
        return (
            Patient.objects.select_related("user")
            .filter(
                appointments__doctor__user=self.request.user,
                appointments__status__in=["BOOKED", "COMPLETED"],
            )
            .distinct()
            .order_by("user__first_name", "user__last_name", "id")
        )