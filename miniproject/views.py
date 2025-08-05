from django.http import HttpResponse
from django.shortcuts import render
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib import messages

def home(request):
    # return HttpResponse("Hello World.")
    return render(request,'home.html')
    
def about(request):
    doctors = [
    {'name': 'Dr. Ananya Verma', 'specialization': 'Cataract Specialist', 'experience': '10+', 'image': 'images/doctor1.jpg'},
    {'name': 'Dr. Aarav Mehta', 'specialization': 'Retina Surgeon', 'experience': '8+', 'image': 'images/doctor2.jpg'},
    {'name': 'Dr. Isha Kapoor', 'specialization': 'Cornea Specialist', 'experience': '6+', 'image': 'images/doctor3.jpg'},
    {'name': 'Dr. Rahul Sharma', 'specialization': 'Lens Replacement', 'experience': '12+', 'image': 'images/doctor4.jpg'},
    {'name': 'Dr. Karan Desai', 'specialization': 'Oculoplasty Expert', 'experience': '7+', 'image': 'images/doctor5.jpg'},
    ]
    return render(request,'about.html', {'doctors': doctors})
def services(request):
    # return HttpResponse("Hello World.")
    return render(request,'services.html')
    
def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')

        subject = f"New Contact Message from {name}"
        full_message = f"""
        Name: {name}
        Email: {email}
        Phone: {phone}

        Message:
        {message}
        """
        print("name:",name,"email:",email,"phone:",phone,"message:",message)

        send_mail(
            subject,
            full_message,
            email,  # from
            ['kashishrishi11@gmail.com'],  # to: Replace with your Gmail
            fail_silently=False,
        )
        print("message sent")
        messages.success(request, 'Your message has been sent successfully!')
        return redirect('contact')  # or any page name

    return render(request, 'contact.html')
    