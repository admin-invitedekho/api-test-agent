# Browser Automation Tests

This document describes the essential browser automation test files for the BrowserUse integration.

## Test Files

### 1. `test_complete_fresh_login.py`

**Primary Test - Complete Login Flow**

- **Purpose**: Demonstrates the complete 5-step login process for stage.invitedekho.com
- **Features**:
  - Fresh browser session (not logged in)
  - Complete workflow from navigation to login verification
  - Uses real credentials: admin@invitedekho.com / Test@123456
- **Steps Tested**:
  1. Navigate to https://stage.invitedekho.com
  2. Click the login button
  3. Select email login option
  4. Fill and submit credentials
  5. Verify login success

**Usage**:

```bash
python test_complete_fresh_login.py
```

### 2. `test_fresh_session.py`

**Verification Test - Session Management**

- **Purpose**: Proves that each browser session starts fresh (not logged in)
- **Features**:
  - Tests session isolation
  - Confirms no state bleeding between tests
  - Validates temporary directory cleanup
- **Test Flow**:
  1. Check initial state (should show login button)
  2. Perform login in fresh session
  3. Check state again (should show login button again)

**Usage**:

```bash
python test_fresh_session.py
```

## Key Features

### Fresh Session Management

- Each test creates a unique temporary directory
- Incognito mode with privacy flags
- Automatic cleanup after each test
- No session persistence between tests

### Real Browser Automation

- Uses BrowserUse library v0.2.5+
- AI-powered element detection and interaction
- Handles dynamic UI elements
- Screenshots and error reporting

### Integration with Test Framework

- Works with existing Behave test framework
- AI routing between API and browser automation
- Centralized step handler in `enhanced_steps.py`

## Cleanup Notes

The following development/intermediate test files were removed during cleanup:

- `test_browser_simple.py` - Early development test
- `test_invitedekho_login.py` - Intermediate test version
- `test_invitedekho_simple.py` - Development test
- `test_invitedekho_steps.py` - Failed multi-session approach
- `test_invitedekho_persistent.py` - Intermediate version
- `pretty.output` - Temporary output file

Only essential, working test files remain to demonstrate the final functionality.
