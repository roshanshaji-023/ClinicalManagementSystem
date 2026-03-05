from django.contrib import admin
from .models import MedicineBill,MedicineInventory,MedicinePrescription,MedicinePurchaseHistory,MedicineType

# Register your models here.

admin.site.register(MedicineBill)
admin.site.register(MedicineInventory)
admin.site.register(MedicinePrescription)
admin.site.register(MedicinePurchaseHistory)
admin.site.register(MedicineType)