from rest_framework import serializers
from .models import (
    MedicineType,
    MedicineInventory,
    MedicinePurchaseHistory,
    MedicinePrescription,
    MedicineBill
)

class MedicineTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = MedicineType
        fields = "__all__"
        read_only_fields = ["medicine_type_id"]

    def validate_medicine_type_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError(
                "Medicine type name must be at least 3 characters long."
            )
        return value


class MedicineInventorySerializer(serializers.ModelSerializer):

    class Meta:
        model = MedicineInventory
        fields = "__all__"
        read_only_fields = ["medicine_id", "created_at", "updated_at"]

    def validate_medicine_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError(
                "Medicine name must contain at least 3 characters."
            )
        return value

    def validate_price_per_unit(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Price must be greater than 0."
            )
        return value




class MedicinePurchaseHistorySerializer(serializers.ModelSerializer):

    medicine_name = serializers.ReadOnlyField(
        source="medicine.medicine_name"
    )

    class Meta:
        model = MedicinePurchaseHistory
        fields = "__all__"
        read_only_fields = ["history_id", "created_at", "updated_at"]

    def create(self, validated_data):

        purchase = MedicinePurchaseHistory.objects.create(**validated_data)

        medicine = purchase.medicine
        medicine.total_quantity += purchase.quantity
        medicine.save()

        return purchase


class MedicinePrescriptionSerializer(serializers.ModelSerializer):

    medicine_name = serializers.ReadOnlyField(
        source="medicine.medicine_name"
    )

    doctor_name = serializers.ReadOnlyField(
        source="doctor.name"
    )

    class Meta:
        model = MedicinePrescription
        fields = "__all__"
        read_only_fields = ["prescription_id", "created_at", "updated_at"]

    def validate(self, data):

        medicine = data.get("medicine")
        quantity = data.get("quantity")

        if medicine and quantity:
            if quantity > medicine.total_quantity:
                raise serializers.ValidationError(
                    "Prescribed quantity cannot exceed available stock."
                )

        return data

    def create(self, validated_data):

        prescription = MedicinePrescription.objects.create(**validated_data)

        medicine = prescription.medicine
        medicine.total_quantity -= prescription.quantity
        medicine.save()

        return prescription


class PrescriptionNestedSerializer(serializers.ModelSerializer):

    medicine_name = serializers.ReadOnlyField(
        source="medicine.medicine_name"
    )

    class Meta:
        model = MedicinePrescription
        fields = ["prescription_id", "medicine", "medicine_name", "quantity", "dosage"]


class MedicineBillSerializer(serializers.ModelSerializer):

    prescriptions = PrescriptionNestedSerializer(many=True)

    class Meta:
        model = MedicineBill
        fields = "__all__"
        read_only_fields = ["bill_id", "billing_date"]

    def validate(self, data):

        total = data.get("total_amount")
        paid = data.get("paid_amount")

        if paid > total:
            raise serializers.ValidationError(
                "Paid amount cannot exceed total amount."
            )

        return data

    def create(self, validated_data):

        prescriptions_data = validated_data.pop("prescriptions")

        bill = MedicineBill.objects.create(**validated_data)

        for prescription_data in prescriptions_data:
            prescription = MedicinePrescription.objects.get(
                prescription_id=prescription_data["prescription_id"]
            )
            bill.prescriptions.add(prescription)

        return bill