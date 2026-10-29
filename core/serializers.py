from rest_framework import serializers

from .models import Doctor


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
    