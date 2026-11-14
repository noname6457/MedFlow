
from datetime import datetime, time, timedelta
from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.utils import timezone

from core.models import AppointmentSlot, Doctor, Specialization


class ScheduleGeneratorTests(TestCase):

    def setUp(self):
        specialization = Specialization.objects.create(
            name="Терапевт"
        )

        self.doctor = Doctor.objects.create(
            first_name="Иван",
            last_name="Иванов",
            specialization=specialization,
            experience_years=5,
        )

    def generate(self, **kwargs):
        output = StringIO()

        call_command(
            "generate_schedule",
            doctor=self.doctor.id,
            stdout=output,
            **kwargs
        )

        return output.getvalue()

    def test_schedule_creation(self):
        self.generate(days=7)

        slots = AppointmentSlot.objects.filter(
            doctor=self.doctor
        )

        self.assertGreater(slots.count(), 0)

        for slot in slots:
            local_start = timezone.localtime(slot.start_at)
            local_end = timezone.localtime(slot.end_at)

            self.assertLess(local_start.weekday(), 5)
            self.assertEqual(
                (slot.end_at - slot.start_at).total_seconds(),
                30 * 60
            )

            self.assertGreaterEqual(local_start.time(), time(9, 0))
            self.assertLessEqual(local_end.time(), time(18, 0))

    def test_no_duplicates(self):
        self.generate(days=7)

        first_count = AppointmentSlot.objects.filter(
            doctor=self.doctor
        ).count()

        self.generate(days=7)

        second_count = AppointmentSlot.objects.filter(
            doctor=self.doctor
        ).count()

        self.assertEqual(first_count, second_count)

    def test_lunch_break(self):
        self.generate(days=7)

        slots = AppointmentSlot.objects.filter(
            doctor=self.doctor
        )

        for slot in slots:
            start = timezone.localtime(slot.start_at).time()
            end = timezone.localtime(slot.end_at).time()

            overlaps_break = (
                start < time(14, 0)
                and end > time(13, 0)
            )

            self.assertFalse(overlaps_break)

    def test_overlapping_slots(self):
        # Выбираем ближайший рабочий день в будущем.
        current_date = timezone.localdate() + timedelta(days=1)

        while current_date.weekday() >= 5:
            current_date += timedelta(days=1)

        tz = timezone.get_current_timezone()

        start = timezone.make_aware(
            datetime.combine(current_date, time(9, 15)),
            tz
        )

        end = start + timedelta(minutes=30)

        existing_slot = AppointmentSlot.objects.create(
            doctor=self.doctor,
            start_at=start,
            end_at=end
        )

        days_until = (
            current_date - timezone.localdate()
        ).days + 1

        self.generate(days=days_until)

        overlapping = AppointmentSlot.objects.filter(
            doctor=self.doctor,
            start_at__lt=existing_slot.end_at,
            end_at__gt=existing_slot.start_at
        ).exclude(pk=existing_slot.pk)

        self.assertFalse(overlapping.exists())

    def test_invalid_parameters(self):
        with self.assertRaises(CommandError):
            self.generate(days=0)

        with self.assertRaises(CommandError):
            self.generate(duration=0)

        with self.assertRaises(CommandError):
            self.generate(
                start="18:00",
                end="09:00"
            )

        with self.assertRaises(CommandError):
            self.generate(
                start="invalid"
            )
