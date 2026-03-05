from django.shortcuts import render
from rest_framework import viewsets
from .models import MedicineType
from .models import MedicineInventory
from .models import MedicinePrescription
from .models import MedicinePurchaseHistory
from .models import MedicineBill
from .serializers import MedicineInventorySerializer
from .serializers import MedicineTypeSerializer
from .serializers import MedicinePurchaseHistorySerializer
from .serializers import MedicinePrescriptionSerializer
from .serializers import MedicineBillSerializer
class MedicineTypeviewset(viewsets.ModelViewSet):
    queryset = MedicineType.objects.all()
    serializer_class = MedicineTypeSerializer

class MedicineInventoryviewset(viewsets.ModelViewSet):
    queryset = MedicineInventory.objects.all()
    serializer_class = MedicineInventorySerializer

class MedicinePurchaseHistoryviewset(viewsets.ModelViewSet):
    queryset = MedicinePurchaseHistory.objects.all()
    serializer_class = MedicinePurchaseHistorySerializer

class MedicinePrescriptionviewset(viewsets.ModelViewSet):
    queryset = MedicinePrescription.objects.all()
    serializer_class = MedicinePrescriptionSerializer

class MedicineBillviewset(viewsets.ModelViewSet):
    queryset = MedicineBill.objects.all()
    serializer_class = MedicineBillSerializer
