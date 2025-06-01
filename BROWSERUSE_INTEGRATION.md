# BrowserUse Integration for UI Automation

This document explains the integration of BrowserUse library for UI automation within the existing AI-driven automation framework.

## Overview

The framework now supports both **API automation** and **UI automation** through a single, centralized step handler. The AI automatically determines whether a step should be executed via API calls or browser automation based on the natural language content.

## Features

✅ **Unified Step Handler**: Continue using the same `@step(u'{step_text}')` function for all steps
✅ **Intelligent Routing**: AI automatically decides between API and browser automation
✅ **Natural Language**: Write UI tests in plain English without specific step definitions
✅ **Mixed Workflows**: Combine API and UI steps seamlessly in the same scenario
✅ **Error Handling**: Comprehensive error handling for both automation types

## Installation

The BrowserUse library is automatically included in the requirements:

```bash
pip install -r requirements.txt
```

## How It Works

### 1. AI Routing Decision

The `ai_decide_tool()` function analyzes each step and assigns a score based on keywords:

**Browser/UI Keywords:**

- open, navigate, click, fill, type, select, enter
- login page, web page, website, browser, form, button
- input field, dropdown, checkbox, scroll, etc.

**API Keywords:**

- api, endpoint, post, get, put, delete, patch
- request, response, json, headers, status code
- curl, rest, graphql, webhook, payload

**Example Routing:**

```gherkin
Given I open the login page and enter credentials  # → Browser
When I POST /api/login with data {"user": "test"}   # → API
Then I should see the dashboard page               # → Browser (assertion)
```

### 2. Browser Automation

UI steps are executed using the BrowserUse library:

```python
# ui_handler.py
def run_browser_instruction(instruction: str) -> Dict[str, Any]:
    # Creates browser session
    # Executes natural language instruction
    # Returns success/failure status
```

**Example UI Steps:**

```gherkin
Given I open the login page and enter credentials
When I click the submit button
Then I navigate to the dashboard
And I fill out the form with user details
```

### 3. API Automation

API steps continue using the existing tools:

```gherkin
When I POST /users with data {"name": "John", "email": "john@example.com"}
Then I should receive a successful response
And I GET /users/123 to verify the user was created
```

## Configuration

### Browser Settings

Configure browser behavior in your environment:

```python
# Default settings in ui_handler.py
config = BrowserConfig(
    headless=True,          # Set to False for visible browser
    disable_security=True,  # For testing purposes
    window_width=1920,
    window_height=1080
)
```

### Environment Variables

Set headless mode via environment:

```bash
# Run in headless mode (default)
BROWSER_HEADLESS=true behave

# Run with visible browser
BROWSER_HEADLESS=false behave
```

## Writing Mixed Scenarios

### Example 1: API Setup + UI Interaction

```gherkin
Scenario: Create user via API then verify in UI
    Given I POST /users with data {"name": "Jane Doe", "email": "jane@example.com"}
    When I open the user management page
    And I search for user "jane@example.com"
    Then I should see the user details displayed
```

### Example 2: UI Action + API Verification

```gherkin
Scenario: Submit form via UI then verify via API
    Given I open the contact form page
    When I fill out the form with name "John Smith" and message "Hello"
    And I submit the contact form
    Then I should see a success message
    And I GET /contacts to verify the submission was recorded
```

### Example 3: Complete E2E Workflow

```gherkin
Scenario: End-to-end user registration workflow
    # UI: User fills registration form
    Given I open the registration page
    When I fill in email "user@example.com" and password "secure123"
    And I click the register button
    Then I should see a confirmation message

    # API: Verify user was created
    And I GET /users?email=user@example.com
    Then I should receive a successful response
    And the response should contain the user data

    # UI: User can now login
    When I navigate to the login page
    And I enter the registered credentials
    Then I should successfully access the dashboard
```

## Error Handling

### Browser Errors

```python
{
    "status": "error",
    "instruction": "click the missing button",
    "error": "Element not found: missing button"
}
```

### API Errors

```python
{
    "status": "error",
    "step_text": "POST /invalid-endpoint",
    "error": "404 Not Found"
}
```

### Missing Dependencies

```python
{
    "status": "error",
    "instruction": "open login page",
    "error": "BrowserUse library not available. Please install with: pip install browseruse"
}
```

## Advanced Usage

### Custom Browser Functions

The `ui_handler.py` provides utility functions:

```python
# Navigate to specific URL
run_browser_navigation("https://example.com")

# Fill form with data
run_browser_form_fill({
    "email": "user@example.com",
    "password": "secure123"
})

# Click specific element
run_browser_click("the submit button")
```

### Session Management

Browser sessions are automatically managed:

```python
# Sessions persist across steps in the same scenario
# Automatically closed after scenario completion
close_browser_session()  # Manual cleanup if needed
```

## Troubleshooting

### Common Issues

1. **BrowserUse not installed**

   ```bash
   pip install browseruse
   ```

2. **Chrome/Browser not found**

   ```bash
   # Install Chrome or set browser path
   export CHROME_EXECUTABLE_PATH=/path/to/chrome
   ```

3. **Async event loop issues**
   ```bash
   pip install nest_asyncio  # Already in requirements.txt
   ```

### Debug Mode

Enable verbose logging:

```python
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

## Examples

See the demo feature file:

- `features/ui_automation_demo.feature`

Run the examples:

```bash
# Run specific feature
behave features/ui_automation_demo.feature

# Run with visible browser
BROWSER_HEADLESS=false behave features/ui_automation_demo.feature

# Run specific scenario
behave features/ui_automation_demo.feature -n "User login via UI"
```

## Migration Guide

### Existing Projects

No changes required! Your existing API-focused feature files will continue to work exactly as before. The AI routing automatically handles the decision.

### Adding UI Tests

Simply write natural language steps mentioning UI interactions:

```gherkin
# Before (API only)
When I POST /login with data {"email": "user@test.com", "password": "pass"}

# After (UI + API)
Given I open the login page and enter credentials
When I POST /login with data {"email": "user@test.com", "password": "pass"}
Then I should see the dashboard page
```

## Performance Considerations

- **Browser startup**: ~2-3 seconds per session
- **API calls**: ~100-500ms per request
- **Mixed scenarios**: Combine for optimal test coverage
- **Headless mode**: Faster execution, no visual feedback
- **Headed mode**: Slower but better for debugging

## Best Practices

1. **Use API for data setup/teardown**
2. **Use UI for user experience validation**
3. **Combine both for comprehensive E2E tests**
4. **Keep browser sessions minimal**
5. **Use descriptive step language for better AI routing**

## Support

For issues or questions:

1. Check the logs for routing decisions
2. Verify BrowserUse installation
3. Test individual components (API vs UI)
4. Use debug mode for detailed information
