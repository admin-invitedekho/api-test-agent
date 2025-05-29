# AI Agent Usage Guide for API Testing

This document provides comprehensive instructions for the AI agent to properly execute BDD scenarios by interacting with APIs using the provided tools.

## Available API Tools

The agent has access to four primary API interaction tools:

### 1. `get_api(endpoint, params=None)`

**Purpose**: Execute GET requests to retrieve data from API endpoints.

**Parameters**:

- `endpoint` (required): The API endpoint path (e.g., "/users/1", "/posts")
- `params` (optional): Dictionary of query parameters

**Usage Examples**:

```python
# Simple GET request
get_api(endpoint="/users/1")

# GET request with query parameters
get_api(endpoint="/users", params={"page": 1, "limit": 10})
```

### 2. `post_api(endpoint, data)`

**Purpose**: Execute POST requests to create new resources.

**Parameters**:

- `endpoint` (required): The API endpoint path (e.g., "/users", "/posts")
- `data` (required): Dictionary containing the JSON payload to send

**Critical Note**: The `data` parameter is REQUIRED for all POST requests.

**Usage Examples**:

```python
# Create a new user
post_api(endpoint="/users", data={"name": "John Doe", "email": "john@email.com"})

# Create a new post
post_api(endpoint="/posts", data={"title": "Test Post", "body": "Content", "userId": 1})
```

### 3. `put_api(endpoint, data)`

**Purpose**: Execute PUT requests to update existing resources.

**Parameters**:

- `endpoint` (required): The API endpoint path (e.g., "/users/1", "/posts/5")
- `data` (required): Dictionary containing the JSON payload for the update

**Critical Note**: The `data` parameter is REQUIRED for all PUT requests.

**Usage Examples**:

```python
# Update user information
put_api(endpoint="/users/1", data={"name": "Updated Name", "email": "updated@email.com"})

# Update a post
put_api(endpoint="/posts/1", data={"title": "Updated Title", "body": "Updated content"})
```

### 4. `delete_api(endpoint)`

**Purpose**: Execute DELETE requests to remove resources.

**Parameters**:

- `endpoint` (required): The API endpoint path (e.g., "/users/1", "/posts/5")

**Usage Examples**:

```python
# Delete a user
delete_api(endpoint="/users/1")

# Delete a post
delete_api(endpoint="/posts/5")
```

## ⚠️ CRITICAL: API Availability Checks - DO NOT PERFORM

**IMPORTANT RULE**: Never perform API availability checks or health checks.

### What NOT to do:

- **NEVER** make GET requests to base URLs to "check if API is available"
- **NEVER** perform health checks or ping operations
- **NEVER** make unnecessary requests to verify API connectivity

### Steps to SKIP/IGNORE (treat as informational only):

These types of step descriptions should be acknowledged but NO API calls should be made:

- `"Given the API is available at [URL]"`
- `"Given the [service] API is accessible"`
- `"Given the API endpoint is reachable"`
- `"Given the system is available"`
- `"Given the service is running"`

### Correct Response for Availability Steps:

When encountering API availability steps, respond with:

```
"Acknowledged that the API is available at [URL]. No availability check needed - proceeding with actual test operations."
```

### Why This Rule Exists:

1. **Security**: Many APIs return 403/401 for base URL requests
2. **Efficiency**: Availability checks are unnecessary overhead
3. **Reliability**: Focus on actual functional testing, not connectivity
4. **Best Practice**: Assume API availability and test actual functionality

### Example Handling:

**Input Step**: `"Given the InviteDeKho API is available at https://api.stage.invitedekho.com"`

**Correct Response**:

```
"Acknowledged that the InviteDeKho API is available at https://api.stage.invitedekho.com. Proceeding with API testing operations."
```

**WRONG Response**: Making a GET request to `https://api.stage.invitedekho.com`

## ⚠️ CRITICAL: URL Construction Rules

**IMPORTANT RULE**: Always use complete URLs based on loaded API contracts.

### URL Construction Guidelines:

1. **NEVER use relative paths** like `/login`, `/users`, etc.
2. **ALWAYS use complete URLs** from the API contracts
3. **Extract base URL from API availability steps** when present
4. **Combine base URL with endpoint paths** to create complete URLs

### API Contract Reference:

Based on the loaded InviteDeKho API contracts:

- **Base URL**: `https://api.stage.invitedekho.com`
- **Login Endpoint**: `https://api.stage.invitedekho.com/login`

### URL Construction Examples:

**CORRECT URL Usage:**

```python
# For InviteDeKho login
post_api(endpoint="https://api.stage.invitedekho.com/login", data={"email": "...", "password": "..."})

# For JSONPlaceholder (if used)
get_api(endpoint="https://jsonplaceholder.typicode.com/users/1")
```

**WRONG URL Usage:**

```python
# These will cause "AI should provide complete URL" errors
post_api(endpoint="/login", data={"email": "...", "password": "..."})
get_api(endpoint="/users/1")
```

