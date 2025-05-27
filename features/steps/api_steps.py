from behave import given, when, then, step
import json
import requests
import re

# Additional step definitions for complex integration scenarios

@given('the API base URL is "{url}"')
def step_set_api_base_url(context, url):
    """Set the base URL for API requests."""
    context.base_url = url
    context.response_history = []
    print(f"Set API base URL to: {url}")

@given('I execute API request "{request_type}" with parameters')
@when('I execute API request "{request_type}" with parameters')
def step_execute_api_request(context, request_type):
    """Execute an API request with the given parameters."""
    import json
    parameters = json.loads(context.text)
    
    # Interpolate variables from previous responses
    parameters = interpolate_variables(parameters, context.response_history)
    
    # Execute the API request
    response = execute_api_request(context.base_url, request_type, parameters)
    
    # Store response in history
    context.last_response = response
    context.response_history.append(response)
    
    print(f"Executed {request_type} request to {parameters.get('endpoint', '')}")
    print(f"Response status: {response.get('status_code', 'N/A')}")

@then('the response status should be {expected_status:d}')
def step_check_response_status(context, expected_status):
    """Check that the response status matches the expected value."""
    actual_status = context.last_response.get('status_code')
    assert actual_status == expected_status, f"Expected status {expected_status}, got {actual_status}"
    print(f"✓ Response status is {actual_status}")

# Order matters: more specific patterns first to avoid ambiguity
@then('the response should contain field "{field_path}" with value "{expected_value}"')
def step_check_response_field_value(context, field_path, expected_value):
    """Check that a response field has a specific value."""
    response_data = context.last_response.get('data', {})
    field_value = get_nested_field(response_data, field_path)
    assert str(field_value) == expected_value, f"Field '{field_path}' has value '{field_value}', expected '{expected_value}'"
    print(f"✓ Field '{field_path}' has expected value: {expected_value}")

@then('the response should contain field "{field_path}" with numeric value')
def step_check_response_field_numeric(context, field_path):
    """Check that a response field contains a numeric value."""
    response_data = context.last_response.get('data', {})
    field_value = get_nested_field(response_data, field_path)
    assert isinstance(field_value, (int, float)), f"Field '{field_path}' is not numeric, got {type(field_value)}"
    print(f"✓ Field '{field_path}' is numeric with value: {field_value}")

@then('the response should contain field "{field_path}"')
def step_check_response_contains_field_basic(context, field_path):
    """Check that the response contains a specific field (supports dot notation)."""
    response_data = context.last_response.get('data', {})
    field_value = get_nested_field(response_data, field_path)
    assert field_value is not None, f"Field '{field_path}' not found in response"
    print(f"✓ Response contains field '{field_path}' with value: {field_value}")

@then('the response field "{field_path}" should be {expected_value}')
def step_check_response_field_boolean_or_value(context, field_path, expected_value):
    """Check that a response field has a specific boolean or other value."""
    response_data = context.last_response.get('data', {})
    field_value = get_nested_field(response_data, field_path)
    
    # Convert string representations to actual values
    if expected_value.lower() == 'true':
        expected_value = True
    elif expected_value.lower() == 'false':
        expected_value = False
    elif expected_value.isdigit():
        expected_value = int(expected_value)
    
    assert field_value == expected_value, f"Field '{field_path}' has value '{field_value}', expected '{expected_value}'"
    print(f"✓ Field '{field_path}' has expected value: {expected_value}")

@then('the response field "{field_path}" should contain "{substring}"')
def step_check_response_field_contains(context, field_path, substring):
    """Check that a response field contains a specific substring."""
    response_data = context.last_response.get('data', {})
    field_value = str(get_nested_field(response_data, field_path))
    assert substring in field_value, f"Field '{field_path}' value '{field_value}' does not contain '{substring}'"
    print(f"✓ Field '{field_path}' contains '{substring}'")

