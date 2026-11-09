from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )

    class Meta:
        model  = User

        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
        ]

        read_only_fields = ["id"]

    def validate_email(self, value):
        email = value.strip().lower()

        if not email:
            raise serializers.ValidationError("Укажите электронную почту.")

        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("Эта почта уже зарегистрирована.")

        return email

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)