#!/usr/bin/env python3
"""
AJHL Complete Opponent System
Comprehensive system for collecting data from Lloydminster Bobcats and all upcoming opponents
"""

import json
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

# Import all system components
from ajhl_team_config import get_active_teams, DATA_DIRECTORIES
from ajhl_opponent_tracker import AJHLOpponentTracker
from hudl_enhanced_csv_downloader import HudlEnhancedCSVDownloader
from ajhl_monitoring_dashboard import AJHLMonitoringDashboard

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ajhl_opponent_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AJHLCompleteOpponentSystem:
    """Complete system for Lloydminster Bobcats and opponent data collection"""
    
    def __init__(self, username: str, password: str):
        """Initialize the complete opponent system"""
        self.username = username
        self.password = password
        self.opponent_tracker = None
        self.csv_downloader = None
        self.dashboard = None
        
        # System configuration
        self.lloydminster_team_id = "21479"  # Known Hudl team ID
        self.lloydminster_team_name = "Lloydminster Bobcats"
        
        # System status
        self.system_status = {
            'initialized': False,
            'opponents_discovered': 0,
            'opponents_processed': 0,
            'opponents_successful': 0,
            'opponents_failed': 0,
            'last_opponent_analysis': None,
            'system_health': 'unknown'
        }
    
    def initialize_system(self) -> bool:
        """Initialize all system components"""
        logger.info("🚀 Initializing AJHL Complete Opponent System...")
        
        try:
            # Initialize components
            self.opponent_tracker = AJHLOpponentTracker(headless=True)
            self.csv_downloader = HudlEnhancedCSVDownloader(headless=True, user_identifier="opponent_system")
            self.dashboard = AJHLMonitoringDashboard()
            
            # Setup directories
            self._setup_opponent_directories()
            
            self.system_status['initialized'] = True
            logger.info("✅ AJHL Complete Opponent System initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize system: {e}")
            return False
    
    def _setup_opponent_directories(self):
        """Setup directories for opponent data storage"""
        base_path = Path(DATA_DIRECTORIES['base_path'])
        
        # Create opponent-specific directories
        opponent_dirs = [
            'opponent_data',
            'opponent_data/lloydminster_bobcats',
            'opponent_data/upcoming_opponents',
            'opponent_data/opponent_analysis',
            'opponent_data/reports'
        ]
        
        for dir_path in opponent_dirs:
            full_path = base_path / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"📁 Created directory: {full_path}")
    
    def discover_and_download_opponent_data(self, days_ahead: int = 30) -> Dict[str, Any]:
        """Discover upcoming opponents and download their data"""
        logger.info(f"🏒 Starting comprehensive opponent data collection for {self.lloydminster_team_name}...")
        
        if not self.initialize_system():
            return {"error": "Failed to initialize system"}
        
        try:
            # Authenticate with Hudl
            if not self.opponent_tracker.authenticate(self.username, self.password):
                return {"error": "Failed to authenticate opponent tracker"}
            
            if not self.csv_downloader.authenticate(self.username, self.password):
                return {"error": "Failed to authenticate CSV downloader"}
            
            # Get comprehensive opponent data
            opponent_results = self.opponent_tracker.get_comprehensive_opponent_data(
                self.lloydminster_team_name, days_ahead
            )
            
            # Update system status
            self.system_status.update({
                'opponents_discovered': opponent_results['opponents_found'],
                'opponents_processed': opponent_results['opponents_processed'],
                'opponents_successful': opponent_results['opponents_successful'],
                'opponents_failed': opponent_results['opponents_failed'],
                'last_opponent_analysis': datetime.now().isoformat()
            })
            
            # Download Lloydminster Bobcats data as well
            logger.info("📥 Downloading Lloydminster Bobcats data...")
            bobcats_results = self.csv_downloader.download_team_comprehensive_data(
                self.lloydminster_team_id, self.lloydminster_team_name
            )
            
            # Combine results
            comprehensive_results = {
                "analysis_timestamp": datetime.now().isoformat(),
                "team_name": self.lloydminster_team_name,
                "days_ahead": days_ahead,
                "lloydminster_bobcats": bobcats_results,
                "opponent_analysis": opponent_results,
                "system_status": self.system_status,
                "summary": {
                    "total_opponents_found": opponent_results['opponents_found'],
                    "opponents_processed": opponent_results['opponents_processed'],
                    "opponents_successful": opponent_results['opponents_successful'],
                    "opponents_failed": opponent_results['opponents_failed'],
                    "lloydminster_successful": "error" not in bobcats_results,
                    "total_csv_files": (
                        len(bobcats_results.get('downloaded_files', [])) +
                        sum(len(result.get('downloaded_files', [])) 
                            for result in opponent_results.get('download_results', {}).values())
                    )
                }
            }
            
            # Save comprehensive results
            results_file = f"ajhl_complete_opponent_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            results_path = Path(DATA_DIRECTORIES['base_path']) / 'opponent_data' / 'reports' / results_file
            
            with open(results_path, 'w') as f:
                json.dump(comprehensive_results, f, indent=2)
            
            logger.info(f"📄 Comprehensive results saved to: {results_path}")
            logger.info(f"✅ Opponent analysis complete: {opponent_results['opponents_successful']}/{opponent_results['opponents_processed']} opponents successful")
            
            return comprehensive_results
            
        except Exception as e:
            logger.error(f"❌ Error in comprehensive opponent analysis: {e}")
            return {"error": str(e)}
        finally:
            self.cleanup()
    
    def download_lloydminster_data_only(self) -> Dict[str, Any]:
        """Download data for Lloydminster Bobcats only"""
        logger.info(f"📥 Downloading Lloydminster Bobcats data...")
        
        if not self.initialize_system():
            return {"error": "Failed to initialize system"}
        
        try:
            if not self.csv_downloader.authenticate(self.username, self.password):
                return {"error": "Failed to authenticate CSV downloader"}
            
            # Download Lloydminster Bobcats data
            results = self.csv_downloader.download_team_comprehensive_data(
                self.lloydminster_team_id, self.lloydminster_team_name
            )
            
            # Save results
            results_file = f"lloydminster_bobcats_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            results_path = Path(DATA_DIRECTORIES['base_path']) / 'opponent_data' / 'lloydminster_bobcats' / results_file
            
            with open(results_path, 'w') as f:
                json.dump(results, f, indent=2)
            
            logger.info(f"📄 Lloydminster results saved to: {results_path}")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error downloading Lloydminster data: {e}")
            return {"error": str(e)}
        finally:
            self.cleanup()
    
    def get_upcoming_opponents_only(self, days_ahead: int = 30) -> Dict[str, Any]:
        """Get list of upcoming opponents without downloading data"""
        logger.info(f"📅 Getting upcoming opponents for {self.lloydminster_team_name}...")
        
        if not self.initialize_system():
            return {"error": "Failed to initialize system"}
        
        try:
            if not self.opponent_tracker.authenticate(self.username, self.password):
                return {"error": "Failed to authenticate opponent tracker"}
            
            # Get upcoming opponents
            opponents = self.opponent_tracker.get_upcoming_opponents(self.lloydminster_team_name, days_ahead)
            
            # Find Hudl team IDs for opponents
            opponents_with_ids = []
            for opponent_info in opponents:
                hudl_team_id = self.opponent_tracker.find_opponent_hudl_team_id(opponent_info['opponent'])
                opponent_info['hudl_team_id'] = hudl_team_id
                opponent_info['has_hudl_access'] = hudl_team_id is not None
                opponents_with_ids.append(opponent_info)
            
            results = {
                "team_name": self.lloydminster_team_name,
                "analysis_timestamp": datetime.now().isoformat(),
                "days_ahead": days_ahead,
                "total_opponents": len(opponents_with_ids),
                "opponents_with_hudl_ids": len([o for o in opponents_with_ids if o['hudl_team_id']]),
                "upcoming_opponents": opponents_with_ids
            }
            
            # Save results
            results_file = f"upcoming_opponents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            results_path = Path(DATA_DIRECTORIES['base_path']) / 'opponent_data' / 'opponent_analysis' / results_file
            
            with open(results_path, 'w') as f:
                json.dump(results, f, indent=2)
            
            logger.info(f"📄 Opponents list saved to: {results_path}")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error getting upcoming opponents: {e}")
            return {"error": str(e)}
        finally:
            self.cleanup()
    
    def generate_opponent_dashboard(self) -> str:
        """Generate monitoring dashboard for opponent data"""
        logger.info("📊 Generating opponent monitoring dashboard...")
        
        try:
            if not self.dashboard:
                self.dashboard = AJHLMonitoringDashboard()
            
            # Generate standard dashboard
            dashboard_path = self.dashboard.generate_html_dashboard()
            
            # Generate opponent-specific summary
            self._generate_opponent_summary()
            
            logger.info(f"✅ Opponent dashboard generated: {dashboard_path}")
            return dashboard_path
            
        except Exception as e:
            logger.error(f"❌ Error generating opponent dashboard: {e}")
            return None
    
    def _generate_opponent_summary(self):
        """Generate opponent-specific summary report"""
        try:
            # Look for recent opponent analysis files
            analysis_dir = Path(DATA_DIRECTORIES['base_path']) / 'opponent_data' / 'opponent_analysis'
            if not analysis_dir.exists():
                return
            
            # Find most recent analysis file
            analysis_files = list(analysis_dir.glob('upcoming_opponents_*.json'))
            if not analysis_files:
                return
            
            latest_file = max(analysis_files, key=lambda x: x.stat().st_mtime)
            
            with open(latest_file, 'r') as f:
                analysis_data = json.load(f)
            
            # Generate summary
            summary = f"""
AJHL Opponent Analysis Summary
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}

TEAM: {analysis_data['team_name']}
ANALYSIS PERIOD: {analysis_data['days_ahead']} days ahead
TOTAL OPPONENTS: {analysis_data['total_opponents']}
OPPONENTS WITH HUDL ACCESS: {analysis_data['opponents_with_hudl_ids']}

UPCOMING OPPONENTS:
"""
            
            for opponent in analysis_data['upcoming_opponents']:
                hudl_status = "✅" if opponent['has_hudl_access'] else "❌"
                home_status = "🏠" if opponent['home_team'] else "✈️"
                summary += f"{hudl_status} {home_status} {opponent['opponent']} - {opponent['game_date']} ({opponent['days_until_game']} days)\n"
                if opponent['hudl_team_id']:
                    summary += f"    Hudl Team ID: {opponent['hudl_team_id']}\n"
            
            # Save summary
            summary_file = Path(DATA_DIRECTORIES['base_path']) / 'opponent_data' / 'reports' / f'opponent_summary_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
            with open(summary_file, 'w') as f:
                f.write(summary)
            
            logger.info(f"📄 Opponent summary saved to: {summary_file}")
            
        except Exception as e:
            logger.warning(f"⚠️  Error generating opponent summary: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        status = {
            'system_status': self.system_status,
            'timestamp': datetime.now().isoformat(),
            'components': {
                'opponent_tracker': self.opponent_tracker is not None,
                'csv_downloader': self.csv_downloader is not None,
                'dashboard': self.dashboard is not None
            },
            'lloydminster_team': {
                'team_id': self.lloydminster_team_id,
                'team_name': self.lloydminster_team_name
            }
        }
        
        return status
    
    def cleanup(self):
        """Cleanup all system components"""
        logger.info("🧹 Cleaning up opponent system components...")
        
        try:
            if self.opponent_tracker:
                self.opponent_tracker.close()
            if self.csv_downloader:
                self.csv_downloader.close()
            
            logger.info("✅ Opponent system cleanup completed")
        except Exception as e:
            logger.warning(f"⚠️  Error during cleanup: {e}")

