# AI API & Browser Test Agent

An intelligent testing framework that uses AI to interpret natural language test scenarios and execute them automatically using both **API testing** and **browser automation** via Playwright MCP integration.

## 🚀 Overview

This project implements an AI-powered agent that:

- **Interprets BDD scenarios** written in natural language
- **Automatically determines** whether to use API calls or browser automation
- **Executes tests intelligently** with minimal configuration using Playwright MCP server
- **Provides organized output** with automatic screenshot management
- **Validates responses** and UI states intelligently

## ✨ Key Features

### 🌐 **Dual Testing Capabilities**

- **API Testing**: REST API validation with intelligent response checking
- **Browser Automation**: Full web UI testing with Playwright MCP integration
- **Automatic Detection**: AI determines test type based on scenario content

### 🧠 **AI-Powered Intelligence**

- **Natural Language Processing**: Write tests in plain English
- **Smart Step Interpretation**: Understands user intent from test descriptions
- **Automatic Tool Selection**: Chooses appropriate testing method automatically
- **Intelligent Validation**: Context-aware response and UI validation

### 📸 **Organized Screenshot Management**

- **Auto-Capture**: Screenshots taken automatically during browser operations
- **Organized Storage**: `screenshots/feature_name/scenario_name/` structure
- **Implicit Waits**: 3-second waits after browser operations for stability
- **Headless Execution**: No visible browser windows during testing

### 🎯 **Streamlined Testing**

- **Consolidated Scenarios**: Maximum coverage with minimal repetition
- **Clean Output**: Focused logging without redundancy
- **Flexible Validation**: Context-aware response checking
- **Easy Execution**: Simple command-line test running

## 🏗️ Architecture & Project Structure

### **System Architecture**

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

### **Project Structure**

```
api-test-agent/
├── features/                           # Test scenarios
│   ├── edit_yourself_249_comprehensive.feature # Browser workflow tests
│   ├── invitedekho_login_tests.feature        # API authentication tests
│   ├── profile_api_tests.feature              # API profile tests
│   ├── user_profile_comprehensive_tests.feature # Mixed API/UI tests
│   ├── environment.py                         # Behave environment wrapper
│   └── steps/
│       └── enhanced_steps.py                  # AI-powered step handler
├── src/
│   ├── agent.py                    # Main AI agent logic
│   ├── api_tools.py               # API interaction tools
│   ├── browser_handler.py         # Playwright MCP integration
│   ├── ai_step_handler.py         # AI step processing
│   ├── ai_schema_validator.py     # Response validation
│   ├── environment.py             # Test environment setup (main logic)
│   └── config.py                  # Configuration settings
├── screenshots/                   # Auto-organized screenshot storage
│   ├── feature_name/
│   │   └── scenario_name/        # Screenshots organized by test
├── requirements.txt              # Python dependencies
├── behave.ini                   # Behave configuration
├── .gitignore                   # Git ignore rules
└── README.md                    # This comprehensive guide
```

## 🚀 Installation & Setup

### **1. Prerequisites**

#### **Node.js and npm** (Required for Playwright MCP server)

```bash
node --version  # Should be v16 or higher
npm --version
```

#### **Python Dependencies**

```bash
pip install -r requirements.txt
pip install mcp fastmcp aiohttp
```

### **2. Playwright MCP Server Setup**

#### **Install Playwright MCP Package**

```bash
# Install globally
npm install -g @playwright/mcp@latest

# Install Playwright browsers
npm install @playwright/test
npx playwright install chromium
```

#### **Verify Installation**

```bash
# Test MCP server
npx @playwright/mcp@latest --help

# Test browser installation
npx playwright install --dry-run
```

### **3. Environment Configuration**

#### **API Keys Setup**

```bash
# For Gemini (default)
export USE_GEMINI=true
export GOOGLE_API_KEY=your_gemini_api_key
export GEMINI_MODEL=gemini-2.5-pro-preview-05-06

# For OpenAI (alternative)
export USE_GEMINI=false
export OPENAI_API_KEY=your_openai_api_key
```

#### **MCP Server Configuration**

The system uses HTTP/SSE transport for MCP communication:

```json
{
  "mcpServers": {
    "playwright": {
      "url": "http://[::1]:3000/sse"
    }
  }
}
```

