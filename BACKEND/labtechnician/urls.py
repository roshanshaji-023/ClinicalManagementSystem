from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import LabTestTypeViewSet,LabTestPrescriptionAPIView, BulkLabTestPrescriptionAPIView

router = DefaultRouter()
router.register(r'lab-test-types', LabTestTypeViewSet)

urlpatterns = [
    path('lab-tests/', LabTestPrescriptionAPIView.as_view()),
    path('prescribe-tests/', BulkLabTestPrescriptionAPIView.as_view()),
]

#Add router URLs instead of replacing
urlpatterns += router.urls
