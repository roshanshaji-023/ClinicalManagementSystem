from django.db import models

# Create your models here.

class LabTestType(models.Model):
    Lab_test_id=models.AutoField(primary_key=True)
    Lab_test_name = models.CharField(max_length=255)
    Lab_test_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.Lab_test_name

