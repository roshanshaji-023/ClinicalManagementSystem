from django.urls import path
from .views import (
    RegisterPatient,
    SearchPatient,
    UpdatePatient,
    DeletePatient,
    DoctorAvailability,
    PatientProfile,
    CreateAppointment,
    AppointmentByDate,
    CancelAppointment,
    RescheduleAppointment,
    SearchAppointments,
    ReceptionDashboard,
    WalkIn,
    DoctorQueue,
    CompleteConsultation,
    PatientHistoryView,
    CreateBill,
    GetBill,
    PayBill,
    CreateFollowUp,
    GenerateBillPDF,
    AppointmentDetail,
    PatientAppointments,
    MarkNoShow,   
)

urlpatterns = [

    # -------------------- PATIENT --------------------
    path('patients/', RegisterPatient.as_view(), name='register-patient'),
    path('patients/search/', SearchPatient.as_view(), name='search-patient'),
    path('patients/<int:patient_id>/update/', UpdatePatient.as_view()),
    path('patients/<int:patient_id>/delete/', DeletePatient.as_view()),
    path('doctor/availability/', DoctorAvailability.as_view()),
    path('patients/<int:patient_id>/', PatientProfile.as_view()),
    


    # -------------------- APPOINTMENT --------------------
    path('appointments/', CreateAppointment.as_view(), name='create-appointment'),
    path('appointments/by-date/', AppointmentByDate.as_view(), name='appointments-by-date'),

    path('appointment/<int:appointment_id>/', AppointmentDetail.as_view(), name='appointment-detail'),  
    path('appointment/cancel/', CancelAppointment.as_view(), name='cancel-appointment'),  
    path('appointment/no-show/', MarkNoShow.as_view(), name='mark-no-show'),  

    path('appointment/reschedule/', RescheduleAppointment.as_view()),
    path('appointments/search/', SearchAppointments.as_view()),


    # -------------------- FOLLOW-UP --------------------
    path('followup/create/', CreateFollowUp.as_view()),
    path('appointments/patient/<int:patient_id>/', PatientAppointments.as_view()),


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
    path('billing/pdf/<int:bill_id>/', GenerateBillPDF.as_view()),


    # -------------------- DASHBOARD --------------------
    path('dashboard/', ReceptionDashboard.as_view()),
]