@then('the response should be an array')
def step_check_response_is_array(context):
    """Check that the response is an array."""
    response_data = context.last_response.get('data')
    assert isinstance(response_data, list), f"Response is not an array, got {type(response_data)}"
    print(f"✓ Response is an array with {len(response_data)} elements")

@then('the response should be an array with length greater than {min_length:d}')
def step_check_response_array_length_greater(context, min_length):
    """Check that the response array has more than a specified number of elements."""
    response_data = context.last_response.get('data')
    assert isinstance(response_data, list), f"Response is not an array, got {type(response_data)}"
    assert len(response_data) > min_length, f"Array length {len(response_data)} is not greater than {min_length}"
    print(f"✓ Response array has {len(response_data)} elements (> {min_length})")

# Cross-response comparison step definitions

@then('the response field "{field_path}" should equal the previous response field "{prev_field_path}"')
def step_check_field_equals_previous(context, field_path, prev_field_path):
    """Check that a field equals a field from the previous response."""
    current_data = context.last_response.get('data', {})
    current_value = get_nested_field(current_data, field_path)
    
    if len(context.response_history) < 2:
        raise AssertionError("No previous response available for comparison")
    
    previous_data = context.response_history[-2].get('data', {})
    previous_value = get_nested_field(previous_data, prev_field_path)
    
    # Convert both values to strings for comparison to handle type differences
    current_str = str(current_value) if current_value is not None else 'None'
    previous_str = str(previous_value) if previous_value is not None else 'None'
    
    assert current_str == previous_str, f"Current field '{field_path}' = '{current_str}' != previous '{prev_field_path}' = '{previous_str}'"
    print(f"✓ Field '{field_path}' ({current_str}) equals previous field '{prev_field_path}' ({previous_str})")

@then('the response field "{field_path}" should equal the second-to-last response field "{prev_field_path}"')
def step_check_field_equals_second_to_last(context, field_path, prev_field_path):
    """Check that a field equals a field from the second-to-last response."""
    current_data = context.last_response.get('data', {})
    current_value = get_nested_field(current_data, field_path)
    
    if len(context.response_history) < 3:
        raise AssertionError("Not enough responses for second-to-last comparison")
    
    second_to_last_data = context.response_history[-3].get('data', {})
    second_to_last_value = get_nested_field(second_to_last_data, prev_field_path)
    
    # Convert both values to strings for comparison to handle type differences
    current_str = str(current_value) if current_value is not None else 'None'
    second_to_last_str = str(second_to_last_value) if second_to_last_value is not None else 'None'
    
    assert current_str == second_to_last_str, f"Current field '{field_path}' = '{current_str}' != second-to-last '{prev_field_path}' = '{second_to_last_str}'"
    print(f"✓ Field '{field_path}' ({current_str}) equals second-to-last field '{prev_field_path}' ({second_to_last_str})")

@then('the response field "{field_path}" should equal the third-to-last response field "{prev_field_path}"')
def step_check_field_equals_third_to_last(context, field_path, prev_field_path):
    """Check that a field equals a field from the third-to-last response."""
    current_data = context.last_response.get('data', {})
    current_value = get_nested_field(current_data, field_path)
    
    if len(context.response_history) < 4:
        raise AssertionError("Not enough responses for third-to-last comparison")
    
    third_to_last_data = context.response_history[-4].get('data', {})
    third_to_last_value = get_nested_field(third_to_last_data, prev_field_path)
    
    # Convert both values to strings for comparison to handle type differences
    current_str = str(current_value) if current_value is not None else 'None'
    third_to_last_str = str(third_to_last_value) if third_to_last_value is not None else 'None'
    
    assert current_str == third_to_last_str, f"Current field '{field_path}' = '{current_str}' != third-to-last '{prev_field_path}' = '{third_to_last_str}'"
    print(f"✓ Field '{field_path}' ({current_str}) equals third-to-last field '{prev_field_path}' ({third_to_last_str})")

