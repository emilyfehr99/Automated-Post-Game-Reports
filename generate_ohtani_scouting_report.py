#!/usr/bin/env python3
"""
Shohei Ohtani Scouting Report Generator
Main script to generate comprehensive scouting report for facing Shohei Ohtani
"""

import os
import sys
from datetime import datetime
from ohtani_scouting_report import OhtaniScoutingReport
from mlb_scouting_report_generator import MLBScoutingReportGenerator

def main():
    """Main function to generate Shohei Ohtani scouting report"""
    print("⚾ Shohei Ohtani Scouting Report Generator ⚾")
    print("=" * 50)
    print("🏟️ Blue Jays vs Dodgers World Series Preparation")
    print("=" * 50)
    
    try:
        # Initialize scouting report generator
        print("🔍 Initializing Ohtani scouting analysis...")
        scout_report = OhtaniScoutingReport()
        
        # Generate comprehensive report
        print("📊 Gathering comprehensive player data...")
        scouting_data = scout_report.create_comprehensive_report(season=2024)
        
        if not scouting_data:
            print("❌ Failed to gather scouting data")
            return
        
        print("✅ Scouting data gathered successfully")
        
        # Generate PDF report
        print("📄 Generating PDF scouting report...")
        pdf_generator = MLBScoutingReportGenerator()
        
        # Create output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"ohtani_scouting_report_{timestamp}.pdf"
        
        # Generate the report
        pdf_generator.generate_report(scouting_data, output_filename)
        
        print(f"✅ Scouting report generated successfully: {output_filename}")
        print(f"📁 File location: {os.path.abspath(output_filename)}")
        
        # Print key insights
        print("\n🎯 KEY SCOUTING INSIGHTS:")
        print("-" * 30)
        
        insights = scouting_data.get('insights', {})
        
        print("\n🏏 HITTING INSIGHTS:")
        for insight in insights.get('hitting_insights', []):
            print(f"  • {insight}")
        
        print("\n⚾ PITCHING INSIGHTS:")
        for insight in insights.get('pitching_insights', []):
            print(f"  • {insight}")
        
        print("\n📋 GAME PLAN RECOMMENDATIONS:")
        for i, recommendation in enumerate(insights.get('game_plan', []), 1):
            print(f"  {i}. {recommendation}")
        
        print(f"\n🏆 Report ready for Blue Jays coaching staff!")
        print("   Use this intelligence to prepare for the World Series matchup.")
        
    except Exception as e:
        print(f"❌ Error generating scouting report: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
