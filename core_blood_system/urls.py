from django.urls import path
from . import views, api_views, views_appointments, views_notifications, views_matching, views_analytics, views_qrcode

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
    
    # USER MANAGEMENT (Admin only)
    path('users/', views.user_list, name='user_list'),
    path('users/<int:user_id>/', views.view_user, name='view_user'),
    path('users/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    
    # APPOINTMENT SCHEDULING SYSTEM (Feature 1)
    path('appointments/book/', views_appointments.book_appointment, name='book_appointment'),
    path('appointments/my/', views_appointments.my_appointments, name='my_appointments'),
    path('appointments/cancel/<int:appointment_id>/', views_appointments.cancel_appointment, name='cancel_appointment'),
    path('appointments/reschedule/<int:appointment_id>/', views_appointments.reschedule_appointment, name='reschedule_appointment'),
    path('appointments/admin/', views_appointments.admin_appointments_list, name='admin_appointments_list'),
    path('appointments/admin/<int:appointment_id>/', views_appointments.admin_appointment_detail, name='admin_appointment_detail'),
    path('appointments/calendar/', views_appointments.appointments_calendar, name='appointments_calendar'),
    
    # NOTIFICATIONS SYSTEM (Feature 2)
    path('notifications/', views_notifications.notification_center, name='notification_center'),
    path('notifications/mark-read/<int:notification_id>/', views_notifications.mark_as_read, name='mark_as_read'),
    path('notifications/mark-all-read/', views_notifications.mark_all_read, name='mark_all_read'),
    path('notifications/delete/<int:notification_id>/', views_notifications.delete_notification, name='delete_notification'),
    path('api/notifications/unread-count/', views_notifications.get_unread_count, name='api_unread_count'),
    path('api/notifications/recent/', views_notifications.get_recent_notifications, name='api_recent_notifications'),
    
    # MATCHING SYSTEM (Feature 3)
    path('matching/results/<int:request_id>/', views_matching.match_results, name='match_results'),
    path('matching/trigger/<int:request_id>/', views_matching.trigger_matching, name='trigger_matching'),
    path('matching/respond/<int:match_id>/', views_matching.donor_response, name='donor_response'),
    path('matching/my-matches/', views_matching.my_matches, name='my_matches'),
    path('matching/admin/', views_matching.admin_matching_dashboard, name='admin_matching_dashboard'),
    
    # ANALYTICS SYSTEM (Feature 4)
    path('analytics/', views_analytics.analytics_dashboard, name='analytics_dashboard'),
    path('analytics/chart-data/', views_analytics.get_chart_data, name='get_chart_data'),
    path('analytics/export/', views_analytics.export_analytics_report, name='export_analytics_report'),
    
    # QR CODE SYSTEM (Feature 5)
    path('qr/donor/<int:donor_id>/', views_qrcode.generate_donor_qr, name='generate_donor_qr'),
    path('qr/certificate/<int:donation_id>/', views_qrcode.generate_certificate_qr, name='generate_certificate_qr'),
    path('qr/scanner/', views_qrcode.qr_scanner, name='qr_scanner'),
    path('qr/verify/', views_qrcode.verify_qr, name='verify_qr'),
    path('qr/download/<int:qr_id>/', views_qrcode.download_qr_image, name='download_qr_image'),
    path('qr/my-codes/', views_qrcode.my_qr_codes, name='my_qr_codes'),
    
    # CLEAR WELCOME FLAG
    path('clear-welcome/', views.clear_welcome_flag, name='clear_welcome_flag'),
    
    # API ENDPOINTS FOR AJAX
    path('api/donors/search/', api_views.donor_search_api, name='api_donor_search'),
    path('api/donor/<int:donor_id>/eligibility/', api_views.check_donor_eligibility_api, name='api_donor_eligibility'),
    path('api/inventory/', api_views.blood_inventory_api, name='api_inventory'),
    path('api/compatible-donors/', api_views.compatible_donors_api, name='api_compatible_donors'),
    path('api/request-statistics/', api_views.request_statistics_api, name='api_request_stats'),
    path('api/donor/<int:donor_id>/availability/', api_views.update_donor_availability_api, name='api_update_availability'),
    path('api/dashboard-stats/', api_views.dashboard_stats_api, name='api_dashboard_stats'),
]