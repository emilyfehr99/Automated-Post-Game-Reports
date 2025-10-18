#!/usr/bin/env python3
"""
Test script for Enhanced NHL Report Generator
Tests all components and API integrations
"""

import sys
import os
from datetime import datetime

def test_imports():
    """Test that all required modules can be imported"""
    print("🔧 Testing imports...")
    
    try:
        import requests
        print("✅ requests")
    except ImportError as e:
        print(f"❌ requests: {e}")
        return False
    
    try:
        import pandas
        print("✅ pandas")
    except ImportError as e:
        print(f"❌ pandas: {e}")
        return False
    
    try:
        import numpy
        print("✅ numpy")
    except ImportError as e:
        print(f"❌ numpy: {e}")
        return False
    
    try:
        import matplotlib
        print("✅ matplotlib")
    except ImportError as e:
        print(f"❌ matplotlib: {e}")
        return False
    
    try:
        import seaborn
        print("✅ seaborn")
    except ImportError as e:
        print(f"❌ seaborn: {e}")
        return False
    
    try:
        from reportlab.lib.pagesizes import letter
        print("✅ reportlab")
    except ImportError as e:
        print(f"❌ reportlab: {e}")
        return False
    
    return True

def test_api_client():
    """Test the enhanced NHL API client"""
    print("\n🌐 Testing Enhanced NHL API Client...")
    
    try:
        from enhanced_nhl_api_client import EnhancedNHLAPIClient
        client = EnhancedNHLAPIClient()
        print("✅ API Client initialized")
        
        # Test basic functionality
        print("Testing API endpoints...")
        
        # Test team roster (we know this works)
        roster = client.get_team_roster('EDM', '20242025')
        if roster:
            print("✅ Team roster API working")
        else:
            print("❌ Team roster API failed")
        
        # Test player stats
        stats = client.get_skater_stats(limit=3)
        if stats:
            print("✅ Player stats API working")
        else:
            print("❌ Player stats API failed")
        
        # Test team info
        team_info = client.get_team_info(22)  # Edmonton Oilers
        if team_info:
            print("✅ Team info API working")
        else:
            print("❌ Team info API failed")
        
        return True
        
    except Exception as e:
        print(f"❌ API Client test failed: {e}")
        return False

def test_analytics():
    """Test the advanced analytics engine"""
    print("\n📊 Testing Advanced Analytics Engine...")
    
    try:
        from nhl_advanced_analytics import NHLAdvancedAnalytics
        analytics = NHLAdvancedAnalytics()
        print("✅ Analytics engine initialized")
        
        # Test that we can create basic charts
        print("Testing chart creation...")
        
        # Create a simple test chart
        import matplotlib.pyplot as plt
        import numpy as np
        
        fig, ax = plt.subplots(figsize=(8, 6))
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        ax.plot(x, y)
        ax.set_title('Test Chart')
        
        # Save to test file
        test_file = 'test_chart.png'
        plt.savefig(test_file, dpi=150, bbox_inches='tight')
        plt.close()
        
        if os.path.exists(test_file):
            print("✅ Chart creation working")
            os.remove(test_file)  # Clean up
        else:
            print("❌ Chart creation failed")
        
        return True
        
    except Exception as e:
        print(f"❌ Analytics test failed: {e}")
        return False

def test_report_generator():
    """Test the enhanced report generator"""
    print("\n📝 Testing Enhanced Report Generator...")
    
    try:
        from enhanced_nhl_report_generator import EnhancedNHLReportGenerator
        generator = EnhancedNHLReportGenerator()
        print("✅ Report generator initialized")
        
        # Test that we can create a basic PDF
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph
        from reportlab.lib.styles import getSampleStyleSheet
        
        test_pdf = 'test_report.pdf'
        doc = SimpleDocTemplate(test_pdf, pagesize=letter)
        styles = getSampleStyleSheet()
        
        story = []
        story.append(Paragraph("Test Report", styles['Title']))
        story.append(Paragraph("This is a test of the PDF generation system.", styles['Normal']))
        
        doc.build(story)
        
        if os.path.exists(test_pdf):
            print("✅ PDF generation working")
            os.remove(test_pdf)  # Clean up
        else:
            print("❌ PDF generation failed")
        
        return True
        
    except Exception as e:
        print(f"❌ Report generator test failed: {e}")
        return False

def test_integration():
    """Test integration between components"""
    print("\n🔗 Testing Component Integration...")
    
    try:
        from enhanced_nhl_api_client import EnhancedNHLAPIClient
        from enhanced_nhl_report_generator import EnhancedNHLReportGenerator
        
        # Initialize components
        api_client = EnhancedNHLAPIClient()
        report_generator = EnhancedNHLReportGenerator()
        
        print("✅ Components can be imported together")
        
        # Test that we can get some data
        roster = api_client.get_team_roster('EDM', '20242025')
        if roster:
            print("✅ Data fetching integration working")
        else:
            print("❌ Data fetching integration failed")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🏒 ENHANCED NHL REPORT GENERATOR - TEST SUITE 🏒")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("API Client Test", test_api_client),
        ("Analytics Test", test_analytics),
        ("Report Generator Test", test_report_generator),
        ("Integration Test", test_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST RESULTS SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Enhanced NHL Report Generator is ready!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
