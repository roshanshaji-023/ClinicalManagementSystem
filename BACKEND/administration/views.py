from logging import Filter

from django.shortcuts import render

# Create your views here.
# administration/views.py
from rest_framework import viewsets
from django.contrib.auth.models import User, Group
from rest_framework import viewsets, status
from rest_framework.response import Response
from .serializer import UserSerializer, GroupSerializer, DepartmentSerializer, StaffSerializer, DoctorSerializer ,DoctorAdditionalInfoSerializer
from .models import Department, Staff, Doctor, Doctor_additional_info

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class DepartmentViewSet(viewsets.ModelViewSet):
    '''
        Filter to return only active departments in API list endpoint.
        This ensures that only active departments are shown in the API responses, 
        while still allowing us to keep inactive departments in the database for historical reference and potential reactivation in the future.
    '''
    def get_queryset(self):
        return Department.objects.filter(status='active')
    serializer_class = DepartmentSerializer
    '''
    override destroy method to implement soft delete by setting status to inactive instead of deleting the record from database.
    This allows us to keep historical data and avoid issues with foreign key constraints in related models.
    '''
    def destroy(self, request, *args, **kwargs):
        department = self.get_object()  # Fetch the specific Department instance
        department.status = 'inactive'  # Set status instead of deleting
        department.save()  # Save change to database
        return Response(
            {"success": f"Department {department.dept_name} set to inactive."},
            status=status.HTTP_200_OK
        )

    
class StaffViewSet(viewsets.ModelViewSet):
    serializer_class = StaffSerializer

    # Only return active staff members
    def get_queryset(self):
        return Staff.objects.filter(status='active')

    # Soft delete implementation for Staff
    def destroy(self, request, *args, **kwargs):
        staff = self.get_object()  # Fetch the staff instance
        staff.status = 'inactive'  # Mark as inactive
        staff.save()  # Update in database
        return Response(
            {"success": f"Staff {staff.user.username} set to inactive."},
            status=status.HTTP_200_OK
        )

class DoctorViewSet(viewsets.ModelViewSet):
    serializer_class = DoctorSerializer

    # Only return active doctors
    def get_queryset(self):
        return Doctor.objects.filter(status='active')

    # Soft delete for Doctor
    def destroy(self, request, *args, **kwargs):
        doctor = self.get_object()  # Get specific doctor instance
        doctor.status = 'inactive'  # Mark as inactive
        doctor.save()  # Save change to DB
        return Response(
            {"success": f"Doctor {doctor.user.username} set to inactive."},
            status=status.HTTP_200_OK
        )

class DoctorAdditionalInfoViewSet(viewsets.ModelViewSet):
    queryset = Doctor_additional_info.objects.all()
    serializer_class = DoctorAdditionalInfoSerializer