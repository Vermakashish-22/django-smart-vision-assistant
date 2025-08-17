# Create your models here.
from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model): 
    ROLE_CHOICES = (
        ('doctor', 'Doctor'),
        ('admin', 'Admin'),
        ('patient', 'Patient'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.email} - {self.role}"
