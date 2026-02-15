import os

# --- 1. UPDATE VIEWS.PY ---
views_code = '''from django.shortcuts import render, redirect
from django.db.models import Count
from .models import Donor, Donation, Recipient
from datetime import date, timedelta

def login_view(request):
    """Fig 5.1: Login Page Logic"""
    if request.method == 'POST':
        role = request.POST.get('role')
        if role == 'admin':
            return redirect('/admin/')
        # All other roles (Donor, Hospital, Recipient, Org) go to Dashboard
        return redirect('/dashboard/')
    return render(request, 'core_blood_system/login.html')

def dashboard(request):
    """Fig 5.2: The Main Dashboard with AI"""
    # 1. Calculate Stock Levels per Type
    stock_data = Donation.objects.filter(status='Approved').values('blood_type').annotate(count=Count('id')).order_by('blood_type')
    stock_dict = {item['blood_type']: item['count'] for item in stock_data}
    
    # 2. Get Pending Requests
    pending_requests = Recipient.objects.filter(status='Pending').order_by('-created_at')[:5]
    
    # 3. Get Expiring Units (TC-03)
    threshold = date.today() + timedelta(days=7)
    expiring_units = Donation.objects.filter(status='Approved', expiry_date__lte=threshold).order_by('expiry_date')
    
    # 4. AI System Insights
    ai_insights = []
    for b_type, count in stock_dict.items():
        if count < 2:
            ai_insights.append({"type": "critical", "msg": f"CRITICAL: {b_type} stock is dangerously low."})
        elif count < 5:
            ai_insights.append({"type": "warning", "msg": f"PREDICTION: {b_type} stock is depleting."})
    
    if not ai_insights:
        ai_insights.append({"type": "success", "msg": "System Status: All stocks optimal."})

    context = {
        'total_donors': Donor.objects.count(),
        'total_stock': Donation.objects.filter(status='Approved').count(),
        'stock_dict': stock_dict,
        'pending_requests': pending_requests,
        'expiring_units': expiring_units,
        'ai_insights': ai_insights,
    }
    return render(request, 'core_blood_system/dashboard.html', context)

def issue_blood(request, recipient_id):
    """Fig 5.5: Interface to issue blood"""
    recipient = Recipient.objects.get(id=recipient_id)
    compatible_units = recipient.get_compatible_units()
    
    if request.method == 'POST':
        unit_id = request.POST.get('unit_id')
        if unit_id:
            unit = Donation.objects.get(id=unit_id)
            recipient.blood_unit = unit
            recipient.save()
            return render(request, 'core_blood_system/success.html', {'recipient': recipient})
            
    context = {'recipient': recipient, 'compatible_units': compatible_units}
    return render(request, 'core_blood_system/issue_blood.html', context)
'''

# Define paths
views_path = r'C:\Users\HP\blood_management_fullstack\core_blood_system\views.py'

# Write views.py
with open(views_path, 'w', encoding='utf-8') as f:
    f.write(views_code)

print("1. views.py updated successfully.")

