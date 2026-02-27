#!/usr/bin/env python3
"""
Verify Django template syntax without running full Django checks
"""
import re

def check_template_syntax(filepath):
    """Check for common Django template syntax errors"""
    errors = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
    
    # Check for malformed endif tags
    malformed_endif = re.findall(r'{%\s*endif\s*%}\s*%}', content)
    if malformed_endif:
        errors.append(f"Found malformed endif tags: {malformed_endif}")
    
    # Check for balanced template tags
    tag_stack = []
    for i, line in enumerate(lines, 1):
        # Find opening tags
        if_tags = re.findall(r'{%\s*if\s+', line)
        for_tags = re.findall(r'{%\s*for\s+', line)
        block_tags = re.findall(r'{%\s*block\s+', line)
        
        tag_stack.extend(['if'] * len(if_tags))
        tag_stack.extend(['for'] * len(for_tags))
        tag_stack.extend(['block'] * len(block_tags))
        
        # Find closing tags
        endif_tags = re.findall(r'{%\s*endif\s*%}', line)
        endfor_tags = re.findall(r'{%\s*endfor\s*%}', line)
        endblock_tags = re.findall(r'{%\s*endblock\s*%}', line)
        
        for _ in endif_tags:
            if tag_stack and tag_stack[-1] == 'if':
                tag_stack.pop()
            else:
                errors.append(f"Line {i}: Unmatched endif tag")
        
        for _ in endfor_tags:
            if tag_stack and tag_stack[-1] == 'for':
                tag_stack.pop()
            else:
                errors.append(f"Line {i}: Unmatched endfor tag")
        
        for _ in endblock_tags:
            if tag_stack and tag_stack[-1] == 'block':
                tag_stack.pop()
            else:
                errors.append(f"Line {i}: Unmatched endblock tag")
    
    if tag_stack:
        errors.append(f"Unclosed template tags: {tag_stack}")
    
    return errors

if __name__ == '__main__':
    template_path = 'core_blood_system/templates/base.html'
    
    print(f"Checking template syntax: {template_path}")
    print("=" * 60)
    
    errors = check_template_syntax(template_path)
    
    if errors:
        print("❌ ERRORS FOUND:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✅ Template syntax looks good!")
        print("\nKey checks passed:")
        print("  ✓ No malformed {% endif %} tags")
        print("  ✓ Template tags appear balanced")
        print("  ✓ No obvious syntax errors")
    
    print("\n" + "=" * 60)
    print("Note: This is a basic syntax check. Full validation requires Django.")
