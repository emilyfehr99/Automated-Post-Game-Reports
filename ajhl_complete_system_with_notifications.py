#!/usr/bin/env python3
"""
AJHL Complete System with Notifications
Comprehensive system for data collection and notifications
"""

import json
import time
import logging
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

# Import all system components
from ajhl_complete_opponent_system import AJHLCompleteOpponentSystem
from ajhl_notification_system import AJHLNotificationSystem
from ajhl_monitoring_dashboard import AJHLMonitoringDashboard

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ajhl_complete_system_with_notifications.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AJHLCompleteSystemWithNotifications:
    """Complete AJHL system with data collection and notifications"""
    
    def __init__(self, username: str, password: str):
        """Initialize the complete system with notifications"""
        self.username = username
        self.password = password
        self.opponent_system = None
        self.notification_system = None
        self.dashboard = None
        
        # System status
        self.system_status = {
            'initialized': False,
            'monitoring_active': False,
            'last_data_collection': None,
            'last_notification_check': None,
            'total_notifications_sent': 0,
            'system_health': 'unknown'
        }
        
        # Monitoring thread
        self.monitoring_thread = None
        self.stop_monitoring = False
    
    def initialize_system(self) -> bool:
        """Initialize all system components"""
        logger.info("🚀 Initializing AJHL Complete System with Notifications...")
        
        try:
            # Initialize components
            self.opponent_system = AJHLCompleteOpponentSystem(self.username, self.password)
            self.notification_system = AJHLNotificationSystem()
            self.dashboard = AJHLMonitoringDashboard()
            
            self.system_status['initialized'] = True
            logger.info("✅ AJHL Complete System with Notifications initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize system: {e}")
            return False
    
    def run_full_analysis_with_notifications(self, days_ahead: int = 30) -> Dict[str, Any]:
        """Run full opponent analysis and send notifications for new data"""
        logger.info("🏒 Running full analysis with notifications...")
        
        if not self.initialize_system():
            return {"error": "Failed to initialize system"}
        
        try:
            # Run full opponent analysis
            analysis_results = self.opponent_system.discover_and_download_opponent_data(days_ahead)
            
            if 'error' in analysis_results:
                return analysis_results
            
            # Check for new game data and send notifications
            notification_results = self.notification_system.check_for_new_game_data()
            
            # Update system status
            self.system_status.update({
                'last_data_collection': datetime.now().isoformat(),
                'last_notification_check': datetime.now().isoformat(),
                'system_health': 'healthy'
            })
            
            # Combine results
            comprehensive_results = {
                "analysis_timestamp": datetime.now().isoformat(),
                "opponent_analysis": analysis_results,
                "notification_check": notification_results,
                "system_status": self.system_status,
                "summary": {
                    "opponents_found": analysis_results['summary']['total_opponents_found'],
                    "opponents_processed": analysis_results['summary']['opponents_processed'],
                    "opponents_successful": analysis_results['summary']['opponents_successful'],
                    "lloydminster_successful": analysis_results['summary']['lloydminster_successful'],
                    "total_csv_files": analysis_results['summary']['total_csv_files'],
                    "notifications_sent": notification_results.get('notification_results', {}),
                    "new_data_detected": notification_results.get('status') == 'new_data'
                }
            }
            
            # Save comprehensive results
            results_file = f"ajhl_complete_analysis_with_notifications_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            results_path = Path('ajhl_data') / 'reports' / results_file
            results_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(results_path, 'w') as f:
                json.dump(comprehensive_results, f, indent=2)
            
            logger.info(f"📄 Comprehensive results saved to: {results_path}")
            return comprehensive_results
            
        except Exception as e:
            logger.error(f"❌ Error in full analysis with notifications: {e}")
            return {"error": str(e)}
        finally:
            self.cleanup()
    
    def start_continuous_monitoring(self, days_ahead: int = 30, check_interval_hours: int = 6):
        """Start continuous monitoring with notifications"""
        logger.info("🚀 Starting continuous monitoring with notifications...")
        
        if not self.initialize_system():
            logger.error("❌ Failed to initialize system for monitoring")
            return False
        
        self.system_status['monitoring_active'] = True
        self.stop_monitoring = False
        
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(days_ahead, check_interval_hours),
            daemon=True
        )
        self.monitoring_thread.start()
        
        logger.info(f"✅ Continuous monitoring started (checking every {check_interval_hours} hours)")
        return True
    
    def _monitoring_loop(self, days_ahead: int, check_interval_hours: int):
        """Main monitoring loop"""
        logger.info("🔄 Starting monitoring loop...")
        
        while not self.stop_monitoring:
            try:
                logger.info("🔍 Running scheduled data collection and notification check...")
                
                # Run data collection
                analysis_results = self.opponent_system.discover_and_download_opponent_data(days_ahead)
                
                # Check for new data and send notifications
                notification_results = self.notification_system.check_for_new_game_data()
                
                # Update system status
                self.system_status.update({
                    'last_data_collection': datetime.now().isoformat(),
                    'last_notification_check': datetime.now().isoformat(),
                    'system_health': 'healthy'
                })
                
                # Log results
                if notification_results.get('status') == 'new_data':
                    logger.info(f"🎉 New data detected! Notifications sent.")
                    self.system_status['total_notifications_sent'] += 1
                else:
                    logger.info("📊 No new data detected")
                
                # Wait for next check
                logger.info(f"⏰ Next check in {check_interval_hours} hours...")
                time.sleep(check_interval_hours * 3600)  # Convert hours to seconds
                
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {e}")
                self.system_status['system_health'] = 'error'
                time.sleep(300)  # Wait 5 minutes before retrying
    
    def stop_continuous_monitoring(self):
        """Stop continuous monitoring"""
        logger.info("🛑 Stopping continuous monitoring...")
        
        self.stop_monitoring = True
        self.system_status['monitoring_active'] = False
        
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=10)
        
        logger.info("✅ Continuous monitoring stopped")
    
    def test_notification_system(self):
        """Test the notification system"""
        logger.info("🧪 Testing notification system...")
        
        if not self.initialize_system():
            return {"error": "Failed to initialize system"}
        
        try:
            # Test notifications
            self.notification_system.test_notifications()
            
            # Test data check
            check_results = self.notification_system.check_for_new_game_data()
            
            return {
                "notification_test": "completed",
                "data_check": check_results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error testing notification system: {e}")
            return {"error": str(e)}
        finally:
            self.cleanup()
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        status = {
            'system_status': self.system_status,
            'timestamp': datetime.now().isoformat(),
            'components': {
                'opponent_system': self.opponent_system is not None,
                'notification_system': self.notification_system is not None,
                'dashboard': self.dashboard is not None
            }
        }
        
        # Add notification system status
        if self.notification_system:
            try:
                notification_config = self.notification_system.config
                status['notification_channels'] = {
                    'email_enabled': notification_config['email']['enabled'],
                    'sms_enabled': notification_config['sms']['enabled'],
                    'push_enabled': notification_config['push']['enabled'],
                    'discord_enabled': notification_config['discord']['enabled'],
                    'slack_enabled': notification_config['slack']['enabled'],
                    'check_interval_minutes': notification_config['check_interval_minutes']
                }
                
                # Get recent notification history
                recent_notifications = self.notification_system.get_notification_history(7)
                status['recent_notifications'] = {
                    'count': len(recent_notifications),
                    'last_notification': recent_notifications[-1]['timestamp'] if recent_notifications else None
                }
            except Exception as e:
                status['notification_channels'] = {'error': str(e)}
        
        return status
    
    def generate_comprehensive_dashboard(self) -> str:
        """Generate comprehensive dashboard including notifications"""
        logger.info("📊 Generating comprehensive dashboard...")
        
        try:
            if not self.dashboard:
                self.dashboard = AJHLMonitoringDashboard()
            
            # Generate standard dashboard
            dashboard_path = self.dashboard.generate_html_dashboard()
            
            # Generate notification-specific summary
            self._generate_notification_summary()
            
            logger.info(f"✅ Comprehensive dashboard generated: {dashboard_path}")
            return dashboard_path
            
        except Exception as e:
            logger.error(f"❌ Error generating comprehensive dashboard: {e}")
            return None
    
    def _generate_notification_summary(self):
        """Generate notification-specific summary report"""
        try:
            if not self.notification_system:
                return
            
            # Get notification history
            recent_notifications = self.notification_system.get_notification_history(30)
            
            # Generate summary
            summary = f"""
AJHL Notification System Summary
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}

SYSTEM STATUS:
Monitoring Active: {'✅ Yes' if self.system_status['monitoring_active'] else '❌ No'}
Last Data Collection: {self.system_status.get('last_data_collection', 'Never')}
Last Notification Check: {self.system_status.get('last_notification_check', 'Never')}
Total Notifications Sent: {self.system_status.get('total_notifications_sent', 0)}

NOTIFICATION CHANNELS:
"""
            
            config = self.notification_system.config
            channels = [
                ('Email', config['email']['enabled'], len(config['email']['recipients'])),
                ('SMS', config['sms']['enabled'], len(config['sms']['recipients'])),
                ('Push', config['push']['enabled'], 1 if config['push']['enabled'] else 0),
                ('Discord', config['discord']['enabled'], 1 if config['discord']['enabled'] else 0),
                ('Slack', config['slack']['enabled'], 1 if config['slack']['enabled'] else 0)
            ]
            
            for channel_name, enabled, count in channels:
                status = "✅" if enabled else "❌"
                summary += f"{status} {channel_name}: {count} {'recipients' if channel_name in ['Email', 'SMS'] else 'configured'}\n"
            
            summary += f"\nCHECK INTERVAL: {config['check_interval_minutes']} minutes\n"
            
            if recent_notifications:
                summary += f"\nRECENT NOTIFICATIONS (Last 30 days): {len(recent_notifications)}\n"
                for notification in recent_notifications[-5:]:  # Show last 5
                    summary += f"  {notification['timestamp']}: {len(notification['new_games'])} new games\n"
            else:
                summary += "\nNo recent notifications\n"
            
            # Save summary
            summary_file = Path('ajhl_data') / 'reports' / f'notification_summary_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
            summary_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(summary_file, 'w') as f:
                f.write(summary)
            
            logger.info(f"📄 Notification summary saved to: {summary_file}")
            
        except Exception as e:
            logger.warning(f"⚠️  Error generating notification summary: {e}")
    
    def cleanup(self):
        """Cleanup all system components"""
        logger.info("🧹 Cleaning up complete system with notifications...")
        
        try:
            if self.opponent_system:
                self.opponent_system.cleanup()
            if self.notification_system:
                # Notification system doesn't need explicit cleanup
                pass
            
            logger.info("✅ Complete system cleanup completed")
        except Exception as e:
            logger.warning(f"⚠️  Error during cleanup: {e}")

def main():
    """Main function for the complete system with notifications"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AJHL Complete System with Notifications')
    parser.add_argument('--full', action='store_true', help='Run full analysis with notifications')
    parser.add_argument('--monitor', action='store_true', help='Start continuous monitoring')
    parser.add_argument('--stop', action='store_true', help='Stop continuous monitoring')
    parser.add_argument('--test', action='store_true', help='Test notification system')
    parser.add_argument('--dashboard', action='store_true', help='Generate comprehensive dashboard')
    parser.add_argument('--status', action='store_true', help='Show system status')
    parser.add_argument('--setup', action='store_true', help='Setup notification channels')
    parser.add_argument('--days', type=int, default=30, help='Days ahead to look for opponents (default: 30)')
    parser.add_argument('--interval', type=int, default=6, help='Check interval in hours for monitoring (default: 6)')
    
    args = parser.parse_args()
    
    try:
        from hudl_credentials import HUDL_USERNAME, HUDL_PASSWORD
        system = AJHLCompleteSystemWithNotifications(HUDL_USERNAME, HUDL_PASSWORD)
    except ImportError:
        print("❌ Please update hudl_credentials.py with your actual credentials")
        return
    
    try:
        if args.setup:
            print("⚙️ Setting up notification channels...")
            import subprocess
            subprocess.run(["python", "setup_notifications.py"])
        
        elif args.full:
            print("🏒 Running full analysis with notifications...")
            results = system.run_full_analysis_with_notifications(args.days)
            if 'error' in results:
                print(f"❌ Full analysis failed: {results['error']}")
            else:
                print(f"✅ Full analysis completed:")
                print(f"  Opponents found: {results['summary']['opponents_found']}")
                print(f"  Opponents processed: {results['summary']['opponents_processed']}")
                print(f"  Opponents successful: {results['summary']['opponents_successful']}")
                print(f"  Lloydminster successful: {results['summary']['lloydminster_successful']}")
                print(f"  Total CSV files: {results['summary']['total_csv_files']}")
                print(f"  New data detected: {results['summary']['new_data_detected']}")
        
        elif args.monitor:
            print("🚀 Starting continuous monitoring...")
            if system.start_continuous_monitoring(args.days, args.interval):
                print(f"✅ Monitoring started (checking every {args.interval} hours)")
                print("Press Ctrl+C to stop monitoring")
                try:
                    while True:
                        time.sleep(60)
                except KeyboardInterrupt:
                    print("\n🛑 Stopping monitoring...")
                    system.stop_continuous_monitoring()
            else:
                print("❌ Failed to start monitoring")
        
        elif args.stop:
            print("🛑 Stopping continuous monitoring...")
            system.stop_continuous_monitoring()
            print("✅ Monitoring stopped")
        
        elif args.test:
            print("🧪 Testing notification system...")
            results = system.test_notification_system()
            if 'error' in results:
                print(f"❌ Test failed: {results['error']}")
            else:
                print("✅ Notification test completed")
        
        elif args.dashboard:
            print("📊 Generating comprehensive dashboard...")
            dashboard_path = system.generate_comprehensive_dashboard()
            if dashboard_path:
                print(f"✅ Dashboard generated: {dashboard_path}")
            else:
                print("❌ Dashboard generation failed")
        
        elif args.status:
            print("📊 System Status:")
            status = system.get_system_status()
            print(json.dumps(status, indent=2))
        
        else:
            print("🏒 AJHL Complete System with Notifications")
            print("=" * 50)
            print("Available commands:")
            print("  --setup     Setup notification channels")
            print("  --full      Run full analysis with notifications")
            print("  --monitor   Start continuous monitoring")
            print("  --stop      Stop continuous monitoring")
            print("  --test      Test notification system")
            print("  --dashboard Generate comprehensive dashboard")
            print("  --status    Show system status")
            print("  --days N    Days ahead to look for opponents (default: 30)")
            print("  --interval N Check interval in hours (default: 6)")
            print("\n📝 First run: --setup to configure notifications")
        
    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled by user")
        system.stop_continuous_monitoring()
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        system.cleanup()

if __name__ == "__main__":
    main()
