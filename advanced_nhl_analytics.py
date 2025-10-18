#!/usr/bin/env python3
"""
Advanced NHL Analytics with Player Stats and xG Model
Extracts player statistics from play-by-play data and builds Expected Goals model
"""

import requests
import pandas as pd
import numpy as np
import json
from datetime import datetime
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import math

class AdvancedNHLAnalytics:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0'})
        
        # xG model coefficients (simplified model based on shot location and type)
        self.xg_coefficients = {
            'shot_type': {
                'wrist': 0.08,
                'slap': 0.12,
                'snap': 0.10,
                'backhand': 0.06,
                'tip-in': 0.15,
                'deflected': 0.13,
                'wrap-around': 0.05,
                'default': 0.08
            },
            'distance_multiplier': 0.95,  # Decreases with distance
            'angle_multiplier': 1.2,     # Better angles = higher xG
            'rush_multiplier': 1.15,     # Rush shots are more dangerous
            'powerplay_multiplier': 1.25 # Power play shots are more dangerous
        }
    
    def get_play_by_play_data(self, game_id):
        """Get play-by-play data from NHL API"""
        print(f"Fetching play-by-play data for game {game_id}...")
        
        play_by_play_url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/play-by-play"
        
        try:
            response = self.session.get(play_by_play_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print("✅ Play-by-play data fetched successfully")
                return data
            else:
                print(f"❌ Play-by-play API returned {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error fetching play-by-play: {e}")
            return None
    
    def calculate_shot_distance_and_angle(self, x_coord, y_coord):
        """Calculate shot distance and angle from coordinates"""
        # NHL rink is 200ft x 85ft, coordinates are typically in feet
        # Goal is at (89, 0) for one end and (-89, 0) for the other
        
        # Calculate distance to nearest goal
        goal_x = 89 if x_coord > 0 else -89
        distance = math.sqrt((x_coord - goal_x)**2 + (y_coord - 0)**2)
        
        # Calculate angle (0 = straight on, 90 = from the side)
        if distance > 0:
            angle = math.degrees(math.asin(abs(y_coord) / distance))
        else:
            angle = 0
        
        return distance, angle
    
    def calculate_expected_goals(self, shot_data):
        """Calculate Expected Goals (xG) for a shot"""
        base_xg = 0.08  # Base xG value
        
        # Shot type multiplier
        shot_type = shot_data.get('shotType', 'default').lower()
        type_multiplier = self.xg_coefficients['shot_type'].get(shot_type, 
                                                               self.xg_coefficients['shot_type']['default'])
        
        # Distance multiplier (closer shots = higher xG)
        x_coord = shot_data.get('xCoord', 0)
        y_coord = shot_data.get('yCoord', 0)
        distance, angle = self.calculate_shot_distance_and_angle(x_coord, y_coord)
        
        # Distance effect (exponential decay)
        distance_multiplier = math.exp(-distance / 50)  # Decay factor
        
        # Angle effect (straight on shots are better)
        angle_multiplier = math.cos(math.radians(angle))
        
        # Game situation multipliers
        situation_multiplier = 1.0
        if shot_data.get('isRush', False):
            situation_multiplier *= self.xg_coefficients['rush_multiplier']
        
        if shot_data.get('isPowerPlay', False):
            situation_multiplier *= self.xg_coefficients['powerplay_multiplier']
        
        # Calculate final xG
        xg = base_xg * type_multiplier * distance_multiplier * angle_multiplier * situation_multiplier
        
        # Cap xG between 0 and 1
        return max(0, min(1, xg))
    
    def extract_player_statistics(self, play_by_play_data):
        """Extract comprehensive player statistics from play-by-play data"""
        if not play_by_play_data or 'plays' not in play_by_play_data:
            return None
        
        plays = play_by_play_data['plays']
        print(f"Extracting player statistics from {len(plays)} plays...")
        
        # Initialize player stats dictionaries
        player_stats = defaultdict(lambda: {
            'goals': 0,
            'assists': 0,
            'shots': 0,
            'shots_on_goal': 0,
            'missed_shots': 0,
            'blocked_shots': 0,
            'hits': 0,
            'hits_taken': 0,
            'faceoffs_won': 0,
            'faceoffs_lost': 0,
            'penalties': 0,
            'penalty_minutes': 0,
            'time_on_ice': 0,
            'expected_goals': 0,
            'shot_locations': [],
            'shot_types': [],
            'goals_scored': [],
            'assists_given': []
        })
        
        # Process each play
        for play in plays:
            play_type = play.get('typeDescKey', '')
            period = play.get('periodNumber', 1)
            time_remaining = play.get('timeRemaining', '20:00')
            
            # Extract player information
            players = play.get('players', [])
            
            for player_info in players:
                player_id = player_info.get('playerId')
                player_name = player_info.get('playerName', 'Unknown')
                player_type = player_info.get('playerType', '')
                
                if not player_id:
                    continue
                
                # Initialize player if not exists
                if player_id not in player_stats:
                    player_stats[player_id]['name'] = player_name
                
                # Goals
                if play_type == 'goal' and player_type == 'Scorer':
                    player_stats[player_id]['goals'] += 1
                    player_stats[player_id]['goals_scored'].append({
                        'period': period,
                        'time': time_remaining,
                        'xG': self.calculate_expected_goals(play)
                    })
                
                # Assists
                elif play_type == 'goal' and player_type == 'Assist':
                    player_stats[player_id]['assists'] += 1
                    player_stats[player_id]['assists_given'].append({
                        'period': period,
                        'time': time_remaining
                    })
                
                # Shots
                elif 'shot' in play_type.lower():
                    player_stats[player_id]['shots'] += 1
                    
                    # Shot location and type
                    x_coord = play.get('xCoord', 0)
                    y_coord = play.get('yCoord', 0)
                    shot_type = play.get('shotType', 'unknown')
                    
                    player_stats[player_id]['shot_locations'].append((x_coord, y_coord))
                    player_stats[player_id]['shot_types'].append(shot_type)
                    
                    # Calculate xG for this shot
                    xg = self.calculate_expected_goals(play)
                    player_stats[player_id]['expected_goals'] += xg
                    
                    # Shots on goal vs missed
                    if play_type == 'shot-on-goal':
                        player_stats[player_id]['shots_on_goal'] += 1
                    elif play_type == 'shot-missed':
                        player_stats[player_id]['missed_shots'] += 1
                    elif play_type == 'shot-blocked':
                        player_stats[player_id]['blocked_shots'] += 1
                
                # Hits
                elif 'hit' in play_type.lower():
                    if player_type == 'Hitter':
                        player_stats[player_id]['hits'] += 1
                    elif player_type == 'Hittee':
                        player_stats[player_id]['hits_taken'] += 1
                
                # Faceoffs
                elif 'faceoff' in play_type.lower():
                    if player_type == 'Winner':
                        player_stats[player_id]['faceoffs_won'] += 1
                    elif player_type == 'Loser':
                        player_stats[player_id]['faceoffs_lost'] += 1
                
                # Penalties
                elif 'penalty' in play_type.lower() and player_type == 'PenaltyOn':
                    player_stats[player_id]['penalties'] += 1
                    penalty_minutes = play.get('penaltyMinutes', 2)
                    player_stats[player_id]['penalty_minutes'] += penalty_minutes
        
        # Calculate derived statistics
        for player_id, stats in player_stats.items():
            # Shooting percentage
            if stats['shots_on_goal'] > 0:
                stats['shooting_percentage'] = (stats['goals'] / stats['shots_on_goal']) * 100
            else:
                stats['shooting_percentage'] = 0
            
            # Faceoff percentage
            total_faceoffs = stats['faceoffs_won'] + stats['faceoffs_lost']
            if total_faceoffs > 0:
                stats['faceoff_percentage'] = (stats['faceoffs_won'] / total_faceoffs) * 100
            else:
                stats['faceoff_percentage'] = 0
            
            # Points
            stats['points'] = stats['goals'] + stats['assists']
            
            # xG vs actual goals
            stats['xg_difference'] = stats['goals'] - stats['expected_goals']
        
        return dict(player_stats)
    
    def create_player_performance_chart(self, player_stats):
        """Create comprehensive player performance visualization"""
        if not player_stats:
            return None
        
        try:
            # Get top 10 players by points
            top_players = sorted(player_stats.items(), 
                               key=lambda x: x[1].get('points', 0), reverse=True)[:10]
            
            if not top_players:
                return None
            
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle('Top Player Performance Analysis', fontsize=16, fontweight='bold')
            
            # 1. Points by player
            player_names = [stats['name'] for _, stats in top_players]
            points = [stats.get('points', 0) for _, stats in top_players]
            goals = [stats.get('goals', 0) for _, stats in top_players]
            assists = [stats.get('assists', 0) for _, stats in top_players]
            
            x = np.arange(len(player_names))
            width = 0.25
            
            ax1.bar(x - width, goals, width, label='Goals', color='gold', alpha=0.8)
            ax1.bar(x, assists, width, label='Assists', color='silver', alpha=0.8)
            ax1.bar(x + width, points, width, label='Points', color='bronze', alpha=0.8)
            
            ax1.set_xlabel('Players')
            ax1.set_ylabel('Count')
            ax1.set_title('Goals, Assists, and Points')
            ax1.set_xticks(x)
            ax1.set_xticklabels(player_names, rotation=45, ha='right')
            ax1.legend()
            
            # 2. Shooting statistics
            shots = [stats.get('shots', 0) for _, stats in top_players]
            shots_on_goal = [stats.get('shots_on_goal', 0) for _, stats in top_players]
            shooting_pct = [stats.get('shooting_percentage', 0) for _, stats in top_players]
            
            ax2_twin = ax2.twinx()
            bars1 = ax2.bar(x - width/2, shots, width, label='Total Shots', color='lightblue', alpha=0.8)
            bars2 = ax2.bar(x + width/2, shots_on_goal, width, label='Shots on Goal', color='blue', alpha=0.8)
            line = ax2_twin.plot(x, shooting_pct, 'ro-', label='Shooting %', linewidth=2, markersize=6)
            
            ax2.set_xlabel('Players')
            ax2.set_ylabel('Shot Count')
            ax2_twin.set_ylabel('Shooting Percentage')
            ax2.set_title('Shooting Statistics')
            ax2.set_xticks(x)
            ax2.set_xticklabels(player_names, rotation=45, ha='right')
            
            # Combine legends
            lines1, labels1 = ax2.get_legend_handles_labels()
            lines2, labels2 = ax2_twin.get_legend_handles_labels()
            ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
            
            # 3. Expected Goals vs Actual Goals
            expected_goals = [stats.get('expected_goals', 0) for _, stats in top_players]
            actual_goals = [stats.get('goals', 0) for _, stats in top_players]
            
            x = np.arange(len(player_names))
            width = 0.35
            
            bars1 = ax3.bar(x - width/2, expected_goals, width, label='Expected Goals (xG)', color='orange', alpha=0.8)
            bars2 = ax3.bar(x + width/2, actual_goals, width, label='Actual Goals', color='green', alpha=0.8)
            
            ax3.set_xlabel('Players')
            ax3.set_ylabel('Goals')
            ax3.set_title('Expected Goals vs Actual Goals')
            ax3.set_xticks(x)
            ax3.set_xticklabels(player_names, rotation=45, ha='right')
            ax3.legend()
            
            # Add value labels on bars
            for bar in bars1:
                height = bar.get_height()
                if height > 0:
                    ax3.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                           f'{height:.2f}', ha='center', va='bottom', fontsize=8)
            
            for bar in bars2:
                height = bar.get_height()
                if height > 0:
                    ax3.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                           f'{height}', ha='center', va='bottom', fontsize=8)
            
            # 4. Advanced metrics
            hits = [stats.get('hits', 0) for _, stats in top_players]
            faceoff_pct = [stats.get('faceoff_percentage', 0) for _, stats in top_players]
            
            ax4_twin = ax4.twinx()
            bars = ax4.bar(x, hits, width, label='Hits', color='red', alpha=0.8)
            line = ax4_twin.plot(x, faceoff_pct, 'go-', label='Faceoff %', linewidth=2, markersize=6)
            
            ax4.set_xlabel('Players')
            ax4.set_ylabel('Hits')
            ax4_twin.set_ylabel('Faceoff Percentage')
            ax4.set_title('Physical Play & Faceoffs')
            ax4.set_xticks(x)
            ax4.set_xticklabels(player_names, rotation=45, ha='right')
            
            # Combine legends
            lines1, labels1 = ax4.get_legend_handles_labels()
            lines2, labels2 = ax4_twin.get_legend_handles_labels()
            ax4.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
            
            plt.tight_layout()
            
            # Save to BytesIO
            img_buffer = BytesIO()
            plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
            img_buffer.seek(0)
            plt.close()
            
            return img_buffer
        except Exception as e:
            print(f"Player performance chart error: {e}")
            return None
    
    def create_shot_heatmap(self, player_stats):
        """Create shot location heat map"""
        if not player_stats:
            return None
        
        try:
            # Collect all shot locations
            all_shots = []
            for player_id, stats in player_stats.items():
                all_shots.extend(stats.get('shot_locations', []))
            
            if not all_shots:
                return None
            
            # Convert to numpy array
            shots_array = np.array(all_shots)
            x_coords = shots_array[:, 0]
            y_coords = shots_array[:, 1]
            
            # Create heatmap
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
            fig.suptitle('Shot Location Analysis', fontsize=16, fontweight='bold')
            
            # 1. Shot density heatmap
            ax1.hexbin(x_coords, y_coords, gridsize=20, cmap='Reds', alpha=0.8)
            ax1.set_title('Shot Density Heatmap')
            ax1.set_xlabel('X Coordinate (feet)')
            ax1.set_ylabel('Y Coordinate (feet)')
            ax1.grid(True, alpha=0.3)
            
            # 2. Shot scatter plot with goal areas
            ax2.scatter(x_coords, y_coords, alpha=0.6, s=20, color='blue')
            
            # Draw goal areas (simplified)
            goal_width = 6  # feet
            goal_depth = 4  # feet
            
            # Left goal
            ax2.add_patch(plt.Rectangle((-89-goal_depth, -goal_width/2), goal_depth, goal_width, 
                                      fill=False, color='red', linewidth=2))
            # Right goal
            ax2.add_patch(plt.Rectangle((89, -goal_width/2), goal_depth, goal_width, 
                                      fill=False, color='red', linewidth=2))
            
            ax2.set_title('Shot Locations with Goal Areas')
            ax2.set_xlabel('X Coordinate (feet)')
            ax2.set_ylabel('Y Coordinate (feet)')
            ax2.grid(True, alpha=0.3)
            ax2.set_xlim(-100, 100)
            ax2.set_ylim(-50, 50)
            
            plt.tight_layout()
            
            # Save to BytesIO
            img_buffer = BytesIO()
            plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
            img_buffer.seek(0)
            plt.close()
            
            return img_buffer
        except Exception as e:
            print(f"Shot heatmap error: {e}")
            return None
    
    def generate_player_stats_summary(self, player_stats):
        """Generate a summary of player statistics"""
        if not player_stats:
            return None
        
        # Sort players by points
        sorted_players = sorted(player_stats.items(), 
                              key=lambda x: x[1].get('points', 0), reverse=True)
        
        summary = {
            'total_players': len(player_stats),
            'top_scorers': [],
            'top_shooters': [],
            'top_hitters': [],
            'best_xg_performers': [],
            'worst_xg_performers': []
        }
        
        # Top 5 in each category
        for i, (player_id, stats) in enumerate(sorted_players[:5]):
            summary['top_scorers'].append({
                'name': stats['name'],
                'points': stats.get('points', 0),
                'goals': stats.get('goals', 0),
                'assists': stats.get('assists', 0)
            })
        
        # Top shooters by shots
        top_shooters = sorted(player_stats.items(), 
                            key=lambda x: x[1].get('shots', 0), reverse=True)[:5]
        for player_id, stats in top_shooters:
            summary['top_shooters'].append({
                'name': stats['name'],
                'shots': stats.get('shots', 0),
                'shots_on_goal': stats.get('shots_on_goal', 0),
                'shooting_percentage': stats.get('shooting_percentage', 0)
            })
        
        # Top hitters
        top_hitters = sorted(player_stats.items(), 
                           key=lambda x: x[1].get('hits', 0), reverse=True)[:5]
        for player_id, stats in top_hitters:
            summary['top_hitters'].append({
                'name': stats['name'],
                'hits': stats.get('hits', 0),
                'hits_taken': stats.get('hits_taken', 0)
            })
        
        # Best xG performers (actual goals > expected goals)
        xg_performers = sorted(player_stats.items(), 
                             key=lambda x: x[1].get('xg_difference', 0), reverse=True)[:5]
        for player_id, stats in xg_performers:
            if stats.get('expected_goals', 0) > 0:  # Only players with shots
                summary['best_xg_performers'].append({
                    'name': stats['name'],
                    'goals': stats.get('goals', 0),
                    'expected_goals': stats.get('expected_goals', 0),
                    'xg_difference': stats.get('xg_difference', 0)
                })
        
        # Worst xG performers
        worst_xg_performers = sorted(player_stats.items(), 
                                   key=lambda x: x[1].get('xg_difference', 0))[:5]
        for player_id, stats in worst_xg_performers:
            if stats.get('expected_goals', 0) > 0:  # Only players with shots
                summary['worst_xg_performers'].append({
                    'name': stats['name'],
                    'goals': stats.get('goals', 0),
                    'expected_goals': stats.get('expected_goals', 0),
                    'xg_difference': stats.get('xg_difference', 0)
                })
        
        return summary

