from django.test import TestCase
from django.template import Template, Context, TemplateSyntaxError
from django.template.loader import get_template
import os


class TemplateSyntaxBugConditionTest(TestCase):
    """
    Bug Condition Exploration Test for Navigation Template Syntax Fix
    
    **Validates: Requirements 2.1, 2.2, 2.3**
    
    Property 1: Fault Condition - Template Syntax Error on Line 611
    
    This test confirms the template syntax error exists on line 611 of base.html.
    
    CRITICAL: This test MUST FAIL on unfixed code - failure confirms the bug exists.
    When the bug is fixed, this test will PASS, confirming the expected behavior.
    
    The test verifies:
    1. Line 611 contains the buggy syntax `{% endif %} %}`
    2. Django's template engine fails to parse base.html due to this malformed tag
    3. A TemplateSyntaxError is raised when attempting to load the template
    """
    
    def test_line_611_contains_buggy_syntax(self):
        """
        Verify line 611 of base.html contains the malformed template tag.
        
        On UNFIXED code: This test will PASS (confirms bug exists)
        On FIXED code: This test will FAIL (confirms bug is fixed)
        """
        # Read the base.html file
        template_path = os.path.join('core_blood_system', 'templates', 'base.html')
        
        with open(template_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Line 611 (0-indexed as line 610)
        line_611 = lines[610] if len(lines) > 610 else ""
        
        # On unfixed code, this should contain the buggy syntax
        # On fixed code, this should NOT contain the buggy syntax
        buggy_syntax = '{% endif %} %}'
        correct_syntax = '{% endif %}'
        self.assertNotIn(buggy_syntax, line_611,
                        msg=f"Line 611 still contains the buggy syntax '{buggy_syntax}'. "
                            f"Expected the correct syntax '{correct_syntax}' after fix.")
    
    def test_base_template_parses_without_syntax_error(self):
        """
        Verify Django's template engine can successfully parse base.html.
        
        On UNFIXED code: This test will FAIL with TemplateSyntaxError (confirms bug exists)
        On FIXED code: This test will PASS (confirms bug is fixed)
        """
        try:
            # Attempt to load the base.html template
            template = get_template('base.html')
            
            # If we reach here, the template parsed successfully
            self.assertIsNotNone(template, 
                                msg="Template loaded successfully - bug is fixed!")
            
        except TemplateSyntaxError as e:
            # On unfixed code, we expect a TemplateSyntaxError
            buggy_tag = '{% endif %} %}'
            self.fail(f"TemplateSyntaxError encountered: {str(e)}. "
                     f"This confirms the bug exists on line 611. "
                     f"The malformed tag '{buggy_tag}' prevents template parsing.")
    
    def test_base_template_renders_successfully(self):
        """
        Verify base.html can be rendered with a minimal context.
        
        On UNFIXED code: This test will FAIL (confirms bug exists)
        On FIXED code: This test will PASS (confirms bug is fixed)
        """
        try:
            # Attempt to load and render the template with minimal context
            template = get_template('base.html')
            
            # Create a minimal context
            context = Context({
                'user': None,  # Unauthenticated user
                'request': None,
            })
            
            # Attempt to render
            rendered = template.render(context)
            
            # If we reach here, rendering succeeded
            self.assertIsNotNone(rendered,
                                msg="Template rendered successfully - bug is fixed!")
            self.assertIsInstance(rendered, str,
                                 msg="Rendered output should be a string")
            
        except TemplateSyntaxError as e:
            # On unfixed code, we expect a TemplateSyntaxError
            self.fail(f"TemplateSyntaxError encountered during rendering: {str(e)}. "
                     f"This confirms the bug exists. The malformed tag on line 611 "
                     f"prevents the template from rendering.")
