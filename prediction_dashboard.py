#!/usr/bin/env python3
"""
Fast Mini Site for Viewing Pre-Game and In-Game Predictions
"""

from flask import Flask, render_template, jsonify, send_file
from datetime import datetime, timedelta
import pytz
import os
from nhl_api_client import NHLAPIClient
from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2
from correlation_model import CorrelationModel
from lineup_service import LineupService
from live_in_game_predictions import LiveInGamePredictor
from run_predictions_for_date import predict_game_for_date
from pdf_report_generator import PostGameReportGenerator

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

# Initialize components
api = NHLAPIClient()
model = ImprovedSelfLearningModelV2()
model.deterministic = True
corr = CorrelationModel()
lineup = LineupService()
live_predictor = LiveInGamePredictor()
report_generator = PostGameReportGenerator()
ct_tz = pytz.timezone('US/Central')


def get_pregame_prediction(away_team, home_team, game_date, game_id):
    """Get pre-game prediction"""
    try:
        result = predict_game_for_date(model, corr, away_team, home_team, game_date, 
                                     game_id=game_id, lineup_service=lineup)
        return {
            'away_prob': result['away_prob'] * 100,
            'home_prob': result['home_prob'] * 100,
            'predicted_winner': home_team if result['home_prob'] > result['away_prob'] else away_team,
            'confidence': abs(result['home_prob'] - result['away_prob']) * 100
        }
    except Exception as e:
        print(f"Error getting pre-game prediction: {e}")
        return None


def get_live_prediction(game_id):
    """Get live in-game prediction"""
    try:
        live_metrics = live_predictor.get_live_game_data(game_id)
        if not live_metrics:
            return None
        
        prediction = live_predictor.predict_live_game(live_metrics)
        if not prediction:
            return None
        
        return {
            'away_team': prediction['away_team'],
            'home_team': prediction['home_team'],
            'away_score': prediction['away_score'],
            'home_score': prediction['home_score'],
            'current_period': prediction['current_period'],
            'time_remaining': prediction['time_remaining'],
            'away_prob': prediction['away_prob'] * 100,
            'home_prob': prediction['home_prob'] * 100,
            'predicted_winner': prediction['home_team'] if prediction['home_prob'] > prediction['away_prob'] else prediction['away_team'],
            'confidence': prediction['confidence'] * 100,
            'momentum': prediction['momentum'],
            'live_metrics': prediction['live_metrics']
        }
    except Exception as e:
        print(f"Error getting live prediction: {e}")
        return None


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('prediction_dashboard.html')


