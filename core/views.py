from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Appointment, AppointmentSlot, Doctor
from .serializers import (
    AppointmentSerializer,
    AppointmentSlotSerializer,
    DoctorSerializer,
)


@api_view(["GET"])
def health_check(request):
    return Response({
        "status": "ok",
        "project": "MedFlow",
        "message": "MedFlow API is running"
    })


class DoctorListView(generics.ListAPIView):
    serializer_class = DoctorSerializer

    def get_queryset(self):
        queryset = Doctor.objects.select_related("specialization").filter(is_active=True)

        specialization = self.request.query_params.get("specialization")

        min_experience = self.request.query_params.get("min_experience")

        search = self.request.query_params.get("search")

        if specialization:
            queryset = queryset.filter(specialization__name__iexact=specialization)

        if min_experience is not None:
            try:
                years = int(min_experience)
                if years < 0:
                    raise ValueError
            except ValueError:
                raise ValidationError({"min_experience": "Введите неотрицательное целое число."})

            queryset = queryset.filter(experience_years__gte=years)

        if search:
            queryset = queryset.filter(last_name__icontains=search)

        return queryset

            
class DoctorDetaileView(generics.RetrieveAPIView):
    queryset = Doctor.objects.select_related(
        "specialization"
    ).filter(is_active=True)

    serializer_class = DoctorSerializer

class DoctorSlotListView(generics.ListAPIView):
    serializer_class = AppointmentSlotSerializer

    def get_queryset(self):
        doctor = get_object_or_404(
            Doctor,
            pk=self.kwargs["pk"],
            is_active=True
        )

        queryset = AppointmentSlot.objects.filter(
            doctor=doctor,
            start_at__gte=timezone.now(),
            appointment__isnull=True
        )

        date_value = self.request.query_params.get("date")

        if date_value:
            try:
                requested_date = parse_date(date_value)
            except ValueError:
                requested_date = None

            if requested_date is None:
                raise ValidationError({
                    "date": "Введите дату в формате ГГГГ-ММ-ДД."
                })

            queryset = queryset.filter(
                start_at__date=requested_date
            )

        return queryset.order_by("start_at")

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def book_appointment(request, pk, slot_id):
    with transaction.atomic():
        slot = get_object_or_404(
            AppointmentSlot.objects.select_for_update(),
            pk=slot_id,
            doctor_id=pk,
            doctor__is_active=True
        )

        if slot.start_at <= timezone.now():
            return Response(
                {"error": "Нельзя записаться на прошедшее время."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if Appointment.objects.filter(slot=slot).exists():
            return Response(
                {"error": "Это время уже занято."},
                status=status.HTTP_409_CONFLICT
            )

        try:
            with transaction.atomic():
                appointment = Appointment.objects.create(
                    slot=slot,
                    patient=request.user
                )
        except IntegrityError:
            return Response(
                {"error": "Это время уже занято."},
                status=status.HTTP_409_CONFLICT
            )

    return Response(
        {
            "message": "Вы успешно записались на приём.",
            "appointment": {
                "id": appointment.id,
                "doctor": str(slot.doctor),
                "start_at": slot.start_at.isoformat(),
                "end_at": slot.end_at.isoformat()
            }
        },
        status=status.HTTP_201_CREATED
    )

class MyAppointmentListView(generics.ListAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Appointment.objects.filter(
            patient=self.request.user
        ).select_related(
            "slot__doctor"
        ).order_by("-created_at")

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def cancel_appointment(request, pk):
    with transaction.atomic():
        appointment = get_object_or_404(
            Appointment,
            pk=pk,
            patient=request.user
        )

        slot = AppointmentSlot.objects.select_for_update().get(
            pk=appointment.slot_id
        )

        if slot.start_at <= timezone.now():
            return Response(
                {
                    "error": "Нельзя отменить прошедший приём."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Повторно проверяем запись после блокировки слота.
        appointment = get_object_or_404(
            Appointment,
            pk=pk,
            patient=request.user
        )

        appointment.delete()

    return Response(
        status=status.HTTP_204_NO_CONTENT
    )