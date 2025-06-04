"""
Browser Handler Module with Playwright MCP Client Integration

This module provides browser automation capabilities by connecting to the 
Playwright MCP server using stdio transport for visible browser windows.
"""

import logging
import asyncio
import json
import os
import re
from typing import Optional, Dict, Any, List
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Configure logging
logger = logging.getLogger(__name__)

class BrowserMCPHandler:
    """
    Handles browser automation by connecting to Playwright MCP server using stdio transport.
    This provides visible browser windows like Cursor does.
    """
    
    def __init__(self):
        self.mcp_session: Optional[ClientSession] = None
        self.stdio_context = None
        self._current_scenario_id: Optional[str] = None
        self._current_feature_name: Optional[str] = None
        self._current_scenario_name: Optional[str] = None
        self.available_tools: List[Dict] = []
        self._screenshot_counter: int = 0
        self._screenshot_folder: Optional[str] = None
        
    def _setup_screenshot_folder(self):
        """Set up organized screenshot folder structure"""
        if self._current_feature_name and self._current_scenario_name:
            # Clean names for folder structure
            feature_name = re.sub(r'[^\w\-_]', '_', self._current_feature_name.lower())
            scenario_name = re.sub(r'[^\w\-_]', '_', self._current_scenario_name.lower())
            
            # Create folder structure: screenshots/feature_name/scenario_name/
            base_folder = "screenshots"
            feature_folder = os.path.join(base_folder, feature_name)
            scenario_folder = os.path.join(feature_folder, scenario_name)
            
            # Create directories if they don't exist
            os.makedirs(scenario_folder, exist_ok=True)
            
            self._screenshot_folder = scenario_folder
            self._screenshot_counter = 0
            
            logger.info(f"Screenshots will be saved to: {scenario_folder}")
        
    async def _take_automatic_screenshot(self, action_description: str = "action"):
        """Automatically take a screenshot for browser operations"""
        # Temporarily disabled due to MCP browser screenshot path issues
        # The feature file has been cleaned of explicit screenshot steps as requested
        # Folder structure is created correctly
        logger.info(f"📸 Screenshot step: {action_description} (auto-screenshots temporarily disabled)")
        return
    
    async def _add_implicit_wait(self, seconds: int = 2):
        """Add implicit wait after browser operations"""
        try:
            await self.mcp_session.call_tool("browser_wait_for", {"time": seconds})
        except Exception as e:
            logger.warning(f"Failed to add implicit wait: {e}")
        
    async def start_mcp_server(self, scenario_id: str, feature_name: str = None, scenario_name: str = None):
        """
        Start the Playwright MCP server using stdio transport.
        
        Args:
            scenario_id (str): Unique identifier for the scenario
            feature_name (str): Name of the feature file (optional)
            scenario_name (str): Name of the scenario (optional)
        """
        logger.info(f"Starting Playwright MCP server for scenario: {scenario_id}")
        
        # Store scenario information for screenshot organization
        self._current_scenario_id = scenario_id
        self._current_feature_name = feature_name
        self._current_scenario_name = scenario_name
        
        try:
            # Configure server parameters for stdio transport - HEADLESS MODE
            server_params = StdioServerParameters(
                command="npx",
                args=[
                    "@playwright/mcp@latest",
                    "--browser=chrome",
                    "--headless",
                    "--no-sandbox",
                    "--viewport-size=1400,900",
                    "--user-data-dir=/tmp/playwright-headless-session"
                ],
                env={
                    "HEADLESS": "true",
                    "PLAYWRIGHT_HEADLESS": "true"
                }
            )
            
            logger.info("Connecting to MCP server via stdio - HEADLESS mode (no visible browser)")
            
            # Create stdio client connection
            self.stdio_context = stdio_client(server_params)
            self.mcp_reader, self.mcp_writer = await self.stdio_context.__aenter__()
            
            # Establish session
            self.mcp_session = ClientSession(self.mcp_reader, self.mcp_writer)
            await self.mcp_session.__aenter__()
            
            # Initialize the session
            await self.mcp_session.initialize()
            
            # Get available tools
            tools_result = await self.mcp_session.list_tools()
            self.available_tools = tools_result.tools if tools_result else []
            
            logger.info(f"Connected to Playwright MCP server with {len(self.available_tools)} tools")
            
            # Set up screenshot folder structure
            self._setup_screenshot_folder()
            
            # Give browser time to start and become visible
            await asyncio.sleep(4)
            
            return True
                    
        except Exception as e:
            logger.error(f"Failed to start MCP server: {e}")
            await self.cleanup_mcp_session()
            raise
    
    async def send_mcp_command(self, instruction: str) -> Dict[str, Any]:
        """
        Send natural language instruction to Playwright MCP server.
        Automatically handles screenshots and waits for browser operations.
        
        Args:
            instruction (str): Natural language instruction for browser automation
            
        Returns:
            Dict[str, Any]: Result from MCP server execution
        """
        if not self.mcp_session:
            raise RuntimeError("MCP session not initialized. Call start_mcp_server() first.")
        
        logger.info(f"Sending instruction to MCP server: {instruction}")
        
        try:
            # For browser automation, we'll route through appropriate MCP tools
            # First, determine what type of action this is
            action_type, tool_args = self._parse_instruction_to_mcp_tool(instruction)
            
            if action_type and tool_args:
                # Take screenshot before major operations
                if action_type in ["browser_navigate", "browser_click", "browser_type"]:
                    await self._take_automatic_screenshot(f"before_{action_type}")
                
                # Execute the specific MCP tool
                result = await self.mcp_session.call_tool(action_type, arguments=tool_args)
                
                # Add implicit wait after browser operations
                if action_type in ["browser_navigate", "browser_click", "browser_type"]:
                    await self._add_implicit_wait(3)
                    
                # Take screenshot after major operations
                if action_type in ["browser_navigate", "browser_click", "browser_type"]:
                    action_description = instruction.replace('"', '').replace("'", "")[:50]
                    await self._take_automatic_screenshot(f"after_{action_description}")
                
                return {
                    'status': 'success',
                    'instruction': instruction,
                    'mcp_tool': action_type,
                    'mcp_args': tool_args,
                    'result': result.content if hasattr(result, 'content') else str(result),
                    'scenario_id': self._current_scenario_id
                }
            else:
                # If we can't parse it, try using browser_snapshot to get current state
                # and return helpful information
                snapshot_result = await self.mcp_session.call_tool("browser_snapshot", arguments={})
                
                return {
                    'status': 'info',
                    'instruction': instruction,
                    'message': 'Instruction not directly mappable to MCP tool. Current page state retrieved.',
                    'page_state': snapshot_result.content if hasattr(snapshot_result, 'content') else str(snapshot_result),
                    'available_tools': [tool.name for tool in self.available_tools],
                    'scenario_id': self._current_scenario_id
                }
                
        except Exception as e:
            logger.error(f"Error executing MCP command '{instruction}': {e}")
            # Take error screenshot
            await self._take_automatic_screenshot(f"error_{instruction[:30]}")
            return {
                'status': 'error',
                'instruction': instruction,
                'error': str(e),
                'scenario_id': self._current_scenario_id
            }
    
    def _parse_instruction_to_mcp_tool(self, instruction: str) -> tuple[Optional[str], Optional[Dict]]:
        """
        Parse natural language instruction into MCP tool calls.
        
        Args:
            instruction (str): Natural language instruction
            
        Returns:
            Tuple of (tool_name, arguments) or (None, None) if not parsable
        """
        instruction_lower = instruction.lower().strip()
        
        # Navigation commands
        if any(keyword in instruction_lower for keyword in ["navigate", "go to", "open", "visit"]):
            url = self._extract_url_from_instruction(instruction)
            if url:
                return "browser_navigate", {"url": url}
        
        # Click commands  
        elif "click" in instruction_lower:
            # For click, we need to get page snapshot first, then identify element
            # This is a simplified approach - in practice, you'd want to chain calls
            element_desc = self._extract_element_description(instruction)
            if element_desc:
                # Note: In real implementation, you'd first take snapshot, 
                # identify element refs, then click
                return "browser_click", {"element": element_desc, "ref": "auto"}
        
        # Type/input commands
        elif any(keyword in instruction_lower for keyword in ["type", "enter", "input", "fill"]):
            text_to_type = self._extract_text_to_type(instruction)
            element_desc = self._extract_element_description(instruction)
            if text_to_type and element_desc:
                return "browser_type", {
                    "element": element_desc, 
                    "ref": "auto",
                    "text": text_to_type
                }
        
        # Wait commands
        elif "wait" in instruction_lower:
            if "second" in instruction_lower:
                import re
                match = re.search(r'(\d+)\s*second', instruction_lower)
                if match:
                    seconds = int(match.group(1))
                    return "browser_wait_for", {"time": seconds}
            else:
                return "browser_wait_for", {"time": 3}  # Default wait
        
        # Screenshot commands
        elif "screenshot" in instruction_lower:
            return "browser_take_screenshot", {}
        
        # Page snapshot (default for analysis)
        elif any(keyword in instruction_lower for keyword in ["see", "verify", "check", "analyze", "current"]):
            return "browser_snapshot", {}
        
        # Initialize/setup commands
        elif any(keyword in instruction_lower for keyword in ["initialize", "setup", "start"]):
            return "browser_snapshot", {}
        
        # Back/forward navigation
        elif "back" in instruction_lower:
            return "browser_navigate_back", {}
        elif "forward" in instruction_lower:
            return "browser_navigate_forward", {}
        
        return None, None
    
    def _extract_url_from_instruction(self, instruction: str) -> Optional[str]:
        """Extract URL from navigation instruction."""
        import re
        # Look for URLs in the instruction
        url_pattern = r'https?://[^\s"\'<>]+'
        match = re.search(url_pattern, instruction)
        if match:
            return match.group()
        
        # Look for quoted URLs
        quoted_pattern = r'"([^"]*)"'
        match = re.search(quoted_pattern, instruction)
        if match and ('http' in match.group(1) or '.' in match.group(1)):
            url = match.group(1)
            if not url.startswith('http'):
                url = 'https://' + url
            return url
        
        return None
    
    def _extract_element_description(self, instruction: str) -> Optional[str]:
        """Extract element description from instruction."""
        import re
        # Look for quoted text
        quoted_pattern = r'"([^"]*)"'
        match = re.search(quoted_pattern, instruction)
        if match:
            return match.group(1)
        
        # Look for common patterns
        patterns = [
            r'click\s+(?:on\s+)?(?:the\s+)?([^,\.\n]+?)(?:\s+button|\s+link|\s*$)',
            r'(?:button|link|element)\s+(?:with\s+)?(?:text\s+)?["\']?([^"\'<>\n]+?)["\']?',
            r'(?:username|email|password|search|name)\s+(?:field|input|box)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, instruction.lower())
            if match:
                if match.groups():
                    return match.group(1).strip()
                else:
                    # Extract field type from the match
                    field_type = match.group().replace(' field', '').replace(' input', '').replace(' box', '')
                    return field_type
        
        return "interactive element"  # Default fallback
    
    def _extract_text_to_type(self, instruction: str) -> Optional[str]:
        """Extract text to type from instruction."""
        import re
        # Look for quoted text - first match is usually the text to type
        quoted_pattern = r'"([^"]*)"'
        matches = re.findall(quoted_pattern, instruction)
        if matches:
            return matches[0]  # Return first quoted text
        
        return None
    
    async def cleanup_mcp_session(self):
        """Clean up MCP session and server process."""
        try:
            if self.mcp_session:
                # Close browser if possible
                try:
                    await self.mcp_session.call_tool("browser_close", arguments={})
                except Exception as e:
                    logger.debug(f"Error closing browser during cleanup: {e}")
                
                try:
                    await self.mcp_session.__aexit__(None, None, None)
                except Exception as e:
                    logger.debug(f"Error exiting MCP session: {e}")
                
                self.mcp_session = None
            
            if self.stdio_context:
                try:
                    await self.stdio_context.__aexit__(None, None, None)
                except Exception as e:
                    logger.debug(f"Error exiting stdio context: {e}")
                
                self.stdio_context = None
            
            self.mcp_reader = None
            self.mcp_writer = None
            
            logger.info("MCP session cleaned up")
            
        except Exception as e:
            logger.warning(f"Error during MCP cleanup: {e}")


# Global handler instance
_mcp_handler: Optional[BrowserMCPHandler] = None

def get_mcp_handler() -> BrowserMCPHandler:
    """Get or create the global MCP handler instance."""
    global _mcp_handler
    if _mcp_handler is None:
        _mcp_handler = BrowserMCPHandler()
    return _mcp_handler

async def start_browser_scenario_async(scenario_id: str, feature_name: str = None, scenario_name: str = None):
    """
    Start a new browser scenario with MCP server.
    
    Args:
        scenario_id (str): Unique identifier for the scenario
        feature_name (str): Name of the feature file (optional)
        scenario_name (str): Name of the scenario (optional)
    """
    handler = get_mcp_handler()
    await handler.start_mcp_server(scenario_id, feature_name, scenario_name)

async def run_browser_instruction_async(instruction: str) -> Dict[str, Any]:
    """
    Execute a browser instruction using MCP server.
    
    Args:
        instruction (str): Natural language instruction for browser automation
        
    Returns:
        Dict[str, Any]: Result of the instruction execution
    """
    handler = get_mcp_handler()
    return await handler.send_mcp_command(instruction)

async def cleanup_browser_scenario_async():
    """Clean up the current browser scenario."""
    handler = get_mcp_handler()
    await handler.cleanup_mcp_session()

# Synchronous wrappers for compatibility
def run_browser_instruction(instruction: str) -> Dict[str, Any]:
    """
    Synchronous wrapper for browser instruction execution.
    
    Args:
        instruction (str): Natural language instruction for browser automation
        
    Returns:
        Dict[str, Any]: Result of the instruction execution
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(run_browser_instruction_async(instruction))

def start_browser_scenario(scenario_id: str, feature_name: str = None, scenario_name: str = None):
    """
    Start a new browser scenario with MCP server.
    
    Args:
        scenario_id (str): Unique identifier for the scenario
        feature_name (str): Name of the feature file (optional)
        scenario_name (str): Name of the scenario (optional)
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    loop.run_until_complete(start_browser_scenario_async(scenario_id, feature_name, scenario_name))

def cleanup_browser_scenario():
    """Clean up the current browser scenario."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    loop.run_until_complete(cleanup_browser_scenario_async())

def cleanup_browser():
    """Clean up the entire browser instance."""
    cleanup_browser_scenario() 