### Step Context Awareness:

When processing login steps:

1. **Identify the API context** from previous availability steps
2. **Use the appropriate base URL** for that API
3. **Construct complete endpoint URLs** by combining base URL + path

**Example Context Processing:**

- Previous step: `"Given the InviteDeKho API is available at https://api.stage.invitedekho.com"`
- Current step: `"When I login with email... and password..."`
- **Correct endpoint**: `https://api.stage.invitedekho.com/login`
- **NOT**: `/login`

## Critical Parsing Instructions for POST and PUT Requests

When processing BDD step descriptions that contain JSON data, follow these exact steps:

### Step-by-Step JSON Extraction Process

#### Example 1: POST Request

**Input**: `"POST /users with JSON data: {\"name\": \"John\", \"email\": \"john@email.com\"}"`

**Processing Steps**:

1. **Extract endpoint**: "/users"
2. **Identify JSON data**: Everything after "JSON data:" → `{\"name\": \"John\", \"email\": \"john@email.com\"}`
3. **Parse JSON string to dictionary**: `{"name": "John", "email": "john@email.com"}`
4. **Execute tool call**: `post_api(endpoint="/users", data={"name": "John", "email": "john@email.com"})`

#### Example 2: PUT Request

**Input**: `"PUT /users/1 with JSON data: {\"name\": \"Updated Name\", \"status\": \"active\"}"`

**Processing Steps**:

1. **Extract endpoint**: "/users/1"
2. **Identify JSON data**: Everything after "JSON data:" → `{\"name\": \"Updated Name\", \"status\": \"active\"}`
3. **Parse JSON string to dictionary**: `{"name": "Updated Name", "status": "active"}`
4. **Execute tool call**: `put_api(endpoint="/users/1", data={"name": "Updated Name", "status": "active"})`

#### Example 3: Simple GET Request

**Input**: `"GET /users/1"`

**Processing Steps**:

1. **Extract endpoint**: "/users/1"
2. **Execute tool call**: `get_api(endpoint="/users/1")`

#### Example 4: GET with Parameters

**Input**: `"GET /users with parameters page=1&limit=5"`

**Processing Steps**:

1. **Extract endpoint**: "/users"
2. **Parse parameters**: `{"page": 1, "limit": 5}`
3. **Execute tool call**: `get_api(endpoint="/users", params={"page": 1, "limit": 5})`

## Common Parsing Patterns

### JSON Data Extraction Keywords

Look for these patterns in step descriptions:

- "with JSON data:"
- "with data:"
- "with payload:"
- "with body:"

### Parameter Extraction Keywords

Look for these patterns for GET request parameters:

- "with parameters"
- "with query parameters"
- "with params"

## Error Handling Guidelines

### Tool Response Structure

Each tool returns a dictionary with the following structure:

```python
{
    "curl_command": "curl -X GET ...",  # Equivalent curl command
    "tool_name": "get_api",             # Name of the tool used
    "endpoint": "/users/1",             # Endpoint that was called
    "status_code": 200,                 # HTTP status code
    "body": "response text",            # Raw response body
    "json_response": {...},             # Parsed JSON response (if available)
    "error": None                       # Error message (if any)
}
```

### Success vs. Failure Detection

- **Success**: `error` field is None or empty, and `status_code` is in 2xx range
- **Failure**: `error` field contains error message, or `status_code` is 4xx/5xx

### Error Response Handling

When an error occurs:

1. The tool will still return a response dictionary
2. The `error` field will contain the error message
3. Status code and response body (if available) will still be provided
4. The agent should report the error details to help with debugging

## Agent Response Guidelines

### When Successful

- Confirm the action was completed
- Report key details from the response (status code, important data)
- Mention the equivalent curl command if relevant

### When Failed

- Clearly state what went wrong
- Include the error message and status code
- Suggest potential solutions if applicable

### Example Responses

**Successful GET**:

```
Successfully retrieved user data from /users/1. Response status: 200.
The user data includes: name="John Doe", email="john@example.com", id=1.
```

**Successful POST**:

```
Successfully created a new user at /users. Response status: 201.
The new user was assigned ID: 11 and contains the data: name="John Doe", email="john@example.com".
```

**Failed Request**:

```
Failed to retrieve data from /users/999. Response status: 404.
Error: Not Found. The requested user does not exist.
```

## Base URL Configuration

The current base URL is set to: `https://jsonplaceholder.typicode.com`

This is a free testing API that provides realistic responses for:

- `/users` - User management
- `/posts` - Blog posts
- `/comments` - Post comments
- `/albums` - Photo albums
- `/photos` - Individual photos
- `/todos` - Todo items

## Important Reminders

1. **Always include the `data` parameter for POST and PUT requests** - Never call these tools with only the endpoint parameter
2. **Parse JSON strings carefully** - Convert escaped JSON strings into proper Python dictionaries
3. **Handle both success and error responses** - Tools return structured data in both cases
4. **Use descriptive language** - Help users understand what happened and why
5. **Include relevant details** - Status codes, error messages, and key response data are important for debugging

