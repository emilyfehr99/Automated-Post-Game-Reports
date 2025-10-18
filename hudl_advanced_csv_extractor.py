#!/usr/bin/env python3
"""
Hudl Advanced CSV Extractor
Advanced CSV extraction with custom data selection for Bobcats games
"""

import json
import pandas as pd
from hudl_csv_extractor import HudlCSVExtractor, GameData

class HudlAdvancedCSVExtractor(HudlCSVExtractor):
    """Advanced CSV extractor with custom data selection capabilities"""
    
    def __init__(self, headless: bool = True, user_identifier: str = None):
        super().__init__(headless, user_identifier)
        
        # Predefined data selection profiles
        self.data_profiles = {
            'comprehensive': {
                'shifts': ['All shifts', 'Even strength shifts', 'Power play shifts', 'Penalty kill shifts'],
                'main_stats': ['Goals', 'Assists', 'Penalties', 'Hits'],
                'shots': ['Shots', 'Shots on goal', 'Blocked shots', 'Missed shots'],
                'passes': ['Passes', 'Accurate passes', 'Inaccurate passes', 'Passes to the slot'],
                'puck_battles': ['Puck battles', 'Puck battles won', 'Puck battles lost'],
                'entries_breakouts': ['Entries', 'Breakouts', 'Faceoffs', 'Faceoffs won', 'Faceoffs lost'],
                'goalie': ['Goals against', 'Shots against', 'Saves']
            },
            'play_by_play': {
                'shifts': ['All shifts'],
                'main_stats': ['Goals', 'Assists', 'Penalties'],
                'shots': ['Shots', 'Shots on goal'],
                'passes': ['Passes', 'Accurate passes', 'Inaccurate passes'],
                'entries_breakouts': ['Entries', 'Breakouts', 'Faceoffs', 'Faceoffs won', 'Faceoffs lost']
            },
            'analytics': {
                'shifts': ['All shifts', 'Even strength shifts', 'Power play shifts', 'Penalty kill shifts'],
                'shots': ['Shots', 'Shots on goal', 'Blocked shots', 'Missed shots', 'Power play shots', 'Short-handed shots'],
                'passes': ['Passes', 'Accurate passes', 'Inaccurate passes', 'Passes to the slot'],
                'puck_battles': ['Puck battles', 'Puck battles won', 'Puck battles lost'],
                'entries_breakouts': ['Entries', 'Breakouts', 'Faceoffs', 'Faceoffs won', 'Faceoffs lost']
            },
            'goalie_focused': {
                'goalie': ['Goals against', 'Shots against', 'Saves', 'Shootouts'],
                'shots': ['Shots', 'Shots on goal', 'Blocked shots'],
                'main_stats': ['Penalties']
            }
        }
    
    def download_game_with_profile(self, game: GameData, profile_name: str = 'comprehensive') -> bool:
        """Download CSV with a predefined data profile"""
        if profile_name not in self.data_profiles:
            logger.warning(f"⚠️  Unknown profile '{profile_name}', using comprehensive")
            profile_name = 'comprehensive'
        
        profile = self.data_profiles[profile_name]
        logger.info(f"📊 Using data profile: {profile_name}")
        
        return self.download_game_csv(game, profile)
    
    def download_custom_selection(self, game: GameData, custom_selections: Dict[str, List[str]]) -> bool:
        """Download CSV with custom data selections"""
        logger.info(f"📊 Using custom data selections")
        return self.download_game_csv(game, custom_selections)
    
    def analyze_csv_data(self, game: GameData) -> Dict:
        """Analyze downloaded CSV data and provide insights"""
        if not game.csv_path:
            return {"error": "No CSV file available for analysis"}
        
        try:
            df = pd.read_csv(game.csv_path)
            
            analysis = {
                'game_info': {
                    'home_team': game.home_team,
                    'away_team': game.away_team,
                    'score': game.score,
                    'date': game.date
                },
                'data_overview': {
                    'total_rows': len(df),
                    'total_columns': len(df.columns),
                    'columns': list(df.columns)
                },
                'data_quality': {
                    'missing_values': df.isnull().sum().to_dict(),
                    'duplicate_rows': df.duplicated().sum()
                }
            }
            
            # Try to identify key metrics if they exist
            if 'Goals' in df.columns:
                analysis['goals'] = {
                    'total_goals': df['Goals'].sum() if df['Goals'].dtype in ['int64', 'float64'] else 'N/A',
                    'goals_by_period': df.groupby('Period')['Goals'].sum().to_dict() if 'Period' in df.columns else 'N/A'
                }
            
            if 'Shots' in df.columns:
                analysis['shots'] = {
                    'total_shots': df['Shots'].sum() if df['Shots'].dtype in ['int64', 'float64'] else 'N/A',
                    'shots_on_goal': df['Shots on goal'].sum() if 'Shots on goal' in df.columns and df['Shots on goal'].dtype in ['int64', 'float64'] else 'N/A'
                }
            
            if 'Passes' in df.columns:
                analysis['passes'] = {
                    'total_passes': df['Passes'].sum() if df['Passes'].dtype in ['int64', 'float64'] else 'N/A',
                    'accurate_passes': df['Accurate passes'].sum() if 'Accurate passes' in df.columns and df['Accurate passes'].dtype in ['int64', 'float64'] else 'N/A'
                }
            
            return analysis
            
        except Exception as e:
            return {"error": f"Failed to analyze CSV data: {e}"}
    
    def export_analysis_report(self, games: List[GameData], filename: str = None) -> str:
        """Export comprehensive analysis report for multiple games"""
        if not filename:
            filename = f"bobcats_analysis_report_{int(time.time())}.json"
        
        report = {
            'team': 'Lloydminster Bobcats',
            'team_id': '21479',
            'analysis_timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'games_analyzed': len(games),
            'games': []
        }
        
        for game in games:
            game_analysis = self.analyze_csv_data(game)
            report['games'].append({
                'game_info': {
                    'game_id': game.game_id,
                    'home_team': game.home_team,
                    'away_team': game.away_team,
                    'score': game.score,
                    'date': game.date,
                    'csv_downloaded': game.csv_downloaded,
                    'csv_path': game.csv_path
                },
                'analysis': game_analysis
            })
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📄 Analysis report exported to: {filename}")
        return filename