@then('the response field "{field_path}" should equal the second-to-last response array first element field "{prev_field_path}"')
def step_check_field_equals_array_element(context, field_path, prev_field_path):
    """Check that a field equals a field from the first element of an array in the second-to-last response."""
    current_data = context.last_response.get('data', {})
    current_value = get_nested_field(current_data, field_path)
    
    if len(context.response_history) < 3:
        raise AssertionError("Not enough responses for second-to-last array comparison")
    
    second_to_last_data = context.response_history[-3].get('data', [])
    if not isinstance(second_to_last_data, list) or len(second_to_last_data) == 0:
        raise AssertionError("Second-to-last response is not a non-empty array")
    
    array_element_value = get_nested_field(second_to_last_data[0], prev_field_path)
    
    # Convert both values to strings for comparison to handle type differences  
    current_str = str(current_value) if current_value is not None else 'None'
    array_element_str = str(array_element_value) if array_element_value is not None else 'None'
    
    assert current_str == array_element_str, f"Current field '{field_path}' = '{current_str}' != array element '{prev_field_path}' = '{array_element_str}'"
    print(f"✓ Field '{field_path}' ({current_str}) equals array element field '{prev_field_path}' ({array_element_str})")

# Enhanced helper functions for complex scenarios

def array_length(array_data):
    """Helper function to get the length of an array."""
    if isinstance(array_data, list):
        return len(array_data)
    return 0

def interpolate_variables(data, response_history):
    """Enhanced variable interpolation with support for array functions and complex references."""
    import json
    import re
    
    def replace_variable(match):
        var_path = match.group(1)
        
        # Handle special functions
        if var_path.startswith('array_length('):
            # Extract the array reference
            array_ref = var_path[13:-1]  # Remove 'array_length(' and ')'
            if array_ref == 'response':
                if response_history:
                    return str(array_length(response_history[-1].get('data', [])))
            elif array_ref == 'previous_response':
                if len(response_history) >= 2:
                    return str(array_length(response_history[-2].get('data', [])))
            return '0'
        
        # Handle response references with array access
        if '[' in var_path and ']' in var_path:
            # Parse array access like response[0].id or previous_response[0].postId
            base_ref = var_path.split('[')[0]
            array_part = var_path.split('[')[1].split(']')[0]
            field_part = var_path.split('].')[1] if '].' in var_path else ''
            
            try:
                array_index = int(array_part)
            except ValueError:
                return var_path
            
            if base_ref == 'response' and response_history:
                array_data = response_history[-1].get('data', [])
            elif base_ref == 'previous_response' and len(response_history) >= 2:
                array_data = response_history[-2].get('data', [])
            elif base_ref == 'second_to_last_response' and len(response_history) >= 3:
                array_data = response_history[-3].get('data', [])
            else:
                return var_path
            
            if isinstance(array_data, list) and 0 <= array_index < len(array_data):
                element = array_data[array_index]
                if field_part:
                    field_value = get_nested_field(element, field_part)
                    return str(field_value) if field_value is not None else 'None'
                else:
                    return str(element.get('id', '')) if isinstance(element, dict) else str(element)
            else:
                return 'None'
        
        # Handle response references (without array access)
        if var_path.startswith('response.') or var_path == 'response':
            if not response_history:
                return var_path
            
            latest_response = response_history[-1].get('data', {})
            if var_path == 'response':
                return str(latest_response.get('id', ''))
            
            field_path = var_path[9:]  # Remove 'response.'
            field_value = get_nested_field(latest_response, field_path)
            return str(field_value) if field_value is not None else 'None'
        
        # Handle previous_response references (without array access)
        if var_path.startswith('previous_response'):
            if len(response_history) < 2:
                return var_path
            
            prev_response = response_history[-2].get('data', {})
            if var_path == 'previous_response':
                return str(prev_response.get('id', ''))
            elif var_path.startswith('previous_response.'):
                field_path = var_path[18:]  # Remove 'previous_response.'
                field_value = get_nested_field(prev_response, field_path)
                return str(field_value) if field_value is not None else 'None'
        
        # Handle second_to_last_response references
        if var_path.startswith('second_to_last_response'):
            if len(response_history) < 3:
                return var_path
            
            second_to_last = response_history[-3].get('data', {})
            if var_path == 'second_to_last_response':
                return str(second_to_last.get('id', ''))
            elif var_path.startswith('second_to_last_response.'):
                field_path = var_path[24:]  # Remove 'second_to_last_response.'
                field_value = get_nested_field(second_to_last, field_path)
                return str(field_value) if field_value is not None else 'None'
        
        return var_path
    
    # Convert data to JSON string for processing
    data_str = json.dumps(data)
    
    # Replace variables in the format ${variable_path}
    data_str = re.sub(r'\$\{([^}]+)\}', replace_variable, data_str)
    
    # Convert back to Python object
    try:
        return json.loads(data_str)
    except json.JSONDecodeError:
        return data

