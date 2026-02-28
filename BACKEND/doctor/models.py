from django.db import models
from administration.models import Doctor


class DoctorAvailability(models.Model):
    """
    Class for Doctor Availability 
    """
    class AvailabilityStatus(models.TextChoices):
        FULLDAY = "Fullday", "Fullday"
        MORNING_ONLY = "Morningonly", "Morning only"
        AFTERNOON_ONLY = "Afternoononly", "Afternoon only"
        ON_LEAVE = "onleave", "On leave"

    avail_id = models.AutoField(primary_key=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    available_status = models.CharField(
        max_length=20,
        choices=AvailabilityStatus.choices
    )
    available_date = models.DateField()
    updated_date = models.DateField(auto_now=True)

    class Meta:
        db_table = "doctoravailability"

    def __str__(self):
        return f"{self.doctor.user_name} - {self.available_status}"