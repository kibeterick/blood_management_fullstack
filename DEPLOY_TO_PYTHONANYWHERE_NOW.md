# Deploy to PythonAnywhere - Complete Guide

## What's Being Deployed

### New Features:
1. ✅ Animated blood bag visualization in admin dashboard
2. ✅ Blood inventory populated with 8 blood types
3. ✅ User Management link added to navigation menu
4. ✅ All bug fixes and improvements

## Step-by-Step Deployment

### Step 1: Open PythonAnywhere Bash Console
Go to: https://www.pythonanywhere.com/user/kibeterick/consoles/

Click "Bash" to open a new console or use an existing one.

### Step 2: Navigate to Project Directory
```bash
cd ~/blood_management_fullstack
```

### Step 3: Pull Latest Changes from GitHub
```bash
git pull origin main
```

Expected output:
```
Updating...
Fast-forward
 core_blood_system/templates/admin_dashboard_enhanced.html | XX ++
 core_blood_system/templates/base.html                     | XX ++
 populate_blood_inventory.py                               | XX ++
 ...
```

### Step 4: Activate Virtual Environment
```bash
source venv/bin/activate
```

You should see `(venv)` appear at the start of your command prompt.

### Step 5: Install Any New Dependencies (if needed)
```bash
pip install -r requirements.txt
```

### Step 6: Populate Blood Inventory
```bash
python populate_blood_inventory.py
```

Expected output:
```
==========================================
Blood Inventory Deployment Script
==========================================
Populating blood inventory...
--------------------------------------------------
✓ Created A+: 15 units
✓ Created A-: 8 units
✓ Created B+: 12 units
✓ Created B-: 6 units
✓ Created AB+: 10 units
✓ Created AB-: 5 units
✓ Created O+: 20 units
✓ Created O-: 7 units
--------------------------------------------------
Blood inventory populated successfully!
```

### Step 7: Collect Static Files
```bash
python manage.py collectstatic --noinput
```

This ensures all CSS and JavaScript files are properly deployed.

### Step 8: Reload Web App
```bash
touch /var/www/kibeterick_pythonanywhere_com_wsgi.py
```

This command reloads your web application with the new changes.

### Step 9: Verify Deployment
Wait 30 seconds, then visit:
https://kibeterick.pythonanywhere.com

Login with:
- Username: `admin`
- Password: `E38736434k`

## What to Check After Deployment

### 1. Blood Bag Visualization
- Go to Admin Dashboard
- Scroll to "Blood Inventory" section
- You should see 8 blood type cards with animated blood bags
- Blood should fill from bottom to top
- Wave animation on blood surface

### 2. User Management Access
- Click "Manage" in top navigation
- Click "All Users" (first option)
- You should see list of all registered users
- Statistics cards at top
- Search and filter options

### 3. Navigation Menu
- Check that "Manage" dropdown has "All Users" at the top
- Verify all other menu items still work

## Complete Command List (Copy & Paste)

```bash
cd ~/blood_management_fullstack
git pull origin main
source venv/bin/activate
python populate_blood_inventory.py
python manage.py collectstatic --noinput
touch /var/www/kibeterick_pythonanywhere_com_wsgi.py
```

## Troubleshooting

### If git pull fails with "uncommitted changes":
```bash
git stash
git pull origin main
```

### If blood inventory already exists:
The script will update existing records, so it's safe to run multiple times.

### If static files don't update:
```bash
python manage.py collectstatic --noinput --clear
touch /var/www/kibeterick_pythonanywhere_com_wsgi.py
```

### If you see "disk quota exceeded":
```bash
# Clean up cache files
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete

# Try again
python manage.py collectstatic --noinput
```

### If changes don't appear:
1. Wait 30-60 seconds after touching wsgi file
2. Hard refresh browser: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
3. Clear browser cache
4. Try incognito/private browsing mode

## Expected Results

### Blood Inventory Display:
```
Blood Inventory
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│   A+    │ │   A-    │ │   B+    │ │   B-    │
│  [bag]  │ │  [bag]  │ │  [bag]  │ │  [bag]  │
│ 15 units│ │ 8 units │ │ 12 units│ │ 6 units │
│Adequate │ │Adequate │ │Adequate │ │Adequate │
└─────────┘ └─────────┘ └─────────┘ └─────────┘

┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│  AB+    │ │  AB-    │ │   O+    │ │   O-    │
│  [bag]  │ │  [bag]  │ │  [bag]  │ │  [bag]  │
│ 10 units│ │ 5 units │ │ 20 units│ │ 7 units │
│Adequate │ │Adequate │ │Adequate │ │Adequate │
└─────────┘ └─────────┘ └─────────┘ └─────────┘
```

### Navigation Menu:
```
[Dashboard] [Manage ▼] [Reports ▼] [Compatibility] [Advanced Search]
              │
              └─> User Management
                  └─> All Users ← NEW!
                  
                  Donor Management
                  └─> Add New Donor
                  └─> All Donors
                  ...
```

## Deployment Checklist

- [ ] Opened PythonAnywhere Bash console
- [ ] Navigated to project directory
- [ ] Pulled latest changes from GitHub
- [ ] Activated virtual environment
- [ ] Populated blood inventory
- [ ] Collected static files
- [ ] Reloaded web app (touched wsgi file)
- [ ] Waited 30-60 seconds
- [ ] Visited live site
- [ ] Logged in as admin
- [ ] Verified blood bag visualization
- [ ] Verified user management access
- [ ] Tested navigation menu

## Support

If you encounter any issues:
1. Check the error log in PythonAnywhere
2. Verify all commands completed successfully
3. Make sure you're in the correct directory
4. Ensure virtual environment is activated
5. Check that GitHub has the latest code

## Summary

This deployment includes:
- Animated blood bag icons with fill levels
- 8 blood types with initial inventory
- User management link in navigation
- All previous features and fixes

Total deployment time: ~2-3 minutes

🚀 Ready to deploy!
