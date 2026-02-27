# 🎯 FOLLOW THESE STEPS - SIMPLE GUIDE

## STEP 1: Open PythonAnywhere
Go to: **https://www.pythonanywhere.com**

Login with your account: **kibeterick**

---

## STEP 2: Go to Web Apps
Click on the **"Web"** tab at the top

You'll see your web app: **kibeterick.pythonanywhere.com**

---

## STEP 3: Open Console
Scroll down and click the button that says:
**"Open Bash console here"**

A black terminal window will open.

---

## STEP 4: Run These Commands

Copy and paste these commands ONE AT A TIME:

### Command 1:
```bash
cd blood_management_fullstack
```
Press Enter. You should see the folder change.

### Command 2:
```bash
git pull origin main
```
Press Enter. You'll see it downloading the latest code from GitHub.

### Command 3:
```bash
touch /var/www/kibeterick_pythonanywhere_com_wsgi.py
```
Press Enter. This tells PythonAnywhere to reload.

---

## STEP 5: Close Console
Close the console window (click the X).

---

## STEP 6: Reload Web App
Go back to the **"Web"** tab.

Click the big green button that says: **"Reload kibeterick.pythonanywhere.com"**

Wait for it to finish (about 5-10 seconds).

---

## STEP 7: Test Your Site

### Open your site:
**https://kibeterick.pythonanywhere.com**

### Clear your browser cache:
Press **Ctrl + Shift + R** (or Cmd + Shift + R on Mac)

### Test as regular user (Kemei):
1. Login as Kemei
2. Go to "View Donors" 
3. You should NOT see "Actions" column ✅
4. Go to donation requests
5. You should NOT see "Actions" column ✅

### Test as admin:
1. Logout
2. Login as **admin** (password: **E38736434k**)
3. Go to "View Donors"
4. You SHOULD see "Actions" column with Edit/Delete buttons ✅
5. Go to donation requests
6. You SHOULD see "Actions" column with Approve/Reject buttons ✅

---

## ✅ DONE!

If you see the Actions column hidden for Kemei but visible for admin, everything is working perfectly!

---

## 🆘 IF CONSOLE DOESN'T WORK

If you can't paste in the console, try this alternative:

1. Go to **"Web"** tab
2. Scroll to **"Code"** section
3. Look for a button or link that says **"Pull latest code from Git"** or **"Update from GitHub"**
4. Click it
5. Then click the green **"Reload"** button

---

## 📞 WHAT YOU'LL SEE

### Regular Users (Kemei):
- Can VIEW donor list ✅
- Can VIEW donation requests ✅
- CANNOT see Actions column ✅
- CANNOT edit/delete/approve/reject ✅

### Admin (You):
- Can VIEW everything ✅
- Can see Actions column ✅
- Can edit/delete donors ✅
- Can approve/reject donations ✅

---

## 🎨 VISUAL CHANGES YOU'LL SEE

1. **"Blood Management System"** in bright red bar at the very top
2. **White text** in navigation (easy to read)
3. **Gold notification bell** 🔔
4. **Orange notification badge** with numbers
5. **No Actions column** for regular users
6. **Actions column visible** only for admin

---

That's it! Just follow steps 1-7 and you're done! 🎉
