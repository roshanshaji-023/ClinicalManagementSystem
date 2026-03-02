# from django.db import models
# from administration.models import  Staff
# from django.core.exceptions import ValidationError
# from django.utils import timezone



# Create your models here.
# class Empty:
#     pass

# class Patient(models.Model):
#     patient_id =models.AutoField(primary_key=True)
#     patient_code = models.CharField(max_length=20, unique=True, blank=True)
#     first_name = models.CharField(max_length=100)
#     last_name = models.CharField(max_length=100)
#     date_of_birth = models.DateField()
#     gender = models.CharField(max_length=10)
#     blood_group = models.CharField(max_length=5)
#     phone_number = models.CharField(max_length=15, unique=True)
#     email_id = models.EmailField(blank=True, null=True)
#     address = models.TextField()
#     is_active = models.BooleanField(default=True)
#     staff = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True)
#     created_date = models.DateTimeField(auto_now_add=True)

#     def clean(self):
#         if not self.phone_number:
#             raise ValidationError("Phone number is required")

#     def __str__(self):
#         return f"{self.first_name} {self.last_name}"
    

# class Appointment(models.Model):

#     STATUS_CHOICES = [
#         ('Scheduled', 'Scheduled'),
#         ('Waiting', 'Waiting'),
#         ('In Consultation', 'In Consultation'),
#         ('Completed', 'Completed'),
#         ('Cancelled', 'Cancelled'),
#         ('No Show', 'No Show'),
#     ]

#     VISIT_TYPE = [
#         ('New', 'New'),
#         ('Follow-Up', 'Follow-Up'),
#     ]

#     patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
#     doctor = models.ForeignKey('doctor.Doctor', on_delete=models.CASCADE)
#     appointment_date = models.DateField()
#     appointment_time = models.TimeField()
#     visit_type = models.CharField(max_length=20, choices=VISIT_TYPE)
#     parent_appointment = models.ForeignKey(
#         'self',
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True
#     )
#     status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Scheduled')
#     is_emergency = models.BooleanField(default=False)
#     cancellation_reason = models.TextField(null=True, blank=True)
#     staff = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def clean(self):
#         if self.appointment_date < timezone.now().date():
#             raise ValidationError("Appointment date cannot be in the past.")

#     def __str__(self):
#         return f"{self.patient} - {self.appointment_date}"
    

# class WaitingToken(models.Model):
#     appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
#     token_number = models.IntegerField()
#     token_date = models.DateField(default=timezone.now)
#     issued_time = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ('token_number', 'token_date')

#     def __str__(self):
#         return f"Token {self.token_number} - {self.token_date}"
    


# class PatientHistory(models.Model):

#       history_id = models.BigAutoField(primary_key=True)

#       patient = models.ForeignKey(
#         'Patient',
#         on_delete=models.CASCADE,
#         related_name='histories'
#       )

#       appointment = models.OneToOneField(
#         'Appointment',
#         on_delete=models.CASCADE,
#         related_name='history'
#       )

#       consultation_note = models.TextField()

#       created_at = models.DateTimeField(auto_now_add=True)

#       def __str__(self):
#         return f"History - {self.patient} ({self.appointment.appointment_date})"
    

    

# class Bill(models.Model):

#     BILL_TYPE = [
#         ('Consultation', 'Consultation'),
#         ('Pharmacy', 'Pharmacy'),
#         ('Lab', 'Lab'),
#     ]

#     STATUS = [
#         ('Pending', 'Pending'),
#         ('Paid', 'Paid'),
#         ('Partial', 'Partial'),
#     ]

#     appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
#     patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
#     bill_type = models.CharField(max_length=30, choices=BILL_TYPE)
#     amount = models.DecimalField(max_digits=12, decimal_places=2)
#     status = models.CharField(max_length=20, choices=STATUS, default='Pending')
#     staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.bill_type} Bill - {self.patient}"
    

# class Payment(models.Model):
#     bill = models.ForeignKey(Bill, on_delete=models.CASCADE)
#     amount_paid = models.DecimalField(max_digits=12, decimal_places=2)
#     payment_method = models.CharField(max_length=30)
#     payment_date = models.DateTimeField(auto_now_add=True)
#     received_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True)

#     def __str__(self):
#         return f"Payment - {self.bill}"
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils import timezone
from administration.models import Staff,Doctor



# Patient Model


class Patient(models.Model):

    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
    ]

    phone_validator = RegexValidator(
        regex=r'^\d{10}$',
        message="Phone number must be exactly 10 digits."
    )

    patient_id = models.AutoField(primary_key=True)

    patient_code = models.CharField(
        max_length=20,
        unique=True,
        editable=False
    )

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    date_of_birth = models.DateField()

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES
    )

    blood_group = models.CharField(
        max_length=5,
        choices=BLOOD_GROUP_CHOICES
    )

    phone_number = models.CharField(
        max_length=10,
        unique=True,
        validators=[phone_validator]
    )

    email_id = models.EmailField(blank=True, null=True)

    address = models.TextField()

    is_active = models.BooleanField(default=True)

    staff = models.ForeignKey(
        Staff,
        on_delete=models.SET_NULL,
        null=True
    )

    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_date']

    def clean(self):
        if self.date_of_birth > timezone.now().date():
            raise ValidationError("Date of birth cannot be in the future.")

    def save(self, *args, **kwargs):
        
        if not self.patient_code:
            self.patient_code = f"PAT{timezone.now().strftime('%Y%m%d%H%M%S')}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"



# Appointment Model


class Appointment(models.Model):

    STATUS_CHOICES = [
        ('Scheduled', 'Scheduled'),
        ('Waiting', 'Waiting'),
        ('In Consultation', 'In Consultation'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('No Show', 'No Show'),
    ]

    VISIT_TYPE = [
        ('New', 'New'),
        ('Follow-Up', 'Follow-Up'),
    ]

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='appointments'
    )

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='appointments'
    )

    appointment_date = models.DateField()
    appointment_time = models.TimeField()

    visit_type = models.CharField(
        max_length=20,
        choices=VISIT_TYPE
    )

    parent_appointment = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='follow_ups'
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='Scheduled'
    )

    is_emergency = models.BooleanField(default=False)

    cancellation_reason = models.TextField(null=True, blank=True)

    staff = models.ForeignKey(
        Staff,
        on_delete=models.SET_NULL,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-appointment_date', '-appointment_time']
        constraints = [
            models.UniqueConstraint(
                fields=['doctor', 'appointment_date', 'appointment_time'],
                name='unique_doctor_appointment_slot'
            )
        ]

    def clean(self):
        
        if self.pk is None and self.appointment_date < timezone.now().date():
            raise ValidationError("Appointment date cannot be in the past.")

    def __str__(self):
        return f"{self.patient} - {self.appointment_date}"



# Waiting Token Model


class WaitingToken(models.Model):

    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name='tokens'
    )

    token_number = models.IntegerField()

    token_date = models.DateField(default=timezone.now)

    issued_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['token_number']
        constraints = [
            models.UniqueConstraint(
                fields=['token_number', 'token_date'],
                name='unique_token_per_day'
            )
        ]

    def clean(self):
        if self.token_number <= 0:
            raise ValidationError("Token number must be positive.")

    def __str__(self):
        return f"Token {self.token_number} - {self.token_date}"



# Patient History Model
# -------------------------

class PatientHistory(models.Model):

    history_id = models.BigAutoField(primary_key=True)

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='histories'
    )

    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name='history'
    )

    consultation_note = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"History - {self.patient} ({self.appointment.appointment_date})"