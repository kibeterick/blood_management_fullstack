# PythonAnywhere Deployment Checklist

## Before You Start
- [ ] All changes committed to GitHub ✅ (Already done!)
- [ ] You have PythonAnywhere login credentials
- [ ] You know your admin password: E38736434k

## Deployment Steps

### 1. Access PythonAnywhere Console
- [ ] Go to https://www.pythonanywhere.com
- [ ] Login to your account
- [ ] Click "Consoles" tab at the top
- [ ] Click "Bash" to open console

### 2. Navigate to Project
- [ ] Type: `cd ~/blood_management_fullstack`
- [ ] Press Enter
- [ ] You should see the path change

### 3. Pull Latest Code
- [ ] Type: `git pull origin main`
- [ ] Press Enter
- [ ] Wait for download to complete
- [ ] Should say "Already up to date" or show files updated

### 4. Activate Virtual Environment
- [ ] Type: `source venv/bin/activate`
- [ ] Press Enter
- [ ] You should see `(venv)` appear before your prompt

### 5. Populate Blood Inventory
- [ ] Type: `python populate_blood_inventory.py`
- [ ] Press Enter
- [ ] Wait for script to complete
- [ ] Should show "✓ Created" for each blood type

### 6. Collect Static Files
- [ ] Type: `python manage.py collectstatic --noinput`
- [ ] Press Enter
- [ ] Wait for files to be collected
- [ ] Should show number of files copied

### 7. Reload Web App
- [ ] Type: `touch /var/www/kibeterick_pythonanywhere_com_wsgi.py`
- [ ] Press Enter
- [ ] Command completes instantly (no output)

### 8. Wait for Reload
- [ ] Wait 30-60 seconds
- [ ] Server is reloading in background

### 9. Test Your Website
- [ ] Open: https://kibeterick.pythonanywhere.com
- [ ] Click "Open" if Kiro asks permission
- [ ] Login with: admin / E38736434k

### 10. Verify Blood Inventory
- [ ] Go to Admin Dashboard
- [ ] Scroll down to "Blood Inventory" section
- [ ] Check for 8 blood type cards
- [ ] Verify blood bags are animated
- [ ] Blood should fill from bottom to top

### 11. Verify User Management
- [ ] Click "Manage" in top navigation
- [ ] Click "All Users" (first option)
- [ ] Should see list of 6 users
- [ ] Check statistics cards at top
- [ ] Try search or filter

### 12. Test Navigation
- [ ] Check all menu items work
- [ ] Verify "Manage" dropdown has "All Users"
- [ ] Test other features

## Troubleshooting

### If git pull fails:
```bash
git stash
git pull origin main
```

### If disk quota exceeded:
```bash
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
python manage.py collectstatic --noinput
```

### If changes don't appear:
- Wait another 30 seconds
- Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
- Try incognito/private browsing mode
- Clear browser cache

### If blood inventory is empty:
```bash
python populate_blood_inventory.py
touch /var/www/kibeterick_pythonanywhere_com_wsgi.py
```

## Success Criteria

✅ Website loads without errors
✅ Can login as admin
✅ Blood inventory shows 8 animated blood bags
✅ "Manage" → "All Users" shows user list
✅ All navigation links work
✅ No error messages

## Completion

- [ ] All features verified
- [ ] No errors encountered
- [ ] Website working smoothly
- [ ] Deployment successful! 🎉

## Time Estimate
Total deployment time: 3-5 minutes

## Support
If you encounter issues:
1. Check PythonAnywhere error logs
2. Verify all commands completed successfully
3. Make sure you're in correct directory
4. Ensure virtual environment is activated

---

**Note**: The dialog asking "Do you want Kiro to open the external website?" is just a security feature. Click "Open" to proceed to your website.
