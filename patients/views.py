from django.shortcuts import render,redirect,get_object_or_404
from patients.models import Patient
from doctor.models import Doctor
from django.contrib.auth import logout as django_logout
from django.contrib.auth.decorators import login_required
from patients.models import ConsultationPatient
import re, datetime
from django.http import HttpResponseForbidden
from django.template.loader import render_to_string
# from weasyprint import HTML,CSS
from xhtml2pdf import pisa
from django.contrib import messages
import os
from django.core.mail import send_mail
from dotenv import load_dotenv
from django.http import HttpResponse


def patients_list(request):
    patients = Patient.objects.all().order_by('-appointment_date')
    return render(request, 'patients/patients_list.html', {'patients': patients})


def patients_add(request):
    doctors = Doctor.objects.filter(user__user_profile__role='doctor')

    if request.method == 'POST':
        name = request.POST.get('name')
        doctor_id = request.POST.get('assigned_doctor')
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        disease = request.POST.get('disease')
        image = request.FILES.get('image')

        assigned_doctor = Doctor.objects.get(id=doctor_id)

        Patient.objects.create(
            name=name,
            assigned_doctor=assigned_doctor,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            disease=disease,
            image=image
        )
        return redirect('patients_list')  # make sure you have this URL and view

    return render(request, 'patients/patients_add.html', {'doctors': doctors})


# def generate_ai_prescription(prompt_text):
#     response = requests.post(
#         'http://localhost:11434/api/generate',
#     json={
#             "model": "gemma:2b",
#             "prompt": prompt_text,
#             "stream": True  # Make sure streaming is ON (default in Ollama)
#         },
#         stream=True  # Important: Handle streamed response!
#     )

#     final_output = ""
#     for line in response.iter_lines():
#         if line:
#             part = json.loads(line.decode('utf-8'))
#             final_output += part.get("response", "")

#     return final_output.strip()

# def clean_ai_prescription(text):
#     # Remove unwanted characters
#     cleaned = re.sub(r'[#:*]+', '', text)

#     # Normalize line breaks
#     cleaned = re.sub(r'\r\n|\r', '\n', cleaned)
    
#     # Insert consistent spacing after sections
#     cleaned = re.sub(r'(?i)Cause\s*:', '\n\n🧠 Cause:\n', cleaned)
#     cleaned = re.sub(r'(?i)Treatment\s*:', '\n\n💊 Treatment:\n', cleaned)
#     cleaned = re.sub(r'(?i)Medicines\s*:', '\n\n💉 Medicines:\n', cleaned)

#     # Format medicine items
#     cleaned = re.sub(r'-\s*([^-\n]+?)\s*-\s*([^-\n]+?)\s*-\s*([^\n]+)', r'• \1\n  ↳ \2\n  ⏱ \3', cleaned)

#     # Remove multiple empty lines
#     cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)

#     return cleaned.strip()

# def consultation_form(request):
#     doctors = Doctor.objects.all()
#     if request.method == 'POST':
#         action = request.POST.get('action')
#         name = request.POST.get('name')
#         email = request.POST.get('email')
#         age = request.POST.get('age')
#         doctor_id = request.POST.get('doctor_id')
#         user_prescription = request.POST.get('prescription')

#         doctor = Doctor.objects.get(id=doctor_id)

#         # Placeholder for now — will integrate Ollama later
        
#         if action == 'generate':
#             prompt_text = f"""
#             You are an experienced ophthalmologist providing online consultations.

#             🔒 Strict Instructions:
#             - Always answer, even if the patient's input is vague or incomplete.
#             - NEVER use markdown, symbols (*, #, –, etc.), or HTML — respond only in clean plain text.
#             - Follow the exact format shown below.
#             - DO NOT prescribe medicine if the issue involves:
#                 • Blurry or reduced eyesight
#                 • Vision correction (spectacles, laser surgery, etc.)
#                 • Eye surgery or any invasive procedures

#             📝 Response Format:
#             Patient's description:
#             {name}'s problem: {user_prescription}
            
#             Cause: [Short sentence describing the cause]

#             [TWO LINE BREAKS]

#             Treatment: [Two sentences of general advice. If surgical or laser procedure is needed, recommend visiting a doctor.]

#             [TWO LINE BREAKS]

#             Medicines:
#             - [Medicine Name] - [Dosage Instructions] - [Duration]

#             ---

#             If the patient's input indicates a **surgical or laser interest**, replace the *Medicines* section with:
#             "Consult a nearby ophthalmologist in person before starting any medication or undergoing surgery."

#             """
            
