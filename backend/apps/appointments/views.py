from datetime import date

from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import User
from apps.accounts.permissions import IsDoctorRole, IsPatientRole
from apps.doctors.models import Doctor

from .models import Appointment, Availability
from .serializers import (
    AppointmentCreateSerializer,
    AppointmentSerializer,
    AvailabilitySerializer,
    CompleteSerializer,
)
from .services import free_slots


class AvailabilityViewSet(viewsets.ModelViewSet):
    """A doctor manages their own weekly working windows."""

    serializer_class = AvailabilitySerializer
    permission_classes = [IsDoctorRole]

    def get_queryset(self):
        return Availability.objects.filter(doctor__user=self.request.user)

    def perform_create(self, serializer):
        doctor, _ = Doctor.objects.get_or_create(user=self.request.user)
        serializer.save(doctor=doctor)


class SlotsView(APIView):
    """GET /api/appointments/slots/?doctor=1&date=2026-11-30"""

    def get(self, request):
        try:
            doctor_id = int(request.query_params.get("doctor", ""))
            day = date.fromisoformat(request.query_params.get("date", ""))
        except ValueError:
            return Response(
                {"detail": "Provide ?doctor=<id>&date=YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        doctor = get_object_or_404(
            Doctor.objects.filter(is_listed=True, user__is_active=True), pk=doctor_id
        )
        slots = [{"start": s, "end": e} for s, e in free_slots(doctor, day)]
        return Response({"doctor": doctor.pk, "date": day, "slots": slots})


class AppointmentViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    serializer_class = AppointmentSerializer

    def get_permissions(self):
        if self.action == "create":
            return [IsPatientRole()]
        if self.action == "complete":
            return [IsDoctorRole()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        queryset = Appointment.objects.select_related(
            "doctor__user", "patient__user"
        ).order_by("start", "id")

        # Each role only ever sees its own appointments.
        if user.role == User.Role.PATIENT:
            queryset = queryset.filter(patient__user=user)
        elif user.role == User.Role.DOCTOR:
            queryset = queryset.filter(doctor__user=user)
        elif user.role != User.Role.ADMIN:
            return queryset.none()

        params = self.request.query_params
        status_filter = params.get("status")
        if status_filter in Appointment.Status.values:
            queryset = queryset.filter(status=status_filter)
        if params.get("upcoming") == "true":
            queryset = queryset.filter(
                start__gte=timezone.now(), status=Appointment.Status.BOOKED
            )
        return queryset

    def create(self, request):
        serializer = AppointmentCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        try:
            with transaction.atomic():
                appointment = serializer.save()
        except IntegrityError:
            # Someone else booked the same slot a split second earlier.
            return Response(
                {"start": ["This slot was just taken. Please choose another."]},
                status=status.HTTP_409_CONFLICT,
            )
        return Response(AppointmentSerializer(appointment).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        appointment = self.get_object()  # 404 if it isn't yours
        if appointment.status != Appointment.Status.BOOKED:
            return Response({"detail": "Only booked appointments can be cancelled."}, status=400)
        if appointment.start <= timezone.now():
            return Response({"detail": "Past appointments cannot be cancelled."}, status=400)
        appointment.status = Appointment.Status.CANCELLED
        appointment.save(update_fields=["status", "updated_at"])
        return Response(AppointmentSerializer(appointment).data)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        appointment = self.get_object()
        if appointment.status != Appointment.Status.BOOKED:
            return Response({"detail": "Only booked appointments can be completed."}, status=400)
        if appointment.start > timezone.now():
            return Response({"detail": "This appointment has not started yet."}, status=400)
        data = CompleteSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        appointment.status = Appointment.Status.COMPLETED
        appointment.doctor_notes = data.validated_data["doctor_notes"]
        appointment.save(update_fields=["status", "doctor_notes", "updated_at"])
        return Response(AppointmentSerializer(appointment).data)