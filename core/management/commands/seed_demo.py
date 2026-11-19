
from django.core.management.base import BaseCommand
from django.core.management import call_command

from core.models import Doctor, Specialization


class Command(BaseCommand):
    help = "Создание демонстрационных врачей и расписания"

    def handle(self, *args, **options):
        demo_doctors = [
            {
                "first_name": "Александр",
                "last_name": "Иванов",
                "specialization": "Терапевт",
                "experience_years": 8,
                "description": (
                    "Проводит первичные консультации, "
                    "занимается профилактикой заболеваний."
                ),
            },
            {
                "first_name": "Мария",
                "last_name": "Петрова",
                "specialization": "Кардиолог",
                "experience_years": 12,
                "description": (
                    "Консультирует по вопросам здоровья "
                    "сердечно-сосудистой системы."
                ),
            },
            {
                "first_name": "Екатерина",
                "last_name": "Смирнова",
                "specialization": "Невролог",
                "experience_years": 6,
                "description": (
                    "Проводит консультации по вопросам "
                    "неврологического здоровья."
                ),
            },
        ]

        for data in demo_doctors:
            specialization, _ = (
                Specialization.objects.get_or_create(
                    name=data["specialization"]
                )
            )

            doctor, created = Doctor.objects.get_or_create(
                first_name=data["first_name"],
                last_name=data["last_name"],
                specialization=specialization,
                defaults={
                    "experience_years": data["experience_years"],
                    "description": data["description"],
                    "is_active": True,
                }
            )

            if created:
                self.stdout.write(
                    f"Создан врач: {doctor}"
                )
            else:
                self.stdout.write(
                    f"Врач уже существует: {doctor}"
                )

            call_command(
                "generate_schedule",
                doctor=doctor.id,
                days=30
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Демонстрационные данные подготовлены!"
            )
        )
