#!/usr/bin/env python3
"""
AJHL Daily Scheduler
Automated daily scheduling system for AJHL data collection
"""

import schedule
import time
import logging
import json
import os
import signal
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
from ajhl_team_manager import AJHLTeamManager
from ajhl_team_config import SCHEDULE_CONFIG, DATA_DIRECTORIES

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ajhl_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AJHLDailyScheduler:
    """Daily scheduler for AJHL data collection"""
    
    def __init__(self, username: str, password: str):
        """Initialize the daily scheduler"""
        self.username = username
        self.password = password
        self.manager = None
        self.running = False
        self.scheduler_stats = {
            'total_runs': 0,
            'successful_runs': 0,
            'failed_runs': 0,
            'last_run': None,
            'next_run': None,
            'errors': []
        }
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"🛑 Received signal {signum}, shutting down gracefully...")
        self.running = False
        if self.manager:
            self.manager.close()
        sys.exit(0)
    
    def daily_data_collection(self):
        """Main daily data collection task"""
        logger.info("🏒 Starting daily AJHL data collection...")
        self.scheduler_stats['total_runs'] += 1
        self.scheduler_stats['last_run'] = datetime.now().isoformat()
        
        try:
            # Initialize manager
            self.manager = AJHLTeamManager(self.username, self.password)
            
            # Run daily data collection
            results = self.manager.process_all_teams_daily('daily_analytics')
            
            if 'error' in results:
                logger.error(f"❌ Daily collection failed: {results['error']}")
                self.scheduler_stats['failed_runs'] += 1
                self.scheduler_stats['errors'].append({
                    'timestamp': datetime.now().isoformat(),
                    'error': results['error'],
                    'run_number': self.scheduler_stats['total_runs']
                })
            else:
                logger.info("✅ Daily collection completed successfully")
                self.scheduler_stats['successful_runs'] += 1
                
                # Log summary
                logger.info(f"📊 Summary: {results['successful_teams']}/{results['total_teams']} teams successful")
                logger.info(f"📁 Files downloaded: {results['total_csv_files']}")
                logger.info(f"⏱️  Processing time: {results['processing_time_minutes']:.1f} minutes")
            
            # Save scheduler stats
            self.save_scheduler_stats()
            
        except Exception as e:
            logger.error(f"❌ Unexpected error in daily collection: {e}")
            self.scheduler_stats['failed_runs'] += 1
            self.scheduler_stats['errors'].append({
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'run_number': self.scheduler_stats['total_runs']
            })
            self.save_scheduler_stats()
        
        finally:
            # Cleanup
            if self.manager:
                self.manager.close()
                self.manager = None
    
    def cleanup_old_data_task(self):
        """Cleanup old data task (runs weekly)"""
        logger.info("🧹 Running weekly data cleanup...")
        
        try:
            self.manager = AJHLTeamManager(self.username, self.password)
            cleaned_files = self.manager.cleanup_old_data(days_to_keep=30)
            logger.info(f"✅ Cleanup complete: {cleaned_files} files removed")
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")
        finally:
            if self.manager:
                self.manager.close()
                self.manager = None
    
    def health_check_task(self):
        """Health check task (runs every 6 hours)"""
        logger.info("🏥 Running health check...")
        
        try:
            # Check if data directories exist
            base_path = Path(DATA_DIRECTORIES['base_path'])
            if not base_path.exists():
                logger.error("❌ Base data directory does not exist")
                return False
            
            # Check recent data files
            recent_files = 0
            cutoff_time = datetime.now() - timedelta(hours=24)
            
            for team_dir in base_path.glob("daily_downloads/*"):
                if team_dir.is_dir():
                    for file_path in team_dir.glob("*.csv"):
                        file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                        if file_time > cutoff_time:
                            recent_files += 1
            
            logger.info(f"📊 Health check: {recent_files} recent files found")
            
            # Check scheduler stats
            success_rate = (self.scheduler_stats['successful_runs'] / 
                          max(self.scheduler_stats['total_runs'], 1)) * 100
            logger.info(f"📈 Success rate: {success_rate:.1f}%")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return False
    
    def save_scheduler_stats(self):
        """Save scheduler statistics to file"""
        stats_path = Path(DATA_DIRECTORIES['base_path']) / DATA_DIRECTORIES['logs'] / 'scheduler_stats.json'
        stats_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(stats_path, 'w') as f:
            json.dump(self.scheduler_stats, f, indent=2)
    
    def load_scheduler_stats(self):
        """Load scheduler statistics from file"""
        stats_path = Path(DATA_DIRECTORIES['base_path']) / DATA_DIRECTORIES['logs'] / 'scheduler_stats.json'
        
        if stats_path.exists():
            try:
                with open(stats_path, 'r') as f:
                    self.scheduler_stats = json.load(f)
                logger.info("📊 Loaded existing scheduler statistics")
            except Exception as e:
                logger.warning(f"⚠️  Could not load scheduler stats: {e}")
    
    def setup_schedule(self):
        """Setup the daily schedule"""
        logger.info("⏰ Setting up daily schedule...")
        
        # Daily data collection
        schedule.every().day.at(SCHEDULE_CONFIG['daily_run_time']).do(self.daily_data_collection)
        
        # Weekly cleanup (Sundays at 2 AM)
        schedule.every().sunday.at("02:00").do(self.cleanup_old_data_task)
        
        # Health checks every 6 hours
        schedule.every(6).hours.do(self.health_check_task)
        
        # Calculate next run time
        next_run = schedule.next_run()
        self.scheduler_stats['next_run'] = next_run.isoformat() if next_run else None
        
        logger.info(f"📅 Daily collection scheduled for: {SCHEDULE_CONFIG['daily_run_time']}")
        logger.info(f"🧹 Weekly cleanup scheduled for: Sundays at 02:00")
        logger.info(f"🏥 Health checks every: 6 hours")
        logger.info(f"⏭️  Next run: {next_run}")
    
    def run_scheduler(self):
        """Run the scheduler continuously"""
        logger.info("🚀 Starting AJHL Daily Scheduler...")
        self.running = True
        
        # Load existing stats
        self.load_scheduler_stats()
        
        # Setup schedule
        self.setup_schedule()
        
        logger.info("✅ Scheduler started successfully")
        logger.info("🔄 Waiting for scheduled tasks...")
        
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logger.info("🛑 Scheduler stopped by user")
        except Exception as e:
            logger.error(f"❌ Scheduler error: {e}")
        finally:
            self.running = False
            logger.info("🔒 Scheduler shutdown complete")
    
    def run_once(self):
        """Run the daily collection once (for testing)"""
        logger.info("🧪 Running single daily collection (test mode)...")
        self.daily_data_collection()
    
    def get_status(self) -> Dict:
        """Get current scheduler status"""
        return {
            'running': self.running,
            'next_run': schedule.next_run().isoformat() if schedule.next_run() else None,
            'stats': self.scheduler_stats,
            'scheduled_jobs': len(schedule.jobs)
        }

def main():
    """Main function for running the scheduler"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AJHL Daily Scheduler')
    parser.add_argument('--test', action='store_true', help='Run once for testing')
    parser.add_argument('--status', action='store_true', help='Show scheduler status')
    args = parser.parse_args()
    
    try:
        from hudl_credentials import HUDL_USERNAME, HUDL_PASSWORD
        scheduler = AJHLDailyScheduler(HUDL_USERNAME, HUDL_PASSWORD)
    except ImportError:
        print("❌ Please update hudl_credentials.py with your actual credentials")
        return
    
    if args.status:
        status = scheduler.get_status()
        print("📊 AJHL Scheduler Status")
        print("=" * 40)
        print(f"Running: {status['running']}")
        print(f"Next run: {status['next_run']}")
        print(f"Total runs: {status['stats']['total_runs']}")
        print(f"Successful: {status['stats']['successful_runs']}")
        print(f"Failed: {status['stats']['failed_runs']}")
        print(f"Scheduled jobs: {status['scheduled_jobs']}")
        return
    
    if args.test:
        scheduler.run_once()
    else:
        scheduler.run_scheduler()

if __name__ == "__main__":
    main()