**Server Settings:**

- **Transport**: HTTP/SSE
- **Host**: `::1` (IPv6 localhost)
- **Port**: `3000`
- **Browser**: Chrome (headless mode)
- **Viewport**: 1400x900
- **User Data**: `/tmp/playwright-headless-session`

### **4. Installation Verification**

```bash
# Clone the repository
git clone <repository-url>
cd api-test-agent

# Install dependencies
pip install -r requirements.txt

# Test the setup
python -c "from src.browser_handler import BrowserMCPHandler; print('✅ Setup successful')"
```

## 🧠 Playwright MCP Integration Details

### **Key Components**

#### **1. Browser MCP Handler (`src/browser_handler.py`)**

- **`BrowserMCPHandler`**: Main class managing MCP client connection
- **`start_mcp_server()`**: Establish connection to Playwright MCP server
- **`send_mcp_command()`**: Send natural language commands to MCP server
- **`cleanup_mcp_session()`**: Clean up MCP client connection
- **Natural Language Parsing**: Converts instructions to MCP tool calls

#### **2. AI Step Handler (`src/ai_step_handler.py`)**

- **`ai_decide_tool()`**: LLM-based step classification
- **`step_handler()`**: Main routing logic
- **`run_browser_instruction_handler()`**: Routes to MCP client
- **`run_api_instruction()`**: Routes to API tools
- **Integrated with existing API validation capabilities**

#### **3. Environment Management (`features/environment.py`)**

- **`before_scenario()`**: Start fresh MCP connection per scenario
- **`after_scenario()`**: Clean up MCP connection
- **`after_all()`**: Final cleanup

### **MCP Server Capabilities (25+ Tools)**

#### **Navigation**

- `browser_navigate` - Navigate to URLs
- `browser_navigate_back` - Go back in history
- `browser_navigate_forward` - Go forward in history

#### **Interactions**

- `browser_click` - Click elements
- `browser_type` - Type text into elements
- `browser_select_option` - Select from dropdowns
- `browser_drag` - Drag and drop
- `browser_hover` - Hover over elements

#### **Information Gathering**

- `browser_snapshot` - Get accessibility snapshot (recommended)
- `browser_take_screenshot` - Capture visual screenshots
- `browser_console_messages` - Get console logs
- `browser_network_requests` - Get network activity

#### **Utilities**

- `browser_wait_for` - Wait for conditions
- `browser_press_key` - Press keyboard keys
- `browser_file_upload` - Upload files
- `browser_handle_dialog` - Handle dialogs

#### **Tab Management**

- `browser_tab_list` - List open tabs
- `browser_tab_new` - Open new tabs
- `browser_tab_select` - Switch tabs
- `browser_tab_close` - Close tabs

### **Natural Language to MCP Mapping**

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

## 🎯 Running Tests

### **Basic Test Execution**

#### **Browser Tests** (Edit @ ₹249 Workflow)

```bash
# Run all browser workflow tests
python -m behave features/edit_yourself_249_comprehensive.feature

# Run specific test scenarios
python -m behave features/edit_yourself_249_comprehensive.feature --tags=@complete_workflow
python -m behave features/edit_yourself_249_comprehensive.feature --tags=@music_integration_detailed
python -m behave features/edit_yourself_249_comprehensive.feature --tags=@edge_cases_validation
```

#### **API Tests** (Authentication & Profile)

```bash
# Run API authentication tests
python -m behave features/invitedekho_login_tests.feature

# Run profile API tests
python -m behave features/profile_api_tests.feature
```

#### **Mixed Tests** (API + Browser)

```bash
# Run comprehensive tests combining API and browser
python -m behave features/user_profile_comprehensive_tests.feature
```

#### **All Tests**

```bash
# Run everything
python -m behave features/

# Run with detailed output
python -m behave features/ --no-capture
```

### **Advanced Test Options**

#### **With Environment Variables**

```bash
# Use Gemini for AI classification
export USE_GEMINI=true
export GOOGLE_API_KEY=your_api_key
python -m behave features/

# Use OpenAI for AI classification
export USE_GEMINI=false
export OPENAI_API_KEY=your_api_key
python -m behave features/
```

#### **Debug Mode**

