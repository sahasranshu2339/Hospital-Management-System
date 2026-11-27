from django.db.models import Q
from rest_framework import generics, viewsets

from apps.accounts.permissions import IsDoctorRole

from .models import Doctor
from .serializers import DoctorPublicSerializer, DoctorSelfSerializer


class DoctorViewSet(viewsets.ReadOnlyModelViewSet):
    """Any logged-in user can browse listed, active doctors."""

    serializer_class = DoctorPublicSerializer

    def get_queryset(self):
        queryset = (
            Doctor.objects.select_related("user")
            .filter(is_listed=True, user__is_active=True)
            .order_by("user__first_name", "user__last_name", "id")
        )
        params = self.request.query_params
        specialization = params.get("specialization")
        if specialization:
            queryset = queryset.filter(specialization__iexact=specialization)
        search = params.get("search")
        if search:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search)
                | Q(user__last_name__icontains=search)
                | Q(specialization__icontains=search)
            )
        return queryset


class DoctorMeView(generics.RetrieveUpdateAPIView):
    serializer_class = DoctorSelfSerializer
    permission_classes = [IsDoctorRole]
    http_method_names = ["get", "patch", "head", "options"]

    def get_object(self):
        doctor, _ = Doctor.objects.select_related("user").get_or_create(user=self.request.user)
        return doctor