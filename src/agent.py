# src/agent.py
import os
import logging
import traceback # Added for full traceback logging
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.schema import SystemMessage, HumanMessage
from .api_tools import get_api, post_api, put_api, delete_api # Changed to relative import

from dotenv import load_dotenv

load_dotenv()

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)
# --- End Logging Setup ---

# Ensure your OPENAI_API_KEY is set in your .env file or environment variables

llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0)

tools = [get_api, post_api, put_api, delete_api]

# Create a simpler prompt template using the legacy functions agent approach
system_message = """You are an AI agent that executes BDD scenarios by interacting with APIs. Use the provided tools to make API calls.

CRITICAL TOOL USAGE:
1. get_api(endpoint, params=None) - for GET requests
2. post_api(endpoint, data) - for POST requests (data parameter is REQUIRED)
3. put_api(endpoint, data) - for PUT requests (data parameter is REQUIRED)  
4. delete_api(endpoint) - for DELETE requests

JSON EXTRACTION FOR POST/PUT:
When you see input like "POST /users with JSON data: {\"name\": \"John\", \"email\": \"john@email.com\"}", you MUST:
1. Extract the endpoint: "/users"
2. Extract the JSON data: {"name": "John", "email": "john@email.com"}
3. Call post_api(endpoint="/users", data={"name": "John", "email": "john@email.com"})

EXACT EXAMPLES:
Input: "POST /posts with JSON data: {\"title\": \"Test\", \"body\": \"Content\", \"userId\": 1}"
→ Call: post_api(endpoint="/posts", data={"title": "Test", "body": "Content", "userId": 1})

Input: "PUT /users/1 with JSON data: {\"name\": \"Updated Name\"}"
→ Call: put_api(endpoint="/users/1", data={"name": "Updated Name"})

Input: "GET /users/1"
→ Call: get_api(endpoint="/users/1")

IMPORTANT: For POST and PUT requests, the data parameter is MANDATORY. Always extract the JSON object from the input and pass it as the data parameter."""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_message),
    ("user", "{input}"),
])

try:
    # Try the functions agent approach which is more stable
    agent = create_openai_functions_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
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
    """
    logger.info(f"Attempting to execute BDD step: '{step_description}'")
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

        return response
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
        logger.info(f"Example 1 Succeeded. Agent output: {response1.get('output') if isinstance(response1, dict) else response1}")
    except AgentProcessingError as e:
        logger.error(f"Example 1 Failed. AgentProcessingError: {e}")
    except Exception as e:
        logger.error(f"Example 1 Failed. Unexpected Exception: {e}\n{traceback.format_exc()}")

    # Example 2: POST request with improved formatting
    step2_desc = 'POST /posts with JSON data: {"title": "My Test Post via Agent", "body": "This is some test content.", "userId": 5}'
    logger.info(f"\n--- Example 2: {step2_desc} ---")
    try:
        response2 = run_scenario_step(step2_desc)
        logger.info(f"Example 2 Succeeded. Agent output: {response2.get('output') if isinstance(response2, dict) else response2}")
    except AgentProcessingError as e:
        logger.error(f"Example 2 Failed. AgentProcessingError: {e}")
    except Exception as e:
        logger.error(f"Example 2 Failed. Unexpected Exception: {e}\n{traceback.format_exc()}")

    # Example 3: Step designed to potentially cause a tool error (e.g., bad endpoint)
    step3_desc = 'Get data from a clearly invalid endpoint /nonexistent/endpoint/12345'
    logger.info(f"\n--- Example 3: {step3_desc} (expecting tool error) ---")
    try:
        response3 = run_scenario_step(step3_desc)
        logger.info(f"Example 3 Succeeded (unexpectedly). Agent output: {response3.get('output') if isinstance(response3, dict) else response3}")
    except AgentProcessingError as e:
        logger.error(f"Example 3 Failed as expected. AgentProcessingError: {e}")
    except Exception as e:
        logger.error(f"Example 3 Failed. Unexpected Exception: {e}\n{traceback.format_exc()}")

    # Example 4: Step that might cause the agent to say it cannot proceed
    step4_desc = "Can you book a flight to Mars for tomorrow?" # A task the agent cannot do with current tools
    logger.info(f"\n--- Example 4: {step4_desc} (expecting agent inability) ---")
    try:
        response4 = run_scenario_step(step4_desc)
        logger.info(f"Example 4 Succeeded (agent might just say it can't do it, which is a valid response but we test for failure phrases). Agent output: {response4.get('output') if isinstance(response4, dict) else response4}")
        # If the agent's output contains a failure phrase, run_scenario_step should have raised an error.
        # If it didn't, this log indicates the heuristic might need adjustment or the agent's response was too nuanced.
    except AgentProcessingError as e:
        logger.error(f"Example 4 Failed as expected (or due to heuristic). AgentProcessingError: {e}")
    except Exception as e:
        logger.error(f"Example 4 Failed. Unexpected Exception: {e}\n{traceback.format_exc()}")

    logger.info("\nAgent execution examples complete.")
    logger.info("Review the console logs for details on successes and failures.")
    logger.info("If using with Behave, AgentProcessingError should propagate and fail the Behave step.")
