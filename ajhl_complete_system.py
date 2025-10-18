#!/usr/bin/env python3
"""
AJHL Complete System Integration
Comprehensive system for daily AJHL data collection with real Hudl Instat structure
"""

import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Import all AJHL system components
from ajhl_team_config import get_active_teams, get_teams_with_hudl_ids, DATA_DIRECTORIES
from ajhl_real_hudl_manager import AJHLRealHudlManager
from ajhl_daily_scheduler import AJHLDailyScheduler
from ajhl_monitoring_dashboard import AJHLMonitoringDashboard
from ajhl_team_id_discovery import AJHLTeamIDDiscovery

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ajhl_complete_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AJHLCompleteSystem:
    """Complete AJHL data collection system with all features"""
    
    def __init__(self, username: str, password: str):
        """Initialize the complete AJHL system"""
        self.username = username
        self.password = password
        self.manager = None
        self.scheduler = None
        self.dashboard = None
        self.discovery = None
        
        # System status
        self.system_status = {
            'initialized': False,
            'teams_configured': 0,
            'teams_with_hudl_ids': 0,
            'last_discovery_run': None,
            'last_data_collection': None,
            'system_health': 'unknown'
        }
    
    def initialize_system(self) -> bool:
        """Initialize all system components"""
        logger.info("🚀 Initializing AJHL Complete System...")
        
        try:
            # Initialize components
            self.manager = AJHLRealHudlManager(self.username, self.password)
            self.scheduler = AJHLDailyScheduler(self.username, self.password)
            self.dashboard = AJHLMonitoringDashboard()
            self.discovery = AJHLTeamIDDiscovery(headless=True)
            
            # Check system status
            self._update_system_status()
            
            self.system_status['initialized'] = True
            logger.info("✅ AJHL Complete System initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize system: {e}")
            return False
    
    def _update_system_status(self):
        """Update system status information"""
        try:
            active_teams = get_active_teams()
            teams_with_ids = get_teams_with_hudl_ids()
            
            self.system_status.update({
                'teams_configured': len(active_teams),
                'teams_with_hudl_ids': len(teams_with_ids),
                'system_health': 'healthy' if len(teams_with_ids) > 0 else 'needs_discovery'
            })
        except Exception as e:
            logger.warning(f"⚠️  Error updating system status: {e}")
            self.system_status['system_health'] = 'error'
    
    def discover_team_ids(self) -> Dict[str, Any]:
        """Discover Hudl team IDs for all AJHL teams"""
        logger.info("🔍 Starting team ID discovery...")
        
        try:
            if not self.discovery.authenticate(self.username, self.password):
                return {"error": "Authentication failed"}
            
            results = self.discovery.discover_all_team_ids()
            self.system_status['last_discovery_run'] = datetime.now().isoformat()
            self._update_system_status()
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Team ID discovery failed: {e}")
            return {"error": str(e)}
        finally:
            if self.discovery:
                self.discovery.close()
    
    def run_daily_collection(self) -> Dict[str, Any]:
        """Run daily data collection for all teams"""
        logger.info("📥 Starting daily data collection...")
        
        try:
            if not self.manager:
                self.manager = AJHLRealHudlManager(self.username, self.password)
            
            results = self.manager.process_all_teams_daily()
            self.system_status['last_data_collection'] = datetime.now().isoformat()
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Daily collection failed: {e}")
            return {"error": str(e)}
    
    def start_scheduler(self):
        """Start the daily scheduler"""
        logger.info("⏰ Starting daily scheduler...")
        
        try:
            if not self.scheduler:
                self.scheduler = AJHLDailyScheduler(self.username, self.password)
            
            self.scheduler.run_scheduler()
            
        except Exception as e:
            logger.error(f"❌ Scheduler failed: {e}")
    
    def generate_dashboard(self) -> str:
        """Generate monitoring dashboard"""
        logger.info("📊 Generating monitoring dashboard...")
        
        try:
            if not self.dashboard:
                self.dashboard = AJHLMonitoringDashboard()
            
            dashboard_path = self.dashboard.generate_html_dashboard()
            logger.info(f"✅ Dashboard generated: {dashboard_path}")
            return dashboard_path
            
        except Exception as e:
            logger.error(f"❌ Dashboard generation failed: {e}")
            return None
    
    def generate_summary_report(self) -> str:
        """Generate summary report"""
        logger.info("📄 Generating summary report...")
        
        try:
            if not self.dashboard:
                self.dashboard = AJHLMonitoringDashboard()
            
            report_path = self.dashboard.generate_summary_report()
            logger.info(f"✅ Summary report generated: {report_path}")
            return report_path
            
        except Exception as e:
            logger.error(f"❌ Summary report generation failed: {e}")
            return None
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        self._update_system_status()
        
        status = {
            'system_status': self.system_status,
            'timestamp': datetime.now().isoformat(),
            'components': {
                'manager': self.manager is not None,
                'scheduler': self.scheduler is not None,
                'dashboard': self.dashboard is not None,
                'discovery': self.discovery is not None
            }
        }
        
        # Add team information
        try:
            active_teams = get_active_teams()
            teams_with_ids = get_teams_with_hudl_ids()
            
            status['teams'] = {
                'total_teams': len(active_teams),
                'teams_with_hudl_ids': len(teams_with_ids),
                'teams_needing_discovery': len(active_teams) - len(teams_with_ids),
                'team_list': [
                    {
                        'team_id': team_id,
                        'team_name': team_data['team_name'],
                        'city': team_data['city'],
                        'division': team_data['division'],
                        'has_hudl_id': bool(team_data['hudl_team_id']),
                        'hudl_team_id': team_data['hudl_team_id']
                    }
                    for team_id, team_data in active_teams.items()
                ]
            }
        except Exception as e:
            status['teams'] = {'error': str(e)}
        
        return status
    
    def run_full_setup(self) -> bool:
        """Run complete system setup and initial data collection"""
        logger.info("🔧 Running full system setup...")
        
        try:
            # Initialize system
            if not self.initialize_system():
                return False
            
            # Discover team IDs if needed
            teams_with_ids = get_teams_with_hudl_ids()
            if len(teams_with_ids) == 0:
                logger.info("🔍 No teams have Hudl IDs, running discovery...")
                discovery_results = self.discover_team_ids()
                if 'error' in discovery_results:
                    logger.error(f"❌ Team discovery failed: {discovery_results['error']}")
                    return False
            
            # Run initial data collection
            logger.info("📥 Running initial data collection...")
            collection_results = self.run_daily_collection()
            if 'error' in collection_results:
                logger.warning(f"⚠️  Initial collection had issues: {collection_results['error']}")
            
            # Generate initial dashboard
            logger.info("📊 Generating initial dashboard...")
            self.generate_dashboard()
            
            logger.info("✅ Full system setup completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Full setup failed: {e}")
            return False
    
    def cleanup(self):
        """Cleanup all system components"""
        logger.info("🧹 Cleaning up system components...")
        
        try:
            if self.manager:
                self.manager.close()
            if self.scheduler:
                # Scheduler cleanup is handled by signal handlers
                pass
            if self.discovery:
                self.discovery.close()
            
            logger.info("✅ System cleanup completed")
        except Exception as e:
            logger.warning(f"⚠️  Error during cleanup: {e}")

