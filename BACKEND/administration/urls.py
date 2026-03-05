# administration/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet,
    GroupViewSet,
    DepartmentViewSet,
    StaffViewSet,
    DoctorViewSet,
    DoctorAdditionalInfoViewSet
)

# Create a router and register our viewsets with it
router = DefaultRouter()

# User APIs
router.register(r'users', UserViewSet, basename='user')

# Group APIs
router.register(r'groups', GroupViewSet, basename='group')

# Department APIs
router.register(r'departments', DepartmentViewSet, basename='department')

# Staff APIs
router.register(r'staff', StaffViewSet, basename='staff')

# Doctor APIs
router.register(r'doctors', DoctorViewSet, basename='doctor')

# Doctor Additional Info APIs
router.register(r'doctor-info', DoctorAdditionalInfoViewSet, basename='doctor-additional-info')

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),  # Include all router URLs
]
