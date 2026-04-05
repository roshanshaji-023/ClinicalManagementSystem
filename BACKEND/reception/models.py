from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils import timezone
from django.contrib.auth.models import User
from administration.models import Staff, Doctor
from decimal import Decimal


# -------------------- PATIENT --------------------

class Patient(models.Model):

    patient_id = models.AutoField(primary_key=True)

    patient_code = models.CharField(
        max_length=20,
        unique=True,
        editable=False
    )

    phone_validator = RegexValidator(
        regex=r'^\d{10}$',
        message="Phone number must be exactly 10 digits."
    )

    phone_number = models.CharField(
        max_length=10,
        unique=True,
        validators=[phone_validator]
    )

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50,blank=True, null=True)

    date_of_birth = models.DateField()

    gender = models.CharField(max_length=10)
    blood_group = models.CharField(max_length=5, blank=True, null=True)

    email_id = models.EmailField(blank=True, null=True)
    address = models.TextField()

    is_active = models.BooleanField(default=True)

    staff = models.ForeignKey(
        Staff,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_date']

    def clean(self):
     if self.date_of_birth > timezone.now().date():
        raise ValidationError("Date of birth cannot be in the future.")

    # First name validation
     if not self.first_name.isalpha():
        raise ValidationError("First name must contain only letters")

     if len(self.first_name) < 2:
        raise ValidationError("First name must be at least 2 characters")

    # ✅ FIXED last_name validation (optional field)
     if self.last_name:  # ONLY validate if provided
        if not self.last_name.isalpha():
            raise ValidationError("Last name must contain only letters")

        

    def save(self, *args, **kwargs):
        self.full_clean()

        if not self.pk:
            super().save(*args, **kwargs)
            self.patient_code = f"PAT{self.patient_id:04d}"
            super().save(update_fields=['patient_code'])
        else:
            super().save(*args, **kwargs)

    #  NEW: Age property 
    @property
    def age(self):
        today = timezone.now().date()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

    def __str__(self):
        return f"{self.patient_code} - {self.first_name}"


# -------------------- APPOINTMENT --------------------

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

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')

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

    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Scheduled')

    is_emergency = models.BooleanField(default=False)

    cancellation_reason = models.TextField(null=True, blank=True)

    staff = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True)

    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

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

        if self.appointment_date and self.appointment_date < timezone.localdate():
            raise ValidationError("Appointment date cannot be in the past.")

        # Apply time validation ONLY during creation
        if not self.pk:
            if self.appointment_date == timezone.localdate():
                if self.appointment_time < timezone.localtime().time():
                    raise ValidationError("Appointment time cannot be in the past")

        if self.visit_type == 'Follow-Up' and not self.parent_appointment:
            raise ValidationError("Follow-Up appointment must have a parent appointment.")

        if self.status == 'Cancelled' and not self.cancellation_reason:
            raise ValidationError("Cancellation reason is required.")

        if self.parent_appointment and self.parent_appointment.patient != self.patient:
            raise ValidationError("Parent appointment must belong to the same patient.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.patient} - {self.appointment_date}"


# -------------------- WAITING TOKEN --------------------

class WaitingToken(models.Model):

    token_id = models.AutoField(primary_key=True)

    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name='tokens'
    )

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        editable=False
    )

    token_number = models.PositiveIntegerField(blank=True, null=True)

    token_date = models.DateField(default=timezone.localdate)

    issued_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['token_number']
        constraints = [
            models.UniqueConstraint(
                fields=['doctor', 'token_number', 'token_date'],
                name='unique_token_per_doctor_per_day'
            )
        ]

    def clean(self):
        if not self.appointment:
            raise ValidationError("Appointment is required")

    def save(self, *args, **kwargs):

        self.full_clean()  #  IMPORTANT

        self.doctor = self.appointment.doctor

        today_token_count = WaitingToken.objects.filter(
            doctor=self.doctor,
            token_date=self.token_date
        ).count()

        #  FIXED: dynamic token limit
        if today_token_count >= self.doctor.max_tokens_per_day:
            raise ValidationError("Maximum token limit reached for this doctor today.")

        if not self.token_number:
            last_token = WaitingToken.objects.filter(
                doctor=self.doctor,
                token_date=self.token_date
            ).order_by('token_number').last()

            self.token_number = last_token.token_number + 1 if last_token else 1

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Token {self.token_number}"


# -------------------- PATIENT HISTORY --------------------

class PatientHistory(models.Model):

    history_id = models.AutoField(primary_key=True)

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name='history'
    )

    consultation_note = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def clean(self):

        if self.appointment.patient != self.patient:
            raise ValidationError("Appointment does not belong to this patient.")

        if self.appointment.status != 'Completed':
            raise ValidationError("History can only be created after completion.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)




# -------------------- BILLING --------------------

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

    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name='bill'
    )

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2)

    # NEW FIELDS 
    lab_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pharmacy_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='Pending')

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD,
        null=True,
        blank=True
    )

    staff = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True)

    paid_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def clean(self):

        #  Existing validations (keep)
        if self.consultation_fee <= 0:
            raise ValidationError("Consultation fee must be greater than zero.")

        if self.payment_status == "Paid" and not self.payment_method:
            raise ValidationError("Payment method required if paid.")
        
        if self.payment_status == "Pending" and self.payment_method:
            raise ValidationError("Payment method should not be set before payment.")

        if self.appointment.patient != self.patient:
            raise ValidationError("Mismatch between appointment and patient.")

        # NEW VALIDATIONS (IMPORTANT)

        if self.lab_cost < 0 or self.pharmacy_cost < 0 or self.discount < 0:
            raise ValidationError("Costs and discount cannot be negative.")

        if self.discount > (self.consultation_fee + self.lab_cost + self.pharmacy_cost):
            raise ValidationError("Discount cannot exceed total charges.")

        if self.total_amount < 0:
            raise ValidationError("Total amount cannot be negative.")

    def save(self, *args, **kwargs):

        #  AUTO CALCULATE TOTAL 
        self.total_amount = (
             Decimal(self.consultation_fee or 0) +
             Decimal(self.lab_cost or 0) +
             Decimal(self.pharmacy_cost or 0) -
             Decimal(self.discount or 0)
            )

        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Bill {self.bill_id}"