# Blood Management System

A comprehensive Django-based blood bank management system that connects blood donors with hospitals and patients in need.

## Features

- **User Authentication**: Role-based access control (Admin, User, Donor)
- **Donor Management**: Register and track blood donors with availability status
- **Blood Request System**: Create and manage blood requests with urgency levels
- **Blood Inventory**: Track blood stock levels by type with low-stock alerts
- **Blood Compatibility Checker**: Find compatible donors for specific blood types
- **Export Functionality**: Export donor and request data to Excel and PDF formats
- **Dashboard**: Separate dashboards for admins and regular users
- **Search & Filter**: Advanced filtering for donors and blood requests

## Technology Stack

- **Backend**: Django 5.2.8
- **Database**: SQLite (development), PostgreSQL ready
- **Frontend**: HTML, CSS, JavaScript
- **Export Libraries**: openpyxl (Excel), reportlab (PDF)
- **Authentication**: Django built-in auth with custom user model

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

## Project Structure

```
blood_management_fullstack/
├── backend/                 # Django project settings
├── core_blood_system/       # Main application
│   ├── models.py           # Database models
│   ├── views.py            # View functions
│   ├── forms.py            # Django forms
│   ├── urls.py             # URL routing
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

## Usage

### For Administrators
- Access admin dashboard at `/admin-dashboard/`
- Manage donors, requests, and inventory
- View statistics and reports
- Export data to Excel/PDF

### For Regular Users
- Register and login at `/register/` and `/login/`
- Create blood requests at `/request-blood/`
- View personal requests at `/blood-requests/`
- Check blood compatibility at `/compatibility/`

### For Donors
- Register as a donor at `/register-donor/`
- Update availability status
- Track donation history

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Contact

For questions or support, please contact: kibeterick57@gmail.com
