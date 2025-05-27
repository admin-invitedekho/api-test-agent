"""
AI Step Handler for processing natural language test steps
"""
import os
import sys
from typing import Dict, Any

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from agent import run_scenario_step, AgentProcessingError


class AIStepHandler:
    """Handles AI-powered step processing for BDD scenarios"""
    
    def __init__(self, llm=None):
        """Initialize the AI step handler"""
        self.llm = llm
        self.context_history = []
        self.response_history = []
    
    def process_step(self, step_text: str, step_type: str) -> Dict[str, Any]:
        """
        Process a BDD step using AI
        
        Args:
            step_text: The natural language step text
            step_type: The step type (given, when, then)
            
        Returns:
            Dict containing step execution results
        """
        try:
            # Execute the step using the AI agent
            agent_response = run_scenario_step(step_text)
            
            # Extract relevant information from agent response
            result = {
                "status": "success",
                "step_text": step_text,
                "step_type": step_type,
                "agent_response": agent_response,
                "method": self._extract_method(agent_response),
                "url": self._extract_url(agent_response),
                "status_code": self._extract_status_code(agent_response),
                "response_data": self._extract_response_data(agent_response)
            }
            
            # Store in history
            self.context_history.append(step_text)
            self.response_history.append(result)
            
            return result
            
        except AgentProcessingError as e:
            return {
                "status": "error",
                "step_text": step_text,
                "step_type": step_type,
                "error": str(e)
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