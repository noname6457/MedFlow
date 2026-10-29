from django.db import models


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