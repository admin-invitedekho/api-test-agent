# Playwright MCP Integration Guide

## Overview

This project integrates with **Playwright MCP (Model Context Protocol)** server for browser automation alongside existing API testing capabilities. The system uses **AI-powered routing** to automatically determine whether a test step should be executed via API calls or browser automation through the Playwright MCP server.

## Key Features

### ✅ **Unified Step Handling**

- All feature file steps use the same natural language format
- AI automatically routes steps to either API or browser handlers
- No need for separate step functions or decorators

### ✅ **Playwright MCP Client Integration**

- Connects to Playwright MCP server as a client
- Leverages all 25+ MCP tools for browser automation
- Natural language commands are parsed and sent to MCP server
- MCP server handles interpretation and browser execution

### ✅ **AI-Powered Classification**

- Uses LangChain LLM to classify step intent
- Fallback to keyword-based classification
- Supports both Gemini and OpenAI models

### ✅ **Mixed Test Scenarios**

- Combine API and browser operations in the same scenario
- Seamless switching between interaction types
- Maintain context across different operation types

## Architecture

```
Test Step (Natural Language)
         ↓
   AI Classification
    ↓         ↓
  'api'    'browser'
    ↓         ↓
API Handler  MCP Client
    ↓         ↓
 API Tools   Playwright MCP Server (Node.js)
    ↓         ↓
  Result    Browser Automation
```

## Installation & Setup

### 1. Dependencies

```bash
# Install Node.js Playwright MCP server
npm install -g @playwright/mcp@latest

# Install browser
npm install @playwright/test
npx playwright install chromium

# Install Python MCP client
pip install mcp fastmcp

# Install existing dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
# For Gemini (default)
export USE_GEMINI=true
export GOOGLE_API_KEY=your_gemini_api_key
export GEMINI_MODEL=gemini-2.5-pro-preview-05-06

# For OpenAI (alternative)
export USE_GEMINI=false
export OPENAI_API_KEY=your_openai_api_key
```

## Usage Examples

### Browser-Only Steps

```gherkin
# These will be classified as 'browser' actions and sent to MCP server
Given I navigate to "https://example.com"
When I click the login button
And I enter "user@example.com" in the email field
Then I should see the welcome message
```

### API-Only Steps

```gherkin
# These will be classified as 'api' actions
Given I make a GET request to "/users/1"
When I send a POST request to "/posts" with data {"title": "Test"}
Then the response status code should be 201
```

### Mixed Scenarios

```gherkin
Scenario: Complete user workflow
  # API step - sets up data
  Given I create a user via POST to "/users" with data {"name": "John"}

  # Browser steps - test UI via MCP
  When I open the application login page
  And I login with the created user credentials

  # Browser step - verify UI via MCP
  Then I should see "Welcome John" on the dashboard

  # API step - verify backend
  And the user session should be active via GET "/sessions"
```

## Key Components

### 1. Browser MCP Handler (`src/browser_handler.py`)

- **`BrowserMCPHandler`**: Main class managing MCP client connection
- **`start_mcp_server()`**: Establish connection to Playwright MCP server
- **`send_mcp_command()`**: Send natural language commands to MCP server
- **`cleanup_mcp_session()`**: Clean up MCP client connection
- **Natural Language Parsing**: Converts instructions to MCP tool calls

### 2. AI Step Handler (`src/ai_step_handler.py`)

- **`ai_decide_tool()`**: LLM-based step classification
- **`step_handler()`**: Main routing logic
- **`run_browser_instruction_handler()`**: Routes to MCP client
- **`run_api_instruction()`**: Routes to API tools
- **Integrated with existing API validation capabilities**

### 3. Environment Management (`features/environment.py`)

- **`before_scenario()`**: Start fresh MCP connection per scenario
- **`after_scenario()`**: Clean up MCP connection
- **`after_all()`**: Final cleanup

## MCP Server Capabilities

The Playwright MCP server provides 25+ tools including:

### Navigation

- `browser_navigate` - Navigate to URLs
- `browser_navigate_back` - Go back in history
- `browser_navigate_forward` - Go forward in history

### Interactions

- `browser_click` - Click elements
- `browser_type` - Type text into elements
- `browser_select_option` - Select from dropdowns
- `browser_drag` - Drag and drop
- `browser_hover` - Hover over elements

### Information Gathering

