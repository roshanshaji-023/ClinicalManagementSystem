from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

from administration.models import Doctor, Staff
from reception.models import Appointment


class MedicineType(models.Model):
    medicine_type_id = models.AutoField(primary_key=True)
    medicine_type_name = models.CharField(max_length=30)

    def __str__(self):
        return self.medicine_type_name


class MedicineInventory(models.Model):
    medicine_id = models.AutoField(primary_key=True)

    medicine_code = models.CharField(max_length=10, unique=True)
    company_name = models.CharField(max_length=100)
    medicine_name = models.CharField(max_length=30)

    medicine_type = models.ForeignKey(
        MedicineType,
        on_delete=models.CASCADE,
        related_name="medicines"
    )

    price_per_unit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )

    total_quantity = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.medicine_name} ({self.company_name})"


class MedicinePurchaseHistory(models.Model):
    history_id = models.AutoField(primary_key=True)

    medicine = models.ForeignKey(
        MedicineInventory,
        on_delete=models.CASCADE,
        related_name="purchase_history"
    )

    quantity = models.PositiveIntegerField()

    purchase_date = models.DateField()

    staff = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE,
        related_name="medicine_purchases"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Purchase #{self.history_id} - {self.medicine.medicine_name}"


class MedicinePrescription(models.Model):
    prescription_id = models.AutoField(primary_key=True)

    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name="medicine_prescriptions"
    )

    medicine = models.ForeignKey(
        MedicineInventory,
        on_delete=models.CASCADE,
        related_name="prescriptions"
    )

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name="prescriptions"
    )

    frequency = models.PositiveIntegerField(
        validators=[MaxValueValidator(10)]
    )

    quantity = models.PositiveIntegerField()

    dosage = models.CharField(max_length=50)

    period = models.PositiveIntegerField(
        validators=[MaxValueValidator(365)]
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.medicine and self.quantity:
            if self.quantity > self.medicine.total_quantity:
                raise ValidationError(
                    "Prescribed quantity cannot be more than available stock."
                )

    def __str__(self):
        return f"Prescription #{self.prescription_id}"


class MedicineBill(models.Model):
    bill_id = models.AutoField(primary_key=True)

    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name="medicine_bills"
    )

    prescriptions = models.ManyToManyField(
        MedicinePrescription,
        related_name="bills"
    )

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    paid_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    payment_status = models.CharField(
        max_length=20,
        choices=[
            ("PENDING", "Pending"),
            ("PAID", "Paid"),
            ("PARTIAL", "Partial")
        ],
        default="PENDING"
    )

    billed_by = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE,
        related_name="medicine_bills"
    )

    billing_date = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.paid_amount > self.total_amount:
            raise ValidationError(
                "Paid amount cannot be greater than total bill amount."
            )

    def __str__(self):
        return f"Bill #{self.bill_id} - {self.payment_status}"
