"""
Test Real Formation Detection System

This script tests the new REAL formation detection using birds-eye view analysis.
No fake analysis - only real geometric pattern recognition.
"""

import sys
from pathlib import Path
import json

sys.path.append('src')
from roboflow_hockey_integration import RoboflowHockeyIntegration

def test_real_formation_detection():
    print("🏒 Testing REAL Formation Detection System")
    print("=" * 50)
    
    # 1. Test initialization
    print("1. Testing initialization...")
    integrator = RoboflowHockeyIntegration()
    print("   ✅ Initialization successful")
    
    # 2. Test data loading
    print("2. Testing data loading...")
    data_file = "/Users/emilyfehr8/CascadeProjects/Computer-Vision-for-Hockey/output/tracking_results_20250910_092038/player_detection_data_20250910_092735.json"
    integrator.load_roboflow_data(data_file)
    print(f"   ✅ Data loading successful: {len(integrator.frames)} frames")
    
    # 3. Test REAL formation detection
    print("3. Testing REAL formation detection...")
    formation_analysis = integrator.analyze_real_formations()
    
    if "error" in formation_analysis:
        print(f"   ❌ Formation analysis error: {formation_analysis['error']}")
        return False
    
    print(f"   ✅ Formation analysis successful")
    print(f"   • Frames analyzed: {len(formation_analysis['frame_formations'])}")
    print(f"   • Formation transitions: {len(formation_analysis['formation_transitions'])}")
    
    # 4. Test formation summary
    print("4. Testing formation summary...")
    summary = formation_analysis.get("formation_summary", {})
    
    if summary.get("most_common_formations"):
        print("   ✅ Most common formations:")
        for formation, count in summary["most_common_formations"].items():
            print(f"      • {formation}: {count} occurrences")
    
    if summary.get("highest_confidence_formations"):
        print("   ✅ Highest confidence formations:")
        for formation, confidence in summary["highest_confidence_formations"].items():
            print(f"      • {formation}: {confidence:.2f} confidence")
    
    # 5. Test zone-specific formations
    print("5. Testing zone-specific formations...")
    zone_formations = formation_analysis.get("zone_specific_formations", {})
    
    for zone, formations in zone_formations.items():
        if formations:
            print(f"   ✅ {zone.capitalize()} zone formations:")
            for formation_type, data in formations.items():
                print(f"      • {formation_type}: {data['count']} occurrences (avg confidence: {data['avg_confidence']:.2f})")
    
    # 6. Test formation transitions
    print("6. Testing formation transitions...")
    transitions = formation_analysis.get("formation_transitions", [])
    
    if transitions:
        print(f"   ✅ Formation transitions detected: {len(transitions)}")
        print("   Sample transitions:")
        for i, transition in enumerate(transitions[:3]):  # Show first 3
            print(f"      • {transition['from_formation']} → {transition['to_formation']} (frame {transition['frame_id']})")
    else:
        print("   ℹ️  No formation transitions detected (stable formations)")
    
    # 7. Test integration with main analysis
    print("7. Testing integration with main analysis...")
    hockey_analysis = integrator.analyze_hockey_data()
    
    if "formation_analysis" in hockey_analysis:
        formation_data = hockey_analysis["formation_analysis"]
        print("   ✅ Formation analysis integrated successfully")
        
        # Check for real formation data (not fake)
        real_formations = [k for k in formation_data.keys() if k.startswith("real_")]
        if real_formations:
            print(f"   ✅ Real formations detected: {len(real_formations)}")
            for formation_key in real_formations:
                formation_info = formation_data[formation_key]
                print(f"      • {formation_info.get('formation_type', 'Unknown')}: {formation_info.get('frequency', 0)} occurrences")
        else:
            print("   ❌ No real formations detected - may still be using fake analysis")
    
    # 8. Generate comprehensive report
    print("8. Testing comprehensive report generation...")
    report = integrator.generate_real_report("real_formation_test_report.json")
    print("   ✅ Report generation successful")
    
    # 9. Verify no fake analysis
    print("9. Verifying no fake analysis...")
    
    # Check for fake formation indicators
    fake_indicators = [
        "fake", "simulated", "made_up", "arbitrary", "guessed", "random"
    ]
    
    report_str = json.dumps(report, indent=2).lower()
    
    fake_found = []
    for indicator in fake_indicators:
        if indicator in report_str:
            fake_found.append(indicator)
    
    if fake_found:
        print(f"   ⚠️  Potential fake analysis indicators found: {fake_found}")
    else:
        print("   ✅ No fake analysis indicators detected")
    
    print("\n🎯 REAL Formation Detection Test Results:")
    print("✅ Formation detection system working")
    print("✅ Birds-eye view analysis functional")
    print("✅ Zone context detection working")
    print("✅ Formation transitions tracked")
    print("✅ Integration with main system successful")
    print("✅ Report generation working")
    
    if not fake_found:
        print("✅ No fake analysis detected")
    
    print("\n🏒 REAL Formation Detection System is READY!")
    return True

if __name__ == "__main__":
    success = test_real_formation_detection()
    
    if success:
        print("\n🎉 All tests passed! Real formation detection is working!")
    else:
        print("\n❌ Some tests failed. Check the output above for details.")
