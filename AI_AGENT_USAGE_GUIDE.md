# AI Agent Usage Guide for API & Browser Testing

## Overview

This AI-powered testing framework supports both **API testing** and **browser automation** using natural language scenarios. The agent intelligently determines whether to use API tools or browser automation based on the test scenario context.

## Available Testing Capabilities

### 🌐 Browser Automation (Playwright MCP)

- **Navigation**: Navigate to web pages
- **Interactions**: Click buttons, fill forms, select options
- **Verification**: Check page content and UI states
- **Screenshots**: Automatic screenshot capture (organized by feature/scenario)
- **Waits**: Implicit 3-second waits after browser operations

### 🔌 API Testing Tools

- **GET**: Retrieve data from endpoints
- **POST**: Create resources with data
- **PUT**: Update existing resources
- **DELETE**: Remove resources

## 🎯 Test Type Detection

The AI agent automatically determines the test type based on scenario content:

### Browser Testing Indicators

- URLs to web pages (e.g., `https://stage.invitedekho.com`)
- UI interaction language ("click button", "enter text", "navigate to")
- Form filling and user workflows
- Visual verification steps

### API Testing Indicators

- API endpoint URLs (e.g., `https://api.stage.invitedekho.com`)
- HTTP method language ("POST request", "GET data")
- JSON data structures
- Response validation steps

## 🌐 Browser Testing Guide

### Navigation Steps

```gherkin
When I navigate to "https://stage.invitedekho.com"
When I click the "Login" button
When I enter "user@example.com" in the email field
```

### Form Interactions

```gherkin
When I enter pincode "400001"
When I click the bride option
When I fill wedding function details with date "15/06/2025" and time "18:00"
```

### Complex Workflows

```gherkin
When I enter song name "Perfect by Ed Sheeran" in search field
And I click the "Search" button
And I click the first YouTube video result
And I click the "Select Audio" button
```

### ✅ Browser Testing Best Practices

1. **Use Natural Language**: Describe actions as a user would perform them
2. **Be Specific**: Include exact text, button names, and field identifiers
3. **Sequential Steps**: Break complex workflows into clear, sequential steps
4. **Avoid Explicit Screenshots**: Screenshots are captured automatically
5. **No Manual Waits**: 3-second waits are added automatically after operations

## 🔌 API Testing Guide

### Available API Tools

#### 1. `get_api(endpoint, params=None)`

Execute GET requests to retrieve data.
**Example**: `get_api(endpoint="/users/1", params={"page": 1})`

#### 2. `post_api(endpoint, data)`

Execute POST requests to create resources. **`data` parameter is REQUIRED**.
**Example**: `post_api(endpoint="/users", data={"name": "John", "email": "john@email.com"})`

#### 3. `put_api(endpoint, data)`

Execute PUT requests to update resources. **`data` parameter is REQUIRED**.
**Example**: `put_api(endpoint="/users/1", data={"name": "Updated Name"})`

#### 4. `delete_api(endpoint)`

Execute DELETE requests to remove resources.
**Example**: `delete_api(endpoint="/users/1")`

### ⚠️ API Testing Critical Rules

#### 1. NO API Availability Checks

**NEVER** perform health checks. For steps like:

- `"Given the API is available at [URL]"`
- `"Given the service is running"`

Respond with: _"Acknowledged that the API is available at [URL]. Proceeding with test operations."_

#### 2. Always Use Complete URLs

**CORRECT**: `https://api.stage.invitedekho.com/login`
**WRONG**: `/login`

#### 3. POST/PUT Data Requirements

Always include `data` parameter:
**CORRECT**: `post_api(endpoint="...", data={"email": "...", "password": "..."})`
**WRONG**: `post_api(endpoint="...")` ❌ Will cause ValidationError

## 📋 Step Type Guidelines

### "Given" Steps - Setup/Context

**Action**: Acknowledge only, usually no API/browser calls
**Example**: `"Given the API is available"` → Acknowledge setup

### "When" Steps - Actions

