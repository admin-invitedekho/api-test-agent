# features/steps/enhanced_steps.py
"""
Unified AI-powered step definitions for both API and browser automation
"""

import sys
import os
from behave import step

# Add the src directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

from ai_step_handler import AIStepHandler

# Global step handler instance
step_handler = AIStepHandler()

@step(u'{step_text}')
def universal_step_handler(context, step_text):
    """
    Single universal step definition that handles ALL instruction patterns.
    Supports any natural language instruction and automatically routes to API or browser automation.
    
    Examples:
    - "I navigate to https://example.com"
    - "click the Login button" 
    - "get user data from API"
    - "verify we are on the profile page"
    """
    result = step_handler.step_handler(step_text)
    context.last_result = result
    
    # Store result details for debugging
    context.last_instruction = step_text
    context.last_action_type = result.get('action_type', 'unknown')
    context.last_status = result.get('status', 'unknown')
    
    # Initialize results list if not exists
    if not hasattr(context, 'ai_results'):
        context.ai_results = []
    context.ai_results.append(result)
    
    # For verification steps, accept both success and info status
    if step_text.startswith(('verify', 'check', 'ensure', 'confirm')):
        acceptable_statuses = ['success', 'info']
    else:
        acceptable_statuses = ['success']
    
    if result['status'] not in acceptable_statuses:
        error_msg = result.get('error', 'Unknown error')
        raise AssertionError(f"Step failed: '{step_text}' - {error_msg}")
    
    print(f"✅ AI Step executed successfully: {step_text}")

# Hook for better debugging and logging
def after_step(context, step):
    """Hook to log step execution details."""
    if hasattr(context, 'last_result'):
        result = context.last_result
        print(f"\n📝 Step: {step.name}")
        print(f"🔧 Action Type: {result.get('action_type', 'unknown')}")
        print(f"📊 Status: {result.get('status', 'unknown')}")
        if result.get('status') == 'error':
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
        else:
            print(f"✅ Result: {result.get('result', 'Success')}")
