#!/usr/bin/env python3
"""
Test that each browser session starts fresh (not logged in)
"""
import os
import sys
import timeout_decorator

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ui_handler import run_browser_instruction, clear_browser_session

@timeout_decorator.timeout(60)  # 60 second timeout
def test_fresh_session():
    """Test that each session starts fresh"""
    
    print("🚀 Testing fresh session behavior...")
    
    # Test 1: Check initial state
    print("\n=== Test 1: Check initial state (should NOT be logged in) ===")
    clear_browser_session()
    
    result1 = run_browser_instruction(
        "Navigate to https://stage.invitedekho.com and check if user is already logged in. Look for login button vs logout button.",
        headless=True,
        fresh_session=True
    )
    
    print(f"Status: {result1.get('status')}")
    print(f"Result: {result1.get('result', '')[:300]}...")
    
    # Test 2: Login 
    print("\n=== Test 2: Perform login ===")
    result2 = run_browser_instruction(
        "Go to https://stage.invitedekho.com, click login, select email login, and login with admin@invitedekho.com / Test@123456",
        headless=True,
        fresh_session=True  # This should start a NEW session, not logged in
    )
    
    print(f"Status: {result2.get('status')}")
    print(f"Result: {result2.get('result', '')[:300]}...")
    
    # Test 3: Check state again (should NOT be logged in due to fresh session)
    print("\n=== Test 3: Check state again (should NOT be logged in) ===")
    result3 = run_browser_instruction(
        "Navigate to https://stage.invitedekho.com and check if user is already logged in. Look for login button vs logout button.",
        headless=True,
        fresh_session=True  # This should start ANOTHER fresh session
    )
    
    print(f"Status: {result3.get('status')}")
    print(f"Result: {result3.get('result', '')[:300]}...")
    
    # Analyze results
    result1_text = str(result1.get('result', '')).lower()
    result3_text = str(result3.get('result', '')).lower()
    
    # Both should show login button (not logged in)
    login_indicators = ['login', 'sign in', 'not logged', 'login button']
    logout_indicators = ['logout', 'sign out', 'logged in', 'dashboard']
    
    test1_has_login = any(indicator in result1_text for indicator in login_indicators)
    test3_has_login = any(indicator in result3_text for indicator in login_indicators)
    
    print("\n=== Analysis ===")
    print(f"Test 1 shows login needed: {test1_has_login}")
    print(f"Test 3 shows login needed: {test3_has_login}")
    
    if test1_has_login and test3_has_login:
        print("✅ SUCCESS: Each session starts fresh (not logged in)")
        return True
    else:
        print("❌ CONCERN: Sessions might be persisting login state")
        return False

if __name__ == "__main__":
    try:
        success = test_fresh_session()
        if success:
            print("\n✅ Fresh session test passed!")
        else:
            print("\n⚠️  Fresh session test shows potential session persistence")
    except timeout_decorator.TimeoutError:
        print("\n⏰ TIMEOUT: Test took longer than 60 seconds")
    except Exception as e:
        print(f"\n💥 UNEXPECTED ERROR: {e}")
    finally:
        clear_browser_session() 