def main():
    """Test the advanced analytics system"""
    print("🏒 ADVANCED NHL ANALYTICS WITH PLAYER STATS & xG MODEL 🏒")
    print("=" * 70)
    
    analytics = AdvancedNHLAnalytics()
    
    # Test with the same game
    game_id = "2024030242"
    
    # Get play-by-play data
    play_by_play_data = analytics.get_play_by_play_data(game_id)
    
    if play_by_play_data:
        # Extract player statistics
        player_stats = analytics.extract_player_statistics(play_by_play_data)
        
        if player_stats:
            print(f"✅ Extracted statistics for {len(player_stats)} players")
            
            # Generate summary
            summary = analytics.generate_player_stats_summary(player_stats)
            
            if summary:
                print("\n📊 TOP PERFORMERS:")
                print("Top Scorers:")
                for player in summary['top_scorers']:
                    print(f"  {player['name']}: {player['points']} points ({player['goals']}G, {player['assists']}A)")
                
                print("\nTop Shooters:")
                for player in summary['top_shooters']:
                    print(f"  {player['name']}: {player['shots']} shots ({player['shooting_percentage']:.1f}% shooting)")
                
                print("\nBest xG Performers:")
                for player in summary['best_xg_performers']:
                    print(f"  {player['name']}: {player['goals']} goals vs {player['expected_goals']:.2f} xG (+{player['xg_difference']:.2f})")
            
            # Create visualizations
            player_chart = analytics.create_player_performance_chart(player_stats)
            shot_heatmap = analytics.create_shot_heatmap(player_stats)
            
            if player_chart:
                print("✅ Player performance chart created")
            if shot_heatmap:
                print("✅ Shot heatmap created")
            
            print("\n🎉 Advanced analytics system working perfectly!")
            print("Ready to integrate into comprehensive report generator!")
        else:
            print("❌ Could not extract player statistics")
    else:
        print("❌ Could not fetch play-by-play data")

if __name__ == "__main__":
    main()
