# AI Agent Usage Guide for API Testing

## Available API Tools

### 1. `get_api(endpoint, params=None)`

Execute GET requests to retrieve data.

**Example**: `get_api(endpoint="/users/1", params={"page": 1})`

### 2. `post_api(endpoint, data)`

Execute POST requests to create resources. **`data` parameter is REQUIRED**.

**Example**: `post_api(endpoint="/users", data={"name": "John", "email": "john@email.com"})`

### 3. `put_api(endpoint, data)`

Execute PUT requests to update resources. **`data` parameter is REQUIRED**.

**Example**: `put_api(endpoint="/users/1", data={"name": "Updated Name"})`

### 4. `delete_api(endpoint)`

Execute DELETE requests to remove resources.

**Example**: `delete_api(endpoint="/users/1")`

## ⚠️ CRITICAL RULES

### 1. NO API Availability Checks

**NEVER** perform health checks or availability verifications. For steps like:

- `"Given the API is available at [URL]"`
- `"Given the service is running"`

Respond with: _"Acknowledged that the API is available at [URL]. Proceeding with test operations."_

### 2. Always Use Complete URLs

**NEVER** use relative paths. Always construct complete URLs:

**CORRECT**: `https://api.stage.invitedekho.com/login`
**WRONG**: `/login`

**InviteDeKho URLs**:

- Base: `https://api.stage.invitedekho.com`
- Login: `https://api.stage.invitedekho.com/login`

### 3. POST/PUT Data Requirements

Always include `data` parameter for POST and PUT requests:

**CORRECT**: `post_api(endpoint="...", data={"email": "...", "password": "..."})`
**WRONG**: `post_api(endpoint="...")` ❌ Will cause ValidationError

### 4. Step Type Understanding

#### "Given" Steps - Setup/Context

**Action**: Acknowledge only, usually no API calls
**Example**: `"Given the API is available"` → Acknowledge setup

#### "When" Steps - Actions

**Action**: Make API calls using tools
**Example**: `"When I login with email..."` → Use `post_api`

#### "Then"/"And" Steps - Assertions

**Action**: Examine PREVIOUS responses, DO NOT make new API calls
**Example**: `"Then I should receive error response"` → Check previous API response

## Quick Reference

### Login Step Processing

```python
# Step: "When I login with email 'user@example.com' and password 'pass123'"
post_api(
    endpoint="https://api.stage.invitedekho.com/login",
    data={"email": "user@example.com", "password": "pass123"}
)
```

### Assertion Step Processing

```python
# Step: "Then I should receive authentication error"
# Action: Check previous API response - NO new API call
# Response: "Previous login returned status 400 with error message..."
```

### JSON Data Extraction

Extract data from steps containing:

- "with JSON data: {...}"
- "with data: {...}"
- "with payload: {...}"

Parse JSON strings to dictionaries before passing to tools.

## Response Guidelines

### Success Response

```
"Successfully [action] at [endpoint]. Status: [code].
Key details: [relevant response data]"
```

### Error Response

```
"Failed to [action] at [endpoint]. Status: [code].
Error: [error message]"
```

### Assertion Response

```
"Previous [action] result: Status [code] with [details].
This [confirms/indicates] [assertion result]."
```

## Common Patterns

### Login Variations

- `"When I login..."` → POST to login endpoint with credentials
- `"When I try to login with invalid..."` → POST with provided invalid data
- `"When I attempt to login..."` → POST with specified parameters

### Error Testing

- `"Then I should receive error response"` → Check previous response status/message
- `"And error should indicate [type]"` → Verify previous error message content

### Security Testing

- SQL injection attempts → POST with malicious data, expect proper error handling
- Oversized input → POST with large payload, expect validation errors

## Troubleshooting

| Error                        | Cause                 | Solution                            |
| ---------------------------- | --------------------- | ----------------------------------- |
| ValidationError missing data | POST/PUT without data | Always include data parameter       |
| Agent failure output         | Wrong action type     | Check step type (Given/When/Then)   |
| 404 Not Found                | Invalid endpoint      | Use complete URLs from contracts    |
| JSON parsing error           | Malformed JSON        | Validate and escape quotes properly |
