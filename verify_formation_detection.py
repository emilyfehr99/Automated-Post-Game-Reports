"""
Verify Formation Detection - Honest Analysis

Let's see what's really happening with formation detection.
"""

import sys
sys.path.append('src')
from roboflow_hockey_integration import RoboflowHockeyIntegration

def verify_formation_detection():
    print("🔍 HONEST Formation Detection Verification")
    print("=" * 50)
    
    # Load real data
    integrator = RoboflowHockeyIntegration()
    data_file = '/Users/emilyfehr8/CascadeProjects/Computer-Vision-for-Hockey/output/tracking_results_20250910_092038/player_detection_data_20250910_092735.json'
    integrator.load_roboflow_data(data_file)
    
    print(f"Loaded {len(integrator.frames)} frames")
    
    # Analyze formations
    formation_analysis = integrator.analyze_real_formations()
    
    print(f"\nFormation Analysis Results:")
    print(f"Total frames: {len(formation_analysis['frame_formations'])}")
    
    # Look at first few formation detections
    for i, frame_formation in enumerate(formation_analysis['frame_formations'][:5]):
        print(f"\nFrame {frame_formation['frame_id']}:")
        print(f"  Formation: {frame_formation['formation_type']}")
        print(f"  Confidence: {frame_formation['confidence']:.2f}")
        print(f"  Zone: {frame_formation['zone_context']}")
        print(f"  Player roles: {frame_formation['player_roles']}")
        
        # Check geometric patterns
        patterns = frame_formation.get('geometric_patterns', {})
        print(f"  Geometric patterns: {patterns}")
    
    # Check why formations are mostly Unknown
    unknown_count = sum(1 for f in formation_analysis['frame_formations'] if f['formation_type'] == 'Unknown')
    known_count = sum(1 for f in formation_analysis['frame_formations'] if f['formation_type'] != 'Unknown')
    
    print(f"\nFormation Summary:")
    print(f"Unknown formations: {unknown_count}")
    print(f"Known formations: {known_count}")
    print(f"Unknown percentage: {unknown_count/(unknown_count+known_count)*100:.1f}%")
    
    # Look at a specific "Unknown" formation to understand why
    unknown_frames = [f for f in formation_analysis['frame_formations'] if f['formation_type'] == 'Unknown']
    if unknown_frames:
        print(f"\nAnalyzing Unknown Formation (Frame {unknown_frames[0]['frame_id']}):")
        unknown_frame = unknown_frames[0]
        patterns = unknown_frame.get('geometric_patterns', {})
        print(f"  Confidence: {unknown_frame['confidence']:.2f}")
        print(f"  Zone: {unknown_frame['zone_context']}")
        print(f"  Geometric patterns: {patterns}")
        print(f"  Formation shape: {unknown_frame['formation_shape']}")
    
    # Look at a known formation
    known_frames = [f for f in formation_analysis['frame_formations'] if f['formation_type'] != 'Unknown']
    if known_frames:
        print(f"\nAnalyzing Known Formation (Frame {known_frames[0]['frame_id']}):")
        known_frame = known_frames[0]
        patterns = known_frame.get('geometric_patterns', {})
        print(f"  Formation: {known_frame['formation_type']}")
        print(f"  Confidence: {known_frame['confidence']:.2f}")
        print(f"  Zone: {known_frame['zone_context']}")
        print(f"  Geometric patterns: {patterns}")
        print(f"  Formation shape: {known_frame['formation_shape']}")
    
    # Check the formation matching logic
    print(f"\nFormation Matching Analysis:")
    print("The system is detecting mostly 'Unknown' formations because:")
    print("1. The geometric patterns don't match the thresholds for known formations")
    print("2. The zone context may not be appropriate for the detected patterns")
    print("3. The formation detection thresholds may be too strict")
    
    return formation_analysis

if __name__ == "__main__":
    verify_formation_detection()
