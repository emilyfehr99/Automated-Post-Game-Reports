from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
import csv
import io
import requests
from datetime import datetime, timedelta

app = Flask(__name__)
# Enable CORS for React frontend - allows Vercel deployment and localhost
CORS(app, origins=[
    "https://nhl-analytics.vercel.app",  # Production Vercel domain
    "https://*.vercel.app",  # All Vercel preview deployments
    "http://localhost:5173",  # Local development
    "http://localhost:3000"   # Alternative local port
], supports_credentials=True)

# Base directory for data files
DATA_DIR = os.path.dirname(os.path.abspath(__file__))

# Initialize predictor
try:
    from live_in_game_predictions import LiveInGamePredictor
    live_predictor = LiveInGamePredictor()
except ImportError:
    print("Warning: LiveInGamePredictor not found, using mock")
    class MockPredictor:
        def get_live_game_data(self, game_id): return {}
        def predict_live_game(self, metrics): return {}
    live_predictor = MockPredictor()

# Cache for team metrics to avoid recalculating on every request
_team_metrics_cache = None
_team_metrics_cache_time = None
_team_metrics_file_mtime = None
CACHE_DURATION = timedelta(hours=1)  # Cache for 1 hour

def load_json(filename):
    """Load JSON file from current directory"""
    try:
        file_path = os.path.join(DATA_DIR, filename)
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: {filename} not found at {file_path}, returning empty dict")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error decoding {filename}: {e}")
        return {}

def get_file_mtime(filename):
    """Get file modification time"""
    try:
        return os.path.getmtime(os.path.join(DATA_DIR, filename))
    except:
        return None

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/team-stats', methods=['GET'])
def get_team_stats():
    """Get current season team stats with advanced metrics"""
    data = load_json('season_2025_2026_team_stats.json')
    
    # Handle both structures: direct team dict or wrapped in 'teams' key
    if 'teams' in data:
        return jsonify(data['teams'])
    return jsonify(data)

@app.route('/api/team-stats/<team_abbrev>', methods=['GET'])
def get_team_stats_by_abbrev(team_abbrev):
    """Get stats for specific team"""
    data = load_json('season_2025_2026_team_stats.json')
    
    # Handle both structures
    teams = data.get('teams', data)
    team_data = teams.get(team_abbrev.upper(), {})
    return jsonify(team_data)

