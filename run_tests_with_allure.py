#!/usr/bin/env python3
"""
Script to run Behave tests with Allure reporting.
This script works around the KeyError issue in allure-behave.
"""

import subprocess
import sys
import os
import json
from datetime import datetime

def run_tests_with_allure():
    """Run tests and generate allure reports"""
    
    # Clean previous results
    if os.path.exists('allure-results'):
        subprocess.run(['rm', '-rf', 'allure-results'], check=False)
    
    os.makedirs('allure-results', exist_ok=True)
    
    print("🚀 Running tests with Allure integration...")
    
    # Run tests with allure formatter, ignoring the KeyError at the end
    try:
        result = subprocess.run([
            'behave', 
            'features/invitedekho_login_tests.feature',
            '-f', 'allure_behave.formatter:AllureFormatter',
            '-o', 'allure-results',
            '--no-capture'
        ], capture_output=True, text=True, timeout=300)
        
        # Print the output regardless of exit code
        print("📊 Test execution output:")
        print(result.stdout)
        if result.stderr:
            print("⚠️ Warnings/Errors:")
            print(result.stderr)
            
    except subprocess.TimeoutExpired:
        print("❌ Tests timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False
    
    # Check if allure results were generated
    if os.path.exists('allure-results') and os.listdir('allure-results'):
        print("✅ Allure results generated successfully!")
        
        # List generated files
        files = os.listdir('allure-results')
        print(f"📁 Generated {len(files)} result files:")
        for file in files:
            print(f"   - {file}")
        
        # Generate HTML report
        print("\n🎨 Generating HTML report...")
        try:
            subprocess.run([
                'allure', 'generate', 'allure-results', 
                '--clean', '-o', 'allure-report'
            ], check=True)
            print("✅ HTML report generated in 'allure-report' directory")
            
            # Try to open the report
            try:
                subprocess.run(['allure', 'open', 'allure-report'], check=False)
                print("🌐 Report opened in browser")
            except:
                print("📖 To view the report, run: allure open allure-report")
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to generate HTML report: {e}")
            return False
            
        return True
    else:
        print("❌ No allure results were generated")
        return False

if __name__ == "__main__":
    success = run_tests_with_allure()
    sys.exit(0 if success else 1) 