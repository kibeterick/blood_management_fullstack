from django.urls import path
from . import views

urlpatterns = [
    # Home
    path('', views.home_portal, name='home_portal'),
    path('home/', views.home, name='home'),
    
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
    path('donor/delete/<int:pk>/', views.delete_donor, name='delete_donor'),
    
    # Blood Requests
    path('request-blood/', views.request_blood, name='request_blood'),
    path('blood-requests/', views.blood_request_list, name='blood_request_list'),
    path('all-requests/', views.all_requests, name='all_requests'),
    path('request/delete/<int:request_id>/', views.delete_request, name='delete_request'),
    
    # Reports
    path('stock-report/', views.stock_report_print, name='stock_report_print'),
    
    # EXPORT URLS
    path('export/donors/excel/', views.export_donors_excel, name='export_donors_excel'),
    path('export/donors/pdf/', views.export_donors_pdf, name='export_donors_pdf'),
    path('export/requests/excel/', views.export_requests_excel, name='export_requests_excel'),
    path('export/requests/pdf/', views.export_requests_pdf, name='export_requests_pdf'),
    
    # BLOOD COMPATIBILITY CHECKER - NEW FEATURE
    path('compatibility/', views.blood_compatibility_checker, name='blood_compatibility_checker'),
    path('compatibility/<str:blood_type>/', views.find_compatible_donors, name='find_compatible_donors'),
]