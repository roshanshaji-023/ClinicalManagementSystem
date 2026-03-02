from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import LabTestType,LabTestPrescription
from .serializer import LabTestTypeSerializer,LabTestPrescriptionSerializer,BulkLabTestPrescriptionSerializer

# Create your views here.

class LabTestTypeViewSet(viewsets.ModelViewSet):
    """
    Handles:
    - List all test types
    - Create new test type
    - Retrieve single test type
    - Update test type
    - Delete test type
    """
    queryset = LabTestType.objects.all()
    serializer_class = LabTestTypeSerializer

#List & Retrieve
class LabTestPrescriptionAPIView(APIView):

    def get(self, request):
        prescriptions = LabTestPrescription.objects.select_related(
            'doctor',
            'appointment__patient',
            'test_type'
        ).all()

        serializer = LabTestPrescriptionSerializer(prescriptions, many=True)
        return Response(serializer.data)


#Bulk Create
class BulkLabTestPrescriptionAPIView(APIView):

    def post(self, request):
        serializer = BulkLabTestPrescriptionSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Tests prescribed successfully"},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
