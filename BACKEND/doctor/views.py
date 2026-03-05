from django.shortcuts import render

"""
The following logic are inside the doctor views.py module 

  *) Create and list docttor availability 
  *) Update and delete availability 
  *) View doctor appointments 
  *) Prescribe medicines 
  *) Prescribe the lab test 
  *) Create consultation notes 
  *) Retrive and update the consulation notes 
"""

# Create your views here.

# Importing necessary modules for views 

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import DoctorAvailability
from .serializer import  (DoctorAvailSerializer,
                          MedicalPrescripSerailizer,
                          AppointmentSerializer,
                          LabTestPrescriptionSerializer,
                          ConsultNoteSerializer)

from reception.models import Appointment,PatientHistory
from pharmacist.models import MedicinePrescription
from labtechnician.models import LabTestPrescription 


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404


# ============================================================
#                  DOCTOR AVAILABILITY VIEW
# ============================================================

class DoctorAvailabilityView(APIView):
    """
    Handles creation and listing of doctor availability.
    """

    def get(self, request):
        """
        Retrieve all doctor availability records.
        """
        availability = DoctorAvailability.objects.all()
        serializer = DoctorAvailSerializer(availability, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Create doctor availability entry.
        """
        serializer = DoctorAvailSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================================================
#             DOCTOR AVAILABILITY UPDATE / DELETE
# ============================================================

class DoctorAvailabilityDetailView(APIView):
    """
    Update or delete doctor availability.
    """

    def put(self, request, pk):
        """
        Update doctor availability.
        """
        availability = get_object_or_404(DoctorAvailability, pk=pk)
        serializer = DoctorAvailSerializer(availability, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Delete doctor availability record.
        """
        availability = get_object_or_404(DoctorAvailability, pk=pk)
        availability.delete()
        return Response(
            {"message": "Availability deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )


# ============================================================
#                 DOCTOR APPOINTMENT VIEW
# ============================================================

class DoctorAppointmentView(APIView):
    """
    Retrieve appointments assigned to doctors.
    """

    def get(self, request):
        """
        List all appointments.
        """
        appointments = Appointment.objects.all()
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)


# ============================================================
#               MEDICAL PRESCRIPTION VIEW
# ============================================================

class MedicalPrescriptionView(APIView):
    """
    Doctors prescribe medicines to patients.
    """

    def post(self, request):
        """
        Create medical prescription.
        """
        serializer = MedicalPrescripSerailizer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================================================
#                LAB TEST PRESCRIPTION VIEW
# ============================================================

class LabTestPrescriptionView(APIView):
    """
    Doctors order lab tests for patients.
    """

    def post(self, request):
        """
        Create lab test prescription.
        """
        serializer = LabTestPrescriptionSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================================================
#               CONSULTATION NOTE VIEW
# ============================================================

class ConsultationNoteView(APIView):
    """
    Doctors add consultation notes after appointment completion.
    """

    def post(self, request):
        """
        Create consultation note.
        """
        serializer = ConsultNoteSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================================================
#          CONSULTATION NOTE UPDATE / RETRIEVE VIEW
# ============================================================

class ConsultationNoteDetailView(APIView):
    """
    Retrieve or update consultation notes.
    """

    def get(self, request, pk):
        """
        Retrieve consultation note.
        """
        note = get_object_or_404(PatientHistory, pk=pk)
        serializer = ConsultNoteSerializer(note)
        return Response(serializer.data)

    def put(self, request, pk):
        """
        Update consultation note.
        """
        note = get_object_or_404(PatientHistory, pk=pk)
        serializer = ConsultNoteSerializer(note, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)