```bash
# Enable detailed logging
export PYTHONPATH=$PWD
python -c "
import logging
logging.getLogger().setLevel(logging.DEBUG)
import subprocess
subprocess.run(['python', '-m', 'behave', 'features/', '--no-capture'])
"
```

## 📊 Test Scenarios

### **🌐 Browser Automation Tests**

#### **@complete_workflow** - End-to-End Workflow Testing

- Complete Edit @ ₹249 workflow with validation
- Form validation testing
- Navigation and UX testing
- Auto-population feature verification
- **19 steps** - Full workflow without music selection

#### **@music_integration_detailed** - YouTube Music Integration

- Complete song search and selection workflow
- YouTube video search and preview
- Audio selection and time configuration
- **20 steps** - Full music integration testing

#### **@edge_cases_validation** - Navigation & Edge Cases

- Form validation with empty fields
- Previous/Next navigation testing
- Minimal data entry workflows
- **19 steps** - Edge case and navigation testing

### **🔌 API Testing Scenarios**

#### **Authentication Tests**

- Valid credential login
- Invalid credential handling
- Malformed input validation
- Empty field validation
- Security testing (SQL injection, oversized input)

#### **Profile Management Tests**

- Profile data retrieval
- Profile updates
- Data validation
- Error handling

## 🧠 AI Intelligence Features

### **Automatic Test Type Detection**

The AI agent automatically determines whether to use API tools or browser automation based on:

#### **Browser Testing Indicators**

- Web page URLs (e.g., `https://stage.invitedekho.com`)
- UI interaction language ("click button", "enter text", "navigate to")
- Form filling and user workflow descriptions
- Visual verification steps

#### **API Testing Indicators**

- API endpoint URLs (e.g., `https://api.stage.invitedekho.com`)
- HTTP method language ("POST request", "GET data")
- JSON data structures
- Response validation steps

### **Smart Step Processing**

- **Given Steps**: Context setup and acknowledgment
- **When Steps**: Action execution (API calls or browser interactions)
- **Then/And Steps**: Validation of previous results

### **Natural Language Understanding Examples**

#### **Browser Automation Examples**

```gherkin
When I navigate to "https://stage.invitedekho.com/designs/wedding-video-invitation/romancia-glassy-love/"
When I click the "Edit Yourself @ ₹249" button
When I enter song name "Perfect by Ed Sheeran" in search field
And I click the "Search" button
And I click the first YouTube video result
And I click the "Select Audio" button
```

#### **API Testing Examples**

```gherkin
When I login with email "admin@invitedekho.com" and password "Test@123456"
When I try to login with invalid email "wrong@test.com" and password "Test@123"
Then I should receive an authentication error response
And the error should indicate invalid credentials
```

#### **Mixed Scenarios**

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

## 🔧 Configuration & Settings

### **Browser Settings**

- **Headless Mode**: Enabled (no visible browser windows)
- **Viewport**: 1400x900 for consistent rendering
- **Screenshots**: Auto-captured and organized by feature/scenario
- **Waits**: 3-second implicit waits after browser operations
- **User Data**: Temporary session directories for isolation

### **API Settings**

- **Base URLs**: Configured for InviteDeKho staging environment
- **Timeouts**: Reasonable defaults for API responses
- **Validation**: Automatic response schema validation
- **Error Handling**: Intelligent error interpretation and reporting

### **Custom MCP Server Configuration**

You can customize the MCP server startup in `src/browser_handler.py`:

```python
server_params = StdioServerParameters(
    command="npx",
    args=[
        "@playwright/mcp@latest",
        "--browser=chromium",
        "--headless",  # Run headless
        "--viewport-size=1920,1080",  # Custom viewport
        "--no-sandbox",
        "--user-data-dir=/tmp/playwright-custom-session"
    ],
    env={
        "HEADLESS": "true",
        "PLAYWRIGHT_HEADLESS": "true"
    }
)
```

## 📊 Test Results & Reporting

### **Console Output**

```
✅ AI Step executed successfully: I navigate to https://stage.invitedekho.com
✅ AI Step executed successfully: I click the "Edit Yourself @ ₹249" button
✅ AI Step executed successfully: I enter song name "Perfect by Ed Sheeran" in search field

📊 Test Summary:
   3 scenarios passed, 0 failed
   58 steps passed, 0 failed
   Total execution time: 8m10s
```

