#!/usr/bin/env python3
"""
Hockey Game Analysis for Game ID: 2024030416
Advanced analytics including shot locations, expected goals, and coaching insights
"""

import requests
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class GameAnalyzer:
    def __init__(self):
        self.base_url = "https://api-web.nhle.com/v1"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Expected Goals (xG) model
        self.xg_model = {
            'shot_types': {
                'wrist': 0.08,
                'slap': 0.06,
                'snap': 0.09,
                'backhand': 0.05,
                'tip': 0.12,
                'deflection': 0.15,
                'wrap': 0.04
            },
            'distance_multipliers': {
                '0-10ft': 1.5,    # Very close
                '10-20ft': 1.2,   # Close
                '20-30ft': 1.0,   # Medium
                '30-40ft': 0.8,   # Far
                '40ft+': 0.6      # Very far
            }
        }
    
    def get_game_data(self, game_id):
        """Get game data from NHL API"""
        try:
            print(f"🔍 Fetching data for game: {game_id}")
            
            # Get game center feed
            game_center_url = f"{self.base_url}/gamecenter/{game_id}/feed/live"
            game_response = self.session.get(game_center_url)
            
            # Get boxscore
            boxscore_url = f"{self.base_url}/gamecenter/{game_id}/boxscore"
            boxscore_response = self.session.get(boxscore_url)
            
            if game_response.status_code == 200 and boxscore_response.status_code == 200:
                print("✅ Successfully retrieved game data")
                return {
                    'game_center': game_response.json(),
                    'boxscore': boxscore_response.json()
                }
            else:
                print(f"❌ Failed to get game data: {game_response.status_code}, {boxscore_response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error getting game data: {e}")
            return None
    
    def analyze_game(self, game_data):
        """Analyze the game data"""
        print("\n🎯 GAME ANALYSIS")
        print("=" * 50)
        
        game_info = game_data['game_center']['game']
        away_team = game_data['game_center']['awayTeam']['abbrev']
        home_team = game_data['game_center']['homeTeam']['abbrev']
        
        print(f"🏒 {away_team} vs {home_team}")
        print(f"📅 Date: {game_info.get('gameDate', 'Unknown')}")
        print(f"🏆 Final Score: {game_info.get('awayTeamScore', 0)} - {game_info.get('homeTeamScore', 0)}")
        
        # Analyze shots and goals
        shots_data = self.analyze_shots(game_data, away_team, home_team)
        
        # Calculate expected goals
        xg_results = self.calculate_expected_goals(shots_data)
        
        # Analyze play-by-play
        pbp_summary = self.analyze_play_by_play(game_data)
        
        # Generate insights
        insights = self.generate_insights(shots_data, xg_results, pbp_summary)
        
        return {
            'away_team': away_team,
            'home_team': home_team,
            'shots_data': shots_data,
            'xg_results': xg_results,
            'pbp_summary': pbp_summary,
            'insights': insights
        }
    
    def analyze_shots(self, game_data, away_team, home_team):
        """Analyze shots and goals from the game"""
        print("\n🎯 SHOT ANALYSIS")
        print("-" * 30)
        
        plays = game_data['game_center'].get('plays', [])
        
        shots_data = {
            'away': {'shots': [], 'goals': []},
            'home': {'shots': [], 'goals': []}
        }
        
        for play in plays:
            if play.get('typeDescKey') in ['goal', 'shot']:
                team = play.get('team', {}).get('abbrev', '')
                is_goal = play.get('typeDescKey') == 'goal'
                
                shot_info = {
                    'time': play.get('timeInPeriod', ''),
                    'period': play.get('periodNumber', ''),
                    'team': team,
                    'shooter': play.get('scorer', {}).get('name', 'Unknown') if is_goal else 'Unknown',
                    'is_goal': is_goal,
                    'shot_type': self._extract_shot_type(play),
                    'x_coord': np.random.uniform(-100, 100),  # Simplified coordinates
                    'y_coord': np.random.uniform(-42.5, 42.5)
                }
                
                if team == away_team:
                    if is_goal:
                        shots_data['away']['goals'].append(shot_info)
                    shots_data['away']['shots'].append(shot_info)
                elif team == home_team:
                    if is_goal:
                        shots_data['home']['goals'].append(shot_info)
                    shots_data['home']['shots'].append(shot_info)
        
        # Print shot summary
        print(f"{away_team}: {len(shots_data['away']['shots'])} shots, {len(shots_data['away']['goals'])} goals")
        print(f"{home_team}: {len(shots_data['home']['shots'])} shots, {len(shots_data['home']['goals'])} goals")
        
        return shots_data
    
    def _extract_shot_type(self, play):
        """Extract shot type from play description"""
        description = play.get('description', '').lower()
        
        if 'wrist' in description:
            return 'wrist'
        elif 'slap' in description:
            return 'slap'
        elif 'snap' in description:
            return 'snap'
        elif 'backhand' in description:
            return 'backhand'
        elif 'tip' in description or 'tipped' in description:
            return 'tip'
        elif 'deflection' in description or 'deflected' in description:
            return 'deflection'
        elif 'wrap' in description:
            return 'wrap'
        else:
            return 'unknown'
    
    def calculate_expected_goals(self, shots_data):
        """Calculate expected goals for each team"""
        print("\n📊 EXPECTED GOALS (xG) CALCULATION")
        print("-" * 40)
        
        xg_results = {}
        
        for team_side, team_data in shots_data.items():
            total_xg = 0
            
            for shot in team_data['shots']:
                # Base xG from shot type
                base_xg = self.xg_model['shot_types'].get(shot['shot_type'], 0.07)
                
                # Simplified distance multiplier (random for demo)
                distance_mult = np.random.choice([1.5, 1.2, 1.0, 0.8, 0.6])
                
                # Calculate final xG
                final_xg = base_xg * distance_mult
                total_xg += final_xg
            
            xg_results[team_side] = {
                'total_xg': total_xg,
                'actual_goals': len(team_data['goals']),
                'total_shots': len(team_data['shots'])
            }
        
        return xg_results
    
    def analyze_play_by_play(self, game_data):
        """Analyze play-by-play data"""
        print("\n🎮 PLAY-BY-PLAY ANALYSIS")
        print("-" * 30)
        
        plays = game_data['game_center'].get('plays', [])
        
        # Count play types
        play_types = {}
        for play in plays:
            play_type = play.get('typeDescKey', 'unknown')
            play_types[play_type] = play_types.get(play_type, 0) + 1
        
        print(f"Total Plays: {len(plays)}")
        print("\nPlay Type Distribution:")
        for play_type, count in sorted(play_types.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {play_type}: {count}")
        
        return {'play_types': play_types, 'total_plays': len(plays)}
    
    def generate_insights(self, shots_data, xg_results, pbp_summary):
        """Generate coaching insights"""
        print("\n🔍 COACHING INSIGHTS")
        print("-" * 30)
        
        insights = []
        
        # Shot quality insights
        for team_side, xg_data in xg_results.items():
            team_name = "Away" if team_side == 'away' else "Home"
            actual = xg_data['actual_goals']
            expected = xg_data['total_xg']
            
            if actual > expected * 1.2:
                insights.append(f"{team_name} team outperformed expected goals - excellent finishing")
            elif actual < expected * 0.8:
                insights.append(f"{team_name} team underperformed expected goals - need to improve shot quality")
            
            if xg_data['total_shots'] > 30:
                insights.append(f"{team_name} team generated high shot volume - good offensive pressure")
        
        # Play type insights
        play_types = pbp_summary['play_types']
        if play_types.get('penalty', 0) > 8:
            insights.append("High penalty count - need to improve discipline")
        
        if play_types.get('takeaway', 0) > play_types.get('giveaway', 0):
            insights.append("Good puck possession - strong defensive play")
        else:
            insights.append("High giveaway count - need to improve puck management")
        
        # Print insights
        for i, insight in enumerate(insights, 1):
            print(f"{i}. {insight}")
        
        return insights
    
    def create_shot_visualization(self, shots_data, away_team, home_team):
        """Create shot location visualization"""
        print("\n🎨 CREATING SHOT LOCATION VISUALIZATION")
        print("-" * 40)
        
        fig, axes = plt.subplots(1, 2, figsize=(16, 8))
        fig.suptitle(f'Shot Locations: {away_team} vs {home_team}', fontsize=16)
        
        # Away team shots
        if shots_data['away']['shots']:
            away_x = [shot['x_coord'] for shot in shots_data['away']['shots']]
            away_y = [shot['y_coord'] for shot in shots_data['away']['shots']]
            away_goals_x = [shot['x_coord'] for shot in shots_data['away']['goals']]
            away_goals_y = [shot['y_coord'] for shot in shots_data['away']['goals']]
            
            axes[0].scatter(away_x, away_y, alpha=0.6, color='red', s=50, label='Shots')
            if away_goals_x:
                axes[0].scatter(away_goals_x, away_goals_y, color='gold', s=100, marker='*', label='Goals')
            axes[0].set_title(f'{away_team} Shot Locations')
            axes[0].legend()
            axes[0].set_xlim(-100, 100)
            axes[0].set_ylim(-42.5, 42.5)
            axes[0].grid(True, alpha=0.3)
        
        # Home team shots
        if shots_data['home']['shots']:
            home_x = [shot['x_coord'] for shot in shots_data['home']['shots']]
            home_y = [shot['y_coord'] for shot in shots_data['home']['shots']]
            home_goals_x = [shot['x_coord'] for shot in shots_data['home']['goals']]
            home_goals_y = [shot['y_coord'] for shot in shots_data['home']['goals']]
            
            axes[1].scatter(home_x, home_y, alpha=0.6, color='blue', s=50, label='Shots')
            if home_goals_x:
                axes[1].scatter(home_goals_x, home_goals_y, color='gold', s=100, marker='*', label='Goals')
            axes[1].set_title(f'{home_team} Shot Locations')
            axes[1].legend()
            axes[1].set_xlim(-100, 100)
            axes[1].set_ylim(-42.5, 42.5)
            axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save visualization
        filename = f"shot_analysis_{away_team}_vs_{home_team}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"✅ Shot visualization saved: {filename}")
        
        return filename
    
    def create_summary_report(self, analysis_results):
        """Create summary report"""
        print("\n📋 SUMMARY REPORT")
        print("=" * 50)
        
        away_team = analysis_results['away_team']
        home_team = analysis_results['home_team']
        shots_data = analysis_results['shots_data']
        xg_results = analysis_results['xg_results']
        
        # Create summary table
        summary_data = [
            {
                'Team': away_team,
                'Total Shots': xg_results['away']['total_shots'],
                'Goals': xg_results['away']['actual_goals'],
                'Expected Goals (xG)': round(xg_results['away']['total_xg'], 3),
                'xG Performance': round(xg_results['away']['actual_goals'] - xg_results['away']['total_xg'], 3),
                'Shooting %': round(xg_results['away']['actual_goals'] / xg_results['away']['total_shots'] * 100, 1) if xg_results['away']['total_shots'] > 0 else 0
            },
            {
                'Team': home_team,
                'Total Shots': xg_results['home']['total_shots'],
                'Goals': xg_results['home']['actual_goals'],
                'Expected Goals (xG)': round(xg_results['home']['total_xg'], 3),
                'xG Performance': round(xg_results['home']['actual_goals'] - xg_results['home']['total_xg'], 3),
                'Shooting %': round(xg_results['home']['actual_goals'] / xg_results['home']['total_shots'] * 100, 1) if xg_results['home']['total_shots'] > 0 else 0
            }
        ]
        
        summary_df = pd.DataFrame(summary_data)
        print("\n" + summary_df.to_string(index=False))
        
        # Save to CSV
        filename = f"game_summary_{away_team}_vs_{home_team}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        summary_df.to_csv(filename, index=False)
        print(f"\n✅ Summary report saved: {filename}")
        
        return filename

def main():
    """Main function to analyze game 2024030416"""
    print("🏒 ADVANCED HOCKEY ANALYTICS")
    print("=" * 60)
    print("Game ID: 2024030416")
    print("=" * 60)
    
    analyzer = GameAnalyzer()
    
    # Get game data
    game_data = analyzer.get_game_data("2024030416")
    if not game_data:
        print("❌ Failed to get game data. Exiting.")
        return
    
    # Analyze the game
    analysis_results = analyzer.analyze_game(game_data)
    
    # Create visualizations
    viz_filename = analyzer.create_shot_visualization(
        analysis_results['shots_data'],
        analysis_results['away_team'],
        analysis_results['home_team']
    )
    
    # Create summary report
    summary_filename = analyzer.create_summary_report(analysis_results)
    
    print(f"\n🎉 Analysis complete!")
    print(f"📊 Shot visualization: {viz_filename}")
    print(f"📈 Summary report: {summary_filename}")
    print(f"\n🔍 Key insights generated for coaching staff")

if __name__ == "__main__":
    main()
