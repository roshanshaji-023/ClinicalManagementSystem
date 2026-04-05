from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Appointment, PatientHistory, WaitingToken


# # -------------------- AUTO CREATE PATIENT HISTORY --------------------

# @receiver(post_save, sender=Appointment)
# def create_patient_history(sender, instance, created, **kwargs):
#     """
#     Automatically create PatientHistory when consultation is completed.
#     Prevents duplicate history creation.
#     """

#     if instance.status == "Completed":

#         if not PatientHistory.objects.filter(appointment=instance).exists():

#             PatientHistory.objects.create(
#                 patient=instance.patient,
#                 appointment=instance,
#                 consultation_note="Auto-generated after consultation"
#             )


# -------------------- AUTO GENERATE TOKEN --------------------

@receiver(post_save, sender=Appointment)
def create_token(sender, instance, created, **kwargs):
    """
    Generate token ONLY when patient arrives (status = Waiting)
    """

    # ✅ Only when status is Waiting
    if instance.status != "Waiting":
        return

    # ✅ Only for today
    if instance.appointment_date != timezone.localdate():
        return

    # ✅ Prevent duplicate token
    if WaitingToken.objects.filter(appointment=instance).exists():
        return

    # ✅ Create token
    WaitingToken.objects.create(appointment=instance)