# src/agent.py
import os
import logging
import traceback # Added for full traceback logging
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.schema import SystemMessage, HumanMessage
import sys
import os
# Add the src directory to the Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from api_tools import get_api, post_api, put_api, delete_api

from dotenv import load_dotenv

load_dotenv()

# --- Logging Setup ---
logging.basicConfig(level=logging.WARNING, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# --- End Logging Setup ---

# Ensure your OPENAI_API_KEY is set in your .env file or environment variables

llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0)

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

# Load the usage guide content
usage_guide_content = load_usage_guide()

# Create system message that includes the full usage guide
system_message = f"""You are an AI agent that executes BDD scenarios by interacting with APIs. 

You have access to four tools:
- get_api(endpoint, params=None) - for GET requests
- post_api(endpoint, data) - for POST requests (data parameter is REQUIRED)
- put_api(endpoint, data) - for PUT requests (data parameter is REQUIRED)  
- delete_api(endpoint) - for DELETE requests

CRITICAL: For POST and PUT requests, you MUST extract JSON data from step descriptions and include both endpoint AND data parameters.

IMPORTANT: 
1. Execute the API call ONCE and provide a summary of the result
2. Do NOT repeat the same API call multiple times
3. If a request fails (404, etc.), report the error and stop
4. Only use the available tools for API testing - do not attempt requests outside of API testing scope

COMPLETE USAGE GUIDE AND INSTRUCTIONS:
{usage_guide_content}

Follow the guide above exactly for parsing step descriptions and executing API calls."""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_message),
    ("user", "{input}"),
    ("assistant", "{agent_scratchpad}"),
])

try:
    # Try the functions agent approach which is more stable
    agent = create_openai_functions_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=True,
        max_iterations=3,  # Prevent infinite loops
        early_stopping_method="generate"  # Stop after first successful tool call
    )
except Exception as e:
    logger.error(f"Failed to create functions agent: {e}")
    # Fallback to a manual approach
    from langchain.agents import initialize_agent, AgentType
    agent_executor = initialize_agent(
        tools, 
        llm, 
        agent=AgentType.OPENAI_FUNCTIONS,
        verbose=True
    )

# --- Custom Exception ---
class AgentProcessingError(Exception):
    """Custom exception for errors during agent processing."""
    pass
# --- End Custom Exception ---

def run_scenario_step(step_description):
    """
    Runs a single BDD step using the AI agent, with error handling and logging.
    Returns both the agent response and the last tool execution details.
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
        # Filter input to only include expected variables
        filtered_input = {"input": step_description}
        response = agent_executor.invoke(filtered_input)
        logger.info(f"Raw agent response: {response}")

        # Since we're not using intermediate_steps, we'll rely on the agent's final output
        # and any error signals from the tools themselves
        final_output = response.get('output', '') if isinstance(response, dict) else str(response)
        
        # Heuristic check for agent's inability to proceed from final output
        failure_phrases = ["i am unable to", "i cannot", "could not process", "failed to", "error occurred"]
        for phrase in failure_phrases:
            if phrase in final_output.lower():
                error_message = f"Agent indicated failure in its final output: '{final_output}'"
                logger.error(error_message)
                raise AgentProcessingError(error_message)

        # Return both the agent response and tool execution details
        return {
            'agent_response': response,
            'tool_execution': dict(LAST_TOOL_EXECUTION)  # Create a copy
        }
    except AgentProcessingError: # Re-raise AgentProcessingError directly
        raise
    except Exception as e:
        # Catch any other exceptions (Langchain internal, network issues, etc.)
        error_message = f"An unexpected error occurred while processing step: '{step_description}'"
        logger.error(error_message)
        # Log the full traceback for unexpected errors
        logger.error(f"Error processing step '{step_description}': {type(e).__name__} - {str(e)}")
        raise AgentProcessingError(f"{error_message}. Original error: {type(e).__name__} - {str(e)}") from e
