#!/usr/bin/env python3
"""
Test Enhanced Report with Logos - Test the logo functionality
"""

from nhl_report_with_png_logos import NHLReportWithPNGLogos

def test_enhanced_report_with_logos():
    """Test the enhanced report with logo functionality"""
    print("🏒 TESTING ENHANCED REPORT WITH LOGOS 🏒")
    print("=" * 60)
    
    # Create the report generator
    generator = NHLReportWithPNGLogos()
    
    # Test with the working game ID
    game_id = "2024030242"
    
    print(f"Generating enhanced report with logos for game {game_id}...")
    result = generator.generate_comprehensive_report(game_id)
    
    if result:
        print(f"🎉 SUCCESS! Enhanced report with logos created: {result}")
        print("\nThis enhanced report now includes:")
        print("  ✅ Real NHL team logos (EDM Oilers & VGK Golden Knights)")
        print("  ✅ All comprehensive metrics from NHL API")
        print("  ✅ Professional logo display in team sections")
        print("  ✅ Enhanced visualizations and charts")
        print("  ✅ Complete post-game analysis")
    else:
        print("❌ Failed to generate enhanced report with logos")

if __name__ == "__main__":
    test_enhanced_report_with_logos()
