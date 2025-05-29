# features/steps/enhanced_steps.py
"""
Enhanced AI-powered step definitions for API testing
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
    Universal AI-powered step that can handle any step definition using LLM
    """
    try:
        # Initialize AI handler if not exists
        if not hasattr(context, 'ai_handler'):
            context.ai_handler = AIStepHandler()
        
        # Initialize results list if not exists
        if not hasattr(context, 'ai_results'):
            context.ai_results = []
        
        # Process the step with AI
        result = context.ai_handler.process_step(step_text, context)
        
        # Store the result
        context.ai_results.append(result)
        
        # Check if the step was successful
        if result.get('status') == 'error':
            error_msg = result.get('error', 'Unknown error occurred')
            raise AssertionError(f"Step failed: {error_msg}")
        
        print(f"✅ AI Step executed successfully: {step_text}")
        
    except Exception as e:
        print(f"❌ AI Step failed: {step_text}")
        print(f"Error: {str(e)}")
        raise
