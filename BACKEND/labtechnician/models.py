from django.db import models
from django.core.exceptions import ValidationError
from administration.models import Doctor
from reception.models import Appointment

# Create your models here.

class LabTestType(models.Model):
    Lab_test_id=models.AutoField(primary_key=True)
    Lab_test_name = models.CharField(max_length=255)
    Lab_test_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.Lab_test_name
    

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