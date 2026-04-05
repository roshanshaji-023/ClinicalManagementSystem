from rest_framework import serializers
from django.utils import timezone
 

from .models import (
    Patient,
    Appointment,
    WaitingToken,
    PatientHistory,
    Billing
)


# -------------------- PATIENT --------------------

class PatientSerializer(serializers.ModelSerializer):

    #  Readable fields for frontend/demo
    full_name = serializers.SerializerMethodField(read_only=True)
    age = serializers.ReadOnlyField()

    class Meta:
        model = Patient
        fields = '__all__'
        read_only_fields = ['patient_id', 'patient_code', 'created_date', 'created_by']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    #  Field validations

    def validate_first_name(self, value):
        if not value.isalpha():
            raise serializers.ValidationError("First name must contain only letters")
        if len(value) < 2:
            raise serializers.ValidationError("First name must be at least 2 characters")
        return value

    def validate_last_name(self, value):
        if not value.isalpha():
            raise serializers.ValidationError("Last name must contain only letters")
        if len(value) < 2:
            raise serializers.ValidationError("Last name must be at least 2 characters")
        return value

    def validate_date_of_birth(self, value):
        if value > timezone.now().date():
            raise serializers.ValidationError("DOB cannot be in the future")
        return value


# -------------------- APPOINTMENT --------------------

class AppointmentSerializer(serializers.ModelSerializer):

    #  Readable fields
    patient_name = serializers.CharField(source='patient.first_name', read_only=True)
    doctor_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = ['appointment_id', 'created_at', 'created_by']

    def get_doctor_name(self, obj):
        return f"{obj.doctor.user.first_name} {obj.doctor.user.last_name}"

    def validate(self, data):

        appointment_date = data.get('appointment_date')
        appointment_time = data.get('appointment_time')
        doctor = data.get('doctor')
        patient = data.get('patient')
        visit_type = data.get('visit_type')
        parent = data.get('parent_appointment')
        status = data.get('status')
        cancellation_reason = data.get('cancellation_reason')

        # Date validation
        if appointment_date and appointment_date < timezone.localdate():
            raise serializers.ValidationError("Appointment date cannot be in the past")

        # Time validation
        if appointment_date == timezone.localdate():
            if appointment_time and appointment_time < timezone.localtime().time():
                raise serializers.ValidationError("Appointment time cannot be in the past")

        # Follow-up validation
        if visit_type == 'Follow-Up' and not parent:
            raise serializers.ValidationError("Follow-up requires parent appointment")

        # Same patient validation
        if parent and parent.patient != patient:
            raise serializers.ValidationError("Parent appointment must belong to same patient")

        # Cancellation validation
        if status == 'Cancelled' and not cancellation_reason:
            raise serializers.ValidationError("Cancellation reason required")

        # Double booking prevention
        if doctor and appointment_date and appointment_time:
            exists = Appointment.objects.filter(
                doctor=doctor,
                appointment_date=appointment_date,
                appointment_time=appointment_time
            ).exclude(pk=self.instance.pk if self.instance else None)

            if exists.exists():
                raise serializers.ValidationError("Doctor already booked for this slot")

        return data


# -------------------- TOKEN --------------------

class WaitingTokenSerializer(serializers.ModelSerializer):

    # Readable fields
    patient_name = serializers.CharField(source='appointment.patient.first_name', read_only=True)
    doctor_name = serializers.SerializerMethodField(read_only=True)
    is_emergency = serializers.BooleanField(source='appointment.is_emergency', read_only=True)

    class Meta:
        model = WaitingToken
        fields = '__all__'
        read_only_fields = ['token_id', 'doctor', 'token_number', 'issued_time']

    def get_doctor_name(self, obj):
        return f"{obj.doctor.user.first_name} {obj.doctor.user.last_name}"

    def validate(self, data):
        if not data.get('appointment'):
            raise serializers.ValidationError("Appointment is required")
        return data


# -------------------- PATIENT HISTORY --------------------

class PatientHistorySerializer(serializers.ModelSerializer):

    #  Readable fields
    patient_name = serializers.CharField(source='patient.first_name', read_only=True)
    appointment_date = serializers.DateField(source='appointment.appointment_date', read_only=True)

    class Meta:
        model = PatientHistory
        fields = '__all__'
        read_only_fields = ['history_id', 'created_at']

    def validate(self, data):

        appointment = data.get('appointment')
        patient = data.get('patient')

        if appointment.patient != patient:
            raise serializers.ValidationError("Appointment does not belong to patient")

        if appointment.status != 'Completed':
            raise serializers.ValidationError("History can only be created after completion")

        return data


# -------------------- BILLING --------------------

class BillingSerializer(serializers.ModelSerializer):

    patient_name = serializers.CharField(source='patient.first_name', read_only=True)
    doctor_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Billing
        fields = '__all__'
        read_only_fields = ['bill_id', 'created_at']

    def get_doctor_name(self, obj):
        return f"{obj.appointment.doctor.user.first_name} {obj.appointment.doctor.user.last_name}"

    def validate(self, data):

        appointment = data.get('appointment')
        consultation_fee = data.get('consultation_fee')
        payment_status = data.get('payment_status')
        payment_method = data.get('payment_method')

        #  Safe validation
        if consultation_fee is not None and consultation_fee <= 0:
            raise serializers.ValidationError("Consultation fee must be positive")

        #  Payment validation
        if payment_status == "Paid" and not payment_method:
            raise serializers.ValidationError("Payment method required if paid")

        if payment_status == "Pending" and payment_method:
            raise serializers.ValidationError("Payment method should not be set before payment")

        return data

    def create(self, validated_data):
        appointment = validated_data.get('appointment')
        validated_data['patient'] = appointment.patient
        return super().create(validated_data)
    


 


class BillingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Billing
        fields = '__all__'