@app.route('/api/games')
def get_games():
    """Get all games for today with predictions"""
    try:
        today = datetime.now(ct_tz).strftime('%Y-%m-%d')
        schedule = api.get_game_schedule(today)
        
        if not schedule or 'gameWeek' not in schedule:
            return jsonify({'games': [], 'date': today})
        
        games = []
        for day in schedule['gameWeek']:
            if day.get('date') != today:
                continue
            
            for game in day.get('games', []):
                away_team = (game.get('awayTeam', {}) or {}).get('abbrev', '')
                home_team = (game.get('homeTeam', {}) or {}).get('abbrev', '')
                game_id = str(game.get('id', ''))
                game_state = game.get('gameState', 'PREVIEW')
                start_time = game.get('startTimeUTC', '')
                
                if not away_team or not home_team:
                    continue
                
                game_data = {
                    'game_id': game_id,
                    'away_team': away_team,
                    'home_team': home_team,
                    'game_state': game_state,
                    'start_time': start_time,
                    'date': today,
                    'is_live': game_state in ['LIVE', 'CRIT'],
                    'pregame_prediction': None,
                    'live_prediction': None
                }
                
                # Get pre-game prediction
                pregame = get_pregame_prediction(away_team, home_team, today, game_id)
                if pregame:
                    game_data['pregame_prediction'] = pregame
                
                # Get live scores and stats directly from API for homepage
                if game_data['is_live']:
                    try:
                        boxscore_data = api.get_game_boxscore(game_id)
                        if boxscore_data:
                            # Try multiple paths for scores
                            away_team_data = boxscore_data.get('awayTeam', {})
                            home_team_data = boxscore_data.get('homeTeam', {})
                            
                            away_score = (
                                away_team_data.get('score') or 
                                away_team_data.get('goals') or 
                                away_team_data.get('teamStats', {}).get('teamSkaterStats', {}).get('goals') or
                                0
                            )
                            home_score = (
                                home_team_data.get('score') or 
                                home_team_data.get('goals') or 
                                home_team_data.get('teamStats', {}).get('teamSkaterStats', {}).get('goals') or
                                0
                            )
                            
                            # Get period info
                            period_desc = boxscore_data.get('periodDescriptor', {})
                            if not period_desc:
                                period_desc = boxscore_data.get('periodInfo', {})
                            
                            current_period = period_desc.get('number') or period_desc.get('currentPeriod') or 1
                            
                            # Get clock/time
                            clock = boxscore_data.get('clock', {})
                            if not clock:
                                clock = boxscore_data.get('periodInfo', {})
                            
                            time_remaining = clock.get('timeRemaining') or clock.get('timeInPeriod') or '20:00'
                            
                            game_data['away_score'] = away_score
                            game_data['home_score'] = home_score
                            game_data['current_period'] = current_period
                            game_data['time_remaining'] = time_remaining
                    except Exception as e:
                        print(f"Error getting live scores: {e}")
                        import traceback
                        traceback.print_exc()
                    
                    # Get live prediction
                    live = get_live_prediction(game_id)
                    if live:
                        game_data['live_prediction'] = live
                        # Use scores from live prediction if boxscore didn't work
                        if 'away_score' not in game_data:
                            game_data['away_score'] = live.get('away_score', 0)
                            game_data['home_score'] = live.get('home_score', 0)
                            game_data['current_period'] = live.get('current_period', 1)
                            game_data['time_remaining'] = live.get('time_remaining', '20:00')
                
                games.append(game_data)
        
        return jsonify({
            'games': games,
            'date': today,
            'last_updated': datetime.now(ct_tz).isoformat()
        })
    
    except Exception as e:
        print(f"Error getting games: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/game/<game_id>')
def get_game(game_id):
    """Get specific game prediction (for live updates)"""
    try:
        # Get game info
        today = datetime.now(ct_tz).strftime('%Y-%m-%d')
        schedule = api.get_game_schedule(today)
        
        game_info = None
        for day in schedule.get('gameWeek', []):
            for game in day.get('games', []):
                if str(game.get('id', '')) == game_id:
                    game_info = game
                    break
            if game_info:
                break
        
        if not game_info:
            return jsonify({'error': 'Game not found'}), 404
        
        away_team = (game_info.get('awayTeam', {}) or {}).get('abbrev', '')
        home_team = (game_info.get('homeTeam', {}) or {}).get('abbrev', '')
        game_state = game_info.get('gameState', 'PREVIEW')
        
        result = {
            'game_id': game_id,
            'away_team': away_team,
            'home_team': home_team,
            'game_state': game_state,
            'is_live': game_state in ['LIVE', 'CRIT'],
            'pregame_prediction': None,
            'live_prediction': None
        }
        
        # Get pre-game prediction
        pregame = get_pregame_prediction(away_team, home_team, today, game_id)
        if pregame:
            result['pregame_prediction'] = pregame
        
        # Get live prediction if live
        if result['is_live']:
            live = get_live_prediction(game_id)
            if live:
                result['live_prediction'] = live
        
        return jsonify(result)
    
    except Exception as e:
        print(f"Error getting game: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/static/rink.jpg')
def serve_rink_image():
    """Serve the rink image for shot charts"""
    try:
        rink_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'F300E016-E2BD-450A-B624-5BADF3853AC0.jpeg')
        if not os.path.exists(rink_path):
            rink_path = os.path.join(os.getcwd(), 'F300E016-E2BD-450A-B624-5BADF3853AC0.jpeg')
        if os.path.exists(rink_path):
            return send_file(rink_path, mimetype='image/jpeg')
        else:
            return jsonify({'error': 'Rink image not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/debug/<game_id>')
def debug_game_data(game_id):
    """Debug endpoint to see actual API structure"""
    try:
        boxscore = api.get_game_boxscore(game_id)
        comp_data = api.get_comprehensive_game_data(game_id)
        
        debug_info = {
            'boxscore_exists': boxscore is not None,
            'comp_data_exists': comp_data is not None,
        }
        
        if boxscore:
            debug_info['boxscore_keys'] = list(boxscore.keys())[:20]
            away_team = boxscore.get('awayTeam', {})
            home_team = boxscore.get('homeTeam', {})
            debug_info['awayTeam'] = {
                'keys': list(away_team.keys())[:15],
                'score': away_team.get('score'),
                'goals': away_team.get('goals'),
                'has_teamStats': bool(away_team.get('teamStats')),
                'teamStats_keys': list(away_team.get('teamStats', {}).keys())[:10] if away_team.get('teamStats') else [],
                'teamSkaterStats_keys': list(away_team.get('teamStats', {}).get('teamSkaterStats', {}).keys())[:15] if away_team.get('teamStats', {}).get('teamSkaterStats') else [],
            }
            debug_info['homeTeam'] = {
                'keys': list(home_team.keys())[:15],
                'score': home_team.get('score'),
                'goals': home_team.get('goals'),
                'has_teamStats': bool(home_team.get('teamStats')),
            }
        
        if comp_data:
            comp_boxscore = comp_data.get('boxscore', {})
            debug_info['comp_boxscore'] = {
                'keys': list(comp_boxscore.keys())[:15] if comp_boxscore else [],
                'awayTeam_score': comp_boxscore.get('awayTeam', {}).get('score') if comp_boxscore else None,
            }
        
        return jsonify(debug_info)
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500


@app.route('/api/game/<game_id>/report')
def get_live_game_report(game_id):
    """Get detailed live game report with comprehensive stats"""
    try:
        # Get comprehensive game data
        game_data = api.get_comprehensive_game_data(game_id)
        if not game_data:
            return jsonify({'error': 'Could not fetch game data'}), 404
        
        # Extract basic game info - boxscore is at top level
        boxscore = game_data.get('boxscore', {})
        if not boxscore:
            return jsonify({'error': 'No boxscore data available'}), 404
        
        # NHL API boxscore structure: {awayTeam: {...}, homeTeam: {...}, ...}
        away_team = boxscore.get('awayTeam', {})
        home_team = boxscore.get('homeTeam', {})
        
        away_abbrev = away_team.get('abbrev', '') or away_team.get('abbreviation', '')
        home_abbrev = home_team.get('abbrev', '') or home_team.get('abbreviation', '')
        away_id = away_team.get('id')
        home_id = home_team.get('id')
        
        # Get current scores - try multiple paths
        away_score = (
            away_team.get('score') or 
            away_team.get('goals') or
            away_team.get('teamStats', {}).get('teamSkaterStats', {}).get('goals') or
            0
        )
        home_score = (
            home_team.get('score') or 
            home_team.get('goals') or
            home_team.get('teamStats', {}).get('teamSkaterStats', {}).get('goals') or
            0
        )
        
        # Get period info
        period_descriptor = boxscore.get('periodDescriptor', {})
        current_period = period_descriptor.get('number', 1)
        period_type = period_descriptor.get('periodType', 'REG')
        
        clock = boxscore.get('clock', {})
        time_remaining = clock.get('timeRemaining', '20:00')
        
        # Calculate advanced metrics using report generator methods
        report_data = {
            'game_id': game_id,
            'away_team': away_abbrev,
            'home_team': home_abbrev,
            'away_id': away_id,
            'home_id': home_id,
            'away_score': away_score,
            'home_score': home_score,
            'current_period': current_period,
            'period_type': period_type,
            'time_remaining': time_remaining,
            'game_state': boxscore.get('gameState', 'LIVE'),
            'stats': {},
            'period_stats': {},
            'player_stats': {},
            'advanced_metrics': {}
        }
        
        try:
            # Calculate xG and other advanced metrics
            if game_data.get('play_by_play') and away_id and home_id:
                away_xg, home_xg = report_generator._calculate_xg_from_plays(game_data)
                away_gs_periods, away_xg_periods = report_generator._calculate_period_metrics(game_data, away_id, 'away')
                home_gs_periods, home_xg_periods = report_generator._calculate_period_metrics(game_data, home_id, 'home')
                
                report_data['advanced_metrics'] = {
                    'away_xg': round(away_xg, 2),
                    'home_xg': round(home_xg, 2),
                    'away_gs_by_period': [round(g, 2) for g in away_gs_periods],
                    'home_gs_by_period': [round(g, 2) for g in home_gs_periods],
                    'away_xg_by_period': [round(x, 2) for x in away_xg_periods],
                    'home_xg_by_period': [round(x, 2) for x in home_xg_periods]
                }
                
                # Get period stats
                away_period_stats = report_generator._calculate_real_period_stats(game_data, away_id, 'away')
                home_period_stats = report_generator._calculate_real_period_stats(game_data, home_id, 'home')
                
                report_data['period_stats'] = {
                    'away': away_period_stats,
                    'home': home_period_stats
                }
                
                # Get pass metrics
                away_ew, away_ns, away_bn = report_generator._calculate_pass_metrics(game_data, away_id, 'away')
                home_ew, home_ns, home_bn = report_generator._calculate_pass_metrics(game_data, home_id, 'home')
                
                report_data['advanced_metrics']['pass_metrics'] = {
                    'away': {'east_west': away_ew, 'north_south': away_ns, 'behind_net': away_bn},
                    'home': {'east_west': home_ew, 'north_south': home_ns, 'behind_net': home_bn}
                }
        
        except Exception as e:
            print(f"Error calculating advanced metrics: {e}")
        
        # Extract team stats - use report generator's method which handles all cases
        try:
            # First try direct boxscore extraction
            away_team_stats = {}
            home_team_stats = {}
            
            # Path 1: teamStats.teamSkaterStats (most common NHL API structure)
            if away_team.get('teamStats', {}).get('teamSkaterStats'):
                away_team_stats = away_team.get('teamStats', {}).get('teamSkaterStats', {})
            elif away_team.get('teamStats'):
                away_team_stats = away_team.get('teamStats', {})
            
            if home_team.get('teamStats', {}).get('teamSkaterStats'):
                home_team_stats = home_team.get('teamStats', {}).get('teamSkaterStats', {})
            elif home_team.get('teamStats'):
                home_team_stats = home_team.get('teamStats', {})
            
            # If not found, use report generator's method to calculate from play-by-play
            if not away_team_stats or not home_team_stats:
                try:
                    # Use report generator's method which calculates from play-by-play
                    away_stats_pbp = report_generator._calculate_team_stats_from_play_by_play(game_data, 'awayTeam')
                    home_stats_pbp = report_generator._calculate_team_stats_from_play_by_play(game_data, 'homeTeam')
                    
                    # Convert to our format
                    if away_stats_pbp and not away_team_stats:
                        away_team_stats = {
                            'shots': away_stats_pbp.get('shotsOnGoal', 0),
                            'hits': away_stats_pbp.get('hits', 0),
                            'pim': away_stats_pbp.get('penaltyMinutes', 0),
                            'faceOffWins': away_stats_pbp.get('faceoffWins', 0),
                            'faceOffTaken': away_stats_pbp.get('faceoffTotal', 0),
                            'powerPlayGoals': away_stats_pbp.get('powerPlayGoals', 0),
                            'powerPlayOpportunities': away_stats_pbp.get('powerPlayOpportunities', 0),
                            'blocked': away_stats_pbp.get('blockedShots', 0),
                            'giveaways': away_stats_pbp.get('giveaways', 0),
                            'takeaways': away_stats_pbp.get('takeaways', 0)
                        }
                    
                    if home_stats_pbp and not home_team_stats:
                        home_team_stats = {
                            'shots': home_stats_pbp.get('shotsOnGoal', 0),
                            'hits': home_stats_pbp.get('hits', 0),
                            'pim': home_stats_pbp.get('penaltyMinutes', 0),
                            'faceOffWins': home_stats_pbp.get('faceoffWins', 0),
                            'faceOffTaken': home_stats_pbp.get('faceoffTotal', 0),
                            'powerPlayGoals': home_stats_pbp.get('powerPlayGoals', 0),
                            'powerPlayOpportunities': home_stats_pbp.get('powerPlayOpportunities', 0),
                            'blocked': home_stats_pbp.get('blockedShots', 0),
                            'giveaways': home_stats_pbp.get('giveaways', 0),
                            'takeaways': home_stats_pbp.get('takeaways', 0)
                        }
                except Exception as e:
                    print(f"Error calculating stats from play-by-play: {e}")
                    # Final fallback: calculate from player data
                    try:
                        player_by_game = boxscore.get('playerByGameStats', {})
                        if player_by_game:
                            away_players = player_by_game.get('away', {})
                            home_players = player_by_game.get('home', {})
                            
                            def calc_team_from_players(players):
                                stats = {
                                    'shots': 0, 'hits': 0, 'pim': 0,
                                    'faceOffWins': 0, 'faceOffTaken': 0,
                                    'powerPlayGoals': 0, 'powerPlayOpportunities': 0,
                                    'blocked': 0, 'giveaways': 0, 'takeaways': 0
                                }
                                for pos_group in ['forwards', 'defense', 'goalies']:
                                    if pos_group in players:
                                        for player in players[pos_group]:
                                            stats['shots'] += player.get('shots', 0) or player.get('sog', 0)
                                            stats['hits'] += player.get('hits', 0)
                                            stats['pim'] += player.get('pim', 0) or player.get('penaltyMinutes', 0)
                                            stats['blocked'] += player.get('blockedShots', 0) or player.get('blocked', 0)
                                            stats['giveaways'] += player.get('giveaways', 0)
                                            stats['takeaways'] += player.get('takeaways', 0)
                                            stats['powerPlayGoals'] += player.get('powerPlayGoals', 0)
                                            fo_wins = player.get('faceoffWins', 0) or player.get('faceOffWins', 0)
                                            fo_taken = player.get('faceoffTaken', 0) or player.get('faceOffTaken', 0)
                                            stats['faceOffWins'] += fo_wins
                                            stats['faceOffTaken'] += fo_taken
                                return stats
                            
                            if not away_team_stats and away_players:
                                away_team_stats = calc_team_from_players(away_players)
                            if not home_team_stats and home_players:
                                home_team_stats = calc_team_from_players(home_players)
                    except Exception as e2:
                        print(f"Error calculating stats from players: {e2}")
            
            # Calculate faceoff totals - use actual totals from stats
            away_fo_wins = away_team_stats.get('faceOffWins') or away_team_stats.get('faceoffWins') or 0
            home_fo_wins = home_team_stats.get('faceOffWins') or home_team_stats.get('faceoffWins') or 0
            away_fo_taken = away_team_stats.get('faceOffTaken') or away_team_stats.get('faceoffTaken') or 0
            home_fo_taken = home_team_stats.get('faceOffTaken') or home_team_stats.get('faceoffTaken') or 0
            
            # If totals are missing, calculate from wins (total = away wins + home wins)
            if away_fo_taken == 0 and home_fo_taken == 0:
                total_faceoffs = away_fo_wins + home_fo_wins
                if total_faceoffs > 0:
                    # Total faceoffs = sum of wins from both teams
                    away_fo_total = total_faceoffs  # Each team takes all faceoffs
                    home_fo_total = total_faceoffs
                else:
                    away_fo_total = 0
                    home_fo_total = 0
            elif away_fo_taken == 0:
                # If away total missing, use home total (they should be the same)
                away_fo_total = home_fo_taken
                home_fo_total = home_fo_taken
            elif home_fo_taken == 0:
                # If home total missing, use away total
                away_fo_total = away_fo_taken
                home_fo_total = away_fo_taken
            else:
                # Both totals available
                away_fo_total = away_fo_taken
                home_fo_total = home_fo_taken
            
            report_data['stats'] = {
                'away': {
                    'shots': away_team_stats.get('shots') or away_team_stats.get('sog') or 0,
                    'hits': away_team_stats.get('hits') or 0,
                    'pim': away_team_stats.get('pim') or 0,
                    'faceoff_wins': away_fo_wins,
                    'faceoff_total': away_fo_total,
                    'power_play_goals': away_team_stats.get('powerPlayGoals') or away_team_stats.get('ppGoals') or 0,
                    'power_play_opportunities': away_team_stats.get('powerPlayOpportunities') or away_team_stats.get('ppOpportunities') or 0,
                    'blocked_shots': away_team_stats.get('blocked') or away_team_stats.get('blockedShots') or 0,
                    'giveaways': away_team_stats.get('giveaways') or 0,
                    'takeaways': away_team_stats.get('takeaways') or 0
                },
                'home': {
                    'shots': home_team_stats.get('shots') or home_team_stats.get('sog') or 0,
                    'hits': home_team_stats.get('hits') or 0,
                    'pim': home_team_stats.get('pim') or 0,
                    'faceoff_wins': home_fo_wins,
                    'faceoff_total': home_fo_total,
                    'power_play_goals': home_team_stats.get('powerPlayGoals') or home_team_stats.get('ppGoals') or 0,
                    'power_play_opportunities': home_team_stats.get('powerPlayOpportunities') or home_team_stats.get('ppOpportunities') or 0,
                    'blocked_shots': home_team_stats.get('blocked') or home_team_stats.get('blockedShots') or 0,
                    'giveaways': home_team_stats.get('giveaways') or 0,
                    'takeaways': home_team_stats.get('takeaways') or 0
                }
            }
            
            # Calculate percentages - only if we have valid data
            # For faceoffs: percentage = wins / total faceoffs taken by that team
            away_fo_pct = 0.0
            home_fo_pct = 0.0
            if report_data['stats']['away']['faceoff_total'] > 0:
                away_fo_pct = (report_data['stats']['away']['faceoff_wins'] / 
                              report_data['stats']['away']['faceoff_total']) * 100
            if report_data['stats']['home']['faceoff_total'] > 0:
                home_fo_pct = (report_data['stats']['home']['faceoff_wins'] / 
                              report_data['stats']['home']['faceoff_total']) * 100
            
            report_data['stats']['away']['faceoff_pct'] = round(away_fo_pct, 1) if away_fo_pct > 0 else 0.0
            report_data['stats']['home']['faceoff_pct'] = round(home_fo_pct, 1) if home_fo_pct > 0 else 0.0
            
            # For power play: percentage = goals / opportunities
            away_pp_pct = 0.0
            home_pp_pct = 0.0
            away_pp_opps = report_data['stats']['away']['power_play_opportunities']
            home_pp_opps = report_data['stats']['home']['power_play_opportunities']
            
            if away_pp_opps > 0:
                away_pp_pct = (report_data['stats']['away']['power_play_goals'] / away_pp_opps) * 100
            if home_pp_opps > 0:
                home_pp_pct = (report_data['stats']['home']['power_play_goals'] / home_pp_opps) * 100
            
            report_data['stats']['away']['power_play_pct'] = round(away_pp_pct, 1) if away_pp_pct > 0 else 0.0
            report_data['stats']['home']['power_play_pct'] = round(home_pp_pct, 1) if home_pp_pct > 0 else 0.0
            
        except Exception as e:
            print(f"Error extracting team stats: {e}")
        
        # Get goalie stats
        try:
            away_goalies = away_team.get('goalies', [])
            home_goalies = home_team.get('goalies', [])
            
            report_data['goalie_stats'] = {
                'away': [],
                'home': []
            }
            
            for goalie in away_goalies:
                goalie_data = goalie.get('playerStats', {})
                report_data['goalie_stats']['away'].append({
                    'name': goalie.get('name', {}).get('default', 'Unknown'),
                    'saves': goalie_data.get('saves', 0),
                    'shots_against': goalie_data.get('shotsAgainst', 0),
                    'save_pct': round((goalie_data.get('saves', 0) / max(1, goalie_data.get('shotsAgainst', 1))) * 100, 2),
                    'toi': goalie_data.get('timeOnIce', '0:00')
                })
            
            for goalie in home_goalies:
                goalie_data = goalie.get('playerStats', {})
                report_data['goalie_stats']['home'].append({
                    'name': goalie.get('name', {}).get('default', 'Unknown'),
                    'saves': goalie_data.get('saves', 0),
                    'shots_against': goalie_data.get('shotsAgainst', 0),
                    'save_pct': round((goalie_data.get('saves', 0) / max(1, goalie_data.get('shotsAgainst', 1))) * 100, 2),
                    'toi': goalie_data.get('timeOnIce', '0:00')
                })
        
        except Exception as e:
            print(f"Error extracting goalie stats: {e}")
        
        # Create player roster map for name lookups
        player_roster_map = {}
        try:
            pbp = game_data.get('play_by_play', {})
            if pbp and 'rosterSpots' in pbp:
                for player in pbp['rosterSpots']:
                    player_id = str(player.get('playerId') or player.get('id') or player.get('personId', ''))
                    if player_id:
                        # Build name from firstName/lastName
                        first_name = ''
                        last_name = ''
                        if player.get('firstName'):
                            if isinstance(player['firstName'], dict):
                                first_name = player['firstName'].get('default', '')
                            else:
                                first_name = str(player['firstName'])
                        if player.get('lastName'):
                            if isinstance(player['lastName'], dict):
                                last_name = player['lastName'].get('default', '')
                            else:
                                last_name = str(player['lastName'])
                        
                        full_name = f"{first_name} {last_name}".strip()
                        if full_name:
                            player_roster_map[player_id] = full_name
        except Exception as e:
            print(f"Error creating player roster map: {e}")
        
        # Get scoring summary
        try:
            scoring_plays = []
            pbp = game_data.get('play_by_play', {})
            
            # Try different play-by-play structures
            plays = []
            if isinstance(pbp, dict):
                plays = pbp.get('plays', []) or pbp.get('events', []) or []
            elif isinstance(pbp, list):
                plays = pbp
            
            for play in plays:
                # Check if it's a goal - try multiple keys
                is_goal = (
                    play.get('typeDescKey') == 'goal' or 
                    play.get('type') == 'goal' or
                    play.get('eventTypeId') == 'GOAL' or
                    play.get('result', {}).get('eventTypeId') == 'GOAL'
                )
                
                if is_goal:
                    # Extract period info
                    period_desc = play.get('periodDescriptor') or play.get('period') or {}
                    period_num = period_desc.get('number') if isinstance(period_desc, dict) else (period_desc if isinstance(period_desc, int) else play.get('period', 1))
                    
                    # Extract time
                    time_str = play.get('timeInPeriod') or play.get('timeRemaining') or play.get('time', '')
                    
                    # Extract details first
                    details = play.get('details', {})
                    
                    # Extract team - try multiple paths
                    team_id = (
                        details.get('eventOwnerTeamId') or
                        play.get('team', {}).get('id') or
                        play.get('teamId') or
                        play.get('eventOwnerTeam', {}).get('id') or
                        details.get('scoringTeamId')
                    )
                    
                    # Convert to int for comparison if needed
                    if team_id:
                        try:
                            team_id = int(team_id)
                        except:
                            pass
                    
                    # Extract scorer - try multiple paths
                    scorer_name = 'Unknown'
                    
                    # Try scoringPlayerName (most common) - NHL API structure
                    if details.get('scoringPlayerName'):
                        scorer_name_obj = details['scoringPlayerName']
                        if isinstance(scorer_name_obj, dict):
                            # Try all possible name fields
                            scorer_name = (
                                scorer_name_obj.get('default') or 
                                scorer_name_obj.get('fullName') or 
                                (scorer_name_obj.get('firstName', '') + ' ' + scorer_name_obj.get('lastName', '')).strip() or
                                scorer_name_obj.get('lastName') or
                                'Unknown'
                            )
                        else:
                            scorer_name = str(scorer_name_obj) if scorer_name_obj else 'Unknown'
                    
                    # Look up player name from roster map using player ID
                    if scorer_name == 'Unknown' or scorer_name.startswith('Player #'):
                        player_id = str(details.get('scoringPlayerId') or details.get('playerId') or '')
                        if player_id and player_id in player_roster_map:
                            scorer_name = player_roster_map[player_id]
                        elif player_id:
                            scorer_name = f"Player #{player_id}"
                    # Try other possible fields
                    if scorer_name == 'Unknown' and details.get('scorer'):
                        scorer_obj = details['scorer']
                        if isinstance(scorer_obj, dict):
                            scorer_name = scorer_obj.get('fullName') or scorer_obj.get('name', {}).get('default', 'Unknown') if isinstance(scorer_obj.get('name'), dict) else 'Unknown'
                        else:
                            scorer_name = str(scorer_obj)
                    elif play.get('player', {}).get('fullName'):
                        scorer_name = play['player']['fullName']
                    
                    # Extract assists - NHL API uses assist1PlayerName and assist2PlayerName
                    assists = []
                    assist1 = details.get('assist1PlayerName')
                    assist2 = details.get('assist2PlayerName')
                    
                    # Also try assistDetails array
                    assist_details = details.get('assistDetails', [])
                    
                    # Process assist1 - try name first, then lookup by ID
                    if assist1:
                        assist_name = ''
                        if isinstance(assist1, dict):
                            assist_name = (
                                assist1.get('default') or 
                                assist1.get('fullName') or 
                                (assist1.get('firstName', '') + ' ' + assist1.get('lastName', '')).strip() or
                                assist1.get('lastName') or
                                ''
                            )
                        else:
                            assist_name = str(assist1) if assist1 else ''
                        
                        # If no name, try looking up by assist1PlayerId
                        if not assist_name or assist_name == 'Unknown':
                            assist_id = str(details.get('assist1PlayerId') or '')
                            if assist_id and assist_id in player_roster_map:
                                assist_name = player_roster_map[assist_id]
                        
                        if assist_name and assist_name != 'Unknown' and assist_name.strip() and not assist_name.startswith('Player #'):
                            assists.append(assist_name)
                    
                    # Process assist2 - try name first, then lookup by ID
                    if assist2:
                        assist_name = ''
                        if isinstance(assist2, dict):
                            assist_name = (
                                assist2.get('default') or 
                                assist2.get('fullName') or 
                                (assist2.get('firstName', '') + ' ' + assist2.get('lastName', '')).strip() or
                                assist2.get('lastName') or
                                ''
                            )
                        else:
                            assist_name = str(assist2) if assist2 else ''
                        
                        # If no name, try looking up by assist2PlayerId
                        if not assist_name or assist_name == 'Unknown':
                            assist_id = str(details.get('assist2PlayerId') or '')
                            if assist_id and assist_id in player_roster_map:
                                assist_name = player_roster_map[assist_id]
                        
                        if assist_name and assist_name != 'Unknown' and assist_name.strip() and not assist_name.startswith('Player #'):
                            assists.append(assist_name)
                    
                    # Extract shot type
                    shot_type = details.get('shotType', 'wrist').title() or 'Wrist'
                    
                    # Calculate xG for this goal
                    play_index = -1
                    try:
                        play_index = plays.index(play)
                    except:
                        pass
                    
                    xg_value = 0.0
                    try:
                        # Get previous events for context (rebounds, rushes)
                        if play_index >= 0:
                            previous_events = plays[max(0, play_index-10):play_index]
                        else:
                            previous_events = []
                        xg_value = report_generator._calculate_shot_xg(details, 'goal', play, previous_events)
                    except Exception as e:
                        print(f"Error calculating xG: {e}")
                        xg_value = 0.0
                    
                    # Get coordinates for shot chart
                    x_coord = details.get('xCoord', 0)
                    y_coord = details.get('yCoord', 0)
                    
                    # Calculate longitudinal (north-south) and lateral (east-west) movement
                    # Get previous shot/play coordinates to calculate movement
                    longitudinal_movement = 0
                    lateral_movement = 0
                    try:
                        if play_index > 0:
                            prev_play = plays[play_index - 1]
                            prev_details = prev_play.get('details', {})
                            prev_x = prev_details.get('xCoord', 0)
                            prev_y = prev_details.get('yCoord', 0)
                            if prev_x and prev_y and x_coord and y_coord:
                                # Lateral = X movement (east-west)
                                lateral_movement = abs(x_coord - prev_x)
                                # Longitudinal = Y movement (north-south)
                                longitudinal_movement = abs(y_coord - prev_y)
                    except:
                        pass
                    
                    # Process assistDetails array if available
                    for assist in assist_details:
                        if isinstance(assist, dict):
                            assist_name = assist.get('playerName', {})
                            if isinstance(assist_name, dict):
                                assist_name = assist_name.get('default') or assist_name.get('fullName', '')
                            else:
                                assist_name = assist.get('playerName') or assist.get('fullName', '')
                        else:
                            assist_name = str(assist)
                        if assist_name and assist_name != 'Unknown' and assist_name not in assists:
                            assists.append(assist_name)
                    
                    # Also try looking up assists by ID if we have IDs but no names
                    assist1_id = details.get('assist1PlayerId')
                    assist2_id = details.get('assist2PlayerId')
                    if assist1_id and str(assist1_id) in player_roster_map:
                        assist_name = player_roster_map[str(assist1_id)]
                        if assist_name and assist_name not in assists:
                            assists.append(assist_name)
                    if assist2_id and str(assist2_id) in player_roster_map:
                        assist_name = player_roster_map[str(assist2_id)]
                        if assist_name and assist_name not in assists:
                            assists.append(assist_name)
                    
                    # Determine team abbreviation - ensure proper comparison
                    team_abbrev = away_abbrev
                    is_away_goal = False
                    if team_id:
                        # Convert both to strings for comparison
                        team_id_str = str(team_id)
                        away_id_str = str(away_id)
                        home_id_str = str(home_id)
                        
                        if team_id_str == away_id_str:
                            team_abbrev = away_abbrev
                            is_away_goal = True
                        elif team_id_str == home_id_str:
                            team_abbrev = home_abbrev
                            is_away_goal = False
                        else:
                            # Fallback: use coordinates to determine team
                            if x_coord and x_coord < 0:
                                team_abbrev = away_abbrev
                                is_away_goal = True
                            else:
                                team_abbrev = home_abbrev
                                is_away_goal = False
                    else:
                        # Fallback: use coordinates to determine team
                        if x_coord and x_coord < 0:
                            team_abbrev = away_abbrev
                            is_away_goal = True
                        else:
                            team_abbrev = home_abbrev
                            is_away_goal = False
                    
                    # Apply coordinate flipping logic like post-game reports
                    # Away team: Always left side (negative X), Home team: Always right side (positive X)
                    plot_x = x_coord
                    plot_y = y_coord
                    if is_away_goal:
                        # Away team goals - force to left side
                        if x_coord > 0:  # If goal is on right side, flip to left
                            plot_x = -x_coord
                            plot_y = -y_coord
                    else:
                        # Home team goals - force to right side
                        if x_coord < 0:  # If goal is on left side, flip to right
                            plot_x = -x_coord
                            plot_y = -y_coord
                    
                    # Get team color for this goal
                    team_color = report_generator._get_team_color(team_abbrev)
                    
                    scoring_plays.append({
                        'period': period_num,
                        'time': time_str,
                        'team': team_abbrev,
                        'scorer': scorer_name,
                        'assists': ', '.join(assists) if assists else 'Unassisted',
                        'xg': round(xg_value, 3),
                        'shot_type': shot_type,
                        'x_coord': plot_x,  # Use flipped coordinates for plotting
                        'y_coord': plot_y,
                        'team_id': team_id,  # Store original team_id for reference
                        'is_away': is_away_goal,
                        'team_color': team_color,  # Store team color for plotting
                        'longitudinal_movement': round(longitudinal_movement, 1) if longitudinal_movement else 0,
                        'lateral_movement': round(lateral_movement, 1) if lateral_movement else 0
                    })
            
            report_data['scoring_summary'] = scoring_plays
        
        except Exception as e:
            print(f"Error extracting scoring summary: {e}")
            import traceback
            traceback.print_exc()
        
        return jsonify(report_data)
    
    except Exception as e:
        print(f"Error getting live game report: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    print("🏒 Starting Prediction Dashboard...")
    print(f"📊 Access at: http://localhost:{port}")
    app.run(debug=debug, host='0.0.0.0', port=port, threaded=True)