@app.route('/api/team-metrics', methods=['GET'])
def get_team_metrics():
    """Get aggregated team metrics for all teams (for Metrics page)
    Uses caching to avoid recalculating on every request.
    Cache is invalidated when the source file is modified or after 1 hour.
    """
    global _team_metrics_cache, _team_metrics_cache_time, _team_metrics_file_mtime
    
    filename = 'season_2025_2026_team_stats.json'
    current_mtime = get_file_mtime(filename)
    current_time = datetime.now()
    
    # Check if cache is valid
    cache_valid = (
        _team_metrics_cache is not None and
        _team_metrics_cache_time is not None and
        _team_metrics_file_mtime is not None and
        current_mtime == _team_metrics_file_mtime and
        (current_time - _team_metrics_cache_time) < CACHE_DURATION
    )
    
    if cache_valid:
        print(f"Returning cached team metrics (age: {(current_time - _team_metrics_cache_time).seconds}s)")
        return jsonify(_team_metrics_cache)
    
    print("Calculating fresh team metrics...")
    data = load_json(filename)
    
    # Handle both structures
    teams = data.get('teams', data)
    
    # Helper function to calculate average from list
    def avg(lst):
        if not lst or len(lst) == 0:
            return 0
        # Filter out non-numeric values
        numeric_values = [x for x in lst if isinstance(x, (int, float))]
        if len(numeric_values) == 0:
            return 0
        return sum(numeric_values) / len(numeric_values)
    
    # Transform to format expected by Metrics page
    # Calculate averages from home/away stats (which are lists)
    metrics = {}
    for team_abbrev, team_data in teams.items():
        # Structure is: teams.EDM.home and teams.EDM.away
        # Each metric is a list of values (one per game)
        home_stats = team_data.get('home', {})
        away_stats = team_data.get('away', {})
        
        # Calculate averages from lists
        home_gs = avg(home_stats.get('gs', []))
        away_gs = avg(away_stats.get('gs', []))
        
        home_nzt = avg(home_stats.get('nzt', []))
        away_nzt = avg(away_stats.get('nzt', []))
        
        home_ozs = avg(home_stats.get('ozs', []))
        away_ozs = avg(away_stats.get('ozs', []))
        
        home_nzs = avg(home_stats.get('nzs', []))
        away_nzs = avg(away_stats.get('nzs', []))
        
        home_dzs = avg(home_stats.get('period_dzs', []))  # Using period_dzs
        away_dzs = avg(away_stats.get('period_dzs', []))
        
        home_fc = avg(home_stats.get('fc', []))
        away_fc = avg(away_stats.get('fc', []))
        
        home_rush = avg(home_stats.get('rush', []))
        away_rush = avg(away_stats.get('rush', []))
        
        # Additional metrics
        home_lat = avg(home_stats.get('lat', []))
        away_lat = avg(away_stats.get('lat', []))
        
        home_long = avg(home_stats.get('long_movement', []))
        away_long = avg(away_stats.get('long_movement', []))
        
        home_nztsa = avg(home_stats.get('nztsa', []))
        away_nztsa = avg(away_stats.get('nztsa', []))
        
        home_xg = avg(home_stats.get('xg', []))
        away_xg = avg(away_stats.get('xg', []))
        
        home_hdc = avg(home_stats.get('hdc', []))
        away_hdc = avg(away_stats.get('hdc', []))

        home_hdca = avg(home_stats.get('hdca', []))
        away_hdca = avg(away_stats.get('hdca', []))
        
        home_corsi = avg(home_stats.get('corsi_pct', []))
        away_corsi = avg(away_stats.get('corsi_pct', []))
        
        home_shots = avg(home_stats.get('shots', []))
        away_shots = avg(away_stats.get('shots', []))
        
        home_goals = avg(home_stats.get('goals', []))
        away_goals = avg(away_stats.get('goals', []))
        
        home_hits = avg(home_stats.get('hits', []))
        away_hits = avg(away_stats.get('hits', []))
        
        home_blocks = avg(home_stats.get('blocked_shots', []))
        away_blocks = avg(away_stats.get('blocked_shots', []))
        
        home_giveaways = avg(home_stats.get('giveaways', []))
        away_giveaways = avg(away_stats.get('giveaways', []))
        
        home_takeaways = avg(home_stats.get('takeaways', []))
        away_takeaways = avg(away_stats.get('takeaways', []))
        
        home_pim = avg(home_stats.get('penalty_minutes', []))
        away_pim = avg(away_stats.get('penalty_minutes', []))
        
        home_pp_pct = avg(home_stats.get('power_play_pct', []))
        away_pp_pct = avg(away_stats.get('power_play_pct', []))
        
        home_pk_pct = avg(home_stats.get('penalty_kill_pct', []))
        away_pk_pct = avg(away_stats.get('penalty_kill_pct', []))
        
        home_fo_pct = avg(home_stats.get('faceoff_pct', []))
        away_fo_pct = avg(away_stats.get('faceoff_pct', []))

        home_ga = avg(home_stats.get('goals_against', []))
        away_ga = avg(away_stats.get('goals_against', []))
        
        # Average home and away stats
        metrics[team_abbrev] = {
            # Core advanced metrics
            'gs': round((home_gs + away_gs) / 2, 1),
            'nzts': round((home_nzt + away_nzt) / 2),  # nzt = neutral zone turnovers
            'nztsa': round((home_nztsa + away_nztsa) / 2, 1),  # neutral zone turnovers to shots against
            'ozs': round((home_ozs + away_ozs) / 2),
            'nzs': round((home_nzs + away_nzs) / 2),
            'dzs': round((home_dzs + away_dzs) / 2),
            'fc': round((home_fc + away_fc) / 2),
            'rush': round((home_rush + away_rush) / 2),
            
            # Movement metrics
            'lat': round((home_lat + away_lat) / 2, 1),
            'long_movement': round((home_long + away_long) / 2, 1),
            
            # Shooting metrics
            'xg': round((home_xg + away_xg) / 2, 2),
            'hdc': round((home_hdc + away_hdc) / 2, 1),
            'hdca': round((home_hdca + away_hdca) / 2, 1),
            'shots': round((home_shots + away_shots) / 2, 1),
            'goals': round((home_goals + away_goals) / 2, 2),
            'ga_gp': round((home_ga + away_ga) / 2, 2),
            
            # Possession metrics
            'corsi_pct': round((home_corsi + away_corsi) / 2, 1),
            
            # Physical metrics
            'hits': round((home_hits + away_hits) / 2, 1),
            'blocks': round((home_blocks + away_blocks) / 2, 1),
            'giveaways': round((home_giveaways + away_giveaways) / 2, 1),
            'takeaways': round((home_takeaways + away_takeaways) / 2, 1),
            'pim': round((home_pim + away_pim) / 2, 1),
            
            # Special teams
            'pp_pct': round((home_pp_pct + away_pp_pct) / 2, 1),
            'pk_pct': round((home_pk_pct + away_pk_pct) / 2, 1),
            'fo_pct': round((home_fo_pct + away_fo_pct) / 2, 1),
            
            # Meta
            'gamesProcessed': len(home_stats.get('games', [])) + len(away_stats.get('games', [])),
            'l10': team_data.get('l10Wins', 0), # Fallback if not in data
            'streak': team_data.get('streakCode', '') + str(team_data.get('streakCount', ''))
        }
    
    # Cache the results
    _team_metrics_cache = metrics
    _team_metrics_cache_time = current_time
    _team_metrics_file_mtime = current_mtime
    
    return jsonify(metrics)

