from django.contrib import admin
from .models import LabTestType,LabTestPrescription,LabTestReport,LabTestBill

# Register your models here.


admin.site.register(LabTestType)
admin.site.register(LabTestPrescription)
admin.site.register(LabTestReport)
admin.site.register(LabTestBill)