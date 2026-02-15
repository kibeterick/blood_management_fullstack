import os

# Define the correct path for your Django app templates
base_dir = r'C:\Users\HP\blood_management_fullstack\core_blood_system'
template_dir = os.path.join(base_dir, 'templates', 'core_blood_system')

# Create the folders if they don't exist
os.makedirs(template_dir, exist_ok=True)

print(f"Folder ready: {template_dir}")

# Define the HTML code
html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Blood Management System</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #f0f2f5; margin: 0; padding: 20px; display: flex; flex-direction: column; align-items: center; }
        .container { max-width: 1100px; width: 100%; text-align: center; }
        
        /* Header Section */
        h1 { color: #d32f2f; margin-bottom: 5px; font-size: 2.5em; }
        .sub-header { color: #555; margin-bottom: 25px; }

        /* Image Section */
        .hero-image { 
            width: 100%; max-width: 600px; height: 300px; object-fit: cover; 
            border-radius: 15px; box-shadow: 0 10px 20px rgba(0,0,0,0.1); 
            margin-bottom: 40px; border: 5px solid white;
        }

        /* Forms Container */
        .forms-wrapper { display: flex; flex-wrap: wrap; gap: 30px; justify-content: center; width: 100%; }

        /* Card Styles */
        .card { 
            background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); 
            flex: 1; min-width: 320px; max-width: 450px; text-align: left; 
        }

        .card h3 { border-bottom: 2px solid #007bff; padding-bottom: 10px; margin-top: 0; color: #333; }

        /* Inputs */
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 6px; font-weight: bold; color: #444; font-size: 0.9em; }
        .form-group input, .form-group select { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 6px; box-sizing: border-box; }
        
        /* Buttons */
        .btn { width: 100%; padding: 12px; border: none; border-radius: 6px; font-size: 16px; cursor: pointer; font-weight: bold; transition: 0.3s; }
        .btn-login { background: #007bff; color: white; }
        .btn-login:hover { background: #0056b3; }
        .btn-register { background: #28a745; color: white; }
        .btn-register:hover { background: #218838; }

        .radio-group { display: flex; gap: 10px; margin-bottom: 15px; }
        .radio-group label { font-weight: normal; cursor: pointer; color: #555; }
    </style>
</head>
<body>
    <div class="container">
        <!-- WELCOME HEADER -->
        <h1>Welcome to Blood Management System</h1>
        <p class="sub-header">Efficient, Smart, and Life-Saving Solutions.</p>
        
        <!-- BLOOD DONATION IMAGE -->
        <img src="https://images.unsplash.com/photo-1615461066841-6e6437260336?auto=format&fit=crop&w=1000&q=80" alt="Blood Donation" class="hero-image">
        
        <!-- FORMS SECTION -->
        <div class="forms-wrapper">
            <!-- LOGIN FORM -->
            <div class="card">
                <h3>Existing User? Login</h3>
                <form method="POST">
                    {% csrf_token %}
                    <div class="radio-group">
                        <label><input type="radio" name="role" value="admin"> Admin</label>
                        <label><input type="radio" name="role" value="donor" checked> Donor</label>
                        <label><input type="radio" name="role" value="hospital"> Hospital</label>
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

            <!-- REGISTER FORM -->
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
</html>"""

# Write the file
file_path = os.path.join(template_dir, 'login.html')
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"File created at: {file_path}")