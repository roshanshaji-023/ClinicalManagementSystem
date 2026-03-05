from django.urls import path
from .views import (
    DoctorAvailabilityView,
    DoctorAvailabilityDetailView,
    DoctorAppointmentView,
    MedicalPrescriptionView,
    LabTestPrescriptionView,
    ConsultationNoteView,
    ConsultationNoteDetailView
)

urlpatterns = [

    # Doctor availability
    path('availability/', DoctorAvailabilityView.as_view(), name='doctor-availability'),
    path('availability/<int:pk>/', DoctorAvailabilityDetailView.as_view(), name='doctor-availability-detail'),

    # Appointments
    path('appointments/', DoctorAppointmentView.as_view(), name='doctor-appointments'),

    # Medicine prescription
    path('prescription/', MedicalPrescriptionView.as_view(), name='medical-prescription'),

    # Lab test prescription
    path('labtest/', LabTestPrescriptionView.as_view(), name='labtest-prescription'),

    # Consultation notes
    path('consultation/', ConsultationNoteView.as_view(), name='consultation-note'),
    path('consultation/<int:pk>/', ConsultationNoteDetailView.as_view(), name='consultation-note-detail'),

]