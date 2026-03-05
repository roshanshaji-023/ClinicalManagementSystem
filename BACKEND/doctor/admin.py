
# Register your models here.
from django.contrib import admin
from .models import DoctorAvailability


@admin.register(DoctorAvailability)
class DoctorAvailabilityAdmin(admin.ModelAdmin):
    list_display = ("avail_id", "doctor", "available_status", "available_date")
    list_filter = ("available_status", "available_date")
    search_fields = ("doctor__user__username",)