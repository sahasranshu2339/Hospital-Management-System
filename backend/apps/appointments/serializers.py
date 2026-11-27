from datetime import date, datetime

from django.utils import timezone
from rest_framework import serializers

from apps.doctors.models import Doctor
from apps.patients.models import Patient

from .models import Appointment, Availability
from .services import free_slots


class AvailabilitySerializer(serializers.ModelSerializer):
    slot_minutes = serializers.IntegerField(min_value=10, max_value=120, default=30)

    class Meta:
        model = Availability
        fields = ["id", "weekday", "start_time", "end_time", "slot_minutes"]
        read_only_fields = ["id"]

    def validate(self, attrs):
        instance = self.instance
        weekday = attrs.get("weekday", instance.weekday if instance else None)
        start = attrs.get("start_time", instance.start_time if instance else None)
        end = attrs.get("end_time", instance.end_time if instance else None)
        slot = attrs.get("slot_minutes", instance.slot_minutes if instance else 30)

        if end <= start:
            raise serializers.ValidationError("End time must be after start time.")

        minutes = (datetime.combine(date.min, end) - datetime.combine(date.min, start)).total_seconds() / 60
        if minutes < slot:
            raise serializers.ValidationError("The window is shorter than one slot.")

        overlapping = Availability.objects.filter(
            doctor__user=self.context["request"].user,
            weekday=weekday,
            start_time__lt=end,
            end_time__gt=start,
        )
        if instance:
            overlapping = overlapping.exclude(pk=instance.pk)
        if overlapping.exists():
            raise serializers.ValidationError("This overlaps another window on the same day.")

        return attrs


class AppointmentSerializer(serializers.ModelSerializer):
    """Read-only view of an appointment."""

    doctor_name = serializers.SerializerMethodField()
    specialization = serializers.CharField(source="doctor.specialization", read_only=True)
    patient_name = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = [
            "id", "doctor", "doctor_name", "specialization",
            "patient", "patient_name", "start", "end",
            "status", "reason", "doctor_notes", "created_at",
        ]
        read_only_fields = fields

    def get_doctor_name(self, obj):
        return obj.doctor.user.get_full_name()

    def get_patient_name(self, obj):
        return obj.patient.user.get_full_name()


class AppointmentCreateSerializer(serializers.Serializer):
    doctor = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.filter(is_listed=True, user__is_active=True)
    )
    start = serializers.DateTimeField()
    reason = serializers.CharField(max_length=500, required=False, allow_blank=True, default="")

    def validate(self, attrs):
        doctor = attrs["doctor"]
        start = attrs["start"]

        slots = dict(free_slots(doctor, timezone.localtime(start).date()))
        if start not in slots:
            raise serializers.ValidationError({"start": "This time slot is not available."})
        attrs["end"] = slots[start]

        patient, _ = Patient.objects.get_or_create(user=self.context["request"].user)
        clash = Appointment.objects.filter(
            patient=patient,
            status=Appointment.Status.BOOKED,
            start__lt=attrs["end"],
            end__gt=start,
        )
        if clash.exists():
            raise serializers.ValidationError("You already have an appointment at this time.")
        attrs["patient"] = patient
        return attrs

    def create(self, validated_data):
        return Appointment.objects.create(**validated_data)


class CompleteSerializer(serializers.Serializer):
    doctor_notes = serializers.CharField(required=False, allow_blank=True, default="")  