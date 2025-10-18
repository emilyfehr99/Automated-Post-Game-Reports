#!/usr/bin/env python3
"""
NHL Advanced Analytics and Visualizations
Advanced statistical analysis and visualization components for NHL reports
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import io
from datetime import datetime
import json

class NHLAdvancedAnalytics:
    def __init__(self):
        """Initialize the advanced analytics engine"""
        # Set up matplotlib style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # NHL team colors
        self.team_colors = {
            'EDM': '#FF4C00',  # Orange
            'FLA': '#C8102E',  # Red
            'BOS': '#FFB81C',  # Gold
            'TOR': '#003E7E',  # Blue
            'MTL': '#AF1E2D',  # Red
            'OTT': '#C52032',  # Red
            'BUF': '#002654',  # Blue
            'DET': '#CE1126',  # Red
            'TBL': '#002868',  # Blue
            'CAR': '#CC0000',  # Red
            'WSH': '#C8102E',  # Red
            'PIT': '#000000',  # Black
            'NYR': '#0038A8',  # Blue
            'NYI': '#00539B',  # Blue
            'NJD': '#CE1126',  # Red
            'PHI': '#F74902',  # Orange
            'CBJ': '#002654',  # Blue
            'NSH': '#FFB81C',  # Gold
            'STL': '#002F87',  # Blue
            'MIN': '#154734',  # Green
            'WPG': '#041E42',  # Blue
            'COL': '#6F263D',  # Burgundy
            'ARI': '#8C2633',  # Red
            'VGK': '#B4975A',  # Gold
            'SJS': '#006D75',  # Teal
            'LAK': '#111111',  # Black
            'ANA': '#F47A20',  # Orange
            'CGY': '#C8102E',  # Red
            'VAN': '#001F5C',  # Blue
            'SEA': '#001628',  # Navy
            'CHI': '#C8102E',  # Red
            'DAL': '#006847'   # Green
        }
    
    def create_shot_heatmap(self, play_by_play_data: Dict, team_abbrev: str) -> plt.Figure:
        """Create a shot location heatmap for a team"""
        if not play_by_play_data or 'plays' not in play_by_play_data:
            return None
        
        shots = []
        for play in play_by_play_data['plays']:
            if (play.get('typeDescKey') == 'shot-on-goal' and 
                play.get('team', {}).get('abbrev') == team_abbrev):
                
                # Extract coordinates if available
                coords = play.get('coordinates', {})
                if coords and 'x' in coords and 'y' in coords:
                    shots.append({
                        'x': coords['x'],
                        'y': coords['y'],
                        'period': play.get('periodNumber', 1),
                        'time': play.get('timeInPeriod', '0:00')
                    })
        
        if not shots:
            return None
        
        df = pd.DataFrame(shots)
        
        # Create the heatmap
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Create a 2D histogram
        x_bins = np.linspace(-100, 100, 20)
        y_bins = np.linspace(-42.5, 42.5, 15)
        
        hist, xedges, yedges = np.histogram2d(df['x'], df['y'], bins=[x_bins, y_bins])
        
        # Plot the heatmap
        im = ax.imshow(hist.T, extent=[-100, 100, -42.5, 42.5], 
                      origin='lower', cmap='Reds', alpha=0.7)
        
        # Add rink outline
        self._draw_rink_outline(ax)
        
        # Customize the plot
        ax.set_title(f'{team_abbrev} Shot Heatmap', fontsize=16, fontweight='bold')
        ax.set_xlabel('Distance from Center Ice', fontsize=12)
        ax.set_ylabel('Distance from Boards', fontsize=12)
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Number of Shots', fontsize=12)
        
        plt.tight_layout()
        return fig
    
    def create_momentum_chart(self, play_by_play_data: Dict) -> plt.Figure:
        """Create a game momentum chart showing scoring chances over time"""
        if not play_by_play_data or 'plays' not in play_by_play_data:
            return None
        
        # Track momentum events
        momentum_events = []
        current_momentum = {'away': 0, 'home': 0}
        
        for play in play_by_play_data['plays']:
            period = play.get('periodNumber', 1)
            time_str = play.get('timeInPeriod', '0:00')
            
            # Convert time to minutes from start of game
            time_minutes = self._convert_time_to_minutes(period, time_str)
            
            # Determine momentum impact
            momentum_impact = 0
            play_type = play.get('typeDescKey', '')
            
            if play_type == 'goal':
                momentum_impact = 3
            elif play_type == 'shot-on-goal':
                momentum_impact = 1
            elif play_type == 'missed-shot':
                momentum_impact = 0.5
            elif play_type == 'penalty':
                momentum_impact = -1
            elif play_type == 'blocked-shot':
                momentum_impact = -0.5
            
            # Determine team
            team = play.get('team', {}).get('abbrev', '')
            if team:
                if team == play_by_play_data.get('awayTeam', {}).get('abbrev', ''):
                    current_momentum['away'] += momentum_impact
                else:
                    current_momentum['home'] += momentum_impact
            
            momentum_events.append({
                'time': time_minutes,
                'away_momentum': current_momentum['away'],
                'home_momentum': current_momentum['home'],
                'play_type': play_type
            })
        
        if not momentum_events:
            return None
        
        df = pd.DataFrame(momentum_events)
        
        # Create the momentum chart
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Plot momentum lines
        ax.plot(df['time'], df['away_momentum'], 
               label=play_by_play_data.get('awayTeam', {}).get('abbrev', 'Away'),
               linewidth=2, alpha=0.8)
        ax.plot(df['time'], df['home_momentum'], 
               label=play_by_play_data.get('homeTeam', {}).get('abbrev', 'Home'),
               linewidth=2, alpha=0.8)
        
        # Add zero line
        ax.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        
        # Add period separators
        for period in range(1, 4):
            period_time = (period - 1) * 20
            ax.axvline(x=period_time, color='gray', linestyle=':', alpha=0.5)
            ax.text(period_time + 1, ax.get_ylim()[1] * 0.9, f'P{period}', 
                   fontsize=10, alpha=0.7)
        
        # Customize the plot
        ax.set_title('Game Momentum Analysis', fontsize=16, fontweight='bold')
        ax.set_xlabel('Game Time (Minutes)', fontsize=12)
        ax.set_ylabel('Momentum Score', fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def create_player_performance_radar(self, player_data: Dict, comparison_players: List[Dict] = None) -> plt.Figure:
        """Create a radar chart for player performance comparison"""
        if not player_data:
            return None
        
        # Extract key stats
        stats = player_data.get('stats', {})
        categories = ['Goals', 'Assists', 'Points', 'Shots', 'Hits', 'Blocks']
        
        # Normalize stats (this is a simplified approach)
        values = [
            stats.get('goals', 0),
            stats.get('assists', 0),
            stats.get('points', 0),
            stats.get('shots', 0),
            stats.get('hits', 0),
            stats.get('blockedShots', 0)
        ]
        
        # Create radar chart
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        # Calculate angles
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        values += values[:1]  # Complete the circle
        angles += angles[:1]
        
        # Plot the radar
        ax.plot(angles, values, 'o-', linewidth=2, label=player_data.get('name', 'Player'))
        ax.fill(angles, values, alpha=0.25)
        
        # Add category labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        
        # Customize
        ax.set_title(f'{player_data.get("name", "Player")} Performance Radar', 
                    size=16, fontweight='bold', pad=20)
        ax.grid(True)
        
        plt.tight_layout()
        return fig
    
    def create_team_comparison_dashboard(self, team1_data: Dict, team2_data: Dict) -> plt.Figure:
        """Create a comprehensive team comparison dashboard"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Team Comparison Dashboard', fontsize=20, fontweight='bold')
        
        # 1. Goals by Period
        ax1 = axes[0, 0]
        periods = ['1st', '2nd', '3rd', 'OT']
        team1_goals = team1_data.get('goalsByPeriod', [0, 0, 0, 0])
        team2_goals = team2_data.get('goalsByPeriod', [0, 0, 0, 0])
        
        x = np.arange(len(periods))
        width = 0.35
        
        bars1 = ax1.bar(x - width/2, team1_goals, width, 
                       label=team1_data.get('abbrev', 'Team 1'), alpha=0.8)
        bars2 = ax1.bar(x + width/2, team2_goals, width, 
                       label=team2_data.get('abbrev', 'Team 2'), alpha=0.8)
        
        ax1.set_title('Goals by Period')
        ax1.set_xlabel('Period')
        ax1.set_ylabel('Goals')
        ax1.set_xticks(x)
        ax1.set_xticklabels(periods)
        ax1.legend()
        
        # 2. Shots Comparison
        ax2 = axes[0, 1]
        shot_categories = ['Shots on Goal', 'Missed Shots', 'Blocked Shots']
        team1_shots = [
            team1_data.get('shotsOnGoal', 0),
            team1_data.get('missedShots', 0),
            team1_data.get('blockedShots', 0)
        ]
        team2_shots = [
            team2_data.get('shotsOnGoal', 0),
            team2_data.get('missedShots', 0),
            team2_data.get('blockedShots', 0)
        ]
        
        x = np.arange(len(shot_categories))
        bars1 = ax2.bar(x - width/2, team1_shots, width, 
                       label=team1_data.get('abbrev', 'Team 1'), alpha=0.8)
        bars2 = ax2.bar(x + width/2, team2_shots, width, 
                       label=team2_data.get('abbrev', 'Team 2'), alpha=0.8)
        
        ax2.set_title('Shot Attempts Comparison')
        ax2.set_xlabel('Shot Type')
        ax2.set_ylabel('Count')
        ax2.set_xticks(x)
        ax2.set_xticklabels(shot_categories, rotation=45)
        ax2.legend()
        
        # 3. Special Teams
        ax3 = axes[1, 0]
        special_teams = ['Power Play', 'Penalty Kill']
        team1_special = [
            team1_data.get('powerPlayGoals', 0),
            team1_data.get('penaltyKillGoals', 0)
        ]
        team2_special = [
            team2_data.get('powerPlayGoals', 0),
            team2_data.get('penaltyKillGoals', 0)
        ]
        
        x = np.arange(len(special_teams))
        bars1 = ax3.bar(x - width/2, team1_special, width, 
                       label=team1_data.get('abbrev', 'Team 1'), alpha=0.8)
        bars2 = ax3.bar(x + width/2, team2_special, width, 
                       label=team2_data.get('abbrev', 'Team 2'), alpha=0.8)
        
        ax3.set_title('Special Teams Performance')
        ax3.set_xlabel('Special Teams Type')
        ax3.set_ylabel('Goals')
        ax3.set_xticks(x)
        ax3.set_xticklabels(special_teams)
        ax3.legend()
        
        # 4. Physical Play
        ax4 = axes[1, 1]
        physical_stats = ['Hits', 'Faceoff Wins', 'Giveaways', 'Takeaways']
        team1_physical = [
            team1_data.get('hits', 0),
            team1_data.get('faceoffWins', 0),
            team1_data.get('giveaways', 0),
            team1_data.get('takeaways', 0)
        ]
        team2_physical = [
            team2_data.get('hits', 0),
            team2_data.get('faceoffWins', 0),
            team2_data.get('giveaways', 0),
            team2_data.get('takeaways', 0)
        ]
        
        x = np.arange(len(physical_stats))
        bars1 = ax4.bar(x - width/2, team1_physical, width, 
                       label=team1_data.get('abbrev', 'Team 1'), alpha=0.8)
        bars2 = ax4.bar(x + width/2, team2_physical, width, 
                       label=team2_data.get('abbrev', 'Team 2'), alpha=0.8)
        
        ax4.set_title('Physical Play Comparison')
        ax4.set_xlabel('Statistic')
        ax4.set_ylabel('Count')
        ax4.set_xticks(x)
        ax4.set_xticklabels(physical_stats, rotation=45)
        ax4.legend()
        
        plt.tight_layout()
        return fig
    
    def create_goalie_performance_chart(self, goalie_data: Dict) -> plt.Figure:
        """Create a comprehensive goalie performance chart"""
        if not goalie_data:
            return None
        
        stats = goalie_data.get('stats', {})
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle(f'{goalie_data.get("name", "Goalie")} Performance Analysis', 
                    fontsize=16, fontweight='bold')
        
        # 1. Save Percentage by Period
        ax1 = axes[0, 0]
        periods = ['1st', '2nd', '3rd', 'OT']
        save_pcts = [
            stats.get('firstPeriodSavePct', 0),
            stats.get('secondPeriodSavePct', 0),
            stats.get('thirdPeriodSavePct', 0),
            stats.get('overtimeSavePct', 0)
        ]
        
        bars = ax1.bar(periods, save_pcts, color='skyblue', alpha=0.7)
        ax1.set_title('Save Percentage by Period')
        ax1.set_ylabel('Save Percentage')
        ax1.set_ylim(0, 1)
        
        # Add value labels
        for bar, pct in zip(bars, save_pcts):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{pct:.3f}', ha='center', va='bottom')
        
        # 2. Shots Faced vs Saves
        ax2 = axes[0, 1]
        shots_against = stats.get('shotsAgainst', 0)
        saves = stats.get('saves', 0)
        goals_against = stats.get('goalsAgainst', 0)
        
        categories = ['Shots Against', 'Saves', 'Goals Against']
        values = [shots_against, saves, goals_against]
        colors = ['red', 'green', 'orange']
        
        bars = ax2.bar(categories, values, color=colors, alpha=0.7)
        ax2.set_title('Shot Statistics')
        ax2.set_ylabel('Count')
        
        # 3. Time on Ice
        ax3 = axes[1, 0]
        time_on_ice = stats.get('timeOnIce', '0:00')
        # Convert time to minutes for visualization
        time_minutes = self._convert_time_to_minutes(1, time_on_ice)
        
        ax3.pie([time_minutes, 60 - time_minutes], 
               labels=['Time Played', 'Time on Bench'],
               autopct='%1.1f%%', startangle=90)
        ax3.set_title('Time Distribution')
        
        # 4. Performance Summary
        ax4 = axes[1, 1]
        summary_stats = [
            f"Save %: {stats.get('savePercentage', 0):.3f}",
            f"GAA: {stats.get('goalsAgainstAverage', 0):.2f}",
            f"Shots Against: {shots_against}",
            f"Saves: {saves}",
            f"Goals Against: {goals_against}"
        ]
        
        ax4.text(0.1, 0.8, '\n'.join(summary_stats), 
                transform=ax4.transAxes, fontsize=12,
                verticalalignment='top', fontfamily='monospace')
        ax4.set_title('Performance Summary')
        ax4.axis('off')
        
        plt.tight_layout()
        return fig
    
    def create_standings_context_chart(self, standings_data: Dict, team1_abbrev: str, team2_abbrev: str) -> plt.Figure:
        """Create a standings context chart showing where teams rank"""
        if not standings_data or 'standings' not in standings_data:
            return None
        
        standings = standings_data['standings']
        
        # Find the teams in standings
        team1_data = None
        team2_data = None
        
        for division in standings.get('divisions', []):
            for team in division.get('teams', []):
                if team.get('abbrev') == team1_abbrev:
                    team1_data = team
                elif team.get('abbrev') == team2_abbrev:
                    team2_data = team
        
        if not team1_data or not team2_data:
            return None
        
        fig, axes = plt.subplots(1, 2, figsize=(16, 8))
        fig.suptitle('Standings Context', fontsize=16, fontweight='bold')
        
        # 1. Points Comparison
        ax1 = axes[0]
        teams = [team1_abbrev, team2_abbrev]
        points = [team1_data.get('points', 0), team2_data.get('points', 0)]
        wins = [team1_data.get('wins', 0), team2_data.get('wins', 0)]
        
        x = np.arange(len(teams))
        width = 0.35
        
        bars1 = ax1.bar(x - width/2, points, width, label='Points', alpha=0.8)
        bars2 = ax1.bar(x + width/2, wins, width, label='Wins', alpha=0.8)
        
        ax1.set_title('Points and Wins Comparison')
        ax1.set_ylabel('Count')
        ax1.set_xticks(x)
        ax1.set_xticklabels(teams)
        ax1.legend()
        
        # 2. Season Record
        ax2 = axes[1]
        team1_record = f"{team1_data.get('wins', 0)}-{team1_data.get('losses', 0)}-{team1_data.get('otLosses', 0)}"
        team2_record = f"{team2_data.get('wins', 0)}-{team2_data.get('losses', 0)}-{team2_data.get('otLosses', 0)}"
        
        records = [team1_record, team2_record]
        colors = ['lightblue', 'lightcoral']
        
        bars = ax2.bar(teams, [1, 1], color=colors, alpha=0.7)
        ax2.set_title('Season Record (W-L-OTL)')
        ax2.set_ylabel('Record')
        
        # Add record text
        for i, (bar, record) in enumerate(zip(bars, records)):
            ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height()/2,
                    record, ha='center', va='center', fontweight='bold', fontsize=12)
        
        plt.tight_layout()
        return fig
    
    def _draw_rink_outline(self, ax):
        """Draw a basic hockey rink outline"""
        # Rink dimensions (simplified)
        rink_length = 200
        rink_width = 85
        
        # Draw rink outline
        rink = plt.Rectangle((-rink_length/2, -rink_width/2), rink_length, rink_width,
                           fill=False, edgecolor='black', linewidth=2)
        ax.add_patch(rink)
        
        # Draw center line
        ax.axvline(x=0, color='red', linestyle='-', linewidth=2)
        
        # Draw goal lines
        ax.axvline(x=-rink_length/2, color='red', linestyle='-', linewidth=2)
        ax.axvline(x=rink_length/2, color='red', linestyle='-', linewidth=2)
        
        # Draw blue lines
        ax.axvline(x=-rink_length/3, color='blue', linestyle='-', linewidth=1)
        ax.axvline(x=rink_length/3, color='blue', linestyle='-', linewidth=1)
    
    def _convert_time_to_minutes(self, period: int, time_str: str) -> float:
        """Convert period and time string to total minutes from game start"""
        try:
            minutes, seconds = map(int, time_str.split(':'))
            total_minutes = (period - 1) * 20 + (20 - minutes) + (60 - seconds) / 60
            return total_minutes
        except:
            return (period - 1) * 20
    
    def create_interactive_dashboard(self, game_data: Dict) -> go.Figure:
        """Create an interactive Plotly dashboard"""
        # This would create an interactive HTML dashboard
        # For now, we'll create a simple interactive chart
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Goals by Period', 'Shots Comparison', 
                          'Player Performance', 'Game Flow'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "scatter"}, {"type": "scatter"}]]
        )
        
        # Add sample data (would be replaced with real data)
        periods = ['1st', '2nd', '3rd', 'OT']
        away_goals = [1, 2, 0, 1]
        home_goals = [0, 1, 2, 0]
        
        fig.add_trace(
            go.Bar(x=periods, y=away_goals, name='Away Team'),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Bar(x=periods, y=home_goals, name='Home Team'),
            row=1, col=1
        )
        
        fig.update_layout(
            title_text="Interactive NHL Game Dashboard",
            showlegend=True,
            height=800
        )
        
        return fig


# Example usage
if __name__ == "__main__":
    analytics = NHLAdvancedAnalytics()
    print("🏒 NHL Advanced Analytics Engine Ready! 🏒")
    print("Available visualizations:")
    print("- Shot heatmaps")
    print("- Momentum charts")
    print("- Player performance radars")
    print("- Team comparison dashboards")
    print("- Goalie performance analysis")
    print("- Standings context charts")
    print("- Interactive dashboards")
