from django.contrib import admin
from .models import LabTestType,LabTestPrescription

# Register your models here.


admin.site.register(LabTestType)
admin.site.register(LabTestPrescription)