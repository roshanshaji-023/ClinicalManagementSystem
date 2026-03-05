from rest_framework import serializers
from django.db import transaction

from .models import (
    MedicineType,
    MedicineInventory,
    MedicinePurchaseHistory,
    MedicinePrescription,
    MedicineBill
)

from administration.models import Doctor, Staff
from reception.models import Appointment


class MedicineTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = MedicineType
        fields = "__all__"

    def validate_medicine_Type_name(self, value):
        if len(value) < 2:
            raise serializers.ValidationError(
                "Medicine type name must be at least 2 characters."
            )
        return value


class MedicineInventorySerializer(serializers.ModelSerializer):

    medicine_Type_id = serializers.PrimaryKeyRelatedField(
        queryset=MedicineType.objects.all()
    )

    medicine_Type_name = serializers.CharField(
        source="medicine_Type_id.medicine_Type_name",
        read_only=True
    )

    class Meta:
        model = MedicineInventory
        fields = [
            "medicine_id",
            "medicine_code",
            "company_name",
            "medicine_name",
            "medicine_Type_id",
            "medicine_Type_name",
            "price_per_unit",
            "total_quantity",
            "created_at",
            "updated_at"
        ]

        read_only_fields = ("created_at", "updated_at")

    def validate_medicine_code(self, value):
        if len(value) < 3:
            raise serializers.ValidationError(
                "Medicine code must be at least 3 characters."
            )
        return value

    def validate_total_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Total quantity cannot be negative."
            )
        return value


class MedicinePurchaseHistorySerializer(serializers.ModelSerializer):

    medicine_id = serializers.PrimaryKeyRelatedField(
        queryset=MedicineInventory.objects.all()
    )

    medicine_name = serializers.CharField(
        source="medicine_id.medicine_name",
        read_only=True
    )

    staff_id = serializers.PrimaryKeyRelatedField(
        queryset=Staff.objects.all()
    )

    class Meta:
        model = MedicinePurchaseHistory
        fields = [
            "history_id",
            "medicine_id",
            "medicine_name",
            "quantity",
            "purchase_date",
            "staff_id",
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

    @transaction.atomic
    def create(self, validated_data):

        medicine = validated_data["medicine_id"]
        quantity = validated_data["quantity"]

        # Increase stock
        medicine.total_quantity += quantity
        medicine.save()

        return MedicinePurchaseHistory.objects.create(**validated_data)


class MedicinePrescriptionSerializer(serializers.ModelSerializer):

    appointment = serializers.PrimaryKeyRelatedField(
        queryset=Appointment.objects.all()
    )

    class Meta:
        model = MedicinePrescription
        fields = "__all__"


class MedicineBillSerializer(serializers.ModelSerializer):

    class Meta:
        model = MedicineBill
        fields = "__all__"