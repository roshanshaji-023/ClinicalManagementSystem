from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from reception.models import Appointment
from .models import LabTestType,LabTestPrescription,LabTestReport,LabTestBill
from .serializer import LabTestTypeSerializer,LabTestPrescriptionSerializer,BulkLabTestPrescriptionSerializer,LabTestReportSerializer,LabTestBillSerializer
from authentication.permissions import IsLabTechnician

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
    # permission_classes=[IsLabTechnician]

#List & Retrieve
class LabTestPrescriptionAPIView(APIView):
    # permission_classes=[IsLabTechnician]

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
    # permission_classes=[IsLabTechnician]

    def post(self, request):
        serializer = BulkLabTestPrescriptionSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Tests prescribed successfully"},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Create & View Lab Reports
class LabTestReportAPIView(APIView):
    # permission_classes=[IsLabTechnician]

    def get(self, request):
        reports = LabTestReport.objects.select_related(
            'prescription__appointment__patient',
            'prescription__test_type'
        ).all()

        serializer = LabTestReportSerializer(reports, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = LabTestReportSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(staff=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Generate Lab Bill
class LabTestBillAPIView(APIView):
    # permission_classes=[IsLabTechnician]

    def post(self, request):
        appointment_id = request.data.get("appointment")

        try:
            appointment = Appointment.objects.get(pk=appointment_id)
        except Appointment.DoesNotExist:
            return Response(
                {"error": "Appointment not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        bill, created = LabTestBill.objects.get_or_create(
            appointment=appointment
        )

        bill.save()  # Recalculate total

        serializer = LabTestBillSerializer(bill)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request):
        bills = LabTestBill.objects.select_related(
            'appointment__patient'
        ).all()

        serializer = LabTestBillSerializer(bills, many=True)
        return Response(serializer.data)