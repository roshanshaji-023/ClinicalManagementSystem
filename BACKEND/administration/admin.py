from django.contrib import admin
from .models import Department,Staff,Doctor,Doctor_additional_info
# Register your models here.

admin.site.register(Department)
admin.site.register(Doctor)
admin.site.register(Staff)
admin.site.register(Doctor_additional_info)
