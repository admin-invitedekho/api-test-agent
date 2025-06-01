"""
AI Step Handler for processing natural language test steps
"""
import os
import sys
import logging
from typing import Dict, Any, Tuple, Optional
import json
import re

# Set logging level to ERROR to reduce noise
logging.getLogger().setLevel(logging.ERROR)

# Add src directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from agent import run_scenario_step, AgentProcessingError
from ai_schema_validator import create_ai_validator
from ui_handler import run_browser_instruction, is_browser_instruction, close_browser_session


class AIStepHandler:
    """Enhanced AI step handler with AI-powered schema validation and browser automation"""
    
    def __init__(self, llm=None, agent=None, headless_browser=True):
        """Initialize the AI step handler"""
        self.llm = llm
        self.agent = agent
        self.headless_browser = headless_browser
        self.context_history = []
        self.response_history = []
        # Initialize AI-powered validator if agent is available
        self.ai_validator = create_ai_validator(agent) if agent else None
    
    def ai_decide_tool(self, step_text: str) -> str:
        """
        AI-powered decision making to determine if a step requires API or browser automation.
        
        Args:
            step_text (str): The natural language step text
            
        Returns:
            str: 'api' or 'browser' based on the step analysis
        """
        # First check using pattern matching for common browser actions
        if is_browser_instruction(step_text):
            return 'browser'
        
        # Check for explicit API patterns
        api_patterns = [
            'api', 'endpoint', 'post', 'get', 'put', 'delete', 'patch',
            'json', 'response', 'status code', 'http', 'request'
        ]
        
        step_lower = step_text.lower()
        for pattern in api_patterns:
            if pattern in step_lower:
                return 'api'
        
        # Check for login patterns - could be either browser or API
        # For now, default login to API unless specifically browser-oriented
        if 'login' in step_lower:
            browser_login_indicators = [
                'page', 'form', 'field', 'button', 'click', 'enter', 'type'
            ]
            for indicator in browser_login_indicators:
                if indicator in step_lower:
                    return 'browser'
            return 'api'  # Default login to API
        
        # Advanced AI-based classification could be added here
        # For now, use heuristics
        
        # If step mentions navigation, interaction, or visual elements
        ui_indicators = [
            'navigate', 'browse', 'page', 'click', 'button', 'link',
            'form', 'field', 'enter', 'type', 'select', 'dropdown',
            'scroll', 'wait', 'see', 'verify on page', 'element',
            'window', 'tab', 'popup', 'modal', 'dialog'
        ]
        
        for indicator in ui_indicators:
            if indicator in step_lower:
                return 'browser'
        
        # Default to API if unclear
        return 'api'
    
    def step_handler(self, step_text: str) -> Dict[str, Any]:
        """
        Unified step handler that routes between API and browser automation.
        
        This is the main function that replaces individual step definitions.
        
        Args:
            step_text (str): Natural language step description
            
        Returns:
            Dict containing execution results
        """
        try:
            # Determine action type using AI decision logic
            action_type = self.ai_decide_tool(step_text)
            
            result = {
                "status": "success",
                "step_text": step_text,
                "action_type": action_type,
                "timestamp": None
            }
            
            if action_type == 'api':
                # Route to API handler
                api_result = self._run_api_instruction(step_text)
                result.update(api_result)
                
            elif action_type == 'browser':
                # Route to browser handler
                browser_result = self._run_browser_instruction(step_text)
                result.update(browser_result)
                
            else:
                result["status"] = "error"
                result["error"] = f"Unknown action type: {action_type}"
            
            # Store in history
            self.context_history.append(step_text)
            self.response_history.append(result)
            
            return result
            
        except Exception as e:
            error_result = {
                "status": "error",
                "step_text": step_text,
                "error": f"Step handler error: {str(e)}"
            }
            self.response_history.append(error_result)
            return error_result
    
    def _run_api_instruction(self, step_text: str) -> Dict[str, Any]:
        """
        Execute API instruction using existing agent.
        
        Args:
            step_text (str): Natural language API instruction
            
        Returns:
            Dict containing API execution results
        """
        try:
            # Use existing API processing logic
            agent_response = run_scenario_step(step_text)
            
            # Extract relevant information from agent response
            tool_execution = agent_response.get('tool_execution', {}) if isinstance(agent_response, dict) else {}
            
            return {
                "agent_response": agent_response,
                "method": self._extract_method(agent_response),
                "url": self._extract_url(agent_response),
                "status_code": tool_execution.get('status_code'),
                "response_data": tool_execution.get('json_response'),
                "execution_type": "api"
            }
            
        except AgentProcessingError as e:
            return {
                "status": "error",
                "error": f"API execution error: {str(e)}",
                "execution_type": "api"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": f"Unexpected API error: {str(e)}",
                "execution_type": "api"
            }
    
    def _run_browser_instruction(self, step_text: str) -> Dict[str, Any]:
        """
        Execute browser instruction using UI handler.
        
        Args:
            step_text (str): Natural language browser instruction
            
        Returns:
            Dict containing browser execution results
        """
        try:
            # Execute browser instruction
            browser_result = run_browser_instruction(step_text, headless=self.headless_browser)
            
            return {
                "browser_result": browser_result,
                "success": browser_result.get("success", False),
                "message": browser_result.get("message", ""),
                "screenshot": browser_result.get("screenshot"),
                "execution_type": "browser"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Browser execution error: {str(e)}",
                "execution_type": "browser"
            }
    
    def cleanup(self):
        """Clean up resources including browser sessions."""
        try:
            close_browser_session()
        except Exception as e:
            logging.error(f"Error during cleanup: {e}")

    def parse_api_call(self, step_description: str) -> Tuple[Optional[str], Optional[str], Optional[Dict], Optional[Dict]]:
        """
        Parse step description to extract API call details
        Returns: (method, endpoint, data, params)
        """
        step_lower = step_description.lower().strip()
        
        # Extract HTTP method
        method = None
        for m in ['post', 'put', 'get', 'delete', 'patch']:
            if step_lower.startswith(m):
                method = m.upper()
                break
        
        if not method:
            return None, None, None, None
        
        # Extract endpoint
        endpoint_match = re.search(r'(post|put|get|delete|patch)\s+(/\S+)', step_lower)
        endpoint = endpoint_match.group(2) if endpoint_match else None
        
        # Extract JSON data for POST/PUT requests
        data = None
        if method in ['POST', 'PUT']:
            json_match = re.search(r'(?:with\s+(?:json\s+)?data|with\s+payload|with\s+body):\s*(\{.*\})', step_description, re.IGNORECASE)
            if json_match:
                try:
                    data = json.loads(json_match.group(1))
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON data: {e}")
        
        # Extract query parameters for GET requests
        params = None
        if method == 'GET':
            params_match = re.search(r'with\s+(?:parameters|params)\s+([^"]*)', step_lower)
            if params_match:
                params_str = params_match.group(1).strip()
                params = {}
                for param_pair in params_str.split('&'):
                    if '=' in param_pair:
                        key, value = param_pair.split('=', 1)
                        # Try to convert to appropriate type
                        try:
                            value = int(value)
                        except ValueError:
                            try:
                                value = float(value)
                            except ValueError:
                                pass  # Keep as string
                        params[key.strip()] = value
        
        return method, endpoint, data, params
    
    def validate_request_before_execution(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Tuple[bool, Optional[str]]:
        """Validate request data before making API call using AI"""
        if method in ['POST', 'PUT'] and data and self.ai_validator:
            return self.ai_validator.validate_request_data(endpoint, method, data)
        return True, None
    
    def validate_response_after_execution(self, endpoint: str, method: str, response_data: Any) -> Tuple[bool, Optional[str]]:
        """Validate response data using AI"""
        if self.ai_validator and response_data:
            return self.ai_validator.validate_response_data(endpoint, method, response_data)
        return True, None
    
    def process_step(self, step_text: str, table_data=None) -> Dict[str, Any]:
        """
        Process a BDD step using AI - LEGACY METHOD for backward compatibility
        Use step_handler() for new implementations
        
        Args:
            step_text: The natural language step text
            table_data: Optional table data from Behave context
            
        Returns:
            Dict containing step execution results
        """
        return self.step_handler(step_text)
    
    def _extract_method(self, agent_response) -> str:
        """Extract HTTP method from agent response"""
        if isinstance(agent_response, dict) and 'tool_execution' in agent_response:
            tool_name = agent_response['tool_execution'].get('tool_name', '')
            # Ensure tool_name is always a string to prevent NoneType errors
            if tool_name is None:
                tool_name = ''
            tool_name = str(tool_name)
            
            if 'get' in tool_name.lower():
                return 'GET'
            elif 'post' in tool_name.lower():
                return 'POST'
            elif 'put' in tool_name.lower():
                return 'PUT'
            elif 'delete' in tool_name.lower():
                return 'DELETE'
        return 'N/A'
    
    def _extract_url(self, agent_response) -> str:
        """Extract URL from agent response"""
        if isinstance(agent_response, dict) and 'tool_execution' in agent_response:
            endpoint = agent_response['tool_execution'].get('endpoint', '')
            if endpoint:
                return f"https://jsonplaceholder.typicode.com{endpoint}"
        return 'N/A'
    
    def _extract_status_code(self, agent_response) -> str:
        """Extract status code from agent response"""
        if isinstance(agent_response, dict) and 'tool_execution' in agent_response:
            return str(agent_response['tool_execution'].get('status_code', 'N/A'))
        return 'N/A'
    
    def _extract_response_data(self, agent_response) -> Any:
        """Extract response data from agent response"""
        if isinstance(agent_response, dict) and 'tool_execution' in agent_response:
            return agent_response['tool_execution'].get('json_response')
        return None
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get a summary of the current test context"""
        api_steps = [r for r in self.response_history if r.get('execution_type') == 'api']
        browser_steps = [r for r in self.response_history if r.get('execution_type') == 'browser']
        
        return {
            "steps_executed": len(self.context_history),
            "api_steps": len(api_steps),
            "browser_steps": len(browser_steps),
            "entities_created": len([r for r in api_steps if r.get('method') in ['POST', 'PUT']]),
            "last_response": self.response_history[-1] if self.response_history else None
        }
    
    def execute_step(self, step_description: str) -> Dict[str, Any]:
        """
        Enhanced step execution with schema validation - LEGACY METHOD
        Use step_handler() for new implementations
        
        Args:
            step_description: Natural language step description
            
        Returns:
            Dict containing execution results and validation status
        """
        return self.step_handler(step_description)
    
    def _execute_with_ai_agent(self, step_description: str) -> Dict[str, Any]:
        """Execute step using AI agent without validation"""
        try:
            return run_scenario_step(step_description)
        except Exception as e:
            return {
                "status": "ai_agent_error",
                "step_description": step_description,
                "error": str(e)
            }
    
    def get_validation_summary(self, endpoint: str, method: str) -> Dict[str, Any]:
        """Get comprehensive validation summary for an endpoint using AI"""
        if not self.ai_validator:
            return {"error": "AI validator not available"}
        
        return {
            "endpoint": endpoint,
            "method": method,
            "validation_insights": self.ai_validator.get_validation_insights(endpoint, method),
            "suggested_data": self.ai_validator.suggest_request_data(endpoint, method),
            "test_scenarios": self.ai_validator.generate_test_scenarios(endpoint, method)
        }