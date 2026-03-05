from django.contrib import admin
from .models import Patient, Appointment, WaitingToken, PatientHistory, Billing


class PatientAdmin(admin.ModelAdmin):
    list_display = [
        'patient_id',
        'patient_code',
        'first_name',
        'phone_number',
        'created_date'
    ]
    search_fields = ['first_name', 'phone_number']
    list_filter = ['created_date']


admin.site.register(Patient, PatientAdmin)
admin.site.register(Appointment)
admin.site.register(WaitingToken)
admin.site.register(PatientHistory)
admin.site.register(Billing)