# --- 2. UPDATE LOGIN.HTML ---
login_html = '''<!DOCTYPE html>
<html>
<head>
    <title>Blood Management System</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f0f2f5; margin: 0; padding: 20px; display: flex; flex-direction: column; align-items: center; min-height: 100vh; }
        .container { max-width: 1200px; width: 100%; text-align: center; }
        
        /* Header Section */
        h1 { color: #d32f2f; margin-bottom: 5px; font-size: 2.5em; }
        .sub-header { color: #555; margin-bottom: 25px; font-size: 1.1em; }

        /* Image Section */
        .hero-image { 
            width: 100%; max-width: 700px; height: 350px; object-fit: cover; 
            border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.15); 
            margin-bottom: 40px; border: 5px solid white; background-color: #e0e0e0;
        }

        /* Forms Container */
        .forms-wrapper { display: flex; flex-wrap: wrap; gap: 40px; justify-content: center; width: 100%; }

        /* Card Styles */
        .card { 
            background: white; padding: 35px; border-radius: 12px; 
            box-shadow: 0 4px 15px rgba(0,0,0,0.05); 
            flex: 1; min-width: 300px; max-width: 450px; text-align: left; 
            border-top: 5px solid #d32f2f;
        }

        .card h3 { margin-top: 0; color: #333; font-size: 1.3em; margin-bottom: 20px; border-bottom: 1px solid #eee; padding-bottom: 10px; }

        /* Inputs */
        .form-group { margin-bottom: 18px; }
        .form-group label { display: block; margin-bottom: 8px; font-weight: 600; color: #444; font-size: 0.9em; }
        .form-group input, .form-group select { width: 100%; padding: 12px; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box; transition: 0.3s; }
        .form-group input:focus { border-color: #d32f2f; outline: none; box-shadow: 0 0 5px rgba(211, 47, 47, 0.1); }
        
        /* Buttons */
        .btn { width: 100%; padding: 14px; border: none; border-radius: 6px; font-size: 16px; cursor: pointer; font-weight: bold; transition: 0.3s; text-transform: uppercase; letter-spacing: 1px; }
        .btn-login { background: #007bff; color: white; }
        .btn-login:hover { background: #0056b3; transform: translateY(-2px); }
        
        .btn-register { background: #28a745; color: white; }
        .btn-register:hover { background: #218838; transform: translateY(-2px); }

        .radio-group { display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }
        .radio-group label { font-size: 0.9em; cursor: pointer; display: flex; align-items: center; gap: 5px; color: #555; }
        .radio-group input[type="radio"] { accent-color: #d32f2f; width: 18px; height: 18px; }
    </style>
</head>
<body>
    <div class="container">
        <!-- WELCOME HEADER -->
        <h1>Welcome to Blood Management System</h1>
        <p class="sub-header">Connecting Lives through Compassionate Donation.</p>
        
        <!-- BLOOD DONATION IMAGE -->
        <img src="https://images.unsplash.com/photo-15953858126066-fd5c811775f?auto=format&fit=crop&w=1200&q=80" alt="Parent donating blood" class="hero-image">
        
        <!-- FORMS SECTION -->
        <div class="forms-wrapper">
            <!-- LOGIN CARD -->
            <div class="card">
                <h3>Existing User? Login</h3>
                <form method="POST">
                    {% csrf_token %}
                    
                    <div class="radio-group">
                        <label><input type="radio" name="role" value="admin"> Admin</label>
                        <label><input type="radio" name="role" value="donor" checked> Donor</label>
                        <label><input type="radio" name="role" value="hospital"> Hospital</label>
                        <label><input type="radio" name="role" value="recipient"> Recipient</label>
                        <label><input type="radio" name="role" value="org"> Organisation</label>
                    </div>

                    <div class="form-group">
                        <label>Email Address</label>
                        <input type="email" required placeholder="user@example.com">
                    </div>

                    <div class="form-group">
                        <label>Password</label>
                        <input type="password" required placeholder="********">
                    </div>

                    <button type="submit" class="btn btn-login">Login Now</button>
                </form>
            </div>

            <!-- REGISTER CARD -->
            <div class="card">
                <h3>New Donor? Register</h3>
                <form action="/admin/core_blood_system/donor/add/" method="GET">
                    <div class="form-group">
                        <label>Full Name</label>
                        <input type="text" placeholder="John Doe" required>
                    </div>

                    <div class="form-group">
                        <label>Blood Type</label>
                        <select>
                            <option value="O+">O+</option>
                            <option value="O-">O-</option>
                            <option value="A+">A+</option>
                            <option value="A-">A-</option>
                            <option value="B+">B+</option>
                            <option value="B-">B-</option>
                            <option value="AB+">AB+</option>
                            <option value="AB-">AB-</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label>Email</label>
                        <input type="email" placeholder="donor@example.com" required>
                    </div>

                    <button type="submit" class="btn btn-register">Create Account</button>
                </form>
            </div>
        </div>
    </div>
</body>
</html>'''

# Define path
login_path = r'C:\Users\HP\blood_management_fullstack\core_blood_system\templates\core_blood_system\login.html'

# Create folder if not exists
os.makedirs(os.path.dirname(login_path), exist_ok=True)

# Write login.html
with open(login_path, 'w', encoding='utf-8') as f:
    f.write(login_html)

print("2. login.html created successfully.")
print("\nAll files updated! Please refresh your browser.")