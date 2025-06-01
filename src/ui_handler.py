"""
UI Handler for processing browser-based instructions using BrowserUse
"""
import os
import logging
from typing import Dict, Any, Optional
import asyncio

try:
    from browser_use import Agent, Browser, BrowserConfig
    from langchain_openai import ChatOpenAI
    BROWSERUSE_AVAILABLE = True
except ImportError:
    BROWSERUSE_AVAILABLE = False
    logging.warning("BrowserUse library not found. Please install it with: pip install browser-use")

# Configure logging
logger = logging.getLogger(__name__)


class UIHandler:
    """Handler for UI automation using BrowserUse"""
    
    def __init__(self, headless: bool = True):
        """
        Initialize UI Handler
        
        Args:
            headless: Whether to run browser in headless mode
        """
        self.headless = headless
        self.browser = None
        self.agent = None
        
    async def _initialize_browser(self):
        """Initialize browser and agent if not already done"""
        if not BROWSERUSE_AVAILABLE:
            raise RuntimeError("BrowserUse library is not available. Please install it with: pip install browser-use")
            
        if self.agent is None:
            # Create browser instance with configuration
            browser_config = BrowserConfig(
                headless=self.headless,
                disable_security=True
            )
            self.browser = Browser(config=browser_config)
            
            # Create LLM for the agent
            llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0.1
            )
            
            # Create BrowserUse agent
            self.agent = Agent(
                task="Execute web automation instructions",
                llm=llm,
                browser=self.browser,
                use_vision=True
            )
            
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
            
            # Execute the instruction using BrowserUse agent
            result = await self.agent.run(instruction)
            
            return {
                "status": "success",
                "instruction": instruction,
                "result": result,
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
        """Close browser session"""
        if self.browser:
            try:
                await self.browser.close()
                self.browser = None
                self.agent = None
                logger.info("Browser session closed successfully")
            except Exception as e:
                logger.error(f"Error closing browser: {str(e)}")


# Global UI handler instance
_ui_handler = None


def get_ui_handler(headless: bool = True) -> UIHandler:
    """Get or create UI handler instance"""
    global _ui_handler
    if _ui_handler is None:
        _ui_handler = UIHandler(headless=headless)
    return _ui_handler


def run_browser_instruction(instruction: str, headless: bool = True) -> Dict[str, Any]:
    """
    Execute browser instruction using BrowserUse
    
    Args:
        instruction: Natural language instruction for browser automation
        headless: Whether to run browser in headless mode
        
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
        # Get UI handler instance
        ui_handler = get_ui_handler(headless=headless)
        
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
    """Navigate to a specific URL"""
    instruction = f"Navigate to {url}"
    return run_browser_instruction(instruction, headless)


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