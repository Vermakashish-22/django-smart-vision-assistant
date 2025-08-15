from django.urls import path
from doctor import views

urlpatterns=[
    path('doctor/login/', views.doctor_login, name='doctor_login'),
    path('doctor/logout/', views.doctor_logout, name='doctor_logout'),
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor/list/', views.doctor_list, name='doctor_list'),
    path('doctor/add/', views.doctor_add, name='doctor_add'),
    path('doctor/save/', views.doctor_save, name='doctor_save'),
    path('doctor/edit/<int:id>/', views.doctor_edit, name='doctor_edit'),
    path('doctor/delete/<int:id>/', views.doctor_delete, name='doctor_delete'),
    path('doctor/update/<int:id>/', views.doctor_update, name='doctor_update'),
    path('appointment_form/', views.appointment_form, name='appointment_form'),
    path('appointment_list/', views.appointment_list, name='appointment_list'),
    path('appointment/edit/<int:id>/', views.appointment_edit, name='appointment_edit'),
    path('appointment/delete/<int:id>/', views.appointment_delete, name='appointment_delete'),
    path('appointment/update/<int:id>/', views.appointment_update, name='appointment_update'),
    
]