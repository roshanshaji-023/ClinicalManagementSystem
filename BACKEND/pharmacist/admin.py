from django.contrib import admin
from .models import MedicineInventory,MedicinePurchaseHistory,MedicineType

# Register your models here.
admin.site.register(MedicineInventory)
admin.site.register(MedicinePurchaseHistory)
admin.site.register(MedicineType)
