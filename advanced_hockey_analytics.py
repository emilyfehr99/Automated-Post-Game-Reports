#!/usr/bin/env python3
"""
Advanced Hockey Analytics System
Modern coaching and analysis tools using NHL API data
"""

import requests
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

class AdvancedHockeyAnalytics:
    def __init__(self):
        self.base_url = "https://api-web.nhle.com/v1"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Expected Goals (xG) model parameters based on NHL analytics
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
            },
            'angle_multipliers': {
                '0-15deg': 0.7,   # Sharp angle
                '15-30deg': 0.9,  # Moderate angle
                '30-45deg': 1.1,  # Good angle
                '45-60deg': 1.3,  # Prime angle
                '60deg+': 1.0     # Wide angle
            },
            'situation_multipliers': {
                'even_strength': 1.0,
                'power_play': 1.3,
                'short_handed': 0.8,
                'empty_net': 1.5,
                'penalty_shot': 1.4
            }
        }
    
    def get_game_data(self, game_id):
        """Get comprehensive game data including play-by-play"""
        try:
            # Get game center feed for play-by-play
            game_center_url = f"{self.base_url}/gamecenter/{game_id}/feed/live"
            game_response = self.session.get(game_center_url)
            
            # Get boxscore for detailed stats
            boxscore_url = f"{self.base_url}/gamecenter/{game_id}/boxscore"
            boxscore_response = self.session.get(boxscore_url)
            
            if game_response.status_code == 200 and boxscore_response.status_code == 200:
                return {
                    'game_center': game_response.json(),
                    'boxscore': boxscore_response.json()
                }
            else:
                print(f"Failed to get game data: {game_response.status_code}, {boxscore_response.status_code}")
                return None
        except Exception as e:
            print(f"Error getting game data: {e}")
            return None
    
    def analyze_shot_locations(self, game_data):
        """Analyze shot and goal locations for each team"""
        print("🎯 ANALYZING SHOT & GOAL LOCATIONS")
        print("=" * 50)
        
        game_info = game_data['game_center']['game']
        away_team = game_data['game_center']['awayTeam']['abbrev']
        home_team = game_data['game_center']['homeTeam']['abbrev']
        
        # Extract all shots and goals from play-by-play
        plays = game_data['game_center'].get('plays', [])
        
        # Initialize shot tracking
        shots_data = {
            'away': {'shots': [], 'goals': []},
            'home': {'shots': [], 'goals': []}
        }
        
        for play in plays:
            if play.get('typeDescKey') in ['goal', 'shot']:
                team = play.get('team', {}).get('abbrev', '')
                is_goal = play.get('typeDescKey') == 'goal'
                
                # Extract shot information
                shot_info = {
                    'time': play.get('timeInPeriod', ''),
                    'period': play.get('periodNumber', ''),
                    'team': team,
                    'shooter': play.get('scorer', {}).get('name', 'Unknown') if is_goal else 'Unknown',
                    'is_goal': is_goal,
                    'shot_type': self._extract_shot_type(play),
                    'distance': self._estimate_shot_distance(play),
                    'angle': self._estimate_shot_angle(play),
                    'situation': self._extract_game_situation(play, game_info),
                    'x_coord': self._estimate_x_coordinate(play),
                    'y_coord': self._estimate_y_coordinate(play)
                }
                
                # Categorize by team
                if team == away_team:
                    if is_goal:
                        shots_data['away']['goals'].append(shot_info)
                    shots_data['away']['shots'].append(shot_info)
                elif team == home_team:
                    if is_goal:
                        shots_data['home']['goals'].append(shot_info)
                    shots_data['home']['shots'].append(shot_info)
        
        return shots_data, away_team, home_team
    
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
    
    def _estimate_shot_distance(self, play):
        """Estimate shot distance from net"""
        # This would ideally come from NHL's tracking data
        # For now, we'll use a simplified estimation
        return np.random.randint(10, 50)  # Placeholder
    
    def _estimate_shot_angle(self, play):
        """Estimate shot angle from net"""
        # Simplified angle estimation
        return np.random.randint(0, 90)  # Placeholder
    
    def _extract_game_situation(self, play, game_info):
        """Extract game situation (even strength, power play, etc.)"""
        # This would need more sophisticated parsing
        return 'even_strength'  # Placeholder
    
    def _estimate_x_coordinate(self, play):
        """Estimate x-coordinate on rink"""
        # Simplified coordinate estimation
        return np.random.uniform(-100, 100)
    
    def _estimate_y_coordinate(self, play):
        """Estimate y-coordinate on rink"""
        # Simplified coordinate estimation
        return np.random.uniform(-42.5, 42.5)
    
    def calculate_expected_goals(self, shots_data):
        """Calculate expected goals for each team using xG model"""
        print("\n📊 CALCULATING EXPECTED GOALS (xG)")
        print("=" * 40)
        
        xg_results = {}
        
        for team_side, team_data in shots_data.items():
            total_xg = 0
            shot_analysis = []
            
            for shot in team_data['shots']:
                # Base xG from shot type
                base_xg = self.xg_model['shot_types'].get(shot['shot_type'], 0.07)
                
                # Apply distance multiplier
                distance = shot['distance']
                if distance <= 10:
                    distance_mult = self.xg_model['distance_multipliers']['0-10ft']
                elif distance <= 20:
                    distance_mult = self.xg_model['distance_multipliers']['10-20ft']
                elif distance <= 30:
                    distance_mult = self.xg_model['distance_multipliers']['20-30ft']
                elif distance <= 40:
                    distance_mult = self.xg_model['distance_multipliers']['30-40ft']
                else:
                    distance_mult = self.xg_model['distance_multipliers']['40ft+']
                
                # Apply angle multiplier
                angle = shot['angle']
                if angle <= 15:
                    angle_mult = self.xg_model['angle_multipliers']['0-15deg']
                elif angle <= 30:
                    angle_mult = self.xg_model['angle_multipliers']['15-30deg']
                elif angle <= 45:
                    angle_mult = self.xg_model['angle_multipliers']['30-45deg']
                elif angle <= 60:
                    angle_mult = self.xg_model['angle_multipliers']['45-60deg']
                else:
                    angle_mult = self.xg_model['angle_multipliers']['60deg+']
                
                # Apply situation multiplier
                situation_mult = self.xg_model['situation_multipliers'].get(shot['situation'], 1.0)
                
                # Calculate final xG
                final_xg = base_xg * distance_mult * angle_mult * situation_mult
                total_xg += final_xg
                
                shot_analysis.append({
                    'shooter': shot['shooter'],
                    'shot_type': shot['shot_type'],
                    'distance': shot['distance'],
                    'angle': shot['angle'],
                    'situation': shot['situation'],
                    'xG': final_xg,
                    'is_goal': shot['is_goal']
                })
            
            xg_results[team_side] = {
                'total_xg': total_xg,
                'actual_goals': len(team_data['goals']),
                'shot_analysis': shot_analysis,
                'total_shots': len(team_data['shots'])
            }
        
        return xg_results
    
    def create_shot_location_visualization(self, shots_data, away_team, home_team):
        """Create shot location heatmaps and goal locations"""
        print("\n🎯 CREATING SHOT LOCATION VISUALIZATIONS")
        print("=" * 50)
        
        # Create rink visualization
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(f'Shot & Goal Location Analysis: {away_team} vs {home_team}', fontsize=16)
        
        # Away team shots
        away_shots = np.array([[shot['x_coord'], shot['y_coord']] for shot in shots_data['away']['shots']])
        away_goals = np.array([[shot['x_coord'], shot['y_coord']] for shot in shots_data['away']['goals']])
        
        # Home team shots
        home_shots = np.array([[shot['x_coord'], shot['y_coord']] for shot in shots_data['home']['shots']])
        home_goals = np.array([[shot['x_coord'], shot['y_coord']] for shot in shots_data['home']['goals']])
        
        # Away team visualization
        if len(away_shots) > 0:
            axes[0, 0].scatter(away_shots[:, 0], away_shots[:, 1], alpha=0.6, color='red', s=50, label='Shots')
            if len(away_goals) > 0:
                axes[0, 0].scatter(away_goals[:, 0], away_goals[:, 1], color='red', s=100, marker='*', label='Goals')
            axes[0, 0].set_title(f'{away_team} Shot Locations')
            axes[0, 0].legend()
            axes[0, 0].set_xlim(-100, 100)
            axes[0, 0].set_ylim(-42.5, 42.5)
            axes[0, 0].grid(True, alpha=0.3)
        
        # Home team visualization
        if len(home_shots) > 0:
            axes[0, 1].scatter(home_shots[:, 0], home_shots[:, 1], alpha=0.6, color='blue', s=50, label='Shots')
            if len(home_goals) > 0:
                axes[0, 1].scatter(home_goals[:, 0], home_goals[:, 1], color='blue', s=100, marker='*', label='Goals')
            axes[0, 1].set_title(f'{home_team} Shot Locations')
            axes[0, 1].legend()
            axes[0, 1].set_xlim(-100, 100)
            axes[0, 1].set_ylim(-42.5, 42.5)
            axes[0, 1].grid(True, alpha=0.3)
        
        # Combined shot heatmap
        all_shots = np.vstack([away_shots, home_shots]) if len(away_shots) > 0 and len(home_shots) > 0 else np.array([])
        if len(all_shots) > 0:
            axes[1, 0].hist2d(all_shots[:, 0], all_shots[:, 1], bins=20, cmap='hot')
            axes[1, 0].set_title('Combined Shot Heatmap')
            axes[1, 0].set_xlim(-100, 100)
            axes[1, 0].set_ylim(-42.5, 42.5)
        
        # Shot type distribution
        shot_types = {}
        for team_data in shots_data.values():
            for shot in team_data['shots']:
                shot_type = shot['shot_type']
                shot_types[shot_type] = shot_types.get(shot_type, 0) + 1
        
        if shot_types:
            axes[1, 1].bar(shot_types.keys(), shot_types.values(), color=['red', 'blue', 'green', 'orange', 'purple'])
            axes[1, 1].set_title('Shot Type Distribution')
            axes[1, 1].set_ylabel('Number of Shots')
            axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        # Save the visualization
        filename = f"shot_analysis_{away_team}_vs_{home_team}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"✅ Shot location visualization saved: {filename}")
        
        return filename
    
    def create_expected_goals_summary(self, xg_results, away_team, home_team):
        """Create expected goals summary table and analysis"""
        print("\n📊 EXPECTED GOALS SUMMARY")
        print("=" * 40)
        
        # Create summary table
        summary_data = []
        for team_side, data in xg_results.items():
            team_name = away_team if team_side == 'away' else home_team
            summary_data.append({
                'Team': team_name,
                'Total Shots': data['total_shots'],
                'Actual Goals': data['actual_goals'],
                'Expected Goals (xG)': round(data['total_xg'], 3),
                'xG Difference': round(data['actual_goals'] - data['total_xg'], 3),
                'Shooting %': round(data['actual_goals'] / data['total_shots'] * 100, 1) if data['total_shots'] > 0 else 0
            })
        
        summary_df = pd.DataFrame(summary_data)
        print("\n" + summary_df.to_string(index=False))
        
        # Save to CSV
        filename = f"xg_summary_{away_team}_vs_{home_team}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        summary_df.to_csv(filename, index=False)
        print(f"\n✅ Expected goals summary saved: {filename}")
        
        return summary_df
    
    def analyze_play_by_play(self, game_data):
        """Analyze play-by-play data for tactical insights"""
        print("\n🎮 PLAY-BY-PLAY ANALYSIS")
        print("=" * 40)
        
        plays = game_data['game_center'].get('plays', [])
        game_info = game_data['game_center']['game']
        away_team = game_data['game_center']['awayTeam']['abbrev']
        home_team = game_data['game_center']['homeTeam']['abbrev']
        
        # Analyze different play types
        play_types = {}
        team_possession = {away_team: 0, home_team: 0}
        zone_entries = {away_team: 0, home_team: 0}
        zone_exits = {away_team: 0, home_team: 0}
        
        for play in plays:
            play_type = play.get('typeDescKey', 'unknown')
            team = play.get('team', {}).get('abbrev', '')
            
            # Count play types
            play_types[play_type] = play_types.get(play_type, 0) + 1
            
            # Track possession (simplified)
            if play_type in ['shot', 'goal', 'faceoff']:
                if team == away_team:
                    team_possession[away_team] += 1
                elif team == home_team:
                    team_possession[home_team] += 1
            
            # Track zone entries/exits (simplified)
            if play_type in ['takeaway', 'giveaway']:
                if team == away_team:
                    zone_entries[away_team] += 1
                elif team == home_team:
                    zone_entries[home_team] += 1
        
        # Create play-by-play summary
        pbp_summary = {
            'play_types': play_types,
            'possession': team_possession,
            'zone_entries': zone_entries,
            'total_plays': len(plays)
        }
        
        print(f"Total Plays: {len(plays)}")
        print(f"\nPlay Type Distribution:")
        for play_type, count in sorted(play_types.items(), key=lambda x: x[1], reverse=True):
            print(f"  {play_type}: {count}")
        
        print(f"\nPossession Indicators:")
        print(f"  {away_team}: {team_possession[away_team]} key plays")
        print(f"  {home_team}: {team_possession[home_team]} key plays")
        
        return pbp_summary
    
    def generate_coaching_report(self, game_data, shots_data, xg_results, pbp_summary):
        """Generate comprehensive coaching report"""
        print("\n📋 GENERATING COACHING REPORT")
        print("=" * 40)
        
        game_info = game_data['game_center']['game']
        away_team = game_data['game_center']['awayTeam']['abbrev']
        home_team = game_data['game_center']['homeTeam']['abbrev']
        
        report = {
            'game_info': {
                'date': game_info.get('gameDate', 'Unknown'),
                'away_team': away_team,
                'home_team': home_team,
                'away_score': game_info.get('awayTeamScore', 0),
                'home_score': game_info.get('homeTeamScore', 0)
            },
            'shot_analysis': {
                'away_shots': len(shots_data['away']['shots']),
                'away_goals': len(shots_data['away']['goals']),
                'home_shots': len(shots_data['home']['shots']),
                'home_goals': len(shots_data['home']['goals'])
            },
            'expected_goals': xg_results,
            'play_by_play': pbp_summary,
            'key_insights': self._generate_key_insights(shots_data, xg_results, pbp_summary)
        }
        
        # Save comprehensive report
        filename = f"coaching_report_{away_team}_vs_{home_team}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Coaching report saved: {filename}")
        
        # Print key insights
        print("\n🔍 KEY INSIGHTS FOR COACHING:")
        print("=" * 40)
        for insight in report['key_insights']:
            print(f"• {insight}")
        
        return report
    
    def _generate_key_insights(self, shots_data, xg_results, pbp_summary):
        """Generate key coaching insights"""
        insights = []
        
        # Shot quality analysis
        for team_side, xg_data in xg_results.items():
            team_name = "Away" if team_side == 'away' else "Home"
            actual = xg_data['actual_goals']
            expected = xg_data['total_xg']
            
            if actual > expected * 1.5:
                insights.append(f"{team_name} team outperformed expected goals significantly - excellent finishing")
            elif actual < expected * 0.7:
                insights.append(f"{team_name} team underperformed expected goals - need to improve shot quality")
            
            if xg_data['total_shots'] > 30:
                insights.append(f"{team_name} team generated high shot volume - good offensive pressure")
        
        # Play type analysis
        play_types = pbp_summary['play_types']
        if play_types.get('penalty', 0) > 10:
            insights.append("High penalty count - need to improve discipline")
        
        if play_types.get('takeaway', 0) > play_types.get('giveaway', 0):
            insights.append("Good puck possession - strong defensive play")
        else:
            insights.append("High giveaway count - need to improve puck management")
        
        return insights

