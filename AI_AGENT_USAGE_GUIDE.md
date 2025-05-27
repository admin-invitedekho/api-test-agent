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