- `browser_snapshot` - Get accessibility snapshot (recommended)
- `browser_take_screenshot` - Capture visual screenshots
- `browser_console_messages` - Get console logs
- `browser_network_requests` - Get network activity

### Utilities

- `browser_wait_for` - Wait for conditions
- `browser_press_key` - Press keyboard keys
- `browser_file_upload` - Upload files
- `browser_handle_dialog` - Handle dialogs

### Tab Management

- `browser_tab_list` - List open tabs
- `browser_tab_new` - Open new tabs
- `browser_tab_select` - Switch tabs
- `browser_tab_close` - Close tabs

## Natural Language to MCP Mapping

Our system automatically maps natural language instructions to MCP tools:

```python
# Navigation
"navigate to https://example.com" → browser_navigate(url="https://example.com")
"go back" → browser_navigate_back()

# Interactions
"click the Submit button" → browser_click(element="Submit button", ref="auto")
"type hello in search field" → browser_type(element="search field", text="hello")

# Information
"take a screenshot" → browser_take_screenshot()
"what do I see" → browser_snapshot()

# Utilities
"wait for 3 seconds" → browser_wait_for(time=3)
```

## Running Tests

### Basic Test Run

```bash
# Activate environment
source venv/bin/activate

# Run with Gemini
export USE_GEMINI=true
export GOOGLE_API_KEY=your_api_key

# Run browser automation demo
behave features/browser_automation_demo.feature
```

### Test MCP Integration

```bash
# Test MCP connection and tools
python test_mcp_integration.py

# Test full browser automation flow
python test_full_browser_flow.py
```

## Troubleshooting

### Common Issues

1. **MCP Server Connection Failed**

   ```bash
   npm install -g @playwright/mcp@latest
   npx playwright install chromium
   ```

2. **Browser Not Installed**

   ```bash
   npm install @playwright/test
   npx playwright install chromium
   ```

3. **Python MCP Client Issues**
   ```bash
   pip install mcp fastmcp
   ```

### Debug Mode

```python
# Enable detailed logging
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

### Verify MCP Tools

```bash
# Test available MCP tools
python test_mcp_integration.py
```

## Best Practices

### Writing Natural Language Steps

1. **Be Explicit**: Use clear, descriptive language
2. **Include Context**: Specify elements clearly ("email field", "submit button")
3. **Use Quotes**: Put values in quotes ("username@example.com")

### MCP Integration

1. **Connection Management**: Each scenario gets a fresh MCP connection
2. **Error Handling**: Graceful fallback when MCP tools fail
3. **Tool Selection**: System automatically selects best MCP tool for instruction

### Performance

1. **Connection Reuse**: MCP connection persists throughout scenario
2. **Resource Management**: Automatic cleanup prevents memory leaks
3. **Efficient Parsing**: Smart natural language to MCP tool mapping

## Advanced Configuration

### Custom MCP Server Options

You can customize the MCP server startup in `browser_handler.py`:

```python
server_params = StdioServerParameters(
    command="npx",
    args=[
        "@playwright/mcp@latest",
        "--browser=chromium",
        "--headless",  # Run headless
        "--viewport-size=1920,1080"  # Custom viewport
    ]
)
```

### Adding New Natural Language Patterns

Extend `_parse_instruction_to_mcp_tool()` in `browser_handler.py`:

```python
elif "scroll" in instruction_lower:
    return "browser_press_key", {"key": "PageDown"}
```

## Future Enhancements

- [ ] Visual element selection via screenshots
- [ ] Advanced MCP tool chaining
- [ ] Custom MCP server configurations
- [ ] Parallel browser sessions
- [ ] Mobile device emulation

## Comparison: Direct Playwright vs MCP

| Aspect               | Direct Playwright         | Playwright MCP           |
| -------------------- | ------------------------- | ------------------------ |
| **Setup**            | Complex async management  | Simple client connection |
| **Capabilities**     | Limited to coded actions  | 25+ pre-built tools      |
| **Natural Language** | Manual parsing required   | Built-in interpretation  |
| **Maintenance**      | Custom browser management | MCP server handles all   |
| **Extensibility**    | Code new features         | Use existing MCP tools   |
| **Debugging**        | Custom logging            | MCP protocol debugging   |

The MCP integration provides a much more robust and maintainable solution for browser automation with natural language interfaces.
