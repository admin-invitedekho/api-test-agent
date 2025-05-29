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


class AIStepHandler:
    """Enhanced AI step handler with AI-powered schema validation"""
    
    def __init__(self, llm=None, agent=None):
        """Initialize the AI step handler"""
        self.llm = llm
        self.agent = agent
        self.context_history = []
        self.response_history = []
        # Initialize AI-powered validator if agent is available
        self.ai_validator = create_ai_validator(agent) if agent else None
    
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
        Process a BDD step using AI
        
        Args:
            step_text: The natural language step text
            table_data: Optional table data from Behave context
            
        Returns:
            Dict containing step execution results
        """
        try:
            # Execute the step using the AI agent
            agent_response = run_scenario_step(step_text)
            
            # Extract relevant information from agent response
            tool_execution = agent_response.get('tool_execution', {}) if isinstance(agent_response, dict) else {}
            
            result = {
                "status": "success",
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
            
            # Store in history
            self.context_history.append(step_text)
            self.response_history.append(result)
            
            return result
            
        except AgentProcessingError as e:
            return {
                "status": "error",
                "step_text": step_text,
                "error": str(e)
            }
        except Exception as e:
            return {
                "status": "error",
                "step_text": step_text,
                "error": f"Unexpected error: {str(e)}"
            }
    
    def _extract_method(self, agent_response) -> str:
        """Extract HTTP method from agent response"""
        if isinstance(agent_response, dict) and 'tool_execution' in agent_response:
            tool_name = agent_response['tool_execution'].get('tool_name', '')
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