def main():
    """Main function for the complete AJHL system"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AJHL Complete System')
    parser.add_argument('--setup', action='store_true', help='Run full system setup')
    parser.add_argument('--discover', action='store_true', help='Discover team IDs')
    parser.add_argument('--collect', action='store_true', help='Run data collection')
    parser.add_argument('--dashboard', action='store_true', help='Generate dashboard')
    parser.add_argument('--status', action='store_true', help='Show system status')
    parser.add_argument('--scheduler', action='store_true', help='Start scheduler')
    parser.add_argument('--test', action='store_true', help='Run test collection')
    
    args = parser.parse_args()
    
    try:
        from hudl_credentials import HUDL_USERNAME, HUDL_PASSWORD
        system = AJHLCompleteSystem(HUDL_USERNAME, HUDL_PASSWORD)
    except ImportError:
        print("❌ Please update hudl_credentials.py with your actual credentials")
        return
    
    try:
        if args.setup:
            print("🔧 Running full system setup...")
            success = system.run_full_setup()
            print(f"{'✅' if success else '❌'} Setup {'completed successfully' if success else 'failed'}")
        
        elif args.discover:
            print("🔍 Discovering team IDs...")
            results = system.discover_team_ids()
            if 'error' in results:
                print(f"❌ Discovery failed: {results['error']}")
            else:
                print(f"✅ Discovery completed: {results['teams_found']}/{results['teams_processed']} teams found")
        
        elif args.collect:
            print("📥 Running data collection...")
            results = system.run_daily_collection()
            if 'error' in results:
                print(f"❌ Collection failed: {results['error']}")
            else:
                print(f"✅ Collection completed: {results['successful_teams']}/{results['total_teams']} teams successful")
        
        elif args.dashboard:
            print("📊 Generating dashboard...")
            dashboard_path = system.generate_dashboard()
            if dashboard_path:
                print(f"✅ Dashboard generated: {dashboard_path}")
            else:
                print("❌ Dashboard generation failed")
        
        elif args.status:
            print("📊 System Status:")
            status = system.get_system_status()
            print(json.dumps(status, indent=2))
        
        elif args.scheduler:
            print("⏰ Starting scheduler...")
            system.start_scheduler()
        
        elif args.test:
            print("🧪 Running test collection...")
            if not system.initialize_system():
                print("❌ System initialization failed")
                return
            
            # Test with just one team that has a Hudl ID
            teams_with_ids = get_teams_with_hudl_ids()
            if teams_with_ids:
                test_team = list(teams_with_ids.keys())[0]
                print(f"🎯 Testing with team: {teams_with_ids[test_team]['team_name']}")
                
                if not system.manager:
                    system.manager = AJHLRealHudlManager(system.username, system.password)
                
                result = system.manager.download_team_comprehensive_data(test_team)
                if result.get('success'):
                    print(f"✅ Test successful: {result['total_files']} files downloaded")
                else:
                    print(f"❌ Test failed: {result.get('error', 'Unknown error')}")
            else:
                print("❌ No teams with Hudl IDs available for testing")
        
        else:
            print("🏒 AJHL Complete System")
            print("=" * 40)
            print("Available commands:")
            print("  --setup     Run full system setup")
            print("  --discover  Discover team IDs")
            print("  --collect   Run data collection")
            print("  --dashboard Generate dashboard")
            print("  --status    Show system status")
            print("  --scheduler Start scheduler")
            print("  --test      Run test collection")
    
    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        system.cleanup()

if __name__ == "__main__":
    main()
