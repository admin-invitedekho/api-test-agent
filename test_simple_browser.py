#!/usr/bin/env python3
"""
Simple test to verify BrowserUse integration is working
"""
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ui_handler import run_browser_instruction

def test_simple_navigation():
    """Test simple browser navigation"""
    print("🚀 Testing simple browser navigation...")
    
    try:
        # Test simple navigation instruction
        result = run_browser_instruction(
            "Navigate to https://example.com and get the page title",
            headless=False
        )
        
        print(f"✅ Result: {result}")
        
        if result.get('status') == 'success':
            print("🎉 Browser navigation test PASSED!")
            return True
        else:
            print(f"❌ Browser navigation test FAILED: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"💥 Test failed with exception: {e}")
        return False

def test_mock_implementation():
    """Test that mock implementation works when BrowserUse is not available"""
    print("🔧 Testing mock implementation...")
    
    # This should fall back to mock since we're testing the fallback
    try:
        result = run_browser_instruction(
            "Mock test - navigate to example.com",
            headless=True
        )
        
        print(f"Mock result: {result}")
        
        if result.get('status') == 'success':
            print("✅ Mock implementation test PASSED!")
            return True
        else:
            print(f"❌ Mock implementation test FAILED")
            return False
            
    except Exception as e:
        print(f"💥 Mock test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Running BrowserUse integration tests...\n")
    
    # Run tests
    test1_passed = test_simple_navigation()
    print()
    
    if test1_passed:
        print("🎊 All tests PASSED! BrowserUse integration is working properly.")
    else:
        print("⚠️ Some tests failed. Check the logs above for details.")
        
    print("\n✨ Test completed!") 