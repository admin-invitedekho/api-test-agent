#!/usr/bin/env python3
"""
Simple HTML Report Generator for Behave Test Results
Converts JSON test results into a beautiful HTML report.
"""

import json
import datetime
from pathlib import Path

def generate_html_report(json_file="test_results_pretty.json", output_file="test_report.html"):
    """Generate HTML report from JSON test results"""
    
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: {json_file} not found. Please run tests first.")
        return False
    
    # Extract test statistics
    features = data
    total_scenarios = 0
    passed_scenarios = 0
    failed_scenarios = 0
    total_steps = 0
    passed_steps = 0
    failed_steps = 0
    
    for feature in features:
        for element in feature.get('elements', []):
            if element.get('type') == 'scenario':
                total_scenarios += 1
                scenario_passed = True
                
                for step in element.get('steps', []):
                    total_steps += 1
                    if step.get('result', {}).get('status') == 'passed':
                        passed_steps += 1
                    else:
                        failed_steps += 1
                        scenario_passed = False
                
                if scenario_passed:
                    passed_scenarios += 1
                else:
                    failed_scenarios += 1
    
    # Calculate success rate
    success_rate = (passed_scenarios / total_scenarios * 100) if total_scenarios > 0 else 0
    
    # Generate HTML report
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI API Test Report</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            
            .header {{
                background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            
            .header h1 {{
                font-size: 2.5em;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }}
            
            .header p {{
                font-size: 1.2em;
                opacity: 0.9;
            }}
            
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                padding: 30px;
                background: #f8f9fa;
            }}
            
            .stat-card {{
                background: white;
                padding: 25px;
                border-radius: 10px;
                text-align: center;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                transition: transform 0.3s ease;
            }}
            
            .stat-card:hover {{
                transform: translateY(-5px);
            }}
            
            .stat-number {{
                font-size: 2.5em;
                font-weight: bold;
                margin-bottom: 10px;
            }}
            
            .stat-label {{
                color: #666;
                font-size: 1.1em;
            }}
            
            .success {{ color: #4CAF50; }}
            .error {{ color: #f44336; }}
            .info {{ color: #2196F3; }}
            .warning {{ color: #FF9800; }}
            
            .success-rate {{
                font-size: 3em !important;
                background: linear-gradient(45deg, #4CAF50, #45a049);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}
            
            .scenarios-section {{
                padding: 30px;
            }}
            
            .section-title {{
                font-size: 1.8em;
                margin-bottom: 20px;
                color: #333;
                border-bottom: 3px solid #4CAF50;
                padding-bottom: 10px;
            }}
            
            .scenario-card {{
                background: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                margin-bottom: 15px;
                overflow: hidden;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
            
            .scenario-header {{
                padding: 15px 20px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                cursor: pointer;
                transition: background 0.3s ease;
            }}
            
            .scenario-header:hover {{
                background: #f5f5f5;
            }}
            
            .scenario-title {{
                font-weight: bold;
                font-size: 1.1em;
            }}
            
            .scenario-status {{
                padding: 5px 15px;
                border-radius: 20px;
                font-weight: bold;
                font-size: 0.9em;
            }}
            
            .status-passed {{
                background: #e8f5e8;
                color: #4CAF50;
            }}
            
            .status-failed {{
                background: #fdeaea;
                color: #f44336;
            }}
            
            .scenario-details {{
                padding: 0 20px 20px;
                background: #fafafa;
                border-top: 1px solid #eee;
            }}
            
            .steps-list {{
                list-style: none;
                margin-top: 15px;
            }}
            
            .step-item {{
                padding: 8px 0;
                border-bottom: 1px solid #eee;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            
            .step-text {{
                flex: 1;
            }}
            
            .step-status {{
                padding: 3px 8px;
                border-radius: 12px;
                font-size: 0.8em;
                font-weight: bold;
            }}
            
            .footer {{
                background: #333;
                color: white;
                text-align: center;
                padding: 20px;
                font-size: 0.9em;
            }}
            
            @media (max-width: 768px) {{
                .stats-grid {{
                    grid-template-columns: repeat(2, 1fr);
                    padding: 20px;
                }}
                
                .header h1 {{
                    font-size: 2em;
                }}
                
                .scenarios-section {{
                    padding: 20px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 AI API Test Report</h1>
                <p>Generated on {datetime.datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number success-rate">{success_rate:.1f}%</div>
                    <div class="stat-label">Success Rate</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number success">{passed_scenarios}</div>
                    <div class="stat-label">Passed Scenarios</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number error">{failed_scenarios}</div>
                    <div class="stat-label">Failed Scenarios</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number info">{total_scenarios}</div>
                    <div class="stat-label">Total Scenarios</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number success">{passed_steps}</div>
                    <div class="stat-label">Passed Steps</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number error">{failed_steps}</div>
                    <div class="stat-label">Failed Steps</div>
                </div>
            </div>
            
            <div class="scenarios-section">
                <h2 class="section-title">📋 Test Scenarios</h2>
    """
    
    # Add scenario details
    for feature in features:
        feature_name = feature.get('name', 'Unknown Feature')
        
        for element in feature.get('elements', []):
            if element.get('type') == 'scenario':
                scenario_name = element.get('name', 'Unknown Scenario')
                
                # Determine scenario status
                scenario_passed = True
                scenario_steps = []
                
                for step in element.get('steps', []):
                    step_status = step.get('result', {}).get('status', 'unknown')
                    if step_status != 'passed':
                        scenario_passed = False
                    
                    scenario_steps.append({
                        'keyword': step.get('keyword', ''),
                        'name': step.get('name', ''),
                        'status': step_status,
                        'duration': step.get('result', {}).get('duration', 0)
                    })
                
                status_class = 'status-passed' if scenario_passed else 'status-failed'
                status_text = '✅ PASSED' if scenario_passed else '❌ FAILED'
                
                html_content += f"""
                <div class="scenario-card">
                    <div class="scenario-header">
                        <div class="scenario-title">{scenario_name}</div>
                        <div class="scenario-status {status_class}">{status_text}</div>
                    </div>
                    <div class="scenario-details">
                        <strong>Feature:</strong> {feature_name}
                        <ul class="steps-list">
                """
                
                for step in scenario_steps:
                    step_status_class = 'status-passed' if step['status'] == 'passed' else 'status-failed'
                    step_status_text = '✅' if step['status'] == 'passed' else '❌'
                    duration_text = f" ({step['duration']:.3f}s)" if step['duration'] > 0 else ""
                    
                    html_content += f"""
                            <li class="step-item">
                                <span class="step-text">{step['keyword']}{step['name']}</span>
                                <span class="step-status {step_status_class}">{step_status_text}{duration_text}</span>
                            </li>
                    """
                
                html_content += """
                        </ul>
                    </div>
                </div>
                """
    
    html_content += f"""
            </div>
            
            <div class="footer">
                Generated by AI API Test Agent | Framework powered by Behave + LangChain
            </div>
        </div>
        
        <script>
            // Add click functionality to scenario headers
            document.querySelectorAll('.scenario-header').forEach(header => {{
                header.addEventListener('click', function() {{
                    const details = this.nextElementSibling;
                    if (details.style.display === 'none') {{
                        details.style.display = 'block';
                    }} else {{
                        details.style.display = 'none';
                    }}
                }});
            }});
            
            // Initially hide scenario details
            document.querySelectorAll('.scenario-details').forEach(details => {{
                details.style.display = 'none';
            }});
        </script>
    </body>
    </html>
    """
    
    # Write HTML file
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    print(f"✅ HTML report generated: {output_file}")
    print(f"📊 Test Summary: {passed_scenarios}/{total_scenarios} scenarios passed ({success_rate:.1f}%)")
    
    return True

def generate_html_report_with_logs(json_file="test_results_with_logs.json", logs_file="agent_logs.json", output_file="enhanced_test_report.html"):
    """Generate enhanced HTML report with agent logs included"""
    
    try:
        with open(json_file, 'r') as f:
            test_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: {json_file} not found. Please run tests first.")
        return False
    
    try:
        with open(logs_file, 'r') as f:
            agent_logs = json.load(f)
    except FileNotFoundError:
        print(f"⚠️ Warning: {logs_file} not found. Generating report without agent logs.")
        agent_logs = {}
    
    # Extract test statistics
    features = test_data
    total_scenarios = 0
    passed_scenarios = 0
    failed_scenarios = 0
    total_steps = 0
    passed_steps = 0
    failed_steps = 0
    
    for feature in features:
        for element in feature.get('elements', []):
            if element.get('type') == 'scenario':
                total_scenarios += 1
                scenario_passed = True
                
                for step in element.get('steps', []):
                    total_steps += 1
                    if step.get('result', {}).get('status') == 'passed':
                        passed_steps += 1
                    else:
                        failed_steps += 1
                        scenario_passed = False
                
                if scenario_passed:
                    passed_scenarios += 1
                else:
                    failed_scenarios += 1
    
    # Calculate success rate
    success_rate = (passed_scenarios / total_scenarios * 100) if total_scenarios > 0 else 0
    
    # Generate enhanced HTML report with logs
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Enhanced AI API Test Report</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            
            .container {{
                max-width: 1400px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            
            .header {{
                background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            
            .header h1 {{
                font-size: 2.5em;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }}
            
            .header p {{
                font-size: 1.2em;
                opacity: 0.9;
            }}
            
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                padding: 30px;
                background: #f8f9fa;
            }}
            
            .stat-card {{
                background: white;
                padding: 25px;
                border-radius: 10px;
                text-align: center;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                transition: transform 0.3s ease;
            }}
            
            .stat-card:hover {{
                transform: translateY(-5px);
            }}
            
            .stat-number {{
                font-size: 2.5em;
                font-weight: bold;
                margin-bottom: 10px;
            }}
            
            .stat-label {{
                color: #666;
                font-size: 1.1em;
            }}
            
            .success {{ color: #4CAF50; }}
            .error {{ color: #f44336; }}
            .info {{ color: #2196F3; }}
            .warning {{ color: #FF9800; }}
            
            .success-rate {{
                font-size: 3em !important;
                background: linear-gradient(45deg, #4CAF50, #45a049);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}
            
            .scenarios-section {{
                padding: 30px;
            }}
            
            .section-title {{
                font-size: 1.8em;
                margin-bottom: 20px;
                color: #333;
                border-bottom: 3px solid #4CAF50;
                padding-bottom: 10px;
            }}
            
            .scenario-card {{
                background: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                margin-bottom: 20px;
                overflow: hidden;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
            
            .scenario-header {{
                padding: 15px 20px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                cursor: pointer;
                transition: background 0.3s ease;
            }}
            
            .scenario-header:hover {{
                background: #f5f5f5;
            }}
            
            .scenario-title {{
                font-weight: bold;
                font-size: 1.1em;
            }}
            
            .scenario-status {{
                padding: 5px 15px;
                border-radius: 20px;
                font-weight: bold;
                font-size: 0.9em;
            }}
            
            .status-passed {{
                background: #e8f5e8;
                color: #4CAF50;
            }}
            
            .status-failed {{
                background: #fdeaea;
                color: #f44336;
            }}
            
            .scenario-details {{
                padding: 0 20px 20px;
                background: #fafafa;
                border-top: 1px solid #eee;
            }}
            
            .steps-list {{
                list-style: none;
                margin-top: 15px;
            }}
            
            .step-item {{
                margin-bottom: 15px;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                background: white;
            }}
            
            .step-header {{
                padding: 12px 15px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                cursor: pointer;
                transition: background 0.3s ease;
            }}
            
            .step-header:hover {{
                background: #f9f9f9;
            }}
            
            .step-text {{
                flex: 1;
                font-weight: 500;
            }}
            
            .step-status {{
                padding: 4px 10px;
                border-radius: 12px;
                font-size: 0.85em;
                font-weight: bold;
            }}
            
            .step-logs {{
                padding: 15px;
                background: #f8f9fa;
                border-top: 1px solid #e0e0e0;
                display: none;
            }}
            
            .logs-container {{
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                overflow: hidden;
            }}
            
            .logs-header {{
                background: #f8f9fa;
                padding: 12px 15px;
                border-bottom: 1px solid #e0e0e0;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            
            .log-count {{
                background: #007bff;
                color: white;
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 0.8em;
                font-weight: bold;
            }}
            
            .logs-content {{
                padding: 15px;
            }}
            
            .single-log-block {{
                background: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 6px;
                padding: 0;
                overflow: hidden;
            }}
            
            .combined-logs {{
                background: #ffffff;
                margin: 0;
                padding: 15px;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-size: 0.9em;
                line-height: 1.6;
                white-space: pre-wrap;
                word-wrap: break-word;
                border: none;
                border-radius: 0;
                color: #333;
                max-height: 400px;
                overflow-y: auto;
            }}
            
            .log-item {{
                margin-bottom: 8px;
                padding: 8px 12px;
                border-radius: 6px;
                font-family: 'Segoe UI', system-ui, sans-serif;
                font-size: 0.9em;
            }}
            
            .log-item:last-child {{
                margin-bottom: 0;
            }}
            
            .log-separator {{
                height: 1px;
                background: #e9ecef;
                margin: 10px 0;
            }}
            
            .log-timestamp {{
                font-size: 0.75em;
                color: #6c757d;
                margin-bottom: 4px;
            }}
            
            .log-content {{
                line-height: 1.4;
            }}
            
            .log-entry {{
                margin-bottom: 10px;
                padding: 8px 12px;
                border-radius: 6px;
                font-family: 'Courier New', monospace;
                font-size: 0.9em;
                white-space: pre-wrap;
                word-break: break-word;
            }}
            
            .log-info {{
                background: #e3f2fd;
                border-left: 4px solid #2196F3;
            }}
            
            .log-tool-call {{
                background: #fff3e0;
                border-left: 4px solid #FF9800;
            }}
            
            .log-api-response {{
                background: #e8f5e8;
                border-left: 4px solid #4CAF50;
            }}
            
            .log-error {{
                background: #ffebee;
                border-left: 4px solid #f44336;
            }}
            
            .api-details-toggle {{
                margin-top: 8px;
            }}
            
            .api-details-toggle summary {{
                cursor: pointer;
                font-weight: 500;
                color: #007bff;
                padding: 4px 0;
            }}
            
            .api-details-toggle summary:hover {{
                color: #0056b3;
            }}
            
            .api-details {{
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 10px;
                margin-top: 5px;
                font-family: 'Courier New', monospace;
                font-size: 0.85em;
                white-space: pre-wrap;
                overflow-x: auto;
                max-height: 300px;
                overflow-y: auto;
            }}
            
            .footer {{
                background: #333;
                color: white;
                text-align: center;
                padding: 20px;
                font-size: 0.9em;
            }}
            
            .logs-toggle {{
                background: #2196F3;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 0.8em;
                cursor: pointer;
                margin-left: 10px;
            }}
            
            .logs-toggle:hover {{
                background: #1976D2;
            }}
            
            @media (max-width: 768px) {{
                .stats-grid {{
                    grid-template-columns: repeat(2, 1fr);
                    padding: 20px;
                }}
                
                .header h1 {{
                    font-size: 2em;
                }}
                
                .scenarios-section {{
                    padding: 20px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 Enhanced AI API Test Report</h1>
                <p>Generated on {datetime.datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                <p>🔍 Includes detailed agent logs and API interactions</p>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number success-rate">{success_rate:.1f}%</div>
                    <div class="stat-label">Success Rate</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number success">{passed_scenarios}</div>
                    <div class="stat-label">Passed Scenarios</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number error">{failed_scenarios}</div>
                    <div class="stat-label">Failed Scenarios</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number info">{total_scenarios}</div>
                    <div class="stat-label">Total Scenarios</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number success">{passed_steps}</div>
                    <div class="stat-label">Passed Steps</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number error">{failed_steps}</div>
                    <div class="stat-label">Failed Steps</div>
                </div>
            </div>
            
            <div class="scenarios-section">
                <h2 class="section-title">📋 Test Scenarios with Agent Logs</h2>
    """
    
    # Add scenario details with logs
    for feature in features:
        feature_name = feature.get('name', 'Unknown Feature')
        
        for element in feature.get('elements', []):
            if element.get('type') == 'scenario':
                scenario_name = element.get('name', 'Unknown Scenario')
                
                # Determine scenario status
                scenario_passed = True
                scenario_steps = []
                
                for step in element.get('steps', []):
                    step_status = step.get('result', {}).get('status', 'unknown')
                    if step_status != 'passed':
                        scenario_passed = False
                    
                    step_text = f"{step.get('keyword', '')}{step.get('name', '')}"
                    scenario_steps.append({
                        'keyword': step.get('keyword', ''),
                        'name': step.get('name', ''),
                        'full_text': step_text,
                        'status': step_status,
                        'duration': step.get('result', {}).get('duration', 0)
                    })
                
                status_class = 'status-passed' if scenario_passed else 'status-failed'
                status_text = '✅ PASSED' if scenario_passed else '❌ FAILED'
                
                html_content += f"""
                <div class="scenario-card">
                    <div class="scenario-header">
                        <div class="scenario-title">{scenario_name}</div>
                        <div class="scenario-status {status_class}">{status_text}</div>
                    </div>
                    <div class="scenario-details">
                        <strong>Feature:</strong> {feature_name}
                        <ul class="steps-list">
                """
                
                # Get logs for this scenario
                scenario_logs = agent_logs.get(scenario_name, {})
                
                for step in scenario_steps:
                    step_status_class = 'status-passed' if step['status'] == 'passed' else 'status-failed'
                    step_status_text = '✅' if step['status'] == 'passed' else '❌'
                    duration_text = f" ({step['duration']:.3f}s)" if step['duration'] > 0 else ""
                    
                    # Get logs for this step - try multiple matching strategies
                    step_logs = []
                    
                    # Strategy 1: Try exact match with keyword + name (with space)
                    step_with_keyword = f"{step['keyword']} {step['name']}"
                    if step_with_keyword in scenario_logs:
                        step_logs = scenario_logs[step_with_keyword]
                    
                    # Strategy 2: Try exact match with keyword + name (without space)
                    elif f"{step['keyword']}{step['name']}" in scenario_logs:
                        step_logs = scenario_logs[f"{step['keyword']}{step['name']}"]
                    
                    # Strategy 3: Try match with just the step name
                    elif step['name'] in scenario_logs:
                        step_logs = scenario_logs[step['name']]
                    
                    # Strategy 4: Try fuzzy matching - look for logs that contain the step name
                    else:
                        for log_key, logs in scenario_logs.items():
                            if step['name'] in log_key or log_key in step['name']:
                                step_logs = logs
                                break
                    
                    logs_button = f'<button class="logs-toggle" onclick="toggleLogs(this)">👁️ Logs ({len(step_logs)})</button>' if step_logs else ''
                    
                    html_content += f"""
                            <li class="step-item">
                                <div class="step-header">
                                    <span class="step-text">{step['keyword']}{step['name']}</span>
                                    <span>
                                        <span class="step-status {step_status_class}">{step_status_text}{duration_text}</span>
                                        {logs_button}
                                    </span>
                                </div>
                    """
                    
                    # Add logs section if available
                    if step_logs:
                        html_content += f'''<div class="step-logs">
                            <div class="logs-container">
                                <div class="logs-header">
                                    <strong>📋 Step Execution Logs</strong>
                                    <span class="log-count">{len(step_logs)} entries</span>
                                </div>
                                <div class="logs-content">
                                    <div class="single-log-block">'''
                        
                        # Combine all logs into a single text block
                        log_text_parts = []
                        
                        for i, log_entry in enumerate(step_logs):
                            log_type = log_entry.get('type', 'info')
                            timestamp = log_entry.get('timestamp', '')
                            message = log_entry.get('message', '')
                            
                            # Format timestamp
                            time_part = f"🕒 {timestamp}" if timestamp else ""
                            
                            if log_type == 'tool_call':
                                tool_name = log_entry.get('tool', 'unknown')
                                endpoint = log_entry.get('endpoint', '')
                                log_text_parts.append(f"{time_part} 🔧 Tool Call: {tool_name} → {endpoint}")
                                if message:
                                    log_text_parts.append(f"   📝 {message}")
                                    
                            elif log_type == 'api_response':
                                status_code = log_entry.get('status_code', '')
                                api_data = log_entry.get('data', {})
                                
                                if status_code:
                                    log_text_parts.append(f"{time_part} 📡 API Response: HTTP {status_code}")
                                else:
                                    log_text_parts.append(f"{time_part} 📡 API Response: {message}")
                                
                                if api_data:
                                    # Add a condensed version of API data
                                    if isinstance(api_data, dict):
                                        key_info = []
                                        for key, value in list(api_data.items())[:3]:  # Show first 3 keys
                                            if isinstance(value, str) and len(str(value)) > 50:
                                                key_info.append(f"{key}: {str(value)[:50]}...")
                                            else:
                                                key_info.append(f"{key}: {value}")
                                        if len(api_data) > 3:
                                            key_info.append("...")
                                        log_text_parts.append(f"   📊 Data: {{{', '.join(key_info)}}}")
                                    else:
                                        data_preview = str(api_data)[:100] + "..." if len(str(api_data)) > 100 else str(api_data)
                                        log_text_parts.append(f"   📊 Data: {data_preview}")
                                        
                            elif log_type == 'error':
                                log_text_parts.append(f"{time_part} ❌ Error: {message}")
                            else:
                                log_text_parts.append(f"{time_part} ℹ️ {message}")
                        
                        # Join all log parts with line breaks
                        combined_log_text = '\n'.join(log_text_parts)
                        
                        html_content += f'''
                                        <pre class="combined-logs">{combined_log_text}</pre>
                                    </div>
                                </div>
                            </div>
                        </div>'''
                    
                    html_content += '</li>'
                
                html_content += """
                        </ul>
                    </div>
                </div>
                """
    
    html_content += f"""
            </div>
            
            <div class="footer">
                Generated by AI API Test Agent | Enhanced with Agent Logs | Powered by Behave + LangChain
            </div>
        </div>
        
        <script>
            // Add click functionality to scenario headers
            document.querySelectorAll('.scenario-header').forEach(header => {{
                header.addEventListener('click', function() {{
                    const details = this.nextElementSibling;
                    if (details.style.display === 'none') {{
                        details.style.display = 'block';
                    }} else {{
                        details.style.display = 'none';
                    }}
                }});
            }});
            
            // Toggle step logs
            function toggleLogs(button) {{
                const stepItem = button.closest('.step-item');
                const logsDiv = stepItem.querySelector('.step-logs');
                if (logsDiv.style.display === 'none' || logsDiv.style.display === '') {{
                    logsDiv.style.display = 'block';
                    button.textContent = button.textContent.replace('👁️', '👁️‍🗨️');
                }} else {{
                    logsDiv.style.display = 'none';
                    button.textContent = button.textContent.replace('👁️‍🗨️', '👁️');
                }}
            }}
            
            // Initially hide scenario details
            document.querySelectorAll('.scenario-details').forEach(details => {{
                details.style.display = 'none';
            }});
        </script>
    </body>
    </html>
    """
    
    # Write HTML file
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    print(f"✅ Enhanced HTML report with logs generated: {output_file}")
    print(f"📊 Test Summary: {passed_scenarios}/{total_scenarios} scenarios passed ({success_rate:.1f}%)")
    print(f"🔍 Agent logs included for detailed step analysis")
    
    return True

if __name__ == "__main__":
    generate_html_report() 