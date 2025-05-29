# src/agent.py
import os
import logging
import traceback # Added for full traceback logging
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage, HumanMessage
from langchain.agents import AgentExecutor, create_tool_calling_agent
import sys
import os
# Add the src directory to the Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from api_tools import get_api, post_api, put_api, delete_api

from dotenv import load_dotenv

load_dotenv()

# --- Logging Setup ---
logging.basicConfig(level=logging.ERROR, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set specific loggers to ERROR level to reduce noise
logging.getLogger('httpx').setLevel(logging.ERROR)
logging.getLogger('openai').setLevel(logging.ERROR)
logging.getLogger('langchain').setLevel(logging.ERROR)
# --- End Logging Setup ---

# Configure LLM to use OpenAI ChatGPT
def get_llm():
    """Get the configured LLM (OpenAI or Ollama based on environment)"""
    use_ollama = os.getenv('USE_OLLAMA', 'false').lower() == 'true'
    
    if use_ollama:
        try:
            from langchain_ollama import ChatOllama
            model_name = os.getenv('OLLAMA_MODEL', 'llama3.2:latest')
            ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
            logger.info(f"Using Ollama model: {model_name} at {ollama_url}")
            return ChatOllama(
                model=model_name,
                base_url=ollama_url,
                temperature=0.1
            )
        except ImportError:
            logger.error("Ollama dependencies not found. Install langchain-ollama or set USE_OLLAMA=false")
            raise
    else:
        # Use OpenAI ChatGPT
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required when USE_OLLAMA=false")
        
        return ChatOpenAI(
            api_key=api_key,
            model="gpt-3.5-turbo",
            temperature=0.1
        )

llm = get_llm()

tools = [get_api, post_api, put_api, delete_api]

# Load the AI Agent Usage Guide
def load_usage_guide():
    """Load the AI Agent Usage Guide content"""
    guide_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'AI_AGENT_USAGE_GUIDE.md')
    try:
        with open(guide_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Escape curly braces to prevent template variable conflicts
            content = content.replace('{', '{{').replace('}', '}}')
            return content
    except FileNotFoundError:
        logger.warning(f"AI_AGENT_USAGE_GUIDE.md not found at {guide_path}")
        return ""

# Load the API Contracts documentation
def load_api_contracts():
    """Load all API Contracts documentation content from contracts directory"""
    contracts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'contracts')
    content = ""
    
    if os.path.isdir(contracts_dir):
        for fname in os.listdir(contracts_dir):
            if fname.lower().endswith('.md'):
                file_path = os.path.join(contracts_dir, fname)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                        # Escape curly braces to prevent template variable conflicts
                        file_content = file_content.replace('{', '{{').replace('}', '}}')
                        content += file_content + "\n\n"
                except Exception as e:
                    logger.warning(f"Could not load contract file {fname}: {e}")
                    continue
    
    if not content:
        logger.warning(f"No contract files found in {contracts_dir}")
        return ""
    
    return content

# Load the usage guide and API contracts content
usage_guide_content = load_usage_guide()
api_contracts_content = load_api_contracts()

# Create system message that includes the full usage guide and API contracts
system_message = f"""You are an AI agent that executes BDD scenarios by interacting with APIs. 

You have access to four tools:
- get_api(endpoint, params=None) - for GET requests
- post_api(endpoint, data) - for POST requests (data parameter is REQUIRED)
- put_api(endpoint, data) - for PUT requests (data parameter is REQUIRED)  
- delete_api(endpoint) - for DELETE requests

CRITICAL TOOL USAGE RULES:
1. For post_api and put_api: ALWAYS include both 'endpoint' AND 'data' parameters
2. Extract data from step descriptions carefully (email, password, etc.)
3. Use complete URLs from loaded contracts (e.g., https://api.stage.invitedekho.com/login)
4. Execute the API call ONCE and provide a summary of the result
5. Do NOT repeat the same API call multiple times
6. If a request fails (404, etc.), report the error and stop
7. Only use the available tools for API testing

EXAMPLE CORRECT USAGE:
- For login steps, extract email and password values and use post_api tool
- Always provide both endpoint parameter AND data parameter for POST requests
- Use complete URLs like https://api.stage.invitedekho.com/login for InviteDeKho API

COMPLETE USAGE GUIDE AND INSTRUCTIONS:
{usage_guide_content}

API CONTRACTS AND SCHEMA DOCUMENTATION:
{api_contracts_content}

Follow the usage guide and API contracts documentation exactly for parsing step descriptions, understanding required parameters, headers, and executing API calls. Use the contracts to know what data is required for each endpoint and what response formats to expect."""

