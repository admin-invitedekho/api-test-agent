# features/steps/enhanced_steps.py
"""
Enhanced AI-powered step definitions for API and browser testing
"""

import sys
import os
from behave import step

# Add the src directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

from ai_step_handler import AIStepHandler


@step(u'{step_text}')
def universal_ai_step(context, step_text):
    """
    Universal AI-powered step that can handle any step definition using LLM.
    This function automatically routes between API and browser automation
    based on the step content.
    """
    try:
        # Initialize AI handler if not exists
        if not hasattr(context, 'ai_handler'):
            # Default to headless browser for CI/CD environments
            # Set headless=False for local development to see browser actions
            headless_browser = os.getenv('HEADLESS_BROWSER', 'true').lower() == 'true'
            context.ai_handler = AIStepHandler(headless_browser=headless_browser)
        
        # Initialize results list if not exists
        if not hasattr(context, 'ai_results'):
            context.ai_results = []
        
        # Process the step with AI using the unified step handler
        result = context.ai_handler.step_handler(step_text)
        
        # Store the result
        context.ai_results.append(result)
        
        # Determine action type for reporting
        action_type = result.get('action_type', 'unknown')
        execution_type = result.get('execution_type', action_type)
        
        # Check if the step was successful
        if result.get('status') == 'error':
            error_msg = result.get('error', 'Unknown error occurred')
            print(f"❌ {execution_type.upper()} Step failed: {step_text}")
            print(f"Error: {error_msg}")
            raise AssertionError(f"Step failed: {error_msg}")
        
        # Report success with execution type
        if execution_type == 'api':
            method = result.get('method', 'N/A')
            status_code = result.get('status_code', 'N/A')
            print(f"✅ API Step executed successfully: {step_text}")
            print(f"   Method: {method}, Status: {status_code}")
        elif execution_type == 'browser':
            success = result.get('success', False)
            message = result.get('message', '')
            print(f"✅ BROWSER Step executed successfully: {step_text}")
            print(f"   Browser result: {message}")
        else:
            print(f"✅ Step executed successfully: {step_text}")
        
    except Exception as e:
        action_type = getattr(context, 'ai_handler', None)
        if action_type and hasattr(action_type, 'ai_decide_tool'):
            try:
                tool_type = action_type.ai_decide_tool(step_text)
                print(f"❌ {tool_type.upper()} Step failed: {step_text}")
            except:
                print(f"❌ Step failed: {step_text}")
        else:
            print(f"❌ Step failed: {step_text}")
        print(f"Error: {str(e)}")
        raise


def cleanup_after_scenario(context):
    """
    Cleanup function to be called after each scenario.
    This should be called from environment.py hooks.
    """
    if hasattr(context, 'ai_handler'):
        try:
            context.ai_handler.cleanup()
        except Exception as e:
            print(f"Warning: Error during cleanup: {e}")


# Example of how to use the unified step handler in feature files:
"""
Feature: Unified API and Browser Testing Example

  Scenario: Mixed API and UI testing
    Given I open the login page                          # Browser action
    When I enter "admin@example.com" in the email field  # Browser action  
    And I enter "password123" in the password field      # Browser action
    And I click the login button                         # Browser action
    Then I should see "Welcome" on the page              # Browser action
    When I login to API with email "admin@example.com" and password "password123"  # API action
    Then I should receive a successful authentication response  # API assertion
    And the response should contain a valid JWT token    # API assertion
"""
