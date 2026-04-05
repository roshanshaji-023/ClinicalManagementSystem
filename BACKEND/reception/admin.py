from django.contrib import admin
from .models import Patient, Appointment, WaitingToken, PatientHistory, Billing


# -------------------- PATIENT --------------------

@admin.register(Patient)
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

    search_fields = [
        'patient_code',
        'first_name',
        'last_name',
        'phone_number'
    ]

    list_filter = ['created_date', 'is_active']

    ordering = ['-created_date']

    list_editable = ['is_active']  #  Quick activate/deactivate

    readonly_fields = ['patient_code', 'created_date', 'created_by']

    fieldsets = (
        ("Basic Info", {
            'fields': ('first_name', 'last_name', 'phone_number', 'date_of_birth', 'gender')
        }),
        ("Medical Info", {
            'fields': ('blood_group',)
        }),
        ("Contact Info", {
            'fields': ('email_id', 'address')
        }),
        ("System Info", {
            'fields': ('patient_code', 'is_active', 'staff', 'created_by', 'created_date')
        }),
    )


# -------------------- APPOINTMENT --------------------

@admin.register(Appointment)
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

    list_filter = ['doctor', 'status', 'visit_type', 'appointment_date']

    search_fields = [
        'patient__first_name',
        'patient__phone_number'
    ]

    ordering = ['-appointment_date', '-appointment_time']

    readonly_fields = ['created_at', 'created_by']

    fieldsets = (
        ("Appointment Info", {
            'fields': ('patient', 'doctor', 'visit_type', 'parent_appointment')
        }),
        ("Schedule", {
            'fields': ('appointment_date', 'appointment_time')
        }),
        ("Status", {
            'fields': ('status', 'is_emergency', 'cancellation_reason')
        }),
        ("System Info", {
            'fields': ('staff', 'created_by', 'created_at')
        }),
    )


# -------------------- WAITING TOKEN --------------------

@admin.register(WaitingToken)
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

    readonly_fields = ['doctor', 'token_number', 'issued_time']


# -------------------- PATIENT HISTORY --------------------

@admin.register(PatientHistory)
class PatientHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'history_id',
        'patient',
        'appointment',
        'created_at'
    ]

    search_fields = ['patient__first_name']

    ordering = ['-created_at']

    readonly_fields = ['created_at']


# -------------------- BILLING --------------------

@admin.register(Billing)
class BillingAdmin(admin.ModelAdmin):
    list_display = [
        'bill_id',
        'patient',
        'appointment',
        'consultation_fee',
        'total_amount',
        'payment_status',
        'staff',
        'paid_at',
        'created_at'
    ]

    list_filter = ['payment_status', 'created_at']

    search_fields = ['patient__first_name']

    ordering = ['-created_at']

    readonly_fields = [
        'total_amount',
        'paid_at',
        'created_at'
    ]

    fieldsets = (
        ("Bill Info", {
            'fields': ('appointment', 'patient')
        }),
        ("Charges", {
            'fields': ('consultation_fee', 'lab_cost', 'pharmacy_cost', 'discount')
        }),
        ("Total", {
            'fields': ('total_amount',)
        }),
        ("Payment", {
            'fields': ('payment_status', 'payment_method', 'paid_at')
        }),
        ("System Info", {
            'fields': ('staff', 'created_at')
        }),
    )