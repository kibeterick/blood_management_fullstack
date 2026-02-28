"""
Preservation Property Tests for Navigation Template Syntax Fix

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7**

Property 2: Preservation - Navigation and Template Functionality

These tests verify that all navigation functionality is preserved after fixing
the template syntax error on line 611. They test that the fix does NOT affect
any other template rendering, navigation logic, or user interface behavior.

IMPORTANT: These tests follow observation-first methodology.
Since the unfixed code has a syntax error preventing rendering, these tests
document the EXPECTED preserved behaviors based on the template structure.

These tests will be run AFTER the fix to verify preservation.
"""

import os
import re
from typing import List, Tuple


def read_template() -> str:
    """Read the base.html template file."""
    template_path = os.path.join('core_blood_system', 'templates', 'base.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()


def extract_nav_items(content: str, section_marker: str) -> List[str]:
    """Extract navigation items from a specific section of the template."""
    items = []
    # Find all href patterns in nav links
    href_pattern = r'href="{% url \'([^\']+)\' %}"'
    matches = re.findall(href_pattern, content)
    return matches


def test_admin_navigation_menu_items_preserved():
    """
    Property 2.1: Admin Navigation Preservation
    
    Validates: Requirement 3.1
    
    For any authenticated admin user, the navigation SHALL display all admin
    menu items including Dashboard, Donors, Patients, Donations, Analytics,
    Reports, Compatibility, and Advanced Search.
    
    This test verifies the template structure contains all expected admin menu items.
    """
    print("\n" + "="*70)
    print("TEST 1: Admin Navigation Menu Items Preservation")
    print("="*70)
    
    content = read_template()
    
    # Expected admin navigation items based on template structure
    expected_admin_items = [
        'admin_dashboard',  # Dashboard
        'notification_center',  # Notifications
        'admin_appointments_list',  # Appointments - All Appointments
     