## Troubleshooting Common Issues

### Issue: "ValidationError for post_api missing data field"

**Cause**: Calling `post_api` or `put_api` without the required `data` parameter
**Solution**: Always extract and include the JSON data when making POST/PUT requests

### Issue: "Agent indicated failure in its final output"

**Cause**: The agent responded with phrases like "I cannot" or "failed to"
**Solution**: Review the step description and ensure it matches available tool capabilities

### Issue: JSON parsing errors

**Cause**: Malformed JSON in the step description
**Solution**: Validate JSON syntax and handle escaped quotes properly

### Issue: 404 Not Found errors

**Cause**: Requesting resources that don't exist on the test API
**Solution**: Use valid resource IDs (1-10 for users, 1-100 for posts on JSONPlaceholder)

## Critical HTTP Method Selection Rules

### ⚠️ MANDATORY: Use Methods Specified in API Contracts

**CRITICAL RULE**: Always use the HTTP method specified in the loaded API contracts for each operation.

### Method Selection from API Contracts

**ALWAYS refer to the loaded API contracts** to determine the correct HTTP method:

1. **Check the API contract documentation** for the specific endpoint
2. **Use the exact method specified** in the contract (GET, POST, PUT, DELETE)
3. **Do not assume methods** based on operation names

### API Contract Reference Process:

**Step 1**: Identify the operation from the step description
**Step 2**: Look up the endpoint in the loaded API contracts  
**Step 3**: Use the HTTP method specified in the contract
**Step 4**: Include required parameters as specified in the contract

### InviteDeKho API Contract Examples:

Based on the loaded API contracts:

- **Login Endpoint**: Use the method specified in the InviteDeKho API contract for `/login`
- **Other endpoints**: Always refer to contract specifications

**CORRECT Method Selection Process:**

```python
# 1. Check API contract for /login endpoint
# 2. Use the method specified in the contract
# 3. Include required data fields from contract

# Example based on contract specifications:
post_api(
    endpoint="https://api.stage.invitedekho.com/login",
    data={
        "email": "user@example.com",
        "password": "password123"
    }
)
```

### HTTP Method Guidelines by Operation:

1. **POST Method** (`post_api`) - Use when contract specifies POST for:

   - Authentication operations (if specified as POST in contract)
   - Creating resources
   - Submitting data with request body

2. **GET Method** (`get_api`) - Use when contract specifies GET for:

   - Retrieving data
   - Reading information
   - No request body needed

3. **PUT Method** (`put_api`) - Use when contract specifies PUT for:

   - Updating entire resources
   - Complete resource replacement

4. **DELETE Method** (`delete_api`) - Use when contract specifies DELETE for:
   - Removing resources

### Contract-Based Step Analysis:

**For login/authentication steps:**

- **Step pattern**: `"When I login with email... and password..."`
- **Action**: Look up `/login` endpoint in loaded API contracts
- **Method**: Use the HTTP method specified in the contract documentation
- **Data**: Include required fields as specified in the contract

**For other operations:**

- **Always reference the API contract** for the specific endpoint
- **Use the method specified** in the contract documentation
- **Include required fields** as documented in the contract

## ⚠️ CRITICAL: Data Parameter Requirements

**MANDATORY RULE**: Always include the `data` parameter for POST and PUT requests.

### POST and PUT Tool Usage:

- **post_api(endpoint, data)** - `data` parameter is REQUIRED
- **put_api(endpoint, data)** - `data` parameter is REQUIRED
- **NEVER call these tools with only endpoint parameter**

### Data Extraction from Steps:

When processing login steps, extract email and password values:

**Step Example**: `"When I try to login with invalid email "wrong@email.com" and password "Test@123456""`

**Correct Tool Call**:

```python
post_api(
    endpoint="https://api.stage.invitedekho.com/login",
    data={
        "email": "wrong@email.com",
        "password": "Test@123456"
    }
)
```

**WRONG Tool Call**:

```python
# This will cause ValidationError - missing data parameter
post_api(endpoint="https://api.stage.invitedekho.com/login")
```

## ⚠️ CRITICAL: Step Type Understanding

**IMPORTANT**: Different step types require different actions.

### Step Classification:

1. **"Given" steps** - Setup/Context (acknowledge only, no API calls usually)
2. **"When" steps** - Actions (make API calls)
3. **"Then" steps** - Assertions (check previous responses, do NOT make new API calls)

### "Then" Step Handling:

For assertion steps like `"Then I should receive an authentication error response"`:

**CORRECT Action**:

- Check the PREVIOUS API call result
- Examine status code and response data
- Report if the assertion passes or fails

**WRONG Action**:

- Making a new API call
- Calling post_api, get_api, etc.

**Example "Then" Step Response**:

```
"Based on the previous login attempt, the response was:
- Status Code: 400
- Error Message: 'Request method GET is not supported'
- This indicates an authentication error response as expected."
```
