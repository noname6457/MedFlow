from django.test import TestCase

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from rest_framework.test import APIClient

from .models import (
    Appointment,
    AppointmentSlot,
    Doctor,
    Specialization,
)


User = get_user_model()


class AppointmentBookingTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.patient = User.objects.create_user(
            username="testpatient",
            password="TestPassword123!"
        )

        self.specialization = Specialization.objects.create(
            name="Терапевт"
        )

        self.doctor = Doctor.objects.create(
            first_name="Иван",
            last_name="Иванов",
            specialization=self.specialization,
            experience_years=5,
        )

        start_at = timezone.now() + timedelta(days=1)

        self.slot = AppointmentSlot.objects.create(
            doctor=self.doctor,
            start_at=start_at,
            end_at=start_at + timedelta(minutes=30),
        )

        self.url = (
            f"/api/doctors/{self.doctor.id}/"
            f"slots/{self.slot.id}/book/"
        )

    def test_successful_booking(self):
        self.client.force_authenticate(user=self.patient)

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            Appointment.objects.filter(
                slot=self.slot,
                patient=self.patient
            ).exists()
        )

    def test_duplicate_booking(self):
        self.client.force_authenticate(user=self.patient)

        first_response = self.client.post(self.url)
        second_response = self.client.post(self.url)

        self.assertEqual(first_response.status_code, 201)
        self.assertEqual(second_response.status_code, 409)

        self.assertEqual(
            Appointment.objects.filter(slot=self.slot).count(),
            1
        )

    def test_unauthorized_booking(self):
        response = self.client.post(self.url)

        self.assertIn(response.status_code, [401, 403])

        self.assertFalse(
            Appointment.objects.filter(slot=self.slot).exists()
        )

    def test_booking_past_slot(self):
        self.client.force_authenticate(user=self.patient)

        past_start = timezone.now() - timedelta(days=1)

        past_slot = AppointmentSlot.objects.create(
            doctor=self.doctor,
            start_at=past_start,
            end_at=past_start + timedelta(minutes=30),
        )

        past_url = (
            f"/api/doctors/{self.doctor.id}/"
            f"slots/{past_slot.id}/book/"
        )

        response = self.client.post(past_url)

        self.assertEqual(response.status_code, 400)

        self.assertFalse(
            Appointment.objects.filter(slot=past_slot).exists()
        )

    def test_cancel_appointment(self):
        self.client.force_authenticate(user=self.patient)

        appointment = Appointment.objects.create(
            slot=self.slot,
            patient=self.patient
        )

        url = f"/api/appointments/{appointment.id}/"

        response = self.client.delete(url)

        self.assertEqual(response.status_code, 204)

        self.assertFalse(
            Appointment.objects.filter(
                pk=appointment.id
            ).exists()
        )

        self.assertFalse(
            Appointment.objects.filter(
                slot=self.slot
            ).exists()
        )

    def test_patient_cannot_cancel_other_appointment(self):
        other_patient = User.objects.create_user(
            username="otherpatient",
            password="TestPassword123!"
        )

        appointment = Appointment.objects.create(
            slot=self.slot,
            patient=other_patient
        )

        self.client.force_authenticate(user=self.patient)

        url = f"/api/appointments/{appointment.id}/"

        response = self.client.delete(url)

        self.assertEqual(response.status_code, 404)

        self.assertTrue(
            Appointment.objects.filter(
                pk=appointment.id,
                patient=other_patient
            ).exists()
        )
