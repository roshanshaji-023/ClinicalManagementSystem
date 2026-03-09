from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MedicineTypeViewSet
from .views import MedicineInventoryViewSet
from .views import MedicinePurchaseHistoryViewSet
from .views import prescription_list_create
from .views import bill_list_create

router = DefaultRouter()
router.register("medicine_types", MedicineTypeViewSet)
router.register("medicine", MedicineInventoryViewSet)
router.register("purchase_history", MedicinePurchaseHistoryViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("prescriptions/", prescription_list_create),
    path("bill/", bill_list_create, name="bill_list_create"),
]