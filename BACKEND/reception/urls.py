from django.urls import path
from .views import (
    RegisterPatient,
    SearchPatient,
    CreateAppointment,
    AppointmentByDate,
    WalkIn,
    DoctorQueue,
    CompleteConsultation,
    PatientHistoryView,
    CreateBill,
    GetBill,
    PayBill,
)

urlpatterns = [

    # -------------------- PATIENT --------------------
    path('patients/', RegisterPatient.as_view(), name='register-patient'),
    path('patients/search/', SearchPatient.as_view(), name='search-patient'),


    # -------------------- APPOINTMENT --------------------
    path('appointments/', CreateAppointment.as_view(), name='create-appointment'),
    path('appointments/by-date/', AppointmentByDate.as_view(), name='appointments-by-date'),


    # -------------------- TOKEN --------------------
    # path('tokens/', GenerateToken.as_view(), name='generate-token'),


    # -------------------- WALK-IN --------------------
    path('walkin/', WalkIn.as_view(), name='walkin'),


    # -------------------- DOCTOR --------------------
    path('doctor/queue/', DoctorQueue.as_view(), name='doctor-queue'),
    path('doctor/complete/', CompleteConsultation.as_view(), name='complete-consultation'),
    path('doctor/history/<int:patient_id>/', PatientHistoryView.as_view(), name='patient-history'),


    # -------------------- BILLING --------------------
    path('billing/create/', CreateBill.as_view(), name='create-bill'),
    path('billing/<int:appointment_id>/', GetBill.as_view(), name='get-bill'),
    path('billing/pay/', PayBill.as_view(), name='pay-bill'),
]