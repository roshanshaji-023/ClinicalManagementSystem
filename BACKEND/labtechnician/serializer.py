from rest_framework import serializers
from .models import LabTestType,LabTestPrescription
from reception.models import Appointment
from administration.models import Doctor

class LabTestTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = LabTestType
        fields = ['Lab_test_id', 'Lab_test_name', 'Lab_test_amount']
        read_only_fields = ['Lab_test_id']

     # Field-level validation
    def validate_test_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError(
                "Test type name must be at least 3 characters long."
            )
        return value

    def validate_test_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Test amount must be greater than 0."
            )
        return value

#LabTestPrescription GET Serializer
class LabTestPrescriptionSerializer(serializers.ModelSerializer):

    doctor_name = serializers.CharField(source='doctor.user_name',read_only=True)
    patient_name = serializers.SerializerMethodField()
    test_name = serializers.CharField(source='test_type.Lab_test_name',read_only=True)

    class Meta:
        model = LabTestPrescription
        fields = ['lab_hist_id','appointment','patient_name','doctor','doctor_name','test_type','test_name','status','result','created_at']

    def get_patient_name(self, obj):
        return f"{obj.appointment.patient.first_name} {obj.appointment.patient.last_name}"


#Bulk Prescription Serializer (POST multiple tests)
class BulkLabTestPrescriptionSerializer(serializers.Serializer):

    appointment = serializers.PrimaryKeyRelatedField(
        queryset=Appointment.objects.all()
    )

    doctor = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.all()
    )

    tests = serializers.PrimaryKeyRelatedField(
        queryset=LabTestType.objects.all(),
        many=True
    )

    def validate(self, data):
        if data['appointment'].doctor != data['doctor']:
            raise serializers.ValidationError(
                "Doctor does not match appointment doctor."
            )
        return data

    def create(self, validated_data):
        appointment = validated_data['appointment']
        doctor = validated_data['doctor']
        tests = validated_data['tests']

        prescriptions = [
            LabTestPrescription(
                appointment=appointment,
                doctor=doctor,
                test_type=test,
                status='Pending'
            )
            for test in tests
        ]

        LabTestPrescription.objects.bulk_create(prescriptions)

        return prescriptions
