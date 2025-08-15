from django.urls import path
from patients import views

urlpatterns=[
    path('patients_list/', views.patients_list, name='patients_list'),
    path('patients_add/', views.patients_add, name='patients_add'),
    path('consultation_form/', views.consultation_form , name='consultation_form'),
    path('consultation_list/', views.consultation_list, name='consultation_list'),
    path('consultation_delete/<int:id>/', views.consultation_delete, name='consultation_delete'),
    path('patient_dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('logout/', views.logout_view, name='logout'),
    
] 