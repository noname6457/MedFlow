from django.urls import path

from .views import (
                    DoctorDetaileView,
                    DoctorListView,
                    DoctorSlotListView,
                    MyAppointmentListView,
                    book_appointment,
                    cancel_appointment,
)

urlpatterns = [
    path(
        "doctors/",
        DoctorListView.as_view(),
        name="doctor-list"
    ),

    path(
        "doctors/<int:pk>/",
        DoctorDetaileView.as_view(),
        name="doctor-detail"
    ),

    path(
    "doctors/<int:pk>/slots/",
    DoctorSlotListView.as_view(),
    name="doctor-slots"
    ),

    path(
    "doctors/<int:pk>/slots/<int:slot_id>/book/",
    book_appointment,
    name="appointment-book"
    ),

    path(
    "appointments/",
    MyAppointmentListView.as_view(),
    name="my-appointments"
    ),

    path(
        "appointments/<int:pk>/",
        cancel_appointment,
        name="appointment-cancel"
    )
]