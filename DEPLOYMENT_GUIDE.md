# 🚀 Deployment Guide - Blood Management System

## Quick Start Options

Choose your deployment platform:
- [PythonAnywhere](#pythonanywhere-deployment) - FREE, easiest for beginners
- [Render](#render-deployment) - FREE, auto-deploy from GitHub
- [Railway](#railway-deployment) - FREE credits, modern platform
- [Local Network](#local-network-access) - Test on your phone via WiFi

---

## 📋 Pre-Deployment Checklist

Before deploying, make sure you have:

- [x] All code committed to GitHub
- [x] requirements.txt file
- [x] .env.example file (don't commit actual .env!)
- [x] Production settings configured
- [ ] Database ready (MySQL)
- [ ] Email credentials (optional but recommended)
- [ ] Domain name (optional)

---

## 🐍 PythonAnywhere Deployment (RECOMMENDED FOR BEGINNERS)

### Why PythonAnywhere?
- ✅ 100% FREE tier
- ✅ Easy Django deployment
- ✅ MySQL database included
- ✅ No credit card required
- ✅ Perfect for students/learning

### Step 1: Sign Up

1. Go to https://www.pythonanywhere.com
2. Click "Start running Python online in less than a minute!"
3. Create a free account (Beginner tier)
4. Verify your email

### Step 2: Upload Your Code

**Option A: From GitHub (Recommended)**

1. Open a Bash console in PythonAnywhere
2. Clone your repository:
```bash
git clone https://github.com/kibeterick/blood_management_fullstack.git
cd blood_management_fullstack
```

**Option B: Upload Files**
1. Use "Files" tab
2. Upload your project folder
3. Extract if zipped

### Step 3: Setup Virtual Environment

In the Bash console:

```bash
# Navigate to your project
cd blood_management_fullstack

# Create virtual environment
python3.10 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Setup Database

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

### Step 5: Configure Web App

1. Go to "Web" tab
2. Click "Add a new web app"
3. Choose "Manual configuration"
4. Select "Python 3.10"
5. Click through the wizard

### Step 6: Configure WSGI File

1. Click on WSGI configuration file link
2. Delete everything and replace with:

```python
import sys
import os

# Add your project directory to the sys.path
project_home = '/home/YOUR_USERNAME/blood_management_fullstack'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variable to tell Django where settings are
os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'

# Activate virtual environment
activate_this = '/home/YOUR_USERNAME/blood_management_fullstack/venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**Replace `YOUR_USERNAME` with your PythonAnywhere username!**

### Step 7: Configure Static Files

In the "Web" tab, scroll to "Static files" section:

| URL | Directory |
|-----|-----------|
| /static/ | /home/YOUR_USERNAME/blood_management_fullstack/staticfiles |
| /media/ | /home/YOUR_USERNAME/blood_management_fullstack/media |

### Step 8: Update Settings

Edit `backend/settings.py`:

```python
# Add your PythonAnywhere domain
ALLOWED_HOSTS = ['YOUR_USERNAME.pythonanywhere.com', 'localhost', '127.0.0.1']

# Set DEBUG to False for production
DEBUG = False
```

### Step 9: Reload and Test

1. Click the big green "Reload" button
2. Visit: `https://YOUR_USERNAME.pythonanywhere.com`
3. Test on your phone!

### Step 10: Setup MySQL Database (If needed)

1. Go to "Databases" tab
2. Create a new MySQL database
3. Note the database name, username, and password
4. Update your settings.py with these credentials

---

## 🎨 Render Deployment

### Why Render?
- ✅ FREE tier
- ✅ Auto-deploy from GitHub
- ✅ PostgreSQL database included
- ✅ HTTPS by default
- ✅ Modern platform

### Step 1: Prepare Your Code

1. Create `build.sh` in project root:

```bash
#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
```

2. Make it executable:
```bash
chmod +x build.sh
```

3. Update `backend/settings.py`:

```python
import dj_database_url

# Database
DATABASES = {
    'default': dj_database_url.config(
        default='mysql://user:password@localhost/dbname',
        conn_max_age=600
    )
}
```

### Step 2: Deploy to Render

1. Go to https://render.com
2. Sign up with GitHub
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Configure:
   - **Name:** blood-management-system
   - **Environment:** Python 3
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn backend.wsgi:application`
6. Add environment variables:
   - `SECRET_KEY`: Generate a new one
   - `DEBUG`: False
   - `DATABASE_URL`: (Render provides this)
7. Click "Create Web Service"

### Step 3: Add Database

1. Click "New +" → "PostgreSQL"
2. Name it and create
3. Copy the Internal Database URL
4. Add to your web service environment variables

### Step 4: Access Your Site

- Your site will be at: `https://blood-management-system.onrender.com`
- First deploy takes 5-10 minutes
- Auto-deploys on every GitHub push!

---

## 🚂 Railway Deployment

### Why Railway?
- ✅ $5 free credits monthly
- ✅ Easy GitHub integration
- ✅ MySQL/PostgreSQL support
- ✅ Fast deployment

### Step 1: Deploy

1. Go to https://railway.app
2. Sign up with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your repository
6. Railway auto-detects Django!

### Step 2: Add Database

1. Click "New" → "Database" → "Add MySQL"
2. Railway creates and links it automatically

### Step 3: Configure Environment

Add these variables in Railway dashboard:
- `SECRET_KEY`: Your secret key
- `DEBUG`: False
- `ALLOWED_HOSTS`: .railway.app
- `DATABASE_URL`: (Railway provides this)

### Step 4: Deploy

- Click "Deploy"
- Get your URL: `https://your-app.railway.app`
- Auto-deploys on GitHub push!

---

## 📱 Local Network Access (Test on Phone)

### For Testing Before Deployment

1. **Find Your Computer's IP Address:**

**Windows:**
```bash
ipconfig
```
Look for "IPv4 Address" (e.g., 192.168.1.100)

**Mac/Linux:**
```bash
ifconfig
```

2. **Update Django Settings:**

```python
# In backend/settings.py
ALLOWED_HOSTS = ['*']  # For testing only!
```

3. **Run Server:**

```bash
python manage.py runserver 0.0.0.0:8000
```

4. **Access from Phone:**

Make sure phone is on same WiFi, then visit:
```
http://YOUR_IP_ADDRESS:8000
```

Example: `http://192.168.1.100:8000`

---

## 🔒 Security Configuration

### Generate Secret Key

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### Environment Variables

Never commit sensitive data! Use `.env` file:

```bash
# Create .env file (don't commit this!)
SECRET_KEY=your-generated-secret-key
DEBUG=False
DB_PASSWORD=your-database-password
EMAIL_HOST_PASSWORD=your-email-password
```

### Update .gitignore

Make sure these are in `.gitignore`:
```
.env
*.pyc
__pycache__/
db.sqlite3
staticfiles/
media/
logs/
```

---

## 📧 Email Configuration

### Using Gmail

1. **Enable 2-Factor Authentication** on your Google account
2. **Generate App Password:**
   - Go to Google Account → Security
   - 2-Step Verification → App passwords
   - Generate password for "Mail"
3. **Add to settings:**

```python
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-16-char-app-password'
DEFAULT_FROM_EMAIL = 'Blood Management <your-email@gmail.com>'
```

---

## 📲 SMS Configuration (Optional)

### Using Twilio

1. Sign up at https://www.twilio.com/try-twilio
2. Get free trial credits
3. Get your credentials:
   - Account SID
   - Auth Token
   - Phone Number
4. Add to settings:

```python
TWILIO_ACCOUNT_SID = 'your_account_sid'
TWILIO_AUTH_TOKEN = 'your_auth_token'
TWILIO_PHONE_NUMBER = '+1234567890'
```

---

## 🎯 Post-Deployment Checklist

After deployment:

- [ ] Test homepage loads
- [ ] Test user registration
- [ ] Test login/logout
- [ ] Test donor registration
- [ ] Test blood request creation
- [ ] Test admin dashboard
- [ ] Test on mobile phone
- [ ] Test email notifications (if configured)
- [ ] Test SMS notifications (if configured)
- [ ] Create admin account
- [ ] Add sample data
- [ ] Share URL with users!

---

## 🐛 Troubleshooting

### Common Issues:

**1. Static files not loading**
```bash
python manage.py collectstatic --noinput
```

**2. Database connection error**
- Check database credentials
- Ensure database exists
- Check ALLOWED_HOSTS

**3. 500 Internal Server Error**
- Check error logs
- Set DEBUG=True temporarily to see error
- Check WSGI configuration

**4. CSS/JS not loading**
- Run collectstatic
- Check static file paths
- Clear browser cache

**5. Can't access from phone**
- Check firewall settings
- Ensure same WiFi network
- Use 0.0.0.0:8000 not localhost

---

## 📊 Monitoring & Maintenance

### Check Logs

**PythonAnywhere:**
- Web tab → Log files → Error log

**Render/Railway:**
- Dashboard → Logs tab

### Update Code

```bash
# Pull latest changes
git pull origin main

# Install new dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Reload (PythonAnywhere) or auto-deploys (Render/Railway)
```

---

## 🎉 Success!

Your Blood Management System is now live and accessible from anywhere!

**Share your URL:**
- PythonAnywhere: `https://YOUR_USERNAME.pythonanywhere.com`
- Render: `https://blood-management-system.onrender.com`
- Railway: `https://your-app.railway.app`

**Next Steps:**
1. Share URL with users
2. Create admin account
3. Add sample donors
4. Test all features
5. Configure email/SMS
6. Add custom domain (optional)
7. Monitor usage and feedback

---

## 📚 Additional Resources

- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/)
- [PythonAnywhere Help](https://help.pythonanywhere.com/)
- [Render Docs](https://render.com/docs)
- [Railway Docs](https://docs.railway.app/)
- [Twilio Python Quickstart](https://www.twilio.com/docs/sms/quickstart/python)

---

## 💡 Tips

1. **Start with PythonAnywhere** - Easiest for beginners
2. **Test locally first** - Use local network access
3. **Keep secrets secret** - Never commit .env file
4. **Monitor logs** - Check regularly for errors
5. **Backup database** - Regular backups are important
6. **Update regularly** - Keep dependencies updated
7. **Use HTTPS** - All platforms provide it free

---

**Need Help?** Check the troubleshooting section or review platform-specific documentation.

**Ready to deploy?** Start with PythonAnywhere - it's the easiest! 🚀
