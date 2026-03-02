from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LabTestTypeViewSet

router = DefaultRouter()
router.register(r'lab-test-types', LabTestTypeViewSet)

urlpatterns = router.urls
