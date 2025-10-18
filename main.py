#!/usr/bin/env python3
"""
Main entry point for Automated NHL Post-Game Reports

Usage:
    python main.py [game_id] [report_type]

Examples:
    python main.py 2024030416 comprehensive
    python main.py 2025020002 quick
    python main.py --help
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        description="Generate NHL post-game reports with professional analytics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py 2024030416 comprehensive  # Generate comprehensive report
  python main.py 2025020002 quick          # Generate quick report
  python main.py --list-types              # List available report types
        """
    )
    
    parser.add_argument(
        "game_id",
        nargs="?",
        help="NHL game ID (e.g., 2024030416)"
    )
    
    parser.add_argument(
        "report_type",
        nargs="?",
        choices=["quick", "comprehensive", "enhanced"],
        default="comprehensive",
        help="Type of report to generate (default: comprehensive)"
    )
    
    parser.add_argument(
        "--list-types",
        action="store_true",
        help="List available report types and exit"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )
    
    args = parser.parse_args()
    
    if args.list_types:
        print("Available Report Types:")
        print("  quick          - Basic shot analysis and stats")
        print("  comprehensive  - Full analytics with play-by-play (default)")
        print("  enhanced       - Professional formatting with coaching insights")
        return
    
    if not args.game_id:
        parser.print_help()
        return
    
    try:
        if args.report_type == "quick":
            from quick_report import create_quick_report
            print(f"🏒 Generating quick report for game {args.game_id}...")
            result = create_quick_report(args.game_id)
            print(f"✅ Quick report generated: {result}")
            
        elif args.report_type == "comprehensive":
            from comprehensive_report import create_comprehensive_report
            print(f"🏒 Generating comprehensive report for game {args.game_id}...")
            result = create_comprehensive_report(args.game_id)
            print(f"✅ Comprehensive report generated: {result}")
            
        elif args.report_type == "enhanced":
            try:
                from enhanced_comprehensive_report import create_enhanced_report
                print(f"🏒 Generating enhanced report for game {args.game_id}...")
                result = create_enhanced_report(args.game_id)
                print(f"✅ Enhanced report generated: {result}")
            except ImportError:
                print("⚠️ Enhanced report type not available, falling back to comprehensive...")
                from comprehensive_report import create_comprehensive_report
                result = create_comprehensive_report(args.game_id)
                print(f"✅ Comprehensive report generated: {result}")
        
        print(f"\n🎉 Report successfully generated for game {args.game_id}!")
        print(f"📄 Report type: {args.report_type}")
        print(f"📁 File: {result}")
        
    except ImportError as e:
        print(f"❌ Error importing required modules: {e}")
        print("💡 Make sure all dependencies are installed: pip install -r src/requirements.txt")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
