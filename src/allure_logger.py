"""
Allure Logger for AI-powered automation framework
Provides comprehensive logging and attachment capabilities for Allure reports
"""
import json
import allure
from typing import Dict, Any, Optional, Union
import datetime
import traceback
from dataclasses import dataclass, asdict


@dataclass
class StepContext:
    """Context data for a single step execution"""
    step_text: str
    tool_type: str  # 'API' or 'Browser'
    ai_prompt: Optional[str] = None
    ai_output: Optional[str] = None
    api_method: Optional[str] = None
    api_endpoint: Optional[str] = None
    api_headers: Optional[Dict] = None
    api_body: Optional[Dict] = None
    api_response_code: Optional[int] = None
    api_response_body: Optional[str] = None
    browser_instruction: Optional[str] = None
    browser_logs: Optional[str] = None
    error_details: Optional[str] = None
    execution_time: Optional[float] = None


class AllureLogger:
    """Enhanced Allure logger for comprehensive step tracking"""
    
    def __init__(self):
        self.current_step_context: Optional[StepContext] = None
        self.scenario_start_time = None
        self.step_counter = 0
        
    def start_scenario(self, scenario_name: str):
        """Initialize logging for a new scenario"""
        self.scenario_start_time = datetime.datetime.now()
        self.step_counter = 0
        
        allure.dynamic.title(scenario_name)
        allure.dynamic.description(f"Scenario started at: {self.scenario_start_time}")
        
        with allure.step(f"🚀 Starting Scenario: {scenario_name}"):
            allure.attach(
                f"Scenario: {scenario_name}\nStart Time: {self.scenario_start_time}",
                name="Scenario Info",
                attachment_type=allure.attachment_type.TEXT
            )
    
    def start_step(self, step_text: str, tool_type: str):
        """Start logging for a new step"""
        self.step_counter += 1
        self.current_step_context = StepContext(
            step_text=step_text,
            tool_type=tool_type
        )
        
        # Add step to Allure with dynamic naming
        step_name = f"Step {self.step_counter}: {tool_type} - {step_text}"
        return allure.step(step_name)
    
    def log_ai_interaction(self, prompt: str, output: str):
        """Log AI agent prompt and response"""
        if self.current_step_context:
            self.current_step_context.ai_prompt = prompt
            self.current_step_context.ai_output = output
            
        # Attach AI interaction details
        allure.attach(
            prompt,
            name="🤖 AI Agent Prompt",
            attachment_type=allure.attachment_type.TEXT
        )
        
        allure.attach(
            output,
            name="🤖 AI Agent Output",
            attachment_type=allure.attachment_type.TEXT
        )
        
        # Create a detailed AI interaction summary
        ai_summary = {
            "timestamp": datetime.datetime.now().isoformat(),
            "prompt_length": len(prompt),
            "output_length": len(output),
            "prompt": prompt[:500] + "..." if len(prompt) > 500 else prompt,
            "output": output[:500] + "..." if len(output) > 500 else output
        }
        
        allure.attach(
            json.dumps(ai_summary, indent=2),
            name="🤖 AI Interaction Summary",
            attachment_type=allure.attachment_type.JSON
        )
    
    def log_api_request(self, method: str, endpoint: str, headers: Optional[Dict] = None, 
                       body: Optional[Dict] = None):
        """Log API request details"""
        if self.current_step_context:
            self.current_step_context.api_method = method
            self.current_step_context.api_endpoint = endpoint
            self.current_step_context.api_headers = headers
            self.current_step_context.api_body = body
        
        # Create comprehensive API request data
        request_data = {
            "method": method,
            "endpoint": endpoint,
            "headers": headers or {},
            "body": body or {},
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        allure.attach(
            json.dumps(request_data, indent=2),
            name="🌐 API Request Details",
            attachment_type=allure.attachment_type.JSON
        )
        
        # Create cURL command for easy reproduction
        curl_command = self._generate_curl_command(method, endpoint, headers, body)
        allure.attach(
            curl_command,
            name="📋 cURL Command",
            attachment_type=allure.attachment_type.TEXT
        )
    
    def log_api_response(self, status_code: int, response_body: str, 
                        response_headers: Optional[Dict] = None):
        """Log API response details"""
        if self.current_step_context:
            self.current_step_context.api_response_code = status_code
            self.current_step_context.api_response_body = response_body
        
        # Parse JSON response if possible
        try:
            parsed_response = json.loads(response_body) if response_body else {}
            response_attachment_type = allure.attachment_type.JSON
            formatted_response = json.dumps(parsed_response, indent=2)
        except (json.JSONDecodeError, TypeError):
            formatted_response = response_body
            response_attachment_type = allure.attachment_type.TEXT
        
        # Create response data
        response_data = {
            "status_code": status_code,
            "headers": response_headers or {},
            "body": parsed_response if response_attachment_type == allure.attachment_type.JSON else response_body,
            "timestamp": datetime.datetime.now().isoformat(),
            "success": 200 <= status_code < 300
        }
        
        allure.attach(
            json.dumps(response_data, indent=2),
            name="🌐 API Response Summary",
            attachment_type=allure.attachment_type.JSON
        )
        
        allure.attach(
            formatted_response,
            name=f"📄 Response Body (Status: {status_code})",
            attachment_type=response_attachment_type
        )
        
        # Add status-specific annotations
        if status_code >= 400:
            allure.attach(
                f"API Error - Status Code: {status_code}\nResponse: {response_body}",
                name="❌ API Error Details",
                attachment_type=allure.attachment_type.TEXT
            )
    
    def log_browser_instruction(self, instruction: str, response: Optional[str] = None):
        """Log browser automation details"""
        if self.current_step_context:
            self.current_step_context.browser_instruction = instruction
            self.current_step_context.browser_logs = response
        
        browser_data = {
            "instruction": instruction,
            "response": response,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        allure.attach(
            json.dumps(browser_data, indent=2),
            name="🌐 Browser Instruction",
            attachment_type=allure.attachment_type.JSON
        )
        
        allure.attach(
            instruction,
            name="🎭 Playwright MCP Instruction",
            attachment_type=allure.attachment_type.TEXT
        )
        
        if response:
            allure.attach(
                response,
                name="🎭 Browser Response",
                attachment_type=allure.attachment_type.TEXT
            )
    
    def log_error(self, error: Exception, context: str = ""):
        """Log error details with full traceback"""
        error_details = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "traceback": traceback.format_exc(),
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        if self.current_step_context:
            self.current_step_context.error_details = json.dumps(error_details, indent=2)
        
        allure.attach(
            json.dumps(error_details, indent=2),
            name="❌ Error Details",
            attachment_type=allure.attachment_type.JSON
        )
        
        allure.attach(
            traceback.format_exc(),
            name="📋 Full Traceback",
            attachment_type=allure.attachment_type.TEXT
        )
    
    def log_step_completion(self, success: bool, execution_time: Optional[float] = None):
        """Complete step logging with summary"""
        if not self.current_step_context:
            return
        
        if execution_time:
            self.current_step_context.execution_time = execution_time
        
        # Create comprehensive step summary
        step_summary = asdict(self.current_step_context)
        step_summary["success"] = success
        step_summary["completion_time"] = datetime.datetime.now().isoformat()
        
        allure.attach(
            json.dumps(step_summary, indent=2),
            name="📊 Step Execution Summary",
            attachment_type=allure.attachment_type.JSON
        )
        
        # Add execution metrics
        metrics = {
            "step_number": self.step_counter,
            "tool_type": self.current_step_context.tool_type,
            "success": success,
            "execution_time_seconds": execution_time,
            "has_error": bool(self.current_step_context.error_details)
        }
        
        allure.attach(
            json.dumps(metrics, indent=2),
            name="⏱️ Step Metrics",
            attachment_type=allure.attachment_type.JSON
        )
        
        # Clear context for next step
        self.current_step_context = None
    
    def complete_scenario(self, success: bool):
        """Complete scenario logging with summary"""
        if not self.scenario_start_time:
            return
        
        end_time = datetime.datetime.now()
        total_duration = (end_time - self.scenario_start_time).total_seconds()
        
        scenario_summary = {
            "total_steps": self.step_counter,
            "success": success,
            "start_time": self.scenario_start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "total_duration_seconds": total_duration
        }
        
        allure.attach(
            json.dumps(scenario_summary, indent=2),
            name="🏁 Scenario Summary",
            attachment_type=allure.attachment_type.JSON
        )
        
        # Reset for next scenario
        self.scenario_start_time = None
        self.step_counter = 0
    
    def _generate_curl_command(self, method: str, endpoint: str, 
                              headers: Optional[Dict] = None, body: Optional[Dict] = None) -> str:
        """Generate a cURL command for API reproduction"""
        curl_parts = [f"curl -X {method}"]
        
        if headers:
            for key, value in headers.items():
                curl_parts.append(f"-H '{key}: {value}'")
        
        if body and method.upper() in ['POST', 'PUT', 'PATCH']:
            json_body = json.dumps(body)
            curl_parts.append(f"-d '{json_body}'")
        
        curl_parts.append(f"'{endpoint}'")
        
        return " \\\n  ".join(curl_parts)


# Global instance for easy access
allure_logger = AllureLogger() 