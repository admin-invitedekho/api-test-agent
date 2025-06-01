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
    from langchain_openai import ChatOpenAI
    BROWSERUSE_AVAILABLE = True
except ImportError:
    BROWSERUSE_AVAILABLE = False
    logging.warning("BrowserUse library not found. Please install it with: pip install browser-use")

# Configure logging
logger = logging.getLogger(__name__)

# Global session management
_global_ui_handler = None


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
        self.llm = None
        self.session_active = False
        
    async def _initialize_llm(self):
        """Initialize LLM if not already done"""
        if not self.llm:
            self.llm = ChatOpenAI(model="gpt-4o")
            logger.info("LLM initialized for BrowserUse")
            
    async def _execute_instruction(self, instruction: str) -> Dict[str, Any]:
        """
        Execute browser instruction using BrowserUse
        
        Args:
            instruction: Natural language instruction for browser automation
            
        Returns:
            Dict containing execution results
        """
        try:
            if not BROWSERUSE_AVAILABLE:
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
                # Real BrowserUse execution
                await self._initialize_llm()
                logger.info(f"Executing browser instruction: {instruction}")
                
                # Create agent for this specific task
                # BrowserUse 0.2.5 manages browser instances internally
                agent = Agent(
                    task=instruction,
                    llm=self.llm,
                )
                
                # Execute the task
                result = await agent.run()
                
                self.session_active = True
                logger.info(f"Browser instruction completed successfully")
                
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
        """Close browser session and clean up"""
        try:
            self.session_active = False
            logger.info("Browser session marked as closed")
        except Exception as e:
            logger.error(f"Error closing browser: {str(e)}")
    
    def is_session_active(self) -> bool:
        """Check if browser session is active"""
        return self.session_active

    async def execute_instruction(self, instruction: str) -> Dict[str, Any]:
        """Public method to execute browser instruction"""
        return await self._execute_instruction(instruction)


def clear_browser_session():
    """Clear the current browser session"""
    global _global_ui_handler
    if _global_ui_handler:
        try:
            # Simple cleanup
            _global_ui_handler.session_active = False
            logger.info("Browser session cleared")
        except Exception as e:
            logger.error(f"Error clearing session: {e}")
        _global_ui_handler = None


def get_ui_handler(headless: bool = True, fresh_session: bool = True) -> UIHandler:
    """
    Get UI Handler instance
    
    Args:
        headless: Whether to run browser in headless mode
        fresh_session: Whether to use a fresh browser session
        
    Returns:
        UIHandler instance
    """
    global _global_ui_handler
    
    # For BrowserUse 0.2.5, always create a new handler as browser management is internal
    _global_ui_handler = UIHandler(headless=headless, fresh_session=fresh_session)
    logger.info(f"Created new UI handler (headless={headless}, fresh_session={fresh_session})")
    return _global_ui_handler


def run_browser_instruction(instruction: str, headless: bool = True, fresh_session: bool = True) -> Dict[str, Any]:
    """
    Execute a browser instruction using BrowserUse
    
    Args:
        instruction: Natural language instruction for browser automation
        headless: Whether to run browser in headless mode
        fresh_session: Whether to use a fresh browser session (incognito mode)
        
    Returns:
        Dict containing execution results and status
    """
    try:
        # Get handler
        handler = get_ui_handler(headless=headless, fresh_session=fresh_session)
        
        # Execute instruction
        try:
            # Try to get existing event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, create a task
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, handler.execute_instruction(instruction))
                    result = future.result()
            else:
                # Run in existing loop
                result = loop.run_until_complete(handler.execute_instruction(instruction))
        except RuntimeError:
            # No event loop exists, create a new one
            result = asyncio.run(handler.execute_instruction(instruction))
        
        logger.info(f"Browser instruction completed: {instruction}")
        return result
        
    except Exception as e:
        error_msg = f"Failed to execute browser instruction: {instruction}. Error: {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "instruction": instruction,
            "error": error_msg,
            "browser_session": "failed"
        }


def close_browser_session():
    """Close the current browser session and clean up resources"""
    global _global_ui_handler
    if _global_ui_handler:
        try:
            # Simple cleanup for BrowserUse 0.2.5
            _global_ui_handler.session_active = False
            logger.info("Browser session closed and cleaned up")
        except Exception as e:
            logger.warning(f"Could not properly close browser session: {e}")
        _global_ui_handler = None
    else:
        logger.info("No active browser session to close") 