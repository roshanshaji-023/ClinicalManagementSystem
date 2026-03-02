from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import LabTestType
from .serializer import LabTestTypeSerializer

# Create your views here.

class LabTestTypeViewSet(viewsets.ModelViewSet):
    """
    Handles:
    - List all test types
    - Create new test type
    - Retrieve single test type
    - Update test type
    - Delete test type
    """
    queryset = LabTestType.objects.all()
    serializer_class = LabTestTypeSerializer
