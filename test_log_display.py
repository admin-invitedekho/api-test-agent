#!/usr/bin/env python3
"""
Test script to verify log display in HTML report
"""

import json

def verify_log_matching():
    """Verify that logs are properly matched between test results and agent logs"""
    
    print("🔍 Verifying log matching in HTML report...")
    
    # Load test results
    try:
        with open('test_results_with_logs.json', 'r') as f:
            test_data = json.load(f)
        print("✅ Test results loaded")
    except FileNotFoundError:
        print("❌ test_results_with_logs.json not found")
        return False
    
    # Load agent logs
    try:
        with open('agent_logs.json', 'r') as f:
            agent_logs = json.load(f)
        print("✅ Agent logs loaded")
    except FileNotFoundError:
        print("❌ agent_logs.json not found")
        return False
    
    print("\n📊 Testing step matching logic...")
    
    total_steps = 0
    matched_steps = 0
    
    for feature in test_data:
        for element in feature.get('elements', []):
            if element.get('type') == 'scenario':
                scenario_name = element.get('name', 'Unknown Scenario')
                scenario_logs = agent_logs.get(scenario_name, {})
                
                print(f"\n🎯 Scenario: {scenario_name}")
                print(f"   Available logs: {list(scenario_logs.keys())}")
                
                for step in element.get('steps', []):
                    total_steps += 1
                    step_name = step.get('name', '')
                    step_keyword = step.get('keyword', '')
                    
                    # Test the same matching strategies as in HTML generator
                    step_logs = []
                    
                    # Strategy 1: Try exact match with keyword + name
                    step_with_keyword = f"{step_keyword}{step_name}"
                    if step_with_keyword in scenario_logs:
                        step_logs = scenario_logs[step_with_keyword]
                        matched_steps += 1
                        print(f"   ✅ Match 1: {step_keyword}{step_name} ({len(step_logs)} logs)")
                    
                    # Strategy 2: Try match with just the step name
                    elif step_name in scenario_logs:
                        step_logs = scenario_logs[step_name]
                        matched_steps += 1
                        print(f"   ✅ Match 2: {step_name} ({len(step_logs)} logs)")
                    
                    # Strategy 3: Try fuzzy matching
                    else:
                        for log_key, logs in scenario_logs.items():
                            if step_name in log_key or log_key in step_name:
                                step_logs = logs
                                matched_steps += 1
                                print(f"   ✅ Match 3: {step_name} -> {log_key} ({len(step_logs)} logs)")
                                break
                        
                        if not step_logs:
                            print(f"   ❌ No match: {step_keyword}{step_name}")
    
    print(f"\n📈 Summary:")
    print(f"   Total steps: {total_steps}")
    print(f"   Matched steps: {matched_steps}")
    print(f"   Match rate: {matched_steps/total_steps*100:.1f}%")
    
    if matched_steps > 0:
        print("\n✅ Log matching is working! You should see logs in the HTML report.")
        print("🌐 Open enhanced_test_report.html to view the logs.")
        print("💡 Click on scenario titles to expand, then click 'Logs' buttons to view step details.")
    else:
        print("\n❌ No logs matched. Check the log capture mechanism.")
    
    return matched_steps > 0

if __name__ == "__main__":
    verify_log_matching() 