@app.route('/api/team-heatmap/<team_abbr>', methods=['GET'])
def get_team_heatmap(team_abbr):
    """Get aggregated shot data for team heatmap"""
    try:
        from nhl_api_client import NHLAPIClient
        client = NHLAPIClient()
        
        # Team ID mapping (copied from client for reliability)
        team_ids = {
            'FLA': 13, 'EDM': 22, 'BOS': 6, 'TOR': 10, 'MTL': 8, 'OTT': 9,
            'BUF': 7, 'DET': 17, 'TBL': 14, 'CAR': 12, 'WSH': 15, 'PIT': 5,
            'NYR': 3, 'NYI': 2, 'NJD': 1, 'PHI': 4, 'CBJ': 29, 'NSH': 18,
            'STL': 19, 'MIN': 30, 'WPG': 52, 'COL': 21, 'ARI': 53, 'VGK': 54,
            'SJS': 28, 'LAK': 26, 'ANA': 24, 'CGY': 20, 'VAN': 23, 'SEA': 55,
            'CHI': 16, 'DAL': 25, 'UTA': 59
        }
        target_team_id = team_ids.get(team_abbr.upper())
        
        # Get recent games (increased to 10)
        game_ids = client.get_team_recent_games(team_abbr, limit=10)
        
        # Get roster for player name mapping
        roster = client.get_team_roster(team_abbr)
        player_names = {}
        if roster:
            for position in ['forwards', 'defensemen', 'goalies']:
                for player in roster.get(position, []):
                    player_names[player['id']] = f"{player['firstName']['default']} {player['lastName']['default']}"

        def calculate_xg(x, y, shot_type):
            """
            Estimate xG based on location and shot type.
            Coordinates are from center ice (0,0) to (100, 42.5).
            Net is approx at x=89.
            """
            import math
            
            # Normalize to offensive zone coordinates (0-100)
            # Abs(x) because we don't know which side they are shooting at, but shots are usually recorded relative to net
            # Standardize: Net is at 89, 0
            
            # Distance to net
            # If x is negative, it might be the other side, but usually API returns coordinates relative to rink center
            # We'll assume offensive zone logic: closer to 89 is closer to net
            
            # Simple distance calculation from (89, 0)
            # x is usually -100 to 100. 
            
            # Use absolute x to treat both sides symmetrically if needed, 
            # but usually we care about distance to NEAREST net.
            # Net locations are -89 and 89.
            
            dist_to_right_net = math.sqrt((89 - x)**2 + y**2)
            dist_to_left_net = math.sqrt((-89 - x)**2 + y**2)
            
            distance = min(dist_to_right_net, dist_to_left_net)
            
            # Base probability based on distance
            # Exponential decay: P = 0.4 * e^(-0.05 * distance)
            # At 0ft: 0.4
            # At 10ft: 0.24
            # At 20ft: 0.14
            # At 40ft: 0.05
            prob = 0.4 * math.exp(-0.05 * distance)
            
            # Adjust for shot type
            multipliers = {
                'tip-in': 1.5,
                'deflected': 1.3,
                'slap': 0.8,  # Often further away
                'snap': 1.0,
                'wrist': 1.0,
                'backhand': 0.9,
                'wrap-around': 1.2
            }
            
            shot_type_key = str(shot_type).lower() if shot_type else 'wrist'
            mult = multipliers.get(shot_type_key, 1.0)
            
            # Bonus for central angle (closer to y=0)
            angle_mult = 1.0
            if abs(y) < 10:
                angle_mult = 1.2
            elif abs(y) > 20:
                angle_mult = 0.8
                
            return min(0.99, prob * mult * angle_mult)

        shots_for = []
        goals_for = []
        shots_against = []
        goals_against = []
        
        for game_id in game_ids:
            # Get play-by-play for each game
            pbp = client.get_play_by_play(game_id)
            
            if not pbp:
                continue
                
            for play in pbp.get('plays', []):
                details = play.get('details', {})
                if not details:
                    continue
                    
                x = details.get('xCoord')
                y = details.get('yCoord')
                event_owner_id = details.get('eventOwnerTeamId')
                
                if x is None or y is None or event_owner_id is None:
                    continue
                
                is_for = (int(event_owner_id) == int(target_team_id)) if target_team_id else True
                
                # Resolve shooter name
                shooter_id = details.get('shootingPlayerId') or details.get('scoringPlayerId')
                shooter_name = details.get('shootingPlayerName') or details.get('scoringPlayerName')
                
                if not shooter_name and shooter_id:
                    shooter_name = player_names.get(shooter_id)
                
                # Calculate xG
                xg = calculate_xg(x, y, details.get('shotType'))
                    
                if play.get('typeDescKey') == 'shot-on-goal':
                    point = {
                        'x': x, 
                        'y': y,
                        'shotType': details.get('shotType'),
                        'shooterId': shooter_id,
                        'shooter': shooter_name,
                        'xg': round(xg, 3)
                    }
                    if is_for:
                        shots_for.append(point)
                    else:
                        shots_against.append(point)
                elif play.get('typeDescKey') == 'goal':
                    point = {
                        'x': x, 
                        'y': y,
                        'shotType': details.get('shotType'),
                        'shooterId': shooter_id,
                        'shooter': shooter_name,
                        'xg': round(xg, 3)
                    }
                    if is_for:
                        goals_for.append(point)
                    else:
                        goals_against.append(point)
                    
        return jsonify({
            'team': team_abbr,
            'games_count': len(game_ids),
            'shots_for': shots_for,
            'goals_for': goals_for,
            'shots_against': shots_against,
            'goals_against': goals_against
        })
        
    except Exception as e:
        print(f"Error generating heatmap for {team_abbr}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/edge-data', methods=['GET'])
def get_edge_data():
    """Get NHL Edge data (skating speeds, distances, bursts)"""
    data = load_json('nhl_edge_data.json')
    return jsonify(data)

@app.route('/api/edge-data/<team_abbrev>', methods=['GET'])
def get_edge_data_by_team(team_abbrev):
    """Get Edge data for specific team"""
    data = load_json('nhl_edge_data.json')
    team_data = data.get(team_abbrev.upper(), {})
    return jsonify(team_data)

@app.route('/api/predictions', methods=['GET'])
def get_predictions():
    """Get all win probability predictions"""
    data = load_json('win_probability_predictions_v2.json')
    return jsonify(data)

@app.route('/api/predictions/today', methods=['GET'])
def get_today_predictions():
    """Get today's game predictions generated dynamically"""
    # Get today's schedule
    today = datetime.now().strftime('%Y-%m-%d')
    try:
        import requests
        url = f"https://api-web.nhle.com/v1/schedule/{today}"
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return jsonify([])
            
        schedule_data = response.json()
        if not schedule_data.get('gameWeek') or not schedule_data['gameWeek'][0].get('games'):
            return jsonify([])
            
        games = schedule_data['gameWeek'][0]['games']
        
        # Load team stats for calculation
        team_stats = {}
        try:
            with open(os.path.join(DATA_DIR, 'season_2025_2026_team_stats.json'), 'r') as f:
                data = json.load(f)
                team_stats = data.get('teams', {})
        except Exception as e:
            print(f"Error loading team stats: {e}")
            
        predictions = []
        
        for game in games:
            away_abbr = game['awayTeam']['abbrev']
            home_abbr = game['homeTeam']['abbrev']
            
            # Calculate win probability based on team stats
            # Simple model: (Home Win % + Away Loss %) / 2 + Home Ice Advantage
            
            away_metrics = team_stats.get(away_abbr, {}).get('away', {})
            home_metrics = team_stats.get(home_abbr, {}).get('home', {})
            
            # Default probability if no stats
            home_prob = 0.55 
            
            if away_metrics and home_metrics:
                # Use xG and Corsi as factors
                home_xg = sum(home_metrics.get('xg', [0])) / len(home_metrics.get('xg', [1])) if home_metrics.get('xg') else 2.5
                away_xg = sum(away_metrics.get('xg', [0])) / len(away_metrics.get('xg', [1])) if away_metrics.get('xg') else 2.5
                
                home_corsi = sum(home_metrics.get('corsi_pct', [0])) / len(home_metrics.get('corsi_pct', [1])) if home_metrics.get('corsi_pct') else 50
                away_corsi = sum(away_metrics.get('corsi_pct', [0])) / len(away_metrics.get('corsi_pct', [1])) if away_metrics.get('corsi_pct') else 50
                
                # Weighted calculation
                xg_factor = (home_xg / (home_xg + away_xg)) * 0.6
                corsi_factor = (home_corsi / (home_corsi + away_corsi)) * 0.4
                
                home_prob = xg_factor + corsi_factor
                # Add small home ice advantage
                home_prob += 0.05
                
                # Clamp
                home_prob = max(0.2, min(0.8, home_prob))
            
            predictions.append({
                "game_id": game['id'],
                "away_team": away_abbr,
                "home_team": home_abbr,
                "predicted_winner": home_abbr if home_prob > 0.5 else away_abbr,
                "predicted_home_win_prob": round(home_prob, 2),
                "predicted_away_win_prob": round(1 - home_prob, 2)
            })
            
        return jsonify(predictions)
    except Exception as e:
        print(f"Error generating predictions: {e}")
        return jsonify([])

@app.route('/api/predictions/game/<game_id>', methods=['GET'])
def get_game_prediction(game_id):
    """Get prediction for specific game"""
    data = load_json('win_probability_predictions_v2.json')
    
    # Find prediction for this game
    if isinstance(data, dict) and 'predictions' in data:
        predictions = data['predictions']
    elif isinstance(data, list):
        predictions = data
    else:
        return jsonify({}), 404
    
    for prediction in predictions:
        if str(prediction.get('game_id')) == str(game_id):
            return jsonify(prediction)
    
    return jsonify({}), 404

@app.route('/api/historical-stats', methods=['GET'])
def get_historical_stats():
    """Get historical season stats"""
    data = load_json('historical_seasons_team_stats.json')
    return jsonify(data)

@app.route('/api/team-roster/<team_abbrev>', methods=['GET'])
def get_team_roster(team_abbrev):
    """Proxy endpoint for NHL team roster to avoid CORS issues"""
    try:
        import requests
        # Use the NHL API to get the roster
        url = f"https://api-web.nhle.com/v1/roster/{team_abbrev}/20252026"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': 'Failed to fetch roster'}), response.status_code
    except Exception as e:
        print(f"Error fetching roster for {team_abbrev}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/historical-stats/<season>', methods=['GET'])
def get_historical_stats_by_season(season):
    """Get stats for specific season (e.g., '2024-2025')"""
    # Try to load the specific season file
    filename = f'season_{season.replace("-", "_")}_team_stats.json'
    data = load_json(filename)
    
    if not data:
        # Fallback to historical stats
        historical = load_json('historical_seasons_team_stats.json')
        data = historical.get(season, {})
    
    return jsonify(data)

@app.route('/api/notify/discord', methods=['POST'])
def send_discord_notification():
    """Trigger Discord notification with today's predictions"""
    try:
        import subprocess
        
        # Run the discord_notifier.py script
        result = subprocess.run(
            ['python3', os.path.join(DATA_DIR, 'discord_notifier.py')],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return jsonify({
                "success": True,
                "message": "Discord notification sent successfully",
                "output": result.stdout
            })
        else:
            return jsonify({
                "success": False,
                "message": "Failed to send Discord notification",
                "error": result.stderr
            }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Error triggering Discord notification",
            "error": str(e)
        }), 500

@app.route('/api/live-game/<game_id>', methods=['GET'])
def get_live_game_data(game_id):
    """Get live game data and predictions"""
    try:
        # Get live metrics
        live_metrics = live_predictor.get_live_game_data(game_id)
        
        if not live_metrics:
            return jsonify({"error": "Game not found or not live"}), 404
            
        # Generate prediction
        prediction = live_predictor.predict_live_game(live_metrics)
        
        if not prediction:
            return jsonify({"error": "Could not generate prediction"}), 500
            
        return jsonify(prediction)
    except Exception as e:
        print(f"Error in live-game endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/lines/<team_abbrev>', methods=['GET'])
def get_team_lines(team_abbrev):
    """Get lines and pairings from MoneyPuck"""
    try:
        url = "https://moneypuck.com/moneypuck/playerData/seasonSummary/2025/regular/lines.csv"
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return jsonify({'error': 'Failed to fetch lines'}), 500
        
        lines_data = []
        # Decode content to string
        content = response.content.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(content))
        
        for row in csv_reader:
            if row['team'] == team_abbrev.upper() and row['situation'] == '5on5':
                # Parse players
                players = row['name'].split('-')
                
                line_item = {
                    'players': [{'name': p} for p in players],
                    'position': row['position'], # 'line' or 'pairing'
                    'icetime': float(row['icetime']),
                    'games_played': int(row['games_played']),
                    'xg_pct': float(row['xGoalsPercentage']) if row['xGoalsPercentage'] else 0.0,
                    'goals_for': float(row['goalsFor']) if row['goalsFor'] else 0.0,
                    'goals_against': float(row['goalsAgainst']) if row['goalsAgainst'] else 0.0
                }
                lines_data.append(line_item)
        
        # Sort by icetime descending
        lines_data.sort(key=lambda x: x['icetime'], reverse=True)
        
        # Separate into forwards and defense
        forwards = [l for l in lines_data if l['position'] == 'line'][:4]
        defense = [l for l in lines_data if l['position'] == 'pairing'][:3]
        
        return jsonify({
            'forwards': forwards,
            'defense': defense
        })
        
    except Exception as e:
        print(f"Error fetching lines for {team_abbrev}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/player-stats', methods=['GET'])
def get_player_stats():
    """Get player stats from MoneyPuck"""
    try:
        season = request.args.get('season', '2025')
        game_type = request.args.get('type', 'regular')
        situation = request.args.get('situation', 'all')  # all, 5on5, etc
        
        url = f"https://moneypuck.com/moneypuck/playerData/seasonSummary/{season}/{game_type}/skaters.csv"
        response = requests.get(url, timeout=15)
        
        if response.status_code != 200:
            return jsonify({'error': 'Failed to fetch player stats'}), 500
        
        players_data = []
        content = response.content.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(content))
        
        for row in csv_reader:
            # Filter by situation if specified
            if row['situation'] == situation:
                player = {
                    'name': row['name'],
                    'team': row['team'],
                    'position': row['position'],
                    'games_played': int(row['games_played']) if row['games_played'] else 0,
                    'icetime': float(row['icetime']) if row['icetime'] else 0,
                    'goals': int(float(row['I_F_goals'])) if row['I_F_goals'] else 0,
                    'assists': int(float(row['I_F_primaryAssists'])) + int(float(row['I_F_secondaryAssists'])) if row['I_F_primaryAssists'] and row['I_F_secondaryAssists'] else 0,
                    'points': int(float(row['I_F_points'])) if row['I_F_points'] else 0,
                    'shots': int(float(row['I_F_shotsOnGoal'])) if row['I_F_shotsOnGoal'] else 0,
                    'game_score': round(float(row['gameScore']), 2) if row['gameScore'] else 0,
                    'xgoals': round(float(row['I_F_xGoals']), 2) if row['I_F_xGoals'] else 0,
                    'corsi_pct': round(float(row['onIce_corsiPercentage']) * 100, 1) if row['onIce_corsiPercentage'] else 0,
                    'xgoals_pct': round(float(row['onIce_xGoalsPercentage']) * 100, 1) if row['onIce_xGoalsPercentage'] else 0,
                    # New fields
                    'I_F_shotAttempts': int(float(row['I_F_shotAttempts'])) if row.get('I_F_shotAttempts') else 0,
                    'I_F_highDangerShots': int(float(row['I_F_highDangerShots'])) if row.get('I_F_highDangerShots') else 0,
                    'I_F_highDangerxGoals': round(float(row['I_F_highDangerxGoals']), 2) if row.get('I_F_highDangerxGoals') else 0,
                    'I_F_highDangerGoals': int(float(row['I_F_highDangerGoals'])) if row.get('I_F_highDangerGoals') else 0,
                    'onIce_corsiPercentage': round(float(row['onIce_corsiPercentage']) * 100, 1) if row.get('onIce_corsiPercentage') else 0,
                    'onIce_xGoalsPercentage': round(float(row['onIce_xGoalsPercentage']) * 100, 1) if row.get('onIce_xGoalsPercentage') else 0,
                }
                players_data.append(player)
        
        return jsonify(players_data)
        
    except Exception as e:
        print(f"Error fetching player stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/team-performers/<team_abbr>', methods=['GET'])
def get_team_performers(team_abbr):
    """Get top 5 performers for a specific team"""
    try:
        # Use 2024 season (2024-25) as that's where the data is
        season = '2024'
        game_type = 'regular'
        situation = 'all'
        
        url = f"https://moneypuck.com/moneypuck/playerData/seasonSummary/{season}/{game_type}/skaters.csv"
        response = requests.get(url, timeout=15)
        
        if response.status_code != 200:
            print(f"MoneyPuck returned status {response.status_code}")
            return jsonify([]), 200  # Return empty array instead of error
        
        team_abbr_upper = team_abbr.upper()
        players_data = []
        content = response.content.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(content))
        
        for row in csv_reader:
            # Filter by team and situation
            if row['team'] == team_abbr_upper and row['situation'] == situation:
                try:
                    player = {
                        'name': row['name'],
                        'team': row['team'],
                        'position': row['position'],
                        'games_played': int(row['games_played']) if row.get('games_played') else 0,
                        'icetime': float(row['icetime']) if row.get('icetime') else 0,
                        'goals': int(float(row['I_F_goals'])) if row.get('I_F_goals') else 0,
                        'assists': int(float(row['I_F_primaryAssists']) or 0) + int(float(row['I_F_secondaryAssists']) or 0) if row.get('I_F_primaryAssists') and row.get('I_F_secondaryAssists') else 0,
                        'points': int(float(row['I_F_points'])) if row.get('I_F_points') else 0,
                        'gsPerGame': round(float(row['gameScore']) / int(row['games_played']), 3) if row.get('gameScore') and row.get('games_played') and int(row['games_played']) > 0 else 0,
                    }
                    players_data.append(player)
                except (ValueError, TypeError) as e:
                    # Skip players with bad data
                    continue
        
        # Sort by points descending, then by game score per game
        players_data.sort(key=lambda x: (x['points'], x['gsPerGame']), reverse=True)
        
        # Return top 5
        top_performers = players_data[:5]
        
        print(f"Returning {len(top_performers)} performers for {team_abbr_upper}")
        return jsonify(top_performers)
        
    except Exception as e:
        print(f"Error fetching team performers for {team_abbr}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify([]), 200  # Return empty array instead of error


# NHL API Proxy endpoints to avoid CORS issues
@app.route('/api/nhl/schedule/<date>', methods=['GET'])
def proxy_nhl_schedule(date):
    """Proxy NHL schedule API to avoid CORS"""
    try:
        url = f"https://api-web.nhle.com/v1/schedule/{date}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return jsonify(response.json())
        return jsonify({'error': 'Failed to fetch schedule'}), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/nhl/standings/<date>', methods=['GET'])
def proxy_nhl_standings(date):
    """Proxy NHL standings API to avoid CORS"""
    try:
        url = f"https://api-web.nhle.com/v1/standings/{date}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return jsonify(response.json())
        return jsonify({'error': 'Failed to fetch standings'}), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/nhl/gamecenter/<game_id>/<endpoint>', methods=['GET'])
def proxy_nhl_gamecenter(game_id, endpoint):
    """Proxy NHL game center API to avoid CORS"""
    try:
        url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/{endpoint}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return jsonify(response.json())
        return jsonify({'error': 'Failed to fetch game data'}), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🏒 NHL Analytics API Server")
    print("=" * 50)
    print(f"Data directory: {DATA_DIR}")
    print(f"Available endpoints:")
    print(f"  GET /api/health")
    print(f"  GET /api/team-stats")
    print(f"  GET /api/team-stats/<team_abbrev>")
    print(f"  GET /api/team-metrics")
    print(f"  GET /api/edge-data")
    print(f"  GET /api/edge-data/<team_abbrev>")
    print(f"  GET /api/predictions")
    print(f"  GET /api/predictions/today")
    print(f"  GET /api/predictions/game/<game_id>")
    print(f"  GET /api/historical-stats")
    print(f"  GET /api/historical-stats/<season>")
    print(f"  POST /api/notify/discord")
    print("=" * 50)
    port = int(os.environ.get('PORT', 5002))
    print(f"Starting server on http://localhost:{port}")
    print()
    
    app.run(debug=False, host='0.0.0.0', port=port)
