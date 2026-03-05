from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    PatientViewSet,
    AppointmentViewSet,
    WaitingTokenViewSet,
    PatientHistoryViewSet,
    BillingViewSet
)

router = DefaultRouter()

router.register(r'patients', PatientViewSet)
router.register(r'appointments', AppointmentViewSet)
router.register(r'tokens', WaitingTokenViewSet)
router.register(r'patient-history', PatientHistoryViewSet)
router.register(r'billing', BillingViewSet)

urlpatterns = [
    path('', include(router.urls)),
]