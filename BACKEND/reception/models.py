from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils import timezone
from administration.models import Staff, Doctor

# Patient Model

class Patient(models.Model):

    patient_id = models.AutoField(primary_key=True)

    patient_code = models.CharField(
        max_length=20,
        unique=True,
        editable=False
    )

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

    phone_number = models.CharField(
        max_length=10,
        unique=True,
        validators=[phone_validator]
    )

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    date_of_birth = models.DateField()

    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES)

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
        super().save(*args, **kwargs)

        if not self.patient_code:
            self.patient_code = f"PAT{self.patient_id:04d}"
        super().save(update_fields=['patient_code'])
    def __str__(self):
        return f"{self.first_name} {self.last_name}"



# Appointment Model


class Appointment(models.Model):

    appointment_id = models.AutoField(primary_key=True)

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

    visit_type = models.CharField(max_length=20, choices=VISIT_TYPE)

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

        # Prevent past appointments
        if self.appointment_date < timezone.now().date():
            raise ValidationError("Appointment date cannot be in the past.")

        # Follow-up must have parent
        if self.visit_type == 'Follow-Up' and not self.parent_appointment:
            raise ValidationError("Follow-Up appointment must have a parent appointment.")

        # Cancellation must have reason
        if self.status == 'Cancelled' and not self.cancellation_reason:
            raise ValidationError("Cancellation reason is required.")

        # Parent appointment must belong to same patient
        if self.parent_appointment and self.parent_appointment.patient != self.patient:
            raise ValidationError("Parent appointment must belong to the same patient.")

    def __str__(self):
        return f"{self.patient} - {self.appointment_date}"



# Waiting Token Model


class WaitingToken(models.Model):

    token_id = models.AutoField(primary_key=True)

    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name='tokens'
    )

    token_number = models.IntegerField(blank=True, null=True)

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
        if self.token_number is not None and self.token_number <= 0:
            raise ValidationError("Token number must be positive.")

    def save(self, *args, **kwargs):

        # Auto-generate token number if not provided
        if not self.token_number:
            last_token = WaitingToken.objects.filter(
                token_date=timezone.now().date()
            ).order_by('token_number').last()

            if last_token:
                self.token_number = last_token.token_number + 1
            else:
                self.token_number = 1

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Token {self.token_number} - {self.token_date}"



# Patient History Model


class PatientHistory(models.Model):

    history_id = models.AutoField(primary_key=True)

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE
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

    def clean(self):

        # Ensure appointment belongs to patient
        if self.appointment.patient != self.patient:
            raise ValidationError("Appointment does not belong to this patient.")

        # History only after completion
        if self.appointment.status != 'Completed':
            raise ValidationError("History can only be created after appointment completion.")

    def __str__(self):
        return f"History - {self.patient} ({self.appointment.appointment_date})"



class Billing(models.Model):

    bill_id = models.AutoField(primary_key=True)

    PAYMENT_STATUS = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
    ]

    PAYMENT_METHOD = [
        ('Cash', 'Cash'),
        ('Card', 'Card'),
        ('UPI', 'UPI'),
    ]

    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE
    )

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE
    )

    consultation_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default='Pending'
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD,
        null=True,
        blank=True
    )

    staff = models.ForeignKey(
        Staff,
        on_delete=models.SET_NULL,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def clean(self):

        # Consultation fee cannot be negative
        if self.consultation_fee < 0:
            raise ValidationError("Consultation fee cannot be negative.")

        # Payment method required if payment completed
        if self.payment_status == "Paid" and not self.payment_method:
            raise ValidationError("Payment method must be provided if payment is completed.")

        # Appointment must belong to the same patient
        if self.appointment.patient != self.patient:
            raise ValidationError("Appointment does not belong to this patient.")

    def __str__(self):
        return f"Bill {self.bill_id} - {self.patient}"
    