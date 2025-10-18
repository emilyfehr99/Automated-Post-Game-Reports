#!/usr/bin/env python3
"""
AJHL Real Hudl Manager
Updated AJHL manager using the actual Hudl Instat tab structure:
OVERVIEW, GAMES, SKATERS, GOALIES, LINES, SHOT MAP, FACEOFFS, EPISODES SEARCH
"""

import json
import time
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from hudl_instat_csv_downloader import HudlInstatCSVDownloader
from ajhl_team_config import get_active_teams, DATA_DIRECTORIES, SCHEDULE_CONFIG

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ajhl_real_hudl_manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AJHLRealHudlManager:
    """AJHL manager using real Hudl Instat structure"""
    
    def __init__(self, username: str, password: str):
        """Initialize the AJHL real Hudl manager"""
        self.username = username
        self.password = password
        self.csv_downloader = None
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
        
        # Define Hudl Instat tabs for data collection
        self.hudl_tabs = [
            "OVERVIEW", "GAMES", "SKATERS", "GOALIES", 
            "LINES", "SHOT MAP", "FACEOFFS", "EPISODES SEARCH"
        ]
    
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
            
            # Create tab-specific subdirectories for each team
            for tab in self.hudl_tabs:
                tab_dir = team_dir / tab.lower().replace(" ", "_")
                tab_dir.mkdir(parents=True, exist_ok=True)
    
    def initialize_csv_downloader(self, user_id: str = "ajhl_real_scraper"):
        """Initialize the CSV downloader"""
        try:
            self.csv_downloader = HudlInstatCSVDownloader(
                headless=True, 
                user_identifier=user_id
            )
            
            if not self.csv_downloader.authenticate(self.username, self.password):
                logger.error("❌ Failed to authenticate CSV downloader")
                return False
            
            logger.info("✅ CSV downloader initialized and authenticated")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error initializing CSV downloader: {e}")
            return False
    
    def download_team_comprehensive_data(self, team_id: str) -> Dict[str, Any]:
        """Download comprehensive data for a specific team from all tabs"""
        team_data = get_active_teams().get(team_id)
        if not team_data:
            return {"error": f"Team {team_id} not found"}
        
        if not team_data['hudl_team_id']:
            return {"error": f"No Hudl team ID for {team_data['team_name']}"}
        
        logger.info(f"📥 Downloading comprehensive data for {team_data['team_name']}...")
        
        try:
            # Download all CSVs for the team
            download_results = self.csv_downloader.download_team_csvs(team_data['hudl_team_id'])
            
            if "error" in download_results:
                return download_results
            
            # Organize downloaded files by tab
            organized_files = self._organize_downloaded_files(download_results, team_id)
            
            # Move files to appropriate team directories
            moved_files = self._move_files_to_team_directories(organized_files, team_id)
            
            result = {
                "team_id": team_id,
                "team_name": team_data['team_name'],
                "hudl_team_id": team_data['hudl_team_id'],
                "download_results": download_results,
                "organized_files": organized_files,
                "moved_files": moved_files,
                "total_files": len(moved_files),
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
    
    def _organize_downloaded_files(self, download_results: Dict, team_id: str) -> Dict[str, List[Dict]]:
        """Organize downloaded files by tab and data type"""
        organized_files = {}
        
        # Initialize tab directories
        for tab in self.hudl_tabs:
            organized_files[tab] = []
        
        try:
            # Get downloaded files from the downloader
            downloaded_files = download_results.get('downloaded_files', [])
            
            # Organize by tab based on download results
            for tab_name, tab_results in download_results.get('tabs_processed', {}).items():
                if tab_results.get('downloads_successful', 0) > 0:
                    # Find files that were downloaded for this tab
                    tab_files = []
                    for file_info in downloaded_files:
                        # Try to determine which tab this file belongs to
                        # This is a simplified approach - in practice, you'd need more sophisticated matching
                        tab_files.append({
                            "filename": file_info['filename'],
                            "file_path": file_info['file_path'],
                            "size_bytes": file_info['size_bytes'],
                            "created_time": file_info['created_time'],
                            "tab": tab_name
                        })
                    
                    organized_files[tab_name] = tab_files
            
        except Exception as e:
            logger.warning(f"⚠️  Error organizing files: {e}")
        
        return organized_files
    
    def _move_files_to_team_directories(self, organized_files: Dict, team_id: str) -> List[Dict]:
        """Move organized files to team-specific directories"""
        moved_files = []
        base_path = Path(DATA_DIRECTORIES['base_path'])
        
        try:
            for tab_name, files in organized_files.items():
                if not files:
                    continue
                
                # Create tab directory for this team
                tab_dir = base_path / DATA_DIRECTORIES['daily_downloads'] / team_id / tab_name.lower().replace(" ", "_")
                tab_dir.mkdir(parents=True, exist_ok=True)
                
                for file_info in files:
                    try:
                        source_path = Path(file_info['file_path'])
                        if source_path.exists():
                            # Create new filename with timestamp
                            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                            new_filename = f"{timestamp}_{file_info['filename']}"
                            dest_path = tab_dir / new_filename
                            
                            # Copy file to team directory
                            import shutil
                            shutil.copy2(source_path, dest_path)
                            
                            moved_files.append({
                                "original_filename": file_info['filename'],
                                "new_filename": new_filename,
                                "team_id": team_id,
                                "tab": tab_name,
                                "file_path": str(dest_path),
                                "size_bytes": file_info['size_bytes'],
                                "moved_time": datetime.now().isoformat()
                            })
                            
                            logger.info(f"📁 Moved {file_info['filename']} to {tab_name} directory")
                    
                    except Exception as e:
                        logger.warning(f"⚠️  Error moving file {file_info['filename']}: {e}")
            
        except Exception as e:
            logger.error(f"❌ Error moving files: {e}")
        
        return moved_files
    
    def process_all_teams_daily(self) -> Dict[str, Any]:
        """Process all active AJHL teams for daily data download"""
        logger.info("🏒 Starting daily AJHL data collection with real Hudl structure...")
        self.daily_stats['start_time'] = datetime.now()
        
        # Initialize CSV downloader
        if not self.initialize_csv_downloader():
            return {"error": "Failed to initialize CSV downloader"}
        
        # Get teams with Hudl IDs
        teams_with_ids = {team_id: team_data for team_id, team_data in get_active_teams().items() 
                         if team_data['hudl_team_id']}
        
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
                result = self.download_team_comprehensive_data(team_id)
                results[team_id] = result
                
                if result.get('success', False):
                    successful_teams += 1
                    self.daily_stats['teams_successful'] += 1
                    self.daily_stats['csv_files_downloaded'] += result.get('total_files', 0)
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
            'hudl_tabs_processed': self.hudl_tabs,
            'results': results,
            'errors': self.daily_stats['errors']
        }
        
        # Save summary report
        report_path = Path(DATA_DIRECTORIES['base_path']) / DATA_DIRECTORIES['reports'] / f"daily_summary_real_hudl_{datetime.now().strftime('%Y%m%d')}.json"
        with open(report_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"📄 Daily summary saved to: {report_path}")
        logger.info(f"✅ Daily processing complete: {successful_teams}/{len(teams_with_ids)} teams successful")
        
        return summary
    
    def get_team_data_summary(self, team_id: str) -> Dict[str, Any]:
        """Get summary of downloaded data for a specific team"""
        team_data = get_active_teams().get(team_id)
        if not team_data:
            return {"error": f"Team {team_id} not found"}
        
        base_path = Path(DATA_DIRECTORIES['base_path']) / DATA_DIRECTORIES['daily_downloads'] / team_id
        
        if not base_path.exists():
            return {"error": f"No data directory found for {team_data['team_name']}"}
        
        # Get all files organized by tab
        tab_summary = {}
        total_files = 0
        
        for tab in self.hudl_tabs:
            tab_dir = base_path / tab.lower().replace(" ", "_")
            if tab_dir.exists():
                files = list(tab_dir.glob("*"))
                file_count = len(files)
                total_files += file_count
                
                tab_summary[tab] = {
                    "file_count": file_count,
                    "files": [f.name for f in files],
                    "latest_file": max(files, key=os.path.getctime).name if files else None
                }
        
        summary = {
            "team_id": team_id,
            "team_name": team_data['team_name'],
            "data_directory": str(base_path),
            "total_files": total_files,
            "tabs": tab_summary,
            "hudl_tabs_available": self.hudl_tabs
        }
        
        return summary
    
    def download_specific_game_data(self, team_id: str, game_id: str) -> Dict[str, Any]:
        """Download data for a specific game"""
        team_data = get_active_teams().get(team_id)
        if not team_data or not team_data['hudl_team_id']:
            return {"error": f"No Hudl team ID for {team_id}"}
        
        try:
            if not self.csv_downloader:
                if not self.initialize_csv_downloader():
                    return {"error": "Failed to initialize CSV downloader"}
            
            # Download specific game CSV
            result = self.csv_downloader.download_specific_game_csv(team_data['hudl_team_id'], game_id)
            
            if result.get('success'):
                # Move the downloaded file to team directory
                downloaded_files = self.csv_downloader._get_downloaded_files()
                if downloaded_files:
                    # Move the most recent file
                    latest_file = max(downloaded_files, key=lambda x: x['created_time'])
                    team_dir = Path(DATA_DIRECTORIES['base_path']) / DATA_DIRECTORIES['daily_downloads'] / team_id / "games"
                    team_dir.mkdir(parents=True, exist_ok=True)
                    
                    import shutil
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    new_filename = f"{timestamp}_game_{game_id}_{latest_file['filename']}"
                    dest_path = team_dir / new_filename
                    shutil.copy2(latest_file['file_path'], dest_path)
                    
                    result['file_path'] = str(dest_path)
                    result['filename'] = new_filename
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error downloading game data: {e}")
            return {"error": str(e)}
    
    def cleanup_old_data(self, days_to_keep: int = 30):
        """Clean up data older than specified days"""
        logger.info(f"🧹 Cleaning up data older than {days_to_keep} days...")
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        cleaned_files = 0
        
        for team_id in get_active_teams().keys():
            team_dir = Path(DATA_DIRECTORIES['base_path']) / DATA_DIRECTORIES['daily_downloads'] / team_id
            
            if team_dir.exists():
                for file_path in team_dir.rglob("*"):
                    if file_path.is_file():
                        file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                        if file_time < cutoff_date:
                            file_path.unlink()
                            cleaned_files += 1
                            logger.info(f"  🗑️  Deleted old file: {file_path.name}")
        
        logger.info(f"✅ Cleanup complete: {cleaned_files} files removed")
        return cleaned_files
    
    def close(self):
        """Close all connections and cleanup"""
        if self.csv_downloader:
            self.csv_downloader.close()
        logger.info("🔒 AJHL Real Hudl Manager closed")

