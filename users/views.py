from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout as django_logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.utils import timezone
from django.db.models.functions import TruncDate
from django.db.models import Count
from datetime import timedelta
import datetime
from django.contrib.auth.hashers import check_password
from users.models import Profile 
from doctor.models import Doctor , Appointment
from patients.models import Patient, ConsultationPatient

# Create your views here.

def login_get_view(request):
    if request.user.is_authenticated:
        print("user is authenticated")
        user = request.user
        if user.is_superuser:
            print("no")
            return redirect('user_list')
        
        user_profile = getattr(user, 'user_profile', None)
        role = getattr(user_profile, 'role', None) if user_profile else None
        
        if role == 'patient':
            return redirect('patient_dashboard')
        else:
            return redirect('user_list')

    # Show login form with user roles (optional)
    users = User.objects.all().select_related('user_profile')

    user_roles = []
    for user in users:
        if user.is_superuser:
            role = 'superuser'
        else:
            role = getattr(getattr(user, 'user_profile', None), 'role', 'No Role Assigned')
            print(role)

        user_roles.append({
            'username': user.username,
            'role': role,
        })

    return render(request, 'admin/login.html', {'user_roles': user_roles})


# POST: Handle login submission
def login_post_view(request):
    if request.method == 'POST':
        print("entering loginpost")
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(username,"and", password)
        
        try:
            user = User.objects.get(username=username)

            if check_password(password, user.password):
                if not user.is_active:
                    print("account is not active")
                    messages.error(request, 'Account is disabled.')
                    return render(request, 'admin/login.html')

                login(request, user)

                if user.is_superuser:
                    return redirect('user_list')

                user_profile = getattr(user, 'user_profile', None)
                role = getattr(user_profile, 'role', None) if user_profile else None
                print("role : ",role)
                if role == 'patient':
                    return redirect('patient_dashboard')
                elif role == 'doctor':
                    return redirect('doctor_dashboard')
                else:
                    return redirect('user_list')

            else:
                print("entering else1")
                messages.error(request, 'Invalid username or password.')
                return render(request, 'admin/login.html')

        except User.DoesNotExist:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'admin/login.html')
    print("everything done")
    return redirect('login_get_view')

def logout(request):
    django_logout(request)
    return redirect('login_get_view')

@login_required(login_url='login_get_view')
def dashboard_users(request):
    doctor_count = Profile.objects.filter(role='doctor').count()
    patient_count = Profile.objects.filter(role='patient').count()
    user_count = Profile.objects.filter(role='user').count()

    appointment_count = Appointment.objects.count()
    consultation_count = ConsultationPatient.objects.count()

    today = timezone.now().date()
    seven_days_ago = today - timedelta(days=6)

    users_per_day = (
        User.objects.filter(date_joined__date__gte=seven_days_ago)
        .annotate(date=TruncDate('date_joined'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )

    role_labels = ['Doctors', 'Patients', 'User']
    role_counts = [doctor_count, patient_count, user_count]

    date_labels = []
    user_counts = []
    for i in range(7):
        day = seven_days_ago + timedelta(days=i)
        date_labels.append(day.strftime('%b %d'))
        day_count = next((item['count'] for item in users_per_day if item['date'] == day), 0)
        user_counts.append(day_count)

    context = {
        'doctor_count': doctor_count,
        'patient_count': patient_count,
        'user_count': user_count,
        'appointment_count': appointment_count,
        'consultation_count': consultation_count,
        'date_labels': date_labels,
        'user_counts': user_counts,
        'role_labels': role_labels,
        'role_counts': role_counts,
    }

    return render(request, 'users/dashboard_users.html', context)


def user_list(request):
    users=User.objects.all().select_related('user_profile')
    return render(request, 'users/user_list.html', {'users': users})


def register_get(request):
    context = {
        'doctors': Doctor.objects.all()
    }
    print("Leaving get method")
    return render(request, 'admin/register.html', context)

def register_post(request):
    if request.method != 'POST':
        print("Request not post")
        return redirect('register_get')

    try:
        print("Entered try block")
        name = request.POST.get('name')
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        role = request.POST.get('role')

        print("name : ",name,"username : ",username,"password :",password,"email :",email, "role :",role)
        if not all([name, username, password, email, role]):
            messages.error(request, "All fields are required.")
            return redirect('register_get')

        if User.objects.filter(username=username).exists():
            messages.error(request, "User already exists.")
            return redirect('register_get')

        user = User.objects.create_user(username=username, password=password, email=email, first_name=name)
        print("user : ",user)
        Profile.objects.create(user=user, role=role)

        
        if role == 'patient':
            try:
            # Get patient-specific data
                age = request.POST.get('age') or 0
                contact = request.POST.get('contact') or username
                blood_group = request.POST.get('blood_group') or 'Unknown'
                assigned_doctor_id = request.POST.get('assigned_doctor')
                image = request.FILES.get('profile_image')
                
                # Validate assigned doctor
                if not assigned_doctor_id:
                    messages.error(request, "Assigned doctor is required.")
                    return redirect('register_get')

                assigned_doctor = Doctor.objects.get(id=assigned_doctor_id)
                print("age:",age,"contact:",contact,"blood group:",blood_group,"doctor:",assigned_doctor)
                # Prevent multiple patient profiles for same user
                if hasattr(user, 'patient_profile'):
                    messages.error(request, "Patient profile already exists for this user.")
                    return redirect('register_get')
                
                print("Going to create new user")
                # Save patient
                Patient.objects.create(
                    user=user,
                    name=name,
                    age=age,
                    contact=contact,
                    email=email,
                    blood_group=blood_group,
                    assigned_doctor=assigned_doctor,
                    image=image,
                    appointment_date=timezone.now().date(),
                    appointment_time=datetime.datetime.now().time()
                )
                
                print("Patient created",Patient)
                # Create Appointment Automatically
                Appointment.objects.create(
                    doctor=assigned_doctor,
                    patient_name=name,
                    appointment_date=timezone.now().date(),
                    appointment_time=datetime.datetime.now().time(),
                    status='Pending'
                )
                print("Appointment created",Appointment)
            except Exception as e:
                print("Error")
                messages.error(request, f"An error occurred: {str(e)}")
                return redirect('register_get')

        elif role == 'doctor':
            print("Entered doctor")
            specialization = request.POST.get('specialization')
            fees = int(request.POST.get('fees') or 0)
            image = request.FILES.get('doctor_image')

            print("Specialization : ",specialization , "fees : ",fees)
            Doctor.objects.update_or_create(
                user=user,
                defaults={
                    'specialization': specialization,
                    'fees': fees,
                    'image': image
                }
            )
            print("Doctor created", Doctor)

        print("Registered")
        messages.success(request, "Registration successful.")
        return redirect('login_get_view')

    except Exception as e:
        print("Error")
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('register_get')