#             raw_ai_prescription = generate_ai_prescription(prompt_text)
#             ai_prescription = clean_ai_prescription(raw_ai_prescription)
            
#             # Save data to ConsultationPatient model
#             return render(request, 'patients/consultation_form.html', {
#                 'doctors': doctors,
#                 'ai_prescription': ai_prescription,
#                 'name': name,
#                 'email': email,
#                 'age': age,
#                 'doctor_id': doctor_id,
#                 'user_prescription': user_prescription,
#             })

#         elif action == 'confirm':
#             ai_prescription = request.POST.get('ai_prescription')

#             # Save to DB
#             ConsultationPatient.objects.create(
#                 name=name,
#                 email=email,
#                 age=age,
#                 doctor=doctor,
#                 user_prescription=user_prescription,
#                 ai_prescription=ai_prescription
#             )

#             return redirect('home')  # 👈 Redirect to home after confirmation

#     # GET request
#     return render(request, 'patients/consultation_form.html', {
#         'doctors': Doctor.objects.all(),
#     })


# def extract_medicines(ai_text):
#     """
#     Extracts prescribed medicines from AI prescription text.
#     Looks for 'Suggested Medication:' block.
#     """
#     pattern = r'<strong>Suggested Medication:</strong><br>\s*(.*?)<br><br>'
#     match = re.search(pattern, ai_text, re.DOTALL | re.IGNORECASE)
    
#     if match:
#         return match.group(1).strip()
#     else:
#         return "Medicines can not be prescribed. Consulted Doctor"


def extract_medicines(ai_text):
    """
    Extracts prescribed medicines from AI prescription text.
    Looks for 'Suggested Medication:' block.
    """
    print("Called")
    pattern = r'<strong>Suggested Medication:</strong>(?:<br>)?\s*(.*?)<br\s*/?>'
    match = re.search(pattern, ai_text, re.DOTALL | re.IGNORECASE)
    
    print("if")
    print(match)
    if match:
        return match.group(1).strip()
    print("matched")
    return "Medicines not found. Please consult a doctor."

load_dotenv()  # Load the .env file
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def clean_ai_prescription(text):
    # Remove unwanted symbols
    cleaned = re.sub(r'[#*]+', '', text)

    # Replace known headers with bold HTML
    headers = ["Symptoms:", "Suggested Medication:", "Recommended Action:", "Urgency:", "Doctor Assigned:"]
    for header in headers:
        cleaned = cleaned.replace(header, f"<strong>{header}</strong><br>")

    # Add line breaks between sections (if not already there)
    cleaned = cleaned.replace('\n',"<br>")  # double line spacing

    return cleaned.strip()


def is_serious_symptom(prescription: str) -> bool:
    serious_keywords = [
        'blurry', 'pain', 'bleeding', 'surgery', 'operation',
        'lasik', 'infection', 'burn', 'double vision'
    ]
    return any(word in prescription.lower() for word in serious_keywords)


def is_minor_symptom(prescription: str) -> bool:
    minor_keywords = [
        'itchy', 'dry', 'tired', 'strain', 'redness',
        'watery', 'irritation', 'light sensitive'
    ]
    return any(word in prescription.lower() for word in minor_keywords)



