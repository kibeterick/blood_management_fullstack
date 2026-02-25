# Deploy Blood Inventory Update to PythonAnywhere

## Quick Deployment Steps

### Step 1: Open PythonAnywhere Bash Console
Go to: https://www.pythonanywhere.com/user/kibeterick/consoles/

### Step 2: Navigate to Project and Pull Changes
```bash
cd ~/blood_management_fullstack
git pull origin main
```

### Step 3: Activate Virtual Environment
```bash
source venv/bin/activate
```

### Step 4: Populate Blood Inventory
```bash
python populate_blood_inventory.py
```

Expected output:
```
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

### Step 5: Reload Web App
```bash
touch /var/www/kibeterick_pythonanywhere_com_wsgi.py
```

### Step 6: Test the Changes
1. Go to: https://kibeterick.pythonanywhere.com/login/
2. Login with:
   - Username: `admin`
   - Password: `E38736434k`
3. You should see the blood bag visualizations on the admin dashboard!

## What You'll See

The Blood Inventory section now displays:
- 8 blood type cards (A+, A-, B+, B-, AB+, AB-, O+, O-)
- Each card has an animated blood bag icon
- Blood level fills from bottom to top based on available units
- Wave animation on the blood surface
- Unit count displayed below each bag
- Status badges (green "Adequate" or pulsing red "Low Stock!")

## Troubleshooting

### If git pull fails with conflicts:
```bash
cd ~/blood_management_fullstack
git stash
git pull origin main
```

### If populate script fails:
```bash
# Check if you're in the right directory
pwd
# Should show: /home/kibeterick/blood_management_fullstack

# Make sure virtual environment is activated
source venv/bin/activate

# Try running the script again
python populate_blood_inventory.py
```

### If blood bags don't show:
1. Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)
2. Check if inventory data exists by running in Django shell:
```bash
python manage.py shell
```
Then in the shell:
```python
from core_blood_system.models import BloodInventory
print(BloodInventory.objects.all())
exit()
```

## All Commands in One Block (Copy & Paste)
```bash
cd ~/blood_management_fullstack
git pull origin main
source venv/bin/activate
python populate_blood_inventory.py
touch /var/www/kibeterick_pythonanywhere_com_wsgi.py
```

That's it! Your blood inventory visualization is now live! 🩸
