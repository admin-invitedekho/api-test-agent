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
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)
# --- End Logging Setup ---

# Ensure your OPENAI_API_KEY is set in your .env file or environment variables

llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0)

tools = [get_api, post_api, put_api, delete_api]

# Create system message that references the usage guide
system_message = """You are an AI agent that executes BDD scenarios by interacting with APIs. 

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

Refer to the AI_AGENT_USAGE_GUIDE.md for detailed parsing instructions and examples."""

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
        logger.error(f"Exception type: {type(e).__name__}, Message: {str(e)}")
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        raise AgentProcessingError(f"{error_message}. Original error: {type(e).__name__} - {str(e)}") from e


if __name__ == '__main__':
    logger.info("Starting agent execution examples with error handling.")

    # Example 1: Successful GET request
    step1_desc = 'Get the user with ID 2 from the endpoint /users/2'
    logger.info(f"\n--- Example 1: {step1_desc} ---")
    try:
        response1 = run_scenario_step(step1_desc)
        agent_output = response1['agent_response'].get('output') if isinstance(response1['agent_response'], dict) else str(response1['agent_response'])
        logger.info(f"Example 1 Succeeded. Agent output: {agent_output}")
        logger.info(f"Tool execution: {response1['tool_execution']}")
    except AgentProcessingError as e:
        logger.error(f"Example 1 Failed. AgentProcessingError: {e}")
    except Exception as e:
        logger.error(f"Example 1 Failed. Unexpected Exception: {e}\n{traceback.format_exc()}")

    # Example 2: POST request with improved formatting
    step2_desc = 'POST /posts with JSON data: {"title": "My Test Post via Agent", "body": "This is some test content.", "userId": 5}'
    logger.info(f"\n--- Example 2: {step2_desc} ---")
    try:
        response2 = run_scenario_step(step2_desc)
        agent_output = response2['agent_response'].get('output') if isinstance(response2['agent_response'], dict) else str(response2['agent_response'])
        logger.info(f"Example 2 Succeeded. Agent output: {agent_output}")
        logger.info(f"Tool execution: {response2['tool_execution']}")
    except AgentProcessingError as e:
        logger.error(f"Example 2 Failed. AgentProcessingError: {e}")
    except Exception as e:
        logger.error(f"Example 2 Failed. Unexpected Exception: {e}\n{traceback.format_exc()}")

    # Example 3: Step designed to potentially cause a tool error (e.g., bad endpoint)
    step3_desc = 'Get data from a clearly invalid endpoint /nonexistent/endpoint/12345'
    logger.info(f"\n--- Example 3: {step3_desc} (expecting tool error) ---")
    try:
        response3 = run_scenario_step(step3_desc)
        agent_output = response3['agent_response'].get('output') if isinstance(response3['agent_response'], dict) else str(response3['agent_response'])
        logger.info(f"Example 3 Succeeded (unexpectedly). Agent output: {agent_output}")
        logger.info(f"Tool execution: {response3['tool_execution']}")
    except AgentProcessingError as e:
        logger.error(f"Example 3 Failed as expected. AgentProcessingError: {e}")
    except Exception as e:
        logger.error(f"Example 3 Failed. Unexpected Exception: {e}\n{traceback.format_exc()}")

    # Example 4: Step that might cause the agent to say it cannot proceed
    step4_desc = "Can you book a flight to Mars for tomorrow?" # A task the agent cannot do with current tools
    logger.info(f"\n--- Example 4: {step4_desc} (expecting agent inability) ---")
    try:
        response4 = run_scenario_step(step4_desc)
        agent_output = response4['agent_response'].get('output') if isinstance(response4['agent_response'], dict) else str(response4['agent_response'])
        logger.info(f"Example 4 Succeeded (agent might just say it can't do it, which is a valid response but we test for failure phrases). Agent output: {agent_output}")
        logger.info(f"Tool execution: {response4['tool_execution']}")
        # If the agent's output contains a failure phrase, run_scenario_step should have raised an error.
        # If it didn't, this log indicates the heuristic might need adjustment or the agent's response was too nuanced.
    except AgentProcessingError as e:
        logger.error(f"Example 4 Failed as expected (or due to heuristic). AgentProcessingError: {e}")
    except Exception as e:
        logger.error(f"Example 4 Failed. Unexpected Exception: {e}\n{traceback.format_exc()}")

    logger.info("\nAgent execution examples complete.")
    logger.info("Review the console logs for details on successes and failures.")
    logger.info("If using with Behave, AgentProcessingError should propagate and fail the Behave step.")
