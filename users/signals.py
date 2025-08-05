from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Profile
from doctor.models import Doctor

@receiver(post_save, sender=Profile)
def create_doctor_for_profile(sender, instance, created, **kwargs):
    if instance.role == 'doctor':
        if not Doctor.objects.filter(user=instance.user).exists():
            Doctor.objects.create(user=instance.user, specialization='General')
