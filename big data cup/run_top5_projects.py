"""Run Top 5 Genius Projects - Big Data Cup 2025."""
import sys
from pathlib import Path
import json
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from models.voronoi_model import VoronoiAnalyzer
from models.entropy_model import EntropyAnalyzer
from models.fourier_model import FourierAnalyzer
from models.passing_network_model import PassingNetworkAnalyzer
from models.changepoint_model import ChangePointAnalyzer

def main():
    """Run all 5 projects and generate results."""
    print("=" * 80)
    print("🧠 TOP 5 GENIUS PROJECTS - BIG DATA CUP 2025")
    print("=" * 80)
    
    # Data directory - try to find it
    possible_dirs = [
        "/Users/emilyfehr8/Desktop/Big_Data_Cup_2025_New_Projects_20251027_125954",
        "/Users/emilyfehr8/Desktop/Big_Data_Cup_2025_NEW_Projects_ONLY_20251027_130155",
        "/Users/emilyfehr8/CascadeProjects/big data cup/Big-Data-Cup-2025-Data",
        "/Users/emilyfehr8/Desktop"
    ]
    
    data_dir = None
    for d in possible_dirs:
        if Path(d).exists():
            # Check if it has Events.csv files (including subdirectories)
            event_files = (list(Path(d).glob("**/*Events.csv")) + 
                          list(Path(d).glob("**/*events.csv")))
            if event_files:
                data_dir = d
                print(f"✅ Found data directory: {d} ({len(event_files)} event files)")
                break
    
    if not data_dir:
        print("❌ Could not find data directory with Events.csv files!")
        return
    
    # Output directory
    output_base = Path("/Users/emilyfehr8/Desktop/top 5")
    output_base.mkdir(parents=True, exist_ok=True)
    
    results_summary = {}
    
    # Project 1: Voronoi Spatial Control
    print("\n" + "=" * 80)
    print("PROJECT 1: Voronoi Spatial Control Index (VSCI)")
    print("=" * 80)
    try:
        voronoi = VoronoiAnalyzer(data_dir)
        voronoi_results = voronoi.run_full_analysis()
        
        voronoi_output = output_base / "voronoi"
        voronoi_output.mkdir(exist_ok=True)
        
        # Ensure results are stored before visualization
        if voronoi_results:
            voronoi.results = voronoi_results
            voronoi.visualize_control(str(voronoi_output))
        
        results_summary['voronoi'] = {
            'insights': voronoi_results.get('insights', {}),
            'status': 'success'
        }
        print("✅ Voronoi Analysis Complete")
    except Exception as e:
        print(f"❌ Voronoi Error: {e}")
        results_summary['voronoi'] = {'status': 'error', 'error': str(e)}
    
    # Project 2: Information Entropy
    print("\n" + "=" * 80)
    print("PROJECT 2: Information Entropy of Play Sequences")
    print("=" * 80)
    try:
        entropy = EntropyAnalyzer(data_dir)
        entropy_results = entropy.run_full_analysis()
        
        entropy_output = output_base / "entropy"
        entropy_output.mkdir(exist_ok=True)
        
        # Ensure results are stored before visualization
        if entropy_results:
            entropy.results = entropy_results
            entropy.visualize_entropy(str(entropy_output))
        
        results_summary['entropy'] = {
            'insights': entropy_results.get('insights', {}),
            'status': 'success'
        }
        print("✅ Entropy Analysis Complete")
    except Exception as e:
        print(f"❌ Entropy Error: {e}")
        results_summary['entropy'] = {'status': 'error', 'error': str(e)}
    
    # Project 3: Fourier Rhythm Analysis
    print("\n" + "=" * 80)
    print("PROJECT 3: Fourier Analysis of Game Rhythm")
    print("=" * 80)
    try:
        fourier = FourierAnalyzer(data_dir)
        fourier_results = fourier.run_full_analysis()
        
        fourier_output = output_base / "fourier"
        fourier_output.mkdir(exist_ok=True)
        
        # Ensure results are stored before visualization
        if fourier_results:
            fourier.results = fourier_results
            fourier.visualize_rhythm(str(fourier_output))
        
        results_summary['fourier'] = {
            'insights': fourier_results.get('insights', {}),
            'status': 'success'
        }
        print("✅ Fourier Analysis Complete")
    except Exception as e:
        print(f"❌ Fourier Error: {e}")
        results_summary['fourier'] = {'status': 'error', 'error': str(e)}
    
    # Project 4: Passing Networks
    print("\n" + "=" * 80)
    print("PROJECT 4: Dynamic Passing Network Centrality")
    print("=" * 80)
    try:
        passing = PassingNetworkAnalyzer(data_dir)
        passing_results = passing.run_full_analysis()
        
        passing_output = output_base / "passing_networks"
        passing_output.mkdir(exist_ok=True)
        
        # Ensure results are stored before visualization
        if passing_results:
            passing.results = passing_results
            passing.visualize_networks(str(passing_output))
        
        results_summary['passing_networks'] = {
            'insights': passing_results.get('insights', {}),
            'status': 'success'
        }
        print("✅ Passing Network Analysis Complete")
    except Exception as e:
        print(f"❌ Passing Network Error: {e}")
        results_summary['passing_networks'] = {'status': 'error', 'error': str(e)}
    
    # Project 5: Change Point Detection
    print("\n" + "=" * 80)
    print("PROJECT 5: Bayesian Change Point Detection")
    print("=" * 80)
    try:
        changepoint = ChangePointAnalyzer(data_dir)
        changepoint_results = changepoint.run_full_analysis()
        
        changepoint_output = output_base / "changepoints"
        changepoint_output.mkdir(exist_ok=True)
        
        # Ensure results are stored before visualization
        if changepoint_results:
            changepoint.results = changepoint_results
            changepoint.visualize_changepoints(str(changepoint_output))
        
        results_summary['changepoints'] = {
            'insights': changepoint_results.get('insights', {}),
            'status': 'success'
        }
        print("✅ Change Point Analysis Complete")
    except Exception as e:
        print(f"❌ Change Point Error: {e}")
        results_summary['changepoints'] = {'status': 'error', 'error': str(e)}
    
    # Save summary
    summary_file = output_base / "results_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(results_summary, f, indent=2, default=str)
    
    # Generate text summary
    summary_text = output_base / "RESULTS_SUMMARY.txt"
    with open(summary_text, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("TOP 5 GENIUS PROJECTS - RESULTS SUMMARY\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        
        for project_name, project_data in results_summary.items():
            f.write(f"\n{project_name.upper().replace('_', ' ')}\n")
            f.write("-" * 80 + "\n")
            
            if project_data.get('status') == 'success':
                insights = project_data.get('insights', {})
                for key, value in insights.items():
                    f.write(f"  {key}: {value}\n")
            else:
                f.write(f"  Status: {project_data.get('status', 'unknown')}\n")
                if 'error' in project_data:
                    f.write(f"  Error: {project_data['error']}\n")
        
        f.write("\n" + "=" * 80 + "\n")
    
    print("\n" + "=" * 80)
    print("✅ ALL PROJECTS COMPLETE!")
    print(f"Results saved to: {output_base}")
    print("=" * 80)

if __name__ == "__main__":
    main()