### **Screenshot Organization**

```
screenshots/
├── edit_yourself_249_comprehensive/
│   ├── complete_edit____249_workflow_with_validation_and_ux_testing/
│   ├── complete_youtube_music_search_and_selection_verification/
│   └── test_navigation__validation__and_edge_cases/
└── user_profile_comprehensive_tests/
    └── complete_user_workflow_testing/
```

### **Detailed Logging**

- AI decision-making process
- Step classification (browser vs API)
- MCP server communication
- Execution timing and performance
- Error details and recovery attempts

## 🛠️ Troubleshooting

### **MCP Server Issues**

#### **Server Won't Start**

```bash
# Check if port is in use
lsof -i :3000

# Kill existing processes
pkill -f "playwright.*mcp"

# Check Node.js version
node --version  # Needs v16+
```

#### **Connection Issues**

```bash
# Verify server is running
curl http://[::1]:3000/sse

# Check firewall settings - ensure port 3000 is accessible

# IPv6 vs IPv4 - try IPv4 if issues
# In browser_handler.py, change:
# self.mcp_server_url = "http://127.0.0.1:3000/sse"
```

### **Browser Issues**

#### **Browser Launch Failed**

```bash
# Install Chrome/Chromium
npm install @playwright/test
npx playwright install chromium

# Set display environment (Linux)
export DISPLAY=:0
```

#### **Browser Not Found**

```bash
# Verify installation
npx playwright install --dry-run

# Manual browser install
npx playwright install chromium --force
```

### **Python Integration Issues**

#### **MCP Client Connection Failed**

```bash
# Install MCP dependencies
pip install mcp fastmcp aiohttp

# Test MCP connection
python -c "from src.browser_handler import BrowserMCPHandler; h = BrowserMCPHandler(); print('✅ MCP client working')"
```

#### **AI Classification Issues**

```bash
# Verify API keys
echo $GOOGLE_API_KEY  # Should not be empty
echo $USE_GEMINI      # Should be 'true' or 'false'

# Test AI classification
python -c "from src.ai_step_handler import ai_decide_tool; print(ai_decide_tool('click button'))"
```

### **Common Error Messages**

| Error                              | Cause                           | Solution                                |
| ---------------------------------- | ------------------------------- | --------------------------------------- |
| `Connection refused`               | MCP server not running          | Start with `npx @playwright/mcp@latest` |
| `Port already in use`              | Another service using port 3000 | Kill process or change port             |
| `Module not found: mcp.client.sse` | Missing MCP library             | `pip install mcp[sse]`                  |
| `Browser launch failed`            | Chrome not found                | `npx playwright install chromium`       |
| `ValidationError missing data`     | POST/PUT without data           | Always include data parameter           |

## 📝 Writing Effective Test Scenarios

### **Browser Testing Best Practices**

```gherkin
# ✅ Good - Natural, specific language
When I click the "Edit Yourself @ ₹249" button
When I enter pincode "400001"
When I fill wedding function details with date "15/06/2025" and time "18:00"

# ❌ Avoid - Vague or overly technical
When I interact with the UI element
When I perform data entry operations
```

### **API Testing Best Practices**

```gherkin
# ✅ Good - Clear action with specific data
When I login with email "admin@invitedekho.com" and password "Test@123456"
Then I should receive a successful authentication response

# ❌ Avoid - Missing data or unclear intent
When I try to login
Then something should happen
```

### **Natural Language Guidelines**

#### **Writing Natural Language Steps**

1. **Be Explicit**: Use clear, descriptive language
2. **Include Context**: Specify elements clearly ("email field", "submit button")
3. **Use Quotes**: Put values in quotes ("username@example.com")
4. **Sequential Steps**: Break complex workflows into clear, sequential steps

#### **Step Type Guidelines**

- **Given**: Context setup (no actions)
- **When**: Actions (API calls or browser interactions)
- **Then/And**: Assertions (validate previous results)

### **MCP Integration Best Practices**

1. **Connection Management**: Each scenario gets a fresh MCP connection
2. **Error Handling**: Graceful fallback when MCP tools fail
3. **Tool Selection**: System automatically selects best MCP tool for instruction
4. **Resource Management**: Automatic cleanup prevents memory leaks
5. **Efficient Parsing**: Smart natural language to MCP tool mapping

