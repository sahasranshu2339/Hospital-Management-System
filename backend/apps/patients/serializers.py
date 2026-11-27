from datetime import date

from rest_framework import serializers

from .models import Patient


class PatientSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    phone = serializers.CharField(source="user.phone", read_only=True)

    class Meta:
        model = Patient
        fields = [
            "id", "email", "first_name", "last_name", "phone",
            "date_of_birth", "gender", "blood_group", "address",
            "emergency_contact_name", "emergency_contact_phone", "allergies",
        ]
        read_only_fields = ["id"]

    def validate_date_of_birth(self, value):
        if value and value > date.today():
            raise serializers.ValidationError("Date of birth cannot be in the future.")
        return value