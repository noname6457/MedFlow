from django.urls import path

from .views import DoctorListView, DoctorDetaileView



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
    )
]