def main():
    """Main function for the complete opponent system"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AJHL Complete Opponent System')
    parser.add_argument('--full', action='store_true', help='Run full opponent analysis and data collection')
    parser.add_argument('--lloydminster', action='store_true', help='Download Lloydminster Bobcats data only')
    parser.add_argument('--opponents', action='store_true', help='Get upcoming opponents list only')
    parser.add_argument('--dashboard', action='store_true', help='Generate opponent dashboard')
    parser.add_argument('--status', action='store_true', help='Show system status')
    parser.add_argument('--days', type=int, default=30, help='Days ahead to look for opponents (default: 30)')
    
    args = parser.parse_args()
    
    try:
        from hudl_credentials import HUDL_USERNAME, HUDL_PASSWORD
        system = AJHLCompleteOpponentSystem(HUDL_USERNAME, HUDL_PASSWORD)
    except ImportError:
        print("❌ Please update hudl_credentials.py with your actual credentials")
        return
    
    try:
        if args.full:
            print("🏒 Running full opponent analysis and data collection...")
            results = system.discover_and_download_opponent_data(args.days)
            if 'error' in results:
                print(f"❌ Full analysis failed: {results['error']}")
            else:
                print(f"✅ Full analysis completed:")
                print(f"  Opponents found: {results['summary']['total_opponents_found']}")
                print(f"  Opponents processed: {results['summary']['opponents_processed']}")
                print(f"  Opponents successful: {results['summary']['opponents_successful']}")
                print(f"  Lloydminster successful: {results['summary']['lloydminster_successful']}")
                print(f"  Total CSV files: {results['summary']['total_csv_files']}")
        
        elif args.lloydminster:
            print("📥 Downloading Lloydminster Bobcats data...")
            results = system.download_lloydminster_data_only()
            if 'error' in results:
                print(f"❌ Lloydminster download failed: {results['error']}")
            else:
                print(f"✅ Lloydminster download completed:")
                print(f"  Total downloads: {results['total_downloads']}")
                print(f"  Successful: {results['successful_downloads']}")
                print(f"  Failed: {results['failed_downloads']}")
                print(f"  Files downloaded: {len(results['downloaded_files'])}")
        
        elif args.opponents:
            print("📅 Getting upcoming opponents list...")
            results = system.get_upcoming_opponents_only(args.days)
            if 'error' in results:
                print(f"❌ Opponents list failed: {results['error']}")
            else:
                print(f"✅ Opponents list completed:")
                print(f"  Total opponents: {results['total_opponents']}")
                print(f"  With Hudl IDs: {results['opponents_with_hudl_ids']}")
                print(f"\nUpcoming opponents:")
                for opponent in results['upcoming_opponents']:
                    hudl_status = "✅" if opponent['has_hudl_access'] else "❌"
                    home_status = "🏠" if opponent['home_team'] else "✈️"
                    print(f"  {hudl_status} {home_status} {opponent['opponent']} - {opponent['game_date']} ({opponent['days_until_game']} days)")
        
        elif args.dashboard:
            print("📊 Generating opponent dashboard...")
            dashboard_path = system.generate_opponent_dashboard()
            if dashboard_path:
                print(f"✅ Dashboard generated: {dashboard_path}")
            else:
                print("❌ Dashboard generation failed")
        
        elif args.status:
            print("📊 System Status:")
            status = system.get_system_status()
            print(json.dumps(status, indent=2))
        
        else:
            print("🏒 AJHL Complete Opponent System")
            print("=" * 50)
            print("Available commands:")
            print("  --full        Run full opponent analysis and data collection")
            print("  --lloydminster Download Lloydminster Bobcats data only")
            print("  --opponents   Get upcoming opponents list only")
            print("  --dashboard   Generate opponent dashboard")
            print("  --status      Show system status")
            print("  --days N      Days ahead to look for opponents (default: 30)")
    
    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        system.cleanup()

if __name__ == "__main__":
    main()
