from rest_framework import serializers
from django.db import transaction
from django.core.exceptions import ValidationError

from .models import (
    MedicineType,
    MedicineInventory,
    MedicinePurchaseHistory,
    MedicinePrescription
)

from administration.models import Staff, Doctor
from reception.models import Appointment
class MedicineTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicineType
        fields = "__all__"
class MedicineInventorySerializer(serializers.ModelSerializer):
    medicine_Type_name = serializers.CharField(
        source="medicine_Type.medicine_Type_name",
        read_only=True
    )

    class Meta:
        model = MedicineInventory
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")
class MedicinePurchaseHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = MedicinePurchaseHistory
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Purchase quantity must be greater than zero."
            )
        return value
    
class MedicinePurchaseHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = MedicinePurchaseHistory
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Purchase quantity must be greater than zero."
            )
        return value
    
class MedicinePrescriptionSerializer(serializers.ModelSerializer):

    medicine_details = MedicineInventoryNestedSerializer(
        source="medicine",
        read_only=True
    )

    class Meta:
        model = MedicinePrescription
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


    def validate(self, data):
        medicine = data.get("medicine")
        quantity = data.get("quantity")

        if medicine and quantity:
            if quantity > medicine.total_quantity:
                raise serializers.ValidationError({
                    "quantity": "Prescribed quantity exceeds available stock."
                })
        return data
    
    @transaction.atomic
    def create(self, validated_data):
        medicine = validated_data["medicine"]
        quantity = validated_data["quantity"]

        # Reduce stock
        medicine.total_quantity -= quantity
        medicine.save()

        prescription = super().create(validated_data)
        return prescription
    
    @transaction.atomic
    def update(self, instance, validated_data):
        old_quantity = instance.quantity
        new_quantity = validated_data.get("quantity", old_quantity)
        medicine = instance.medicine

        difference = new_quantity - old_quantity

        if difference > 0 and difference > medicine.total_quantity:
            raise serializers.ValidationError({
                "quantity": "Not enough stock available for update."
            })

        medicine.total_quantity -= difference
        medicine.save()

        return super().update(instance, validated_data)