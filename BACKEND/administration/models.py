from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
import re
# Create your models here.

class Department(models.Model):
    '''
    Stores clinic departments like Cardiology, Neurology, etc.
    '''
    dept_id = models.AutoField(primary_key=True)
    dept_code =models.CharField(max_length=10,unique=True)
    dept_name = models.CharField(max_length=100,unique=True)
    status = models.CharField(max_length=20,
                              choices=[('active','Active'),('inactive','Inactive')],
                              default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # model level validation
    def clean(self):
        if not self.dept_code.isalnum():
            raise ValidationError("Department code must be alphanumeric.")
    
    # Overriding save to trigger django for model level validation
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    def __str__(self):
        return self.dept_name

class Staff(models.Model):
    '''
    Stores info about the non-doctor staff information.
    Each staff must have a User account.
    '''
    staff_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    department = models.ForeignKey(Department,on_delete=models.CASCADE)
    date_of_birth = models.DateField()
    blood_group = models.CharField(
                max_length=5,
                choices=[
                    ('A+', 'A+'), ('A-', 'A-'),
                    ('B+', 'B+'), ('B-', 'B-'),
                    ('O+', 'O+'), ('O-', 'O-'),
                    ('AB+', 'AB+'), ('AB-', 'AB-'),
                ])
    phone_number = models.CharField(max_length=15)
    status = models.CharField(
        max_length=20,
        choices=[('active', 'Active'),('inactive', 'Inactive')],
        default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # model level validation 
    def clean(self):
    # DOB cannot be in future
        if self.date_of_birth > timezone.now().date():
            raise ValidationError("Date of birth cannot be in the future.")

        # Age must be at least 18
        age = (timezone.now().date() - self.date_of_birth).days // 365
        if age < 18:
            raise ValidationError("Staff must be at least 18 years old.")

        # Phone number validation (digits only, 10–15 length)
        if not re.fullmatch(r'\d{10,15}', self.phone_number):
            raise ValidationError("Phone number must contain 10 to 15 digits.")

        # Department must be active
        if self.department.status != 'active':
            raise ValidationError("Cannot assign staff to inactive department.")
    
    # Overriding save to trigger django for model level validation
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

class Doctor(models.Model):
    '''
    Stores doctor information.
    Each doctor must have a User account.
    '''
    doctor_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    department = models.ForeignKey(Department,on_delete=models.CASCADE)
    date_of_birth = models.DateField()
    qualification = models.CharField(max_length=150)
    experience_years = models.PositiveIntegerField()
    license_number = models.CharField(max_length=150,unique=True)
    consultation_fee = models.DecimalField(max_digits=10,decimal_places=2)
    max_tokens_per_day = models.PositiveIntegerField(default=60)
    phone_number = models.CharField(max_length=15)
    status = models.CharField(
        max_length=20,
        choices=[('active', 'Active'),('inactive', 'Inactive')],
        default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # model level validation
    def clean(self):
        # DOB cannot be future
        if self.date_of_birth > timezone.now().date():
            raise ValidationError("Date of birth cannot be in the future.")

        # Doctor must be at least 23 years old
        age = (timezone.now().date() - self.date_of_birth).days // 365
        if age < 23:
            raise ValidationError("Doctor must be at least 23 years old.")

        # Consultation fee must be positive
        if self.consultation_fee <= 0:
            raise ValidationError("Consultation fee must be greater than zero.")

        # Experience cannot exceed age-22 (logical check)
        if self.experience_years > (age - 22):
            raise ValidationError("Experience years exceed logical working age.")

        # Phone number validation
        if not re.fullmatch(r'\d{10,15}', self.phone_number):
            raise ValidationError("Phone number must contain 10 to 15 digits.")

        # Department must be active
        if self.department.status != 'active':
            raise ValidationError("Cannot assign doctor to inactive department.")
    
    # Overriding save to trigger django for model level validation
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    def __str__(self):
        return f"Dr. {self.user.username}"
    
    
class Doctor_additional_info(models.Model):
    '''
    stores additionall info about doctor 
    '''
    info_id = models.AutoField(primary_key=True)
    doctor = models.OneToOneField(Doctor,on_delete=models.CASCADE)
    specialization = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Additional info for Dr. {self.doctor.user.username}"
