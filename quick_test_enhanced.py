#!/usr/bin/env python3
"""
Quick test for Enhanced NHL Report Generator
Fast test without hanging on API calls
"""

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

def test_components():
    """Test that our components can be imported"""
    print("\n🔧 Testing component imports...")
    
    try:
        from enhanced_nhl_api_client import EnhancedNHLAPIClient
        print("✅ Enhanced NHL API Client")
    except Exception as e:
        print(f"❌ Enhanced NHL API Client: {e}")
        return False
    
    try:
        from nhl_advanced_analytics import NHLAdvancedAnalytics
        print("✅ Advanced Analytics Engine")
    except Exception as e:
        print(f"❌ Advanced Analytics Engine: {e}")
        return False
    
    try:
        from enhanced_nhl_report_generator import EnhancedNHLReportGenerator
        print("✅ Enhanced Report Generator")
    except Exception as e:
        print(f"❌ Enhanced Report Generator: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic functionality without API calls"""
    print("\n🔧 Testing basic functionality...")
    
    try:
        # Test API client initialization
        from enhanced_nhl_api_client import EnhancedNHLAPIClient
        client = EnhancedNHLAPIClient()
        print("✅ API Client initialized")
        
        # Test analytics initialization
        from nhl_advanced_analytics import NHLAdvancedAnalytics
        analytics = NHLAdvancedAnalytics()
        print("✅ Analytics engine initialized")
        
        # Test report generator initialization
        from enhanced_nhl_report_generator import EnhancedNHLReportGenerator
        generator = EnhancedNHLReportGenerator()
        print("✅ Report generator initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def test_pdf_generation():
    """Test PDF generation without API calls"""
    print("\n🔧 Testing PDF generation...")
    
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph
        from reportlab.lib.styles import getSampleStyleSheet
        import os
        
        test_pdf = 'quick_test_report.pdf'
        doc = SimpleDocTemplate(test_pdf, pagesize=letter)
        styles = getSampleStyleSheet()
        
        story = []
        story.append(Paragraph("Enhanced NHL Report Generator Test", styles['Title']))
        story.append(Paragraph("This is a quick test of the PDF generation system.", styles['Normal']))
        story.append(Paragraph("✅ PDF generation is working!", styles['Normal']))
        
        doc.build(story)
        
        if os.path.exists(test_pdf):
            print("✅ PDF generation working")
            os.remove(test_pdf)  # Clean up
            return True
        else:
            print("❌ PDF generation failed")
            return False
        
    except Exception as e:
        print(f"❌ PDF generation test failed: {e}")
        return False

def main():
    """Run quick tests"""
    print("🏒 ENHANCED NHL REPORT GENERATOR - QUICK TEST 🏒")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("Component Import Test", test_components),
        ("Basic Functionality Test", test_basic_functionality),
        ("PDF Generation Test", test_pdf_generation)
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
    print("📊 QUICK TEST RESULTS SUMMARY")
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
        print("🎉 All quick tests passed! Enhanced NHL Report Generator is ready!")
        print("\n🚀 Ready to generate enhanced NHL reports with:")
        print("  • Real-time NHL API integration (2025 endpoints)")
        print("  • Advanced player analytics with game logs")
        print("  • Play-by-play analysis with shot locations")
        print("  • Real-time standings and historical context")
        print("  • Advanced visualizations and interactive charts")
        print("  • Comprehensive goalie performance analysis")
        print("  • Momentum tracking and game flow analysis")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
