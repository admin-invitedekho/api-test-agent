"""
UI Handler Module for Browser-Use Integration

This module provides browser automation capabilities using browser-use library
with natural language instructions that can be integrated into the AI-driven
automation framework.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from browser_use import Agent
from langchain_openai import ChatOpenAI
import os

logger = logging.getLogger(__name__)

class UIHandler:
    """Handler class for browser-based UI automation using browser-use."""
    
    def __init__(self, headless: bool = True):
        """
        Initialize the UI handler.
        
        Args:
            headless (bool): Whether to run browser in headless mode
        """
        self.headless = headless
        self.agent = None
        self.session_active = False
        
    async def _ensure_agent_started(self):
        """Ensure browser agent is started and reuse the same session."""
        if self.agent is None or not self.session_active:
            try:
                # Initialize browser-use agent with ChatOpenAI
                llm = ChatOpenAI(
                    model="gpt-4o-mini",  # Use a cost-effective model for UI tasks
                    temperature=0.1
                )
                
                # Create a persistent agent for the entire scenario
                self.agent = Agent(
                    task="Browser automation session for multiple steps",
                    llm=llm,
                    # Additional configuration can be added here
                )
                
                self.session_active = True
                logger.info(f"Browser agent initialized in {'headless' if self.headless else 'headed'} mode")
            except Exception as e:
                logger.error(f"Failed to start browser agent: {e}")
                raise
    
    async def _execute_browser_instruction(self, instruction: str) -> Dict[str, Any]:
        """
        Execute a browser instruction using the existing browser session.
        
        Args:
            instruction (str): Natural language instruction for browser action
            
        Returns:
            Dict containing success status, message, and any relevant data
        """
        try:
            await self._ensure_agent_started()
            
            # Instead of creating a new agent, we'll execute the instruction
            # as a continuation of the existing session
            if hasattr(self.agent, 'run_step'):
                # If browser-use supports step execution
                result = await self.agent.run_step(instruction)
            else:
                # Fallback: Create agent with combined task context
                if not hasattr(self, '_scenario_context'):
                    self._scenario_context = []
                
                self._scenario_context.append(instruction)
                
                # Create a combined task that includes all previous steps
                combined_task = "Continue browser automation session. Previous steps: " + \
                              ". ".join(self._scenario_context[:-1]) + \
                              f". Current step: {instruction}"
                
                # Create a new agent instance but with the combined context
                task_agent = Agent(
                    task=combined_task,
                    llm=self.agent.llm if self.agent else ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
                )
                
                result = await task_agent.run()
            
            return {
                "success": True,
                "message": f"Successfully executed: {instruction}",
                "result": str(result) if result else "Task completed",
                "screenshot": None  # Can add screenshot capture if needed
            }
            
        except Exception as e:
            logger.error(f"Failed to execute browser instruction '{instruction}': {e}")
            return {
                "success": False,
                "message": f"Failed to execute: {instruction}. Error: {str(e)}",
                "result": None,
                "screenshot": None
            }
    
    async def close_browser(self):
        """Close the browser session."""
        if self.agent:
            try:
                # browser-use handles cleanup automatically
                self.agent = None
                self.session_active = False
                if hasattr(self, '_scenario_context'):
                    self._scenario_context = []
                logger.info("Browser session closed")
            except Exception as e:
                logger.error(f"Error closing browser: {e}")
    
    def reset_scenario_context(self):
        """Reset the scenario context for a new test scenario."""
        if hasattr(self, '_scenario_context'):
            self._scenario_context = []
        self.session_active = False

# Global UI handler instance
_ui_handler = None

def get_ui_handler(headless: bool = True) -> UIHandler:
    """
    Get or create the global UI handler instance.
    
    Args:
        headless (bool): Whether to run browser in headless mode
        
    Returns:
        UIHandler instance
    """
    global _ui_handler
    if _ui_handler is None:
        _ui_handler = UIHandler(headless=headless)
    return _ui_handler

def run_browser_instruction(instruction: str, headless: bool = True) -> Dict[str, Any]:
    """
    Execute a browser instruction using natural language.
    
    This is the main function that will be called by the AI routing logic
    to handle UI/browser interactions.
    
    Args:
        instruction (str): Natural language instruction like "Click login", "Enter password"
        headless (bool): Whether to run browser in headless mode
        
    Returns:
        Dict containing:
            - success (bool): Whether the instruction was executed successfully
            - message (str): Success/error message
            - result: Any relevant data from the browser action
            - screenshot: Optional screenshot data
    """
    try:
        # Get the UI handler instance
        ui_handler = get_ui_handler(headless=headless)
        
        # Execute the instruction asynchronously
        try:
            # Use asyncio.run for Python 3.7+
            result = asyncio.run(
                ui_handler._execute_browser_instruction(instruction)
            )
            return result
        except RuntimeError as e:
            if "asyncio.run() cannot be called from a running event loop" in str(e):
                # Handle case where we're already in an event loop
                loop = asyncio.get_event_loop()
                task = loop.create_task(ui_handler._execute_browser_instruction(instruction))
                return loop.run_until_complete(task)
            else:
                raise
            
    except Exception as e:
        logger.error(f"Error in run_browser_instruction: {e}")
        return {
            "success": False,
            "message": f"Failed to execute browser instruction: {str(e)}",
            "result": None,
            "screenshot": None
        }

def close_browser_session():
    """
    Close the current browser session.
    
    This should be called at the end of test scenarios or when cleanup is needed.
    """
    global _ui_handler
    if _ui_handler:
        try:
            asyncio.run(_ui_handler.close_browser())
            logger.info("Browser session closed and handler reset")
        except RuntimeError as e:
            if "asyncio.run() cannot be called from a running event loop" in str(e):
                # Handle case where we're already in an event loop
                loop = asyncio.get_event_loop()
                loop.run_until_complete(_ui_handler.close_browser())
                logger.info("Browser session closed and handler reset")
            else:
                raise
        except Exception as e:
            logger.error(f"Error closing browser session: {e}")

def reset_browser_session():
    """
    Reset the browser session for a new scenario while keeping the handler instance.
    """
    global _ui_handler
    if _ui_handler:
        _ui_handler.reset_scenario_context()

# Browser instruction patterns for AI routing
BROWSER_INSTRUCTION_PATTERNS = [
    # Navigation patterns
    "open", "go to", "navigate to", "visit", "browse",
    
    # Click patterns
    "click", "tap", "press", "select",
    
    # Input patterns
    "enter", "type", "fill", "input", "write",
    
    # Form patterns
    "submit", "login", "sign in", "register",
    
    # Verification patterns
    "verify", "check", "see", "find", "look for",
    
    # Wait patterns
    "wait", "pause", "delay",
    
    # Scroll patterns
    "scroll", "scroll down", "scroll up",
    
    # Window patterns
    "switch", "close tab", "new tab"
]

def is_browser_instruction(instruction: str) -> bool:
    """
    Determine if an instruction is likely a browser/UI interaction.
    
    Args:
        instruction (str): The instruction text to analyze
        
    Returns:
        bool: True if the instruction appears to be a browser action
    """
    instruction_lower = instruction.lower()
    
    # Check for browser-specific patterns
    for pattern in BROWSER_INSTRUCTION_PATTERNS:
        if pattern in instruction_lower:
            return True
    
    # Check for UI-specific keywords
    ui_keywords = [
        "button", "link", "field", "form", "page", "window",
        "dropdown", "checkbox", "radio", "menu", "dialog",
        "popup", "modal", "tab", "iframe", "element", "website"
    ]
    
    for keyword in ui_keywords:
        if keyword in instruction_lower:
            return True
    
    # Check for URLs in the instruction
    if any(protocol in instruction_lower for protocol in ["http://", "https://", "www."]):
        return True
    
    return False 