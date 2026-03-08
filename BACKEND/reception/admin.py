from django.contrib import admin
from .models import Patient, Appointment, WaitingToken, PatientHistory, Billing


class PatientAdmin(admin.ModelAdmin):
    list_display = [
        'patient_id',
        'patient_code',
        'first_name',
        'last_name',
        'phone_number',
        'is_active',
        'staff',
        'created_date'
    ]
    search_fields = ['first_name', 'last_name', 'phone_number']
    list_filter = ['created_date']
    ordering = ['-created_date']


class AppointmentAdmin(admin.ModelAdmin):
    list_display = [
        'appointment_id',
        'patient',
        'doctor',
        'visit_type',
        'appointment_date',
        'appointment_time',
        'status'
    ]
    list_filter = ['doctor', 'status', 'appointment_date']
    search_fields = ['patient__first_name', 'patient__phone_number']
    ordering = ['-appointment_date']


class WaitingTokenAdmin(admin.ModelAdmin):
    list_display = [
        'token_id',
        'appointment',
        'doctor',
        'token_number',
        'token_date',
        'issued_time'
    ]
    list_filter = ['doctor', 'token_date']
    ordering = ['token_number']


class PatientHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'history_id',
        'patient',
        'appointment',
        'created_at'
    ]
    search_fields = ['patient__first_name']
    ordering = ['-created_at']


class BillingAdmin(admin.ModelAdmin):
    list_display = [
        'bill_id',
        'patient',
        'appointment',
        'consultation_fee',
        'payment_status',
        'staff',
        'created_at'
    ]
    list_filter = ['payment_status']
    search_fields = ['patient__first_name']
    ordering = ['-created_at']


admin.site.register(Patient, PatientAdmin)
admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(WaitingToken, WaitingTokenAdmin)
admin.site.register(PatientHistory, PatientHistoryAdmin)
admin.site.register(Billing, BillingAdmin)