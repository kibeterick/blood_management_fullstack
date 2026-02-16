# MySQL Database Setup Guide for Blood Management System

This guide will help you switch from SQLite to MySQL database.

## Why Switch to MySQL?

- **Better Performance**: MySQL handles concurrent users better than SQLite
- **Production Ready**: Most production servers use MySQL/PostgreSQL
- **Scalability**: Better for large datasets and multiple users
- **Railway Compatible**: Railway supports MySQL databases

---

## Step 1: Install MySQL Server

### Option A: Install MySQL Standalone
1. Download MySQL from: https://dev.mysql.com/downloads/mysql/
2. Run the installer
3. Set a root password during installation (remember this!)
4. Complete the installation

### Option B: Use XAMPP (Easier for Windows)
1. Download XAMPP from: https://www.apachefriends.org/
2. Install XAMPP
3. Start MySQL from XAMPP Control Panel
4. MySQL will run on port 3306

---

## Step 2: Install MySQL Python Driver

Open your terminal in the project folder and run:

```bash
# Activate virtual environment first
venv\Scripts\activate

# Install MySQL driver (try this first)
pip install mysqlclient

# If mysqlclient fails on Windows, use PyMySQL instead:
pip install pymysql
```

If using PyMySQL, add this to the top of `backend/settings.py`:
```python
import pymysql
pymysql.install_as_MySQLdb()
```

---

## Step 3: Create MySQL Database

### Using MySQL Command Line:
```sql
-- Login to MySQL
mysql -u root -p

-- Create database
CREATE DATABASE blood_management_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user (optional but recommended)
CREATE USER 'blood_admin'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON blood_management_db.* TO 'blood_admin'@'localhost';
FLUSH PRIVILEGES;

-- Exit
EXIT;
```

### Using phpMyAdmin (if using XAMPP):
1. Open http://localhost/phpmyadmin
2. Click "New" to create a database
3. Name it: `blood_management_db`
4. Collation: `utf8mb4_unicode_ci`
5. Click "Create"

---

## Step 4: Configure Django to Use MySQL

### Method 1: Using Environment Variables (Recommended)

Create a `.env` file in your project root:

```env
USE_MYSQL=True
MYSQL_DATABASE=blood_management_db
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_HOST=localhost
MYSQL_PORT=3306
```

Then install python-dotenv:
```bash
pip install python-dotenv
```

Add to `backend/settings.py` at the top:
```python
from dotenv import load_dotenv
load_dotenv()
```

### Method 2: Direct Configuration

Edit `backend/settings.py` and set:
```python
USE_MYSQL = True
```

Or modify the DATABASES section directly:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'blood_management_db',
        'USER': 'root',
        'PASSWORD': 'your_password',  # Your MySQL password
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}
```

---

## Step 5: Migrate Data to MySQL

```bash
# Run migrations to create tables in MySQL
python manage.py migrate

# Create a new superuser
python manage.py createsuperuser
```

---

## Step 6: Test the Connection

Run the test script:
```bash
python database.py
```

Or start the server:
```bash
python manage.py runserver
```

---

## Migrating Existing Data from SQLite to MySQL

If you have existing data in SQLite that you want to keep:

### Method 1: Using dumpdata/loaddata
```bash
# 1. Export data from SQLite
python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission --indent 4 > data_backup.json

# 2. Switch to MySQL configuration

# 3. Run migrations
python manage.py migrate

# 4. Load data into MySQL
python manage.py loaddata data_backup.json
```

### Method 2: Manual Export/Import
1. Export data from SQLite using Django admin
2. Switch to MySQL
3. Import data through Django admin

---

## Railway Deployment with MySQL

### 1. Add MySQL Plugin to Railway:
- Go to your Railway project
- Click "New" → "Database" → "Add MySQL"
- Railway will provide connection details

### 2. Set Environment Variables in Railway:
```
USE_MYSQL=True
MYSQL_DATABASE=railway
MYSQL_USER=root
MYSQL_PASSWORD=<from Railway>
MYSQL_HOST=<from Railway>
MYSQL_PORT=<from Railway>
```

### 3. Update requirements.txt:
```bash
pip freeze > requirements.txt
```

Make sure it includes:
```
mysqlclient==2.2.0
# or
pymysql==1.1.0
```

---

## Troubleshooting

### Error: "No module named 'MySQLdb'"
**Solution**: Install mysqlclient or pymysql
```bash
pip install mysqlclient
# or
pip install pymysql
```

### Error: "Can't connect to MySQL server"
**Solution**: 
- Check if MySQL is running
- Verify host, port, username, and password
- Check firewall settings

### Error: "Access denied for user"
**Solution**: 
- Verify MySQL username and password
- Grant proper privileges to the user

### Error: "Unknown database"
**Solution**: Create the database first using MySQL command line or phpMyAdmin

### Windows: mysqlclient installation fails
**Solution**: 
1. Download wheel file from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#mysqlclient
2. Install: `pip install mysqlclient‑1.4.6‑cp310‑cp310‑win_amd64.whl`
3. Or use PyMySQL instead: `pip install pymysql`

---

## Switching Back to SQLite

If you want to switch back to SQLite:

1. Set environment variable:
```
USE_MYSQL=False
```

Or in settings.py:
```python
USE_MYSQL = False
```

2. Run migrations:
```bash
python manage.py migrate
```

---

## Performance Tips

1. **Add Database Indexes**: Already configured in models
2. **Connection Pooling**: Configured with `conn_max_age=600`
3. **Query Optimization**: Use `select_related()` and `prefetch_related()`
4. **Database Backup**: Regular backups using mysqldump

```bash
# Backup MySQL database
mysqldump -u root -p blood_management_db > backup.sql

# Restore MySQL database
mysql -u root -p blood_management_db < backup.sql
```

---

## Summary

✅ Install MySQL Server
✅ Install mysqlclient or pymysql
✅ Create database: `blood_management_db`
✅ Configure Django settings
✅ Run migrations: `python manage.py migrate`
✅ Create superuser: `python manage.py createsuperuser`
✅ Test: `python manage.py runserver`

---

## Need Help?

Contact support:
- Email: support@bloodmanagement.com
- Phone: +254 700 123 456
