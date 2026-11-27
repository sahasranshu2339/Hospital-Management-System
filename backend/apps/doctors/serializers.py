from rest_framework import serializers

from .models import Doctor


class DoctorPublicSerializer(serializers.ModelSerializer):
    """What patients see when browsing. No email, no licence number."""

    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Doctor
        fields = ["id", "full_name", "specialization", "experience_years", "consultation_fee", "bio"]

    def get_full_name(self, obj):
        return obj.user.get_full_name()


class DoctorSelfSerializer(serializers.ModelSerializer):
    """What a doctor sees and can edit about themself."""

    email = serializers.EmailField(source="user.email", read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Doctor
        fields = [
            "id", "email", "full_name", "specialization", "license_number",
            "experience_years", "consultation_fee", "bio", "is_listed",
        ]
        # A doctor may edit only bio and experience. Fee, specialization,
        # licence and listing are controlled by the admin.
        read_only_fields = ["id", "specialization", "license_number", "consultation_fee", "is_listed"]

    def get_full_name(self, obj):
        return obj.user.get_full_name() 