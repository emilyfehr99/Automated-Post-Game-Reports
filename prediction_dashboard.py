#!/usr/bin/env python3
"""
Fast Mini Site for Viewing Pre-Game and In-Game Predictions
"""

from flask import Flask, render_template, jsonify
from datetime import datetime, timedelta
import pytz
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
                
                # Get live prediction if game is live
                if game_data['is_live']:
                    live = get_live_prediction(game_id)
                    if live:
                        game_data['live_prediction'] = live
                        # Update scores from live data
                        game_data['away_score'] = live['away_score']
                        game_data['home_score'] = live['home_score']
                        game_data['current_period'] = live['current_period']
                        game_data['time_remaining'] = live['time_remaining']
                
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


@app.route('/api/game/<game_id>/report')
def get_live_game_report(game_id):
    """Get detailed live game report with comprehensive stats"""
    try:
        # Get comprehensive game data
        game_data = api.get_comprehensive_game_data(game_id)
        if not game_data:
            return jsonify({'error': 'Could not fetch game data'}), 404
        
        # Extract basic game info
        boxscore = game_data.get('boxscore', {})
        if not boxscore:
            return jsonify({'error': 'No boxscore data available'}), 404
        
        away_team = boxscore.get('awayTeam', {})
        home_team = boxscore.get('homeTeam', {})
        
        away_abbrev = away_team.get('abbrev', '')
        home_abbrev = home_team.get('abbrev', '')
        away_id = away_team.get('id')
        home_id = home_team.get('id')
        
        # Get current scores and stats
        away_score = away_team.get('score', 0)
        home_score = home_team.get('score', 0)
        
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
        
        # Extract team stats from boxscore - try multiple possible paths
        try:
            # Try different possible paths for stats
            away_team_stats = {}
            home_team_stats = {}
            
            # Path 1: teamStats.teamSkaterStats
            if away_team.get('teamStats', {}).get('teamSkaterStats'):
                away_team_stats = away_team.get('teamStats', {}).get('teamSkaterStats', {})
            # Path 2: teamStats directly
            elif away_team.get('teamStats'):
                away_team_stats = away_team.get('teamStats', {})
            # Path 3: stats directly on team
            elif away_team.get('stats'):
                away_team_stats = away_team.get('stats', {})
            
            if home_team.get('teamStats', {}).get('teamSkaterStats'):
                home_team_stats = home_team.get('teamStats', {}).get('teamSkaterStats', {})
            elif home_team.get('teamStats'):
                home_team_stats = home_team.get('teamStats', {})
            elif home_team.get('stats'):
                home_team_stats = home_team.get('stats', {})
            
            # Also try getting from boxscore directly if available
            if not away_team_stats and boxscore.get('awayTeam', {}).get('teamStats'):
                away_team_stats = boxscore.get('awayTeam', {}).get('teamStats', {}).get('teamSkaterStats', {})
            if not home_team_stats and boxscore.get('homeTeam', {}).get('teamStats'):
                home_team_stats = boxscore.get('homeTeam', {}).get('teamStats', {}).get('teamSkaterStats', {})
            
            report_data['stats'] = {
                'away': {
                    'shots': away_team_stats.get('shots') or away_team_stats.get('sog') or 0,
                    'hits': away_team_stats.get('hits') or 0,
                    'pim': away_team_stats.get('pim') or 0,
                    'faceoff_wins': away_team_stats.get('faceOffWins') or away_team_stats.get('faceoffWins') or 0,
                    'faceoff_total': away_team_stats.get('faceOffTaken') or away_team_stats.get('faceoffTaken') or (away_team_stats.get('faceOffWins', 0) + away_team_stats.get('faceoffWins', 0)),
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
                    'faceoff_wins': home_team_stats.get('faceOffWins') or home_team_stats.get('faceoffWins') or 0,
                    'faceoff_total': home_team_stats.get('faceOffTaken') or home_team_stats.get('faceoffTaken') or (home_team_stats.get('faceOffWins', 0) + home_team_stats.get('faceoffWins', 0)),
                    'power_play_goals': home_team_stats.get('powerPlayGoals') or home_team_stats.get('ppGoals') or 0,
                    'power_play_opportunities': home_team_stats.get('powerPlayOpportunities') or home_team_stats.get('ppOpportunities') or 0,
                    'blocked_shots': home_team_stats.get('blocked') or home_team_stats.get('blockedShots') or 0,
                    'giveaways': home_team_stats.get('giveaways') or 0,
                    'takeaways': home_team_stats.get('takeaways') or 0
                }
            }
            
            # Calculate percentages
            away_fo_pct = (report_data['stats']['away']['faceoff_wins'] / 
                          max(1, report_data['stats']['away']['faceoff_total'])) * 100
            home_fo_pct = (report_data['stats']['home']['faceoff_wins'] / 
                          max(1, report_data['stats']['home']['faceoff_total'])) * 100
            
            report_data['stats']['away']['faceoff_pct'] = round(away_fo_pct, 1)
            report_data['stats']['home']['faceoff_pct'] = round(home_fo_pct, 1)
            
            away_pp_pct = (report_data['stats']['away']['power_play_goals'] / 
                          max(1, report_data['stats']['away']['power_play_opportunities'])) * 100
            home_pp_pct = (report_data['stats']['home']['power_play_goals'] / 
                          max(1, report_data['stats']['home']['power_play_opportunities'])) * 100
            
            report_data['stats']['away']['power_play_pct'] = round(away_pp_pct, 1)
            report_data['stats']['home']['power_play_pct'] = round(home_pp_pct, 1)
            
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
                    
                    # Extract team - try multiple paths
                    team_id = (
                        play.get('details', {}).get('eventOwnerTeamId') or
                        play.get('team', {}).get('id') or
                        play.get('teamId') or
                        play.get('eventOwnerTeam', {}).get('id')
                    )
                    
                    # Extract scorer - try multiple paths
                    details = play.get('details', {})
                    scorer_name = 'Unknown'
                    if details.get('scoringPlayerName'):
                        if isinstance(details['scoringPlayerName'], dict):
                            scorer_name = details['scoringPlayerName'].get('default') or details['scoringPlayerName'].get('fullName') or 'Unknown'
                        else:
                            scorer_name = details['scoringPlayerName']
                    elif details.get('scorer'):
                        scorer_name = details['scorer'].get('fullName', 'Unknown') if isinstance(details['scorer'], dict) else details['scorer']
                    elif play.get('player', {}).get('fullName'):
                        scorer_name = play['player']['fullName']
                    
                    # Extract assists - try multiple paths
                    assists = []
                    assist_details = details.get('assistDetails', []) or details.get('assists', []) or []
                    for assist in assist_details:
                        if isinstance(assist, dict):
                            assist_name = assist.get('playerName', {}).get('default') if isinstance(assist.get('playerName'), dict) else assist.get('playerName') or assist.get('fullName', '')
                        else:
                            assist_name = str(assist)
                        if assist_name:
                            assists.append(assist_name)
                    
                    scoring_plays.append({
                        'period': period_num,
                        'time': time_str,
                        'team': team_id,
                        'scorer': scorer_name,
                        'assists': assists
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