def execute_api_request(base_url, request_type, parameters):
    """Enhanced API request execution with comprehensive error handling."""
    import requests
    import json
    
    endpoint = parameters.get('endpoint', '')
    url = f"{base_url}{endpoint}"
    
    try:
        if request_type == 'get_api':
            response = requests.get(url, timeout=30)
        elif request_type == 'post_api':
            data = parameters.get('data', {})
            response = requests.post(url, json=data, timeout=30)
        elif request_type == 'put_api':
            data = parameters.get('data', {})
            response = requests.put(url, json=data, timeout=30)
        elif request_type == 'delete_api':
            response = requests.delete(url, timeout=30)
        else:
            return {
                'status_code': 400,
                'data': {'error': f'Unsupported request type: {request_type}'}
            }
        
        # Parse response
        try:
            response_data = response.json()
        except (json.JSONDecodeError, ValueError):
            response_data = {'raw_response': response.text}
        
        return {
            'status_code': response.status_code,
            'data': response_data,
            'headers': dict(response.headers)
        }
        
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return {
            'status_code': 500,
            'data': {'error': str(e)}
        }

def get_nested_field(data, field_path):
    """Enhanced nested field access with array index support."""
    if not field_path:
        return data
    
    parts = field_path.split('.')
    current = data
    
    for part in parts:
        if isinstance(current, dict):
            current = current.get(part)
        elif isinstance(current, list):
            try:
                # Handle array index access like [0]
                if part.startswith('[') and part.endswith(']'):
                    index = int(part[1:-1])
                    current = current[index] if 0 <= index < len(current) else None
                else:
                    current = None
            except (ValueError, IndexError):
                current = None
        else:
            current = None
        
        if current is None:
            break
    
    return current

@then('the response should contain')
def step_check_response_contains_json(context):
    """Check that the response contains the specified JSON structure."""
    import json
    expected_data = json.loads(context.text)
    response_data = context.last_response.get('data', {})
    
    def check_nested_contains(expected, actual):
        """Recursively check if expected fields are contained in actual response."""
        if isinstance(expected, dict) and isinstance(actual, dict):
            for key, value in expected.items():
                if key not in actual:
                    return False, f"Missing key: {key}"
                if not check_nested_contains(value, actual[key])[0]:
                    return check_nested_contains(value, actual[key])
        elif isinstance(expected, list) and isinstance(actual, list):
            if len(expected) > len(actual):
                return False, f"Expected array length {len(expected)}, got {len(actual)}"
            for i, expected_item in enumerate(expected):
                if not check_nested_contains(expected_item, actual[i])[0]:
                    return check_nested_contains(expected_item, actual[i])
        else:
            if expected != actual:
                return False, f"Expected {expected}, got {actual}"
        return True, "Match"
    
    success, message = check_nested_contains(expected_data, response_data)
    assert success, f"Response validation failed: {message}"
    print(f"✓ Response contains expected JSON structure")