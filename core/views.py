from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

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
    serializer_class = DoctorSerializer

    def get_queryset(self):
        queryset = Doctor.objects.select_related("specialization").filter(is_active=True)

        specialization = self.request.query_params.get("specialization")

        min_experience = self.request.query_params.get("min_experience")

        search = self.request.query_params.get("search")

        if specialization:
            queryset = queryset.filter(specialization__name__iexact=specialization)

        if min_experience is not None:
            try:
                years = int(min_experience)
                if years < 0:
                    raise ValueError
            except ValueError:
                raise ValidationError({"min_experience": "Введите неотрицательное целое число."})

            queryset = queryset.filter(experience_years__gte=years)

        if search:
            queryset = queryset.filter(last_name__icontains=search)

        return queryset

            
class DoctorDetaileView(generics.RetrieveAPIView):
    queryset = Doctor.objects.select_related("specialization").all()

    serializer_class = DoctorSerializer