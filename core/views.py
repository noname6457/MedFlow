from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Doctor
from .serializers import DoctorSerializer


@api_view(["GET"])
def health_check(request):
    return Response({
        "status": "ok",
        "project": "MedFlow",
        "message": "MedFlow API is running"
    })


class DoctorListView(generics.ListAPIView):
    queryset = Doctor.objects.select_related("specialization").all()

    serializer_class = DoctorSerializer


class DoctorDetaileView(generics.RetrieveAPIView):
    queryset = Doctor.objects.select_related("specialization").all()

    serializer_class = DoctorSerializer