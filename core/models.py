from django.conf import settings
from django.db import models
from django.db.models import F, Q


class Specialization(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = "Специализация"
        verbose_name_plural = "Специализации"

class Doctor(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    specialization = models.ForeignKey(
        Specialization,
        on_delete=models.PROTECT,
        related_name="doctors"
    )

    experience_years = models.PositiveIntegerField(default=0)

    description = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

    class Meta:
        ordering = ["last_name", "first_name"]
        verbose_name = "Врач"
        verbose_name_plural = "Врачи"

class AppointmentSlot(models.Model):
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name="slots"
    )

    start_at = models.DateTimeField()
    end_at = models.DateTimeField()

    def __str__(self):
        return f"{self.doctor} - {self.start_at:%d.%m.%Y %H:%M}"

    class Meta:
        ordering = ["start_at"]
        verbose_name = "Временной слот"
        verbose_name_plural = "Временные слоты"

        constraints = [  
            models.UniqueConstraint(
                fields=["doctor", "start_at"],
                name="unique_doctor_slot_start"
            ),
            models.CheckConstraint(
                condition=Q(end_at__gt=F("start_at")),
                name="slot_end_after_start"
            )
        ]


class Appointment(models.Model):
    slot = models.OneToOneField(
        AppointmentSlot,
        on_delete=models.PROTECT,
        related_name="appointment"
    )

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="appointments"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient} - {self.slot}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Запись на приём"
        verbose_name_plural = "Записи на приём"