## 🚀 Advanced Features & Extensions

### **Performance Optimization**

- **Connection Reuse**: MCP connection persists throughout scenario
- **Headless Execution**: No visual browser interference for speed
- **Efficient Screenshot Management**: Organized storage without redundancy
- **Optimized Wait Strategies**: Smart timing for reliable tests

### **Extensibility Options**

#### **Adding New Natural Language Patterns**

Extend `_parse_instruction_to_mcp_tool()` in `browser_handler.py`:

```python
elif "scroll" in instruction_lower:
    return "browser_press_key", {"key": "PageDown"}
elif "refresh" in instruction_lower:
    return "browser_press_key", {"key": "F5"}
```

#### **Custom Validation Rules**

Add new validation patterns in `ai_step_handler.py`:

```python
def custom_validation(step_text, previous_result):
    if "should contain user data" in step_text:
        return validate_user_data_presence(previous_result)
    return True
```

### **Future Enhancements**

- [ ] Visual element selection via screenshots
- [ ] Advanced MCP tool chaining
- [ ] Parallel browser sessions
- [ ] Mobile device emulation
- [ ] Custom MCP server configurations

## 🎯 Success Metrics & Results

### **Recent Test Results**

- **✅ 100% Pass Rate**: All consolidated scenarios passing
- **⚡ 8m10s Total Time**: Efficient execution across 58 steps
- **🎯 Maximum Coverage**: Comprehensive testing with minimal repetition
- **🧹 Clean Output**: Organized, focused reporting

### **Key Achievements**

- **Consolidated Testing**: Reduced from 5 repetitive scenarios to 3 focused ones
- **Intelligent Automation**: AI-driven test type detection and execution
- **Organized Screenshots**: Automatic capture and organization
- **Headless Execution**: No visual browser interference
- **Natural Language**: Plain English test scenario writing

### **Performance Comparison**

| Aspect               | Direct Playwright         | Playwright MCP           | Our AI Integration            |
| -------------------- | ------------------------- | ------------------------ | ----------------------------- |
| **Setup**            | Complex async management  | Simple client connection | AI-powered automation         |
| **Capabilities**     | Limited to coded actions  | 25+ pre-built tools      | Natural language + AI routing |
| **Natural Language** | Manual parsing required   | Built-in interpretation  | AI classification + routing   |
| **Maintenance**      | Custom browser management | MCP server handles all   | Zero maintenance              |
| **Extensibility**    | Code new features         | Use existing MCP tools   | AI adapts automatically       |
| **Debugging**        | Custom logging            | MCP protocol debugging   | AI decision logging           |

## 🚀 Getting Started Examples

### **Example 1: Browser Workflow Test**

```gherkin
Scenario: Complete Edit @ ₹249 workflow
  When I navigate to "https://stage.invitedekho.com/designs/wedding-video-invitation/romancia-glassy-love/"
  And I click the "Edit Yourself @ ₹249" button
  And I handle any popup by clicking "Close" if present
  When I enter pincode "400001"
  And I click the "Next" button
  When I click the bride option
  And I click the "Next" button
  # ... continue with workflow steps
```

### **Example 2: API Authentication Test**

```gherkin
Scenario: Successful login with valid credentials
  Given the API is available at https://api.stage.invitedekho.com
  When I login with email "admin@invitedekho.com" and password "Test@123456"
  Then I should receive a successful authentication response
  And the response should contain a valid JWT token
```

### **Example 3: Mixed API + Browser Test**

```gherkin
Scenario: End-to-end user journey
  # API setup
  Given I create a test user via API

  # Browser testing
  When I navigate to the login page
  And I login with the test user credentials
  Then I should see the user dashboard

  # API verification
  And the user session should be active via API
```

## 🎯 Philosophy

**Intelligence over Configuration**: This framework prioritizes smart interpretation over rigid rules, enabling natural language testing that adapts to your needs.

**Simplicity over Complexity**: Clean, focused output and minimal setup requirements make testing accessible and efficient.

**Coverage over Repetition**: Consolidated scenarios provide maximum test coverage with minimal duplication and maintenance overhead.

**Unified Testing**: Seamlessly combine API and browser testing in natural language scenarios with AI-powered routing.
