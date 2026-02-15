# Blood Management System

A comprehensive Django-based blood bank management system that connects blood donors with hospitals and patients in need.

## 🌟 Features

### Core Features
- **User Authentication**: Role-based access control (Admin, User, Donor)
- **Donor Management**: Register and track blood donors with availability status
- **Blood Request System**: Create and manage blood requests with urgency levels
- **Blood Inventory**: Track blood stock levels by type with low-stock alerts
- **Blood Compatibility Checker**: Find compatible donors for specific blood types
- **Export Functionality**: Export donor and request data to Excel and PDF formats
- **Dashboard**: Separate dashboards for admins and regular users
- **Search & Filter**: Advanced filtering for donors and blood requests

### Advanced Features ✨
- **📧 Email Notifications**: Automated emails for blood requests, status updates, and confirmations
- **🔍 Real-time AJAX Search**: Fast donor search with live filtering
- **📊 Advanced Analytics**: Comprehensive statistics and trends analysis
- **📜 Donation Certificates**: Generate beautiful PDF certificates for donors
- **📅 Appointment Scheduling**: Book and manage blood donation appointments
- **📱 SMS Notifications**: Twilio integration for urgent alerts (optional)
- **📱 Mobile Responsive**: Fully optimized for phones and tablets
- **🎯 Donor Eligibility Checker**: Automatic validation of donation eligibility
- **🔔 Low Stock Alerts**: Automatic notifications when blood inventory is low

## Technology Stack

- **Backend**: Django 5.2.8
- **Database**: SQLite (development), PostgreSQL ready
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Export Libraries**: openpyxl (Excel), reportlab (PDF)
- **Authentication**: Django built-in auth with custom user model
- **Notifications**: Django email backend, Twilio SMS (optional)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/kibeterick/blood_management_fullstack.git
cd blood_management_fullstack
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

7. Access the application at `http://127.0.0.1:8000/`

## 📧 Email Configuration

The system uses Django's email backend. For production, configure in `backend/settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'
```

## 📲 SMS Configuration (Optional)

To enable SMS notifications via Twilio:

1. Install Twilio SDK:
```bash
pip install twilio
```

2. Add to `backend/settings.py`:
```python
TWILIO_ACCOUNT_SID = 'your_account_sid'
TWILIO_AUTH_TOKEN = 'your_auth_token'
TWILIO_PHONE_NUMBER = '+1234567890'
```

3. Sign up at [Twilio](https://www.twilio.com/try-twilio)

## Project Structure

```
blood_management_fullstack/
├── backend/                 # Django project settings
├── core_blood_system/       # Main application
│   ├── models.py           # Database models
│   ├── views.py            # View functions
│   ├── forms.py            # Django forms
│   ├── urls.py             # URL routing
│   ├── notifications.py    # Email notification system
│   ├── sms_notifications.py # SMS notification system
│   ├── certificates.py     # PDF certificate generator
│   ├── appointments.py     # Appointment scheduling
│   ├── analytics.py        # Advanced analytics
│   ├── utils.py            # Utility functions
│   ├── api_views.py        # AJAX API endpoints
│   ├── templates/          # HTML templates
│   └── static/             # CSS, JS, images
├── manage.py               # Django management script
└── requirements.txt        # Python dependencies
```

## Models

- **CustomUser**: Extended Django user with role, blood type, and contact info
- **Donor**: Blood donor information with availability tracking
- **BloodRequest**: Patient/hospital blood requests with status tracking
- **BloodDonation**: Records of blood donations
- **BloodInventory**: Blood stock management by type
- **DonationAppointment**: Scheduled donation appointments

## API Endpoints

The system includes RESTful API endpoints for AJAX operations:

- `/api/donors/search/` - Real-time donor search
- `/api/donor/<id>/eligibility/` - Check donor eligibility
- `/api/inventory/` - Get blood inventory status
- `/api/compatible-donors/` - Find compatible donors
- `/api/request-statistics/` - Get request statistics
- `/api/dashboard-stats/` - Dashboard analytics data

## Usage

### For Administrators
- Access admin dashboard at `/admin-dashboard/`
- Manage donors, requests, and inventory
- View statistics and reports
- Export data to Excel/PDF
- Schedule appointments
- Send notifications

### For Regular Users
- Register and login at `/register/` and `/login/`
- Create blood requests at `/request-blood/`
- View personal requests at `/blood-requests/`
- Check blood compatibility at `/compatibility/`
- Schedule donation appointments

### For Donors
- Register as a donor at `/register-donor/`
- Update availability status
- Track donation history
- Download donation certificates
- Manage appointments

## Key Features Explained

### 📧 Email Notifications
- Automatic emails when blood requests are created
- Status update notifications
- Donor registration confirmations
- Low stock alerts to administrators
- Appointment reminders

### 📜 Donation Certificates
- Professional PDF certificates for each donation
- Includes donor name, blood type, date, and location
- Unique certificate numbers
- Downloadable and printable

### 📅 Appointment System
- Schedule donations in advance
- Time slot management
- Automatic reminders 24 hours before
- Conflict detection
- Cancellation with 24-hour notice

### 🔍 Advanced Search
- Real-time AJAX search
- Filter by blood type, availability, location
- Instant results without page reload
- Mobile-optimized interface

### 📊 Analytics Dashboard
- Donation trends and statistics
- Blood type distribution
- Request fulfillment rates
- Donor engagement metrics
- Low stock warnings

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Contact

For questions or support, please contact: kibeterick57@gmail.com

## Acknowledgments

- Built with Django and Bootstrap
- Icons by Bootstrap Icons
- PDF generation by ReportLab
- SMS by Twilio