def main():
    """Example usage of the advanced CSV extractor"""
    print("🏒 Hudl Advanced CSV Extractor")
    print("=" * 60)
    
    # Initialize advanced extractor
    extractor = HudlAdvancedCSVExtractor(headless=False)
    
    try:
        # Authenticate
        from hudl_credentials import HUDL_USERNAME, HUDL_PASSWORD
        if not extractor.authenticate(HUDL_USERNAME, HUDL_PASSWORD):
            print("❌ Authentication failed")
            return
        
        print("✅ Successfully authenticated")
        
        # Get games list
        print("\n🔍 Getting games list...")
        games = extractor.get_games_list()
        print(f"Found {len(games)} games")
        
        if not games:
            print("❌ No games found")
            return
        
        # Show available data profiles
        print(f"\n📊 Available data profiles:")
        for profile_name in extractor.data_profiles.keys():
            print(f"  - {profile_name}")
        
        # Download with different profiles
        print(f"\n📥 Downloading CSV data with different profiles...")
        
        # Download first game with comprehensive profile
        first_game = games[0]
        print(f"\n🎯 Game 1: {first_game.home_team} vs {first_game.away_team}")
        
        # Comprehensive data
        print("  📊 Downloading comprehensive data...")
        success1 = extractor.download_game_with_profile(first_game, 'comprehensive')
        if success1:
            analysis1 = extractor.analyze_csv_data(first_game)
            print(f"    ✅ Downloaded: {analysis1.get('data_overview', {}).get('total_rows', 'N/A')} rows")
        
        # Play-by-play data
        print("  📊 Downloading play-by-play data...")
        success2 = extractor.download_game_with_profile(first_game, 'play_by_play')
        if success2:
            analysis2 = extractor.analyze_csv_data(first_game)
            print(f"    ✅ Downloaded: {analysis2.get('data_overview', {}).get('total_rows', 'N/A')} rows")
        
        # Custom selection example
        print(f"\n🎯 Game 2: {games[1].home_team} vs {games[1].away_team}")
        custom_selection = {
            'main_stats': ['Goals', 'Assists'],
            'shots': ['Shots', 'Shots on goal'],
            'passes': ['Passes', 'Accurate passes']
        }
        print("  📊 Downloading with custom selection...")
        success3 = extractor.download_custom_selection(games[1], custom_selection)
        if success3:
            analysis3 = extractor.analyze_csv_data(games[1])
            print(f"    ✅ Downloaded: {analysis3.get('data_overview', {}).get('total_rows', 'N/A')} rows")
        
        # Export analysis report
        print(f"\n📄 Exporting analysis report...")
        report_file = extractor.export_analysis_report(games[:3])  # First 3 games
        print(f"Report exported to: {report_file}")
        
    except ImportError:
        print("❌ Please update hudl_credentials.py with your actual credentials")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        extractor.close()

if __name__ == "__main__":
    main()
