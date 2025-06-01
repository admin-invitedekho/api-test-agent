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

from agent import run_scenario_step, AgentProcessingError, get_llm
from ai_schema_validator import create_ai_validator

# Import browser handler
try:
    from browser_handler import run_browser_instruction
    BROWSER_HANDLER_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Browser handler not available: {e}")
    BROWSER_HANDLER_AVAILABLE = False


class AIStepHandler:
    """Enhanced AI step handler with AI-powered schema validation and browser automation"""
    
    def __init__(self, llm=None, agent=None):
        """Initialize the AI step handler"""
        self.llm = llm or get_llm()
        self.agent = agent
        self.context_history = []
        self.response_history = []
        # Initialize AI-powered validator if agent is available
        self.ai_validator = create_ai_validator(agent) if agent else None
    
    def ai_decide_tool(self, step_text: str) -> str:
        """
        Use LangChain LLM to decide whether a step is API-related or browser-related.
        
        Args:
            step_text (str): The natural language step text
            
        Returns:
            str: 'api' or 'browser' indicating the type of action
        """
        try:
            # Create a prompt to classify the step
            classification_prompt = f"""
            Analyze the following test step and classify it as either 'api' or 'browser' based on the action described.

            API actions include:
            - Making HTTP requests (GET, POST, PUT, DELETE)
            - Testing API endpoints
            - Validating JSON responses
            - Setting up data via API calls
            - Database operations via API

            Browser actions include:
            - Opening web pages
            - Clicking buttons or links
            - Filling forms
            - Navigating between pages
            - Interacting with UI elements
            - Taking screenshots
            - Verifying page content
            - Login through web interface

            Step: "{step_text}"

            Respond with only one word: 'api' or 'browser'
            """
            
            # Use the LLM to classify
            response = self.llm.invoke(classification_prompt)
            
            # Extract the classification from response
            if hasattr(response, 'content'):
                classification = response.content.strip().lower()
            else:
                classification = str(response).strip().lower()
            
            # Validate the response
            if 'api' in classification:
                return 'api'
            elif 'browser' in classification:
                return 'browser'
            else:
                # Default fallback - analyze keywords
                return self._fallback_classification(step_text)
                
        except Exception as e:
            logging.warning(f"Error in AI classification, using fallback: {e}")
            return self._fallback_classification(step_text)
    
    def _fallback_classification(self, step_text: str) -> str:
        """
        Fallback classification using keyword matching.
        
        Args:
            step_text (str): The step text to classify
            
        Returns:
            str: 'api' or 'browser'
        """
        step_lower = step_text.lower()
        
        # Browser keywords
        browser_keywords = [
            'open', 'navigate', 'click', 'type', 'enter', 'fill', 'select',
            'page', 'button', 'link', 'form', 'field', 'login', 'logout',
            'screenshot', 'verify', 'see', 'displayed', 'visible', 'browser',
            'web', 'url', 'website', 'interface', 'ui', 'user interface'
        ]
        
        # API keywords
        api_keywords = [
            'get', 'post', 'put', 'delete', 'patch', 'api', 'endpoint',
            'request', 'response', 'json', 'data', 'payload', 'status code',
            'header', 'parameter', 'query', 'body', 'rest', 'http', 'https'
        ]
        
        # Count matches
        browser_matches = sum(1 for keyword in browser_keywords if keyword in step_lower)
        api_matches = sum(1 for keyword in api_keywords if keyword in step_lower)
        
        # Determine classification
        if browser_matches > api_matches:
            return 'browser'
        elif api_matches > browser_matches:
            return 'api'
        else:
            # Default to API for ambiguous cases to maintain backward compatibility
            return 'api'

    def run_api_instruction(self, step_text: str) -> Dict[str, Any]:
        """
        Execute an API-related instruction using the existing agent.
        
        Args:
            step_text (str): The natural language step text
            
        Returns:
            Dict[str, Any]: Result of the API instruction execution
        """
        try:
            # Execute the step using the AI agent (existing logic)
            agent_response = run_scenario_step(step_text)
            
            # Extract relevant information from agent response
            tool_execution = agent_response.get('tool_execution', {}) if isinstance(agent_response, dict) else {}
            
            result = {
                "status": "success",
                "action_type": "api",
                "step_text": step_text,
                "agent_response": agent_response,
                "method": self._extract_method(agent_response),
                "url": self._extract_url(agent_response),
                "status_code": tool_execution.get('status_code'),
                "response_data": tool_execution.get('json_response')
            }
            
            # If this was an API call, validate response schema
            if result["status_code"] and result["response_data"]:
                endpoint = tool_execution.get('endpoint', '')
                method = tool_execution.get('tool_name', '').replace('_api', '').upper()
                if endpoint and method:
                    self.validate_response_after_execution(endpoint, method, result["response_data"])
            
            return result
            
        except AgentProcessingError as e:
            return {
                "status": "error",
                "action_type": "api",
                "step_text": step_text,
                "error": str(e)
            }
        except Exception as e:
            return {
                "status": "error",
                "action_type": "api",
                "step_text": step_text,
                "error": f"Unexpected error: {str(e)}"
            }

    def run_browser_instruction_handler(self, step_text: str) -> Dict[str, Any]:
        """
        Execute a browser-related instruction using the browser handler.
        
        Args:
            step_text (str): The natural language step text
            
        Returns:
            Dict[str, Any]: Result of the browser instruction execution
        """
        if not BROWSER_HANDLER_AVAILABLE:
            return {
                "status": "error",
                "action_type": "browser",
                "step_text": step_text,
                "error": "Browser handler not available. Please ensure playwright-mcp is installed."
            }
        
        try:
            # Use the proper async wrapper from browser_handler
            result = run_browser_instruction(step_text)
            
            # Ensure the result has the correct format
            if isinstance(result, dict):
                result["action_type"] = "browser"
                return result
            else:
                return {
                    "status": "success",
                    "action_type": "browser",
                    "step_text": step_text,
                    "result": result
                }
                
        except Exception as e:
            return {
                "status": "error",
                "action_type": "browser",
                "step_text": step_text,
                "error": f"Browser execution error: {str(e)}"
            }

    def step_handler(self, step_text: str) -> Dict[str, Any]:
        """
        Main step handler that routes between API and browser actions using AI classification.
        
        Args:
            step_text (str): The natural language step text
            
        Returns:
            Dict[str, Any]: Result of the step execution
        """
        # Use AI to decide the action type
        action_type = self.ai_decide_tool(step_text)
        
        logging.info(f"AI classified step as: {action_type} - '{step_text}'")
        
        # Route to the appropriate handler
        if action_type == 'api':
            result = self.run_api_instruction(step_text)
        elif action_type == 'browser':
            result = self.run_browser_instruction_handler(step_text)
        else:
            # Fallback to API for unknown classifications
            logging.warning(f"Unknown action type '{action_type}', defaulting to API")
            result = self.run_api_instruction(step_text)
        
        # Store in history
        self.context_history.append(step_text)
        self.response_history.append(result)
        
        return result

    def process_step(self, step_text: str, context=None, table_data=None) -> Dict[str, Any]:
        """
        Process a BDD step using AI routing between API and browser actions.
        
        Args:
            step_text: The natural language step text
            context: Behave context object (optional)
            table_data: Optional table data from Behave context
            
        Returns:
            Dict containing step execution results
        """
        # Use the new routing logic
        return self.step_handler(step_text)

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
        return {
            "steps_executed": len(self.context_history),
            "entities_created": len([r for r in self.response_history if r.get('method') in ['POST', 'PUT']]),
            "last_response": self.response_history[-1] if self.response_history else None
        }
    
    def execute_step(self, step_description: str) -> Dict[str, Any]:
        """
        Enhanced step execution with schema validation
        
        Args:
            step_description: Natural language step description
            
        Returns:
            Dict containing execution results and validation status
        """
        try:
            # Parse the step to extract API call details
            method, endpoint, data, params = self.parse_api_call(step_description)
            
            if not method or not endpoint:
                # Fall back to AI agent for non-standard steps
                return self._execute_with_ai_agent(step_description)
            
            # Validate request data before execution
            if method in ['POST', 'PUT'] and data:
                is_valid, validation_error = self.validate_request_before_execution(method, endpoint, data)
                if not is_valid:
                    return {
                        "status": "validation_error",
                        "step_description": step_description,
                        "method": method,
                        "endpoint": endpoint,
                        "validation_error": validation_error,
                        "error": f"Request validation failed: {validation_error}"
                    }
            
            # Execute with AI agent
            response = run_scenario_step(step_description)
            
            # Validate response if available
            if isinstance(response, dict) and 'json_response' in response:
                response_data = response['json_response']
                if response_data:
                    is_valid, validation_error = self.validate_response_after_execution(endpoint, method, response_data)
                    if not is_valid:
                        response['response_validation_warning'] = validation_error
            
            # Add validation info to response
            if isinstance(response, dict):
                validation_insights = self.ai_validator.get_validation_insights(endpoint, method) if self.ai_validator else {}
                response['schema_validation'] = {
                    "request_validated": method in ['POST', 'PUT'],
                    "response_validated": True,
                    "validation_insights": validation_insights
                }
            
            return response
            
        except ValueError as e:
            return {
                "status": "parsing_error", 
                "step_description": step_description,
                "error": str(e)
            }
        except Exception as e:
            return {
                "status": "execution_error",
                "step_description": step_description, 
                "error": f"Unexpected error: {str(e)}"
            }
    
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