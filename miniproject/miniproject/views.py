from django.http import HttpResponse
from django.shortcuts import render
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.cache import cache
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  
def home(request):
    # return HttpResponse("Hello World.")
    return render(request,'home.html')
 
@cache_page(60 * 15)  
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
    