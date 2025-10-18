#!/usr/bin/env python3
"""
Demo script for Automated NHL Post-Game Reports

This script demonstrates the capabilities of the repository by generating
sample reports and showing the different report types available.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def demo_comprehensive_report():
    """Demonstrate comprehensive report generation."""
    print("🏒 DEMO: Comprehensive Report Generation")
    print("=" * 50)
    
    try:
        from comprehensive_report import create_comprehensive_report
        print("✅ Comprehensive report module imported successfully")
        
        # Generate a sample report
        print("🎯 Generating sample comprehensive report...")
        result = create_comprehensive_report("2024030416")
        print(f"✅ Report generated: {result}")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

def demo_quick_report():
    """Demonstrate quick report generation."""
    print("\n🏒 DEMO: Quick Report Generation")
    print("=" * 50)
    
    try:
        from quick_report import create_quick_report
        print("✅ Quick report module imported successfully")
        
        # Generate a sample report
        print("🎯 Generating sample quick report...")
        result = create_quick_report("2024030416")
        print(f"✅ Report generated: {result}")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

def demo_main_script():
    """Demonstrate the main script functionality."""
    print("\n🏒 DEMO: Main Script Functionality")
    print("=" * 50)
    
    try:
        import subprocess
        import sys
        
        # Test the main script
        print("🎯 Testing main script with --help...")
        result = subprocess.run([sys.executable, "main.py", "--help"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Main script working correctly")
            print("📖 Help output:")
            print(result.stdout)
        else:
            print(f"❌ Main script error: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Run all demos."""
    print("🏒 AUTOMATED NHL POST-GAME REPORTS - DEMO")
    print("=" * 60)
    print("This demo showcases the repository's capabilities")
    print("and demonstrates different report generation methods.\n")
    
    # Run demos
    demo_comprehensive_report()
    demo_quick_report()
    demo_main_script()
    
    print("\n🎉 DEMO COMPLETE!")
    print("=" * 60)
    print("To use the repository:")
    print("1. Install dependencies: pip install -r src/requirements.txt")
    print("2. Generate reports: python main.py [game_id] [report_type]")
    print("3. Check examples/ folder for sample outputs")
    print("\nFor more information, see README.md")

if __name__ == "__main__":
    main()
