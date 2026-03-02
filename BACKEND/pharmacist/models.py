from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

from reception.models import Appointment
from administration.models import Staff,Doctor



class MedicineType(models.Model):
    medicine_Type_id = models.AutoField(primary_key=True)
    medicine_Type_name = models.CharField(max_length=30)

    def __str__(self):
        return self.medicine_Type_name


class MedicineInventory(models.Model):
    medicine = models.AutoField(primary_key=True)
    medicine_code = models.CharField(max_length=10, unique=True)
    company_name = models.CharField(max_length=10)
    medicine_name = models.CharField(max_length=30)
    medicine_Type = models.ForeignKey(MedicineType, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    price_per_unit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )

    total_quantity = models.IntegerField(
        validators=[MinValueValidator(0)]
    )

    def __str__(self):
        return self.medicine_name


class MedicinePurchaseHistory(models.Model):
    history_id = models.AutoField(primary_key=True)
    medicine = models.ForeignKey(MedicineInventory, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    quantity = models.IntegerField(
        validators=[MinValueValidator(1)]
    )

    purchase_data = models.DateField()
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.history_id)


class MedicinePrescription(models.Model):
    prescription_id = models.AutoField(primary_key=True)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    medicine = models.ForeignKey(MedicineInventory, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    frequency = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )

    quantity = models.IntegerField(
        validators=[MinValueValidator(1)]
    )

    dosage = models.CharField(max_length=50)

    period = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(365)]
    )

    def clean(self):
        if self.medicine and self.quantity:
            if self.quantity > self.medicine.total_quantity:
                raise ValidationError(
                    "Prescribed quantity cannot be more than available stock."
                )

    def __str__(self):
        return str(self.prescription_id)
