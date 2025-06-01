"""
Environment configuration for unified API and browser testing
"""

import os
import sys

# Add the src directory to the Python path
project_root = os.path.dirname(os.path.dirname(__file__))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

from features.steps.enhanced_steps import cleanup_after_scenario


def before_all(context):
    """
    Setup performed before all tests
    """
    # Set default browser configuration
    context.config = {
        'headless_browser': os.getenv('HEADLESS_BROWSER', 'true').lower() == 'true',
        'browser_timeout': int(os.getenv('BROWSER_TIMEOUT', '30')),
        'api_timeout': int(os.getenv('API_TIMEOUT', '10'))
    }
    
    print("🚀 Starting unified API and Browser testing framework")
    print(f"Browser mode: {'Headless' if context.config['headless_browser'] else 'Headed'}")


def before_scenario(context, scenario):
    """
    Setup performed before each scenario
    """
    print(f"\n📋 Starting scenario: {scenario.name}")
    context.scenario_name = scenario.name


def after_scenario(context, scenario):
    """
    Cleanup performed after each scenario
    """
    # Clean up browser sessions and other resources
    cleanup_after_scenario(context)
    
    # Print scenario results
    if scenario.status.name == 'passed':
        print(f"✅ Scenario completed successfully: {scenario.name}")
    else:
        print(f"❌ Scenario failed: {scenario.name}")
        print(f"Status: {scenario.status}")


def after_all(context):
    """
    Cleanup performed after all tests
    """
    # Final cleanup
    if hasattr(context, 'ai_handler'):
        try:
            context.ai_handler.cleanup()
        except Exception as e:
            print(f"Warning: Error during final cleanup: {e}")
    
    print("\n🏁 Unified testing framework execution completed")


def before_step(context, step):
    """
    Setup performed before each step
    """
    # Optional: Add step-level setup here
    pass


def after_step(context, step):
    """
    Cleanup performed after each step
    """
    # Optional: Add step-level cleanup here
    # This could include screenshot capture on failure for browser steps
    if step.status.name == 'failed' and hasattr(context, 'ai_handler'):
        try:
            # Could add screenshot capture here for browser failures
            pass
        except Exception as e:
            print(f"Warning: Error capturing failure info: {e}")


# Configuration for different environments
def configure_for_environment():
    """Configure settings based on environment variables"""
    
    # CI/CD environment detection
    is_ci = any([
        os.getenv('CI'),
        os.getenv('GITHUB_ACTIONS'),
        os.getenv('GITLAB_CI'),
        os.getenv('JENKINS_URL')
    ])
    
    if is_ci:
        # Force headless mode in CI/CD
        os.environ['HEADLESS_BROWSER'] = 'true'
        print("🔧 CI/CD environment detected - forcing headless browser mode")
    
    # Development environment
    if os.getenv('ENVIRONMENT') == 'development':
        # Enable headed browser for debugging
        os.environ.setdefault('HEADLESS_BROWSER', 'false')
        print("🔧 Development environment - enabling headed browser mode")


# Call configuration on import
configure_for_environment() 