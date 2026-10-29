from django.contrib import admin

from .models import Specialization, Doctor


@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description")
    search_fields = ("name",)

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "last_name",
        "first_name",
        "specialization",
        "experience_years",
        "is_active"
    )

    list_filter = ("specialization", "is_active")

    search_fields = ("first_name", "last_name")