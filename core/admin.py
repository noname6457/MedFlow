from django.contrib import admin

from .models import Specialization, Doctor
from .models import Appointment, AppointmentSlot

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

@admin.register(AppointmentSlot)
class AppointmentSlotAdmin(admin.ModelAdmin):
    list_display = ("doctor", "start_at", "end_at")
    list_filter = ("doctor", "doctor__specialization")
    search_fields = (
        "doctor__first_name",
        "doctor__last_name",
    )
    date_hierarchy = "start_at"
    list_select_related = ("doctor", "doctor__specialization")


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("patient", "slot", "created_at")
    list_filter = (
        "slot__doctor",
        "slot__doctor__specialization",
    )
    search_fields = (
        "patient__username",
        "patient__email",
        "slot__doctor__first_name",
        "slot__doctor__last_name",
    )
    readonly_fields = ("created_at",)
    list_select_related = ("patient", "slot", "slot__doctor")