@login_required(login_url='login_get_view')
def consultation_form(request):
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        # not a patient → block or redirect
        return HttpResponseForbidden("You must be a patient to access this form.")
    if request.method == 'POST':
        action = request.POST.get('action')
        name = request.POST.get('name')
        email = request.POST.get('email')
        user_prescription = request.POST.get('prescription')
        patient = get_object_or_404(Patient, user=request.user)
        age = patient.age
        date = datetime.datetime.now().strftime('%d-%m-%Y')

        serious_keywords = ['blurry', 'pain', 'bleeding', 'swalling', 'surgery', 'operation', 'lasik', 'infection', 'burn', 'double vision']
        minor_keywords = ['itchy', 'dry', 'tired', 'strain', 'redness', 'watery', 'irritation', 'light sensitive','low sight','low eye sight','swalling']

        if action == 'generate':
            serious = any(word in user_prescription.lower() for word in serious_keywords)
            minor = any(word in user_prescription.lower() for word in minor_keywords)

            if serious:
                doctor = Doctor.objects.first()
                ai_prescription = f"""
                    <strong>Patient Name:</strong> {name}<br>
                    <strong>Age:</strong> {age}<br>
                    <strong>Date:</strong> {date}<br>
                    <strong>Symptoms:</strong>{user_prescription}<br>
                    <strong>Recommended Action:</strong>Your reported symptoms may indicate an underlying ocular condition 
                        such as infection, inflammation, or retinal involvement. 
                        It is strongly advised to consult an ophthalmologist at the earliest for a comprehensive eye examination 
                        and diagnosis. Delay in treatment may worsen the condition.<br>                   
                    <strong>Urgency:</strong>Immediate<br>
                    <strong>Doctor Assigned:</strong> Dr. {doctor.user.first_name if doctor else 'Not Available'}<br>
                    <strong>Prescribed on : </strong>{date}
                """
                context = {
                    'name': name,
                    'email': email,
                    'age': age,
                    'user_prescription': user_prescription,
                    'ai_prescription': clean_ai_prescription(ai_prescription),
                    'doctor_id': doctor.id if doctor else '',
                    'date': date
                }
                return render(request, 'patients/consultation_form.html', context)

            elif minor:
                ai_prescription = f"""
                    <strong>Patient Name:</strong> {name}<br>
                    <strong>Age:</strong> {age}<br>
                    <strong>Date:</strong> {date}<br>
                    <strong>Symptoms:</strong>{user_prescription}<br>
                    <strong>Suggested Medication:</strong> Prescribe lubricating eye drops (e.g., Carboxymethylcellulose 0.5%)
                        - 1 drop in each eye, three times daily for 7 days.<br>
                    <strong>Recommended Action:</strong> No critical pathology detected. 
                        Symptoms indicate mild digital eye strain. Ensure 20-20-20 rule compliance (every 20 minutes, 
                        look 20 feet away for 20 seconds), maintain screen hygiene, and limit prolonged screen exposure. 
                        If symptoms persist, consult an ophthalmologist in person.

                    <strong>Urgency:</strong>Normal<br>
                """
                context = {
                    'name': name,
                    'email': email,
                    'age': age,
                    'user_prescription': user_prescription,
                    'ai_prescription': clean_ai_prescription(ai_prescription),
                    'doctor_id': '',
                    'date': date
                }
                return render(request, 'patients/consultation_form.html', context)

            else:
                messages.warning(request, "Unable to assess your symptoms. Please provide more detail.")
                return redirect('consultation_form')

        elif action == 'confirm':
            doctor_id = request.POST.get('doctor_id')
            ai_prescription = request.POST.get('ai_prescription')
            doctor = get_object_or_404(Doctor, id=doctor_id) if doctor_id else None

            print("About to enter")
            extracted_medicine = extract_medicines(ai_prescription)
            
            ConsultationPatient.objects.create(
                name=name,
                email=email,
                age=age,
                doctor=doctor,
                user_prescription=user_prescription,
                ai_prescription=ai_prescription,
                medicine_summary=extracted_medicine
            )

            try:
                send_mail(
                    "Eye Consultation Confirmation",
                    f"Hi {name},\n\nThank you for consulting with Vision Assistant. Here's the analysis:\n\n{ai_prescription}\n\n- Vision Care Team",
                    'noreply@visioncare.com',
                    [email],
                    fail_silently=True,
                )
            except Exception as e:
                print("Email failed:", e)

            messages.success(request, "Your consultation has been recorded successfully.")
            return redirect('consultation_form')

        elif action == 'download_pdf':
            html_content = request.POST.get('ai_prescription')
            html_string = render_to_string('patients/pdf_template.html', {'content': html_content})
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="prescription.pdf"'
            pisa_status = pisa.CreatePDF(html_string, dest=response)
            if pisa_status.err:
                return HttpResponse('Error generating PDF', status=500)
            return response

    return render(request, 'patients/consultation_form.html')

def consultation_list(request):
    consultation_patients = ConsultationPatient.objects.all().order_by('-date', '-time')

    # Attach medicines separately for display
    for patient in consultation_patients:
        patient.medicines_only = extract_medicines(patient.ai_prescription)

    return render(request, 'patients/consultation_list.html', {'consultation_patients': consultation_patients})


def consultation_delete(request, id):
    patient = get_object_or_404(ConsultationPatient, id=id)
    patient.delete()
    return redirect('consultation_list')

@login_required(login_url='login_get_view')
def patient_dashboard(request):
    user = request.user
    try:
        patient = Patient.objects.filter(user=user).first()
        if not patient:
            messages.error(request, "Patient profile not found.")
    except Patient.DoesNotExist:
        messages.error(request, "Patient profile not found.")
        return render(request,'patients/patient_dashboard.html')

    # Fetch only the patient's appointments
    appointments = ConsultationPatient.objects.filter(email=user.email).order_by('-date', '-time')

    return render(request, 'patients/patient_dashboard.html', {
        'patient': patient,
        'appointments': appointments,
    })

@login_required
def logout_view(request):
    django_logout(request)
    return redirect('home')