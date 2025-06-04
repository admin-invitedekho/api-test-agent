"""
Behave environment configuration with browser scenario management and Allure reporting.

This module sets up the test environment with proper browser context
management for each scenario, ensuring clean isolation between tests,
and comprehensive Allure reporting integration.
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

# Import AI step handler and Allure logger
try:
    from ai_step_handler import AIStepHandler
    from allure_logger import allure_logger
    AI_STEP_HANDLER_AVAILABLE = True
except ImportError as e:
    logging.warning(f"AI step handler not available: {e}")
    AI_STEP_HANDLER_AVAILABLE = False

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
    logging.info("Starting test suite with Allure reporting")
    
    # Initialize global test configuration
    context.browser_handler_available = BROWSER_HANDLER_AVAILABLE
    context.ai_step_handler_available = AI_STEP_HANDLER_AVAILABLE
    
    # Initialize AI step handler
    if AI_STEP_HANDLER_AVAILABLE:
        context.step_handler = AIStepHandler()
        logging.info("AIStepHandler initialized successfully")
    
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
    
    # Initialize Allure logging for the scenario
    if AI_STEP_HANDLER_AVAILABLE:
        scenario_name = f"{scenario.feature.name}: {scenario.name}"
        allure_logger.start_scenario(scenario_name)
        
        # Add scenario tags to Allure
        try:
            import allure
            if scenario.tags:
                for tag in scenario.tags:
                    allure.dynamic.tag(tag)
            
            # Add feature and environment labels
            allure.dynamic.feature(scenario.feature.name)
            allure.dynamic.label("environment", "staging")
            allure.dynamic.label("test_type", "automated")
            
        except ImportError:
            logging.warning("Allure not available for dynamic labeling")
        
        # Reset step handler context for new scenario
        if hasattr(context, 'step_handler'):
            context.step_handler.context_history = []
            context.step_handler.response_history = []
            context.step_handler.jwt_token = None
            context.step_handler.ui_data = {}
            context.step_handler.api_data = {}
    
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
    
    # Complete Allure scenario logging
    if AI_STEP_HANDLER_AVAILABLE:
        scenario_passed = scenario.status.name == 'passed'
        allure_logger.complete_scenario(scenario_passed)
        
        # Clear AI step handler context for next scenario
        if hasattr(context, 'step_handler'):
            context.step_handler.context_history = []
            context.step_handler.response_history = []
            context.step_handler.jwt_token = None
            context.step_handler.ui_data = {}
            context.step_handler.api_data = {}
    
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