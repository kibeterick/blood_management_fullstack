"""
Database Configuration Helper for Blood Management System

This file helps configure MySQL database connection.
Follow the instructions below to set up MySQL for your project.

SETUP INSTRUCTIONS:
===================

1. Install MySQL Server:
   - Download from: https://dev.mysql.com/downloads/mysql/
   - Or use XAMPP/WAMP which includes MySQL

2. Install MySQL Python connector:
   pip install mysqlclient
   
   If mysqlclient fails on Windows, try:
   pip install pymysql
   
3. Create a MySQL database:
   - Open MySQL command line or phpMyAdmin
   - Run: CREATE DATABASE blood_management_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   
4. Create a MySQL user (optional but recommended):
   CREATE USER 'blood_admin'@'localhost' IDENTIFIED BY 'your_password_here';
   GRANT ALL PRIVILEGES ON blood_management_db.* TO 'blood_admin'@'localhost';
   FLUSH PRIVILEGES;

5. Update backend/settings.py DATABASES configuration:
   Replace the SQLite configuration with MySQL configuration (see below)

6. Run migrations:
   python manage.py migrate
   
7. Create superuser:
   python manage.py createsuperuser

"""

# MySQL Database Configuration
# Copy this to your backend/settings.py file

MYSQL_DATABASE_CONFIG = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'blood_management_db',  # Your database name
        'USER': 'root',  # Your MySQL username (default is 'root')
        'PASSWORD': '',  # Your MySQL password (leave empty if no password)
        'HOST': 'localhost',  # Database host (usually 'localhost')
        'PORT': '3306',  # MySQL port (default is 3306)
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Alternative: Using PyMySQL (if mysqlclient doesn't work)
# Add this at the top of backend/settings.py:
"""
import pymysql
pymysql.install_as_MySQLdb()
"""

# For Railway deployment with MySQL:
RAILWAY_MYSQL_CONFIG = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'railway',  # Railway database name
        'USER': 'root',  # Railway MySQL user
        'PASSWORD': 'your_railway_mysql_password',  # From Railway variables
        'HOST': 'your_railway_mysql_host',  # From Railway variables
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}

# Connection test function
def test_mysql_connection():
    """Test MySQL connection"""
    import pymysql
    
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',  # Your password
            database='blood_management_db',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        print("✅ MySQL connection successful!")
        print(f"Server version: {connection.get_server_info()}")
        connection.close()
        return True
    except Exception as e:
        print(f"❌ MySQL connection failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing MySQL connection...")
    test_mysql_connection()
