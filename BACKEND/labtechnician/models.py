from django.db import models
from django.core.exceptions import ValidationError
from administration.models import Doctor,Staff
from reception.models import Appointment

# Create your models here.

class LabTestType(models.Model):
    Lab_test_id=models.AutoField(primary_key=True)
    Lab_test_name = models.CharField(max_length=255)
    Lab_test_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.Lab_test_name
    
#Lab-test-prescription
class LabTestPrescription(models.Model):
    lab_hist_id = models.AutoField(primary_key=True)
    appointment = models.ForeignKey(Appointment,on_delete=models.CASCADE,related_name='lab_tests')
    doctor= models.ForeignKey(Doctor,on_delete=models.CASCADE,related_name='lab_tests')
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Completed', 'Completed'),
        ]
    test_type = models.ForeignKey(LabTestType,on_delete=models.CASCADE,related_name='prescriptions')
    status =models.CharField(max_length=20,choices=STATUS_CHOICES,default='Pending')
    result = models.TextField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at']
        unique_together = ('appointment', 'test_type')  # prevents duplicate test for same appointment
    
    #model-level validation
    def clean(self):
        """
        Ensure doctor matches appointment doctor
        """
        if self.appointment.doctor != self.doctor_id:
            raise ValidationError(
                "Doctor must match the appointment doctor."
            )

    def __str__(self):
        return f"{self.appointment.patient} - {self.test_type.Lab_test_name} ({self.status})"
    
#lab-test-report
class LabTestReport(models.Model):
    report_id = models.AutoField(primary_key=True)
    prescription = models.OneToOneField(LabTestPrescription,on_delete=models.CASCADE,related_name='report')
    staff = models.ForeignKey(Staff,on_delete=models.SET_NULL,null=True,related_name='generated_reports')
    report_file = models.FileField(upload_to='lab_reports/', blank=True, null=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Auto mark prescription as completed
        self.prescription.status = 'Completed'
        self.prescription.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Report - {self.prescription}"

#lab-test-bill-generation

# Lab Test Bill
class LabTestBill(models.Model):
    bill_id = models.AutoField(primary_key=True)
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name='lab_bill'
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    generated_at = models.DateTimeField(auto_now_add=True)

    def calculate_total(self):
        prescriptions = LabTestPrescription.objects.filter(
            appointment=self.appointment
        )
        total = sum(p.test_type.Lab_test_amount for p in prescriptions)
        return total

    def save(self, *args, **kwargs):
        self.total_amount = self.calculate_total()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Bill - {self.appointment.patient}"
