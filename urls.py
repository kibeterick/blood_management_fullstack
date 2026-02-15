from django.contrib import admin
from django.urls import path
from core_blood_system import views

urlpatterns = [
    # This is the "frame" to view users
    path('admin/', admin.site.urls), 
    
    # Your custom landing page
    path('', views.landing_page, name='home'),
    
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
]