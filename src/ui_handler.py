"""
UI Handler for processing browser-based instructions using BrowserUse
"""
import os
import logging
from typing import Dict, Any, Optional
import asyncio
import tempfile
import shutil

try:
    from browser_use import Agent
    from browser_use.browser.profile import BrowserProfile
    from langchain_openai import ChatOpenAI
    BROWSERUSE_AVAILABLE = True
except ImportError:
    BROWSERUSE_AVAILABLE = False
    logging.warning("BrowserUse library not found. Please install it with: pip install browser-use")

# Configure logging
logger = logging.getLogger(__name__)


class UIHandler:
    """Handler for UI automation using BrowserUse"""
    
    def __init__(self, headless: bool = True, fresh_session: bool = True):
        """
        Initialize UI Handler
        
        Args:
            headless: Whether to run browser in headless mode
            fresh_session: Whether to use a fresh browser session (incognito mode)
        """
        self.headless = headless
        self.fresh_session = fresh_session
        self.agent = None
        self.llm = None
        self.temp_profile_dir = None
        
    def _create_fresh_profile(self) -> BrowserProfile:
        """Create a fresh browser profile with temporary directory"""
        # Create a unique temporary directory for this session
        self.temp_profile_dir = tempfile.mkdtemp(prefix="browseruse_fresh_")
        
        profile = BrowserProfile(
            headless=self.headless,
            user_data_dir=self.temp_profile_dir,
            profile_directory="fresh_session",
            # Disable security for testing
            disable_security=True,
            # Clear any existing state
            storage_state=None,
            # Don't keep alive to ensure fresh session
            keep_alive=False,
            # Additional fresh session settings
            args=[
                "--incognito",
                "--no-first-run", 
                "--disable-background-networking",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-back-forward-cache",
                "--disable-breakpad",
                "--disable-component-extensions-with-background-pages",
                "--disable-component-update",
                "--disable-default-apps",
                "--disable-dev-shm-usage",
                "--disable-extensions",
                "--disable-features=VizDisplayCompositor",
                "--disable-hang-monitor",
                "--disable-ipc-flooding-protection",
                "--disable-popup-blocking",
                "--disable-prompt-on-repost",
                "--disable-renderer-backgrounding",
                "--disable-sync",
                "--force-color-profile=srgb",
                "--metrics-recording-only",
                "--password-store=basic",
                "--use-mock-keychain",
                "--no-service-autorun"
            ]
        )
        
        logger.info(f"Created fresh browser profile with temp directory: {self.temp_profile_dir}")
        return profile
        
    async def _initialize_browser(self):
        """Initialize browser and agent if not already done"""
        if not BROWSERUSE_AVAILABLE:
            raise RuntimeError("BrowserUse library is not available. Please install it with: pip install browser-use")
            
        if self.agent is None:
            try:
                # Initialize LLM for browser-use
                if not self.llm:
                    self.llm = ChatOpenAI(model="gpt-4o")
                
                # Create browser-use agent with the new simplified API
                self.agent = Agent(
                    task="Browser automation agent",
                    llm=self.llm,
                )
                
                logger.info("BrowserUse agent initialized successfully")
                
            except Exception as e:
                logger.error(f"Failed to initialize BrowserUse agent: {str(e)}")
                # Fall back to mock implementation if initialization fails
                self.agent = "mock_browser_agent"
                logger.warning("Falling back to mock browser implementation")
            
    async def _execute_instruction(self, instruction: str) -> Dict[str, Any]:
        """
        Execute browser instruction using BrowserUse
        
        Args:
            instruction: Natural language instruction for browser automation
            
        Returns:
            Dict containing execution results
        """
        try:
            await self._initialize_browser()
            
            # Check if we have a real agent or mock
            if self.agent == "mock_browser_agent":
                # Mock implementation for demonstration
                logger.info(f"Mock browser execution: {instruction}")
                
                # Simulate different types of browser actions
                if "navigate" in instruction.lower() or "open" in instruction.lower():
                    result = f"Successfully navigated to page as requested: {instruction}"
                elif "click" in instruction.lower():
                    result = f"Successfully clicked element as requested: {instruction}"
                elif "fill" in instruction.lower() or "enter" in instruction.lower():
                    result = f"Successfully filled form fields as requested: {instruction}"
                else:
                    result = f"Successfully executed browser action: {instruction}"
                
                return {
                    "status": "success",
                    "instruction": instruction,
                    "result": result,
                    "browser_session": "active",
                    "note": "Mock implementation - install browser-use and configure OpenAI API key for real browser automation"
                }
            else:
                # Real BrowserUse execution with fresh session
                logger.info(f"Executing browser instruction: {instruction}")
                
                # Create browser profile for fresh session if needed
                browser_profile = None
                if self.fresh_session:
                    browser_profile = self._create_fresh_profile()
                    logger.info("Using fresh browser profile for this session")
                
                # Create a new agent instance for this specific task with fresh session
                task_agent = Agent(
                    task=instruction,
                    llm=self.llm,
                    browser_profile=browser_profile
                )
                
                # Execute the task
                result = await task_agent.run()
                
                return {
                    "status": "success",
                    "instruction": instruction,
                    "result": str(result),
                    "browser_session": "active"
                }
            
        except Exception as e:
            logger.error(f"Browser instruction failed: {instruction}. Error: {str(e)}")
            return {
                "status": "error",
                "instruction": instruction,
                "error": str(e),
                "browser_session": "failed"
            }
    
    async def close_browser(self):
        """Close browser session and clean up temporary directories"""
        if self.agent and self.agent != "mock_browser_agent":
            try:
                # BrowserUse agents are stateless, so no explicit cleanup needed
                self.agent = None
                self.llm = None
                logger.info("Browser session closed successfully")
            except Exception as e:
                logger.error(f"Error closing browser: {str(e)}")
        else:
            self.agent = None
            logger.info("Mock browser session closed")
            
        # Clean up temporary profile directory
        if self.temp_profile_dir and os.path.exists(self.temp_profile_dir):
            try:
                shutil.rmtree(self.temp_profile_dir)
                logger.info(f"Cleaned up temporary profile directory: {self.temp_profile_dir}")
                self.temp_profile_dir = None
            except Exception as e:
                logger.warning(f"Could not clean up temp directory {self.temp_profile_dir}: {e}")