# Create agent with tool calling support
prompt = ChatPromptTemplate.from_messages([
    ("system", system_message),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

# Initialize agent executor with tool support
agent_executor = None
try:
    use_ollama = os.getenv('USE_OLLAMA', 'false').lower() == 'true'
    
    if use_ollama:
        # Use simpler approach for Ollama compatibility
        from langchain.agents import initialize_agent, AgentType
        
        agent_executor = initialize_agent(
            tools=tools,
            llm=llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            max_iterations=3,
            early_stopping_method="generate"
        )
        logger.info("Successfully created ZERO_SHOT_REACT agent with Ollama")
    else:
        # Use modern tool-calling approach for OpenAI
        agent = create_tool_calling_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            max_iterations=3,
            early_stopping_method="generate"
        )
        logger.info("Successfully created tool-calling agent with OpenAI")
        
except Exception as e:
    logger.warning(f"Could not create agent: {e}. Will use text-based parsing fallback.")
    agent_executor = None

# --- Custom Exception ---
class AgentProcessingError(Exception):
    """Custom exception for errors during agent processing."""
    pass
# --- End Custom Exception ---

def run_scenario_step(step_description):
    """
    Runs a single BDD step using the AI agent with tool calling support.
    Falls back to text parsing if tool calling is not available.
    """
    logger.info(f"Attempting to execute BDD step: '{step_description}'")
    
    # Clear the global tool execution before running
    from api_tools import LAST_TOOL_EXECUTION
    LAST_TOOL_EXECUTION.update({
        "curl_command": None,
        "status_code": None,
        "body": None,
        "json_response": None,
        "tool_name": None,
        "error": None
    })
    
    try:
        if agent_executor is not None:
            # Use tool-calling agent if available
            logger.info("Using tool-calling agent")
            filtered_input = {"input": step_description}
            response = agent_executor.invoke(filtered_input)
            logger.info(f"Tool-calling agent response received")

            final_output = response.get('output', '') if isinstance(response, dict) else str(response)
            
            # Check for failure indicators in the response
            failure_phrases = ["i am unable to", "i cannot", "could not process", "failed to", "error occurred"]
            for phrase in failure_phrases:
                if phrase in final_output.lower():
                    error_message = f"Agent indicated failure: '{final_output}'"
                    logger.error(error_message)
                    raise AgentProcessingError(error_message)
        else:
            # Fallback to text-based parsing
            logger.info("Using text-based parsing fallback")
            response = _execute_step_with_ollama(step_description)

        # Return both the agent response and tool execution details
        return {
            'agent_response': response,
            'tool_execution': dict(LAST_TOOL_EXECUTION)  # Create a copy
        }
        
    except AgentProcessingError:
        raise
    except Exception as e:
        error_message = f"An unexpected error occurred while processing step: '{step_description}'"
        logger.error(error_message)
        logger.error(f"Error processing step '{step_description}': {type(e).__name__} - {str(e)}")
        raise AgentProcessingError(f"{error_message}. Original error: {type(e).__name__} - {str(e)}") from e

class Agent:
    """Enhanced Agent class that works with Ollama and tool calling"""
    
    def __init__(self):
        """Initialize the agent with loaded contracts and LLM configuration"""
        self.llm = get_llm()
        self.usage_guide = load_usage_guide()
        self.api_contracts = load_api_contracts()
        self.system_message = self._build_system_message()
        self.tools = tools
        
    def _build_system_message(self):
        """Build comprehensive system message with API contracts knowledge"""
        return f"""You are an intelligent API testing agent with comprehensive knowledge of API contracts and testing best practices.

AVAILABLE API TOOLS:
- get_api(endpoint, params=None) - for GET requests
- post_api(endpoint, data) - for POST requests (data parameter is REQUIRED)
- put_api(endpoint, data) - for PUT requests (data parameter is REQUIRED)  
- delete_api(endpoint) - for DELETE requests

CRITICAL INSTRUCTIONS:
1. For validation requests, analyze the data against API contracts
2. For test suggestions, use contract knowledge to create realistic data
3. For error analysis, provide specific, actionable recommendations
4. Always reference the API contracts for accurate field requirements

COMPLETE USAGE GUIDE:
{self.usage_guide}

API CONTRACTS AND SCHEMA DOCUMENTATION:
{self.api_contracts}

When responding to validation or testing questions, provide clear, specific guidance based on the API contracts."""
    
    def process_request(self, user_input: str) -> str:
        """Process a user request and return the response"""
        try:
            return self._process_with_ollama(user_input)
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            return f"Error processing request: {str(e)}"
    
    def _process_with_ollama(self, user_input: str) -> str:
        """Process request using Ollama"""
        full_prompt = f"{self.system_message}\n\nUser Request: {user_input}\n\nAnalyze this request using your API contracts knowledge and provide a helpful response. If this involves API testing, explain what should be done step by step.\n\nResponse:"
        
        try:
            response = self.llm.invoke(full_prompt)
            # Clean up response if needed
            if isinstance(response, str):
                return response.strip()
            else:
                return str(response).strip()
        except Exception as e:
            logger.error(f"Ollama processing error: {str(e)}")
            return f"Error processing request with Ollama: {str(e)}"

def _execute_step_with_ollama(step_description):
    """
    Execute API step using Ollama with text-based parsing
    This avoids function calling which Ollama doesn't support
    """
    import json
    import re
    from api_tools import get_api, post_api, put_api, delete_api, LAST_TOOL_EXECUTION
    
    step_lower = step_description.lower().strip()
    
    # Parse the step description to extract API call details
    method = None
    endpoint = None
    data = None
    params = None
    
    # Extract HTTP method
    for m in ['post', 'put', 'get', 'delete', 'patch']:
        if step_lower.startswith(m):
            method = m.upper()
            break
    
    if not method:
        return {
            'output': f"Could not determine HTTP method from step: {step_description}",
            'error': 'No valid HTTP method found'
        }
    
    # Extract endpoint
    endpoint_match = re.search(r'(post|put|get|delete|patch)\s+(/\S+)', step_lower)
    endpoint = endpoint_match.group(2) if endpoint_match else None
    
    if not endpoint:
        return {
            'output': f"Could not determine endpoint from step: {step_description}",
            'error': 'No valid endpoint found'
        }
    
    # Extract JSON data for POST/PUT requests
    if method in ['POST', 'PUT']:
        json_match = re.search(r'(?:with\s+(?:json\s+)?data|with\s+payload|with\s+body):\s*(\{.*\})', step_description, re.IGNORECASE)
        if json_match:
            try:
                data = json.loads(json_match.group(1))
            except json.JSONDecodeError as e:
                return {
                    'output': f"Invalid JSON data in step: {e}",
                    'error': f'JSON parsing error: {e}'
                }
        elif method in ['POST', 'PUT']:
            return {
                'output': f"Missing JSON data for {method} request",
                'error': f'No JSON data found for {method} request'
            }
    
    # Extract query parameters for GET requests
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
    
    # Execute the API call
    try:
        if method == 'GET':
            result = get_api(endpoint, params)
        elif method == 'POST':
            result = post_api(endpoint, data)
        elif method == 'PUT':
            result = put_api(endpoint, data)
        elif method == 'DELETE':
            result = delete_api(endpoint)
        else:
            return {
                'output': f"Unsupported HTTP method: {method}",
                'error': f'Method {method} not supported'
            }
        
        # Generate a response message
        response_msg = f"Successfully executed {method} {endpoint}"
        if LAST_TOOL_EXECUTION.get('status_code'):
            response_msg += f" (Status: {LAST_TOOL_EXECUTION['status_code']})"
        
        return {
            'output': response_msg,
            'result': result
        }
        
    except Exception as e:
        logger.error(f"Error executing {method} {endpoint}: {str(e)}")
        return {
            'output': f"Error executing {method} {endpoint}: {str(e)}",
            'error': str(e)
        }
