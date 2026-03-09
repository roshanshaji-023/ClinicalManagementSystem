from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/admin/', include('administration.urls')),
    path('api/lab/', include('labtechnician.urls')),
    path('api/reception/', include('reception.urls')),
    path('api/pharmacy/', include('pharmacist.urls')),
]