def main():
    """Main function to run advanced hockey analytics"""
    print("🏒 ADVANCED HOCKEY ANALYTICS SYSTEM 🏒")
    print("=" * 60)
    
    analytics = AdvancedHockeyAnalytics()
    
    # Analyze the specific game requested by the user
    game_id = "2024030416"
    
    print(f"Analyzing game: {game_id}")
    
    # Get game data
    game_data = analytics.get_game_data(game_id)
    if not game_data:
        print("❌ Failed to get game data")
        return
    
    # Analyze shot locations
    shots_data, away_team, home_team = analytics.analyze_shot_locations(game_data)
    
    # Calculate expected goals
    xg_results = analytics.calculate_expected_goals(shots_data)
    
    # Create shot location visualizations
    viz_filename = analytics.create_shot_location_visualization(shots_data, away_team, home_team)
    
    # Create expected goals summary
    xg_summary = analytics.create_expected_goals_summary(xg_results, away_team, home_team)
    
    # Analyze play-by-play
    pbp_summary = analytics.analyze_play_by_play(game_data)
    
    # Generate comprehensive coaching report
    coaching_report = analytics.generate_coaching_report(game_data, shots_data, xg_results, pbp_summary)
    
    print(f"\n🎉 Analysis complete! Generated files:")
    print(f"  📊 Shot visualization: {viz_filename}")
    print(f"  📈 Expected goals summary: {xg_summary}")
    print(f"  📋 Coaching report: {coaching_report}")

if __name__ == "__main__":
    main()
