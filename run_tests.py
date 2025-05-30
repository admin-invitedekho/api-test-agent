#!/usr/bin/env python3
"""
Simple script to run Behave tests.
"""

import subprocess
import sys
import os
from datetime import datetime

def get_scenarios():
    """Extract scenario names from the feature file"""
    scenarios = []
    try:
        with open('features/invitedekho_login_tests.feature', 'r') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if line.startswith('Scenario:'):
                    scenario_name = line.replace('Scenario:', '').strip()
                    scenarios.append(scenario_name)
        return scenarios
    except FileNotFoundError:
        print("❌ Feature file not found")
        return []

def run_scenario_individually(scenario_name):
    """Run a single scenario and capture results"""
    print(f"🧪 Running scenario: {scenario_name}")
    
    try:
        result = subprocess.run([
            'behave', 
            'features/invitedekho_login_tests.feature',
            '-n', scenario_name,
            '--no-capture'
        ], capture_output=True, text=True, timeout=120)
        
        success = result.returncode == 0
        print(f"{'✅' if success else '❌'} Scenario: {scenario_name} - {'PASSED' if success else 'FAILED'}")
        
        if not success:
            print(f"   Error output: {result.stderr[:200]}...")
        
        return {
            'name': scenario_name,
            'success': success,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
        
    except subprocess.TimeoutExpired:
        print(f"❌ Scenario '{scenario_name}' timed out")
        return {
            'name': scenario_name,
            'success': False,
            'stdout': '',
            'stderr': 'Test timed out after 120 seconds',
            'returncode': -1
        }
    except Exception as e:
        print(f"❌ Error running scenario '{scenario_name}': {e}")
        return {
            'name': scenario_name,
            'success': False,
            'stdout': '',
            'stderr': str(e),
            'returncode': -1
        }

def run_all_tests():
    """Run all test scenarios"""
    
    print("🚀 Running all test scenarios...")
    
    scenarios = get_scenarios()
    if not scenarios:
        print("❌ No scenarios found")
        return False
    
    print(f"📋 Found {len(scenarios)} scenarios to test")
    
    # Run each scenario individually 
    all_results = []
    passed = 0
    failed = 0
    
    for scenario in scenarios:
        result = run_scenario_individually(scenario)
        all_results.append(result)
        if result['success']:
            passed += 1
        else:
            failed += 1
    
    # Also run all scenarios together for a final summary
    print("\n🎯 Running all scenarios together...")
    try:
        result = subprocess.run([
            'behave', 
            'features/invitedekho_login_tests.feature',
            '--no-capture'
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ All scenarios passed in combined run")
        else:
            print("❌ Some scenarios failed in combined run")
            
    except Exception as e:
        print(f"⚠️ Combined run had issues: {e}")
    
    # Print summary
    print(f"\n📊 Test Summary:")
    print(f"   Total Scenarios: {len(scenarios)}")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   Success Rate: {(passed/len(scenarios)*100):.1f}%")
    
    if failed > 0:
        print(f"\n❌ Failed scenarios:")
        for result in all_results:
            if not result['success']:
                print(f"   - {result['name']}")
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 