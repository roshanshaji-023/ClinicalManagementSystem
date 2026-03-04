# importing the libraries and modules necessary for doctor module

from rest_framework import serializers
from django.utils import timezone
from administration.models import Doctor, Staff
from reception.models import Appointment, Patient, PatientHistory
from pharmacist.models import MedicineInventory, MedicinePrescription
from labtechnician.models import LabTest, LabTestPrescription
from .models import DoctorAvailability


# =====================================================================
#                      DOCTOR AVAILABILITY SERIALIZER
# =====================================================================

class DoctorAvailSerializer(serializers.ModelSerializer):
    """
    Serializer for handling doctor availability.
    
    Performs:
    - field-level validations for availability date & status
    - object-level validation to prevent duplicate availability entries
    """

    class Meta:
        model = DoctorAvailability
        fields = "__all__"

    def validate_available_date(self, value):
        """
        Validate that availability date is not in the past.
        """
        if value < timezone.now().date():
            raise serializers.ValidationError("Doctor availability cannot be in the past.")
        return value

    def validate_available_status(self, value):
        """
        Validate the doctor's availability status.
        Ensures the value matches the allowed enum.
        """
        allowed = ['Fullday', 'Morningonly', 'Afternoononly', 'onleave']
        if value not in allowed:
            raise serializers.ValidationError("Invalid availability status.")
        return value

    def validate(self, data):
        """
        Object-level validation.
        Prevents multiple entries for the same doctor on the same date.
        """
        doctor = data.get("doctor")
        date = data.get("available_date")

        if DoctorAvailability.objects.filter(doctor=doctor, available_date=date).exists():
            raise serializers.ValidationError(
                f"Availability for this doctor on {date} already exists."
            )

        return data



# =====================================================================
#                   MEDICAL PRESCRIPTION SERIALIZER
# =====================================================================

class MedicalPrescripSerailizer(serializers.ModelSerializer):
    """
    Serializer for medical prescription functionality.

    Handles:
    - field-level validations (quantity, period, frequency)
    - object-level validation for doctor ownership, stock, appointment status
    """

    class Meta:
        model = MedicinePrescription
        fields = "__all__"

    def validate_quantity(self, value):
        """
        Quantity must be greater than zero.
        """
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return value

    def validate_period(self, value):
        """
        Period must be a positive number of days.
        """
        if value <= 0:
            raise serializers.ValidationError("Period must be positive.")
        return value

    def validate_frequency(self, value):
        """
        Validate consumption frequency pattern.
        """
        allowed = ["1-1-1", "1-0-1", "1-0-0", "0-1-1", "0-0-1", "0-1-0"]
        if value not in allowed:
            raise serializers.ValidationError("Invalid frequency format.")
        return value

    def validate(self, data):
        """
        Object-level validation for prescription:
        - The appointment must belong to the selected doctor
        - Quantity must not exceed available stock
        - Appointment status must allow prescribing
        """
        appointment = data["appointment"]
        medicine = data["medicine"]
        quantity = data["quantity"]
        doctor = data["doctor"]

        if appointment.doctor_id != doctor.doctor_id:
            raise serializers.ValidationError("Appointment belongs to another doctor.")

        if quantity > medicine.total_quantity:
            raise serializers.ValidationError(
                f"Only {medicine.total_quantity} units available in stock."
            )

        if appointment.status in ["Completed", "Cancelled", "No Show"]:
            raise serializers.ValidationError(
                "Cannot prescribe medicine for completed or cancelled appointments."
            )

        return data



# =====================================================================
#                    APPOINTMENT SERIALIZER (LIST/VIEW)
# =====================================================================

class AppointmentSerializer(serializers.ModelSerializer):
    """
    Serializer for listing appointments for the doctor module.
    Includes computed patient name field.
    """

    patient_name = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = [
            "appointment_id",
            "appointment_date",
            "appointment_time",
            "status",
            "patient_name",
            "visit_type"
        ]

    def get_patient_name(self, obj):
        """
        Returns patient full name for display.
        """
        return f"{obj.patient.first_name} {obj.patient.last_name}"



# =====================================================================
#                CONSULTATION NOTE SERIALIZER
# =====================================================================

class ConsultNoteSerializer(serializers.ModelSerializer):
    """
    Serializer for adding or updating consultation notes post-visit.
    
    Performs:
    - field-level validation on note length
    - object-level validation checking appointment-patient match
    - ensures notes can be added only after appointment completion
    """

    class Meta:
        model = PatientHistory
        fields = ["patient", "appointment", "consultation_note"]

    def validate_consultation_note(self, value):
        """
        Validate that consultation notes contain enough meaningful text.
        """
        if len(value.strip()) < 5:
            raise serializers.ValidationError(
                "Consultation note must have at least 5 characters."
            )
        return value

    def validate(self, data):
        """
        Object-level validation ensuring:
        - Appointment belongs to selected patient
        - Notes can only be added for completed appointments
        """
        appointment = data["appointment"]
        patient = data["patient"]

        if appointment.patient_id != patient.patient_id:
            raise serializers.ValidationError("Appointment does not belong to this patient.")

        if appointment.status != "Completed":
            raise serializers.ValidationError(
                "Notes can be added only after appointment completion."
            )

        return data