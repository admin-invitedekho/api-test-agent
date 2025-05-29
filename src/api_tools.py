# src/api_tools.py
import requests
import json
from langchain.tools import tool
import shlex # For safely quoting shell arguments

# API tools now rely on AI to provide complete URLs based on loaded contracts

# Global context to store the last tool execution results
# This allows step definitions to access detailed tool outputs
LAST_TOOL_EXECUTION = {
    "curl_command": None,
    "status_code": None,
    "body": None,
    "json_response": None,
    "tool_name": None,
    "error": None
}

def _construct_curl_command(method: str, endpoint: str, params: dict = None, data: dict = None, headers: dict = None) -> str:
    """Helper function to construct a curl command string."""
    # AI should provide complete URLs based on loaded contracts
    if not endpoint.startswith(('http://', 'https://')):
        raise ValueError(f"AI should provide complete URL, got: {endpoint}")
    
    full_url = endpoint
    curl_parts = ['curl', '-X', method]

    # Add headers
    if headers is None:
        headers = {} # Initialize if None
    if method in ["POST", "PUT"] and 'Content-Type' not in headers:
        headers['Content-Type'] = 'application/json' # Default for POST/PUT

    for key, value in headers.items():
        curl_parts.extend(['-H', shlex.quote(f'{key}: {value}')])

    if params:
        param_string = '&'.join([f'{key}={requests.utils.quote(str(value))}' for key, value in params.items()])
        full_url = f'{full_url}?{param_string}'
    
    curl_parts.append(shlex.quote(full_url))

    if data:
        curl_parts.extend(['-d', shlex.quote(json.dumps(data))])
    
    return ' '.join(curl_parts)

@tool
def get_api(endpoint: str, params: dict = None) -> dict:
    """Sends a GET request to the specified API endpoint.
       AI should provide complete URL based on loaded contracts (e.g., https://api.stage.invitedekho.com/login)"""
    global LAST_TOOL_EXECUTION
    request_headers = {"Accept": "application/json"}
    curl_command = _construct_curl_command('GET', endpoint, params=params, headers=request_headers)
    tool_result = {"curl_command": curl_command, "tool_name": "get_api", "endpoint": endpoint, "params": params}
    try:
        response = requests.get(endpoint, params=params, headers=request_headers)
        tool_result["status_code"] = response.status_code
        tool_result["body"] = response.text
        try:
            tool_result["json_response"] = response.json()
        except json.JSONDecodeError:
            tool_result["json_response"] = None
        response.raise_for_status()
        
        LAST_TOOL_EXECUTION.update(tool_result)
        return tool_result
    except requests.exceptions.RequestException as e:
        tool_result["error"] = str(e)
        if e.response is not None:
            tool_result["status_code"] = e.response.status_code
            tool_result["body"] = e.response.text
            try:
                tool_result["json_response"] = e.response.json()
            except json.JSONDecodeError:
                tool_result["json_response"] = None
        else:
            tool_result["status_code"] = "N/A"
            tool_result["body"] = "No response"
            tool_result["json_response"] = None
        
        LAST_TOOL_EXECUTION.update(tool_result)
        return tool_result

