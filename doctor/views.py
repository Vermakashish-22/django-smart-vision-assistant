from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from doctor.models import Doctor, Appointment 
from django.contrib import messages
from django.contrib.auth.models import User
from patients.models import Patient, ConsultationPatient
import random

def doctor_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(f"🛠 Submitted username={username!r}, password={password!r}")
        user = authenticate(request, username=username, password=password)
        print("✅ after Authentication ",{user})

        if user is not None:
            print("Entered if block")
            if hasattr(user, 'user_profile') and user.user_profile.role == 'doctor':
                print("Entered if block2")
                login(request, user)
                return redirect('doctor_dashboard')
            else:
                print("Entered else block")
                messages.error(request, 'Access denied: Not a doctor.')
                return render(request,'doctor/doctor_login.html')
        else:
            print("Entered else block2")
            messages.error(request, 'Invalid username or password.')

    return render(request, 'doctor/doctor_login.html')


@login_required
def doctor_dashboard(request):
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        doctor = None

    appointments = []

    if doctor:
        # Patient count, consultations, recent patients
        patient_count = Patient.objects.filter(assigned_doctor=doctor).count()
        consultation_count = ConsultationPatient.objects.filter(doctor=doctor).count()
        recent_patients = Patient.objects.filter(assigned_doctor=doctor).order_by('-id')[:5]

        # Virtual appointments from Patient model
        patients = Patient.objects.filter(assigned_doctor=doctor).order_by('-appointment_date')

        # Convert each patient to a dict like Appointment
        for patient in patients:
            appointments.append({
                'id': patient.id,
                'profile_image': patient.image,
                'patient_name': patient.name,
                'appointment_date': patient.appointment_date,
                'appointment_time': patient.appointment_time,
                'reason': patient.disease or "N/A",
                'status': 'Pending',  # Default/fake status
            })

    else:
        patient_count = 0
        consultation_count = 0
        recent_patients = []

    return render(request, 'doctor/doctor_dashboard.html', {
        'patient_count': patient_count,
        'consultation_count': consultation_count,
        'recent_patients': recent_patients,
        'appointments': appointments,
    })

def doctor_list(request):
    doctors = Doctor.objects.select_related('user').filter(user__user_profile__role='doctor')
    return render(request, 'doctor/doctor_list.html', {'doctors': doctors})

def doctor_add(request):
    users = User.objects.filter(user_profile__role ='doctor')
    return render(request, 'doctor/doctor_add.html',{'users':users})


# 🔹 View 3: Handle form POST and save doctor + user
def doctor_save(request):
    if request.method == 'POST':
        user_id = request.POST.get('user')
        specialization = request.POST.get('specialization')
        fees = request.POST.get('fees')
        image = request.FILES.get('image')

        # Check if a doctor with this user already exists
        if Doctor.objects.filter(user_id=user_id).exists():
            messages.error(request, "Doctor for this user already exists.")
            return render(request,'doctor/doctor_add.html')

    
        print("Entries taken")
        # Create doctor
        doctor = Doctor(
            user_id=user_id,
            specialization=specialization,
            fees=fees,
            image=image
        )
        print("doctor created")
        doctor.save()

        messages.success(request, "Doctor added successfully.")
        return render(request,'doctor/doctor_list.html')

    return redirect('doctor_add')

def doctor_edit(request, id):
    doctor = Doctor.objects.get(id=id)
    users=User.objects.all()
    return render(request, 'doctor/doctor_edit.html', {'doctor': doctor,'users':users})

def doctor_update(request, id):
    if request.method == 'POST':
        doctor = get_object_or_404(Doctor, id=id)
        doctor.specialization = request.POST.get('specialization')
        doctor.fees = request.POST.get('fees')
        doctor.image = request.FILES.get('image')

        doctor.save()
        return redirect('doctor_list')
    else:
        return redirect('doctor_edit', id=id)

def doctor_delete(request, id):
    doctor = get_object_or_404(Doctor, id=id)
    doctor.user.delete()  
    messages.success(request, "Doctor deleted successfully.")
    return redirect('doctor_list')


@login_required(login_url='login_get_view')
def appointment_form(request):
    if request.method == 'POST':
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        reason = request.POST.get('reason')
        image = request.FILES.get('profile_image')

        # Automatically assign a doctor
        doctors = Doctor.objects.all()
        if not doctors.exists():
            messages.error(request, "No doctors available at the moment.")
            return render(request, 'doctor/appointment_form.html')

        doctor = random.choice(doctors)

        # Get existing patient object
        patient = get_object_or_404(Patient, user=request.user)

        # Create Appointment
        Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            patient_name=patient.name,
            reason=reason,
            profile_image=image if image else patient.image,  # fallback to patient image
            appointment_date=appointment_date,
            appointment_time=appointment_time,
        )

        messages.success(request, f"Appointment made successfully! You have been assigned to Dr. {doctor.user}.")
        return render(request, 'doctor/appointment_form.html')

    return render(request, 'doctor/appointment_form.html')



@login_required
def appointment_list(request):
    user = request.user

    try:
        # If the logged-in user is a doctor
        doctor = Doctor.objects.get(user=user)
        appointments = Appointment.objects.filter(doctor=doctor)
    except Doctor.DoesNotExist:
        # If not a doctor, maybe patient
        try:
            patient = Patient.objects.get(user=user)
            appointments = Appointment.objects.filter(patient=patient)
        except Patient.DoesNotExist:
            appointments = Appointment.objects.none()

    return render(request, 'doctor/appointment_list.html', {
        'appointments': appointments
    })
    
    
@login_required
def appointment_edit(request, id):
    appointment = get_object_or_404(Appointment, id=id)
    return render(request, 'doctor/appointment_edit.html', {'appointment': appointment})

@login_required
def appointment_update(request, id):
    if request.method == 'POST':
        appointment = get_object_or_404(Appointment, id=id)
        appointment.patient_name = request.POST.get('patient_name')
        appointment.appointment_date = request.POST.get('appointment_date')
        appointment.appointment_time = request.POST.get('appointment_time')
        appointment.reason = request.POST.get('reason')
        appointment.status = request.POST.get('status')

        if request.FILES.get('profile_image'):
            appointment.profile_image = request.FILES.get('profile_image')

        appointment.save()
        return redirect('appointment_list')
    else:
        return redirect('appointment_edit', id=id)

@login_required
def appointment_delete(request, id):
    appointment = get_object_or_404(Appointment, id=id)
    appointment.delete()
    return redirect('appointment_list')


@login_required
def doctor_logout(request):
    logout(request)
    return redirect('doctor_login')