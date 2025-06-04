"""
Behave environment configuration with browser scenario management.

This module sets up the test environment with proper browser context
management for each scenario, ensuring clean isolation between tests.
"""

import logging
import sys
import os

# Add the src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import browser handler for scenario management
try:
    from browser_handler import start_browser_scenario, cleanup_browser_scenario, cleanup_browser
    BROWSER_HANDLER_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Browser handler not available: {e}")
    BROWSER_HANDLER_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def before_all(context):
    """
    Set up the test environment before all scenarios.
    
    Args:
        context: Behave context object
    """
    logging.info("Starting test suite")
    
    # Initialize any global test configuration here
    context.browser_handler_available = BROWSER_HANDLER_AVAILABLE
    
    # Store scenario counter for unique IDs
    context.scenario_counter = 0

def before_scenario(context, scenario):
    """
    Set up before each scenario starts.
    
    Args:
        context: Behave context object
        scenario: Current scenario object
    """
    # Generate unique scenario ID
    context.scenario_counter += 1
    scenario_id = f"scenario_{context.scenario_counter}_{scenario.name.replace(' ', '_').lower()}"
    context.current_scenario_id = scenario_id
    
    # Extract feature name from scenario.feature.filename
    feature_name = "unknown_feature"
    if hasattr(scenario, 'feature') and hasattr(scenario.feature, 'filename'):
        feature_filename = os.path.basename(scenario.feature.filename)
        feature_name = os.path.splitext(feature_filename)[0]  # Remove .feature extension
    
    logging.info(f"Starting scenario: {scenario.name} (ID: {scenario_id})")
    
    # Start fresh browser context for this scenario if browser handler is available
    if context.browser_handler_available:
        try:
            start_browser_scenario(scenario_id, feature_name, scenario.name)
            logging.info(f"Fresh browser context created for scenario: {scenario_id}")
        except Exception as e:
            logging.error(f"Failed to start browser context for scenario {scenario_id}: {e}")
            # Continue without browser context
            context.browser_handler_available = False

def after_scenario(context, scenario):
    """
    Clean up after each scenario completes.
    
    Args:
        context: Behave context object
        scenario: Current scenario object
    """
    scenario_id = getattr(context, 'current_scenario_id', 'unknown')
    logging.info(f"Completing scenario: {scenario.name} (ID: {scenario_id})")
    
    # Clean up browser context for this scenario
    if context.browser_handler_available:
        try:
            cleanup_browser_scenario()
            logging.info(f"Browser context cleaned up for scenario: {scenario_id}")
        except Exception as e:
            logging.warning(f"Error cleaning up browser context for scenario {scenario_id}: {e}")
    
    # Log scenario result
    if scenario.status.name == 'passed':
        logging.info(f"✅ Scenario passed: {scenario.name}")
    elif scenario.status.name == 'failed':
        logging.error(f"❌ Scenario failed: {scenario.name}")
        # Log any additional failure information
        if hasattr(context, 'last_error'):
            logging.error(f"Last error: {context.last_error}")
    else:
        logging.warning(f"⚠️ Scenario status: {scenario.status.name} - {scenario.name}")

def after_all(context):
    """
    Clean up after all scenarios complete.
    
    Args:
        context: Behave context object
    """
    logging.info("Test suite completed")
    
    # Final cleanup of browser resources
    if context.browser_handler_available:
        try:
            cleanup_browser()
            logging.info("Browser resources completely cleaned up")
        except Exception as e:
            logging.warning(f"Error during final browser cleanup: {e}")

def before_step(context, step):
    """
    Called before each step execution.
    
    Args:
        context: Behave context object
        step: Current step object
    """
    logging.debug(f"Executing step: {step.step_type} {step.name}")

def after_step(context, step):
    """
    Called after each step execution.
    
    Args:
        context: Behave context object
        step: Current step object
    """
    if step.status.name == 'failed':
        logging.error(f"❌ Step failed: {step.step_type} {step.name}")
        # Store the error for potential use in scenario cleanup
        if hasattr(step, 'exception'):
            context.last_error = str(step.exception)
    elif step.status.name == 'passed':
        logging.debug(f"✅ Step passed: {step.step_type} {step.name}")
    else:
        logging.debug(f"Step status: {step.status.name} - {step.step_type} {step.name}")

# Error handling for step failures
def handle_step_error(context, step, error):
    """
    Handle errors that occur during step execution.
    
    Args:
        context: Behave context object
        step: Current step object
        error: Exception that occurred
    """
    logging.error(f"Error in step '{step.step_type} {step.name}': {error}")
    context.last_error = str(error)
    
    # Store error details for debugging
    if not hasattr(context, 'step_errors'):
        context.step_errors = []
    
    context.step_errors.append({
        'step': f"{step.step_type} {step.name}",
        'error': str(error),
        'scenario': getattr(context, 'current_scenario_id', 'unknown')
    }) 