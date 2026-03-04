from django.shortcuts import render
from rest_framework import viewsets
from .models import MedicineType
from .models import MedicineInventory
from .models import MedicinePrescription
from .models import MedicinePurchaseHistory
from .serializers import MedicineInventorySerializer
from .serializers import MedicineTypeSerializer
from .serializers import MedicinePurchaseHistorySerializer
from .serializers import 