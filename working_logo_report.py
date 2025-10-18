#!/usr/bin/env python3
"""
Working NHL Report Generator with Team Logos and Player Avatars
Handles SVG team logos and PNG player headshots from NHL API
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
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from PIL import Image as PILImage
import cairosvg

class WorkingLogoReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_styles()
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0'})
        
        # xG model coefficients
        self.xg_coefficients = {
            'shot_type': {
                'wrist': 0.08, 'slap': 0.12, 'snap': 0.10, 'backhand': 0.06,
                'tip-in': 0.15, 'deflected': 0.13, 'wrap-around': 0.05, 'default': 0.08
            }
        }
        
        # Situation code meanings
        self.situation_codes = {
            '1551': '5v5',
            '1451': '4v5 (Power Play)',
            '1351': '3v5 (5v3 Power Play)',
            '1541': '5v4 (Penalty Kill)',
            '1441': '4v4',
            '0660': '3v3 (Overtime)'
        }
        
        # Zone codes
        self.zone_codes = {
            'O': 'Offensive Zone',
            'D': 'Defensive Zone', 
            'N': 'Neutral Zone'
        }
    
    def setup_styles(self):
        self.title_style = ParagraphStyle(
            'Title', parent=self.styles['Heading1'],
            fontSize=24, textColor=colors.darkblue,
            alignment=TA_CENTER, spaceAfter=20
        )
        self.subtitle_style = ParagraphStyle(
            'Subtitle', parent=self.styles['Heading2'],
            fontSize=18, textColor=colors.darkblue,
            alignment=TA_CENTER, spaceAfter=15
        )
        self.normal_style = ParagraphStyle(
            'Normal', parent=self.styles['Normal'],
            fontSize=11, textColor=colors.black, spaceAfter=6
        )
    
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
    
    def download_and_convert_image(self, image_url, name, is_svg=False):
        """Download image and convert to proper format for ReportLab"""
        try:
            print(f"Downloading {'SVG' if is_svg else 'PNG'} image for {name}...")
            response = self.session.get(image_url, timeout=10)
            if response.status_code == 200:
                if is_svg:
                    # Convert SVG to PNG using cairosvg
                    try:
                        png_data = cairosvg.svg2png(bytestring=response.content)
                        png_buffer = BytesIO(png_data)
                        print(f"✅ SVG converted to PNG for {name}")
                        return png_buffer
                    except Exception as e:
                        print(f"❌ Error converting SVG for {name}: {e}")
                        return None
                else:
                    # PNG image - convert to ensure compatibility
                    img_buffer = BytesIO(response.content)
                    pil_image = PILImage.open(img_buffer)
                    
                    # Convert to RGB if necessary
                    if pil_image.mode in ('RGBA', 'LA', 'P'):
                        pil_image = pil_image.convert('RGB')
                    
                    # Save as PNG in memory
                    png_buffer = BytesIO()
                    pil_image.save(png_buffer, format='PNG')
                    png_buffer.seek(0)
                    
                    print(f"✅ PNG image processed for {name}")
                    return png_buffer
            else:
                print(f"❌ Failed to download image for {name}: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error downloading image for {name}: {e}")
            return None
    
    def create_player_mapping_with_avatars(self, play_by_play_data):
        """Create player mapping with avatar URLs"""
        player_mapping = {}
        
        if 'rosterSpots' in play_by_play_data:
            roster_spots = play_by_play_data['rosterSpots']
            print(f"Creating player mapping with avatars from {len(roster_spots)} roster spots...")
            
            for spot in roster_spots:
                player_id = spot.get('playerId')
                first_name = spot.get('firstName', {}).get('default', '')
                last_name = spot.get('lastName', {}).get('default', '')
                sweater_number = spot.get('sweaterNumber', '')
                position = spot.get('positionCode', '')
                team_id = spot.get('teamId', '')
                headshot_url = spot.get('headshot', '')
                
                if player_id and first_name and last_name:
                    full_name = f"{first_name} {last_name}"
                    if sweater_number:
                        full_name = f"{full_name} #{sweater_number}"
                    if position:
                        full_name = f"{full_name} ({position})"
                    
                    player_mapping[player_id] = {
                        'name': full_name,
                        'first_name': first_name,
                        'last_name': last_name,
                        'number': sweater_number,
                        'position': position,
                        'team_id': team_id,
                        'headshot_url': headshot_url
                    }
        
        print(f"✅ Created player mapping with avatars for {len(player_mapping)} players")
        return player_mapping
    
    def calculate_advanced_xg(self, shot_data):
        """Calculate advanced Expected Goals with more factors"""
        base_xg = 0.08
        
        # Shot type multiplier
        shot_type = shot_data.get('shotType', 'default').lower()
        type_multiplier = self.xg_coefficients['shot_type'].get(shot_type, 
                                                               self.xg_coefficients['shot_type']['default'])
        
        # Distance and angle calculations
        x_coord = shot_data.get('xCoord', 0)
        y_coord = shot_data.get('yCoord', 0)
        
        # Calculate distance to nearest goal
        goal_x = 89 if x_coord > 0 else -89
        distance = math.sqrt((x_coord - goal_x)**2 + (y_coord - 0)**2)
        
        # Distance effect (exponential decay)
        distance_multiplier = math.exp(-distance / 50)
        
        # Angle effect
        if distance > 0:
            angle = math.degrees(math.asin(abs(y_coord) / distance))
            angle_multiplier = math.cos(math.radians(angle))
        else:
            angle_multiplier = 1.0
        
        # Zone effect
        zone = shot_data.get('zoneCode', 'O')
        zone_multiplier = 1.0
        if zone == 'O':  # Offensive zone
            zone_multiplier = 1.2
        elif zone == 'D':  # Defensive zone
            zone_multiplier = 0.3
        else:  # Neutral zone
            zone_multiplier = 0.8
        
        # Calculate final xG
        xg = base_xg * type_multiplier * distance_multiplier * angle_multiplier * zone_multiplier
        
        return max(0, min(1, xg))
    
    def extract_comprehensive_metrics(self, play_by_play_data, player_mapping):
        """Extract comprehensive metrics from play-by-play data"""
        if not play_by_play_data or 'plays' not in play_by_play_data:
            return None
        
        plays = play_by_play_data['plays']
        print(f"Extracting comprehensive metrics from {len(plays)} plays...")
        
        # Initialize player stats
        player_stats = defaultdict(lambda: {
            # Basic stats
            'goals': 0, 'assists': 0, 'points': 0,
            'shots': 0, 'shots_on_goal': 0, 'missed_shots': 0, 'blocked_shots': 0,
            'hits': 0, 'hits_taken': 0, 'faceoffs_won': 0, 'faceoffs_lost': 0,
            'penalties': 0, 'penalty_minutes': 0, 'giveaways': 0, 'takeaways': 0,
            
            # Advanced stats
            'expected_goals': 0, 'corsi': 0, 'fenwick': 0,
            'high_danger_chances': 0, 'scoring_chances': 0, 'slot_shots': 0,
            'power_play_goals': 0, 'power_play_assists': 0, 'power_play_shots': 0,
            'penalty_kill_goals': 0, 'penalty_kill_assists': 0, 'penalty_kill_shots': 0,
            
            # Detailed tracking
            'shot_locations': [], 'shot_types': [], 'goals_scored': [], 'assists_given': []
        })
        
        # Game-level stats
        game_stats = {
            'total_plays': len(plays),
            'play_types': defaultdict(int),
            'situation_breakdown': defaultdict(int),
            'zone_breakdown': defaultdict(int),
            'period_stats': defaultdict(lambda: {
                'total_plays': 0, 'goals': 0, 'shots': 0, 'penalties': 0,
                'hits': 0, 'faceoffs': 0, 'giveaways': 0, 'takeaways': 0
            }),
            'goals': [], 'shots': [], 'hits': [], 'faceoffs': [], 'penalties': [],
            'giveaways': [], 'takeaways': [], 'scoring_chances': [], 'high_danger_chances': []
        }
        
        # Process each play
        for play in plays:
            play_type = play.get('typeDescKey', '')
            period = play.get('periodDescriptor', {}).get('number', 1)
            time_remaining = play.get('timeRemaining', '20:00')
            situation_code = play.get('situationCode', '1551')
            details = play.get('details', {})
            
            # Update game-level stats
            game_stats['play_types'][play_type] += 1
            game_stats['situation_breakdown'][situation_code] += 1
            game_stats['period_stats'][period]['total_plays'] += 1
            
            # Zone analysis
            zone = details.get('zoneCode', 'N')
            game_stats['zone_breakdown'][zone] += 1
            
            # Goals
            if play_type == 'goal':
                game_stats['goals'].append(play)
                game_stats['period_stats'][period]['goals'] += 1
                
                scoring_player_id = details.get('scoringPlayerId')
                if scoring_player_id:
                    player_stats[scoring_player_id]['goals'] += 1
                    player_stats[scoring_player_id]['goals_scored'].append({
                        'period': period, 'time': time_remaining,
                        'xG': self.calculate_advanced_xg(details),
                        'situation': self.situation_codes.get(situation_code, 'Unknown'),
                        'zone': self.zone_codes.get(zone, 'Unknown')
                    })
                    
                    # Situation-specific goals
                    if '1451' in situation_code or '1351' in situation_code:  # Power play
                        player_stats[scoring_player_id]['power_play_goals'] += 1
                    elif '1541' in situation_code:  # Penalty kill
                        player_stats[scoring_player_id]['penalty_kill_goals'] += 1
                
                # Assists
                for assist_key in ['assist1PlayerId', 'assist2PlayerId']:
                    assist_player_id = details.get(assist_key)
                    if assist_player_id:
                        player_stats[assist_player_id]['assists'] += 1
                        player_stats[assist_player_id]['assists_given'].append({
                            'period': period, 'time': time_remaining,
                            'situation': self.situation_codes.get(situation_code, 'Unknown'),
                            'zone': self.zone_codes.get(zone, 'Unknown')
                        })
                        
                        # Situation-specific assists
                        if '1451' in situation_code or '1351' in situation_code:
                            player_stats[assist_player_id]['power_play_assists'] += 1
                        elif '1541' in situation_code:
                            player_stats[assist_player_id]['penalty_kill_assists'] += 1
            
            # Shots
            elif play_type in ['shot-on-goal', 'missed-shot', 'blocked-shot']:
                game_stats['shots'].append(play)
                game_stats['period_stats'][period]['shots'] += 1
                
                shooting_player_id = details.get('shootingPlayerId')
                if shooting_player_id:
                    player_stats[shooting_player_id]['shots'] += 1
                    player_stats[shooting_player_id]['corsi'] += 1
                    
                    x_coord = details.get('xCoord', 0)
                    y_coord = details.get('yCoord', 0)
                    shot_type = details.get('shotType', 'unknown')
                    
                    player_stats[shooting_player_id]['shot_locations'].append((x_coord, y_coord))
                    player_stats[shooting_player_id]['shot_types'].append(shot_type)
                    
                    # Calculate advanced xG
                    xg = self.calculate_advanced_xg(details)
                    player_stats[shooting_player_id]['expected_goals'] += xg
                    
                    # Calculate distance for shot quality
                    goal_x = 89 if x_coord > 0 else -89
                    distance = math.sqrt((x_coord - goal_x)**2 + (y_coord - 0)**2)
                    
                    # Shot classification
                    if play_type == 'shot-on-goal':
                        player_stats[shooting_player_id]['shots_on_goal'] += 1
                        player_stats[shooting_player_id]['fenwick'] += 1
                        
                        # High-danger chance (close to net, good angle)
                        if distance < 20 and abs(y_coord) < 15:
                            player_stats[shooting_player_id]['high_danger_chances'] += 1
                            game_stats['high_danger_chances'].append(play)
                        
                        # Slot shot (between faceoff dots)
                        if abs(y_coord) < 20 and x_coord > 0:
                            player_stats[shooting_player_id]['slot_shots'] += 1
                        
                        # Scoring chance (close to net)
                        if distance < 25:
                            player_stats[shooting_player_id]['scoring_chances'] += 1
                            game_stats['scoring_chances'].append(play)
                        
                    elif play_type == 'missed-shot':
                        player_stats[shooting_player_id]['missed_shots'] += 1
                        player_stats[shooting_player_id]['fenwick'] += 1
                    elif play_type == 'blocked-shot':
                        player_stats[shooting_player_id]['blocked_shots'] += 1
                    
                    # Situation-specific shots
                    if '1451' in situation_code or '1351' in situation_code:
                        player_stats[shooting_player_id]['power_play_shots'] += 1
                    elif '1541' in situation_code:
                        player_stats[shooting_player_id]['penalty_kill_shots'] += 1
            
            # Hits
            elif play_type == 'hit':
                game_stats['hits'].append(play)
                game_stats['period_stats'][period]['hits'] += 1
                
                hitting_player_id = details.get('hittingPlayerId')
                hittee_player_id = details.get('hitteePlayerId')
                
                if hitting_player_id:
                    player_stats[hitting_player_id]['hits'] += 1
                if hittee_player_id:
                    player_stats[hittee_player_id]['hits_taken'] += 1
            
            # Faceoffs
            elif play_type == 'faceoff':
                game_stats['faceoffs'].append(play)
                game_stats['period_stats'][period]['faceoffs'] += 1
                
                winning_player_id = details.get('winningPlayerId')
                losing_player_id = details.get('losingPlayerId')
                
                if winning_player_id:
                    player_stats[winning_player_id]['faceoffs_won'] += 1
                if losing_player_id:
                    player_stats[losing_player_id]['faceoffs_lost'] += 1
            
            # Penalties
            elif play_type == 'penalty':
                game_stats['penalties'].append(play)
                game_stats['period_stats'][period]['penalties'] += 1
                
                committed_by_player_id = details.get('committedByPlayerId')
                if committed_by_player_id:
                    player_stats[committed_by_player_id]['penalties'] += 1
                    penalty_minutes = details.get('duration', 2)
                    player_stats[committed_by_player_id]['penalty_minutes'] += penalty_minutes
            
            # Giveaways
            elif play_type == 'giveaway':
                game_stats['giveaways'].append(play)
                game_stats['period_stats'][period]['giveaways'] += 1
                
                player_id = details.get('playerId')
                if player_id:
                    player_stats[player_id]['giveaways'] += 1
            
            # Takeaways
            elif play_type == 'takeaway':
                game_stats['takeaways'].append(play)
                game_stats['period_stats'][period]['takeaways'] += 1
                
                player_id = details.get('playerId')
                if player_id:
                    player_stats[player_id]['takeaways'] += 1
        
        # Calculate derived statistics
        for player_id, stats in player_stats.items():
            # Basic derived stats
            stats['points'] = stats['goals'] + stats['assists']
            
            if stats['shots_on_goal'] > 0:
                stats['shooting_percentage'] = (stats['goals'] / stats['shots_on_goal']) * 100
            else:
                stats['shooting_percentage'] = 0
            
            total_faceoffs = stats['faceoffs_won'] + stats['faceoffs_lost']
            if total_faceoffs > 0:
                stats['faceoff_percentage'] = (stats['faceoffs_won'] / total_faceoffs) * 100
            else:
                stats['faceoff_percentage'] = 0
            
            # Advanced derived stats
            stats['xg_difference'] = stats['goals'] - stats['expected_goals']
            
            if stats['giveaways'] + stats['takeaways'] > 0:
                stats['turnover_ratio'] = stats['takeaways'] / (stats['giveaways'] + stats['takeaways'])
            else:
                stats['turnover_ratio'] = 0
            
            # Add player name and avatar info
            if player_id in player_mapping:
                stats['name'] = player_mapping[player_id]['name']
                stats['position'] = player_mapping[player_id]['position']
                stats['team_id'] = player_mapping[player_id]['team_id']
                stats['headshot_url'] = player_mapping[player_id]['headshot_url']
            else:
                stats['name'] = f'Player {player_id}'
                stats['position'] = 'Unknown'
                stats['team_id'] = 'Unknown'
                stats['headshot_url'] = ''
        
        return {
            'game_stats': dict(game_stats),
            'player_stats': dict(player_stats),
            'game_info': play_by_play_data.get('game', {}),
            'away_team': play_by_play_data.get('awayTeam', {}),
            'home_team': play_by_play_data.get('homeTeam', {})
        }
    
    def create_logo_header(self, away_team, home_team):
        """Create header with team logos"""
        try:
            # Download team logos (SVG format)
            away_logo_url = away_team.get('logo', '')
            home_logo_url = home_team.get('logo', '')
            
            away_logo_buffer = None
            home_logo_buffer = None
            
            if away_logo_url:
                away_logo_buffer = self.download_and_convert_image(away_logo_url, away_team.get('abbrev', 'Away'), is_svg=True)
            if home_logo_url:
                home_logo_buffer = self.download_and_convert_image(home_logo_url, home_team.get('abbrev', 'Home'), is_svg=True)
            
            # Create header table with logos
            header_data = []
            
            if away_logo_buffer and home_logo_buffer:
                # Both logos available
                away_logo_img = Image(away_logo_buffer)
                away_logo_img.drawHeight = 1*inch
                away_logo_img.drawWidth = 1*inch
                
                home_logo_img = Image(home_logo_buffer)
                home_logo_img.drawHeight = 1*inch
                home_logo_img.drawWidth = 1*inch
                
                header_data = [
                    [away_logo_img, f"{away_team.get('abbrev', 'Away')} vs {home_team.get('abbrev', 'Home')}", home_logo_img],
                    [f"{away_team.get('commonName', {}).get('default', 'Away Team')}", "NHL Game Report", f"{home_team.get('commonName', {}).get('default', 'Home Team')}"]
                ]
            else:
                # No logos, just text
                header_data = [
                    [f"{away_team.get('abbrev', 'Away')} vs {home_team.get('abbrev', 'Home')}"],
                    [f"{away_team.get('commonName', {}).get('default', 'Away Team')} vs {home_team.get('commonName', {}).get('default', 'Home Team')}"]
                ]
            
            header_table = Table(header_data, colWidths=[2*inch, 4*inch, 2*inch] if away_logo_buffer and home_logo_buffer else [8*inch])
            header_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 18),
                ('FONTSIZE', (0, 1), (-1, 1), 14),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.darkblue),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ]))
            
            return header_table
            
        except Exception as e:
            print(f"Error creating logo header: {e}")
            # Fallback to simple text header
            return Paragraph(f"{away_team.get('abbrev', 'Away')} vs {home_team.get('abbrev', 'Home')}", self.subtitle_style)
    
    def create_comprehensive_metrics_chart(self, analysis_data):
        """Create comprehensive metrics visualization"""
        if not analysis_data:
            return None
        
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 16))
            fig.suptitle('COMPREHENSIVE NHL METRICS DASHBOARD', fontsize=20, fontweight='bold')
            
            game_stats = analysis_data['game_stats']
            player_stats = analysis_data['player_stats']
            
            # 1. Situation breakdown
            situation_breakdown = game_stats['situation_breakdown']
            situation_labels = [self.situation_codes.get(code, code) for code in situation_breakdown.keys()]
            situation_values = list(situation_breakdown.values())
            
            ax1.pie(situation_values, labels=situation_labels, autopct='%1.1f%%', startangle=90)
            ax1.set_title('Game Situation Breakdown', fontsize=14, fontweight='bold')
            
            # 2. Zone breakdown
            zone_breakdown = game_stats['zone_breakdown']
            zone_labels = [self.zone_codes.get(code, code) for code in zone_breakdown.keys()]
            zone_values = list(zone_breakdown.values())
            
            bars = ax2.bar(zone_labels, zone_values, color=['lightblue', 'lightgreen', 'lightcoral'], alpha=0.8)
            ax2.set_title('Zone Distribution', fontsize=14, fontweight='bold')
            ax2.set_ylabel('Number of Plays')
            
            # Add value labels
            for bar, value in zip(bars, zone_values):
                ax2.text(bar.get_x() + bar.get_width()/2., value + 1,
                       f'{value}', ha='center', va='bottom', fontweight='bold')
            
            # 3. Advanced metrics comparison
            top_players = sorted(player_stats.items(), 
                               key=lambda x: x[1].get('points', 0), reverse=True)[:8]
            
            if top_players:
                player_names = [stats['name'] for _, stats in top_players]
                corsi_values = [stats.get('corsi', 0) for _, stats in top_players]
                fenwick_values = [stats.get('fenwick', 0) for _, stats in top_players]
                xg_values = [stats.get('expected_goals', 0) for _, stats in top_players]
                
                x = np.arange(len(player_names))
                width = 0.25
                
                ax3.bar(x - width, corsi_values, width, label='Corsi', color='blue', alpha=0.8)
                ax3.bar(x, fenwick_values, width, label='Fenwick', color='green', alpha=0.8)
                ax3.bar(x + width, xg_values, width, label='Expected Goals', color='orange', alpha=0.8)
                
                ax3.set_xlabel('Players')
                ax3.set_ylabel('Count')
                ax3.set_title('Advanced Metrics Comparison', fontsize=14, fontweight='bold')
                ax3.set_xticks(x)
                ax3.set_xticklabels(player_names, rotation=45, ha='right')
                ax3.legend()
            
            # 4. High-danger chances and scoring chances
            if top_players:
                hdc_values = [stats.get('high_danger_chances', 0) for _, stats in top_players]
                sc_values = [stats.get('scoring_chances', 0) for _, stats in top_players]
                slot_values = [stats.get('slot_shots', 0) for _, stats in top_players]
                
                x = np.arange(len(player_names))
                width = 0.25
                
                ax4.bar(x - width, hdc_values, width, label='High-Danger Chances', color='red', alpha=0.8)
                ax4.bar(x, sc_values, width, label='Scoring Chances', color='purple', alpha=0.8)
                ax4.bar(x + width, slot_values, width, label='Slot Shots', color='gold', alpha=0.8)
                
                ax4.set_xlabel('Players')
                ax4.set_ylabel('Count')
                ax4.set_title('Shot Quality Metrics', fontsize=14, fontweight='bold')
                ax4.set_xticks(x)
                ax4.set_xticklabels(player_names, rotation=45, ha='right')
                ax4.legend()
            
            plt.tight_layout()
            
            # Save to BytesIO
            img_buffer = BytesIO()
            plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
            img_buffer.seek(0)
            plt.close()
            
            return img_buffer
        except Exception as e:
            print(f"Comprehensive metrics chart error: {e}")
            return None
    
    def generate_working_logo_report(self, game_id, output_filename=None):
        """Generate the working report with team logos"""
        print("🏒 GENERATING WORKING NHL REPORT WITH TEAM LOGOS 🏒")
        print("=" * 80)
        
        # Get play-by-play data
        play_by_play_data = self.get_play_by_play_data(game_id)
        
        if not play_by_play_data:
            print("❌ Could not fetch play-by-play data")
            return None
        
        # Create player mapping with avatars
        player_mapping = self.create_player_mapping_with_avatars(play_by_play_data)
        
        # Extract comprehensive metrics
        analysis_data = self.extract_comprehensive_metrics(play_by_play_data, player_mapping)
        
        if not analysis_data:
            print("❌ Could not extract comprehensive metrics")
            return None
        
        # Create output filename
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"working_logo_nhl_report_{game_id}_{timestamp}.pdf"
        
        # Create PDF
        doc = SimpleDocTemplate(output_filename, pagesize=letter)
        story = []
        
        # Title with team logos
        story.append(Paragraph("🏒 WORKING NHL GAME REPORT WITH TEAM LOGOS 🏒", self.title_style))
        story.append(Spacer(1, 10))
        
        # Create header with team logos
        away_team = analysis_data['away_team']
        home_team = analysis_data['home_team']
        logo_header = self.create_logo_header(away_team, home_team)
        story.append(logo_header)
        story.append(Spacer(1, 20))
        
        # Game info
        game_info = analysis_data['game_info']
        story.append(Paragraph(f"Game ID: {game_id}", self.normal_style))
        story.append(Paragraph(f"Date: {game_info.get('gameDate', 'Unknown')}", self.normal_style))
        story.append(Spacer(1, 20))
        
        # Comprehensive metrics summary
        game_stats = analysis_data['game_stats']
        story.append(Paragraph("COMPREHENSIVE METRICS SUMMARY", self.subtitle_style))
        
        # Basic stats
        basic_stats_data = [
            ['Basic Statistics', 'Count'],
            ['Total Plays', game_stats['total_plays']],
            ['Goals', len(game_stats.get('goals', []))],
            ['Shots', len(game_stats.get('shots', []))],
            ['Hits', len(game_stats.get('hits', []))],
            ['Faceoffs', len(game_stats.get('faceoffs', []))],
            ['Penalties', len(game_stats.get('penalties', []))],
            ['Giveaways', len(game_stats.get('giveaways', []))],
            ['Takeaways', len(game_stats.get('takeaways', []))]
        ]
        
        basic_table = Table(basic_stats_data, colWidths=[3*inch, 2*inch])
        basic_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        story.append(basic_table)
        story.append(Spacer(1, 20))
        
        # Add comprehensive metrics chart
        chart_buffer = self.create_comprehensive_metrics_chart(analysis_data)
        if chart_buffer:
            img = Image(chart_buffer)
            img.drawHeight = 8*inch
            img.drawWidth = 10*inch
            story.append(img)
            story.append(Spacer(1, 20))
        
        # Top players with comprehensive metrics
        story.append(Paragraph("TOP PLAYERS - COMPREHENSIVE METRICS", self.subtitle_style))
        
        player_stats = analysis_data['player_stats']
        top_players = sorted(player_stats.items(), 
                           key=lambda x: x[1].get('points', 0), reverse=True)[:10]
        
        comprehensive_player_data = [
            ['Player', 'Pts', 'G', 'A', 'SOG', 'Corsi', 'Fenwick', 'xG', 'HDC', 'SC', 'Slot', 'Hits', 'FO%']
        ]
        
        for player_id, stats in top_players:
            comprehensive_player_data.append([
                stats['name'][:20],  # Truncate long names
                stats.get('points', 0),
                stats.get('goals', 0),
                stats.get('assists', 0),
                stats.get('shots_on_goal', 0),
                stats.get('corsi', 0),
                stats.get('fenwick', 0),
                f"{stats.get('expected_goals', 0):.2f}",
                stats.get('high_danger_chances', 0),
                stats.get('scoring_chances', 0),
                stats.get('slot_shots', 0),
                stats.get('hits', 0),
                f"{stats.get('faceoff_percentage', 0):.1f}%"
            ])
        
        comprehensive_table = Table(comprehensive_player_data, 
                                  colWidths=[2*inch, 0.5*inch, 0.5*inch, 0.5*inch, 0.5*inch, 
                                           0.5*inch, 0.5*inch, 0.5*inch, 0.5*inch, 0.5*inch, 
                                           0.5*inch, 0.5*inch, 0.5*inch])
        comprehensive_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkred),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Left align player names
        ]))
        
        story.append(comprehensive_table)
        story.append(Spacer(1, 20))
        
        # Enhanced features note
        story.append(Paragraph("ENHANCED FEATURES", self.subtitle_style))
        story.append(Paragraph("This working report includes:", self.normal_style))
        story.append(Paragraph("• Team logos (SVG converted to PNG) from NHL API", self.normal_style))
        story.append(Paragraph("• Player avatar URLs (PNG format) available for future enhancement", self.normal_style))
        story.append(Paragraph("• All comprehensive metrics from previous reports", self.normal_style))
        story.append(Paragraph("• Professional layout with visual team branding", self.normal_style))
        story.append(Paragraph("• Based on NHL API Reference: https://github.com/Zmalski/NHL-API-Reference", self.normal_style))
        story.append(Paragraph("• Proper SVG to PNG conversion for ReportLab compatibility", self.normal_style))
        
        # Build PDF
        doc.build(story)
        
        print(f"✅ Working logo NHL report generated: {output_filename}")
        return output_filename

def main():
    """Generate the working logo NHL report"""
    print("🏒 WORKING NHL REPORT GENERATOR WITH TEAM LOGOS 🏒")
    print("=" * 60)
    
    generator = WorkingLogoReportGenerator()
    
    # Use the game ID from your example
    game_id = "2024030242"
    
    print(f"Generating working logo report for game {game_id}...")
    result = generator.generate_working_logo_report(game_id)
    
    if result:
        print(f"🎉 SUCCESS! Working logo NHL report created: {result}")
        print("\nThis working report includes:")
        print("  • Team logos (SVG converted to PNG) from NHL API")
        print("  • Player avatar URLs (PNG format) available for future enhancement")
        print("  • All comprehensive metrics from previous reports")
        print("  • Professional layout with visual team branding")
        print("  • Based on NHL API Reference: https://github.com/Zmalski/NHL-API-Reference")
        print("  • Proper SVG to PNG conversion for ReportLab compatibility")
        print("  • This is the MOST VISUALLY ENHANCED NHL analytics report!")
    else:
        print("❌ Failed to generate working logo report")

if __name__ == "__main__":
    main()
