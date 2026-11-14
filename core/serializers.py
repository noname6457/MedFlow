from rest_framework import serializers

from .models import Appointment, AppointmentSlot, Doctor


class DoctorSerializer(serializers.ModelSerializer):
    specialization_name = serializers.CharField(
        source="specialization.name",
        read_only=True
    )

    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Doctor

        fields = [  # noqa: RUF012
            'id',
            "first_name",
            "last_name",
            "full_name",
            "specialization",
            "specialization_name",
            "experience_years",
            "description",
            "is_active",
        ]

    def get_full_name(self, obj):
        return f"{obj.last_name} {obj.first_name}"

class AppointmentSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentSlot
        fields = [
            "id",
            "start_at",
            "end_at",
        ]

class AppointmentSerializer(serializers.ModelSerializer):
    doctor_id = serializers.IntegerField(
        source="slot.doctor_id",
        read_only=True
    )

    doctor_name = serializers.CharField(
        source="slot.doctor",
        read_only=True
    )

    start_at = serializers.DateTimeField(
        source="slot.start_at",
        read_only=True
    )

    end_at = serializers.DateTimeField(
        source="slot.end_at",
        read_only=True
    )

    class Meta:
        model = Appointment

        fields = [
            "id",
            "slot",
            "doctor_id",
            "doctor_name",
            "start_at",
            "end_at",
            "created_at",
        ]