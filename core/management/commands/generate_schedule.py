
from datetime import datetime, time, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from core.models import AppointmentSlot, Doctor


class Command(BaseCommand):
    help = "Генерация расписания врача"

    def add_arguments(self, parser):
        parser.add_argument("--doctor", type=int, required=True)
        parser.add_argument("--days", type=int, default=30)
        parser.add_argument("--start", default="09:00")
        parser.add_argument("--end", default="18:00")
        parser.add_argument("--duration", type=int, default=30)
        parser.add_argument("--break-start", default="13:00")
        parser.add_argument("--break-end", default="14:00")

    def handle(self, *args, **options):
        try:
            doctor = Doctor.objects.get(
                pk=options["doctor"],
                is_active=True
            )
        except Doctor.DoesNotExist as exc:
            raise CommandError(
                "Активный врач с таким ID не найден."
            ) from exc

        days = options["days"]
        duration = options["duration"]

        if days < 1 or days > 365:
            raise CommandError(
                "Количество дней должно быть от 1 до 365."
            )

        if duration < 1:
            raise CommandError(
                "Продолжительность приёма должна быть положительной."
            )

        def parse_time(value):
            try:
                return time.fromisoformat(value)
            except ValueError as exc:
                raise CommandError(
                    f"Некорректное время: {value}"
                ) from exc

        start_time = parse_time(options["start"])
        end_time = parse_time(options["end"])
        break_start = parse_time(options["break_start"])
        break_end = parse_time(options["break_end"])

        if start_time >= end_time:
            raise CommandError(
                "Начало рабочего дня должно быть раньше окончания."
            )

        if not (
            start_time <= break_start < break_end <= end_time
        ):
            raise CommandError(
                "Перерыв должен находиться внутри рабочего дня."
            )

        tz = timezone.get_current_timezone()
        today = timezone.localdate()
        now = timezone.now()

        created = 0
        skipped = 0

        for day_offset in range(days):
            current_date = today + timedelta(days=day_offset)

            # 0 = понедельник, 6 = воскресенье.
            if current_date.weekday() >= 5:
                continue

            current = datetime.combine(
                current_date,
                start_time
            )
            day_end = datetime.combine(
                current_date,
                end_time
            )

            pause_start = datetime.combine(
                current_date,
                break_start
            )
            pause_end = datetime.combine(
                current_date,
                break_end
            )

            while current + timedelta(minutes=duration) <= day_end:
                slot_end = current + timedelta(minutes=duration)

                # Пропускаем время обеда.
                overlaps_break = (
                    current < pause_end
                    and slot_end > pause_start
                )

                if overlaps_break:
                    current = slot_end
                    skipped += 1
                    continue

                aware_start = timezone.make_aware(current, tz)
                aware_end = timezone.make_aware(slot_end, tz)

                # Не создаём слоты в прошлом.
                if aware_start <= now:
                    current = slot_end
                    skipped += 1
                    continue

                with transaction.atomic():
                    # Сериализуем генерацию для одного врача.
                    Doctor.objects.select_for_update().get(pk=doctor.pk)

                    overlaps_existing = AppointmentSlot.objects.filter(
                        doctor=doctor,
                        start_at__lt=aware_end,
                        end_at__gt=aware_start
                    ).exists()

                    if overlaps_existing:
                        skipped += 1
                    else:
                        AppointmentSlot.objects.create(
                            doctor=doctor,
                            start_at=aware_start,
                            end_at=aware_end
                        )
                        created += 1

                current = slot_end

        self.stdout.write(
            self.style.SUCCESS(
                f"Готово! Создано слотов: {created}. "
                f"Пропущено: {skipped}."
            )
        )
