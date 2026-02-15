from django.urls import path
from . import views

urlpatterns = [
    # Home
    path('', views.home, name='home'),
    
    # Authentication
    path('register/', views.user_register, name='user_register'),
    path('admin-register/', views.admin_register, name='admin_register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Dashboards
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Donor Management
    path('register-donor/', views.register_donor, name='register_donor'),
    path('donor-list/', views.donor_list, name='donor_list'),
    
    # Blood Requests
    path('request-blood/', views.request_blood, name='request_blood'),
    path('blood-requests/', views.blood_request_list, name='blood_request_list'),
    path('blood-request/<int:pk>/', views.blood_request_detail, name='blood_request_detail'),
    path('blood-request/<int:pk>/update-status/', views.update_request_status, name='update_request_status'),
    
    # Donations
    path('record-donation/', views.record_donation, name='record_donation'),
    path('donations/', views.donation_list, name='donation_list'),
    
    # Inventory
    path('blood-inventory/', views.blood_inventory, name='blood_inventory'),
]