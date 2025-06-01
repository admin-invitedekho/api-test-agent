"""
Behave environment configuration for browser session management
"""
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import browser session cleanup
try:
    from ui_handler import close_browser_session
    UI_CLEANUP_AVAILABLE = True
except ImportError:
    UI_CLEANUP_AVAILABLE = False


def after_scenario(context, scenario):
    """Clean up browser session after each scenario"""
    if UI_CLEANUP_AVAILABLE:
        try:
            close_browser_session()
            print(f"✅ Browser session cleaned up after scenario: {scenario.name}")
        except Exception as e:
            print(f"⚠️ Warning: Could not clean up browser session: {e}")


def before_scenario(context, scenario):
    """Initialize context before each scenario"""
    context.last_result = None
    context.last_step = None
    print(f"🚀 Starting scenario: {scenario.name}") 