from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from django.db import transaction

from .models import Patient, Appointment, WaitingToken, PatientHistory, Billing
from .serializers import (
    PatientSerializer,
    AppointmentSerializer,
    WaitingTokenSerializer,
    PatientHistorySerializer,
    BillingSerializer
)


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all().order_by('-created_date')
    serializer_class = PatientSerializer
    filter_backends = [SearchFilter]
    search_fields = ['first_name', 'phone_number']


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

    @transaction.atomic
    def perform_create(self, serializer):
        appointment = serializer.save()
        WaitingToken.objects.create(appointment=appointment)


class WaitingTokenViewSet(viewsets.ModelViewSet):
    queryset = WaitingToken.objects.all().order_by('token_number')
    serializer_class = WaitingTokenSerializer


class PatientHistoryViewSet(viewsets.ModelViewSet):
    queryset = PatientHistory.objects.all().order_by('-created_at')
    serializer_class = PatientHistorySerializer


class BillingViewSet(viewsets.ModelViewSet):
    queryset = Billing.objects.all()
    serializer_class = BillingSerializer

    def perform_create(self, serializer):
        appointment = serializer.validated_data['appointment']
        serializer.save(patient=appointment.patient)