@tool
def post_api(endpoint: str, data: dict) -> dict:
    """Sends a POST request to the specified API endpoint with the given JSON data.
       AI should provide complete URL based on loaded contracts (e.g., https://api.stage.invitedekho.com/login)"""
    global LAST_TOOL_EXECUTION
    request_headers = {"Content-Type": "application/json", "Accept": "application/json"}
    curl_command = _construct_curl_command('POST', endpoint, data=data, headers=request_headers)
    tool_result = {"curl_command": curl_command, "tool_name": "post_api", "endpoint": endpoint, "data": data}
    try:
        response = requests.post(endpoint, json=data, headers=request_headers)
        tool_result["status_code"] = response.status_code
        tool_result["body"] = response.text
        try:
            tool_result["json_response"] = response.json()
        except json.JSONDecodeError:
            tool_result["json_response"] = None
        response.raise_for_status()
        
        LAST_TOOL_EXECUTION.update(tool_result)
        return tool_result
    except requests.exceptions.RequestException as e:
        tool_result["error"] = str(e)
        if e.response is not None:
            tool_result["status_code"] = e.response.status_code
            tool_result["body"] = e.response.text
            try:
                tool_result["json_response"] = e.response.json()
            except json.JSONDecodeError:
                tool_result["json_response"] = None
        else:
            tool_result["status_code"] = "N/A"
            tool_result["body"] = "No response"
            tool_result["json_response"] = None
        
        LAST_TOOL_EXECUTION.update(tool_result)
        return tool_result

@tool
def put_api(endpoint: str, data: dict) -> dict:
    """Sends a PUT request to the specified API endpoint with the given JSON data.
       AI should provide complete URL based on loaded contracts (e.g., https://jsonplaceholder.typicode.com/users/1)"""
    global LAST_TOOL_EXECUTION
    request_headers = {"Content-Type": "application/json", "Accept": "application/json"}
    curl_command = _construct_curl_command('PUT', endpoint, data=data, headers=request_headers)
    tool_result = {"curl_command": curl_command, "tool_name": "put_api", "endpoint": endpoint, "data": data}
    try:
        response = requests.put(endpoint, json=data, headers=request_headers)
        tool_result["status_code"] = response.status_code
        tool_result["body"] = response.text
        try:
            tool_result["json_response"] = response.json()
        except json.JSONDecodeError:
            tool_result["json_response"] = None
        response.raise_for_status()
        
        LAST_TOOL_EXECUTION.update(tool_result)
        return tool_result
    except requests.exceptions.RequestException as e:
        tool_result["error"] = str(e)
        if e.response is not None:
            tool_result["status_code"] = e.response.status_code
            tool_result["body"] = e.response.text
            try:
                tool_result["json_response"] = e.response.json()
            except json.JSONDecodeError:
                tool_result["json_response"] = None
        else:
            tool_result["status_code"] = "N/A"
            tool_result["body"] = "No response"
            tool_result["json_response"] = None
        
        LAST_TOOL_EXECUTION.update(tool_result)
        return tool_result

@tool
def delete_api(endpoint: str) -> dict:
    """Sends a DELETE request to the specified API endpoint.
       AI should provide complete URL based on loaded contracts (e.g., https://jsonplaceholder.typicode.com/users/1)"""
    global LAST_TOOL_EXECUTION
    request_headers = {"Accept": "application/json"}
    curl_command = _construct_curl_command('DELETE', endpoint, headers=request_headers)
    tool_result = {"curl_command": curl_command, "tool_name": "delete_api", "endpoint": endpoint}
    try:
        response = requests.delete(endpoint, headers=request_headers)
        tool_result["status_code"] = response.status_code
        tool_result["body"] = response.text

        # For DELETE, 204 No Content is common
        if response.status_code != 204 and response.text:
            try:
                tool_result["json_response"] = response.json()
            except json.JSONDecodeError:
                tool_result["json_response"] = None
        else:
            tool_result["json_response"] = None
        
        response.raise_for_status()
        
        LAST_TOOL_EXECUTION.update(tool_result)
        return tool_result
    except requests.exceptions.RequestException as e:
        tool_result["error"] = str(e)
        if e.response is not None:
            tool_result["status_code"] = e.response.status_code
            tool_result["body"] = e.response.text
            try:
                tool_result["json_response"] = e.response.json()
            except json.JSONDecodeError:
                tool_result["json_response"] = None
        else:
            tool_result["status_code"] = "N/A"
            tool_result["body"] = "No response"
            tool_result["json_response"] = None
        
        LAST_TOOL_EXECUTION.update(tool_result)
        return tool_result
