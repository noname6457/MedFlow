from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from .models import Doctor


def home_page(request):
    return render(request, "home.html")

def doctors_page(request):
    return render(request, "doctors.html")

def doctor_detail_page(request, pk):
    doctor = get_object_or_404(
        Doctor.objects.select_related("specialization"),
        pk=pk,
        is_active=True
    )

    return render(
        request,
        "doctor_detail.html",
        {"doctor": doctor}
    )

def login_page(request):
    return render(request, "login.html")


def register_page(request):
    return render(request, "register.html")

@login_required(login_url="/login/")
def appointments_page(request):
    return render(request, "appointments.html")