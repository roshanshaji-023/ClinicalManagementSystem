from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Appointment, WaitingToken


@receiver(post_save, sender=Appointment)
def create_waiting_token(sender, instance, created, **kwargs):

    if created:
        WaitingToken.objects.create(appointment=instance)