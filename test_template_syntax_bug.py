"""
Bug Condition Exploration Test for Navigation Template Syntax Fix

**Validates: Requirements 2.1, 2.2, 2.3**

Property 1: Fault Condition - Template Syntax Error on Line 611

This test confirms the template syntax error exists on line 611 of base.html.

CRITICAL: This test MUST FAIL on unfixed code - failure confirms the bug exists.
When the bug is fixed, this test will PASS, confirming the expected behavior.
"""

import os
import sys


def test_line_611_contains_buggy_syntax():
    """
    Verify line 610 (0-indexed) / line 611 (1-indexed) of base.html contains the malformed template tag.
    
    On UNFIXED code: This test will FAIL (confirms bug exists)
    On FIXED code: This test will PASS (confirms bug is fixed)
    """
    print("\n" + "="*70)
    print("TEST 1: Checking if line 610 (line 611 in editor) contains buggy syntax")
    print("="*70)
    
    # Read the base.html file
    template_path = os.path.join('core_blood_system', 'templates', 'base.html')
    
    if not os.path.exists(template_path):
        print(f"ERROR: Template file not found at {template_path}")
        return False
    
    with open(template_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Line 611 in editor (1-indexed) = Line 610 in array (0-indexed)
    line_index = 609  # 0-indexed
    line_display = 610  # What we show to user (matches file line numbers starting from 1)
    
    if len(lines) <= line_index:
        print(f"ERROR: File has only {len(lines)} lines, cannot check line {line_display}")
        return False
    
    line_content = lines[line_index]
    
    print(f"\nLine {line_display} content: {repr(line_content)}")
    
    buggy_syntax = '{% endif %} %}'
    correct_syntax = '{% endif %}'
    
    # On unfixed code, this should contain the buggy syntax
    # On fixed code, this should NOT contain the buggy syntax
    if buggy_syntax in line_content:
        print(f"\n❌ FAIL: Line {line_display} contains the buggy syntax '{buggy_syntax}'")
        print(f"   This confirms the bug EXISTS on line {line_display}.")
        print(f"   Expected: '{correct_syntax}'")
        return False
    else:
        print(f"\n✓ PASS: Line {line_display} does NOT contain the buggy syntax")
        print(f"   The bug has been FIXED!")
        return True


def test_template_syntax_validation():
    """
    Verify the template syntax by checking for the malformed tag pattern.
    
    On UNFIXED code: This test will FAIL (confirms bug exists)
    On FIXED code: This test will PASS (confirms bug is fixed)
    """
    print("\n" + "="*70)
    print("TEST 2: Validating template syntax structure")
    print("="*70)
    
    # Read the base.html file
    template_path = os.path.join('core_blood_system', 'templates', 'base.html')
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for the specific malformed pattern
    buggy_pattern = '{% endif %} %}'
    
    if buggy_pattern in content:
        # Find all occurrences
        lines = content.split('\n')
        occurrences = []
        for i, line in enumerate(lines, 1):
            if buggy_pattern in line:
                occurrences.append((i, line.strip()))
        
        print(f"\n❌ FAIL: Found {len(occurrences)} occurrence(s) of malformed tag '{buggy_pattern}'")
        for line_num, line_content in occurrences:
            print(f"   Line {line_num}: {line_content}")
        print(f"\n   This confirms the template syntax bug EXISTS.")
        return False
    else:
        print(f"\n✓ PASS: No malformed tags found")
        print(f"   Template syntax is correct!")
        return True


def test_endif_tag_balance():
    """
    Verify that all {% if %} tags have matching {% endif %} tags.
    
    This is a sanity check to ensure template structure is valid.
    """
    print("\n" + "="*70)
    print("TEST 3: Checking if/endif tag balance")
    print("="*70)
    
    # Read the base.html file
    template_path = os.path.join('core_blood_system', 'templates', 'base.html')
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count if/endif tags (simplified check)
    if_count = content.count('{% if ')
    endif_count = content.count('{% endif %}')
    
    if_tag = '{% if %}'
    endif_tag = '{% endif %}'
    
    print(f"\n{if_tag} tags: {if_count}")
    print(f"{endif_tag} tags: {endif_count}")
    
    if if_count == endif_count:
        print(f"\n✓ PASS: Tag balance is correct ({if_count} if tags, {endif_count} endif tags)")
        return True
    else:
        print(f"\n❌ FAIL: Tag imbalance detected!")
        print(f"   Expected {if_count} endif tags, found {endif_count}")
        return False


def main():
    """Run all bug condition exploration tests."""
    print("\n" + "="*70)
    print("BUG CONDITION EXPLORATION TEST")
    print("Navigation Template Syntax Fix - Line 610 (Editor Line 611)")
    print("="*70)
    print("\nThis test suite confirms the template syntax error exists.")
    print("EXPECTED BEHAVIOR ON UNFIXED CODE: Tests should FAIL")
    print("EXPECTED BEHAVIOR ON FIXED CODE: Tests should PASS")
    
    results = []
    
    # Run all tests
    results.append(("Line 610 Syntax Check", test_line_611_contains_buggy_syntax()))
    results.append(("Template Syntax Validation", test_template_syntax_validation()))
    results.append(("If/Endif Tag Balance", test_endif_tag_balance()))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    failed = len(results) - passed
    
    for test_name, result in results:
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed} passed, {failed} failed out of {len(results)} tests")
    
    if failed > 0:
        print("\n" + "="*70)
        print("COUNTEREXAMPLES FOUND - BUG CONFIRMED")
        print("="*70)
        print("\nThe template syntax error EXISTS on line 610 of base.html")
        print("(displayed as line 611 in most text editors).")
        print("Line 610 contains: '{% endif %} %}' (malformed)")
        print("Expected syntax: '{% endif %}' (correct)")
        print("\nThis malformed tag causes Django's template engine to fail")
        print("when parsing base.html, preventing proper rendering of the")
        print("two-row navigation layout and blocking deployment.")
        return 1
    else:
        print("\n" + "="*70)
        print("ALL TESTS PASSED - BUG IS FIXED")
        print("="*70)
        print("\nThe template syntax has been corrected!")
        return 0


if __name__ == '__main__':
    sys.exit(main())
