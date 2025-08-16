from django.urls import path
from django.contrib.auth import views as auth_views
from users import views

urlpatterns=[
    path('login/', views.login_get_view, name='login_get_view'),
    path('login/submit/', views.login_post_view, name='login_post_view'),
    path('dashboard_users/', views.dashboard_users, name='dashboard_users'),
    path('user_list/', views.user_list, name='user_list'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register_get, name='register_get'),
    path('register/submit/', views.register_post, name='register_post'),
]