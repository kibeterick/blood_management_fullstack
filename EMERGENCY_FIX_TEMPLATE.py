#!/usr/bin/env python3
"""
Emergency fix script - Run this in PythonAnywhere bash console
This will directly fix the template file on the server
"""

# The corrected template content
template_fix = """                                        <div class="d-flex justify-content-between align-items-start mb-3">
                                            <h5 class="card-title mb-0">
                                                {{ appointment.appointment_date|date:"F d, Y" }}
                                            </h5>
                                            {% if appointment.status == 'confirmed' %}
                                            <span class="badge bg-success">
                                            {% else %}
                                            <span class="badge bg-warning">
                                            {% endif %}
                                                {{ appointment.get_status_display }}
                                            </span>
                                        </div>"""

import os
import sys

def main():
    template_path = "/home/kibeterick/blood_management_fullstack/core_blood_system/templates/appointments/my_appointments.html"
    
    print("=" * 60)
    print("EMERGENCY TEMPLATE FIX")
    print("=" * 60)
    
    if not os.path.exists(template_path):
        print(f"ERROR: Template file not found at {template_path}")
        sys.exit(1)
    
    # Read the current template
    with open(template_path, 'r') as f:
        content = f.read()
    
    # Find and replace the problematic line
    old_pattern = '<span class="badge bg-{{ appointment.status == \'confirmed\' and \'success\' or \'warning\' }}">'
    
    if old_pattern in content:
        print("✓ Found the problematic syntax")
        
        # Replace the entire section
        old_section = """                                        <div class="d-flex justify-content-between align-items-start mb-3">
                                            <h5 class="card-title mb-0">
                                                {{ appointment.appointment_date|date:"F d, Y" }}
                                            </h5>
                                            <span class="badge bg-{{ appointment.status == 'confirmed' and 'success' or 'warning' }}">
                                                {{ appointment.get_status_display }}
                                            </span>
                                        </div>"""
        
        content = content.replace(old_section, template_fix)
        
        # Write the fixed content
        with open(template_path, 'w') as f:
            f.write(content)
        
        print("✓ Template fixed successfully!")
        print("\nNow run these commands:")
        print("1. python manage.py collectstatic --noinput")
        print("2. touch /var/www/kibeterick_pythonanywhere_com_wsgi.py")
        print("3. Go to Web tab and click 'Reload'")
        
    else:
        print("✗ Problematic syntax not found - template may already be fixed")
        print("Try clearing Django's cache and reloading the web app")

if __name__ == "__main__":
    main()
