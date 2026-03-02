from rest_framework import serializers
from .models import MedicineType
from .models import MedicineInventory
from .models import MedicinePurchaseHistory
from .models import MedicinePrescription
from django.db import transaction
from django.core.exceptions import ValidationError
from doctor.models import Doctor
from reception.models import Appointment
from administration.models import Staff

class MedicineTypeSerializer(serializers.ModelSerializer):
    medicine_Type_name = serializers.CharField(required=True)
    class Meta:
        model = MedicineType
        fields ="__all__"
        def validate_medicine_Type_name(self,value):
            if len(value)>2:
                raise serializers.ValidationError("medicine type name will be ateast 2 char")
            return value



class MedicineInventorySerializer(serializers.ModelSerializer):
    
    medicine_Type = serializers.PrimaryKeyRelatedField(
        queryset = MedicineType.objects.all()
    )

    medicine_Type_name = serializers.CharField(
        source="medicine_Type.medicine_Type_name",
        read_only=True
    )
    class Meta:
        model = MedicineInventory
        fields = [
                    "medicine_id",
                    "medicine_code",
                    "company_name",
                    "medicine_name",
                    "medicine_Type",
                    "medicine_Type_name",
                    "price_per_unit",
                    "total_quantity",
                    "created_at",
                    "updated_at"
                ]
        read_only_fields = ("created_at", "updated_at")
        def validate_medicine_code(self,value):
            if len(value)>3:
                raise serializers.ValidationError("medicine code must be at least 3 characters.")
            return value
        def validate_total_quantity(self,value):
            if value<0:
                raise serializers.ValidationError("The total quantity cannot be negative")
            return value

class MedicinePurchaseHistorySerializer(serializers.ModelSerializer):
    medicine=serializers.PrimaryKeyRelatedField(
        queryset = MedicineInventory.objects.all()
    )

    medicine_name = serializers.CharField(
        source="medicine.medicine_name",
        read_only=True
    )
    prescription_id = serializers.PrimaryKeyRelatedField(
        queryset = MedicinePrescription.objects.all()
    )
    prescription_id = serializers.IntegerField(
        source="prescription_id.prescription_id",
        read_only=True
    )
    class Meta:
        model = MedicinePurchaseHistory
        fields = [
            "history_id",
            "medicine",
            "medicine_name",
            "quantity",
            "purchase_data",
            "created_at",
            "updated_at"
        ]
        read_only_fields = ("history_id", "created_at", "updated_at")
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Purchase quantity must be greater than zero."
            )
        return value
    def validate(self, data):
        medicine = data.get("medicine")
        quantity = data.get("quantity")
        if quantity > medicine.total_quantity:
            raise serializers.ValidationError(
                "quantity is more than available stock"
            )
        return data
    @transaction.atomic
    def create(self,validated_data):
        medicine = validated_data["medicine"]
        quantity = validated_data["quantity"]
        medicine.total_quantity -= quantity
        medicine.save()
        prescription = MedicinePrescription.objects.create(validated_data)
        return prescription
