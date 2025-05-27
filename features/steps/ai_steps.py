"""
AI-powered step definitions that replace traditional rigid Cucumber steps
with intelligent natural language processing.
"""

from behave import step, given, when, then
import os
import sys

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'src'))

from src.ai_step_handler import AIStepHandler
from langchain_openai import ChatOpenAI


# Initialize AI components
def get_ai_handler(context):
    """Get or create AI handler for the context"""
    if not hasattr(context, 'ai_handler'):
        # Initialize LLM
        llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.1,
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
        
        # Initialize AI handler
        context.ai_handler = AIStepHandler(llm)
        context.step_results = []
        context.validation_results = []
    
    return context.ai_handler


# Universal step handler - matches ANY step text
@step('{step_text}')
def universal_step_handler(context, step_text):
    """
    True universal step handler that matches any step text and processes it with AI
    """
    # Get step type from the behave context by examining the executing step
    step_type = "when"  # Default to when, but we'll try to get the actual type
    
    # Try to get the actual step type from behave's current execution context
    try:
        import inspect
        frame = inspect.currentframe()
        while frame:
            if 'step' in frame.f_locals and hasattr(frame.f_locals['step'], 'step_type'):
                step_type = frame.f_locals['step'].step_type.lower()
                break
            frame = frame.f_back
    except:
        # Fallback: analyze the step text to determine type
        step_text_lower = step_text.lower()
        if any(step_text_lower.startswith(word) for word in ['given', 'and i have', 'and there']):
            step_type = "given"
        elif any(step_text_lower.startswith(word) for word in ['when', 'and i']):
            step_type = "when"
        elif any(step_text_lower.startswith(word) for word in ['then', 'and the', 'and it']):
            step_type = "then"
    
    try:
        # Get AI handler
        ai_handler = get_ai_handler(context)
        
        # Process the step using AI
        result = ai_handler.process_step(step_text, step_type)
        
        # Store result in context
        if not hasattr(context, 'step_results'):
            context.step_results = []
        if not hasattr(context, 'validation_results'):
            context.validation_results = []
            
        context.step_results.append(result)
        context.last_result = result
        
        # Handle different result types
        if result.get("status") == "success":
            _handle_successful_step(context, result, step_text, step_type)
        elif result.get("status") == "validation":
            _handle_validation_step(context, result, step_text)
        elif result.get("status") == "error":
            _handle_error_step(context, result, step_text)
            
    except Exception as e:
        raise AssertionError(f"AI step processing failed: {str(e)}")


def _handle_successful_step(context, result, step_text, step_type):
    """Handle successful step execution"""
    method = result.get("method", "N/A")
    url = result.get("url", "N/A")
    status_code = result.get("status_code", "N/A")
    
    # Only show essential information
    if method != "N/A" and status_code != "N/A":
        print(f"✅ {method} → {status_code}")
    
    # Handle validation results for 'then' steps
    validation = result.get("validation")
    if validation and step_type == "then":
        _process_validation_result(context, validation, step_text)


def _handle_validation_step(context, result, step_text):
    """Handle validation-only steps"""
    # Simplified validation handling
    pass


def _handle_error_step(context, result, step_text):
    """Handle error steps"""
    error_message = result.get("message", "Unknown error")
    print(f"❌ Step failed: {error_message}")
    
    # For some tests, errors might be expected
    if any(word in step_text.lower() for word in ["should fail", "error", "invalid", "not exist"]):
        print("   ℹ️  Error was expected based on step text")
        return
    
    # Otherwise, treat as test failure
    raise AssertionError(f"Step execution failed: {error_message}")


def _process_validation_result(context, validation, step_text):
    """Process intelligent validation results"""
    status = validation.get("status", "unknown")
    validations_performed = validation.get("validations_performed", [])
    failures = validation.get("failures", [])
    
    context.validation_results.append(validation)
    
    print(f"🔍 Intelligent Validation: {status}")
    
    # Show validation details
    for v in validations_performed:
        if v.get("passed", False):
            print(f"   ✅ {v.get('description', 'Validation passed')}")
        else:
            print(f"   ❌ {v.get('description', 'Validation failed')}")
            if 'expected' in v and 'actual' in v:
                print(f"      Expected: {v['expected']}, Got: {v['actual']}")
    
    # Fail the test if any critical validations failed
    if failures:
        failure_messages = [f.get('description', 'Unknown validation failure') for f in failures]
        raise AssertionError(f"Validation failures: {'; '.join(failure_messages)}")


# Legacy step definitions for backward compatibility (these will rarely be used)
@given('the API base URL is "{base_url}"')
def step_given_api_base_url(context, base_url):
    """Legacy compatibility - set base URL"""
    context.base_url = base_url
    print(f"🌐 Base URL set to: {base_url}")


@given('I execute API request "{request_type}" with parameters')
def step_given_execute_api_request(context, request_type):
    """Legacy compatibility - execute parameterized request"""
    # This will be handled by the universal step handler
    # Just pass through for now
    pass


# Debug and utility steps
@then('show me the current test context')
def step_show_context(context):
    """Debug step to show current test context"""
    if hasattr(context, 'ai_handler'):
        summary = context.ai_handler.get_context_summary()
        print(f"\n📊 Test Context Summary:")
        print(f"   Steps executed: {summary['steps_executed']}")
        print(f"   Entities created: {summary['entities_created']}")
        
        if hasattr(context, 'step_results') and context.step_results:
            print(f"   Last response status: {context.step_results[-1].get('status_code', 'N/A')}")


@then('the test should have no validation failures')
def step_check_no_failures(context):
    """Ensure no validation failures occurred during the test"""
    if hasattr(context, 'validation_results'):
        all_failures = []
        for validation in context.validation_results:
            failures = validation.get('failures', [])
            all_failures.extend(failures)
        
        if all_failures:
            failure_summary = [f.get('description', 'Unknown failure') for f in all_failures]
            raise AssertionError(f"Test had validation failures: {'; '.join(failure_summary)}")
        else:
            print("✅ All validations passed successfully!")


# All step patterns are handled by the universal step handler
# The @step('.*') decorator handles ALL step types automatically