def main():
    """Example usage of the AJHL Real Hudl Manager"""
    print("🏒 AJHL Real Hudl Manager - Daily Data Collection")
    print("=" * 60)
    
    try:
        from hudl_credentials import HUDL_USERNAME, HUDL_PASSWORD
        manager = AJHLRealHudlManager(HUDL_USERNAME, HUDL_PASSWORD)
    except ImportError:
        print("❌ Please update hudl_credentials.py with your actual credentials")
        return
    
    # Process all teams
    print("\n📊 Processing all teams with real Hudl structure...")
    results = manager.process_all_teams_daily()
    
    if 'error' not in results:
        print(f"\n✅ Daily processing complete:")
        print(f"  Teams processed: {results['total_teams']}")
        print(f"  Successful: {results['successful_teams']}")
        print(f"  Failed: {results['failed_teams']}")
        print(f"  CSV files downloaded: {results['total_csv_files']}")
        print(f"  Processing time: {results['processing_time_minutes']:.1f} minutes")
        print(f"  Hudl tabs processed: {', '.join(results['hudl_tabs_processed'])}")
    else:
        print(f"❌ Error: {results['error']}")
    
    # Show team summaries
    print(f"\n📋 Team Data Summaries:")
    for team_id in get_active_teams().keys():
        summary = manager.get_team_data_summary(team_id)
        if 'error' not in summary:
            print(f"  {summary['team_name']}: {summary['total_files']} files across {len([t for t in summary['tabs'].values() if t['file_count'] > 0])} tabs")
        else:
            print(f"  {team_id}: {summary['error']}")
    
    # Cleanup
    manager.close()
    print("\n✅ Manager closed")

if __name__ == "__main__":
    main()
