# features/steps/api_steps.py
import json
import allure
from behave import given, when, then
from src.agent import run_scenario_step, AgentProcessingError # Import AgentProcessingError
from src.api_tools import LAST_TOOL_EXECUTION # Import the global context

# Corrected regular expressions for step definitions
@given('the API endpoint "{endpoint}"')
def step_given_api_endpoint(context, endpoint):
    context.api_endpoint = endpoint

@given('the request body is')
def step_given_request_body(context):
    # Assuming the request body is provided as a JSON string in the feature file
    context.request_body = context.text

@when('I send a {method} request')
def step_when_send_request(context, method):
    context.response = None
    context.step_error = None
    try:
        # Here, method should be 'GET', 'POST', etc. as per the feature file
        # We use the context.api_endpoint and context.request_body set in the @given steps
        if method.upper() == 'POST':
            # Format the request to make JSON extraction easier for the agent
            if hasattr(context, 'request_body') and context.request_body:
                # Clean up the request body and format it properly
                request_body = context.request_body.strip()
                step_description = f"POST {context.api_endpoint} with JSON data: {request_body}"
            else:
                step_description = f"POST {context.api_endpoint}"
            context.response = run_scenario_step(step_description)
        elif method.upper() == 'PUT':
            # Add PUT support with similar formatting
            if hasattr(context, 'request_body') and context.request_body:
                request_body = context.request_body.strip()
                step_description = f"PUT {context.api_endpoint} with JSON data: {request_body}"
            else:
                step_description = f"PUT {context.api_endpoint}"
            context.response = run_scenario_step(step_description)
        elif method.upper() == 'DELETE':
            context.response = run_scenario_step(f"DELETE {context.api_endpoint}")
        elif method.upper() == 'GET':
            context.response = run_scenario_step(f"GET {context.api_endpoint}")
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        allure.attach(str(context.response), name="Raw Agent Response", attachment_type=allure.attachment_type.TEXT)
        
        # Use the global context instead of intermediate_steps
        if LAST_TOOL_EXECUTION['tool_name']:
            allure.attach(str(LAST_TOOL_EXECUTION), name="Tool Execution Details", attachment_type=allure.attachment_type.JSON)
            
            if LAST_TOOL_EXECUTION.get('curl_command'):
                allure.attach(LAST_TOOL_EXECUTION['curl_command'], name="cURL Command", attachment_type=allure.attachment_type.TEXT)
            
            if LAST_TOOL_EXECUTION.get('status_code') is not None:
                allure.attach(str(LAST_TOOL_EXECUTION['status_code']), name="API Status Code", attachment_type=allure.attachment_type.TEXT)
            
            if LAST_TOOL_EXECUTION.get('body') is not None:
                # Try to pretty-print if JSON, otherwise attach as text
                try:
                    pretty_body = json.dumps(json.loads(LAST_TOOL_EXECUTION['body']), indent=2)
                    allure.attach(pretty_body, name="API Response Body (Formatted)", attachment_type=allure.attachment_type.JSON)
                except (json.JSONDecodeError, TypeError):
                    allure.attach(str(LAST_TOOL_EXECUTION['body']), name="API Response Body (Raw)", attachment_type=allure.attachment_type.TEXT)
            
            # If the tool itself reported an error, attach it
            if LAST_TOOL_EXECUTION.get('error'):
                allure.attach(str(LAST_TOOL_EXECUTION['error']), name="Tool Execution Error", attachment_type=allure.attachment_type.TEXT)

        # Attach final agent output if available
        if context.response and 'output' in context.response:
            allure.attach(str(context.response['output']), name="Agent Final Output", attachment_type=allure.attachment_type.TEXT)

    except AgentProcessingError as e:
        context.step_error = e
        allure.attach(str(e), name="Agent Processing Error", attachment_type=allure.attachment_type.TEXT)
        # The error will be asserted in a @then step or will naturally fail the test here.
        # For immediate failure and clear reporting, we re-raise it.
        raise # This ensures Behave marks the step as failed
    except Exception as e:
        context.step_error = e
        allure.attach(str(e), name="Unexpected Step Execution Error", attachment_type=allure.attachment_type.TEXT)
        raise # This ensures Behave marks the step as failed

@then('the response status code should be {status_code:d}')
@allure.step("Assert API response status code is {status_code}")
def step_impl(context, status_code):
    if context.step_error:
        # If an error occurred in the @when step, this @then step should not proceed with assertions
        # as the context might not be as expected. The test has already failed.
        # We can optionally log or attach the pending assertion here for clarity if needed.
        allure.attach(f"Skipping status code assertion due to previous error: {context.step_error}", 
                      name="Assertion Skipped", attachment_type=allure.attachment_type.TEXT)
        # Depending on Behave's behavior with re-raised exceptions, this might not be strictly necessary
        # but it makes the report clearer.
        assert False, f"Step failed prior to status code assertion: {context.step_error}"
        return

    assert LAST_TOOL_EXECUTION['tool_name'], "No tool execution found for status code check."
    actual_status_code = LAST_TOOL_EXECUTION.get('status_code')
    allure.attach(str(actual_status_code), name="Actual Status Code for Assertion", attachment_type=allure.attachment_type.TEXT)
    allure.attach(str(status_code), name="Expected Status Code for Assertion", attachment_type=allure.attachment_type.TEXT)
    assert actual_status_code == status_code, \
        f"Expected status code {status_code}, but got {actual_status_code}. Tool output: {LAST_TOOL_EXECUTION}"

