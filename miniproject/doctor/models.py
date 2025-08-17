from django.db import models
from django.contrib.auth.models import User

# Profile model to differentiate roles
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, choices=[('doctor', 'Doctor'), ('user', 'User')])

    def __str__(self):
        return f"{self.user.username} ({self.role})"

# Doctor model
class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    specialization = models.CharField(max_length=100)
    fees = models.IntegerField(default=0)
    image = models.ImageField(upload_to='doctor_images/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.specialization}"

    
#image = models.ImageField(upload_to='doctr_images/' , blank=True, null=True)


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    doctor = models.ForeignKey('doctor.Doctor', on_delete=models.CASCADE)
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE)
    patient_name = models.CharField(max_length=100)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    profile_image = models.ImageField(upload_to='appointments/images/', blank=True, null=True)
    reason = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"{self.patient_name} - {self.appointment_date} at {self.appointment_time}"