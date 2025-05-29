# AI API Test Agent

An intelligent API testing framework that uses AI to interpret natural language test scenarios and execute them automatically.

## Overview

This project implements an AI-powered agent that:

- Interprets BDD scenarios written in natural language
- Automatically determines the appropriate API calls to make
- Validates responses intelligently
- Provides concise, actionable feedback

## Key Features

- **Natural Language Testing**: Write tests in plain English
- **AI-Driven Execution**: Smart interpretation of test intentions
- **Minimal Logging**: Clean, focused output without redundancy
- **Flexible Validation**: Intelligent response checking

## Project Structure

```
api-test-agent/
├── features/                 # Gherkin feature files
│   ├── ai_api_tests.feature # Sample AI-driven tests
│   └── steps/               # Step definitions
│       ├── ai_steps.py      # AI-powered step handler
│       └── api_steps.py     # Compatibility layer
├── src/
│   ├── agent.py             # Main AI agent logic
│   ├── api_tools.py         # API interaction tools
│   ├── ai_step_handler.py   # AI step processing
│   └── intelligent_validator.py # Smart validation
├── requirements.txt         # Dependencies
└── README.md               # This file
```

## Quick Start

1. Install dependencies: `pip install -r requirements.txt`
2. Set up your OpenAI API key in `.env`
3. Run tests: `behave features/ai_api_tests.feature`

## Writing AI-Compatible Scenarios

To ensure your scenarios work effectively with the AI agent, follow these proven patterns and guidelines:

### 📋 **Step Type Guidelines**

#### ✅ **"Given" Steps - Context Setup**

Use for establishing test preconditions. The AI will acknowledge these without making API calls.

```gherkin
Given the API is available at https://api.example.com
Given the system is ready for testing
Given the authentication service is configured
```

#### ✅ **"When" Steps - Actions**

Use for actual operations that should trigger API calls. Be specific about credentials and data.

```gherkin
When I login with email "admin@example.com" and password "SecurePass123"
When I try to login with invalid email "wrong@test.com" and password "Test@123"
When I attempt to login with malformed email "not-an-email" and password "Test@123"
```

#### ✅ **"Then" and "And" Steps - Assertions**

Use for verifying results of previous actions. These will examine previous API responses, not make new calls.

```gherkin
Then I should receive a successful authentication response
And the response should contain a valid JWT token
And the token should be properly formatted and not empty
Then I should receive an authentication error response
And the error should indicate invalid credentials
```

### 🎯 **Data Extraction Patterns**

#### ✅ **Clear Email/Password Specification**

```gherkin
When I login with email "user@domain.com" and password "MyPassword123"
When I try to login with invalid email "wrong@test.com" and password "Test@123456"
```

#### ✅ **Empty Credentials Handling**

```gherkin
When I try to login with empty email and password fields
```

#### ✅ **Malformed Data Testing**

```gherkin
When I try to login with malformed email "not-an-email" and password "Test@123456"
```

### 🔧 **Technical Best Practices**

#### ✅ **Complete URLs**

Always reference complete URLs from API contracts, not relative paths:

```gherkin
# ✅ Good
Given the InviteDeKho API is available at https://api.stage.invitedekho.com

# ❌ Avoid
Given the API is available at /api
```

#### ✅ **Reasonable Content Length**

Avoid extremely long test data that could cause context length issues:

```gherkin
# ✅ Good
When I try to login with a long password of 100 characters

# ❌ Avoid
When I try to login with password "Aa123456789!..." (1000+ characters)
```

#### ✅ **Specific Assertion Language**

Use clear, specific language for assertions:

```gherkin
# ✅ Good
Then I should receive an authentication error response
And the error should indicate invalid credentials
And the response should contain a valid JWT token

# ❌ Avoid vague assertions
Then something should happen
And it should work correctly
```

### 🚫 **Common Anti-Patterns to Avoid**

#### ❌ **Don't Mix Actions and Assertions**

```gherkin
# ❌ Wrong - This mixes action with assertion
Then I login and should get a success response

# ✅ Correct - Separate action and assertion
When I login with valid credentials
Then I should receive a successful response
```

#### ❌ **Don't Use Assertion Words in Action Steps**

```gherkin
# ❌ Wrong - "should" suggests assertion but it's an action step
When I should login with credentials

# ✅ Correct - Clear action language
When I login with credentials
```

#### ❌ **Don't Create Ambiguous Steps**

```gherkin
# ❌ Wrong - Unclear what should happen
When I do something with the API

# ✅ Correct - Specific action
When I attempt to authenticate with invalid credentials
```

### 📝 **Scenario Structure Templates**

#### **Template 1: Successful Operation**

```gherkin
Scenario: Successful login with valid credentials
  Given the API is available at https://api.example.com
  When I login with email "valid@user.com" and password "ValidPass123"
  Then I should receive a successful authentication response
  And the response should contain a valid JWT token
  And the token should be properly formatted and not empty
```

#### **Template 2: Error Handling**

```gherkin
Scenario: Login failure with invalid credentials
  Given the API is available at https://api.example.com
  When I try to login with invalid email "wrong@test.com" and password "WrongPass"
  Then I should receive an authentication error response
  And the error should indicate invalid credentials
```

#### **Template 3: Input Validation**

```gherkin
Scenario: Malformed input handling
  Given the API is available at https://api.example.com
  When I try to login with malformed email "not-an-email" and password "Test@123"
  Then I should receive an email format validation error
  And the error should indicate invalid email format
```

### 🎯 **Key Success Factors**

1. **Clear Step Types**: Use Given/When/Then appropriately
2. **Specific Data**: Include exact email/password values in quotes
3. **Complete URLs**: Reference full API endpoints
4. **Focused Assertions**: One specific check per assertion step
5. **Reasonable Length**: Avoid extremely long test data
6. **Consistent Language**: Use clear, unambiguous wording

### 🚀 **Testing Your Scenarios**

Before running your scenarios:

1. **Review step types**: Ensure Given/When/Then are used correctly
2. **Check data extraction**: Verify email/password are clearly specified
3. **Validate assertions**: Confirm assertion steps examine previous responses
4. **Test incrementally**: Start with simple scenarios and build complexity

Following these guidelines will ensure your scenarios work reliably with the AI agent and provide clear, actionable test results.

## Philosophy

Less is more. This framework focuses on:

- Clarity over verbosity
- Intelligence over rigid rules
- Simplicity over complexity
