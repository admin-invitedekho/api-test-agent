"""
AI-powered schema validation utilities for API testing
Uses the AI agent for intelligent, context-aware validation
"""

import json
from typing import Dict, Any, Tuple, Optional, List


class AISchemaValidator:
    """AI-powered schema validator that uses the agent for intelligent validation"""
    
    def __init__(self, agent):
        self.agent = agent
    
    def validate_request_data(self, endpoint: str, method: str, data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Use AI agent to validate request data intelligently"""
        
        validation_prompt = f"""
        Please validate the following API request data against the API contracts:
        
        Endpoint: {method} {endpoint}
        Request Data: {json.dumps(data, indent=2)}
        
        Based on the API contracts in your memory, please:
        1. Check if all required fields are present
        2. Validate field formats and constraints
        3. Check data types are correct
        4. Verify field values make sense for this endpoint
        
        Respond with either:
        - "VALID" if the request data is correct
        - "INVALID: [specific reason]" if there are issues
        
        Be specific about what's wrong if invalid.
        """
        
        try:
            response = self.agent.process_request(validation_prompt)
            
            # Ensure response is always a string to prevent NoneType errors
            if response is None:
                response = ''
            response = str(response)
            
            if response.startswith("VALID"):
                return True, None
            elif response.startswith("INVALID:"):
                return False, response[8:].strip()  # Remove "INVALID:" prefix
            else:
                # Parse the response to extract validation result
                if "valid" in response.lower() and "invalid" not in response.lower():
                    return True, None
                else:
                    return False, response
                    
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def validate_response_data(self, endpoint: str, method: str, response_data: Any) -> Tuple[bool, Optional[str]]:
        """Use AI agent to validate response data intelligently"""
        
        validation_prompt = f"""
        Please validate the following API response data against the API contracts:
        
        Endpoint: {method} {endpoint}
        Response Data: {json.dumps(response_data, indent=2) if isinstance(response_data, (dict, list)) else str(response_data)}
        
        Based on the API contracts in your memory, please:
        1. Check if the response structure matches expected format
        2. Verify all required response fields are present
        3. Check data types are correct
        4. Validate that field values make sense
        
        Respond with either:
        - "VALID" if the response data is correct
        - "INVALID: [specific reason]" if there are issues
        
        Be specific about what's wrong if invalid.
        """
        
        try:
            response = self.agent.process_request(validation_prompt)
            
            # Ensure response is always a string to prevent NoneType errors
            if response is None:
                response = ''
            response = str(response)
            
            if response.startswith("VALID"):
                return True, None
            elif response.startswith("INVALID:"):
                return False, response[8:].strip()
            else:
                if "valid" in response.lower() and "invalid" not in response.lower():
                    return True, None
                else:
                    return False, response
                    
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def suggest_request_data(self, endpoint: str, method: str, context: str = "") -> Dict[str, Any]:
        """Use AI agent to suggest appropriate request data for an endpoint"""
        
        suggestion_prompt = f"""
        Based on the API contracts in your memory, please suggest appropriate request data for:
        
        Endpoint: {method} {endpoint}
        Context: {context}
        
        Please provide a JSON object with realistic, valid data that would work for this API call.
        Include all required fields and some optional fields where appropriate.
        
        Respond with only the JSON object, no other text.
        """
        
        try:
            response = self.agent.process_request(suggestion_prompt)
            
            # Try to extract JSON from the response
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:-3].strip()
            elif response.startswith('```'):
                response = response[3:-3].strip()
            
            return json.loads(response)
            
        except Exception as e:
            # Fallback to basic data structure
            return self._get_fallback_data(endpoint, method)
    
    def get_validation_insights(self, endpoint: str, method: str) -> Dict[str, Any]:
        """Use AI agent to provide validation insights for an endpoint"""
        
        insights_prompt = f"""
        Based on the API contracts in your memory, please provide validation insights for:
        
        Endpoint: {method} {endpoint}
        
        Please provide information about:
        1. Required fields
        2. Optional fields
        3. Field constraints (length, format, etc.)
        4. Common validation errors to watch for
        5. Best practices for this endpoint
        
        Format your response as a JSON object with these keys:
        - required_fields: array of required field names
        - optional_fields: array of optional field names
        - field_constraints: object with field-specific constraints
        - common_errors: array of common validation issues
        - best_practices: array of recommendations
        
        Respond with only the JSON object.
        """
        
        try:
            response = self.agent.process_request(insights_prompt)
            
            # Try to extract JSON from the response
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:-3].strip()
            elif response.startswith('```'):
                response = response[3:-3].strip()
            
            return json.loads(response)
            
        except Exception as e:
            return {
                "required_fields": [],
                "optional_fields": [],
                "field_constraints": {},
                "common_errors": [],
                "best_practices": [],
                "error": str(e)
            }
    
    def analyze_api_error(self, endpoint: str, method: str, error_response: Any) -> str:
        """Use AI agent to analyze API errors and suggest fixes"""
        
        analysis_prompt = f"""
        Please analyze this API error and suggest how to fix it:
        
        Endpoint: {method} {endpoint}
        Error Response: {json.dumps(error_response, indent=2) if isinstance(error_response, (dict, list)) else str(error_response)}
        
        Based on the API contracts in your memory:
        1. Explain what went wrong
        2. Suggest specific fixes
        3. Provide corrected request data if applicable
        
        Be practical and specific in your recommendations.
        """
        
        try:
            return self.agent.process_request(analysis_prompt)
        except Exception as e:
            return f"Error analyzing API error: {str(e)}"
    
    def generate_test_scenarios(self, endpoint: str, method: str) -> List[Dict[str, Any]]:
        """Use AI agent to generate comprehensive test scenarios"""
        
        scenarios_prompt = f"""
        Based on the API contracts in your memory, please generate comprehensive test scenarios for:
        
        Endpoint: {method} {endpoint}
        
        Generate test scenarios for:
        1. Valid requests (happy path)
        2. Invalid requests (missing required fields)
        3. Edge cases (boundary values)
        4. Error conditions
        
        Format as a JSON array where each scenario has:
        - name: scenario description
        - type: "valid" or "invalid"
        - data: request data to use
        - expected_result: what should happen
        
        Respond with only the JSON array.
        """
        
        try:
            response = self.agent.process_request(scenarios_prompt)
            
            # Try to extract JSON from the response
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:-3].strip()
            elif response.startswith('```'):
                response = response[3:-3].strip()
            
            return json.loads(response)
            
        except Exception as e:
            return [
                {
                    "name": f"Basic {method} test for {endpoint}",
                    "type": "valid",
                    "data": self._get_fallback_data(endpoint, method),
                    "expected_result": "Success",
                    "error": str(e)
                }
            ]
    
    def _get_fallback_data(self, endpoint: str, method: str) -> Dict[str, Any]:
        """Provide fallback data when AI agent is not available"""
        endpoint_lower = endpoint.lower()
        
        if '/users' in endpoint_lower:
            return {
                "name": "Test User",
                "email": "test@example.com",
                "username": "testuser"
            }
        elif '/posts' in endpoint_lower:
            return {
                "title": "Test Post",
                "body": "Test content",
                "userId": 1
            }
        elif '/todos' in endpoint_lower:
            return {
                "title": "Test Todo",
                "completed": False,
                "userId": 1
            }
        else:
            return {}


def create_ai_validator(agent) -> AISchemaValidator:
    """Factory function to create AI-powered validator"""
    return AISchemaValidator(agent)