**Action**: Make API calls or perform browser actions
**Examples**:

- `"When I login with email..."` → Use `post_api`
- `"When I click the Login button"` → Use browser automation

### "Then"/"And" Steps - Assertions

**Action**: Examine PREVIOUS responses/states, DO NOT make new calls
**Example**: `"Then I should receive error response"` → Check previous result

## 🏗️ Project Structure

```
api-test-agent/
├── features/                           # Test scenarios
│   ├── edit_yourself_249_comprehensive.feature  # Browser workflow tests
│   ├── user_profile_verification.feature        # Browser UI tests
│   ├── invitedekho_login_tests.feature         # API tests
│   ├── profile_api_tests.feature              # API tests
│   ├── user_profile_comprehensive_tests.feature # Mixed tests
│   ├── environment.py                         # Test environment setup
│   └── steps/
│       └── enhanced_steps.py                  # AI-powered step handler
├── src/
│   ├── agent.py                    # Main AI agent logic
│   ├── api_tools.py               # API interaction tools
│   ├── browser_handler.py         # Playwright MCP integration
│   ├── ai_step_handler.py         # AI step processing
│   └── ai_schema_validator.py     # Response validation
├── screenshots/                   # Organized screenshot storage
│   ├── feature_name/
│   │   └── scenario_name/        # Auto-organized by test
├── requirements.txt              # Dependencies
└── README.md                    # Documentation
```

## 🚀 Running Tests

### Browser Tests

```bash
# Run comprehensive Edit @ ₹249 workflow tests
python -m behave features/edit_yourself_249_comprehensive.feature

# Run specific browser test scenarios
python -m behave features/edit_yourself_249_comprehensive.feature --tags=@complete_workflow
python -m behave features/edit_yourself_249_comprehensive.feature --tags=@music_integration_detailed
```

### API Tests

```bash
# Run API login tests
python -m behave features/invitedekho_login_tests.feature

# Run profile API tests
python -m behave features/profile_api_tests.feature
```

### All Tests

```bash
# Run all tests
python -m behave features/
```

## 🔧 Configuration

### Browser Settings

- **Headless Mode**: Enabled (no visible browser windows)
- **Screenshots**: Auto-captured and organized by feature/scenario
- **Waits**: 3-second implicit waits after browser operations
- **Viewport**: 1400x900 for consistent rendering

### API Settings

- **Base URLs**: Configured for InviteDeKho staging environment
- **Timeouts**: Reasonable defaults for API responses
- **Validation**: Automatic response schema validation

## 📊 Features

### ✅ Consolidated Test Scenarios

- **@complete_workflow**: End-to-end workflow with validation testing
- **@music_integration_detailed**: Complete YouTube music integration
- **@edge_cases_validation**: Navigation, validation, and edge cases

### ✅ Intelligent Step Processing

- Automatic detection of test type (API vs Browser)
- Natural language interpretation
- Smart error handling and recovery

### ✅ Organized Output

- Screenshots organized by feature/scenario
- Clean, focused logging
- Comprehensive test reporting

## 🎯 Best Practices

### Browser Testing

1. Use descriptive, natural language for UI interactions
2. Break complex workflows into sequential steps
3. Be specific about button text, field names, and UI elements
4. Let the system handle screenshots and waits automatically

### API Testing

1. Always use complete URLs
2. Include required data parameters for POST/PUT
3. Use appropriate step types (Given/When/Then)
4. Focus on one action per step

### Mixed Testing

1. Clearly separate browser and API test scenarios
2. Use appropriate language for each test type
3. Leverage the AI's automatic detection capabilities
4. Maintain consistent naming conventions

## 🚀 Success Factors

1. **Clear Intent**: Write scenarios that clearly express test intentions
2. **Appropriate Granularity**: One action per step, focused assertions
3. **Natural Language**: Use language that describes user actions naturally
4. **Consistent Structure**: Follow Given/When/Then patterns consistently
5. **Specific Details**: Include exact values, button text, and field names
