from django.contrib import admin
from patients.models import Consultation, Patient, ConsultationPatient

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['name', 'assigned_doctor', 'appointment_date', 'appointment_time']

@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'doctor']

@admin.register(ConsultationPatient)
class ConsultationPatientAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'age', 'doctor', 'date', 'time', 'ai_prescription']
    search_fields = ['name', 'email', 'user_prescription', 'ai_prescription']
