from django.urls import path
from . import views, api_views

urlpatterns = [
    # Home
    path('', views.home_portal, name='home_portal'),
    path('home/', views.home, name='home'),
    
    # Authentication
    path('register/', views.user_register, name='user_register'),
    path('admin-register/', views.admin_register, name='admin_register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Password Reset
    path('password-reset/', views.password_reset_request, name='password_reset'),
    path('password-reset/done/', views.password_reset_done, name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('password-reset-complete/', views.password_reset_complete, name='password_reset_complete'),
    
    # Contact Us
    path('contact/', views.contact_us, name='contact_us'),
    path('contact-for-blood/', views.contact_for_blood, name='contact_for_blood'),
    
    # Dashboards
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Donor Management
    path('register-donor/', views.register_donor, name='register_donor'),
    path('donor-list/', views.donor_list, name='donor_list'),
    path('donor/edit/<int:donor_id>/', views.edit_donor, name='edit_donor'),
    path('donor/delete/<int:pk>/', views.delete_donor, name='delete_donor'),
    path('donor-search/', views.donor_search_view, name='donor_search'),
    
    # Blood Requests
    path('request-blood/', views.request_blood, name='request_blood'),
    path('blood-requests/', views.blood_request_list, name='blood_request_list'),
    path('all-requests/', views.all_requests, name='all_requests'),
    path('request/delete/<int:request_id>/', views.delete_request, name='delete_request'),
    
    # Patient Management
    path('patient-list/', views.patient_list, name='patient_list'),
    path('patient/edit/<int:request_id>/', views.edit_patient, name='edit_patient'),
    path('patient/delete/<int:request_id>/', views.delete_patient, name='delete_patient'),
    
    # Reports
    path('stock-report/', views.stock_report_print, name='stock_report_print'),
    
    # EXPORT URLS
    path('export/donors/excel/', views.export_donors_excel, name='export_donors_excel'),
    path('export/donors/pdf/', views.export_donors_pdf, name='export_donors_pdf'),
    path('export/requests/excel/', views.export_requests_excel, name='export_requests_excel'),
    path('export/requests/pdf/', views.export_requests_pdf, name='export_requests_pdf'),
    
    # BLOOD COMPATIBILITY CHECKER
    path('compatibility/', views.blood_compatibility_checker, name='blood_compatibility_checker'),
    
    # ADVANCED SEARCH
    path('advanced-search/', views.advanced_search, name='advanced_search'),
    
    # CERTIFICATES
    path('certificate/download/<int:donation_id>/', views.download_certificate, name='download_certificate'),
    path('my-donations/', views.my_donations, name='my_donations'),
    
    # DONATION APPROVAL/REJECTION
    path('donation-requests/', views.donation_request_list, name='donation_request_list'),
    path('donation/approve/<int:donation_id>/', views.approve_donation, name='approve_donation'),
    path('donation/reject/<int:donation_id>/', views.reject_donation, name='reject_donation'),
    
    # API ENDPOINTS FOR AJAX
    path('api/donors/search/', api_views.donor_search_api, name='api_donor_search'),
    path('api/donor/<int:donor_id>/eligibility/', api_views.check_donor_eligibility_api, name='api_donor_eligibility'),
    path('api/inventory/', api_views.blood_inventory_api, name='api_inventory'),
    path('api/compatible-donors/', api_views.compatible_donors_api, name='api_compatible_donors'),
    path('api/request-statistics/', api_views.request_statistics_api, name='api_request_stats'),
    path('api/donor/<int:donor_id>/availability/', api_views.update_donor_availability_api, name='api_update_availability'),
    path('api/dashboard-stats/', api_views.dashboard_stats_api, name='api_dashboard_stats'),
]