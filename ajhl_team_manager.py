#!/usr/bin/env python3
"""
AJHL Team Manager
Specialized manager for all Alberta Junior Hockey League teams with daily CSV downloading
"""

import json
import time
import logging
import os
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from hudl_multi_user_manager import HudlMultiUserManager
from hudl_advanced_csv_extractor import HudlAdvancedCSVExtractor
from ajhl_team_config import (
    AJHL_TEAMS, get_active_teams, get_teams_with_hudl_ids, 
    get_data_profile, DATA_DIRECTORIES, SCHEDULE_CONFIG
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ajhl_daily_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AJHLTeamManager:
    """Manager for all AJHL teams with daily CSV downloading capabilities"""
    
    def __init__(self, username: str, password: str):
        """Initialize the AJHL team manager"""
        self.username = username
        self.password = password
        self.manager = HudlMultiUserManager(username, password)
        self.csv_extractor = None
        self.setup_directories()
        self.daily_stats = {
            'total_teams': len(get_active_teams()),
            'teams_processed': 0,
            'teams_successful': 0,
            'teams_failed': 0,
            'csv_files_downloaded': 0,
            'start_time': None,
            'end_time': None,
            'errors': []
        }
    
    def setup_directories(self):
        """Create necessary directories for data storage"""
        base_path = Path(DATA_DIRECTORIES['base_path'])
        
        for dir_name in DATA_DIRECTORIES.values():
            if dir_name != base_path:
                dir_path = base_path / dir_name
                dir_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"📁 Created directory: {dir_path}")
        
        # Create team-specific subdirectories
        for team_id in get_active_teams().keys():
            team_dir = base_path / DATA_DIRECTORIES['daily_downloads'] / team_id
            team_dir.mkdir(parents=True, exist_ok=True)
    
    def initialize_csv_extractor(self, user_id: str = "ajhl_scraper"):
        """Initialize the CSV extractor for downloading data"""
        try:
            self.csv_extractor = HudlAdvancedCSVExtractor(
                headless=True, 
                user_identifier=user_id
            )
            
            if not self.csv_extractor.authenticate(self.username, self.password):
                logger.error("❌ Failed to authenticate CSV extractor")
                return False
            
            logger.info("✅ CSV extractor initialized and authenticated")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error initializing CSV extractor: {e}")
            return False
    
    def discover_team_hudl_ids(self) -> Dict[str, str]:
        """Discover Hudl team IDs for teams that don't have them yet"""
        logger.info("🔍 Discovering Hudl team IDs for AJHL teams...")
        
        discovered_ids = {}
        teams_without_ids = {
            team_id: team_data for team_id, team_data in get_active_teams().items()
            if not team_data['hudl_team_id']
        }
        
        if not teams_without_ids:
            logger.info("✅ All teams already have Hudl IDs")
            return discovered_ids
        
        # This would need to be implemented based on Hudl's search functionality
        # For now, we'll return empty and log what needs to be done
        logger.warning(f"⚠️  {len(teams_without_ids)} teams need Hudl ID discovery:")
        for team_id, team_data in teams_without_ids.items():
            logger.warning(f"  - {team_data['team_name']} ({team_data['city']})")
        
        logger.info("💡 Manual discovery required - check Hudl Instat platform for team IDs")
        return discovered_ids
    
    def download_team_daily_data(self, team_id: str, profile_name: str = 'daily_analytics') -> Dict:
        """Download daily CSV data for a specific team"""
        team_data = get_active_teams().get(team_id)
        if not team_data:
            return {"error": f"Team {team_id} not found"}
        
        if not team_data['hudl_team_id']:
            return {"error": f"No Hudl team ID for {team_data['team_name']}"}
        
        logger.info(f"📥 Downloading data for {team_data['team_name']}...")
        
        try:
            # Get games list for the team
            games = self.csv_extractor.get_games_list()
            if not games:
                logger.warning(f"⚠️  No games found for {team_data['team_name']}")
                return {"error": "No games found", "team": team_data['team_name']}
            
            # Filter games for this team (this would need to be implemented based on game data structure)
            team_games = games  # For now, assume all games are relevant
            
            # Download CSV for each game
            downloaded_files = []
            profile = get_data_profile(profile_name)
            
            for game in team_games[:5]:  # Limit to 5 most recent games
                try:
                    success = self.csv_extractor.download_game_with_profile(game, profile_name)
                    if success and game.csv_path:
                        downloaded_files.append(game.csv_path)
                        logger.info(f"  ✅ Downloaded: {game.csv_path}")
                    else:
                        logger.warning(f"  ⚠️  Failed to download game data")
                except Exception as e:
                    logger.error(f"  ❌ Error downloading game: {e}")
            
            # Move files to team-specific directory
            team_dir = Path(DATA_DIRECTORIES['base_path']) / DATA_DIRECTORIES['daily_downloads'] / team_id
            moved_files = []
            
            for file_path in downloaded_files:
                try:
                    filename = Path(file_path).name
                    new_path = team_dir / f"{datetime.now().strftime('%Y%m%d')}_{filename}"
                    
                    # Copy file to team directory
                    import shutil
                    shutil.copy2(file_path, new_path)
                    moved_files.append(str(new_path))
                    
                except Exception as e:
                    logger.error(f"  ❌ Error moving file {file_path}: {e}")
            
            result = {
                "team_id": team_id,
                "team_name": team_data['team_name'],
                "hudl_team_id": team_data['hudl_team_id'],
                "games_processed": len(team_games),
                "files_downloaded": len(downloaded_files),
                "files_moved": len(moved_files),
                "file_paths": moved_files,
                "profile_used": profile_name,
                "timestamp": datetime.now().isoformat(),
                "success": len(moved_files) > 0
            }
            
            if result['success']:
                logger.info(f"✅ Successfully processed {team_data['team_name']}: {len(moved_files)} files")
            else:
                logger.error(f"❌ Failed to process {team_data['team_name']}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error downloading data for {team_data['team_name']}: {e}")
            return {"error": str(e), "team": team_data['team_name']}
    
    def process_all_teams_daily(self, profile_name: str = 'daily_analytics') -> Dict:
        """Process all active AJHL teams for daily data download"""
        logger.info("🏒 Starting daily AJHL data collection...")
        self.daily_stats['start_time'] = datetime.now()
        
        # Initialize CSV extractor
        if not self.initialize_csv_extractor():
            return {"error": "Failed to initialize CSV extractor"}
        
        # Get teams with Hudl IDs
        teams_with_ids = get_teams_with_hudl_ids()
        if not teams_with_ids:
            logger.error("❌ No teams have Hudl IDs - run discovery first")
            return {"error": "No teams have Hudl IDs"}
        
        logger.info(f"📊 Processing {len(teams_with_ids)} teams with Hudl IDs")
        
        results = {}
        successful_teams = 0
        failed_teams = 0
        
        for team_id, team_data in teams_with_ids.items():
            logger.info(f"\n🏒 Processing {team_data['team_name']}...")
            
            try:
                result = self.download_team_daily_data(team_id, profile_name)
                results[team_id] = result
                
                if result.get('success', False):
                    successful_teams += 1
                    self.daily_stats['teams_successful'] += 1
                    self.daily_stats['csv_files_downloaded'] += result.get('files_downloaded', 0)
                else:
                    failed_teams += 1
                    self.daily_stats['teams_failed'] += 1
                    self.daily_stats['errors'].append({
                        'team': team_data['team_name'],
                        'error': result.get('error', 'Unknown error'),
                        'timestamp': datetime.now().isoformat()
                    })
                
                # Delay between teams to avoid overwhelming Hudl
                time.sleep(SCHEDULE_CONFIG['team_delay_seconds'])
                
            except Exception as e:
                logger.error(f"❌ Unexpected error processing {team_data['team_name']}: {e}")
                failed_teams += 1
                self.daily_stats['teams_failed'] += 1
                self.daily_stats['errors'].append({
                    'team': team_data['team_name'],
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        self.daily_stats['end_time'] = datetime.now()
        self.daily_stats['teams_processed'] = len(teams_with_ids)
        
        # Generate summary report
        summary = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'total_teams': len(teams_with_ids),
            'successful_teams': successful_teams,
            'failed_teams': failed_teams,
            'total_csv_files': self.daily_stats['csv_files_downloaded'],
            'processing_time_minutes': (self.daily_stats['end_time'] - self.daily_stats['start_time']).total_seconds() / 60,
            'results': results,
            'errors': self.daily_stats['errors']
        }
        
        # Save summary report
        report_path = Path(DATA_DIRECTORIES['base_path']) / DATA_DIRECTORIES['reports'] / f"daily_summary_{datetime.now().strftime('%Y%m%d')}.json"
        with open(report_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"📄 Daily summary saved to: {report_path}")
        logger.info(f"✅ Daily processing complete: {successful_teams}/{len(teams_with_ids)} teams successful")
        
        return summary
    
    def get_team_data_summary(self, team_id: str) -> Dict:
        """Get summary of downloaded data for a specific team"""
        team_data = get_active_teams().get(team_id)
        if not team_data:
            return {"error": f"Team {team_id} not found"}
        
        team_dir = Path(DATA_DIRECTORIES['base_path']) / DATA_DIRECTORIES['daily_downloads'] / team_id
        
        if not team_dir.exists():
            return {"error": f"No data directory found for {team_data['team_name']}"}
        
        # Get all CSV files for this team
        csv_files = list(team_dir.glob("*.csv"))
        
        summary = {
            "team_id": team_id,
            "team_name": team_data['team_name'],
            "data_directory": str(team_dir),
            "total_files": len(csv_files),
            "files": [str(f) for f in csv_files],
            "latest_file": max(csv_files, key=os.path.getctime).name if csv_files else None,
            "oldest_file": min(csv_files, key=os.path.getctime).name if csv_files else None
        }
        
        return summary
    
    def cleanup_old_data(self, days_to_keep: int = 30):
        """Clean up data older than specified days"""
        logger.info(f"🧹 Cleaning up data older than {days_to_keep} days...")
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        cleaned_files = 0
        
        for team_id in get_active_teams().keys():
            team_dir = Path(DATA_DIRECTORIES['base_path']) / DATA_DIRECTORIES['daily_downloads'] / team_id
            
            if team_dir.exists():
                for file_path in team_dir.glob("*.csv"):
                    file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_time < cutoff_date:
                        file_path.unlink()
                        cleaned_files += 1
                        logger.info(f"  🗑️  Deleted old file: {file_path.name}")
        
        logger.info(f"✅ Cleanup complete: {cleaned_files} files removed")
        return cleaned_files
    
    def close(self):
        """Close all connections and cleanup"""
        if self.csv_extractor:
            self.csv_extractor.close()
        self.manager.close_all_sessions()
        logger.info("🔒 AJHL Team Manager closed")

def main():
    """Example usage of the AJHL Team Manager"""
    print("🏒 AJHL Team Manager - Daily Data Collection")
    print("=" * 60)
    
    try:
        from hudl_credentials import HUDL_USERNAME, HUDL_PASSWORD
        manager = AJHLTeamManager(HUDL_USERNAME, HUDL_PASSWORD)
    except ImportError:
        print("❌ Please update hudl_credentials.py with your actual credentials")
        return
    
    # Discover team IDs (if needed)
    print("\n🔍 Discovering team Hudl IDs...")
    discovered = manager.discover_team_hudl_ids()
    
    # Process all teams
    print("\n📊 Processing all teams...")
    results = manager.process_all_teams_daily('daily_analytics')
    
    if 'error' not in results:
        print(f"\n✅ Daily processing complete:")
        print(f"  Teams processed: {results['total_teams']}")
        print(f"  Successful: {results['successful_teams']}")
        print(f"  Failed: {results['failed_teams']}")
        print(f"  CSV files downloaded: {results['total_csv_files']}")
        print(f"  Processing time: {results['processing_time_minutes']:.1f} minutes")
    else:
        print(f"❌ Error: {results['error']}")
    
    # Show team summaries
    print(f"\n📋 Team Data Summaries:")
    for team_id in get_active_teams().keys():
        summary = manager.get_team_data_summary(team_id)
        if 'error' not in summary:
            print(f"  {summary['team_name']}: {summary['total_files']} files")
        else:
            print(f"  {team_id}: {summary['error']}")
    
    # Cleanup
    manager.close()
    print("\n✅ Manager closed")

if __name__ == "__main__":
    main()