@then('the response should contain "{expected_content}"')
@allure.step("Assert API response body contains '{expected_content}'")
def step_impl(context, expected_content):
    if context.step_error:
        allure.attach(f"Skipping body content assertion due to previous error: {context.step_error}", 
                      name="Assertion Skipped", attachment_type=allure.attachment_type.TEXT)
        assert False, f"Step failed prior to body content assertion: {context.step_error}"
        return

    assert LAST_TOOL_EXECUTION['tool_name'], "No tool execution found for body check."
    response_body = str(LAST_TOOL_EXECUTION.get('body', '')) # Ensure it's a string
    allure.attach(response_body, name="Actual Response Body for Assertion", attachment_type=allure.attachment_type.TEXT)
    allure.attach(expected_content, name="Expected Text in Body for Assertion", attachment_type=allure.attachment_type.TEXT)
    assert expected_content in response_body, \
        f"Expected text '{expected_content}' not found in response body. Body: '{response_body}'"

@then('the API response body should be the JSON {expected_json_str}')
@allure.step("Assert API response body is JSON: {expected_json_str}")
def step_impl(context, expected_json_str):
    if context.step_error:
        allure.attach(f"Skipping JSON body assertion due to previous error: {context.step_error}", 
                      name="Assertion Skipped", attachment_type=allure.attachment_type.TEXT)
        assert False, f"Step failed prior to JSON body assertion: {context.step_error}"
        return

    assert LAST_TOOL_EXECUTION['tool_name'], "No tool execution found for JSON body check."
    
    try:
        expected_json = json.loads(expected_json_str)
    except json.JSONDecodeError as e:
        assert False, f"Invalid expected JSON string provided in Gherkin step: {expected_json_str}. Error: {e}"

    actual_json_response = LAST_TOOL_EXECUTION.get('json_response') # This should be pre-parsed by the tool
    if actual_json_response is None:
        # If json_response is None, try to parse the raw body
        raw_body = LAST_TOOL_EXECUTION.get('body')
        if raw_body:
            try:
                actual_json_response = json.loads(raw_body)
            except json.JSONDecodeError:
                assert False, f"Response body is not valid JSON. Raw body: '{raw_body}'"
        else:
            assert False, "Response body is empty, cannot compare with JSON."

    allure.attach(json.dumps(actual_json_response, indent=2), name="Actual JSON Response for Assertion", attachment_type=allure.attachment_type.JSON)
    allure.attach(json.dumps(expected_json, indent=2), name="Expected JSON for Assertion", attachment_type=allure.attachment_type.JSON)
    
    assert actual_json_response == expected_json, \
        f"Expected JSON response {expected_json}, but got {actual_json_response}."

@then('the step should fail with a message containing "{expected_error_message_part}"')
@allure.step("Assert step failed with message containing '{expected_error_message_part}'")
def step_impl(context, expected_error_message_part):
    assert context.step_error is not None, "Step was expected to fail, but it did not."
    error_message = str(context.step_error)
    allure.attach(error_message, name="Actual Error Message", attachment_type=allure.attachment_type.TEXT)
    allure.attach(expected_error_message_part, name="Expected Error Message Part", attachment_type=allure.attachment_type.TEXT)
    assert expected_error_message_part in error_message, \
        f"Step failed, but error message '{error_message}' did not contain expected part '{expected_error_message_part}'."

@then('the agent output should indicate it cannot perform the action')
@allure.step("Assert agent output indicates inability to perform action")
def step_impl(context):
    if context.step_error:
        # This case might occur if run_scenario_step's heuristic for "agent cannot proceed" worked
        # and raised an AgentProcessingError.
        allure.attach(f"Step failed as expected with AgentProcessingError: {context.step_error}", 
                      name="Failure Confirmation", attachment_type=allure.attachment_type.TEXT)
        # We can check if the error message matches expectations if needed, similar to the step above.
        # For now, just confirm an error occurred.
        assert isinstance(context.step_error, AgentProcessingError), \
            f"Expected AgentProcessingError due to agent inability, but got {type(context.step_error)}"
        return

    # If no AgentProcessingError was raised by run_scenario_step, 
    # we check the agent's final output directly.
    assert context.response and 'output' in context.response, \
        "No agent output found to check for inability message."
    
    agent_final_output = str(context.response['output']).lower()
    allure.attach(agent_final_output, name="Agent Final Output for Inability Check", attachment_type=allure.attachment_type.TEXT)
    
    # Define phrases that indicate the agent cannot perform the action
    # These should align with the heuristic in run_scenario_step or be more general.
    inability_phrases = ["i am unable to", "i cannot", "i do not have the tools to", "i can't help with that"]
    
    can_perform_action = True
    for phrase in inability_phrases:
        if phrase in agent_final_output:
            can_perform_action = False
            break
    
    assert not can_perform_action, \
        f"Agent output '{agent_final_output}' did not clearly indicate inability to perform the action. Expected one of {inability_phrases}."
