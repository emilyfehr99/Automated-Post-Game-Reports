#!/usr/bin/env python3
"""
Team Report Generator - Creates comprehensive PDF reports for NHL teams
"""

from reportlab.lib.pagesizes import letter
from reportlab.platypus import BaseDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageTemplate, Flowable
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors
from pdf_report_generator import PostGameReportGenerator, HeaderFlowable, BackgroundPageTemplate
from nhl_api_client import NHLAPIClient
from advanced_metrics_analyzer import AdvancedMetricsAnalyzer
from collections import defaultdict
import numpy as np
import json
from pathlib import Path
from datetime import datetime
from io import BytesIO
import os
import requests

class TeamReportGenerator(PostGameReportGenerator):
    """Generate comprehensive team reports aggregating data across all games"""
    
    def __init__(self):
        super().__init__()
        self.api = NHLAPIClient()
    
    def get_team_games(self, team_abbrev: str, season_start_date: str = None):
        """Get all games for a team from predictions file"""
        predictions_file = Path('win_probability_predictions_v2.json')
        if not predictions_file.exists():
            return []
        
        with open(predictions_file, 'r') as f:
            data = json.load(f)
        
        team_games = []
        for pred in data.get('predictions', []):
            away = pred.get('away_team', '').upper()
            home = pred.get('home_team', '').upper()
            
            if team_abbrev.upper() in [away, home]:
                actual_winner = (pred.get('actual_winner', '') or '').upper()
                # Only include games that have actually been played (have an actual_winner)
                if actual_winner:
                    is_home = (team_abbrev.upper() == home)
                    # Determine if this team won
                    # actual_winner can be: "HOME", "AWAY", or team abbreviation
                    if actual_winner == 'HOME':
                        won = is_home
                    elif actual_winner == 'AWAY':
                        won = not is_home
                    else:
                        # It's a team abbreviation
                        won = (actual_winner == team_abbrev.upper())
                    
                    # Get win probability for this team
                    if is_home:
                        team_win_prob = pred.get('predicted_home_win_prob', 50.0)
                    else:
                        team_win_prob = pred.get('predicted_away_win_prob', 50.0)
                    
                    # Convert to percentage (it's stored as decimal 0-1)
                    team_win_prob_pct = team_win_prob * 100 if team_win_prob <= 1.0 else team_win_prob
                    
                    game_info = {
                        'game_id': pred.get('game_id'),
                        'date': pred.get('game_date'),
                        'away_team': away,
                        'home_team': home,
                        'was_home': is_home,
                        'won': won,
                        'win_probability': team_win_prob_pct
                    }
                    team_games.append(game_info)
        
        # Sort by date, handling None values
        return sorted(team_games, key=lambda x: x.get('date') or '0000-00-00')
    
    def aggregate_team_stats(self, team_abbrev: str, games: list):
        """Aggregate statistics across all games for a team"""
        aggregated = {
            'games_played': len(games),
            'wins': 0,
            'losses': 0,
            'home_wins': 0,
            'home_losses': 0,
            'away_wins': 0,
            'away_losses': 0,
            'wins_above_expected': 0,  # Count games where win prob < 50% but team won
            'home_wins_above_expected': 0,  # Home wins above expected
            'away_wins_above_expected': 0,  # Away wins above expected
            'period_goals': {'p1': 0, 'p2': 0, 'p3': 0},  # Goals by period
            'period_metrics': {
                'p1': {'shots': [], 'corsi_pct': [], 'pp_goals': [], 'pp_attempts': [], 'pim': [], 
                      'hits': [], 'fo_pct': [], 'blocks': [], 'gv': [], 'tk': [], 'gs': [], 'xg': [],
                      'nzt': [], 'nztsa': [], 'ozs': [], 'nzs': [], 'dzs': [], 'fc': [], 'rush': []},
                'p2': {'shots': [], 'corsi_pct': [], 'pp_goals': [], 'pp_attempts': [], 'pim': [],
                      'hits': [], 'fo_pct': [], 'blocks': [], 'gv': [], 'tk': [], 'gs': [], 'xg': [],
                      'nzt': [], 'nztsa': [], 'ozs': [], 'nzs': [], 'dzs': [], 'fc': [], 'rush': []},
                'p3': {'shots': [], 'corsi_pct': [], 'pp_goals': [], 'pp_attempts': [], 'pim': [],
                      'hits': [], 'fo_pct': [], 'blocks': [], 'gv': [], 'tk': [], 'gs': [], 'xg': [],
                      'nzt': [], 'nztsa': [], 'ozs': [], 'nzs': [], 'dzs': [], 'fc': [], 'rush': []}
            },
            'clutch': {
                'third_period_goals': 0,
                'one_goal_games': 0,
                'one_goal_wins': 0
            },
            
            # Home stats
            'home': {
                'goals_for': [], 'goals_against': [], 'shots_for': [], 'shots_against': [],
                'xG_for': [], 'xG_against': [], 'hdc_for': [], 'hdc_against': [],
                'corsi_pct': [], 'pp_pct': [], 'fo_pct': [], 'lateral': [], 'longitudinal': [],
                'pim': [], 'hits': [], 'blocks': [], 'giveaways': [], 'takeaways': [],
                'gs': [], 'nzt': [], 'nztsa': [], 'ozs': [], 'nzs': [], 'dzs': [], 'fc': [], 'rush': []
            },
            # Away stats
            'away': {
                'goals_for': [], 'goals_against': [], 'shots_for': [], 'shots_against': [],
                'xG_for': [], 'xG_against': [], 'hdc_for': [], 'hdc_against': [],
                'corsi_pct': [], 'pp_pct': [], 'fo_pct': [], 'lateral': [], 'longitudinal': [],
                'pim': [], 'hits': [], 'blocks': [], 'giveaways': [], 'takeaways': [],
                'gs': [], 'nzt': [], 'nztsa': [], 'ozs': [], 'nzs': [], 'dzs': [], 'fc': [], 'rush': []
            },
            # All games (for trends)
            'all_games': [],
            
            # Player stats
            'player_stats': defaultdict(lambda: {
                'name': '', 'position': '', 'games': 0, 'total_gs': 0.0, 'total_xg': 0.0, 'gs_plus_xg': 0.0
            })
        }
        
        for game_info in games:
            game_id = game_info['game_id']
            if not game_id:
                continue
            
            try:
                game_data = self.api.get_comprehensive_game_data(str(game_id))
                if not game_data or 'boxscore' not in game_data:
                    continue
                
                boxscore = game_data['boxscore']
                away_team_data = boxscore.get('awayTeam', {})
                home_team_data = boxscore.get('homeTeam', {})
                
                is_home = game_info['was_home']
                venue_key = 'home' if is_home else 'away'
                
                if is_home:
                    team_data = home_team_data
                    opponent_data = away_team_data
                else:
                    team_data = away_team_data
                    opponent_data = home_team_data
                
                team_id = team_data.get('id')
                
                # Count wins and losses (OT/SO losses count as losses, OT/SO wins count as wins)
                # The actual_winner field already correctly identifies the winner regardless of OT/SO
                if game_info['won']:
                    aggregated['wins'] += 1
                    if is_home:
                        aggregated['home_wins'] += 1
                    else:
                        aggregated['away_wins'] += 1
                    
                    # Count wins above expected: wins where win probability was < 50%
                    win_prob = game_info.get('win_probability', 50.0)
                    if win_prob < 50.0:
                        aggregated['wins_above_expected'] += 1
                        if is_home:
                            aggregated['home_wins_above_expected'] += 1
                        else:
                            aggregated['away_wins_above_expected'] += 1
                else:
                    # Loss includes regulation losses, OT losses, and SO losses
                    aggregated['losses'] += 1
                    if is_home:
                        aggregated['home_losses'] += 1
                    else:
                        aggregated['away_losses'] += 1
                
                # Basic stats
                goals_for = team_data.get('score', 0)
                goals_against = opponent_data.get('score', 0)
                shots_for = team_data.get('sog', 0)
                shots_against = opponent_data.get('sog', 0)
                
                # Calculate goals by period and period-by-period metrics
                if 'play_by_play' in game_data:
                    period_goals, ot_goals, so_goals = self._calculate_goals_by_period(game_data, team_id)
                    aggregated['period_goals']['p1'] += period_goals[0]
                    aggregated['period_goals']['p2'] += period_goals[1]
                    aggregated['period_goals']['p3'] += period_goals[2]
                    
                    # Track third period goals for clutch metric
                    aggregated['clutch']['third_period_goals'] += period_goals[2]
                    
                    # Calculate period-by-period stats
                    period_stats = self._calculate_real_period_stats(game_data, team_id, venue_key)
                    period_gs_xg = self._calculate_period_metrics(game_data, team_id, venue_key)
                    zone_metrics = self._calculate_zone_metrics(game_data, team_id, venue_key)
                    
                    # Store period metrics for each period
                    for period_idx, period_key in enumerate(['p1', 'p2', 'p3']):
                        aggregated['period_metrics'][period_key]['shots'].append(period_stats['shots'][period_idx])
                        aggregated['period_metrics'][period_key]['corsi_pct'].append(period_stats['corsi_pct'][period_idx])
                        aggregated['period_metrics'][period_key]['pp_goals'].append(period_stats['pp_goals'][period_idx])
                        aggregated['period_metrics'][period_key]['pp_attempts'].append(period_stats['pp_attempts'][period_idx])
                        aggregated['period_metrics'][period_key]['pim'].append(period_stats['pim'][period_idx])
                        aggregated['period_metrics'][period_key]['hits'].append(period_stats['hits'][period_idx])
                        aggregated['period_metrics'][period_key]['fo_pct'].append(period_stats['fo_pct'][period_idx])
                        aggregated['period_metrics'][period_key]['blocks'].append(period_stats['bs'][period_idx])
                        aggregated['period_metrics'][period_key]['gv'].append(period_stats['gv'][period_idx])
                        aggregated['period_metrics'][period_key]['tk'].append(period_stats['tk'][period_idx])
                        
                        if period_gs_xg:
                            gs_periods, xg_periods = period_gs_xg
                            aggregated['period_metrics'][period_key]['gs'].append(gs_periods[period_idx])
                            aggregated['period_metrics'][period_key]['xg'].append(xg_periods[period_idx])
                        
                        # Zone metrics
                        aggregated['period_metrics'][period_key]['nzt'].append(zone_metrics['nz_turnovers'][period_idx])
                        aggregated['period_metrics'][period_key]['nztsa'].append(zone_metrics['nz_turnovers_to_shots'][period_idx])
                        aggregated['period_metrics'][period_key]['ozs'].append(zone_metrics['oz_originating_shots'][period_idx])
                        aggregated['period_metrics'][period_key]['nzs'].append(zone_metrics['nz_originating_shots'][period_idx])
                        aggregated['period_metrics'][period_key]['dzs'].append(zone_metrics['dz_originating_shots'][period_idx])
                        aggregated['period_metrics'][period_key]['fc'].append(zone_metrics['fc_cycle_sog'][period_idx])
                        aggregated['period_metrics'][period_key]['rush'].append(zone_metrics['rush_sog'][period_idx])
                
                # Track one-goal games (games decided by 1 goal, excluding empty netters)
                goal_diff = abs(goals_for - goals_against)
                if goal_diff == 1:
                    aggregated['clutch']['one_goal_games'] += 1
                    if game_info['won']:
                        aggregated['clutch']['one_goal_wins'] += 1
                
                aggregated[venue_key]['goals_for'].append(goals_for)
                aggregated[venue_key]['goals_against'].append(goals_against)
                aggregated[venue_key]['shots_for'].append(shots_for)
                aggregated[venue_key]['shots_against'].append(shots_against)
                
                # Advanced metrics
                if 'play_by_play' in game_data:
                    team_xg, opp_xg = self._calculate_xg_from_plays(game_data)
                    team_hdc, opp_hdc = self._calculate_hdc_from_plays(game_data)
                    
                    aggregated[venue_key]['xG_for'].append(team_xg)
                    aggregated[venue_key]['xG_against'].append(opp_xg)
                    aggregated[venue_key]['hdc_for'].append(team_hdc)
                    aggregated[venue_key]['hdc_against'].append(opp_hdc)
                    
                    # Movement metrics
                    analyzer = AdvancedMetricsAnalyzer(game_data.get('play_by_play', {}))
                    movement_metrics = analyzer.calculate_pre_shot_movement_metrics(team_id)
                    
                    lat_avg = movement_metrics['lateral_movement'].get('avg_delta_y', 0.0)
                    long_avg = movement_metrics['longitudinal_movement'].get('avg_delta_x', 0.0)
                    
                    aggregated[venue_key]['lateral'].append(lat_avg)
                    aggregated[venue_key]['longitudinal'].append(long_avg)
                    
                    # Period stats
                    period_stats = self._calculate_real_period_stats(game_data, team_id, venue_key)
                    
                    if period_stats.get('corsi_pct'):
                        aggregated[venue_key]['corsi_pct'].append(np.mean(period_stats['corsi_pct']))
                    
                    pp_goals = sum(period_stats.get('pp_goals', [0]))
                    pp_attempts = sum(period_stats.get('pp_attempts', [0]))
                    if pp_attempts > 0:
                        aggregated[venue_key]['pp_pct'].append((pp_goals / pp_attempts) * 100)
                    
                    fo_wins = sum(period_stats.get('faceoff_wins', [0]))
                    fo_total = sum(period_stats.get('faceoff_total', [0]))
                    if fo_total > 0:
                        aggregated[venue_key]['fo_pct'].append((fo_wins / fo_total) * 100)
                    
                    # Additional metrics for period-by-period table
                    aggregated[venue_key]['pim'].append(sum(period_stats.get('pim', [0])))
                    aggregated[venue_key]['hits'].append(sum(period_stats.get('hits', [0])))
                    aggregated[venue_key]['blocks'].append(sum(period_stats.get('bs', [0])))
                    aggregated[venue_key]['giveaways'].append(sum(period_stats.get('gv', [0])))
                    aggregated[venue_key]['takeaways'].append(sum(period_stats.get('tk', [0])))
                    
                    # Zone metrics
                    zone_metrics = self._calculate_zone_metrics(game_data, team_id, venue_key)
                    aggregated[venue_key]['nzt'].append(sum(zone_metrics.get('nz_turnovers', [0])))
                    aggregated[venue_key]['nztsa'].append(sum(zone_metrics.get('nz_turnovers_to_shots', [0])))
                    aggregated[venue_key]['ozs'].append(sum(zone_metrics.get('oz_originating_shots', [0])))
                    aggregated[venue_key]['nzs'].append(sum(zone_metrics.get('nz_originating_shots', [0])))
                    aggregated[venue_key]['dzs'].append(sum(zone_metrics.get('dz_originating_shots', [0])))
                    aggregated[venue_key]['fc'].append(sum(zone_metrics.get('fc_cycle_sog', [0])))
                    aggregated[venue_key]['rush'].append(sum(zone_metrics.get('rush_sog', [0])))
                    
                    # Game Score from period metrics
                    period_gs_xg = self._calculate_period_metrics(game_data, team_id, venue_key)
                    if period_gs_xg:
                        gs_periods, xg_periods = period_gs_xg
                        aggregated[venue_key]['gs'].append(sum(gs_periods))
                    
                    # Player stats
                    player_stats_dict = self._calculate_player_stats_from_play_by_play(
                        game_data, 'homeTeam' if is_home else 'awayTeam')
                    
                    # Calculate xG for each player
                    player_xg = defaultdict(float)
                    if 'play_by_play' in game_data and 'plays' in game_data['play_by_play']:
                        for play in game_data['play_by_play']['plays']:
                            if play.get('typeDescKey') in ['shot-on-goal', 'goal', 'missed-shot']:
                                details = play.get('details', {})
                                if details.get('eventOwnerTeamId') == team_id:
                                    player_id = details.get('shootingPlayerId')
                                    if player_id:
                                        xg_val = self._calculate_shot_xg(details, play.get('typeDescKey', ''), 
                                                                          play, [])
                                        player_xg[str(player_id)] += xg_val
                    
                    # Aggregate player stats
                    for player_id, stats in player_stats_dict.items():
                        player_name = stats.get('name', f'Player_{player_id}')
                        player_position = stats.get('position', '')
                        gs = stats.get('gameScore', 0.0)
                        xg = player_xg.get(str(player_id), 0.0)
                        
                        aggregated['player_stats'][player_id]['name'] = player_name
                        aggregated['player_stats'][player_id]['position'] = player_position
                        aggregated['player_stats'][player_id]['games'] += 1
                        aggregated['player_stats'][player_id]['total_gs'] += gs
                        aggregated['player_stats'][player_id]['total_xg'] += xg
                        aggregated['player_stats'][player_id]['gs_plus_xg'] += (gs + xg)
                
                # Store for trends
                aggregated['all_games'].append({
                    'date': game_info['date'],
                    'goals_for': goals_for,
                    'goals_against': goals_against,
                    'xG_for': team_xg if 'team_xg' in locals() else 0.0,
                    'xG_against': opp_xg if 'opp_xg' in locals() else 0.0,
                    'shots_for': shots_for,
                    'shots_against': shots_against,
                    'won': game_info['won']
                })
                
            except Exception as e:
                print(f"Error processing game {game_id}: {e}")
                continue
        
        # Calculate averages
        for venue in ['home', 'away']:
            v = aggregated[venue]
            aggregated[f'avg_{venue}_goals_for'] = np.mean(v['goals_for']) if v['goals_for'] else 0.0
            aggregated[f'avg_{venue}_goals_against'] = np.mean(v['goals_against']) if v['goals_against'] else 0.0
            aggregated[f'avg_{venue}_xG_for'] = np.mean(v['xG_for']) if v['xG_for'] else 0.0
            aggregated[f'avg_{venue}_xG_against'] = np.mean(v['xG_against']) if v['xG_against'] else 0.0
            aggregated[f'avg_{venue}_corsi'] = np.mean(v['corsi_pct']) if v['corsi_pct'] else 50.0
            aggregated[f'avg_{venue}_pp'] = np.mean(v['pp_pct']) if v['pp_pct'] else 0.0
            aggregated[f'avg_{venue}_fo'] = np.mean(v['fo_pct']) if v['fo_pct'] else 50.0
            aggregated[f'avg_{venue}_lateral'] = np.mean(v['lateral']) if v['lateral'] else 0.0
            aggregated[f'avg_{venue}_longitudinal'] = np.mean(v['longitudinal']) if v['longitudinal'] else 0.0
            # Keep raw lists for totals (pim, hits, blocks, etc. are summed, not averaged)
        
        aggregated['win_percentage'] = (aggregated['wins'] / aggregated['games_played'] * 100) if aggregated['games_played'] > 0 else 0.0
        home_games = aggregated['home_wins'] + aggregated['home_losses']
        away_games = aggregated['away_wins'] + aggregated['away_losses']
        aggregated['home_win_pct'] = (aggregated['home_wins'] / home_games * 100) if home_games > 0 else 0.0
        aggregated['away_win_pct'] = (aggregated['away_wins'] / away_games * 100) if away_games > 0 else 0.0
        
        return aggregated
    
    def create_header_image(self, team_abbrev: str):
        """Create header image for team report with NHL and team logo, showing full team name"""
        try:
            # Team name mapping
            team_names = {
                'TBL': 'Tampa Bay Lightning', 'NSH': 'Nashville Predators', 'EDM': 'Edmonton Oilers',
                'FLA': 'Florida Panthers', 'COL': 'Colorado Avalanche', 'DAL': 'Dallas Stars',
                'BOS': 'Boston Bruins', 'TOR': 'Toronto Maple Leafs', 'MTL': 'Montreal Canadiens',
                'OTT': 'Ottawa Senators', 'BUF': 'Buffalo Sabres', 'DET': 'Detroit Red Wings',
                'CAR': 'Carolina Hurricanes', 'WSH': 'Washington Capitals', 'PIT': 'Pittsburgh Penguins',
                'NYR': 'New York Rangers', 'NYI': 'New York Islanders', 'NJD': 'New Jersey Devils',
                'PHI': 'Philadelphia Flyers', 'CBJ': 'Columbus Blue Jackets', 'STL': 'St. Louis Blues',
                'MIN': 'Minnesota Wild', 'WPG': 'Winnipeg Jets', 'ARI': 'Arizona Coyotes',
                'VGK': 'Vegas Golden Knights', 'SJS': 'San Jose Sharks', 'LAK': 'Los Angeles Kings',
                'ANA': 'Anaheim Ducks', 'CGY': 'Calgary Flames', 'VAN': 'Vancouver Canucks',
                'SEA': 'Seattle Kraken', 'UTA': 'Utah Hockey Club', 'CHI': 'Chicago Blackhawks'
            }
            
            full_team_name = team_names.get(team_abbrev, team_abbrev)
            
            # Use the parent class method but with custom team name and subtitle
            from PIL import Image as PILImage, ImageDraw, ImageFont
            import os
            import requests
            from io import BytesIO
            
            # Load header image
            script_dir = os.path.dirname(os.path.abspath(__file__))
            header_path = os.path.join(script_dir, "Header.jpg")
            
            if not os.path.exists(header_path):
                return None
            
            header_img = PILImage.open(header_path)
            draw = ImageDraw.Draw(header_img)
            
            # Load fonts
            try:
                font_path = os.path.join(script_dir, 'RussoOne-Regular.ttf')
                if os.path.exists(font_path):
                    font = ImageFont.truetype(font_path, 110)
                    subtitle_font = ImageFont.truetype(font_path, 43)
                else:
                    font = ImageFont.truetype("/Users/emilyfehr8/Library/Fonts/RussoOne-Regular.ttf", 110)
                    subtitle_font = ImageFont.truetype("/Users/emilyfehr8/Library/Fonts/RussoOne-Regular.ttf", 43)
            except:
                try:
                    font = ImageFont.truetype("/Users/emilyfehr8/Library/Fonts/DAGGERSQUARE.otf", 110)
                    subtitle_font = ImageFont.truetype("/Users/emilyfehr8/Library/Fonts/DAGGERSQUARE.otf", 43)
                except:
                    font = ImageFont.load_default()
                    subtitle_font = ImageFont.load_default()
            
            # Draw full team name
            team_text = full_team_name
            team_bbox = draw.textbbox((0, 0), team_text, font=font)
            team_text_width = team_bbox[2] - team_bbox[0]
            team_text_height = team_bbox[3] - team_bbox[1]
            
            team_x = 20 + 233 + 28 + 56
            team_y = (header_img.height - team_text_height) // 2 - 20
            
            # Draw team name with outline
            draw.text((team_x-1, team_y-1), team_text, font=font, fill=(0, 0, 0))
            draw.text((team_x+1, team_y-1), team_text, font=font, fill=(0, 0, 0))
            draw.text((team_x-1, team_y+1), team_text, font=font, fill=(0, 0, 0))
            draw.text((team_x+1, team_y+1), team_text, font=font, fill=(0, 0, 0))
            draw.text((team_x, team_y), team_text, font=font, fill=(255, 255, 255))
            
            # Load team and NHL logos
            logo_abbrev_map = {
                'TBL': 'tb', 'NSH': 'nsh', 'EDM': 'edm', 'FLA': 'fla',
                'COL': 'col', 'DAL': 'dal', 'BOS': 'bos', 'TOR': 'tor',
                'MTL': 'mtl', 'OTT': 'ott', 'BUF': 'buf', 'DET': 'det',
                'CAR': 'car', 'WSH': 'wsh', 'PIT': 'pit', 'NYR': 'nyr',
                'NYI': 'nyi', 'NJD': 'nj', 'PHI': 'phi', 'CBJ': 'cbj',
                'STL': 'stl', 'MIN': 'min', 'WPG': 'wpg', 'ARI': 'ari',
                'VGK': 'vgk', 'SJS': 'sj', 'LAK': 'la', 'ANA': 'ana',
                'CGY': 'cgy', 'VAN': 'van', 'SEA': 'sea', 'CHI': 'chi',
                'UTA': 'utah'
            }
            
            team_logo_abbrev = logo_abbrev_map.get(team_abbrev, team_abbrev.lower())
            team_logo_url = f"https://a.espncdn.com/i/teamlogos/nhl/500/{team_logo_abbrev}.png"
            nhl_logo_url = "https://a.espncdn.com/i/teamlogos/leagues/500/nhl.png"
            
            # Download and paste NHL logo first (moved 6cm left total = 168 points)
            nhl_response = requests.get(nhl_logo_url, timeout=5)
            if nhl_response.status_code == 200:
                nhl_logo = PILImage.open(BytesIO(nhl_response.content))
                nhl_logo = nhl_logo.resize((212, 184), PILImage.Resampling.LANCZOS)
                nhl_logo_x = header_img.width - 601 - 56 - 56 - 56  # Move left 6cm total (168pt)
                nhl_logo_y = team_y + 92 - 28 - 28 - 28 + 14 - 28  # Move up 3.5cm total (98pt)
                header_img.paste(nhl_logo, (nhl_logo_x, nhl_logo_y), nhl_logo)
                print(f"Loaded NHL logo")
            
            # Download and paste team logo - 1cm higher than NHL logo
            team_response = requests.get(team_logo_url, timeout=5)
            if team_response.status_code == 200:
                team_logo = PILImage.open(BytesIO(team_response.content))
                team_logo = team_logo.resize((240, 212), PILImage.Resampling.LANCZOS)
                team_logo_x = header_img.width - 519 - 56  # Original position (2cm left from start)
                team_logo_y = nhl_logo_y - 28  # 1cm higher than NHL logo (28pt)
                header_img.paste(team_logo, (team_logo_x, team_logo_y), team_logo)
                print(f"Loaded team logo: {full_team_name}")
            
            # Draw subtitle: "Team Report | 25/26 Regular Season"
            subtitle_text = "Team Report | 25/26 Regular Season"
            subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
            subtitle_text_width = subtitle_bbox[2] - subtitle_bbox[0]
            subtitle_text_height = subtitle_bbox[3] - subtitle_bbox[1]
            
            subtitle_x = 20 + 233 + 28 + 56
            subtitle_y = team_y + team_text_height + 29
            
            draw.text((subtitle_x, subtitle_y), subtitle_text, font=subtitle_font, fill=(127, 127, 127))
            
            # Draw grey line below subtitle
            line_y = subtitle_y + subtitle_text_height + 42
            line_start_x = subtitle_x
            line_width = subtitle_text_width
            draw.rectangle([line_start_x, line_y, line_start_x + line_width, line_y + 2], fill=(127, 127, 127))
            
            # Save to temporary file (same format as parent class) - use absolute path
            modified_header_path = os.path.join(script_dir, f"temp_header_{team_abbrev}_{os.getpid()}.png")
            header_img.save(modified_header_path)
            
            # Create ReportLab Image object (exactly same as parent class)
            header_image = Image(modified_header_path, width=756, height=180)
            header_image.hAlign = 'CENTER'
            header_image.vAlign = 'TOP'
            
            # Store the temp file path for cleanup
            header_image.temp_path = modified_header_path
            
            return header_image
            
        except Exception as e:
            print(f"Error creating team header: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_team_record_from_standings(self, team_abbrev: str):
        """Get team record from NHL standings API"""
        try:
            url = 'https://api-web.nhle.com/v1/standings/now'
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            print(f"DEBUG: Standings API status code: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"DEBUG: Found {len(data.get('standings', []))} teams in standings")
                for team in data.get('standings', []):
                    team_abbrev_from_api = team.get('teamAbbrev', {}).get('default', '')
                    if team_abbrev_from_api == team_abbrev.upper():
                        record = {
                            'wins': team.get('wins', 0),
                            'losses': team.get('losses', 0),
                            'ot_losses': team.get('otLosses', 0),
                            'total_losses': team.get('losses', 0) + team.get('otLosses', 0),
                            'games_played': team.get('gamesPlayed', 0),
                            'home_wins': team.get('homeWins', 0),
                            'home_losses': team.get('homeLosses', 0),
                            'home_ot_losses': team.get('homeOtLosses', 0),
                            'home_total_losses': team.get('homeLosses', 0) + team.get('homeOtLosses', 0),
                            'home_games_played': team.get('homeGamesPlayed', 0),
                            'away_wins': team.get('roadWins', 0),
                            'away_losses': team.get('roadLosses', 0),
                            'away_ot_losses': team.get('roadOtLosses', 0),
                            'away_total_losses': team.get('roadLosses', 0) + team.get('roadOtLosses', 0),
                            'away_games_played': team.get('roadGamesPlayed', 0),
                        }
                        print(f"DEBUG: Found {team_abbrev} record: {record['wins']}-{record['total_losses']}")
                        return record
                print(f"DEBUG: Team {team_abbrev.upper()} not found in standings")
            else:
                print(f"DEBUG: Standings API returned status {response.status_code}")
        except Exception as e:
            print(f"Error getting standings: {e}")
            import traceback
            traceback.print_exc()
        return None
    
    def create_team_summary_section(self, team_abbrev: str, stats: dict):
        """Create condensed team summary section (simplified since record is now in home/away table)"""
        story = []
        # Summary section is now minimal - record info moved to home/away table header
        # Keep a small spacer for visual spacing
        story.append(Spacer(1, 4))
        return story
    
    def create_home_away_comparison(self, stats: dict, team_abbrev: str):
        """Create home vs away comparison table styled like period-by-period"""
        story = []
        
        # Get team color
        team_colors = {
            'TBL': colors.Color(0/255, 40/255, 104/255), 'NSH': colors.Color(255/255, 184/255, 28/255),
            'EDM': colors.Color(4/255, 30/255, 66/255), 'FLA': colors.Color(200/255, 16/255, 46/255),
            'COL': colors.Color(111/255, 38/255, 61/255), 'DAL': colors.Color(0/255, 99/255, 65/255),
            'BOS': colors.Color(252/255, 181/255, 20/255), 'TOR': colors.Color(0/255, 32/255, 91/255),
            'MTL': colors.Color(175/255, 30/255, 45/255), 'OTT': colors.Color(200/255, 16/255, 46/255),
            'BUF': colors.Color(0/255, 38/255, 84/255), 'DET': colors.Color(206/255, 17/255, 38/255),
            'CAR': colors.Color(226/255, 24/255, 54/255), 'WSH': colors.Color(4/255, 30/255, 66/255),
            'PIT': colors.Color(255/255, 184/255, 28/255), 'NYR': colors.Color(0/255, 56/255, 168/255),
            'NYI': colors.Color(0/255, 83/255, 155/255), 'NJD': colors.Color(206/255, 17/255, 38/255),
            'PHI': colors.Color(247/255, 30/255, 36/255), 'CBJ': colors.Color(0/255, 38/255, 84/255),
            'STL': colors.Color(0/255, 47/255, 108/255), 'MIN': colors.Color(0/255, 99/255, 65/255),
            'WPG': colors.Color(4/255, 30/255, 66/255), 'ARI': colors.Color(140/255, 38/255, 51/255),
            'VGK': colors.Color(185/255, 151/255, 91/255), 'SJS': colors.Color(0/255, 109/255, 117/255),
            'LAK': colors.Color(162/255, 170/255, 173/255), 'ANA': colors.Color(185/255, 151/255, 91/255),
            'CGY': colors.Color(200/255, 16/255, 46/255), 'VAN': colors.Color(0/255, 32/255, 91/255),
            'SEA': colors.Color(0/255, 22/255, 40/255), 'UTA': colors.Color(105/255, 179/255, 231/255),
            'CHI': colors.Color(207/255, 10/255, 44/255)
        }
        team_color = team_colors.get(team_abbrev, colors.grey)
        
        # Get record from standings for the table (needed for Record column)
        standings_record = self.get_team_record_from_standings(team_abbrev)
        
        # Title bar - simple title without record info (record is now in table columns)
        title_data = [["HOME VS AWAY COMPARISON"]]
        title_table = Table(title_data, colWidths=[2.5*inch])
        title_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), team_color),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'RussoOne-Regular'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTWEIGHT', (0, 0), (-1, -1), 'BOLD'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(title_table)
        story.append(Spacer(1, 5))
        
        # Create table similar to period-by-period style
        # Calculate per-game averages (not totals)
        home_games = stats['home_wins'] + stats['home_losses']
        away_games = stats['away_wins'] + stats['away_losses']
        
        home_avg_goals_for = np.mean(stats['home']['goals_for']) if stats['home']['goals_for'] else 0.0
        away_avg_goals_for = np.mean(stats['away']['goals_for']) if stats['away']['goals_for'] else 0.0
        
        home_avg_shots = np.mean(stats['home']['shots_for']) if stats['home']['shots_for'] else 0.0
        away_avg_shots = np.mean(stats['away']['shots_for']) if stats['away']['shots_for'] else 0.0
        
        home_avg_xg = np.mean(stats['home']['xG_for']) if stats['home']['xG_for'] else 0.0
        away_avg_xg = np.mean(stats['away']['xG_for']) if stats['away']['xG_for'] else 0.0
        
        # Calculate per-game averages for all metrics
        home_avg_pim = np.mean(stats['home']['pim']) if stats['home']['pim'] else 0.0
        home_avg_hits = np.mean(stats['home']['hits']) if stats['home']['hits'] else 0.0
        home_avg_blocks = np.mean(stats['home']['blocks']) if stats['home']['blocks'] else 0.0
        home_avg_gv = np.mean(stats['home']['giveaways']) if stats['home']['giveaways'] else 0.0
        home_avg_tk = np.mean(stats['home']['takeaways']) if stats['home']['takeaways'] else 0.0
        home_avg_gs = np.mean(stats['home']['gs']) if stats['home']['gs'] else 0.0
        home_avg_nzt = np.mean(stats['home']['nzt']) if stats['home']['nzt'] else 0.0
        home_avg_nztsa = np.mean(stats['home']['nztsa']) if stats['home']['nztsa'] else 0.0
        home_avg_ozs = np.mean(stats['home']['ozs']) if stats['home']['ozs'] else 0.0
        home_avg_nzs = np.mean(stats['home']['nzs']) if stats['home']['nzs'] else 0.0
        home_avg_dzs = np.mean(stats['home']['dzs']) if stats['home']['dzs'] else 0.0
        home_avg_fc = np.mean(stats['home']['fc']) if stats['home']['fc'] else 0.0
        home_avg_rush = np.mean(stats['home']['rush']) if stats['home']['rush'] else 0.0
        
        away_avg_pim = np.mean(stats['away']['pim']) if stats['away']['pim'] else 0.0
        away_avg_hits = np.mean(stats['away']['hits']) if stats['away']['hits'] else 0.0
        away_avg_blocks = np.mean(stats['away']['blocks']) if stats['away']['blocks'] else 0.0
        away_avg_gv = np.mean(stats['away']['giveaways']) if stats['away']['giveaways'] else 0.0
        away_avg_tk = np.mean(stats['away']['takeaways']) if stats['away']['takeaways'] else 0.0
        away_avg_gs = np.mean(stats['away']['gs']) if stats['away']['gs'] else 0.0
        away_avg_nzt = np.mean(stats['away']['nzt']) if stats['away']['nzt'] else 0.0
        away_avg_nztsa = np.mean(stats['away']['nztsa']) if stats['away']['nztsa'] else 0.0
        away_avg_ozs = np.mean(stats['away']['ozs']) if stats['away']['ozs'] else 0.0
        away_avg_nzs = np.mean(stats['away']['nzs']) if stats['away']['nzs'] else 0.0
        away_avg_dzs = np.mean(stats['away']['dzs']) if stats['away']['dzs'] else 0.0
        away_avg_fc = np.mean(stats['away']['fc']) if stats['away']['fc'] else 0.0
        away_avg_rush = np.mean(stats['away']['rush']) if stats['away']['rush'] else 0.0
        
        # PP format: use average PP% from aggregated stats
        home_pp_pct = stats['avg_home_pp'] if stats.get('avg_home_pp') else 0.0
        away_pp_pct = stats['avg_away_pp'] if stats.get('avg_away_pp') else 0.0
        home_pp_display = f"{home_pp_pct:.1f}%"
        away_pp_display = f"{away_pp_pct:.1f}%"
        
        # Get wins above expected for home and away
        home_wins_ax = stats.get('home_wins_above_expected', 0)
        away_wins_ax = stats.get('away_wins_above_expected', 0)
        
        # Get records for home and away (from standings or stats)
        if standings_record:
            home_wins = standings_record['home_wins']
            home_total_losses = standings_record['home_total_losses']
            away_wins = standings_record['away_wins']
            away_total_losses = standings_record['away_total_losses']
            home_record = f"{home_wins}-{home_total_losses}"
            away_record = f"{away_wins}-{away_total_losses}"
        else:
            home_record = f"{stats['home_wins']}-{stats['home_losses']}"
            away_record = f"{stats['away_wins']}-{stats['away_losses']}"
        
        # Table with all columns plus Record (2nd column) and WinsAX
        comparison_data = [
            # Header row (added Record as 2nd column, WinsAX at end)
            ['Venue', 'Record', 'GF', 'S', 'CF%', 'PP%', 'PIM', 'Hits', 'FO%', 'BLK', 'GV', 'TK', 'GS', 'xG', 'NZT', 'NZTSA', 'OZS', 'NZS', 'DZS', 'FC', 'Rush', 'WinsAX'],
            # Home row
            ['Home', home_record,
             f"{home_avg_goals_for:.1f}", f"{home_avg_shots:.1f}", f"{stats['avg_home_corsi']:.1f}%",
             f"{home_pp_display}", f"{home_avg_pim:.1f}", f"{home_avg_hits:.1f}", 
             f"{stats['avg_home_fo']:.1f}%", f"{home_avg_blocks:.1f}", f"{home_avg_gv:.1f}", f"{home_avg_tk:.1f}", 
             f"{home_avg_gs:.1f}", f"{home_avg_xg:.2f}", f"{home_avg_nzt:.1f}", f"{home_avg_nztsa:.1f}",
             f"{home_avg_ozs:.1f}", f"{home_avg_nzs:.1f}", f"{home_avg_dzs:.1f}", f"{home_avg_fc:.1f}", f"{home_avg_rush:.1f}",
             str(home_wins_ax)],
            # Away row
            ['Away', away_record,
             f"{away_avg_goals_for:.1f}", f"{away_avg_shots:.1f}", f"{stats['avg_away_corsi']:.1f}%",
             f"{away_pp_display}", f"{away_avg_pim:.1f}", f"{away_avg_hits:.1f}",
             f"{stats['avg_away_fo']:.1f}%", f"{away_avg_blocks:.1f}", f"{away_avg_gv:.1f}", f"{away_avg_tk:.1f}",
             f"{away_avg_gs:.1f}", f"{away_avg_xg:.2f}", f"{away_avg_nzt:.1f}", f"{away_avg_nztsa:.1f}",
             f"{away_avg_ozs:.1f}", f"{away_avg_nzs:.1f}", f"{away_avg_dzs:.1f}", f"{away_avg_fc:.1f}", f"{away_avg_rush:.1f}",
             str(away_wins_ax)],
        ]
        
        # Calculate column widths for 22 columns (added Record as 2nd column)
        col_widths = [0.5*inch, 0.4*inch, 0.35*inch, 0.35*inch, 0.4*inch, 0.35*inch, 0.35*inch, 0.35*inch, 
                      0.4*inch, 0.35*inch, 0.35*inch, 0.35*inch, 0.35*inch, 0.4*inch, 0.35*inch, 0.4*inch,
                      0.35*inch, 0.35*inch, 0.35*inch, 0.35*inch, 0.35*inch, 0.4*inch]
        
        table = Table(comparison_data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), team_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'RussoOne-Regular'),
            ('FONTSIZE', (0, 0), (-1, 0), 7),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, 1), colors.beige),
            ('BACKGROUND', (0, 2), (-1, 2), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'RussoOne-Regular'),
            ('FONTSIZE', (0, 1), (-1, -1), 6),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 5))  # Reduced from 10 to move next section up
        
        return story
    
    def create_movement_patterns_visualization(self, stats: dict, team_abbrev: str):
        """Create movement patterns table showing lateral vs longitudinal movement"""
        story = []
        
        # Get team color
        team_colors = {
            'TBL': colors.Color(0/255, 40/255, 104/255), 'NSH': colors.Color(255/255, 184/255, 28/255),
            'EDM': colors.Color(4/255, 30/255, 66/255), 'FLA': colors.Color(200/255, 16/255, 46/255),
            'COL': colors.Color(111/255, 38/255, 61/255), 'DAL': colors.Color(0/255, 99/255, 65/255),
            'BOS': colors.Color(252/255, 181/255, 20/255), 'TOR': colors.Color(0/255, 32/255, 91/255),
            'MTL': colors.Color(175/255, 30/255, 45/255), 'OTT': colors.Color(200/255, 16/255, 46/255),
            'BUF': colors.Color(0/255, 38/255, 84/255), 'DET': colors.Color(206/255, 17/255, 38/255),
            'CAR': colors.Color(226/255, 24/255, 54/255), 'WSH': colors.Color(4/255, 30/255, 66/255),
            'PIT': colors.Color(255/255, 184/255, 28/255), 'NYR': colors.Color(0/255, 56/255, 168/255),
            'NYI': colors.Color(0/255, 83/255, 155/255), 'NJD': colors.Color(206/255, 17/255, 38/255),
            'PHI': colors.Color(247/255, 30/255, 36/255), 'CBJ': colors.Color(0/255, 38/255, 84/255),
            'STL': colors.Color(0/255, 47/255, 108/255), 'MIN': colors.Color(0/255, 99/255, 65/255),
            'WPG': colors.Color(4/255, 30/255, 66/255), 'ARI': colors.Color(140/255, 38/255, 51/255),
            'VGK': colors.Color(185/255, 151/255, 91/255), 'SJS': colors.Color(0/255, 109/255, 117/255),
            'LAK': colors.Color(162/255, 170/255, 173/255), 'ANA': colors.Color(185/255, 151/255, 91/255),
            'CGY': colors.Color(200/255, 16/255, 46/255), 'VAN': colors.Color(0/255, 32/255, 91/255),
            'SEA': colors.Color(0/255, 22/255, 40/255), 'UTA': colors.Color(105/255, 179/255, 231/255),
            'CHI': colors.Color(207/255, 10/255, 44/255)
        }
        team_color = team_colors.get(team_abbrev, colors.grey)
        
        # Collect movement data
        home_lateral = stats['home']['lateral'] if stats['home']['lateral'] else []
        home_longitudinal = stats['home']['longitudinal'] if stats['home']['longitudinal'] else []
        away_lateral = stats['away']['lateral'] if stats['away']['lateral'] else []
        away_longitudinal = stats['away']['longitudinal'] if stats['away']['longitudinal'] else []
        
        # Classify movement into categories
        def classify_lateral(avg_feet):
            if avg_feet == 0:
                return "Stationary"
            elif avg_feet < 10:
                return "Minor"
            elif avg_feet < 20:
                return "Cross-ice"
            elif avg_feet < 35:
                return "Wide-lane"
            else:
                return "Full-width"
        
        def classify_longitudinal(avg_feet):
            if avg_feet == 0:
                return "Stationary"
            elif avg_feet < 15:
                return "Close-range"
            elif avg_feet < 30:
                return "Mid-range"
            elif avg_feet < 50:
                return "Extended"
            else:
                return "Long-range"
        
        # Calculate averages and classify
        home_avg_lat = np.mean(home_lateral) if home_lateral else 0.0
        home_avg_long = np.mean(home_longitudinal) if home_longitudinal else 0.0
        away_avg_lat = np.mean(away_lateral) if away_lateral else 0.0
        away_avg_long = np.mean(away_longitudinal) if away_longitudinal else 0.0
        
        home_lat_cat = classify_lateral(home_avg_lat)
        home_long_cat = classify_longitudinal(home_avg_long)
        away_lat_cat = classify_lateral(away_avg_lat)
        away_long_cat = classify_longitudinal(away_avg_long)
        
        # Title - minimum width to fit text
        title_data = [["MOVEMENT PATTERNS"]]
        title_table = Table(title_data, colWidths=[2.5*inch])
        title_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), team_color),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'RussoOne-Regular'),
            ('FONTWEIGHT', (0, 0), (-1, -1), 'BOLD'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        # Movement patterns table - simplified for regular fans
        # Lateral = Side-to-side puck movement before shots (cross-ice movement creates better shooting angles)
        # Longitudinal = Distance from goal when shots are taken
        movement_data = [
            ['Venue', 'Puck Movement Pre-Shot', 'Shot Distance\nFrom Goal'],
            ['Home', home_lat_cat, home_long_cat],
            ['Away', away_lat_cat, away_long_cat],
        ]
        
        movement_table = Table(movement_data, colWidths=[0.8*inch, 1.3*inch, 1.3*inch])
        movement_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), team_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'RussoOne-Regular'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('BACKGROUND', (0, 1), (-1, 1), colors.beige),
            ('BACKGROUND', (0, 2), (-1, 2), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'RussoOne-Regular'),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ]))
        
        # Wrap title and table in positioning table to shift right by 10cm (8cm + 2cm more)
        # 10cm = 10 * 72 / 2.54 ≈ 283.5 points
        shift_right_cm = 10.0
        shift_right_points = shift_right_cm * 72 / 2.54  # Convert cm to points
        
        # Create a Flowable wrapper that handles both horizontal and vertical positioning
        class CenteredShiftFlowable(Flowable):
            def __init__(self, flowable, target_y_pos, flowable_width, left_position=None, center_vertically=False):
                Flowable.__init__(self)
                self.flowable = flowable
                self.target_y_pos = target_y_pos  # Y position from bottom of page
                self.flowable_width = flowable_width
                self.left_position = left_position  # Explicit left position in points (for horizontal centering)
                self.center_vertically = center_vertically
                self.width = flowable_width
                self.height = flowable.height if hasattr(flowable, 'height') else 0
                
            def wrap(self, availWidth, availHeight):
                # Wrap the flowable to get its actual size
                if hasattr(self.flowable, 'wrap'):
                    w, h = self.flowable.wrap(self.flowable_width, availHeight)
                    self.height = h
                    # Return actual wrapped size but we'll position absolutely
                    return (w, h)
                # Return minimal size if can't wrap
                return (self.flowable_width, self.height if self.height > 0 else 50)
            
            def draw(self):
                self.canv.saveState()
                # Get page dimensions (standard letter size: 8.5 x 11 inch = 612 x 792 points)
                page_height = 792.0
                page_width = 612.0
                
                # Get current Y position from bottom of page using canvas state
                current_y = self.canv._y if hasattr(self.canv, '_y') else 0
                
                # Calculate vertical position
                if self.center_vertically:
                    if hasattr(self.flowable, 'height'):
                        flowable_height = self.flowable.height
                    else:
                        flowable_height = self.height
                    target_y = (page_height - flowable_height) / 2
                    y_translation = target_y - current_y
                else:
                    if current_y is not None and current_y > 0:
                        y_translation = self.target_y_pos - current_y
                    else:
                        y_translation = self.target_y_pos
                
                # Handle horizontal positioning
                if self.left_position is not None:
                    # Get current X position (usually starts at page left margin = 0 for frame with no padding)
                    # We need to position at the specified left_position
                    # Since frame starts at page x=0, we can translate directly
                    x_translation = self.left_position
                else:
                    x_translation = 0
                
                # Sanity checks
                if y_translation > 600:
                    y_translation = 170.0
                elif y_translation < -100:
                    y_translation = 0.0
                
                # Translate both horizontally and vertically
                self.canv.translate(x_translation, y_translation)
                
                # Draw the flowable - need to remove LEFTPADDING if it's a Table since we're positioning it directly
                # Actually, if the flowable is a Table with LEFTPADDING, we should draw it at (0, 0) since we've already translated
                if hasattr(self.flowable, 'drawOn'):
                    # Draw at (0, 0) since we've already translated
                    self.flowable.drawOn(self.canv, 0, 0)
                elif hasattr(self.flowable, 'draw'):
                    self.flowable.draw()
                self.canv.restoreState()
        
        # Center movement patterns on the same center point as player rankings table
        # Player rankings: left at 9cm (moved 1cm left from 10cm), width 3.8 inches
        player_rankings_left = 9 * 72 / 2.54  # 9cm in points (moved 1cm left)
        player_rankings_width = 3.8 * 72  # 3.8 inches in points
        player_rankings_center = player_rankings_left + (player_rankings_width / 2)
        
        # Movement patterns table width
        movement_table_width = sum([0.8, 1.3, 1.3]) * inch  # 3.4 inches = 244.8 points
        title_width = 3.5 * inch  # Title table width = 252 points
        
        # Center both title bar and table on the player rankings center point
        # Title bar centered on player rankings center, then moved right by 2.5cm total (3cm - 0.5cm)
        title_bar_left = player_rankings_center - (title_width / 2) + (2.5 * 72 / 2.54)  # Moved right 2.5cm total
        
        # Movement table also centered on player rankings center, then moved right by 1cm
        movement_table_left = player_rankings_center - (movement_table_width / 2) + (1.0 * 72 / 2.54)  # Moved right 1cm
        
        # Create title wrapper without LEFTPADDING (we'll position it directly in the flowable)
        title_wrapper = Table([[title_table]], colWidths=[title_width])
        title_wrapper.setStyle(TableStyle([
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        # Wrap title - positioned 1 cm above top players table, moved up 5cm more, then down 3cm, then down another 7cm, then down 0.5cm more, then down 1.5cm more
        # Top players table is at ~586.6pt from top (205.4pt from bottom)
        # Title should be 1cm (28.3pt) above that = 558.3pt from top = 233.7pt from bottom
        # Since content appears after period table, estimate current position and shift accordingly
        # Use a fixed shift value that should work: shift up by ~170pt to reach target
        # Adjust: moved up 5cm = 5 * 72 / 2.54 ≈ 141.7 points, then down 3cm = 3 * 72 / 2.54 ≈ 85.0 points
        # Then down another 7cm = 7 * 72 / 2.54 ≈ 198.4 points, then down 0.5cm = 0.5 * 72 / 2.54 ≈ 14.2 points
        # Then down another 1.5cm = 1.5 * 72 / 2.54 ≈ 42.5 points
        title_shift_up_points = 170.0 + 141.7 - 85.0 - 198.4 - 14.2 - 42.5  # Shift: 170pt + 141.7pt (5cm) - 85.0pt (3cm) - 198.4pt (7cm) - 14.2pt (0.5cm) - 42.5pt (1.5cm) = -28.4pt
        title_wrapper_shifted = CenteredShiftFlowable(title_wrapper, title_shift_up_points, title_width, left_position=title_bar_left, center_vertically=False)
        
        # Movement table wrapper - positioned directly, no LEFTPADDING
        movement_wrapper = Table([[movement_table]], colWidths=[movement_table_width])
        movement_wrapper.setStyle(TableStyle([
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        # Movement table - positioned just below title (about 25pt lower for title height)
        # Adjust: moved up 5cm = 5 * 72 / 2.54 ≈ 141.7 points, then down 3cm = 3 * 72 / 2.54 ≈ 85.0 points
        # Then down another 7cm = 7 * 72 / 2.54 ≈ 198.4 points, then down 1.5cm = 1.5 * 72 / 2.54 ≈ 42.5 points
        table_shift_up_points = 145.0 + 141.7 - 85.0 - 198.4 - 42.5  # Shift: 145pt + 141.7pt (5cm) - 85.0pt (3cm) - 198.4pt (7cm) - 42.5pt (1.5cm) = -39.2pt
        movement_wrapper_shifted = CenteredShiftFlowable(movement_wrapper, table_shift_up_points, movement_table_width, left_position=movement_table_left, center_vertically=False)
        
        story.append(title_wrapper_shifted)
        story.append(Spacer(1, 3))
        story.append(movement_wrapper_shifted)
        # Reduced spacer to move section up - parent will handle final spacing
        # Don't add spacer here - let the parent control spacing
        return story
    
    def create_performance_trend_graph(self, stats: dict, team_abbrev: str):
        """Create performance trend graph showing wins, goals, and xG over time"""
        story = []
        
        if not stats['all_games']:
            return story
        
        try:
            import matplotlib.pyplot as plt
            from io import BytesIO
            import matplotlib
            
            # Set transparent background and use Russo One font
            script_dir = os.path.dirname(os.path.abspath(__file__))
            font_path = os.path.join(script_dir, 'RussoOne-Regular.ttf')
            if not os.path.exists(font_path):
                font_path = "/Users/emilyfehr8/Library/Fonts/RussoOne-Regular.ttf"
            
            # Try to load Russo One font for matplotlib
            try:
                if os.path.exists(font_path):
                    from matplotlib.font_manager import FontProperties
                    russo_font = FontProperties(fname=font_path)
                    plt.rcParams['font.family'] = 'sans-serif'
                    # Register the font
                    from matplotlib import font_manager
                    font_manager.fontManager.addfont(font_path)
                    russo_font_prop = FontProperties(fname=font_path)
                else:
                    russo_font_prop = None
            except:
                russo_font_prop = None
            
            games = stats['all_games']
            game_nums = range(1, len(games) + 1)
            
            # Create dual-axis plot with transparent background
            fig, ax1 = plt.subplots(figsize=(6, 3.5))
            fig.patch.set_alpha(0.0)  # Transparent figure background
            ax1.patch.set_alpha(0.0)  # Transparent axes background
            
            # Left axis: Goals and xG
            goals_for = [g['goals_for'] for g in games]
            goals_against = [g['goals_against'] for g in games]
            xg_for = [g['xG_for'] for g in games]
            
            ax1.plot(game_nums, goals_for, label='GF', marker='o', markersize=3, 
                    linewidth=1.5, color='green', alpha=0.7)
            ax1.plot(game_nums, goals_against, label='GA', marker='s', markersize=3,
                    linewidth=1.5, color='red', alpha=0.7)
            ax1.plot(game_nums, xg_for, label='xGF', marker='^', markersize=3,
                    linewidth=1.5, color='blue', linestyle='--', alpha=0.7)
            
            # Add average lines
            avg_gf = np.mean(goals_for)
            avg_ga = np.mean(goals_against)
            ax1.axhline(y=avg_gf, color='green', linestyle=':', alpha=0.5, linewidth=1)
            ax1.axhline(y=avg_ga, color='red', linestyle=':', alpha=0.5, linewidth=1)
            
            # Use Russo One font if available
            if russo_font_prop:
                ax1.set_xlabel('Game Number', fontsize=9, fontweight='bold', fontproperties=russo_font_prop)
                ax1.set_ylabel('Goals / Expected Goals', fontsize=9, fontweight='bold', color='black', fontproperties=russo_font_prop)
                ax1.tick_params(axis='both', labelsize=8)
                ax1.legend(loc='upper left', fontsize=7, prop=russo_font_prop)
                plt.title(f'{team_abbrev} Performance Trends', fontsize=10, fontweight='bold', pad=10, fontproperties=russo_font_prop)
            else:
                ax1.set_xlabel('Game Number', fontsize=9, fontweight='bold')
                ax1.set_ylabel('Goals / Expected Goals', fontsize=9, fontweight='bold', color='black')
                ax1.tick_params(axis='y', labelsize=8)
                ax1.legend(loc='upper left', fontsize=7)
                plt.title(f'{team_abbrev} Performance Trends', fontsize=10, fontweight='bold', pad=10)
            
            ax1.grid(True, alpha=0.3, linestyle='--')
            
            # Right axis: Win/Loss indicator
            ax2 = ax1.twinx()
            ax2.patch.set_alpha(0.0)  # Transparent background
            wins = [1 if g['won'] else 0 for g in games]
            # Create cumulative win percentage
            cumulative_wins = np.cumsum(wins)
            win_pct = [(cumulative_wins[i] / (i + 1)) * 100 for i in range(len(wins))]
            
            ax2.plot(game_nums, win_pct, label='Win %', linewidth=2, color='purple', alpha=0.8)
            ax2.fill_between(game_nums, win_pct, alpha=0.2, color='purple')
            
            if russo_font_prop:
                ax2.set_ylabel('Cumulative Win %', fontsize=9, fontweight='bold', color='purple', fontproperties=russo_font_prop)
                ax2.tick_params(axis='y', labelsize=8, labelcolor='purple')
            else:
                ax2.set_ylabel('Cumulative Win %', fontsize=9, fontweight='bold', color='purple')
                ax2.tick_params(axis='y', labelsize=8, labelcolor='purple')
            ax2.set_ylim([0, 100])
            ax2.axhline(y=50, color='purple', linestyle=':', alpha=0.3, linewidth=1)
            
            plt.tight_layout()
            
            # Save to buffer with transparent background
            img_buffer = BytesIO()
            plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight', 
                       transparent=True, facecolor='none', edgecolor='none')
            img_buffer.seek(0)
            # Store buffer for custom drawing
            img_buffer_copy = BytesIO(img_buffer.read())
            img_buffer.seek(0)
            img = Image(img_buffer)
            img.drawHeight = 2.5*inch
            img.drawWidth = 3.75*inch
            # Store the buffer for later use
            img._buffer_data = img_buffer_copy
            
            # Create a custom Flowable wrapper to align image to left edge of page
            # Page: Letter size = 612 x 792 points (8.5 x 11 inches)
            # Frame: starts at (0, 18) with width 612, height 756, leftPadding=0
            # Content flows within the frame, but we want to draw at absolute page x=0
            class LeftAlignedImage(Flowable):
                def __init__(self, image):
                    Flowable.__init__(self)
                    self.image = image
                    self.width = image.drawWidth
                    self.height = image.drawHeight
                    # Store the image buffer for direct drawing
                    # Image from BytesIO - access the stored buffer
                    from reportlab.lib.utils import ImageReader
                    if hasattr(image, '_buffer_data'):
                        image._buffer_data.seek(0)
                        self.img_reader = ImageReader(image._buffer_data)
                    elif hasattr(image, '_data'):
                        self.img_reader = ImageReader(image._data)
                    elif hasattr(image, 'image'):
                        self.img_reader = ImageReader(image.image)
                    else:
                        # Fallback: try to use image directly (might not work)
                        self.img_reader = image
                
                def wrap(self, availWidth, availHeight):
                    # Return zero size so this doesn't take up any space in document flow
                    # The graph is positioned absolutely, so it shouldn't push other content down
                    return (0, 0)
                
                def draw(self):
                    # Save current canvas state
                    self.canv.saveState()
                    
                    # Get current transform to extract position before modifying
                    # The canvas is at the flow position when draw() is called
                    # We want to maintain Y but shift X to page x=0
                    
                    # Extract current position from transform stack
                    if hasattr(self.canv, '_xformStack') and len(self.canv._xformStack) > 0:
                        # Transform matrix: [a, b, c, d, e, f] where e=x translation, f=y translation
                        transform = self.canv._xformStack[-1]
                        if isinstance(transform, (list, tuple)) and len(transform) >= 6:
                            current_x = transform[4]  # e = x translation
                            current_y = transform[5]  # f = y translation
                        else:
                            # Fallback: estimate
                            current_x = 72  # Assume 1 inch from left
                            current_y = None  # Will maintain current
                    else:
                        current_x = 72  # Default estimate
                        current_y = None
                    
                    # Frame starts at page (0, 18) with leftPadding=0
                    # Content flows within frame starting at frame x=0 = page x=0
                    # To align to absolute page x=0, shift left by current_x
                    # But if frame is truly at x=0, content should already be close
                    # Try shifting by current_x or a fixed amount
                    
                    # Position graph - moved right 2cm more and down 3cm
                    # Now 1cm + 2cm = 3cm from left edge
                    shift_right_cm = 3.0
                    shift_right_points = shift_right_cm * 72 / 2.54  # Convert cm to points
                    shift_left = current_x - shift_right_points  # Shift left to position
                    
                    # Position graph 1 cm above the top players table
                    # Top players table title is approximately at ~586.6pt from top of page
                    # Graph should be 1cm (28.3pt) ABOVE that = ~558.3pt from top = ~233.7pt from bottom
                    # Since canvas translate with positive Y moves content UP,
                    # and content naturally flows from top, we need a large upward shift
                    page_height = 792.0
                    players_table_y_from_top = 586.6  # Estimated position from top
                    graph_target_y_from_top = players_table_y_from_top - 28.3  # 1cm above = 558.3pt from top
                    graph_target_y_from_bottom = page_height - graph_target_y_from_top  # 233.7pt from bottom
                    
                    # The graph now appears earlier in the story (before top players table)
                    # Calculate absolute position: target is 233.7pt from bottom
                    # Get current position and shift to target
                    if current_y is not None:
                        # Current Y is measured from bottom, shift to target
                        shift_up_points = graph_target_y_from_bottom - current_y
                    else:
                        # Graph appears after period table, estimate position
                        # Period table ends around ~370pt from top, so ~422pt from bottom
                        # We need to shift up from ~422pt to 233.7pt = shift up by ~188pt
                        # But we need to account for the fact that graph is positioned earlier now
                        estimated_current_y = 422.0
                        shift_up_points = graph_target_y_from_bottom - estimated_current_y
                    
                    # Debug: ensure we're not positioning off-page
                    # Page height is 792pt, so 233.7pt from bottom should be visible
                    if shift_up_points > 700:
                        # If shift is too large, something's wrong - limit it
                        shift_up_points = 250.0  # Fallback reasonable value
                    
                    # Translate: negative X to shift left, positive Y to shift up
                    self.canv.translate(-shift_left, shift_up_points)
                    
                    # Set transparency/alpha for the image
                    # Use setFillAlpha to make image semi-transparent (0.0 = fully transparent, 1.0 = fully opaque)
                    # Using 0.85 for subtle transparency
                    self.canv.setFillAlpha(0.85)
                    self.canv.setStrokeAlpha(0.85)
                    
                    # Now draw image - it will be at page x=0, shifted up by 3cm
                    # The alpha settings will apply to the image
                    self.canv.drawImage(self.img_reader, 0, 0,
                                       width=self.image.drawWidth,
                                       height=self.image.drawHeight,
                                       mask='auto')  # 'auto' mask helps with transparency
                    
                    # Reset alpha back to fully opaque for subsequent drawing
                    self.canv.setFillAlpha(1.0)
                    self.canv.setStrokeAlpha(1.0)
                    
                    self.canv.restoreState()
            
            # Use custom flowable to align to left edge
            left_aligned_img = LeftAlignedImage(img)
            story.append(left_aligned_img)
            plt.close()
            # Don't add spacer here - let the parent control spacing
            
        except Exception as e:
            print(f"Error creating performance trend: {e}")
            import traceback
            traceback.print_exc()
        
        return story
    
    def create_momentum_wave_chart(self, stats: dict, team_abbrev: str):
        """Create momentum wave chart showing rolling win percentage over time"""
        story = []
        
        if not stats['all_games']:
            return story
        
        try:
            import matplotlib.pyplot as plt
            from io import BytesIO
            
            # Set transparent background and use Russo One font
            script_dir = os.path.dirname(os.path.abspath(__file__))
            font_path = os.path.join(script_dir, 'RussoOne-Regular.ttf')
            if not os.path.exists(font_path):
                font_path = "/Users/emilyfehr8/Library/Fonts/RussoOne-Regular.ttf"
            
            # Try to load Russo One font for matplotlib
            try:
                if os.path.exists(font_path):
                    from matplotlib.font_manager import FontProperties
                    from matplotlib import font_manager
                    font_manager.fontManager.addfont(font_path)
                    russo_font_prop = FontProperties(fname=font_path)
                else:
                    russo_font_prop = None
            except:
                russo_font_prop = None
            
            games = stats['all_games']
            game_nums = np.array(range(1, len(games) + 1))
            
            # Calculate win/loss for each game
            wins = np.array([1 if g['won'] else 0 for g in games])
            
            # Calculate rolling win percentage with 5-game window
            window_size = min(5, len(games))
            rolling_win_pct = []
            for i in range(len(games)):
                start_idx = max(0, i - window_size + 1)
                window_wins = np.sum(wins[start_idx:i+1])
                window_games = min(i + 1, window_size)
                rolling_win_pct.append((window_wins / window_games) * 100)
            
            rolling_win_pct = np.array(rolling_win_pct)
            
            # Create thin horizontal chart (8 inches wide, ~1 inch tall)
            fig, ax = plt.subplots(figsize=(8, 1.2))
            fig.patch.set_alpha(0.0)  # Transparent figure background
            ax.patch.set_alpha(0.0)  # Transparent axes background
            
            # Smooth the line for wave effect using scipy's savgol filter
            if len(rolling_win_pct) > 5:
                try:
                    # Use Savitzky-Golay filter for smooth wave
                    from scipy import signal
                    smooth_window = min(5, len(rolling_win_pct) // 3)
                    if smooth_window % 2 == 0:
                        smooth_window += 1  # Must be odd
                    if smooth_window >= 3:
                        smoothed = signal.savgol_filter(rolling_win_pct, smooth_window, 2)
                    else:
                        smoothed = rolling_win_pct
                except ImportError:
                    # Fallback to simple moving average if scipy not available
                    smoothed = np.convolve(rolling_win_pct, np.ones(3)/3, mode='same')
                except:
                    smoothed = rolling_win_pct
            else:
                smoothed = rolling_win_pct
            
            # Create color gradient based on win percentage
            # Green (high win%) to yellow (50%) to red (low win%)
            colors_list = []
            for val in smoothed:
                if val >= 50:
                    # Green to yellow gradient (50-100%)
                    ratio = (val - 50) / 50.0
                    r = ratio * 0.2  # Green to yellow
                    g = 0.8 + ratio * 0.2
                    b = ratio * 0.2
                else:
                    # Yellow to red gradient (0-50%)
                    ratio = val / 50.0
                    r = 0.8 + ratio * 0.2
                    g = 0.8 - ratio * 0.8
                    b = 0.0
                colors_list.append((r, g, b))
            
            # Plot line segments with gradient colors
            for i in range(len(game_nums) - 1):
                ax.plot(game_nums[i:i+2], smoothed[i:i+2], 
                       color=colors_list[i], linewidth=2.5, alpha=0.9, solid_capstyle='round')
            
            # Add fill area below the line with gradient
            ax.fill_between(game_nums, smoothed, alpha=0.15, 
                          color='steelblue', interpolate=True)
            
            # Add 50% reference line
            ax.axhline(y=50, color='gray', linestyle='--', linewidth=0.8, alpha=0.4)
            
            # Set limits
            ax.set_ylim([0, 100])
            ax.set_xlim([1, len(games)])
            
            # Styling
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.spines['bottom'].set_alpha(0.3)
            
            # Use Russo One font if available
            if russo_font_prop:
                ax.set_xlabel('Game Number', fontsize=9, fontweight='bold', 
                             fontproperties=russo_font_prop, alpha=0.7)
                ax.set_ylabel('Rolling Win %', fontsize=9, fontweight='bold', 
                             fontproperties=russo_font_prop, alpha=0.7)
                ax.tick_params(axis='both', labelsize=7, labelcolor='black')
                plt.title('Momentum Wave', fontsize=11, fontweight='bold', 
                         pad=8, fontproperties=russo_font_prop, alpha=0.9)
            else:
                ax.set_xlabel('Game Number', fontsize=9, fontweight='bold', alpha=0.7)
                ax.set_ylabel('Rolling Win %', fontsize=9, fontweight='bold', alpha=0.7)
                ax.tick_params(axis='both', labelsize=7, labelcolor='black')
                plt.title('Momentum Wave', fontsize=11, fontweight='bold', pad=8, alpha=0.9)
            
            ax.grid(True, alpha=0.2, linestyle='--', linewidth=0.5)
            ax.set_axisbelow(True)
            
            plt.tight_layout()
            
            # Save to buffer with transparent background
            img_buffer = BytesIO()
            plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight', 
                       transparent=True, facecolor='none', edgecolor='none')
            img_buffer.seek(0)
            img_buffer_copy = BytesIO(img_buffer.read())
            img_buffer.seek(0)
            img = Image(img_buffer)
            img.drawHeight = 1.2*inch
            img.drawWidth = 8*inch
            img._buffer_data = img_buffer_copy
            
            # Create custom Flowable to center the chart
            class CenteredMomentumWave(Flowable):
                def __init__(self, image):
                    Flowable.__init__(self)
                    self.image = image
                    self.width = image.drawWidth
                    self.height = image.drawHeight
                    
                    from reportlab.lib.utils import ImageReader
                    if hasattr(image, '_buffer_data'):
                        image._buffer_data.seek(0)
                        self.img_reader = ImageReader(image._buffer_data)
                    elif hasattr(image, '_data'):
                        self.img_reader = ImageReader(image._data)
                    else:
                        self.img_reader = image
                
                def wrap(self, availWidth, availHeight):
                    return (0, 0)  # Takes no space in flow
                
                def draw(self):
                    self.canv.saveState()
                    
                    # Get current position
                    current_y = None
                    if hasattr(self.canv, '_y'):
                        current_y = self.canv._y
                    
                    # Center horizontally on page (page is 612pt wide = 8.5 inches)
                    # Image is 8 inches = 576pt
                    page_width = 612.0
                    image_width = self.width
                    center_x = (page_width - image_width) / 2.0
                    
                    # Position vertically - moved down by 14.5cm from center (7cm + 3cm + 4.5cm)
                    # 14.5cm = 14.5 * 72 / 2.54 ≈ 411.0 points
                    shift_down_cm = 14.5
                    shift_down_points = shift_down_cm * 72 / 2.54
                    
                    if current_y is not None:
                        # Shift down from current position
                        # Negative Y translation moves down in ReportLab
                        shift_up = -shift_down_points
                    else:
                        # Default: shift down by 7cm
                        shift_up = -shift_down_points
                    
                    # Translate to center horizontally, shift down vertically
                    self.canv.translate(center_x, shift_up)
                    
                    # Draw image
                    self.canv.drawImage(self.img_reader, 0, 0,
                                       width=self.image.drawWidth,
                                       height=self.image.drawHeight,
                                       mask='auto')
                    
                    self.canv.restoreState()
            
            centered_wave = CenteredMomentumWave(img)
            story.append(centered_wave)
            plt.close()
            
        except Exception as e:
            print(f"Error creating momentum wave chart: {e}")
            import traceback
            traceback.print_exc()
        
        return story
    
    def create_movement_and_performance_section(self, stats: dict, team_abbrev: str):
        """Create side-by-side layout: movement patterns on left, performance trends on right"""
        story = []
        
        # Add negative spacer at start to move this section up by 4cm
        # We'll do this by reducing space before it - add a minimal spacer
        # Actually, we need to insert movement patterns earlier, so we'll wrap it
        
        # Get movement patterns content (returns list)
        movement_story = self.create_movement_patterns_visualization(stats, team_abbrev)
        
        # Get performance trends graph (returns list)
        performance_story = self.create_performance_trend_graph(stats, team_abbrev)
        
        # Create side-by-side layout using a two-column table
        # Movement patterns: shift left 3cm (85 points)
        # Performance trends: shift right 3cm (85 points) and up 3cm (85 points)
        
        from reportlab.platypus import KeepTogether
        
        # Extract the actual content from stories (remove spacers)
        movement_content = [item for item in movement_story if not isinstance(item, Spacer)]
        performance_content = [item for item in performance_story if not isinstance(item, Spacer)]
        
        # Wrap movement content in a Flowable that shifts it up by 4cm
        # 4cm = 4 * 72 / 2.54 ≈ 113.4 points
        class ShiftUpFlowableList(Flowable):
            def __init__(self, content_list, shift_up_points):
                Flowable.__init__(self)
                self.content_list = content_list
                self.shift_up_points = shift_up_points
                
            def wrap(self, availWidth, availHeight):
                # Return minimal dimensions - content will be positioned manually
                return (availWidth, 0)
            
            def draw(self):
                # This won't work for multiple flowables easily
                # Instead, we'll handle shifting in the movement_patterns function itself
                pass
        
        # Create side-by-side layout: performance trends on left, movement patterns on right
        # Both will be positioned using their individual wrappers, but we need to ensure both are visible
        # Put performance trends first (left side), then movement patterns (right side)
        # NOTE: Performance trends graph is now added earlier in the story, so skip it here
        # if performance_content:
        #     # Performance trends graph already has its own positioning in LeftAlignedImage
        #     story.extend(performance_content)
        
        # Add a spacer to separate the two sections horizontally/vertically
        # Since both use absolute positioning, we add minimal spacing
        story.append(Spacer(1, 0))
        
        # Movement patterns on the right (already has positioning wrapper)
        if movement_content:
            story.extend(movement_content)
        
        # Minimal spacer to move next section up
        story.append(Spacer(1, 3))
        
        return story
    
    def create_player_stats_section(self, stats: dict, team_abbrev: str):
        """Create condensed player stats section with top 3 and bottom 3 in GS+XG"""
        story = []
        
        # Get team color
        team_colors = {
            'TBL': colors.Color(0/255, 40/255, 104/255), 'NSH': colors.Color(255/255, 184/255, 28/255),
            'EDM': colors.Color(4/255, 30/255, 66/255), 'FLA': colors.Color(200/255, 16/255, 46/255),
            'COL': colors.Color(111/255, 38/255, 61/255), 'DAL': colors.Color(0/255, 99/255, 65/255),
            'BOS': colors.Color(252/255, 181/255, 20/255), 'TOR': colors.Color(0/255, 32/255, 91/255),
            'MTL': colors.Color(175/255, 30/255, 45/255), 'OTT': colors.Color(200/255, 16/255, 46/255),
            'BUF': colors.Color(0/255, 38/255, 84/255), 'DET': colors.Color(206/255, 17/255, 38/255),
            'CAR': colors.Color(226/255, 24/255, 54/255), 'WSH': colors.Color(4/255, 30/255, 66/255),
            'PIT': colors.Color(255/255, 184/255, 28/255), 'NYR': colors.Color(0/255, 56/255, 168/255),
            'NYI': colors.Color(0/255, 83/255, 155/255), 'NJD': colors.Color(206/255, 17/255, 38/255),
            'PHI': colors.Color(247/255, 30/255, 36/255), 'CBJ': colors.Color(0/255, 38/255, 84/255),
            'STL': colors.Color(0/255, 47/255, 108/255), 'MIN': colors.Color(0/255, 99/255, 65/255),
            'WPG': colors.Color(4/255, 30/255, 66/255), 'ARI': colors.Color(140/255, 38/255, 51/255),
            'VGK': colors.Color(185/255, 151/255, 91/255), 'SJS': colors.Color(0/255, 109/255, 117/255),
            'LAK': colors.Color(162/255, 170/255, 173/255), 'ANA': colors.Color(185/255, 151/255, 91/255),
            'CGY': colors.Color(200/255, 16/255, 46/255), 'VAN': colors.Color(0/255, 32/255, 91/255),
            'SEA': colors.Color(0/255, 22/255, 40/255), 'UTA': colors.Color(105/255, 179/255, 231/255),
            'CHI': colors.Color(207/255, 10/255, 44/255)
        }
        team_color = team_colors.get(team_abbrev, colors.grey)
        
        # Convert player stats to list and filter (need at least 3 games, exclude goalies)
        player_list = []
        for player_id, pstats in stats['player_stats'].items():
            # Exclude goalies (position 'G')
            if pstats.get('position', '').upper() == 'G':
                continue
            if pstats['games'] >= 3:  # Minimum games threshold
                avg_gs_plus_xg = pstats['gs_plus_xg'] / pstats['games']
                player_list.append({
                    'name': pstats['name'],
                    'games': pstats['games'],
                    'total_gs': pstats['total_gs'],
                    'total_xg': pstats['total_xg'],
                    'total_gs_plus_xg': pstats['gs_plus_xg'],
                    'avg_gs_plus_xg': avg_gs_plus_xg
                })
        
        if not player_list:
            return story
        
        # Sort by GS+XG
        player_list.sort(key=lambda x: x['avg_gs_plus_xg'], reverse=True)
        top_3 = player_list[:3]  # Top 3
        bottom_3 = player_list[-3:] if len(player_list) >= 3 else player_list
        bottom_3.reverse()  # Show worst first
        
        # Combined title - renamed to "Player Rankings" with 0.1cm padding on each side
        title_data = [["Player Rankings"]]
        # Calculate width: text width (~1.8 inches for "Player Rankings") + 0.1cm padding on each side (0.2cm total = ~0.079 inches)
        title_width = 1.8*inch + (0.2 * 72 / 2.54)  # Text width + 0.2cm total padding
        title_table = Table(title_data, colWidths=[title_width])
        title_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), team_color),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'RussoOne-Regular'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 0.1 * 72 / 2.54),  # 0.1cm left padding
            ('RIGHTPADDING', (0, 0), (-1, -1), 0.1 * 72 / 2.54),  # 0.1cm right padding
        ]))
        
        # Calculate table width for centering title bar
        table_total_width = sum([0.4*inch, 1.5*inch, 0.6*inch, 0.6*inch, 0.7*inch])  # 3.8 inches
        # Title width already calculated above (2.5" text + 0.2cm padding)
        # Center title bar over table: offset = (table_width - title_width) / 2
        title_offset = (table_total_width - title_width) / 2
        
        # Wrap title table to shift it right by 9cm (moved 1cm left from 10cm) and center it over the table
        title_wrapper = Table([[title_table]], colWidths=[7.5*inch])
        title_wrapper.setStyle(TableStyle([
            ('LEFTPADDING', (0, 0), (-1, -1), 9 * 72 / 2.54 + title_offset),  # 9cm right + center offset (moved 1cm left)
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        story.append(title_wrapper)
        story.append(Spacer(1, 3))  # Reduced from 5 to move section up
        
        # Combined table with top 3 and bottom 3 (per game values)
        combined_data = [['Rank', 'Player', 'GS/GP', 'xG/GP', 'TOTAL']]
        
        # Add top 3 (ranked 1-3) - per game values
        for i, p in enumerate(top_3, 1):
            gs_per_game = p['total_gs'] / p['games']
            xg_per_game = p['total_xg'] / p['games']
            gs_xg_per_game = p['avg_gs_plus_xg']
            combined_data.append([
                str(i), p['name'], f"{gs_per_game:.2f}", f"{xg_per_game:.2f}",
                f"{gs_xg_per_game:.2f}"
            ])
        
        # Add bottom 3 (ranked from worst, showing rank) - per game values
        for i, p in enumerate(bottom_3):
            rank = len(player_list) - i
            gs_per_game = p['total_gs'] / p['games']
            xg_per_game = p['total_xg'] / p['games']
            gs_xg_per_game = p['avg_gs_plus_xg']
            combined_data.append([
                str(rank), p['name'], f"{gs_per_game:.2f}", f"{xg_per_game:.2f}",
                f"{gs_xg_per_game:.2f}"
            ])
        
        # Updated column widths: removed GP column, now 5 columns instead of 6
        combined_table = Table(combined_data, colWidths=[0.4*inch, 1.5*inch, 0.6*inch, 0.6*inch, 0.7*inch])
        combined_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'RussoOne-Regular'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            # Top 3 rows (beige background)
            ('BACKGROUND', (0, 1), (-1, 3), colors.beige),
            # Bottom 3 rows (lightgrey background) - start after top 3
            ('BACKGROUND', (0, 4), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
        ]))
        
        # Wrap combined table to shift it right by 10cm (9cm + 1cm) - add left padding to push content right
        table_wrapper = Table([[combined_table]], colWidths=[7.5*inch])
        table_wrapper.setStyle(TableStyle([
            ('LEFTPADDING', (0, 0), (-1, -1), 10 * 72 / 2.54),  # Add 10cm left padding to push content right
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        story.append(table_wrapper)
        story.append(Spacer(1, 5))  # Reduced from 10 to move next section up
        
        return story
    
    def create_period_by_period_table(self, stats: dict, team_abbrev: str):
        """Create period-by-period table with all metrics like post-game reports"""
        story = []
        
        # Get team color
        team_colors = {
            'TBL': colors.Color(0/255, 40/255, 104/255), 'NSH': colors.Color(255/255, 184/255, 28/255),
            'EDM': colors.Color(4/255, 30/255, 66/255), 'FLA': colors.Color(200/255, 16/255, 46/255),
            'COL': colors.Color(111/255, 38/255, 61/255), 'DAL': colors.Color(0/255, 99/255, 65/255),
            'BOS': colors.Color(252/255, 181/255, 20/255), 'TOR': colors.Color(0/255, 32/255, 91/255),
            'MTL': colors.Color(175/255, 30/255, 45/255), 'OTT': colors.Color(200/255, 16/255, 46/255),
            'BUF': colors.Color(0/255, 38/255, 84/255), 'DET': colors.Color(206/255, 17/255, 38/255),
            'CAR': colors.Color(226/255, 24/255, 54/255), 'WSH': colors.Color(4/255, 30/255, 66/255),
            'PIT': colors.Color(255/255, 184/255, 28/255), 'NYR': colors.Color(0/255, 56/255, 168/255),
            'NYI': colors.Color(0/255, 83/255, 155/255), 'NJD': colors.Color(206/255, 17/255, 38/255),
            'PHI': colors.Color(247/255, 30/255, 36/255), 'CBJ': colors.Color(0/255, 38/255, 84/255),
            'STL': colors.Color(0/255, 47/255, 108/255), 'MIN': colors.Color(0/255, 99/255, 65/255),
            'WPG': colors.Color(4/255, 30/255, 66/255), 'ARI': colors.Color(140/255, 38/255, 51/255),
            'VGK': colors.Color(185/255, 151/255, 91/255), 'SJS': colors.Color(0/255, 109/255, 117/255),
            'LAK': colors.Color(162/255, 170/255, 173/255), 'ANA': colors.Color(185/255, 151/255, 91/255),
            'CGY': colors.Color(200/255, 16/255, 46/255), 'VAN': colors.Color(0/255, 32/255, 91/255),
            'SEA': colors.Color(0/255, 22/255, 40/255), 'UTA': colors.Color(105/255, 179/255, 231/255),
            'CHI': colors.Color(207/255, 10/255, 44/255)
        }
        team_color = team_colors.get(team_abbrev, colors.grey)
        
        # Title bar - minimum width to fit text
        title_data = [["PERIOD PERFORMANCE"]]
        title_table = Table(title_data, colWidths=[2.5*inch])
        title_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), team_color),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'RussoOne-Regular'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTWEIGHT', (0, 0), (-1, -1), 'BOLD'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        # Helper function to calculate average from list
        def avg_or_zero(lst):
            return np.mean(lst) if lst else 0.0
        
        # Helper function to sum for totals (like PP goals/attempts)
        def sum_list(lst):
            return sum(lst) if lst else 0
        
        # Build period data with all metrics
        period_data = [
            # Header row (same as post-game reports)
            ['Period', 'GF', 'S', 'CF%', 'PP', 'PIM', 'Hits', 'FO%', 'BLK', 'GV', 'TK', 'GS', 'xG', 'NZT', 'NZTSA', 'OZS', 'NZS', 'DZS', 'FC', 'Rush']
        ]
        
        # Add data for each period (1st, 2nd, 3rd)
        for period_key, period_label in [('p1', '1'), ('p2', '2'), ('p3', '3')]:
            period_metrics = stats['period_metrics'][period_key]
            
            # Calculate averages/totals
            goals = stats['period_goals'][period_key]
            avg_shots = avg_or_zero(period_metrics['shots'])
            avg_corsi = avg_or_zero(period_metrics['corsi_pct'])
            total_pp_goals = sum_list(period_metrics['pp_goals'])
            total_pp_attempts = sum_list(period_metrics['pp_attempts'])
            avg_pim = avg_or_zero(period_metrics['pim'])
            avg_hits = avg_or_zero(period_metrics['hits'])
            avg_fo = avg_or_zero(period_metrics['fo_pct'])
            avg_blocks = avg_or_zero(period_metrics['blocks'])
            avg_gv = avg_or_zero(period_metrics['gv'])
            avg_tk = avg_or_zero(period_metrics['tk'])
            avg_gs = avg_or_zero(period_metrics['gs'])
            avg_xg = avg_or_zero(period_metrics['xg'])
            avg_nzt = avg_or_zero(period_metrics['nzt'])
            avg_nztsa = avg_or_zero(period_metrics['nztsa'])
            avg_ozs = avg_or_zero(period_metrics['ozs'])
            avg_nzs = avg_or_zero(period_metrics['nzs'])
            avg_dzs = avg_or_zero(period_metrics['dzs'])
            avg_fc = avg_or_zero(period_metrics['fc'])
            avg_rush = avg_or_zero(period_metrics['rush'])
            
            # Format PP as "goals/attempts"
            pp_display = f"{total_pp_goals}/{total_pp_attempts}" if total_pp_attempts > 0 else "0/0"
            
            period_data.append([
                period_label,
                str(int(goals)),
                f"{avg_shots:.1f}",
                f"{avg_corsi:.1f}%",
                pp_display,
                f"{avg_pim:.1f}",
                f"{avg_hits:.1f}",
                f"{avg_fo:.1f}%",
                f"{avg_blocks:.1f}",
                f"{avg_gv:.1f}",
                f"{avg_tk:.1f}",
                f"{avg_gs:.1f}",
                f"{avg_xg:.2f}",
                f"{avg_nzt:.1f}",
                f"{avg_nztsa:.1f}",
                f"{avg_ozs:.1f}",
                f"{avg_nzs:.1f}",
                f"{avg_dzs:.1f}",
                f"{avg_fc:.1f}",
                f"{avg_rush:.1f}"
            ])
        
        # Column widths matching post-game report (20 columns)
        col_widths = [0.4*inch, 0.35*inch, 0.35*inch, 0.4*inch, 0.35*inch, 0.35*inch, 0.35*inch, 
                      0.4*inch, 0.35*inch, 0.35*inch, 0.35*inch, 0.35*inch, 0.4*inch, 0.35*inch, 
                      0.4*inch, 0.35*inch, 0.35*inch, 0.35*inch, 0.35*inch, 0.35*inch]
        
        period_table = Table(period_data, colWidths=col_widths)
        period_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), team_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'RussoOne-Regular'),
            ('FONTSIZE', (0, 0), (-1, 0), 7),
            ('FONTSIZE', (0, 1), (-1, -1), 6.5),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, 1), colors.beige),
            ('BACKGROUND', (0, 2), (-1, 2), colors.lightgrey),
            ('BACKGROUND', (0, 3), (-1, 3), colors.beige),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ]))
        
        story.append(title_table)
        story.append(Spacer(1, 3))  # Reduced spacing
        story.append(period_table)
        story.append(Spacer(1, 5))  # Reduced from 10 to move next section up
        
        return story
    
    def create_clutch_performance_box(self, stats: dict, team_abbrev: str):
        """Create clutch performance indicator box with league rank"""
        story = []
        
        # Get team color
        team_colors = {
            'TBL': colors.Color(0/255, 40/255, 104/255), 'NSH': colors.Color(255/255, 184/255, 28/255),
            'EDM': colors.Color(4/255, 30/255, 66/255), 'FLA': colors.Color(200/255, 16/255, 46/255),
            'COL': colors.Color(111/255, 38/255, 61/255), 'DAL': colors.Color(0/255, 99/255, 65/255),
            'BOS': colors.Color(252/255, 181/255, 20/255), 'TOR': colors.Color(0/255, 32/255, 91/255),
            'MTL': colors.Color(175/255, 30/255, 45/255), 'OTT': colors.Color(200/255, 16/255, 46/255),
            'BUF': colors.Color(0/255, 38/255, 84/255), 'DET': colors.Color(206/255, 17/255, 38/255),
            'CAR': colors.Color(226/255, 24/255, 54/255), 'WSH': colors.Color(4/255, 30/255, 66/255),
            'PIT': colors.Color(255/255, 184/255, 28/255), 'NYR': colors.Color(0/255, 56/255, 168/255),
            'NYI': colors.Color(0/255, 83/255, 155/255), 'NJD': colors.Color(206/255, 17/255, 38/255),
            'PHI': colors.Color(247/255, 30/255, 36/255), 'CBJ': colors.Color(0/255, 38/255, 84/255),
            'STL': colors.Color(0/255, 47/255, 108/255), 'MIN': colors.Color(0/255, 99/255, 65/255),
            'WPG': colors.Color(4/255, 30/255, 66/255), 'ARI': colors.Color(140/255, 38/255, 51/255),
            'VGK': colors.Color(185/255, 151/255, 91/255), 'SJS': colors.Color(0/255, 109/255, 117/255),
            'LAK': colors.Color(162/255, 170/255, 173/255), 'ANA': colors.Color(185/255, 151/255, 91/255),
            'CGY': colors.Color(200/255, 16/255, 46/255), 'VAN': colors.Color(0/255, 32/255, 91/255),
            'SEA': colors.Color(0/255, 22/255, 40/255), 'UTA': colors.Color(105/255, 179/255, 231/255),
            'CHI': colors.Color(207/255, 10/255, 44/255)
        }
        team_color = team_colors.get(team_abbrev, colors.grey)
        
        # Calculate clutch metrics
        third_period_goals = stats['clutch']['third_period_goals']
        one_goal_games = stats['clutch']['one_goal_games']
        one_goal_wins = stats['clutch']['one_goal_wins']
        one_goal_win_pct = (one_goal_wins / one_goal_games * 100) if one_goal_games > 0 else 0.0
        
        # Calculate composite clutch score (simplified - in reality would compare to league)
        # For now, estimate rank based on metrics (would need league data for accurate ranking)
        # Using a simple heuristic: combine 3rd period goals and one-goal win%
        clutch_score = (third_period_goals * 2) + (one_goal_win_pct * 0.5)
        
        # Estimate league rank (1-32) - this is a placeholder
        # In production, you'd fetch league-wide data and calculate actual rank
        # For now, estimate based on score percentile (higher score = better rank)
        estimated_rank = max(1, min(32, int(32 - (clutch_score / 10))))  # Rough estimate
        
        # Format rank with suffix
        def get_rank_suffix(n):
            if 11 <= n <= 13:
                return 'th'
            return {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
        
        rank_text = f"{estimated_rank}{get_rank_suffix(estimated_rank)} rank"
        
        # Create single-column table with two rows
        clutch_data = [
            ["CLUTCH PERFORMANCE"],  # Row 1: Title
            [rank_text]              # Row 2: Rank
        ]
        
        clutch_table = Table(clutch_data, colWidths=[1.8*inch])
        clutch_table.setStyle(TableStyle([
            # Row 1 (title) - team color background, white text
            ('BACKGROUND', (0, 0), (-1, 0), team_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'RussoOne-Regular'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),  # Title font size
            ('FONTSIZE', (0, 1), (-1, 1), 13),  # Rank font size (larger)
            ('TOPPADDING', (0, 0), (-1, 0), 6),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('LEFTPADDING', (0, 0), (-1, 0), 8),
            ('RIGHTPADDING', (0, 0), (-1, 0), 8),
            # Row 2 (rank) - white background, black text
            ('BACKGROUND', (0, 1), (-1, 1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, 1), colors.black),
            ('TOPPADDING', (0, 1), (-1, 1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, 1), 8),
            ('LEFTPADDING', (0, 1), (-1, 1), 8),
            ('RIGHTPADDING', (0, 1), (-1, 1), 8),
            # Border
            ('GRID', (0, 0), (-1, -1), 1, team_color),
        ]))
        
        # Position clutch box to the left of player rankings table on page 1
        # Player rankings table is at 9cm from left, positioned at same vertical level
        # Position clutch box at ~3cm from left (moved left by 2cm from 5cm)
        clutch_left_cm = 3.0
        clutch_left_points = clutch_left_cm * 72 / 2.54
        
        # Create a custom Flowable wrapper for absolute positioning (similar to movement patterns)
        class ClutchBoxFlowable(Flowable):
            def __init__(self, table, left_points, shift_up_points):
                Flowable.__init__(self)
                self.table = table
                self.left_points = left_points
                self.shift_up_points = shift_up_points
                self.width = 1.8 * inch
                # Wrap table to get its height
                try:
                    w, h = self.table.wrap(1.8 * inch, 792)
                    self.height = h
                except:
                    self.height = 50  # Fallback height
                
            def wrap(self, availWidth, availHeight):
                return (0, 0)  # Takes no space in flow
                
            def draw(self):
                self.canv.saveState()
                current_y = self.canv._y if hasattr(self.canv, '_y') else 0
                
                # Calculate vertical shift - negative values move down
                # If shift_up_points is negative, it means move down
                # We want to position relative to where content naturally flows
                if current_y is not None and current_y > 0:
                    # Calculate target position: current position - shift (negative shift = down)
                    y_translation = -abs(self.shift_up_points) if self.shift_up_points < 0 else self.shift_up_points - current_y
                    # If shift is negative, move down from current position
                    if self.shift_up_points < 0:
                        y_translation = -abs(self.shift_up_points)
                else:
                    # If no current_y, use shift directly but invert if negative to move down
                    y_translation = -abs(self.shift_up_points) if self.shift_up_points < 0 else self.shift_up_points
                
                # Sanity check - allow negative values (moving down)
                if abs(y_translation) > 700:
                    y_translation = -200.0  # Fallback reasonable shift down
                
                # Translate to position: horizontally and vertically (negative Y = down)
                self.canv.translate(self.left_points, y_translation)
                
                # Wrap and draw the table properly
                try:
                    w, h = self.table.wrap(1.8 * inch, 792)
                    self.table.drawOn(self.canv, 0, 0)
                except:
                    # Fallback: try direct draw
                    if hasattr(self.table, 'drawOn'):
                        self.table.drawOn(self.canv, 0, 0)
                    elif hasattr(self.table, 'draw'):
                        self.table.draw()
                self.canv.restoreState()
        
        # Wrap clutch table and position it absolutely
        # Moved down by 6cm total (10cm - 4cm up) from player rankings position
        clutch_shift_up_points = 78.3 - 113.4 - 85.0 - 85.0 + (4 * 72 / 2.54)  # Moved up by 4cm total
        clutch_flowable = ClutchBoxFlowable(clutch_table, clutch_left_points, clutch_shift_up_points)
        
        story.append(clutch_flowable)
        return story
    
    def generate_team_report(self, team_abbrev: str, output_filename: str = None, season_start_date: str = None):
        """Generate complete team report"""
        print(f"Generating team report for {team_abbrev}...")
        
        games = self.get_team_games(team_abbrev, season_start_date)
        
        if not games:
            print(f"No games found for {team_abbrev}")
            return None
        
        print(f"Found {len(games)} games for {team_abbrev}")
        
        stats = self.aggregate_team_stats(team_abbrev, games)
        
        # Create temp file in system temp directory (won't save to project directory)
        import tempfile
        if output_filename is None:
            output_filename = f"team_report_{team_abbrev}_{datetime.now().strftime('%Y%m%d')}.pdf"
        temp_dir = tempfile.gettempdir()
        temp_filepath = os.path.join(temp_dir, output_filename)
        
        # Create PDF with same styling as postgame reports
        doc = BaseDocTemplate(temp_filepath, pagesize=letter, 
                              rightMargin=72, leftMargin=72, 
                              topMargin=0, bottomMargin=18)
        
        story = []
        
        # Add header (same as postgame reports)
        header_image = self.create_header_image(team_abbrev)
        if header_image:
            story.append(Spacer(1, -40))  # Negative spacer to pull header to top
            story.append(header_image)
            story.append(Spacer(1, 14))  # Space after header
        
        # Add sections
        story.extend(self.create_team_summary_section(team_abbrev, stats))
        story.extend(self.create_home_away_comparison(stats, team_abbrev))
        story.extend(self.create_period_by_period_table(stats, team_abbrev))  # Period table
        
        # Add momentum wave chart - positioned in middle of page (user will adjust)
        momentum_story = self.create_momentum_wave_chart(stats, team_abbrev)
        if momentum_story:
            story.extend(momentum_story)
        
        # Add performance trends graph early so it can be positioned above top players table
        performance_story = self.create_performance_trend_graph(stats, team_abbrev)
        performance_content = [item for item in performance_story if not isinstance(item, Spacer)]
        if performance_content:
            story.extend(performance_content)
        
        # Add movement patterns table right after performance graph so they appear side-by-side on page 1
        movement_story = self.create_movement_patterns_visualization(stats, team_abbrev)
        if movement_story:
            story.extend(movement_story)
        
        # Move player stats section down - positioned to stay on page 1
        # Spacer adjusted to position section: moved up 1cm (78.3pt - 28.3pt = 50pt)
        story.append(Spacer(1, 50.0))  # Spacer to position after graphs, moved up 1cm
        
        # Add clutch performance box early so it appears on page 1, to the left of player rankings
        clutch_story = self.create_clutch_performance_box(stats, team_abbrev)
        if clutch_story:
            story.extend(clutch_story)
        
        # Add player stats section early to keep it on page 1
        from reportlab.platypus import KeepTogether
        player_stats_content = self.create_player_stats_section(stats, team_abbrev)
        # Wrap in KeepTogether to prevent splitting across pages
        if player_stats_content:
            # Convert list to KeepTogether (which takes a list of flowables)
            story.append(KeepTogether(player_stats_content))
        
        # Add background template
        script_dir = os.path.dirname(__file__)
        abs_background = os.path.join(script_dir, "Paper.png")
        cwd_background = "Paper.png"
        background_path = abs_background if os.path.exists(abs_background) else cwd_background
        
        if os.path.exists(background_path):
            from reportlab.platypus.frames import Frame
            # Allow content to extend beyond normal margins for positioning
            # Start frame further left and wider to allow negative padding shifts
            frame = Frame(0, 18, 612, 756, leftPadding=0, bottomPadding=0, rightPadding=0, topPadding=0)
            page_template = BackgroundPageTemplate('background', [frame], background_path)
            doc.addPageTemplates([page_template])
        
        doc.build(story)
        
        # Open in Preview instead of saving to directory
        import subprocess
        
        # Open in Preview on macOS
        subprocess.run(['open', '-a', 'Preview', temp_filepath])
        print(f"Team report opened in Preview: {temp_filepath}")
        
        return temp_filepath


def main():
    """Example usage"""
    generator = TeamReportGenerator()
    
    team = input("Enter team abbreviation (e.g., FLA, EDM, COL): ").upper()
    
    if team:
        generator.generate_team_report(team)  # No output filename needed - will open in Preview

if __name__ == '__main__':
    main()
