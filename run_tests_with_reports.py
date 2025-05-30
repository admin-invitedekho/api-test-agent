#!/usr/bin/env python3
"""
Enhanced test runner with automatic HTML report generation.
Runs tests and generates beautiful HTML reports.
"""

import subprocess
import sys
import os
from datetime import datetime
from generate_html_report import generate_html_report

def run_tests_with_reports():
    """Run all tests and generate comprehensive reports"""
    
    print("🚀 Running AI API Tests with Report Generation...")
    print("=" * 60)
    
    # Step 1: Run tests with JSON output
    print("📊 Step 1: Running tests and generating JSON report...")
    try:
        result = subprocess.run([
            'behave', 
            'features/invitedekho_login_tests.feature',
            '--format', 'json.pretty',
            '--outfile', 'test_results_pretty.json',
            '--no-capture'
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Tests completed successfully!")
        else:
            print("⚠️ Some tests may have failed, but JSON report generated")
            
    except subprocess.TimeoutExpired:
        print("❌ Tests timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False
    
    # Step 2: Generate JUnit XML for CI/CD compatibility
    print("\n📋 Step 2: Generating JUnit XML report...")
    try:
        os.makedirs('reports', exist_ok=True)
        subprocess.run([
            'behave', 
            'features/invitedekho_login_tests.feature',
            '--junit',
            '--junit-directory', 'reports',
            '--no-capture',
            '-q'
        ], capture_output=True, timeout=120)
        print("✅ JUnit XML report generated in reports/ directory")
    except Exception as e:
        print(f"⚠️ JUnit report generation failed: {e}")
    
    # Step 3: Generate beautiful HTML report
    print("\n🌐 Step 3: Generating HTML report...")
    try:
        if generate_html_report():
            print("✅ Beautiful HTML report generated!")
        else:
            print("❌ HTML report generation failed")
            return False
    except Exception as e:
        print(f"❌ Error generating HTML report: {e}")
        return False
    
    # Step 4: Display summary and file locations
    print("\n" + "=" * 60)
    print("🎉 REPORT GENERATION COMPLETE!")
    print("=" * 60)
    
    print("\n📁 Generated Reports:")
    print("   📊 JSON Report:     test_results_pretty.json")
    print("   🌐 HTML Report:     test_report.html")
    print("   📋 JUnit XML:       reports/TESTS-invitedekho_login_tests.xml")
    
    print("\n🌐 To view the HTML report:")
    print("   • Open test_report.html in your browser")
    print("   • Or run: open test_report.html")
    
    print("\n💡 Report Features:")
    print("   ✅ Interactive HTML dashboard")
    print("   ✅ Click-to-expand scenario details")
    print("   ✅ Beautiful statistics and charts")
    print("   ✅ Mobile-responsive design")
    print("   ✅ CI/CD compatible XML format")
    
    return True

if __name__ == "__main__":
    success = run_tests_with_reports()
    if success:
        # Try to open the HTML report automatically
        try:
            subprocess.run(['open', 'test_report.html'], check=False)
            print("\n🚀 HTML report opened in your browser!")
        except:
            print("\n📖 Please open test_report.html manually to view the report")
    
    sys.exit(0 if success else 1) 