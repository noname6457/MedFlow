from django.contrib import admin
from django.urls import include, path

from core.views import health_check
from core.page_views import (
    home_page, 
    doctors_page, 
    doctor_detail_page,
    login_page,
    register_page,
    appointments_page
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/health/", health_check),
    path("api/", include("core.urls")),
    path("api/auth/", include("users.urls")),

    path("", home_page, name="home"),
    path("doctors/", doctors_page, name="doctors-page"),
    path("doctors/<int:pk>/", doctor_detail_page, name="doctor-detail-page"),
    path("login/", login_page, name="login-page"),
    path("register/", register_page, name="register-page"),
    path("appointments/", appointments_page, name="appointments-page")
]