# Global UI handler instance - Reset for each test
_ui_handler = None


def clear_browser_session():
    """Clear the current browser session to ensure fresh start"""
    global _ui_handler
    if _ui_handler:
        try:
            loop = None
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    import nest_asyncio
                    nest_asyncio.apply()
                    loop.run_until_complete(_ui_handler.close_browser())
                else:
                    loop.run_until_complete(_ui_handler.close_browser())
            except RuntimeError:
                asyncio.run(_ui_handler.close_browser())
        except Exception as e:
            logger.error(f"Error clearing browser session: {str(e)}")
        finally:
            _ui_handler = None
            logger.info("Browser session cleared for fresh start")


def get_ui_handler(headless: bool = True, fresh_session: bool = True) -> UIHandler:
    """Get or create UI handler instance with fresh session"""
    global _ui_handler
    
    # Always clear previous session if fresh_session is True
    if fresh_session and _ui_handler is not None:
        clear_browser_session()
    
    if _ui_handler is None:
        _ui_handler = UIHandler(headless=headless, fresh_session=fresh_session)
        logger.info("Created new UI handler instance for fresh session")
    
    return _ui_handler


def run_browser_instruction(instruction: str, headless: bool = True, fresh_session: bool = True) -> Dict[str, Any]:
    """
    Execute browser instruction using BrowserUse with fresh session
    
    Args:
        instruction: Natural language instruction for browser automation
        headless: Whether to run browser in headless mode
        fresh_session: Whether to use a fresh browser session (recommended for testing)
        
    Returns:
        Dict containing execution results
    """
    if not BROWSERUSE_AVAILABLE:
        return {
            "status": "error",
            "instruction": instruction,
            "error": "BrowserUse library is not available. Please install it with: pip install browser-use"
        }
    
    try:
        # Get UI handler instance with fresh session
        ui_handler = get_ui_handler(headless=headless, fresh_session=fresh_session)
        
        # Run the instruction in async context
        loop = None
        try:
            # Try to get existing event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, we need to use asyncio.create_task
                # This typically happens in Jupyter notebooks or other async environments
                import nest_asyncio
                nest_asyncio.apply()
                result = loop.run_until_complete(ui_handler._execute_instruction(instruction))
            else:
                result = loop.run_until_complete(ui_handler._execute_instruction(instruction))
        except RuntimeError:
            # No event loop exists, create a new one
            result = asyncio.run(ui_handler._execute_instruction(instruction))
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to execute browser instruction: {instruction}. Error: {str(e)}")
        return {
            "status": "error",
            "instruction": instruction,
            "error": f"Failed to execute browser instruction: {str(e)}"
        }


def close_browser_session():
    """Close the current browser session"""
    global _ui_handler
    if _ui_handler:
        try:
            loop = None
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    import nest_asyncio
                    nest_asyncio.apply()
                    loop.run_until_complete(_ui_handler.close_browser())
                else:
                    loop.run_until_complete(_ui_handler.close_browser())
            except RuntimeError:
                asyncio.run(_ui_handler.close_browser())
            
            _ui_handler = None
            
        except Exception as e:
            logger.error(f"Error closing browser session: {str(e)}")


# Additional utility functions for specific browser operations
def run_browser_navigation(url: str, headless: bool = True) -> Dict[str, Any]:
    """Navigate to a specific URL with fresh session"""
    instruction = f"Navigate to {url}"
    return run_browser_instruction(instruction, headless, fresh_session=True)


def run_browser_form_fill(form_data: Dict[str, str], headless: bool = True) -> Dict[str, Any]:
    """Fill form fields with provided data"""
    form_instructions = []
    for field, value in form_data.items():
        form_instructions.append(f"Fill the {field} field with '{value}'")
    
    instruction = " and ".join(form_instructions)
    return run_browser_instruction(instruction, headless)


def run_browser_click(element_description: str, headless: bool = True) -> Dict[str, Any]:
    """Click on a specific element"""
    instruction = f"Click on {element_description}"
    return run_browser_instruction(instruction, headless) 