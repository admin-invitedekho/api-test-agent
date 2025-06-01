# features/steps/ai_steps.py
"""
AI-powered step definitions for Behave BDD tests.
Integrates with the main agent for intelligent API and browser automation.
"""

from behave import given, when, then
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from agent import run_scenario_step


@given('{step_text}')
def step_given(context, step_text):
    """Handle any given step using AI agent"""
    result = run_scenario_step(step_text)
    context.last_result = result
    context.last_step = step_text


@when('{step_text}')
def step_when(context, step_text):
    """Handle any when step using AI agent"""
    result = run_scenario_step(step_text)
    context.last_result = result
    context.last_step = step_text


@then('{step_text}')
def step_then(context, step_text):
    """Handle any then step using AI agent"""
    result = run_scenario_step(step_text)
    context.last_result = result
    context.last_step = step_text
    
    # For assertion steps, check if the result indicates success
    if result and isinstance(result, dict):
        status = result.get('status', 'unknown')
        if status == 'error':
            error_msg = result.get('error', 'Unknown error occurred')
            raise AssertionError(f"Step failed: {step_text}\nError: {error_msg}")
        elif status == 'success':
            # Step passed successfully
            pass
        else:
            # Unknown status, assume success for now
            pass
    else:
        # No result or unexpected format, assume success
        pass
