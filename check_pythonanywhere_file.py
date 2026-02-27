"""
Script to verify if base.html was updated on PythonAnywhere
Run this on PythonAnywhere console
"""

# Check the file size and a specific line
file_path = '/home/kibeterick/blood_management_fullstack/core_blood_system/templates/base.html'

try:
    with open(file_path, 'r') as f:
        lines = f.readlines()
        total_lines = len(lines)
        
    print(f"Total lines in base.html: {total_lines}")
    print(f"\nExpected: 682 lines")
    print(f"Status: {'✓ CORRECT' if total_lines == 682 else '✗ WRONG - File not updated!'}")
    
    # Check for the admin dropdown comment
    file_content = ''.join(lines)
    if 'Admin Dropdown (Right Side)' in file_content:
        print("\n✓ Admin dropdown code found!")
    else:
        print("\n✗ Admin dropdown code NOT found - file was not updated properly")
        
    # Show first 5 lines
    print("\nFirst 5 lines of file:")
    for i, line in enumerate(lines[:5], 1):
        print(f"{i}: {line.rstrip()}")
        
except Exception as e:
    print(f"Error: {e}")
