from rest_framework import serializers
from django.utils import timezone
from .models import Patient, Appointment, WaitingToken, PatientHistory, Billing
# from pharmacist.models import PharmacyBill



class PatientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Patient
        fields = '__all__'
        read_only_fields = ['patient_id', 'patient_code', 'created_date' , 'staff']

    
        
    def validate_date_of_birth(self, value):
        if value > timezone.now().date():
            raise serializers.ValidationError(
            "Date of birth cannot be in the future."
        )
        return value
    

class AppointmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = ['appointment_id', 'created_at']

    def validate(self, data):

        appointment_date = data.get('appointment_date',getattr(self.instance, 'appointment_date', None))
        visit_type = data.get(
            'visit_type',
            getattr(self.instance, 'visit_type', None)
       )

        parent_appointment = data.get(
             'parent_appointment',
            getattr(self.instance, 'parent_appointment', None)
        )

        status = data.get(
             'status',
             getattr(self.instance, 'status', None)
        )

        # Prevent past appointment
        if appointment_date and appointment_date < timezone.now().date():
            raise serializers.ValidationError(
                "Appointment date cannot be in the past"
            )

        # Follow-up validation
        if visit_type == "Follow-Up" and not parent_appointment:
            raise serializers.ValidationError(
                "Follow-up appointment must have parent appointment"
            )

        # Appointment workflow validation 
        if (
            status == "Completed"
            and visit_type == "New"
            and getattr(self.instance, 'status', None) != "In Consultation"
        ):
            raise serializers.ValidationError(
                "New appointment cannot be marked completed immediately."
           )
        return data
    
class WaitingTokenSerializer(serializers.ModelSerializer):

    class Meta:
        model = WaitingToken
        fields = '__all__'
        read_only_fields = ['token_id','token_number','doctor', 'issued_time']

class PatientHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = PatientHistory
        fields = '__all__'
        read_only_fields = ['history_id', 'created_at']




class BillingSerializer(serializers.ModelSerializer):

    total_bill = serializers.SerializerMethodField()

    class Meta:
        model = Billing
        fields = '__all__'
        read_only_fields = ['bill_id', 'created_at', 'patient' , 'staff']

    def get_total_bill(self, obj):

        consultation = obj.consultation_fee or 0

        lab_total = 0
        lab_bill = getattr(obj.appointment, 'lab_bill', None)
        if lab_bill:
            lab_total = lab_bill.total_amount

        pharmacy_total = 0

        return consultation + lab_total + pharmacy_total

    def validate_consultation_fee(self, value):

        if value < 0:
            raise serializers.ValidationError(
                "Consultation fee cannot be negative"
            )

        return value

    def validate(self, data):

        appointment = data.get('appointment')
        patient = data.get('patient')

        if appointment and patient and appointment.patient != patient:
            raise serializers.ValidationError(
                "Appointment does not belong to this patient."
            )

        return data

    #  CUSTOM CREATE
    def create(self, validated_data):

        appointment = validated_data.get('appointment')

        validated_data['patient'] = appointment.patient

        return super().create(validated_data)

    #  CUSTOM UPDATE
    def update(self, instance, validated_data):

        appointment = validated_data.get('appointment', instance.appointment)

        validated_data['patient'] = appointment.patient

        return super().update(instance, validated_data)
class AppointmentNestedSerializer(serializers.ModelSerializer):

    class Meta:
        model = Appointment
        fields = ['appointment_id', 'appointment_date', 'status']


class PatientDetailSerializer(serializers.ModelSerializer):

    appointments = AppointmentNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Patient
        fields = '__all__'