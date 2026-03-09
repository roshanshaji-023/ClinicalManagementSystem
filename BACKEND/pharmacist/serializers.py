from rest_framework.decorators import api_view
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from .models import MedicineType
from .models import MedicineInventory
from .models import MedicinePurchaseHistory
from .models import MedicinePrescription
from .models import MedicineBill
from .serializers import MedicineTypeSerializer
from .serializers import MedicineInventorySerializer
from .serializers import MedicinePurchaseHistorySerializer
from .serializers import MedicinePrescriptionSerializer
from .serializers import MedicineBillSerializer
class MedicineTypeViewSet(viewsets.ModelViewSet):
    queryset = MedicineType.objects.all()
    serializer_class = MedicineTypeSerializer


class MedicineInventoryViewSet(viewsets.ModelViewSet):
    queryset = MedicineInventory.objects.all()
    serializer_class = MedicineInventorySerializer


class MedicinePurchaseHistoryViewSet(viewsets.ModelViewSet):
    queryset = MedicinePurchaseHistory.objects.all()
    serializer_class = MedicinePurchaseHistorySerializer


@api_view(['GET','POST'])
def prescription_list_create(request):
    try:
        if request.method == 'GET':
           prescriptions = MedicinePrescription.objects.all().order_by("-created_at")
           serializer = MedicinePrescriptionSerializer(prescriptions,many=True)
           return Response(serializer.data)

        if request.method == 'POST':
           serializer = MedicinePrescriptionSerializer(data=request.data)
           if serializer.is_valid():
              serializer.save()
              return Response(serializer.data,status=status.HTTP_201_CREATED)
           return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response(
            {"error":str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
@api_view(['GET','POST'])
def bill_list_create(request):
    try:
        if request.method =='GET':
            bill = MedicineBill.objects.all().order_by("-created_at")
            serializer = MedicineBillSerializer(bill,many=True)
            return Response(serializer.data)
        if request.method =='POST':
            serializer = MedicineBillSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,status=status.HTTP_201_CREATED)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(
            {"error":str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )