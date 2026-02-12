from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
import sys
from datetime import datetime, timedelta
import requests
import csv
import io
import ipaddress

app = Flask(__name__)

# Render IP ranges for allowlisting (if needed)
RENDER_IP_RANGES = [
    '74.220.49.0/24',
    '74.220.57.0/24'
]

# Convert CIDR ranges to networks for IP checking
RENDER_NETWORKS = [ipaddress.ip_network(cidr) for cidr in RENDER_IP_RANGES]

def is_render_ip(ip_address):
    """Check if an IP address belongs to Render's IP ranges"""
    try:
        ip = ipaddress.ip_address(ip_address)
        return any(ip in network for network in RENDER_NETWORKS)
    except ValueError:
        return False

# Enable CORS for React frontend (allows all origins by default)
# If you need to restrict to specific domains, configure CORS with specific origins
CORS(app, resources={
    r"/api/*": {
        "origins": "*",  # Allow all origins, or specify: ["https://nhl-analytics.vercel.app", "https://nhl-analytics-frontend.onrender.com"]
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Try to enable response compression (optional, speeds up responses)
try:
    from flask_compress import Compress
    Compress(app)
    print("✅ Response compression enabled")
except ImportError:
    print("⚠️ flask-compress not installed (optional, install with: pip install flask-compress)")

# Base directory for data files
DATA_DIR = os.path.dirname(os.path.abspath(__file__))

# Add project root and reports dir to sys.path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

reports_dir = os.path.join(project_root, 'automated-post-game-reports')
if os.path.exists(reports_dir) and reports_dir not in sys.path:
    sys.path.insert(0, reports_dir)

# Initialize predictor
try:
    from live_in_game_predictions import LiveInGamePredictor
    live_predictor = LiveInGamePredictor()
except ImportError as e:
    print(f"Warning: LiveInGamePredictor not found ({e}), using mock")
    class MockPredictor:
        def get_live_game_data(self, game_id): return {}
        def predict_live_game(self, metrics): return {}
    live_predictor = MockPredictor()

# Cache for team metrics to avoid recalculating on every request
_team_metrics_cache = None
_team_metrics_cache_time = None

# Force cache invalidation for testing - set to True to bypass cache
FORCE_REFRESH_TEAM_METRICS = False
_team_metrics_file_mtime = None
CACHE_DURATION = timedelta(hours=1)  # Cache for 1 hour

def load_json(filename):
    """Load JSON file from current directory"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: {filename} not found, returning empty dict")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error decoding {filename}: {e}")
        return {}

def get_file_mtime(filename):
    """Get file modification time"""
    try:
        return os.path.getmtime(filename)
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
    """Get aggregated team metrics for all teams (for pre-game comparisons)
    Primary source: season_2025_2026_team_stats.json (created daily with calculated metrics)
    Supplemented with: MoneyPuck data for additional fields
    Uses caching to avoid recalculating on every request.
    Cache is invalidated after 1 hour.
    """
    global _team_metrics_cache, _team_metrics_cache_time, FORCE_REFRESH_TEAM_METRICS
    
    # Allow force refresh via query param
    if request.args.get('force') == '1':
        FORCE_REFRESH_TEAM_METRICS = True
    
    current_time = datetime.now()
    
    # Check if cache is valid
    cache_valid = (
        not FORCE_REFRESH_TEAM_METRICS and
        _team_metrics_cache is not None and
        _team_metrics_cache_time is not None and
        (current_time - _team_metrics_cache_time) < CACHE_DURATION
    )
    
    if cache_valid:
        print(f"Returning cached team metrics (age: {(current_time - _team_metrics_cache_time).seconds}s)")
        return jsonify(_team_metrics_cache)
    
    print("Loading team metrics from season_2025_2026_team_stats.json (primary source)...")
    
    # Helper function to calculate average from list
    def avg_from_list(lst):
        """Calculate average from list, handling empty lists"""
        if not lst or not isinstance(lst, list) or len(lst) == 0:
            return None
        return sum(lst) / len(lst)
    
    # PRIMARY SOURCE: Load from season_2025_2026_team_stats.json (created daily)
    metrics = {}
    try:
        season_stats = load_json('season_2025_2026_team_stats.json')
        teams_stats = season_stats.get('teams', season_stats) if isinstance(season_stats, dict) else {}
        print(f"Loaded {len(teams_stats)} teams from season stats")
        
        # Debug: Check if CBJ has data
        if 'CBJ' in teams_stats:
            cbj_data = teams_stats['CBJ']
            print(f"DEBUG: CBJ has home: {'home' in cbj_data}, away: {'away' in cbj_data}")
            if 'home' in cbj_data:
                home_ozs = cbj_data['home'].get('ozs', [])
                print(f"DEBUG: CBJ home ozs is list: {isinstance(home_ozs, list)}, length: {len(home_ozs) if isinstance(home_ozs, list) else 'N/A'}")
        
        # Process each team from season stats (primary source)
        for team_abbr, team_data in teams_stats.items():
            home_data = team_data.get('home', {})
            away_data = team_data.get('away', {})
            
            # Initialize team metrics
            team_metrics = {}
            
            # Calculate averages from home and away arrays for all metrics
            if home_data or away_data:
                # Zone metrics (from calculated play-by-play data)
                # JSON now stores per-game values directly (already per-game averages)
                # Each value in the list is already a per-game value (e.g., 11, 12, 4, 8, 18)
                # So we just need to average them across all games
                home_ozs_list = home_data.get('ozs', [])
                home_nzs_list = home_data.get('nzs', [])
                home_dzs_list = home_data.get('dzs', [])
                away_ozs_list = away_data.get('ozs', [])
                away_nzs_list = away_data.get('nzs', [])
                away_dzs_list = away_data.get('dzs', [])
                
                # Calculate per-game averages: sum all games / number of games
                # Each value in the list is already a per-game value
                home_games = len(home_ozs_list) if home_ozs_list else 0
                away_games = len(away_ozs_list) if away_ozs_list else 0
                total_games = home_games + away_games
                
                # Sum all home and away values, then divide by total games to get average per-game value
                total_ozs = sum(home_ozs_list) + sum(away_ozs_list) if (home_ozs_list and away_ozs_list) else (sum(home_ozs_list) if home_ozs_list else 0) + (sum(away_ozs_list) if away_ozs_list else 0)
                total_nzs = sum(home_nzs_list) + sum(away_nzs_list) if (home_nzs_list and away_nzs_list) else (sum(home_nzs_list) if home_nzs_list else 0) + (sum(away_nzs_list) if away_nzs_list else 0)
                total_dzs = sum(home_dzs_list) + sum(away_dzs_list) if (home_dzs_list and away_dzs_list) else (sum(home_dzs_list) if home_dzs_list else 0) + (sum(away_dzs_list) if away_dzs_list else 0)
                
                # Average per-game value (values are already per-game, just average them)
                team_metrics['ozs'] = total_ozs / total_games if total_games > 0 else 0
                team_metrics['nzs'] = total_nzs / total_games if total_games > 0 else 0
                team_metrics['dzs'] = total_dzs / total_games if total_games > 0 else 0
                
                # Shot generation metrics
                home_fc = avg_from_list(home_data.get('fc', []))
                away_fc = avg_from_list(away_data.get('fc', []))
                team_metrics['fc'] = (home_fc + away_fc) / 2 if (home_fc is not None and away_fc is not None) else (home_fc or away_fc or 0)
                
                home_rush = avg_from_list(home_data.get('rush', []))
                away_rush = avg_from_list(away_data.get('rush', []))
                team_metrics['rush'] = (home_rush + away_rush) / 2 if (home_rush is not None and away_rush is not None) else (home_rush or away_rush or 0)
                
                # Turnover metrics
                home_nzt = avg_from_list(home_data.get('nzt', []))
                away_nzt = avg_from_list(away_data.get('nzt', []))
                team_metrics['nzts'] = (home_nzt + away_nzt) / 2 if (home_nzt is not None and away_nzt is not None) else (home_nzt or away_nzt or 0)
                
                home_nztsa = avg_from_list(home_data.get('nztsa', []))
                away_nztsa = avg_from_list(away_data.get('nztsa', []))
                team_metrics['nztsa'] = (home_nztsa + away_nztsa) / 2 if (home_nztsa is not None and away_nztsa is not None) else (home_nztsa or away_nztsa or 0)
                
                # Movement metrics
                home_lat = avg_from_list(home_data.get('lat', []))
                away_lat = avg_from_list(away_data.get('lat', []))
                team_metrics['lat'] = (home_lat + away_lat) / 2 if (home_lat is not None and away_lat is not None) else (home_lat or away_lat or 0)
                
                home_long = avg_from_list(home_data.get('long_movement', []))
                away_long = avg_from_list(away_data.get('long_movement', []))
                team_metrics['long_movement'] = (home_long + away_long) / 2 if (home_long is not None and away_long is not None) else (home_long or away_long or 0)
                
                # Game Score - JSON now stores per-game team totals directly (e.g., 6.65, 8.65, 4.23)
                # These are already per-game values, so we just average them
                home_gs_list = home_data.get('gs', [])
                away_gs_list = away_data.get('gs', [])
                home_games_gs = len(home_gs_list) if home_gs_list else 0
                away_games_gs = len(away_gs_list) if away_gs_list else 0
                
                # Average per game (sum of all games / number of games)
                # Values are already per-game team totals
                home_gs_per_game = sum(home_gs_list) / home_games_gs if home_games_gs > 0 else 0
                away_gs_per_game = sum(away_gs_list) / away_games_gs if away_games_gs > 0 else 0
                
                # Average home and away to get overall team average per game
                team_metrics['gs'] = (home_gs_per_game + away_gs_per_game) / 2 if (home_games_gs > 0 and away_games_gs > 0) else (home_gs_per_game or away_gs_per_game or 0)
                
                # Basic stats (per game averages)
                home_goals = avg_from_list(home_data.get('goals', []))
                away_goals = avg_from_list(away_data.get('goals', []))
                team_metrics['goals_per_game'] = (home_goals + away_goals) / 2 if (home_goals is not None and away_goals is not None) else (home_goals or away_goals or 0)
                
                home_goals_against = avg_from_list(home_data.get('goals_against', []))
                away_goals_against = avg_from_list(away_data.get('goals_against', []))
                team_metrics['goals_against_per_game'] = (home_goals_against + away_goals_against) / 2 if (home_goals_against is not None and away_goals_against is not None) else (home_goals_against or away_goals_against or 0)
                
                home_shots = avg_from_list(home_data.get('shots', []))
                away_shots = avg_from_list(away_data.get('shots', []))
                team_metrics['shots'] = (home_shots + away_shots) / 2 if (home_shots is not None and away_shots is not None) else (home_shots or away_shots or 0)
                
                home_hits = avg_from_list(home_data.get('hits', []))
                away_hits = avg_from_list(away_data.get('hits', []))
                team_metrics['hits_per_game'] = (home_hits + away_hits) / 2 if (home_hits is not None and away_hits is not None) else (home_hits or away_hits or 0)
                
                home_blocks = avg_from_list(home_data.get('blocked_shots', []))
                away_blocks = avg_from_list(away_data.get('blocked_shots', []))
                team_metrics['blocks_per_game'] = (home_blocks + away_blocks) / 2 if (home_blocks is not None and away_blocks is not None) else (home_blocks or away_blocks or 0)
                
                home_giveaways = avg_from_list(home_data.get('giveaways', []))
                away_giveaways = avg_from_list(away_data.get('giveaways', []))
                team_metrics['giveaways_per_game'] = (home_giveaways + away_giveaways) / 2 if (home_giveaways is not None and away_giveaways is not None) else (home_giveaways or away_giveaways or 0)
                
                home_takeaways = avg_from_list(home_data.get('takeaways', []))
                away_takeaways = avg_from_list(away_data.get('takeaways', []))
                team_metrics['takeaways_per_game'] = (home_takeaways + away_takeaways) / 2 if (home_takeaways is not None and away_takeaways is not None) else (home_takeaways or away_takeaways or 0)
                
                home_pim = avg_from_list(home_data.get('penalty_minutes', []))
                away_pim = avg_from_list(away_data.get('penalty_minutes', []))
                team_metrics['pim_per_game'] = (home_pim + away_pim) / 2 if (home_pim is not None and away_pim is not None) else (home_pim or away_pim or 0)
                
                # Percentages
                home_corsi = avg_from_list(home_data.get('corsi_pct', []))
                away_corsi = avg_from_list(away_data.get('corsi_pct', []))
                team_metrics['corsi_pct'] = (home_corsi + away_corsi) / 2 if (home_corsi is not None and away_corsi is not None) else (home_corsi or away_corsi or 50.0)
                
                home_pp = avg_from_list(home_data.get('power_play_pct', []))
                away_pp = avg_from_list(away_data.get('power_play_pct', []))
                team_metrics['pp_pct'] = (home_pp + away_pp) / 2 if (home_pp is not None and away_pp is not None) else (home_pp or away_pp or 0.0)
                
                home_pk = avg_from_list(home_data.get('penalty_kill_pct', []))
                away_pk = avg_from_list(away_data.get('penalty_kill_pct', []))
                team_metrics['pk_pct'] = (home_pk + away_pk) / 2 if (home_pk is not None and away_pk is not None) else (home_pk or away_pk or 0.0)
                
                home_fo = avg_from_list(home_data.get('faceoff_pct', []))
                away_fo = avg_from_list(away_data.get('faceoff_pct', []))
                team_metrics['faceoff_pct'] = (home_fo + away_fo) / 2 if (home_fo is not None and away_fo is not None) else (home_fo or away_fo or 50.0)
                
                # xG and HDC (if available in season stats, otherwise will supplement from MoneyPuck)
                home_xg = avg_from_list(home_data.get('xg', []))
                away_xg = avg_from_list(away_data.get('xg', []))
                if home_xg is not None or away_xg is not None:
                    team_metrics['xg'] = (home_xg + away_xg) / 2 if (home_xg is not None and away_xg is not None) else (home_xg or away_xg or 0)
                
                home_hdc = avg_from_list(home_data.get('hdc', []))
                away_hdc = avg_from_list(away_data.get('hdc', []))
                if home_hdc is not None or away_hdc is not None:
                    team_metrics['hdc'] = (home_hdc + away_hdc) / 2 if (home_hdc is not None and away_hdc is not None) else (home_hdc or away_hdc or 0)
                
                home_hdca = avg_from_list(home_data.get('hdca', []))
                away_hdca = avg_from_list(away_data.get('hdca', []))
                if home_hdca is not None or away_hdca is not None:
                    team_metrics['hdca'] = (home_hdca + away_hdca) / 2 if (home_hdca is not None and away_hdca is not None) else (home_hdca or away_hdca or 0)
            
            metrics[team_abbr] = team_metrics
        
        # Debug: Check CBJ metrics after calculation
        if 'CBJ' in metrics:
            cbj_metrics = metrics['CBJ']
            print(f"DEBUG: CBJ metrics after calculation - ozs: {cbj_metrics.get('ozs')}, nzs: {cbj_metrics.get('nzs')}, gs: {cbj_metrics.get('gs')}, fc: {cbj_metrics.get('fc')}")
        
        print(f"✅ Calculated averages from season stats for {len(metrics)} teams")
        
        # SUPPLEMENT with MoneyPuck data for any missing fields (optional, can skip for faster loading)
        # Only fetch MoneyPuck if explicitly requested or if critical fields are missing
        skip_moneypuck = request.args.get('skip_moneypuck', '0') == '1'
        
        if not skip_moneypuck:
            print("Supplementing with MoneyPuck data for additional fields...")
        
        season = request.args.get('season', '2025')
        game_type = request.args.get('type', 'regular')
        situation = request.args.get('situation', 'all')
        
        url = f"https://moneypuck.com/moneypuck/playerData/seasonSummary/{season}/{game_type}/teams.csv"
        
        try:
            response = requests.get(url, timeout=15)
            
            if response.status_code != 200:
                raise Exception(f"MoneyPuck API returned status {response.status_code}")
            
            # Parse MoneyPuck CSV data
            content = response.content.decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(content))
            
            # Helper functions
            def safe_float(val, default=0.0):
                try:
                    return float(val) if val else default
                except:
                    return default
            
            def safe_int(val, default=0):
                try:
                    return int(float(val)) if val else default
                except:
                    return default
            
            # Supplement existing metrics with MoneyPuck data (only fill in missing fields)
            moneypuck_count = 0
            for row in csv_reader:
                if row.get('situation', '').strip() == situation:
                    team_abbr = row.get('team', '').strip()
                    if not team_abbr or team_abbr not in metrics:
                        continue
                    
                    # Only supplement fields that are missing or need updating from MoneyPuck
                    team_metrics = metrics[team_abbr]
                    
                    # Supplement xG if missing
                    if 'xg' not in team_metrics or team_metrics.get('xg') == 0:
                        team_metrics['xg'] = safe_float(row.get('xGoalsFor'))
                    
                    # Supplement HDC if missing
                    if 'hdc' not in team_metrics or team_metrics.get('hdc') == 0:
                        team_metrics['hdc'] = safe_int(row.get('highDangerShotsFor'))
                    
                    # Supplement HDCA if missing
                    if 'hdca' not in team_metrics or team_metrics.get('hdca') == 0:
                        team_metrics['hdca'] = safe_int(row.get('highDangerShotsAgainst'))
                    
                    # Supplement shots if missing
                    if 'shots' not in team_metrics or team_metrics.get('shots') == 0:
                        team_metrics['shots'] = safe_int(row.get('shotsOnGoalFor'))
                    
                    # Supplement corsi_pct if missing
                    if 'corsi_pct' not in team_metrics or team_metrics.get('corsi_pct') == 0:
                        team_metrics['corsi_pct'] = safe_float(row.get('corsiPercentage')) * 100
                    
                    # Supplement PP/PK/Faceoff if missing
                    if 'pp_pct' not in team_metrics or team_metrics.get('pp_pct') == 0:
                        pp_goals = safe_int(row.get('powerPlayGoalsFor'), 0)
                        pp_attempts = safe_int(row.get('powerPlayAttemptsFor'), 0)
                        if pp_attempts > 0:
                            team_metrics['pp_pct'] = (pp_goals / pp_attempts) * 100
                    
                    if 'pk_pct' not in team_metrics or team_metrics.get('pk_pct') == 0:
                        pk_goals_against = safe_int(row.get('powerPlayGoalsAgainst'), 0)
                        pk_attempts = safe_int(row.get('powerPlayAttemptsAgainst'), 0)
                        if pk_attempts > 0:
                            team_metrics['pk_pct'] = ((pk_attempts - pk_goals_against) / pk_attempts) * 100
                    
                    if 'faceoff_pct' not in team_metrics or team_metrics.get('faceoff_pct') == 0:
                        faceoffs_won = safe_int(row.get('faceOffsWonFor'), 0)
                        faceoffs_total = faceoffs_won + safe_int(row.get('faceOffsWonAgainst'), 0)
                        if faceoffs_total > 0:
                            team_metrics['faceoff_pct'] = (faceoffs_won / faceoffs_total) * 100
                    
                    moneypuck_count += 1
            
            print(f"✅ Supplemented {moneypuck_count} teams with MoneyPuck data")
            
            # Debug: Check CBJ metrics after MoneyPuck supplement
            if 'CBJ' in metrics:
                cbj_metrics = metrics['CBJ']
                print(f"DEBUG: CBJ metrics after MoneyPuck - ozs: {cbj_metrics.get('ozs')}, nzs: {cbj_metrics.get('nzs')}, gs: {cbj_metrics.get('gs')}, fc: {cbj_metrics.get('fc')}")
        
        except Exception as moneypuck_error:
            print(f"⚠️ Warning: Could not fetch MoneyPuck data (non-critical): {moneypuck_error}")
            # Continue without MoneyPuck data - season stats are primary source
        
        if skip_moneypuck:
            print("⏩ Skipping MoneyPuck supplement for faster response (use ?skip_moneypuck=0 to enable)")
        
        # Debug: Final check before caching
        if 'CBJ' in metrics:
            cbj_metrics = metrics['CBJ']
            print(f"DEBUG: Final CBJ metrics before cache - ozs: {cbj_metrics.get('ozs')}, nzs: {cbj_metrics.get('nzs')}, gs: {cbj_metrics.get('gs')}, fc: {cbj_metrics.get('fc')}, rush: {cbj_metrics.get('rush')}, lat: {cbj_metrics.get('lat')}")
    
        # Cache the results
        _team_metrics_cache = metrics
        _team_metrics_cache_time = current_time
        return jsonify(metrics)
    except Exception as e:
        print(f"Error loading team metrics: {e}")
        import traceback
        traceback.print_exc()
        # Return empty dict if primary source fails
        return jsonify({})

@app.route('/api/team-heatmap/<team_abbr>', methods=['GET'])
def get_team_heatmap(team_abbr):
    """Get aggregated shot data for team heatmap"""
    try:
        from nhl_api_client import NHLAPIClient
        client = NHLAPIClient()
        
        # ----- XG model import with fallback -----
        use_xg_model = False
        xg_model = None
        try:
            import sys
            import os
            # Add the project root to path if not already there
            project_root = os.path.abspath(os.path.dirname(__file__))
            if project_root not in sys.path:
                sys.path.insert(0, project_root)
            
            # Also try adding the automated-post-game-reports subdir
            reports_dir = os.path.join(project_root, 'automated-post-game-reports')
            if os.path.exists(reports_dir) and reports_dir not in sys.path:
                sys.path.insert(0, reports_dir)

            from improved_xg_model import ImprovedXGModel
            xg_model = ImprovedXGModel()
            use_xg_model = True
        except Exception as e:
            print(f"Could not load ImprovedXGModel: {e} – using distance-based fallback")

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
        
        # Get recent games (limit 10)
        game_ids = client.get_team_recent_games(team_abbr, limit=10)
        
        shots_for = []
        goals_for = []
        shots_against = []
        goals_against = []
        
        for game_id in game_ids:
            # Get play-by-play and game center for each game
            pbp = client.get_play_by_play(game_id)
            game_center = client.get_game_center(game_id)
            
            # Robust check for game_center data
            home_team_id = None
            away_team_id = None
            if game_center:
                home_team_id = game_center.get('homeTeam', {}).get('id')
                away_team_id = game_center.get('awayTeam', {}).get('id')
            
            # Determine if target team is home or away
            is_home_team = False
            if home_team_id and target_team_id:
                is_home_team = (int(home_team_id) == int(target_team_id))
            
            if not pbp or 'plays' not in pbp:
                continue
                
            for play_index, play in enumerate(pbp.get('plays', [])):
                details = play.get('details', {})
                if not details:
                    continue
                    
                x = details.get('xCoord')
                y = details.get('yCoord')
                event_owner_id = details.get('eventOwnerTeamId')
                period = play.get('periodDescriptor', {}).get('number', 1)
                
                if x is None or y is None or event_owner_id is None:
                    continue
                
                is_for = (int(event_owner_id) == int(target_team_id)) if target_team_id else True
                
                # Normalize coordinates so target team always shoots right (positive x)
                normalized_x = x
                normalized_y = y
                
                if is_home_team:
                    # Home team: in odd periods shoots right, even periods shoots left
                    if period % 2 == 0:  # Even period - flip
                        normalized_x = -x
                        normalized_y = -y
                else:
                    # Away team: in odd periods shoots left, even periods shoots right  
                    if period % 2 == 1:  # Odd period - flip
                        normalized_x = -x
                        normalized_y = -y
                    
                # Helper for xG calculation
                def _calc_xg(event_type):
                    if use_xg_model and xg_model:
                        try:
                            previous = pbp.get('plays', [])[max(0, play_index-10):play_index]
                            shot_data = {
                                'x_coord': x,
                                'y_coord': y,
                                'shot_type': details.get('shotType', 'wrist').lower(),
                                'event_type': event_type,
                                'time_in_period': play.get('timeInPeriod', '00:00'),
                                'period': period,
                                'strength_state': 'even',
                                'score_differential': 0,
                                'team_id': event_owner_id,
                            }
                            return xg_model.calculate_xg(shot_data, previous)
                        except Exception as e:
                            print(f"xG model error: {e}")
                    
                    # Fallback distance-based xG
                    # IMPORTANT: Use RAW coordinates (x, y), not normalized
                    # NHL coordinates: Goals at x=89 and x=-89
                    import math
                    goal_x = 89 if x >= 0 else -89
                    distance_from_goal = math.sqrt((goal_x - x)**2 + y**2)
                    if event_type == 'goal':
                        return max(0.1, min(0.8, 1.0 - (distance_from_goal / 100)))
                    return max(0.01, min(0.5, 1.0 - (distance_from_goal / 100)))

                # Common point data
                shooter_name = None
                shooter_id = details.get('shootingPlayerId') or details.get('scoringPlayerId')
                
                if shooter_id and 'rosterSpots' in pbp:
                    for spot in pbp['rosterSpots']:
                        if spot.get('playerId') == shooter_id:
                            shooter_name = spot.get('firstName', {}).get('default', '') + ' ' + spot.get('lastName', {}).get('default', '')
                            break
                
                # Determine movement type based on previous events
                movement = None
                if play_index > 0:
                    prev_play = pbp['plays'][play_index - 1]
                    prev_type = prev_play.get('typeDescKey', '')
                    if 'faceoff' in prev_type:
                        movement = 'rush'
                    elif 'hit' in prev_type or 'takeaway' in prev_type:
                        movement = 'forecheck'
                    elif prev_play.get('details', {}).get('zoneCode') != play.get('details', {}).get('zoneCode'):
                        movement = 'transition'

                point = {
                    'x': normalized_x,
                    'y': normalized_y,
                    'shooter': shooter_name,
                    'shotType': details.get('shotType'),
                    'movement': movement
                }

                if play.get('typeDescKey') == 'shot-on-goal':
                    point['xg'] = _calc_xg('shot-on-goal')
                    if is_for:
                        shots_for.append(point)
                    else:
                        shots_against.append(point)
                elif play.get('typeDescKey') == 'goal':
                    point['xg'] = _calc_xg('goal')
                    if is_for:
                        goals_for.append(point)
                    else:
                        goals_against.append(point)
        
        heatmap = {
            'shots_for': shots_for,
            'goals_for': goals_for,
            'shots_against': shots_against,
            'goals_against': goals_against
        }
        
        return jsonify(heatmap)

    except Exception as e:
        print(f"Error generating heatmap for {team_abbr}: {e}")
        import traceback
        traceback.print_exc()
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
    """Get today's game predictions using the self-learning model"""
    try:
        # First, try to read from the predictions file
        predictions_file = os.path.join('automated-post-game-reports', 'win_probability_predictions_v2.json')
        today = datetime.now().strftime('%Y-%m-%d')
        
        try:
            with open(predictions_file, 'r') as f:
                data = json.load(f)
                all_predictions = data.get('predictions', [])
                
                print(f"📊 Total predictions in file: {len(all_predictions)}")
                
                # Filter for today's predictions
                todays_predictions = []
                for pred in all_predictions:
                    # Show all of today's games (even if they already have a winner)
                    if pred.get('date') == today:
                        # Values are already in decimal format (0.47) in the file
                        away_prob = pred.get('predicted_away_win_prob', 0.5)
                        home_prob = pred.get('predicted_home_win_prob', 0.5)
                        
                        todays_predictions.append({
                            'game_id': pred.get('game_id'),
                            'away_team': pred.get('away_team'),
                            'home_team': pred.get('home_team'),
                            'away_win_prob': away_prob,
                            'home_win_prob': home_prob,
                            'favorite': pred.get('home_team') if home_prob > away_prob else pred.get('away_team'),
                            'spread': abs(home_prob - away_prob),
                            'confidence': max(away_prob, home_prob),
                            'actual_winner': pred.get('actual_winner')  # Include for reference
                        })
                
                if todays_predictions:
                    print(f"✅ Found {len(todays_predictions)} predictions for today ({today}) from file")
                    for p in todays_predictions:
                        status = f"(FINAL: {p['actual_winner']})" if p.get('actual_winner') else "(UPCOMING)"
                        print(f"   {p['away_team']} @ {p['home_team']}: {p['away_win_prob']:.1%} / {p['home_win_prob']:.1%} {status}")
                    return jsonify(todays_predictions)
                else:
                    print(f"⚠️  No predictions found for today ({today}) in file")
        except Exception as file_error:
            print(f"Could not read predictions file: {file_error}")
        
        # Fallback: Try to use the actual prediction model OR fetches Olympic schedule
        try:
            from prediction_interface import PredictionInterface
            # Check if model exists/can be used, otherwise skip to schedule fetch
            pass 
        except Exception:
            pass

        # If no predictions found in file, fetch from NHL API directly to support Olympic games
        # This acts as a fallback when the automated workflow is paused
        print("Fetching schedule directly from NHL API (Olympic Fallback)...")
        import requests
        url = f"https://api-web.nhle.com/v1/schedule/{today}"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                schedule_data = response.json()
                if schedule_data.get('gameWeek'):
                    for day in schedule_data['gameWeek']:
                        if day['date'] == today:
                            games = day.get('games', [])
                            fallback_predictions = []
                            
                            for game in games:
                                # Game Type 9 is International/Olympic
                                # We also include regular season (2) and playoffs (3) just in case
                                game_type = game.get('gameType')
                                
                                away_abbr = game.get('awayTeam', {}).get('abbrev', game.get('awayTeam', {}).get('placeName', {}).get('default'))
                                home_abbr = game.get('homeTeam', {}).get('abbrev', game.get('homeTeam', {}).get('placeName', {}).get('default'))
                                
                                if not away_abbr or not home_abbr:
                                    continue
                                    
                                # For Olympic games, we don't have a model, so return neutral 50/50
                                # The frontend will render this as a "Toss Up" or neutral matching
                                
                                fallback_predictions.append({
                                    'game_id': game.get('id'),
                                    'away_team': away_abbr,
                                    'home_team': home_abbr,
                                    'away_win_prob': 0.50,
                                    'home_win_prob': 0.50,
                                    'favorite': 'N/A',
                                    'spread': 0.0,
                                    'confidence': 'N/A', # Frontend should handle this string
                                    'start_time': game.get('startTimeUTC') # Pass through start time if needed
                                })
                            
                            if fallback_predictions:
                                print(f"✅ Found {len(fallback_predictions)} games from NHL API")
                                return jsonify(fallback_predictions)
        except Exception as api_error:
            print(f"Error fetching direct NHL schedule: {api_error}")

        return jsonify([])

    except Exception as e:
        print(f"Error in get_today_predictions: {e}")
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

@app.route('/api/team-data', methods=['GET'])
def get_team_data():
    """Get team-level data from MoneyPuck teams.csv"""
    try:
        season = request.args.get('season', '2025')
        game_type = request.args.get('type', 'regular')
        situation = request.args.get('situation', '5on5')  # 5on5, all, etc
        
        url = f"https://moneypuck.com/moneypuck/playerData/seasonSummary/{season}/{game_type}/teams.csv"
        response = requests.get(url, timeout=15)
        
        if response.status_code != 200:
            return jsonify({'error': 'Failed to fetch team data'}), 500
        
        teams_data = {}
        content = response.content.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(content))
        
        for row in csv_reader:
            if row['situation'] == situation:
                team_abbr = row['team']
                if team_abbr not in teams_data:
                    teams_data[team_abbr] = {}
                
                # Add all relevant fields
                def safe_float(val, default=0.0):
                    try:
                        return float(val) if val else default
                    except:
                        return default
                
                def safe_int(val, default=0):
                    try:
                        return int(float(val)) if val else default
                    except:
                        return default
                
                teams_data[team_abbr] = {
                    'team': team_abbr,
                    'situation': situation,
                    'games_played': safe_int(row.get('games_played')),
                    'xGoalsPercentage': safe_float(row.get('xGoalsPercentage')) * 100,
                    'corsiPercentage': safe_float(row.get('corsiPercentage')) * 100,
                    'fenwickPercentage': safe_float(row.get('fenwickPercentage')) * 100,
                    'iceTime': safe_float(row.get('iceTime')),
                    'xGoalsFor': safe_float(row.get('xGoalsFor')),
                    'xGoalsAgainst': safe_float(row.get('xGoalsAgainst')),
                    'goalsFor': safe_int(row.get('goalsFor')),
                    'goalsAgainst': safe_int(row.get('goalsAgainst')),
                    'shotsOnGoalFor': safe_int(row.get('shotsOnGoalFor')),
                    'shotsOnGoalAgainst': safe_int(row.get('shotsOnGoalAgainst')),
                    'highDangerShotsFor': safe_int(row.get('highDangerShotsFor')),
                    'highDangerShotsAgainst': safe_int(row.get('highDangerShotsAgainst')),
                    'highDangerxGoalsFor': safe_float(row.get('highDangerxGoalsFor')),
                    'highDangerxGoalsAgainst': safe_float(row.get('highDangerxGoalsAgainst')),
                    'reboundsFor': safe_int(row.get('reboundsFor')),
                    'reboundGoalsFor': safe_int(row.get('reboundGoalsFor')),
                    'xGoalsFromxReboundsOfShotsFor': safe_float(row.get('xGoalsFromxReboundsOfShotsFor')),
                    'xGoalsFromActualReboundsOfShotsFor': safe_float(row.get('xGoalsFromActualReboundsOfShotsFor')),
                    'reboundxGoalsFor': safe_float(row.get('reboundxGoalsFor')),
                    'playContinuedInZoneFor': safe_int(row.get('playContinuedInZoneFor')),
                    'playContinuedOutsideZoneFor': safe_int(row.get('playContinuedOutsideZoneFor')),
                    'playStoppedFor': safe_int(row.get('playStoppedFor')),
                    'reboundsAgainst': safe_int(row.get('reboundsAgainst')),
                    'reboundGoalsAgainst': safe_int(row.get('reboundGoalsAgainst')),
                    'playContinuedInZoneAgainst': safe_int(row.get('playContinuedInZoneAgainst')),
                }
        
        return jsonify(teams_data)
        
    except Exception as e:
        print(f"Error fetching team data: {e}")
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
            # Filter by situation if specified (handle different formats)
            row_situation = row.get('situation', '').strip()
            requested_situation = situation.strip() if situation else 'all'
            
            # Map common variations - MoneyPuck uses exact values like '5on5', 'all', 'other', etc.
            situation_map = {
                '5v5': '5on5',
                '5on5': '5on5',
                'all': 'all',
                'other': 'other'
            }
            requested_situation = situation_map.get(requested_situation.lower(), requested_situation)
            
            # Match situation (case-insensitive comparison)
            if requested_situation.lower() == 'all' or row_situation.lower() == requested_situation.lower():
                # Helper functions to safely parse values
                def safe_int(val, default=0):
                    try:
                        return int(float(val)) if val else default
                    except:
                        return default
                
                def safe_float(val, default=0.0):
                    try:
                        return round(float(val), 2) if val else default
                    except:
                        return default
                
                def safe_pct(val, default=0.0):
                    try:
                        return round(float(val) * 100, 1) if val else default
                    except:
                        return default
                
                # Return all available columns from MoneyPuck
                player = {}
                
                # Copy all fields from the row, converting numeric values appropriately
                for key, value in row.items():
                    if key in ['name', 'team', 'position', 'situation']:
                        player[key] = value
                    elif 'percentage' in key.lower() or 'pct' in key.lower():
                        player[key] = safe_pct(value)
                    elif key in ['icetime', 'gameScore', 'I_F_xGoals', 'onIce_F_xGoals', 'onIce_A_xGoals']:
                        player[key] = safe_float(value)
                    elif key.startswith('I_F_') or key.startswith('onIce_') or key.startswith('OnIce_') or key in ['games_played', 'offensiveZoneStarts', 'defensiveZoneStarts', 'neutralZoneStarts']:
                        # Try to parse as int first, fall back to float
                        try:
                            if '.' in str(value):
                                player[key] = safe_float(value)
                            else:
                                player[key] = safe_int(value)
                        except:
                            player[key] = value
                    else:
                        # Keep as string or try to parse
                        try:
                            if value and value.replace('.', '').replace('-', '').isdigit():
                                player[key] = safe_float(value) if '.' in value else safe_int(value)
                            else:
                                player[key] = value
                        except:
                            player[key] = value
                
                # Add computed fields for convenience
                player['goals'] = safe_int(row.get('I_F_goals'))
                player['assists'] = safe_int(row.get('I_F_primaryAssists', 0)) + safe_int(row.get('I_F_secondaryAssists', 0))
                player['points'] = safe_int(row.get('I_F_points'))
                player['shots'] = safe_int(row.get('I_F_shotsOnGoal'))
                player['game_score'] = safe_float(row.get('gameScore'))
                player['xgoals'] = safe_float(row.get('I_F_xGoals'))
                player['corsi_pct'] = safe_pct(row.get('onIce_corsiPercentage'))
                player['xgoals_pct'] = safe_pct(row.get('onIce_xGoalsPercentage'))
                
                players_data.append(player)
        
        return jsonify(players_data)
        
    except Exception as e:
        print(f"Error fetching player stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/team-top-performers/<team_abbr>', methods=['GET'])
def get_team_top_performers(team_abbr):
    """Get top performers from team's recent games (for pre-game display)"""
    try:
        from nhl_api_client import NHLAPIClient
        client = NHLAPIClient()
        
        # Get recent games (last 5)
        game_ids = client.get_team_recent_games(team_abbr, limit=5)
        
        if not game_ids:
            return jsonify([])
        
        # Aggregate player stats across games
        player_stats = {}  # player_id -> {name, position, sweaterNumber, total_gs, games, goals, assists, points, shots}
        
        for game_id in game_ids:
            try:
                game_data = client.get_game_center(game_id)
                if not game_data or 'boxscore' not in game_data:
                    continue
                
                boxscore = game_data['boxscore']
                player_by_game_stats = boxscore.get('playerByGameStats', {})
                
                # Determine which team's players to process
                away_team = boxscore.get('awayTeam', {})
                home_team = boxscore.get('homeTeam', {})
                
                team_player_stats = None
                if away_team.get('abbrev') == team_abbr.upper():
                    team_player_stats = player_by_game_stats.get('awayTeam', {})
                elif home_team.get('abbrev') == team_abbr.upper():
                    team_player_stats = player_by_game_stats.get('homeTeam', {})
                
                if not team_player_stats:
                    continue
                
                # Process all player groups
                for group in ['forwards', 'defense', 'goalies']:
                    players = team_player_stats.get(group, [])
                    for player in players:
                        # Try multiple possible ID fields
                        player_id = player.get('playerId') or player.get('id') or player.get('playerID')
                        if not player_id:
                            continue
                        
                        # Get name - could be in 'name' field (as object or string) or constructed from firstName/lastName
                        name = ''
                        name_field = player.get('name', '')
                        if isinstance(name_field, dict):
                            name = name_field.get('default', '')
                        elif isinstance(name_field, str):
                            name = name_field
                        
                        if not name:
                            firstName = player.get('firstName', {}).get('default', '') if isinstance(player.get('firstName'), dict) else player.get('firstName', '')
                            lastName = player.get('lastName', {}).get('default', '') if isinstance(player.get('lastName'), dict) else player.get('lastName', '')
                            name = f"{firstName} {lastName}".strip()
                        
                        if not name:
                            continue
                        
                        # Get position
                        position = player.get('position', '') or player.get('positionCode', '')
                        
                        # Stats are directly on the player object, not in a nested 'stats' field
                        stats = player.get('stats', {}) if player.get('stats') else player
                        
                        # Calculate Game Score
                        goals = stats.get('goals', 0) or 0
                        assists = stats.get('assists', 0) or 0
                        shots = stats.get('shots', 0) or stats.get('sog', 0) or stats.get('shotsOnGoal', 0) or 0
                        blocked_shots = stats.get('blockedShots', 0) or 0
                        pim = stats.get('pim', 0) or 0
                        plus_minus = stats.get('plusMinus', 0) or 0
                        
                        # Simplified Game Score calculation
                        game_score = (
                            0.75 * goals +
                            0.7 * assists +  # Simplified - not distinguishing primary/secondary
                            0.075 * shots +
                            0.05 * blocked_shots +
                            0.15 * (plus_minus if plus_minus > 0 else 0) -
                            0.15 * (abs(plus_minus) if plus_minus < 0 else 0)
                        )
                        
                        if player_id not in player_stats:
                            # Generate headshot URL from player ID
                            headshot_url = f"https://assets.nhle.com/mugs/nhl/20242025/{player_id}.jpg"
                            
                            player_stats[player_id] = {
                                'name': name,
                                'position': position,
                                'sweaterNumber': player.get('sweaterNumber', ''),
                                'playerId': player_id,
                                'headshot': headshot_url,
                                'total_gs': 0,
                                'games': 0,
                                'goals': 0,
                                'assists': 0,
                                'points': 0,
                                'shots': 0
                            }
                        
                        player_stats[player_id]['total_gs'] += game_score
                        player_stats[player_id]['games'] += 1
                        player_stats[player_id]['goals'] += goals
                        player_stats[player_id]['assists'] += assists
                        player_stats[player_id]['points'] += (goals + assists)
                        player_stats[player_id]['shots'] += shots
                        
            except Exception as e:
                print(f"Error processing game {game_id}: {e}")
                continue
        
        # Convert to list and calculate GS/GP
        performers = []
        for player_id, stats in player_stats.items():
            if stats['games'] > 0:
                performers.append({
                    'name': stats['name'],
                    'team': team_abbr.upper(),
                    'position': stats['position'],
                    'sweaterNumber': stats['sweaterNumber'],
                    'playerId': stats.get('playerId', player_id),
                    'headshot': stats.get('headshot', f"https://assets.nhle.com/mugs/nhl/20242025/{player_id}.jpg"),
                    'gsPerGame': stats['total_gs'] / stats['games'],
                    'goals': stats['goals'],
                    'assists': stats['assists'],
                    'points': stats['points'],
                    'shots': stats['shots']
                })
        
        # Sort by GS/GP and return top 5
        performers.sort(key=lambda x: x['gsPerGame'], reverse=True)
        return jsonify(performers[:5])
        
    except Exception as e:
        print(f"Error fetching team top performers: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/live-game/<game_id>', methods=['GET'])
def get_live_game_data(game_id):
    """Get live game data and predictions"""
    print(f"🚀🚀🚀 ENTERING get_live_game_data for game_id={game_id}", flush=True)
    try:
        # Get live metrics (works for live and completed games)
        live_metrics = live_predictor.get_live_game_data(game_id)
        
        if not live_metrics:
            return jsonify({"error": "Game not found"}), 404
        
        # CRITICAL: Extract physical stats from boxscore RIGHT HERE if they're 0
        # This ensures they're set before predict_live_game
        if live_metrics.get('away_hits', 0) == 0 or live_metrics.get('away_blocked_shots', 0) == 0:
            try:
                from nhl_api_client import NHLAPIClient
                api_early = NHLAPIClient()
                boxscore_early = api_early.get_game_boxscore(game_id)
                if boxscore_early and 'playerByGameStats' in boxscore_early:
                    pbg_early = boxscore_early['playerByGameStats']
                    if 'awayTeam' in pbg_early and 'homeTeam' in pbg_early:
                        away_pl_early = (pbg_early['awayTeam'].get('forwards', []) or []) + (pbg_early['awayTeam'].get('defense', []) or [])
                        home_pl_early = (pbg_early['homeTeam'].get('forwards', []) or []) + (pbg_early['homeTeam'].get('defense', []) or [])
                        live_metrics['away_hits'] = sum(p.get('hits', 0) for p in away_pl_early)
                        live_metrics['home_hits'] = sum(p.get('hits', 0) for p in home_pl_early)
                        live_metrics['away_pim'] = sum(p.get('pim', 0) for p in away_pl_early)
                        live_metrics['home_pim'] = sum(p.get('pim', 0) for p in home_pl_early)
                        live_metrics['away_blocked_shots'] = sum(p.get('blockedShots', 0) for p in away_pl_early)
                        live_metrics['home_blocked_shots'] = sum(p.get('blockedShots', 0) for p in home_pl_early)
                        live_metrics['away_giveaways'] = sum(p.get('giveaways', 0) for p in away_pl_early)
                        live_metrics['home_giveaways'] = sum(p.get('giveaways', 0) for p in home_pl_early)
                        live_metrics['away_takeaways'] = sum(p.get('takeaways', 0) for p in away_pl_early)
                        live_metrics['home_takeaways'] = sum(p.get('takeaways', 0) for p in home_pl_early)
                        print(f"✅✅✅ EARLY EXTRACTION: Set away_hits={live_metrics['away_hits']}, blocked={live_metrics['away_blocked_shots']}, gv={live_metrics['away_giveaways']}", flush=True)
            except Exception as e:
                print(f"⚠️ EARLY EXTRACTION failed: {e}", flush=True)
            
        # Generate prediction
        prediction = live_predictor.predict_live_game(live_metrics)
        
        if not prediction:
            return jsonify({"error": "Could not generate prediction"}), 500
            
        # CRITICAL: Preserve original live_metrics physical stats IMMEDIATELY after predict_live_game
        # predict_live_game might overwrite or not preserve these values, so we force them back
        if 'live_metrics' not in prediction:
            prediction['live_metrics'] = {}
        physical_stats_preserve = ['away_hits', 'home_hits', 'away_pim', 'home_pim', 'away_blocked_shots', 'home_blocked_shots', 
                                   'away_giveaways', 'home_giveaways', 'away_takeaways', 'home_takeaways', 'away_shots', 'home_shots']
        # Extract from boxscore if values are 0
        from nhl_api_client import NHLAPIClient
        api_preserve = NHLAPIClient()
        boxscore_preserve = api_preserve.get_game_boxscore(game_id)
        if boxscore_preserve and 'playerByGameStats' in boxscore_preserve:
            pbg_preserve = boxscore_preserve['playerByGameStats']
            if 'awayTeam' in pbg_preserve and 'homeTeam' in pbg_preserve:
                away_pl_preserve = (pbg_preserve['awayTeam'].get('forwards', []) or []) + (pbg_preserve['awayTeam'].get('defense', []) or [])
                home_pl_preserve = (pbg_preserve['homeTeam'].get('forwards', []) or []) + (pbg_preserve['homeTeam'].get('defense', []) or [])
                # Extract all physical stats
                prediction['live_metrics']['away_hits'] = sum(p.get('hits', 0) for p in away_pl_preserve)
                prediction['live_metrics']['home_hits'] = sum(p.get('hits', 0) for p in home_pl_preserve)
                prediction['live_metrics']['away_pim'] = sum(p.get('pim', 0) for p in away_pl_preserve)
                prediction['live_metrics']['home_pim'] = sum(p.get('pim', 0) for p in home_pl_preserve)
                prediction['live_metrics']['away_blocked_shots'] = sum(p.get('blockedShots', 0) for p in away_pl_preserve)
                prediction['live_metrics']['home_blocked_shots'] = sum(p.get('blockedShots', 0) for p in home_pl_preserve)
                prediction['live_metrics']['away_giveaways'] = sum(p.get('giveaways', 0) for p in away_pl_preserve)
                prediction['live_metrics']['home_giveaways'] = sum(p.get('giveaways', 0) for p in home_pl_preserve)
                prediction['live_metrics']['away_takeaways'] = sum(p.get('takeaways', 0) for p in away_pl_preserve)
                prediction['live_metrics']['home_takeaways'] = sum(p.get('takeaways', 0) for p in home_pl_preserve)
                # Also set at top level
                prediction['away_hits'] = prediction['live_metrics']['away_hits']
                prediction['home_hits'] = prediction['live_metrics']['home_hits']
                prediction['away_pim'] = prediction['live_metrics']['away_pim']
                prediction['home_pim'] = prediction['live_metrics']['home_pim']
                prediction['away_blocked_shots'] = prediction['live_metrics']['away_blocked_shots']
                prediction['home_blocked_shots'] = prediction['live_metrics']['home_blocked_shots']
                prediction['away_giveaways'] = prediction['live_metrics']['away_giveaways']
                prediction['home_giveaways'] = prediction['live_metrics']['home_giveaways']
                prediction['away_takeaways'] = prediction['live_metrics']['away_takeaways']
                prediction['home_takeaways'] = prediction['live_metrics']['home_takeaways']
                if boxscore_preserve.get('awayTeam', {}).get('sog'):
                    prediction['live_metrics']['away_shots'] = int(boxscore_preserve['awayTeam']['sog'])
                    prediction['away_shots'] = prediction['live_metrics']['away_shots']
                if boxscore_preserve.get('homeTeam', {}).get('sog'):
                    prediction['live_metrics']['home_shots'] = int(boxscore_preserve['homeTeam']['sog'])
                    prediction['home_shots'] = prediction['live_metrics']['home_shots']
                print(f"✅✅✅ PRESERVATION: Extracted physical stats - away_hits={prediction['live_metrics']['away_hits']}, blocked={prediction['live_metrics']['away_blocked_shots']}, gv={prediction['live_metrics']['away_giveaways']}", flush=True)
            
        print(f"🔍 Prediction keys after predict_live_game: {list(prediction.keys())[:25]}")
        print(f"🔍 Has away_period_stats: {'away_period_stats' in prediction}")
        print(f"🔍 Has home_period_stats: {'home_period_stats' in prediction}")
        
        # Remove any existing period_stats from prediction - we'll format it ourselves
        if 'period_stats' in prediction:
            del prediction['period_stats']
            
        # Transform the response to match frontend expectations
        # Frontend expects: advanced_metrics.xg.away_total, advanced_metrics.corsi.away, etc.
        # predict_live_game returns everything at top level (no 'live_metrics' key)
        # So live_data IS the prediction dict itself
        # BUT: We also create a 'live_metrics' key for frontend compatibility
        if 'live_metrics' in prediction:
            live_data = prediction['live_metrics']
        else:
            # predict_live_game returns everything at top level, so use prediction itself
            live_data = prediction
        
        # CRITICAL: Since predict_live_game merges live_metrics into result, period stats are at top level
        # But we also need to check live_metrics if it exists
        print(f"🔍 Checking for period stats in prediction structure...")
        print(f"   prediction has 'live_metrics': {'live_metrics' in prediction}")
        print(f"   prediction has 'away_period_stats' at top level: {'away_period_stats' in prediction}")
        print(f"   live_data has 'away_period_stats': {'away_period_stats' in live_data if isinstance(live_data, dict) else False}")
        if 'live_metrics' in prediction and isinstance(prediction['live_metrics'], dict):
            print(f"   prediction['live_metrics'] has 'away_period_stats': {'away_period_stats' in prediction['live_metrics']}")
        
        print(f"🔍 live_data keys: {list(live_data.keys())[:20] if isinstance(live_data, dict) else 'Not a dict'}")
        print(f"🔍 live_data has away_period_stats: {'away_period_stats' in live_data if isinstance(live_data, dict) else False}")
        
        # Initialize period_stats early to ensure it's always set
        prediction['period_stats'] = []
        
        # FORCE period_stats formatting - this MUST execute
        if live_data and isinstance(live_data, dict):
            print(f"🔍 Processing live_data for period_stats...")
            print(f"🔍 live_data keys: {list(live_data.keys())[:15]}")
            # Build the advanced_metrics structure the frontend expects
            advanced_metrics = {
                'xg': {
                    'away_total': live_data.get('away_xg', 0),
                    'home_total': live_data.get('home_xg', 0)
                },
                'corsi': {
                    'away': live_data.get('away_corsi_pct', 0),
                    'home': live_data.get('home_corsi_pct', 0)
                },
                'shot_quality': {
                    'high_danger_shots': {
                        'away': live_data.get('away_hdc', 0),
                        'home': live_data.get('home_hdc', 0)
                    },
                    'shooting_percentage': {
                        'away': (live_data.get('away_score', 0) / live_data.get('away_shots', 1) * 100) if live_data.get('away_shots', 0) > 0 else 0,
                        'home': (live_data.get('home_score', 0) / live_data.get('home_shots', 1) * 100) if live_data.get('home_shots', 0) > 0 else 0
                    }
                },
                'pressure': {
                    'oz_shots': {
                        'away': live_data.get('away_ozs', 0),
                        'home': live_data.get('home_ozs', 0)
                    },
                    'rush_shots': {
                        'away': live_data.get('away_rush', 0),
                        'home': live_data.get('home_rush', 0)
                    },
                    'sustained_pressure': {
                        'away': live_data.get('away_fc', 0),
                        'home': live_data.get('home_fc', 0)
                    }
                },
                'shots': {
                    'away': live_data.get('away_shots', 0),
                    'home': live_data.get('home_shots', 0)
                }
            }
            
            # Add advanced_metrics to the prediction response
            prediction['advanced_metrics'] = advanced_metrics
            
            # Create proper live_metrics structure for frontend
            # Frontend expects liveData.period_stats, so ensure live_metrics exists
            if 'live_metrics' not in prediction:
                prediction['live_metrics'] = {}
            
            # Copy all live metrics fields into live_metrics for frontend access
            # CRITICAL: Since predict_live_game merges everything to top level via result.update(live_metrics),
            # all the keys are at prediction['away_period_stats'], not prediction['live_metrics']['away_period_stats']
            # So we need to copy from prediction (top level), not live_data
            # Physical stats are extracted separately - don't include them in the copying loop
            live_metrics_fields = [
                'away_period_stats', 'home_period_stats', 'away_period_goals', 'home_period_goals',
                'away_xg_by_period', 'home_xg_by_period', 'away_zone_metrics', 'home_zone_metrics',
                'away_xg', 'home_xg', 'away_shots', 'home_shots', 'away_corsi_pct', 'home_corsi_pct',
                'away_hdc', 'home_hdc', 'away_ozs', 'home_ozs', 'away_rush', 'home_rush', 
                'away_fc', 'home_fc', 'shots_data', 'away_score', 'home_score', 'current_period',
                'time_remaining', 'game_state', 'away_team', 'home_team', 'game_id',
                # Physical stats removed - they're extracted separately after this loop
                'away_faceoff_pct', 'home_faceoff_pct', 'away_power_play_pct', 'home_power_play_pct'
            ]
            
            # Also copy boxscore to live_metrics for frontend access to team.sog
            if 'boxscore' in live_data:
                prediction['live_metrics']['boxscore'] = live_data['boxscore']
            elif 'boxscore' in prediction:
                if 'live_metrics' not in prediction:
                    prediction['live_metrics'] = {}
                prediction['live_metrics']['boxscore'] = prediction['boxscore']
            # Physical stats that should NOT be overwritten by the copying loop
            physical_stats = ['away_hits', 'home_hits', 'away_pim', 'home_pim', 'away_blocked_shots', 'home_blocked_shots', 
                            'away_giveaways', 'home_giveaways', 'away_takeaways', 'home_takeaways', 'away_shots', 'home_shots']
            
            for key in live_metrics_fields:
                # SKIP physical stats - they're already extracted and should not be overwritten
                if key in physical_stats:
                    continue
                # Check prediction first (top level where predict_live_game puts everything)
                if key in prediction:
                    prediction['live_metrics'][key] = prediction[key]
                elif key in live_data:
                    prediction['live_metrics'][key] = live_data[key]
                # FORCE: Also check original live_metrics if still not found
                elif key in live_metrics:
                    prediction['live_metrics'][key] = live_metrics[key]
            
            # CRITICAL: Ensure ALL live metrics are copied from live_metrics to prediction['live_metrics']
            # This includes zone_metrics, period data, and all other metrics
            for key, value in live_metrics.items():
                if key not in prediction['live_metrics']:
                    prediction['live_metrics'][key] = value
                # Also ensure zone_metrics and period data are explicitly set (they're critical for period table)
                if key in ['away_zone_metrics', 'home_zone_metrics', 'away_period_goals', 'home_period_goals',
                           'away_ot_goals', 'home_ot_goals', 'away_so_goals', 'home_so_goals',
                           'away_xg_by_period', 'home_xg_by_period', 'away_period_stats', 'home_period_stats',
                           'away_gs', 'home_gs', 'away_nzt', 'home_nzt', 'away_nztsa', 'home_nztsa',
                           'away_ozs', 'home_ozs', 'away_nzs', 'home_nzs', 'away_dzs', 'home_dzs',
                           'away_fc', 'home_fc', 'away_rush', 'home_rush', 'away_hdc', 'home_hdc',
                           'away_corsi_pct', 'home_corsi_pct', 'away_xg', 'home_xg', 'current_period']:
                    prediction['live_metrics'][key] = value
            
            # FORCE: Extract physical stats AFTER the copying loop to ensure they're not overwritten
            # This is the FINAL source of truth - extract directly from boxscore
            from nhl_api_client import NHLAPIClient
            api_physical = NHLAPIClient()
            boxscore_physical = api_physical.get_game_boxscore(game_id)
            if boxscore_physical and 'playerByGameStats' in boxscore_physical:
                pbg_physical = boxscore_physical['playerByGameStats']
                if 'awayTeam' in pbg_physical and 'homeTeam' in pbg_physical:
                    away_pl_physical = (pbg_physical['awayTeam'].get('forwards', []) or []) + (pbg_physical['awayTeam'].get('defense', []) or [])
                    home_pl_physical = (pbg_physical['homeTeam'].get('forwards', []) or []) + (pbg_physical['homeTeam'].get('defense', []) or [])
                    # FORCE SET - this overwrites any 0s that might have been copied
                    prediction['live_metrics']['away_hits'] = sum(p.get('hits', 0) for p in away_pl_physical)
                    prediction['live_metrics']['home_hits'] = sum(p.get('hits', 0) for p in home_pl_physical)
                    prediction['live_metrics']['away_pim'] = sum(p.get('pim', 0) for p in away_pl_physical)
                    prediction['live_metrics']['home_pim'] = sum(p.get('pim', 0) for p in home_pl_physical)
                    prediction['live_metrics']['away_blocked_shots'] = sum(p.get('blockedShots', 0) for p in away_pl_physical)
                    prediction['live_metrics']['home_blocked_shots'] = sum(p.get('blockedShots', 0) for p in home_pl_physical)
                    prediction['live_metrics']['away_giveaways'] = sum(p.get('giveaways', 0) for p in away_pl_physical)
                    prediction['live_metrics']['home_giveaways'] = sum(p.get('giveaways', 0) for p in home_pl_physical)
                    prediction['live_metrics']['away_takeaways'] = sum(p.get('takeaways', 0) for p in away_pl_physical)
                    prediction['live_metrics']['home_takeaways'] = sum(p.get('takeaways', 0) for p in home_pl_physical)
                    # Also set at top level
                    prediction['away_hits'] = prediction['live_metrics']['away_hits']
                    prediction['home_hits'] = prediction['live_metrics']['home_hits']
                    prediction['away_pim'] = prediction['live_metrics']['away_pim']
                    prediction['home_pim'] = prediction['live_metrics']['home_pim']
                    prediction['away_blocked_shots'] = prediction['live_metrics']['away_blocked_shots']
                    prediction['home_blocked_shots'] = prediction['live_metrics']['home_blocked_shots']
                    prediction['away_giveaways'] = prediction['live_metrics']['away_giveaways']
                    prediction['home_giveaways'] = prediction['live_metrics']['home_giveaways']
                    prediction['away_takeaways'] = prediction['live_metrics']['away_takeaways']
                    prediction['home_takeaways'] = prediction['live_metrics']['home_takeaways']
                    if boxscore_physical.get('awayTeam', {}).get('sog'):
                        prediction['live_metrics']['away_shots'] = int(boxscore_physical['awayTeam']['sog'])
                        prediction['away_shots'] = prediction['live_metrics']['away_shots']
                    if boxscore_physical.get('homeTeam', {}).get('sog'):
                        prediction['live_metrics']['home_shots'] = int(boxscore_physical['homeTeam']['sog'])
                        prediction['home_shots'] = prediction['live_metrics']['home_shots']
                    print(f"✅✅✅ FINAL PHYSICAL EXTRACTION: away_hits={prediction['live_metrics']['away_hits']}, blocked={prediction['live_metrics']['away_blocked_shots']}, gv={prediction['live_metrics']['away_giveaways']}", flush=True)
            
            # Also add shots_data if available - check both live_data and live_metrics
            shots_data_to_fix = None
            if 'shots_data' in live_data:
                shots_data_to_fix = live_data['shots_data']
                print(f"🔍 API_SERVER: Found shots_data in live_data: {len(shots_data_to_fix) if shots_data_to_fix else 0} shots", flush=True)
            elif 'shots_data' in live_metrics:
                shots_data_to_fix = live_metrics['shots_data']
                print(f"🔍 API_SERVER: Found shots_data in live_metrics: {len(shots_data_to_fix) if shots_data_to_fix else 0} shots", flush=True)
            elif 'shots_data' in prediction:
                shots_data_to_fix = prediction['shots_data']
                print(f"🔍 API_SERVER: Found shots_data in prediction: {len(shots_data_to_fix) if shots_data_to_fix else 0} shots", flush=True)
            else:
                print(f"⚠️ API_SERVER: shots_data NOT FOUND in live_data, live_metrics, or prediction!", flush=True)
                print(f"   live_data keys: {list(live_data.keys())[:10] if isinstance(live_data, dict) else 'Not a dict'}", flush=True)
                print(f"   prediction keys: {list(prediction.keys())[:10] if isinstance(prediction, dict) else 'Not a dict'}", flush=True)
            
            if shots_data_to_fix:
                print(f"🔍 API_SERVER: Processing {len(shots_data_to_fix)} shots for integer conversion", flush=True)
                # FINAL SAFETY NET: Ensure all shooters are strings, never integers
                # This is the absolute last line of defense - convert any integer shooters to names
                shots_data = shots_data_to_fix
                if shots_data:
                    # Get boxscore for lookup - try multiple paths
                    boxscore_for_api_fix = live_data.get('boxscore', {})
                    if not boxscore_for_api_fix:
                        boxscore_for_api_fix = prediction.get('live_metrics', {}).get('boxscore', {})
                    if not boxscore_for_api_fix:
                        game_center = live_data.get('game_center', {})
                        boxscore_for_api_fix = game_center.get('boxscore', {}) if game_center else {}
                    
                    player_by_game_stats_api = boxscore_for_api_fix.get('playerByGameStats', {}) if boxscore_for_api_fix else {}
                    
                    # If we still don't have it, try to get it from the API client directly
                    if not player_by_game_stats_api:
                        try:
                            from nhl_api_client import NHLAPIClient
                            api_client = NHLAPIClient()
                            game_center_direct = api_client.get_game_center(game_id)
                            if game_center_direct and 'boxscore' in game_center_direct:
                                boxscore_for_api_fix = game_center_direct['boxscore']
                                player_by_game_stats_api = boxscore_for_api_fix.get('playerByGameStats', {}) if boxscore_for_api_fix else {}
                        except Exception as e:
                            print(f"⚠️ Could not fetch boxscore for API fix: {e}", flush=True)
                    
                    for shot in shots_data:
                        if 'shooter' in shot:
                            shooter_val = shot['shooter']
                            
                            # If it's an integer, convert it using boxscore lookup (same as top performers)
                            if isinstance(shooter_val, int):
                                shooter_id_to_fix = shooter_val
                                name_found = None
                                
                                # Look up in boxscore (same method as top performers)
                                if player_by_game_stats_api:
                                    for team_key in ['awayTeam', 'homeTeam']:
                                        team_players = player_by_game_stats_api.get(team_key, {})
                                        for position_group in ['forwards', 'defense', 'goalies']:
                                            players = team_players.get(position_group, [])
                                            for player in players:
                                                p_id = player.get('playerId') or player.get('id') or player.get('playerID')
                                                if p_id == shooter_id_to_fix or str(p_id) == str(shooter_id_to_fix):
                                                    # Get name - EXACT SAME METHOD AS TOP PERFORMERS
                                                    name = ''
                                                    name_field = player.get('name', '')
                                                    if isinstance(name_field, dict):
                                                        name = name_field.get('default', '')
                                                    elif isinstance(name_field, str):
                                                        name = name_field
                                                    
                                                    if not name:
                                                        firstName = player.get('firstName', {}).get('default', '') if isinstance(player.get('firstName'), dict) else player.get('firstName', '')
                                                        lastName = player.get('lastName', {}).get('default', '') if isinstance(player.get('lastName'), dict) else player.get('lastName', '')
                                                        name = f"{firstName} {lastName}".strip()
                                                    
                                                    if name:
                                                        name_found = name
                                                        break
                                            if name_found:
                                                break
                                        if name_found:
                                            break
                                
                                if name_found:
                                    shot['shooter'] = name_found
                                    shot['shooterName'] = name_found
                                    print(f"✅✅✅ API_SERVER FIX: Converted INT {shooter_id_to_fix} to name '{name_found}'", flush=True)
                                else:
                                    shot['shooter'] = f"Player #{shooter_id_to_fix}"
                                    shot['shooterName'] = shot['shooter']
                                    print(f"⚠️ API_SERVER FIX: INT {shooter_id_to_fix} not found, using fallback", flush=True)
                            # If it's a string that's just digits, convert it
                            elif isinstance(shooter_val, str) and shooter_val.isdigit():
                                shooter_id_int = int(shooter_val)
                                name_found = None
                                
                                if player_by_game_stats_api:
                                    for team_key in ['awayTeam', 'homeTeam']:
                                        team_players = player_by_game_stats_api.get(team_key, {})
                                        for position_group in ['forwards', 'defense', 'goalies']:
                                            players = team_players.get(position_group, [])
                                            for player in players:
                                                p_id = player.get('playerId') or player.get('id') or player.get('playerID')
                                                if p_id == shooter_id_int or str(p_id) == str(shooter_id_int):
                                                    name = ''
                                                    name_field = player.get('name', '')
                                                    if isinstance(name_field, dict):
                                                        name = name_field.get('default', '')
                                                    elif isinstance(name_field, str):
                                                        name = name_field
                                                    
                                                    if not name:
                                                        firstName = player.get('firstName', {}).get('default', '') if isinstance(player.get('firstName'), dict) else player.get('firstName', '')
                                                        lastName = player.get('lastName', {}).get('default', '') if isinstance(player.get('lastName'), dict) else player.get('lastName', '')
                                                        name = f"{firstName} {lastName}".strip()
                                                    
                                                    if name:
                                                        name_found = name
                                                        break
                                            if name_found:
                                                break
                                        if name_found:
                                            break
                                
                                if name_found:
                                    shot['shooter'] = name_found
                                    shot['shooterName'] = name_found
                                    print(f"✅✅✅ API_SERVER FIX: Converted STRING ID '{shooter_val}' to name '{name_found}'", flush=True)
                                else:
                                    shot['shooter'] = f"Player #{shooter_val}"
                                    shot['shooterName'] = shot['shooter']
                                    print(f"⚠️ API_SERVER FIX: STRING ID '{shooter_val}' not found, using fallback", flush=True)
                
                # Assign the fixed shots_data back
                prediction['shots_data'] = shots_data
                # Also ensure it's in live_metrics if that exists
                if 'live_metrics' in prediction:
                    prediction['live_metrics']['shots_data'] = shots_data
                print(f"✅✅✅ API_SERVER: Fixed {len(shots_data)} shots, assigned to prediction", flush=True)
            
            # Format period_stats for the frontend PeriodStatsTable component
            # Frontend expects: liveData.period_stats
            # PeriodStatsTable expects: [{ period: '1', away_stats: {...}, home_stats: {...} }, ...]
            # CRITICAL: The data IS in live_metrics.away_period_stats and live_metrics.home_period_stats (we can see it in the response)
            # Get it directly from prediction['live_metrics'] since we just copied it there
            import sys
            sys.stdout.flush()  # Force flush to see logs immediately
            
            print(f"🔍 Getting period stats from live_metrics (where we just copied them)...", flush=True)
            
            # Get from live_metrics first (most reliable since we just copied it there)
            away_period_stats = None
            home_period_stats = None
            
            # CRITICAL: Check prediction['live_metrics'] FIRST since that's where the data is in the response
            if 'live_metrics' in prediction and isinstance(prediction['live_metrics'], dict):
                away_period_stats = prediction['live_metrics'].get('away_period_stats')
                home_period_stats = prediction['live_metrics'].get('home_period_stats')
                print(f"✅ Checked prediction['live_metrics'] - away: {bool(away_period_stats)}, home: {bool(home_period_stats)}", flush=True)
            
            # Fallback: check prediction top level (where predict_live_game puts them)
            if not away_period_stats:
                away_period_stats = prediction.get('away_period_stats')
            if not home_period_stats:
                home_period_stats = prediction.get('home_period_stats')
            
            # Fallback: check live_data
            if not away_period_stats:
                away_period_stats = live_data.get('away_period_stats')
            if not home_period_stats:
                home_period_stats = live_data.get('home_period_stats')
            
            print(f"🔍 Final check - away_period_stats: {bool(away_period_stats)}, type: {type(away_period_stats)}", flush=True)
            print(f"🔍 Final check - home_period_stats: {bool(home_period_stats)}, type: {type(home_period_stats)}", flush=True)
            
            # CRITICAL: Format the data - this MUST happen if the data exists
            # The data IS in the response (live_metrics.away_period_stats exists), so this should ALWAYS run
            # If we still don't have it, get it directly from prediction['live_metrics'] one final time
            if not away_period_stats or not home_period_stats:
                print(f"⚠️ Still missing, trying ONE MORE TIME from prediction['live_metrics']...", flush=True)
                if 'live_metrics' in prediction and isinstance(prediction['live_metrics'], dict):
                    if not away_period_stats:
                        away_period_stats = prediction['live_metrics'].get('away_period_stats')
                        print(f"   Final attempt - away_period_stats: {bool(away_period_stats)}, type: {type(away_period_stats)}", flush=True)
                    if not home_period_stats:
                        home_period_stats = prediction['live_metrics'].get('home_period_stats')
                        print(f"   Final attempt - home_period_stats: {bool(home_period_stats)}, type: {type(home_period_stats)}", flush=True)
            
            if away_period_stats and home_period_stats and isinstance(away_period_stats, dict) and isinstance(home_period_stats, dict):
                print(f"✅ Formatting period_stats from play-by-play data...")
                print(f"✅ away_period_stats is dict: {isinstance(away_period_stats, dict)}, keys: {list(away_period_stats.keys())}")
                print(f"✅ home_period_stats is dict: {isinstance(home_period_stats, dict)}, keys: {list(home_period_stats.keys())}")
                # Get period goals - these should now be in live_data
                away_period_goals = live_data.get('away_period_goals', [0, 0, 0])
                home_period_goals = live_data.get('home_period_goals', [0, 0, 0])
                away_ot_goals = live_data.get('away_ot_goals', 0)
                home_ot_goals = live_data.get('home_ot_goals', 0)
                away_so_goals = live_data.get('away_so_goals', 0)
                home_so_goals = live_data.get('home_so_goals', 0)
                print(f"   away_period_goals: {away_period_goals}")
                print(f"   home_period_goals: {home_period_goals}")
                print(f"   OT/SO goals - away: OT={away_ot_goals}, SO={away_so_goals}, home: OT={home_ot_goals}, SO={home_so_goals}")
                
                # Get xG by period
                away_xg_by_period = live_data.get('away_xg_by_period', [0, 0, 0])
                home_xg_by_period = live_data.get('home_xg_by_period', [0, 0, 0])
                
                # Get zone metrics per period if available
                away_zone_metrics = live_data.get('away_zone_metrics', {})
                home_zone_metrics = live_data.get('home_zone_metrics', {})
                
                # Get current period to determine which periods to show (MUST be before OT check)
                current_period = live_data.get('current_period', 1)
                game_state = live_data.get('game_state', '')
                
                # CRITICAL: Dynamically determine current_period from play-by-play if available
                # This ensures we show the active period even if it just started
                if game_state not in ['FINAL', 'OFF']:
                    # Fetch play-by-play data directly from NHL API to get the most accurate current period
                    try:
                        from nhl_api_client import NHLAPIClient
                        api_client = NHLAPIClient()
                        play_by_play = api_client.get_play_by_play(game_id)
                        if play_by_play:
                            plays = play_by_play.get('plays', []) if play_by_play else []
                            if plays:
                                # Get the most recent play's period - this is the ACTIVE period
                                last_play = plays[-1]
                                last_play_period = last_play.get('periodDescriptor', {}).get('number', current_period)
                                if last_play_period and last_play_period > 0:
                                    current_period = last_play_period
                                    print(f"   ✅ Dynamically determined current_period from play-by-play: {current_period} (was {live_data.get('current_period', 1)})")
                                    # CRITICAL: Update current_period in live_data and prediction so frontend receives it
                                    live_data['current_period'] = current_period
                                    prediction['current_period'] = current_period
                                    if 'live_metrics' in prediction:
                                        prediction['live_metrics']['current_period'] = current_period
                    except Exception as e:
                        print(f"   ⚠️ Could not get current_period from play-by-play: {e}")
                        import traceback
                        traceback.print_exc()
                
                # CRITICAL: For completed games (FINAL/OFF), always show all 3 periods
                # Also check if we have period stats with data for all 3 periods (indicates game is complete)
                if game_state in ['FINAL', 'OFF']:
                    current_period = 3  # Force show all periods for completed games
                    # CRITICAL: Update current_period in all places so frontend receives it
                    live_data['current_period'] = current_period
                    prediction['current_period'] = current_period
                    if 'live_metrics' in prediction:
                        prediction['live_metrics']['current_period'] = current_period
                    print(f"   ✅ Game is FINAL/OFF, showing all 3 periods (current_period set to {current_period})")
                elif away_period_stats and home_period_stats:
                    # If we have period stats with data for all periods, show all periods
                    away_shots_list = away_period_stats.get('shots', [])
                    home_shots_list = home_period_stats.get('shots', [])
                    # Check if we have data for period 3 (game is likely complete)
                    if len(away_shots_list) >= 3 and len(home_shots_list) >= 3:
                        # If period 3 has any shots, the game is complete
                        if away_shots_list[2] > 0 or home_shots_list[2] > 0:
                            current_period = 3  # Game is complete, show all periods
                            print(f"   ✅ Period 3 has data, showing all 3 periods")
                    # Also check if we have period goals for period 3
                    if len(away_period_goals) >= 3 and len(home_period_goals) >= 3:
                        if away_period_goals[2] > 0 or home_period_goals[2] > 0:
                            current_period = 3
                            print(f"   ✅ Period 3 has goals, showing all 3 periods")
                
                # Check if game has OT/SO periods
                # If OT/SO goals exist, then those periods occurred
                has_ot = (away_ot_goals > 0 or home_ot_goals > 0)
                has_so = (away_so_goals > 0 or home_so_goals > 0)
                # Also check if current_period >= 4 (indicates OT is active/completed)
                if current_period >= 4:
                    has_ot = True
                
                # Also try to check using report generator if game_data is available
                try:
                    game_data_check = prediction.get('game_data') or live_data.get('game_data') or live_metrics.get('game_data')
                    if game_data_check:
                        from pdf_report_generator import PostGameReportGenerator
                        report_gen_check = PostGameReportGenerator()
                        has_ot_from_check = report_gen_check._check_for_ot_period(game_data_check)
                        if has_ot_from_check:
                            has_ot = True
                except:
                    pass  # Non-critical, continue with existing logic
                
                print(f"   Current period: {current_period}, game_state: {game_state}, has_ot: {has_ot}, has_so: {has_so}")
                
                # Build period stats array - only include periods that are active or completed
                period_stats_array = []
                for period_num in range(1, 4):  # Periods 1, 2, 3
                    # Only show period if it's completed or currently active
                    # For completed games (FINAL/OFF), always show all periods
                    # For live games, show periods <= current_period (including the active period)
                    if game_state not in ['FINAL', 'OFF'] and period_num > current_period:
                        continue  # Skip future periods for live games
                    # Always include the current_period (active period) even if it just started
                    period_idx = period_num - 1
                    
                    # Get zone metrics per period if available
                    away_ozs_period = away_zone_metrics.get('oz_originating_shots', [0, 0, 0])[period_idx] if isinstance(away_zone_metrics, dict) and period_idx < len(away_zone_metrics.get('oz_originating_shots', [])) else 0
                    away_dzs_period = away_zone_metrics.get('dz_originating_shots', [0, 0, 0])[period_idx] if isinstance(away_zone_metrics, dict) and period_idx < len(away_zone_metrics.get('dz_originating_shots', [])) else 0
                    away_nzs_period = away_zone_metrics.get('nz_originating_shots', [0, 0, 0])[period_idx] if isinstance(away_zone_metrics, dict) and period_idx < len(away_zone_metrics.get('nz_originating_shots', [])) else 0
                    away_nzt_period = away_zone_metrics.get('nz_turnovers', [0, 0, 0])[period_idx] if isinstance(away_zone_metrics, dict) and period_idx < len(away_zone_metrics.get('nz_turnovers', [])) else 0
                    away_nztsa_period = away_zone_metrics.get('nz_turnovers_to_shots', [0, 0, 0])[period_idx] if isinstance(away_zone_metrics, dict) and period_idx < len(away_zone_metrics.get('nz_turnovers_to_shots', [])) else 0
                    away_rush_period = away_zone_metrics.get('rush_sog', [0, 0, 0])[period_idx] if isinstance(away_zone_metrics, dict) and period_idx < len(away_zone_metrics.get('rush_sog', [])) else 0
                    away_fc_period = away_zone_metrics.get('fc_cycle_sog', [0, 0, 0])[period_idx] if isinstance(away_zone_metrics, dict) and period_idx < len(away_zone_metrics.get('fc_cycle_sog', [])) else 0
                    
                    home_ozs_period = home_zone_metrics.get('oz_originating_shots', [0, 0, 0])[period_idx] if isinstance(home_zone_metrics, dict) and period_idx < len(home_zone_metrics.get('oz_originating_shots', [])) else 0
                    home_dzs_period = home_zone_metrics.get('dz_originating_shots', [0, 0, 0])[period_idx] if isinstance(home_zone_metrics, dict) and period_idx < len(home_zone_metrics.get('dz_originating_shots', [])) else 0
                    home_nzs_period = home_zone_metrics.get('nz_originating_shots', [0, 0, 0])[period_idx] if isinstance(home_zone_metrics, dict) and period_idx < len(home_zone_metrics.get('nz_originating_shots', [])) else 0
                    home_nzt_period = home_zone_metrics.get('nz_turnovers', [0, 0, 0])[period_idx] if isinstance(home_zone_metrics, dict) and period_idx < len(home_zone_metrics.get('nz_turnovers', [])) else 0
                    home_nztsa_period = home_zone_metrics.get('nz_turnovers_to_shots', [0, 0, 0])[period_idx] if isinstance(home_zone_metrics, dict) and period_idx < len(home_zone_metrics.get('nz_turnovers_to_shots', [])) else 0
                    home_rush_period = home_zone_metrics.get('rush_sog', [0, 0, 0])[period_idx] if isinstance(home_zone_metrics, dict) and period_idx < len(home_zone_metrics.get('rush_sog', [])) else 0
                    home_fc_period = home_zone_metrics.get('fc_cycle_sog', [0, 0, 0])[period_idx] if isinstance(home_zone_metrics, dict) and period_idx < len(home_zone_metrics.get('fc_cycle_sog', [])) else 0
                    
                    # Get goals against (opposite team's goals for)
                    away_ga = home_period_goals[period_idx] if period_idx < len(home_period_goals) else 0
                    home_ga = away_period_goals[period_idx] if period_idx < len(away_period_goals) else 0
                    
                    # Get xG against (opposite team's xG for)
                    away_xga = home_xg_by_period[period_idx] if period_idx < len(home_xg_by_period) else 0
                    home_xga = away_xg_by_period[period_idx] if period_idx < len(away_xg_by_period) else 0
                    
                    period_stats_array.append({
                        'period': str(period_num),
                        'away_stats': {
                            'goals': away_period_goals[period_idx] if period_idx < len(away_period_goals) else 0,
                            'ga': away_ga,
                            'shots': away_period_stats.get('shots', [0, 0, 0])[period_idx] if period_idx < len(away_period_stats.get('shots', [])) else 0,
                            'corsi': away_period_stats.get('corsi_pct', [50, 50, 50])[period_idx] if period_idx < len(away_period_stats.get('corsi_pct', [])) else 50,
                            'xg': away_xg_by_period[period_idx] if period_idx < len(away_xg_by_period) else 0,
                            'xga': away_xga,
                            'hits': away_period_stats.get('hits', [0, 0, 0])[period_idx] if period_idx < len(away_period_stats.get('hits', [])) else 0,
                            'faceoff_pct': away_period_stats.get('fo_pct', [None, None, None])[period_idx] if period_idx < len(away_period_stats.get('fo_pct', [])) else None,
                            'pim': away_period_stats.get('pim', [0, 0, 0])[period_idx] if period_idx < len(away_period_stats.get('pim', [])) else 0,
                            'blocked_shots': away_period_stats.get('bs', [0, 0, 0])[period_idx] if period_idx < len(away_period_stats.get('bs', [])) else 0,
                            'giveaways': away_period_stats.get('gv', [0, 0, 0])[period_idx] if period_idx < len(away_period_stats.get('gv', [])) else 0,
                            'takeaways': away_period_stats.get('tk', [0, 0, 0])[period_idx] if period_idx < len(away_period_stats.get('tk', [])) else 0,
                            'nzt': away_nzt_period,
                            'nztsa': away_nztsa_period,
                            'ozs': away_ozs_period,
                            'dzs': away_dzs_period,
                            'nzs': away_nzs_period,
                            'rush': away_rush_period,
                            'fc': away_fc_period
                        },
                        'home_stats': {
                            'goals': home_period_goals[period_idx] if period_idx < len(home_period_goals) else 0,
                            'ga': home_ga,
                            'shots': home_period_stats.get('shots', [0, 0, 0])[period_idx] if period_idx < len(home_period_stats.get('shots', [])) else 0,
                            'corsi': home_period_stats.get('corsi_pct', [50, 50, 50])[period_idx] if period_idx < len(home_period_stats.get('corsi_pct', [])) else 50,
                            'xg': home_xg_by_period[period_idx] if period_idx < len(home_xg_by_period) else 0,
                            'xga': home_xga,
                            'hits': home_period_stats.get('hits', [0, 0, 0])[period_idx] if period_idx < len(home_period_stats.get('hits', [])) else 0,
                            'faceoff_pct': home_period_stats.get('fo_pct', [None, None, None])[period_idx] if period_idx < len(home_period_stats.get('fo_pct', [])) else None,
                            'pim': home_period_stats.get('pim', [0, 0, 0])[period_idx] if period_idx < len(home_period_stats.get('pim', [])) else 0,
                            'blocked_shots': home_period_stats.get('bs', [0, 0, 0])[period_idx] if period_idx < len(home_period_stats.get('bs', [])) else 0,
                            'giveaways': home_period_stats.get('gv', [0, 0, 0])[period_idx] if period_idx < len(home_period_stats.get('gv', [])) else 0,
                            'takeaways': home_period_stats.get('tk', [0, 0, 0])[period_idx] if period_idx < len(home_period_stats.get('tk', [])) else 0,
                            'nzt': home_nzt_period,
                            'nztsa': home_nztsa_period,
                            'ozs': home_ozs_period,
                            'dzs': home_dzs_period,
                            'nzs': home_nzs_period,
                            'rush': home_rush_period,
                            'fc': home_fc_period
                        }
                    })
                
                # Add OT period if it occurred and is active/completed
                if has_ot and (current_period >= 4 or live_data.get('game_state') in ['FINAL', 'OFF']):
                    # Get OT stats using the report generator
                    # Try to get game_data from live_metrics or fetch it if needed
                    try:
                        from pdf_report_generator import PostGameReportGenerator
                        from nhl_api_client import NHLAPIClient
                        report_gen = PostGameReportGenerator()
                        # Try to get game_data from various sources
                        game_data_ot = prediction.get('game_data') or live_data.get('game_data') or live_metrics.get('game_data')
                        # If not available, try to fetch it
                        if not game_data_ot:
                            try:
                                api_client = NHLAPIClient()
                                game_data_ot = api_client.get_comprehensive_game_data(game_id)
                            except:
                                pass
                        if game_data_ot:
                            away_ot_stats = report_gen._calculate_ot_so_stats(game_data_ot, live_data.get('away_team_id') or prediction.get('away_team_id'), 'away', 'OT')
                            home_ot_stats = report_gen._calculate_ot_so_stats(game_data_ot, live_data.get('home_team_id') or prediction.get('home_team_id'), 'home', 'OT')
                            
                            period_stats_array.append({
                                'period': 'OT',
                                'away_stats': {
                                    'goals': away_ot_goals,
                                    'ga': home_ot_goals,
                                    'shots': away_ot_stats.get('shots', 0),
                                    'corsi': away_ot_stats.get('corsi_pct', 50.0),
                                    'xg': away_ot_stats.get('xg', 0.0),
                                    'xga': home_ot_stats.get('xg', 0.0),
                                    'hits': away_ot_stats.get('hits', 0),
                                    'faceoff_pct': away_ot_stats.get('fo_pct', None),
                                    'pim': away_ot_stats.get('pim', 0),
                                    'blocked_shots': away_ot_stats.get('bs', 0),
                                    'giveaways': away_ot_stats.get('gv', 0),
                                    'takeaways': away_ot_stats.get('tk', 0),
                                    'nzt': away_ot_stats.get('nz_turnovers', 0),
                                    'nztsa': away_ot_stats.get('nz_turnovers_to_shots', 0),
                                    'ozs': away_ot_stats.get('oz_originating_shots', 0),
                                    'dzs': away_ot_stats.get('dz_originating_shots', 0),
                                    'nzs': away_ot_stats.get('nz_originating_shots', 0),
                                    'rush': away_ot_stats.get('rush_sog', 0),
                                    'fc': away_ot_stats.get('fc_cycle_sog', 0)
                                },
                                'home_stats': {
                                    'goals': home_ot_goals,
                                    'ga': away_ot_goals,
                                    'shots': home_ot_stats.get('shots', 0),
                                    'corsi': home_ot_stats.get('corsi_pct', 50.0),
                                    'xg': home_ot_stats.get('xg', 0.0),
                                    'xga': away_ot_stats.get('xg', 0.0),
                                    'hits': home_ot_stats.get('hits', 0),
                                    'faceoff_pct': home_ot_stats.get('fo_pct', None),
                                    'pim': home_ot_stats.get('pim', 0),
                                    'blocked_shots': home_ot_stats.get('bs', 0),
                                    'giveaways': home_ot_stats.get('gv', 0),
                                    'takeaways': home_ot_stats.get('tk', 0),
                                    'nzt': home_ot_stats.get('nz_turnovers', 0),
                                    'nztsa': home_ot_stats.get('nz_turnovers_to_shots', 0),
                                    'ozs': home_ot_stats.get('oz_originating_shots', 0),
                                    'dzs': home_ot_stats.get('dz_originating_shots', 0),
                                    'nzs': home_ot_stats.get('nz_originating_shots', 0),
                                    'rush': home_ot_stats.get('rush_sog', 0),
                                    'fc': home_ot_stats.get('fc_cycle_sog', 0)
                                }
                            })
                            print(f"✅ Added OT period to period_stats")
                    except Exception as e:
                        print(f"⚠️ Error calculating OT stats: {e}")
                
                # Add SO period if it occurred (only show if game is final)
                if has_so and live_data.get('game_state') in ['FINAL', 'OFF']:
                    try:
                        from pdf_report_generator import PostGameReportGenerator
                        from nhl_api_client import NHLAPIClient
                        report_gen = PostGameReportGenerator()
                        # Try to get game_data from various sources
                        game_data_so = prediction.get('game_data') or live_data.get('game_data') or live_metrics.get('game_data')
                        # If not available, try to fetch it
                        if not game_data_so:
                            try:
                                api_client = NHLAPIClient()
                                game_data_so = api_client.get_comprehensive_game_data(game_id)
                            except:
                                pass
                        if game_data_so:
                            away_so_stats = report_gen._calculate_ot_so_stats(game_data_so, live_data.get('away_team_id') or prediction.get('away_team_id'), 'away', 'SO')
                            home_so_stats = report_gen._calculate_ot_so_stats(game_data_so, live_data.get('home_team_id') or prediction.get('home_team_id'), 'home', 'SO')
                            
                            period_stats_array.append({
                                'period': 'SO',
                                'away_stats': {
                                    'goals': away_so_goals,
                                    'ga': home_so_goals,
                                    'shots': away_so_stats.get('shots', 0),
                                    'corsi': away_so_stats.get('corsi_pct', 50.0),
                                    'xg': away_so_stats.get('xg', 0.0),
                                    'xga': home_so_stats.get('xg', 0.0),
                                    'hits': away_so_stats.get('hits', 0),
                                    'faceoff_pct': away_so_stats.get('fo_pct', None),
                                    'pim': away_so_stats.get('pim', 0),
                                    'blocked_shots': away_so_stats.get('bs', 0),
                                    'giveaways': away_so_stats.get('gv', 0),
                                    'takeaways': away_so_stats.get('tk', 0),
                                    'nzt': away_so_stats.get('nz_turnovers', 0),
                                    'nztsa': away_so_stats.get('nz_turnovers_to_shots', 0),
                                    'ozs': away_so_stats.get('oz_originating_shots', 0),
                                    'dzs': away_so_stats.get('dz_originating_shots', 0),
                                    'nzs': away_so_stats.get('nz_originating_shots', 0),
                                    'rush': away_so_stats.get('rush_sog', 0),
                                    'fc': away_so_stats.get('fc_cycle_sog', 0)
                                },
                                'home_stats': {
                                    'goals': home_so_goals,
                                    'ga': away_so_goals,
                                    'shots': home_so_stats.get('shots', 0),
                                    'corsi': home_so_stats.get('corsi_pct', 50.0),
                                    'xg': home_so_stats.get('xg', 0.0),
                                    'xga': away_so_stats.get('xg', 0.0),
                                    'hits': home_so_stats.get('hits', 0),
                                    'faceoff_pct': home_so_stats.get('fo_pct', None),
                                    'pim': home_so_stats.get('pim', 0),
                                    'blocked_shots': home_so_stats.get('bs', 0),
                                    'giveaways': home_so_stats.get('gv', 0),
                                    'takeaways': home_so_stats.get('tk', 0),
                                    'nzt': home_so_stats.get('nz_turnovers', 0),
                                    'nztsa': home_so_stats.get('nz_turnovers_to_shots', 0),
                                    'ozs': home_so_stats.get('oz_originating_shots', 0),
                                    'dzs': home_so_stats.get('dz_originating_shots', 0),
                                    'nzs': home_so_stats.get('nz_originating_shots', 0),
                                    'rush': home_so_stats.get('rush_sog', 0),
                                    'fc': home_so_stats.get('fc_cycle_sog', 0)
                                }
                            })
                            print(f"✅ Added SO period to period_stats")
                    except Exception as e:
                        print(f"⚠️ Error calculating SO stats: {e}")
                
                # CRITICAL: Set period_stats at top level AND in live_metrics for frontend
                prediction['period_stats'] = period_stats_array
                print(f"✅ Set prediction['period_stats'] = {len(period_stats_array)} periods")
                
                # Ensure live_metrics exists and set period_stats there
                if 'live_metrics' not in prediction:
                    prediction['live_metrics'] = {}
                prediction['live_metrics']['period_stats'] = period_stats_array
                print(f"✅ Set prediction['live_metrics']['period_stats'] = {len(period_stats_array)} periods")
                
                # SUM PERIOD STATS to get overall totals for physical stats
                # This ensures live_metrics has the correct totals even if extraction failed
                away_blocked_total = sum(p.get('away_stats', {}).get('blocked_shots', 0) for p in period_stats_array)
                home_blocked_total = sum(p.get('home_stats', {}).get('blocked_shots', 0) for p in period_stats_array)
                away_giveaways_total = sum(p.get('away_stats', {}).get('giveaways', 0) for p in period_stats_array)
                home_giveaways_total = sum(p.get('home_stats', {}).get('giveaways', 0) for p in period_stats_array)
                away_takeaways_total = sum(p.get('away_stats', {}).get('takeaways', 0) for p in period_stats_array)
                home_takeaways_total = sum(p.get('home_stats', {}).get('takeaways', 0) for p in period_stats_array)
                away_hits_total = sum(p.get('away_stats', {}).get('hits', 0) for p in period_stats_array)
                home_hits_total = sum(p.get('home_stats', {}).get('hits', 0) for p in period_stats_array)
                away_pim_total = sum(p.get('away_stats', {}).get('pim', 0) for p in period_stats_array)
                home_pim_total = sum(p.get('home_stats', {}).get('pim', 0) for p in period_stats_array)
                
                # Only set if we got values from period stats (don't overwrite with 0)
                if away_blocked_total > 0:
                    prediction['live_metrics']['away_blocked_shots'] = away_blocked_total
                    print(f"✅ SUMMED away_blocked_shots from period_stats: {away_blocked_total}", flush=True)
                if home_blocked_total > 0:
                    prediction['live_metrics']['home_blocked_shots'] = home_blocked_total
                    print(f"✅ SUMMED home_blocked_shots from period_stats: {home_blocked_total}", flush=True)
                if away_giveaways_total > 0:
                    prediction['live_metrics']['away_giveaways'] = away_giveaways_total
                    print(f"✅ SUMMED away_giveaways from period_stats: {away_giveaways_total}", flush=True)
                if home_giveaways_total > 0:
                    prediction['live_metrics']['home_giveaways'] = home_giveaways_total
                    print(f"✅ SUMMED home_giveaways from period_stats: {home_giveaways_total}", flush=True)
                if away_takeaways_total > 0:
                    prediction['live_metrics']['away_takeaways'] = away_takeaways_total
                    print(f"✅ SUMMED away_takeaways from period_stats: {away_takeaways_total}", flush=True)
                if home_takeaways_total > 0:
                    prediction['live_metrics']['home_takeaways'] = home_takeaways_total
                    print(f"✅ SUMMED home_takeaways from period_stats: {home_takeaways_total}", flush=True)
                if away_hits_total > 0:
                    prediction['live_metrics']['away_hits'] = away_hits_total
                    print(f"✅ SUMMED away_hits from period_stats: {away_hits_total}", flush=True)
                if home_hits_total > 0:
                    prediction['live_metrics']['home_hits'] = home_hits_total
                    print(f"✅ SUMMED home_hits from period_stats: {home_hits_total}", flush=True)
                if away_pim_total > 0:
                    prediction['live_metrics']['away_pim'] = away_pim_total
                    print(f"✅ SUMMED away_pim from period_stats: {away_pim_total}", flush=True)
                if home_pim_total > 0:
                    prediction['live_metrics']['home_pim'] = home_pim_total
                    print(f"✅ SUMMED home_pim from period_stats: {home_pim_total}", flush=True)
            else:
                print(f"❌ ERROR: Cannot format period_stats!")
                print(f"   away_period_stats: {bool(away_period_stats)}, type: {type(away_period_stats)}")
                print(f"   home_period_stats: {bool(home_period_stats)}, type: {type(home_period_stats)}")
                if away_period_stats:
                    print(f"   away_period_stats is dict: {isinstance(away_period_stats, dict)}")
                if home_period_stats:
                    print(f"   home_period_stats is dict: {isinstance(home_period_stats, dict)}")
                print(f"   live_data keys: {list(live_data.keys())[:20] if isinstance(live_data, dict) else 'Not a dict'}")
                print(f"   prediction keys: {list(prediction.keys())[:30] if isinstance(prediction, dict) else 'Not a dict'}")
                if 'live_metrics' in prediction:
                    print(f"   prediction['live_metrics'] keys: {list(prediction['live_metrics'].keys())[:30] if isinstance(prediction['live_metrics'], dict) else 'Not a dict'}")
                
                # FALLBACK: Try to calculate period stats directly from play-by-play if we have game_data
                # This is a last resort if period stats weren't calculated in get_live_game_data
                try:
                    print(f"🔄 Attempting fallback: calculating period stats directly from play-by-play...")
                    # We need to get the game_data to access play-by-play
                    # Try to get it from live_predictor's cache or fetch it
                    game_data = live_predictor.api.get_comprehensive_game_data(game_id)
                    if game_data and game_data.get('play_by_play'):
                        # Use the same report_generator that live_predictor uses
                        report_gen = live_predictor.report_generator
                        
                        # Get team IDs from live_data
                        away_team_id = live_data.get('away_team_id') or (live_data.get('away_team') and live_data.get('away_team').get('id'))
                        home_team_id = live_data.get('home_team_id') or (live_data.get('home_team') and live_data.get('home_team').get('id'))
                        
                        if away_team_id and home_team_id:
                            print(f"🔄 Calculating with team IDs: away={away_team_id}, home={home_team_id}")
                            away_period_stats = report_gen._calculate_real_period_stats(game_data, away_team_id, 'away')
                            home_period_stats = report_gen._calculate_real_period_stats(game_data, home_team_id, 'home')
                            
                            if away_period_stats and home_period_stats:
                                print(f"✅ Fallback calculation successful!")
                                # Now format it the same way as above
                                away_period_goals = live_data.get('away_period_goals', [0, 0, 0])
                                home_period_goals = live_data.get('home_period_goals', [0, 0, 0])
                                away_xg_by_period = live_data.get('away_xg_by_period', [0, 0, 0])
                                home_xg_by_period = live_data.get('home_xg_by_period', [0, 0, 0])
                                away_zone_metrics = live_data.get('away_zone_metrics', {})
                                home_zone_metrics = live_data.get('home_zone_metrics', {})
                                
                                # Get current period to filter periods
                                current_period = live_data.get('current_period', 1)
                                game_state_fallback = live_data.get('game_state', '')
                                
                                # CRITICAL: For completed games (FINAL/OFF), always show all 3 periods
                                if game_state_fallback in ['FINAL', 'OFF']:
                                    current_period = 3
                                    print(f"   ✅ Fallback: Game is FINAL/OFF, showing all 3 periods")
                                
                                period_stats_array = []
                                for period_num in range(1, 4):
                                    # Only show period if it's completed or currently active
                                    # For completed games (FINAL/OFF), always show all periods
                                    if game_state_fallback not in ['FINAL', 'OFF'] and period_num > current_period:
                                        continue  # Skip future periods for live games
                                    period_idx = period_num - 1
                                    # Get zone metrics per period
                                    away_ozs_period = away_zone_metrics.get('oz_originating_shots', [0, 0, 0])[period_idx] if isinstance(away_zone_metrics, dict) and period_idx < len(away_zone_metrics.get('oz_originating_shots', [])) else 0
                                    away_dzs_period = away_zone_metrics.get('dz_originating_shots', [0, 0, 0])[period_idx] if isinstance(away_zone_metrics, dict) and period_idx < len(away_zone_metrics.get('dz_originating_shots', [])) else 0
                                    away_nzs_period = away_zone_metrics.get('nz_originating_shots', [0, 0, 0])[period_idx] if isinstance(away_zone_metrics, dict) and period_idx < len(away_zone_metrics.get('nz_originating_shots', [])) else 0
                                    away_nzt_period = away_zone_metrics.get('nz_turnovers', [0, 0, 0])[period_idx] if isinstance(away_zone_metrics, dict) and period_idx < len(away_zone_metrics.get('nz_turnovers', [])) else 0
                                    away_nztsa_period = away_zone_metrics.get('nz_turnovers_to_shots', [0, 0, 0])[period_idx] if isinstance(away_zone_metrics, dict) and period_idx < len(away_zone_metrics.get('nz_turnovers_to_shots', [])) else 0
                                    away_rush_period = away_zone_metrics.get('rush_sog', [0, 0, 0])[period_idx] if isinstance(away_zone_metrics, dict) and period_idx < len(away_zone_metrics.get('rush_sog', [])) else 0
                                    away_fc_period = away_zone_metrics.get('fc_cycle_sog', [0, 0, 0])[period_idx] if isinstance(away_zone_metrics, dict) and period_idx < len(away_zone_metrics.get('fc_cycle_sog', [])) else 0
                                    
                                    home_ozs_period = home_zone_metrics.get('oz_originating_shots', [0, 0, 0])[period_idx] if isinstance(home_zone_metrics, dict) and period_idx < len(home_zone_metrics.get('oz_originating_shots', [])) else 0
                                    home_dzs_period = home_zone_metrics.get('dz_originating_shots', [0, 0, 0])[period_idx] if isinstance(home_zone_metrics, dict) and period_idx < len(home_zone_metrics.get('dz_originating_shots', [])) else 0
                                    home_nzs_period = home_zone_metrics.get('nz_originating_shots', [0, 0, 0])[period_idx] if isinstance(home_zone_metrics, dict) and period_idx < len(home_zone_metrics.get('nz_originating_shots', [])) else 0
                                    home_nzt_period = home_zone_metrics.get('nz_turnovers', [0, 0, 0])[period_idx] if isinstance(home_zone_metrics, dict) and period_idx < len(home_zone_metrics.get('nz_turnovers', [])) else 0
                                    home_nztsa_period = home_zone_metrics.get('nz_turnovers_to_shots', [0, 0, 0])[period_idx] if isinstance(home_zone_metrics, dict) and period_idx < len(home_zone_metrics.get('nz_turnovers_to_shots', [])) else 0
                                    home_rush_period = home_zone_metrics.get('rush_sog', [0, 0, 0])[period_idx] if isinstance(home_zone_metrics, dict) and period_idx < len(home_zone_metrics.get('rush_sog', [])) else 0
                                    home_fc_period = home_zone_metrics.get('fc_cycle_sog', [0, 0, 0])[period_idx] if isinstance(home_zone_metrics, dict) and period_idx < len(home_zone_metrics.get('fc_cycle_sog', [])) else 0
                                    
                                    away_ga = home_period_goals[period_idx] if period_idx < len(home_period_goals) else 0
                                    home_ga = away_period_goals[period_idx] if period_idx < len(away_period_goals) else 0
                                    away_xga = home_xg_by_period[period_idx] if period_idx < len(home_xg_by_period) else 0
                                    home_xga = away_xg_by_period[period_idx] if period_idx < len(away_xg_by_period) else 0
                                    
                                    period_stats_array.append({
                                        'period': str(period_num),
                                        'away_stats': {
                                            'goals': away_period_goals[period_idx] if period_idx < len(away_period_goals) else 0,
                                            'ga': away_ga,
                                            'shots': away_period_stats.get('shots', [0, 0, 0])[period_idx] if period_idx < len(away_period_stats.get('shots', [])) else 0,
                                            'corsi': away_period_stats.get('corsi_pct', [50, 50, 50])[period_idx] if period_idx < len(away_period_stats.get('corsi_pct', [])) else 50,
                                            'xg': away_xg_by_period[period_idx] if period_idx < len(away_xg_by_period) else 0,
                                            'xga': away_xga,
                                            'hits': away_period_stats.get('hits', [0, 0, 0])[period_idx] if period_idx < len(away_period_stats.get('hits', [])) else 0,
                                            'faceoff_pct': away_period_stats.get('fo_pct', [None, None, None])[period_idx] if period_idx < len(away_period_stats.get('fo_pct', [])) else None,
                                            'pim': away_period_stats.get('pim', [0, 0, 0])[period_idx] if period_idx < len(away_period_stats.get('pim', [])) else 0,
                                            'blocked_shots': away_period_stats.get('bs', [0, 0, 0])[period_idx] if period_idx < len(away_period_stats.get('bs', [])) else 0,
                                            'giveaways': away_period_stats.get('gv', [0, 0, 0])[period_idx] if period_idx < len(away_period_stats.get('gv', [])) else 0,
                                            'takeaways': away_period_stats.get('tk', [0, 0, 0])[period_idx] if period_idx < len(away_period_stats.get('tk', [])) else 0,
                                            'nzt': away_nzt_period,
                                            'nztsa': away_nztsa_period,
                                            'ozs': away_ozs_period,
                                            'dzs': away_dzs_period,
                                            'nzs': away_nzs_period,
                                            'rush': away_rush_period,
                                            'fc': away_fc_period
                                        },
                                        'home_stats': {
                                            'goals': home_period_goals[period_idx] if period_idx < len(home_period_goals) else 0,
                                            'ga': home_ga,
                                            'shots': home_period_stats.get('shots', [0, 0, 0])[period_idx] if period_idx < len(home_period_stats.get('shots', [])) else 0,
                                            'corsi': home_period_stats.get('corsi_pct', [50, 50, 50])[period_idx] if period_idx < len(home_period_stats.get('corsi_pct', [])) else 50,
                                            'xg': home_xg_by_period[period_idx] if period_idx < len(home_xg_by_period) else 0,
                                            'xga': home_xga,
                                            'hits': home_period_stats.get('hits', [0, 0, 0])[period_idx] if period_idx < len(home_period_stats.get('hits', [])) else 0,
                                            'faceoff_pct': home_period_stats.get('fo_pct', [None, None, None])[period_idx] if period_idx < len(home_period_stats.get('fo_pct', [])) else None,
                                            'pim': home_period_stats.get('pim', [0, 0, 0])[period_idx] if period_idx < len(home_period_stats.get('pim', [])) else 0,
                                            'blocked_shots': home_period_stats.get('bs', [0, 0, 0])[period_idx] if period_idx < len(home_period_stats.get('bs', [])) else 0,
                                            'giveaways': home_period_stats.get('gv', [0, 0, 0])[period_idx] if period_idx < len(home_period_stats.get('gv', [])) else 0,
                                            'takeaways': home_period_stats.get('tk', [0, 0, 0])[period_idx] if period_idx < len(home_period_stats.get('tk', [])) else 0,
                                            'nzt': home_nzt_period,
                                            'nztsa': home_nztsa_period,
                                            'ozs': home_ozs_period,
                                            'dzs': home_dzs_period,
                                            'nzs': home_nzs_period,
                                            'rush': home_rush_period,
                                            'fc': home_fc_period
                                        }
                                    })
                                
                                prediction['period_stats'] = period_stats_array
                                if 'live_metrics' not in prediction:
                                    prediction['live_metrics'] = {}
                                prediction['live_metrics']['period_stats'] = period_stats_array
                                # CRITICAL: Also update current_period for FINAL games
                                if game_state_fallback in ['FINAL', 'OFF']:
                                    prediction['current_period'] = 3
                                    prediction['live_metrics']['current_period'] = 3
                                print(f"✅ Fallback period_stats formatted: {len(period_stats_array)} periods (game_state={game_state_fallback}, current_period={current_period})")
                except Exception as e:
                    print(f"⚠️ Fallback calculation failed: {e}")
                    import traceback
                    traceback.print_exc()
                
                # Still set empty array so frontend knows to show "No period stats available"
                if 'period_stats' not in prediction:
                    prediction['period_stats'] = []
        else:
            print(f"⚠️ No live_data found in prediction. Prediction keys: {list(prediction.keys()) if isinstance(prediction, dict) else 'Not a dict'}")
            prediction['period_stats'] = []
        
        # FORCE: Always copy physical stats from original live_metrics (OUTSIDE the if live_data block)
        # This ensures they're ALWAYS set, even if live_data is empty
        # BUT: Only copy if the value doesn't already exist or is 0 (don't overwrite summed values from period_stats)
        if 'live_metrics' not in prediction:
            prediction['live_metrics'] = {}
        physical_stats_force = ['away_hits', 'home_hits', 'away_pim', 'home_pim', 'away_blocked_shots', 'home_blocked_shots', 
                                'away_giveaways', 'home_giveaways', 'away_takeaways', 'home_takeaways', 'away_shots', 'home_shots']
        for stat in physical_stats_force:
            current_val = prediction['live_metrics'].get(stat, 0)
            # Only copy if current value is 0 or doesn't exist (don't overwrite summed values)
            if current_val == 0 or current_val is None:
                if stat in live_metrics and live_metrics[stat] > 0:
                    prediction['live_metrics'][stat] = live_metrics[stat]
                    print(f"✅ FORCED {stat}={live_metrics[stat]} from original live_metrics", flush=True)
                elif stat in prediction and prediction[stat] > 0:
                    prediction['live_metrics'][stat] = prediction[stat]
                    print(f"✅ FORCED {stat}={prediction[stat]} from prediction", flush=True)
        
        # Always ensure period_stats key exists - CRITICAL for frontend
        if 'period_stats' not in prediction or prediction.get('period_stats') is None:
            prediction['period_stats'] = []
        elif not isinstance(prediction.get('period_stats'), list):
            prediction['period_stats'] = []
        
        # Ensure live_metrics.period_stats also exists for frontend
        if 'live_metrics' not in prediction:
            prediction['live_metrics'] = {}
        if 'period_stats' not in prediction['live_metrics']:
            prediction['live_metrics']['period_stats'] = prediction.get('period_stats', [])
        
        print(f"✅ Returning period_stats: length={len(prediction.get('period_stats', []))}")
        print(f"✅ live_metrics.period_stats: length={len(prediction.get('live_metrics', {}).get('period_stats', []))}")
        
        # CRITICAL: Ensure play_by_play_with_likelihood is copied from live_metrics to prediction
        # This is needed for extracting the latest likelihood in the API response
        if 'live_metrics' not in prediction:
            prediction['live_metrics'] = {}
        if 'play_by_play_with_likelihood' in live_metrics and 'play_by_play_with_likelihood' not in prediction['live_metrics']:
            prediction['live_metrics']['play_by_play_with_likelihood'] = live_metrics.get('play_by_play_with_likelihood')
            print(f"✅ Copied play_by_play_with_likelihood to prediction (length: {len(live_metrics.get('play_by_play_with_likelihood', []))})", flush=True)
        
        # ABSOLUTE FINAL: Extract physical stats RIGHT BEFORE creating final_response
        # This ensures they're set and nothing can overwrite them
        from nhl_api_client import NHLAPIClient
        api_absolute_final = NHLAPIClient()
        boxscore_absolute_final = api_absolute_final.get_game_boxscore(game_id)
        if boxscore_absolute_final and 'playerByGameStats' in boxscore_absolute_final:
            pbg_absolute_final = boxscore_absolute_final['playerByGameStats']
            if 'awayTeam' in pbg_absolute_final and 'homeTeam' in pbg_absolute_final:
                away_pl_absolute_final = (pbg_absolute_final['awayTeam'].get('forwards', []) or []) + (pbg_absolute_final['awayTeam'].get('defense', []) or [])
                home_pl_absolute_final = (pbg_absolute_final['homeTeam'].get('forwards', []) or []) + (pbg_absolute_final['homeTeam'].get('defense', []) or [])
                if 'live_metrics' not in prediction:
                    prediction['live_metrics'] = {}
                # FORCE SET - this is the absolute last chance before deepcopy
                prediction['live_metrics']['away_hits'] = sum(p.get('hits', 0) for p in away_pl_absolute_final)
                prediction['live_metrics']['home_hits'] = sum(p.get('hits', 0) for p in home_pl_absolute_final)
                prediction['live_metrics']['away_pim'] = sum(p.get('pim', 0) for p in away_pl_absolute_final)
                prediction['live_metrics']['home_pim'] = sum(p.get('pim', 0) for p in home_pl_absolute_final)
                prediction['live_metrics']['away_blocked_shots'] = sum(p.get('blockedShots', 0) for p in away_pl_absolute_final)
                prediction['live_metrics']['home_blocked_shots'] = sum(p.get('blockedShots', 0) for p in home_pl_absolute_final)
                prediction['live_metrics']['away_giveaways'] = sum(p.get('giveaways', 0) for p in away_pl_absolute_final)
                prediction['live_metrics']['home_giveaways'] = sum(p.get('giveaways', 0) for p in home_pl_absolute_final)
                prediction['live_metrics']['away_takeaways'] = sum(p.get('takeaways', 0) for p in away_pl_absolute_final)
                prediction['live_metrics']['home_takeaways'] = sum(p.get('takeaways', 0) for p in home_pl_absolute_final)
                if boxscore_absolute_final.get('awayTeam', {}).get('sog'):
                    prediction['live_metrics']['away_shots'] = int(boxscore_absolute_final['awayTeam']['sog'])
                if boxscore_absolute_final.get('homeTeam', {}).get('sog'):
                    prediction['live_metrics']['home_shots'] = int(boxscore_absolute_final['homeTeam']['sog'])
                print(f"✅✅✅ ABSOLUTE FINAL BEFORE DEEPCOPY: away_hits={prediction['live_metrics']['away_hits']}, blocked={prediction['live_metrics']['away_blocked_shots']}, gv={prediction['live_metrics']['away_giveaways']}", flush=True)
        
        # CRITICAL DEBUG: This print MUST appear in logs if code is executing
        print(f"🔍🔍🔍 REACHED LINE 2265: About to create final_response via deepcopy", flush=True)
        
        # FINAL CHECK: Ensure period_stats is in the response
        # Use deep copy to avoid reference issues
        import copy
        final_response = copy.deepcopy(prediction)
        
        # CRITICAL DEBUG: This print MUST appear after deepcopy
        print(f"🔍🔍🔍 REACHED LINE 2269: After deepcopy, about to check game_state", flush=True)
        
        # FINAL CHECK: Calculate PP%, PK%, and FO% from period stats for FINAL games (if not already calculated)
        # The boxscore doesn't have these percentages, so we need to calculate from period stats
        # CRITICAL: Do this AFTER deep copy so we modify final_response directly
        game_state_before_copy = final_response.get('game_state') or final_response.get('live_metrics', {}).get('game_state', '')
        print(f"🔍 API_SERVER FINAL CHECK: game_state_before_copy='{game_state_before_copy}', is FINAL/OFF: {game_state_before_copy in ['FINAL', 'OFF']}", flush=True)
        if game_state_before_copy in ['FINAL', 'OFF']:
            try:
                # Get period stats from live_metrics - try multiple paths
                live_metrics_for_final = final_response.get('live_metrics', {})
                away_period_stats_final = live_metrics_for_final.get('away_period_stats', {})
                home_period_stats_final = live_metrics_for_final.get('home_period_stats', {})
                
                # Fallback: check top level
                if not away_period_stats_final:
                    away_period_stats_final = final_response.get('away_period_stats', {})
                if not home_period_stats_final:
                    home_period_stats_final = final_response.get('home_period_stats', {})
                
                print(f"🔍 API_SERVER FINAL: Calculating percentages from period stats", flush=True)
                print(f"🔍 API_SERVER FINAL: away_period_stats exists: {bool(away_period_stats_final)}, type: {type(away_period_stats_final)}", flush=True)
                print(f"🔍 API_SERVER FINAL: away_period_stats keys: {list(away_period_stats_final.keys()) if isinstance(away_period_stats_final, dict) else 'Not a dict'}", flush=True)
                
                # Calculate Power Play Percentage from period stats
                if away_period_stats_final and isinstance(away_period_stats_final, dict):
                    away_pp_goals_total = sum(away_period_stats_final.get('pp_goals', [0]))
                    away_pp_attempts_total = sum(away_period_stats_final.get('pp_attempts', [0]))
                    print(f"🔍 API_SERVER FINAL: away_pp_goals_total={away_pp_goals_total}, away_pp_attempts_total={away_pp_attempts_total}", flush=True)
                    if away_pp_attempts_total > 0:
                        final_response['live_metrics']['away_power_play_pct'] = (away_pp_goals_total / away_pp_attempts_total) * 100
                        print(f"✅✅✅ API_SERVER FINAL: Calculated away_power_play_pct from period stats: {final_response['live_metrics']['away_power_play_pct']:.1f}% (goals={away_pp_goals_total}, attempts={away_pp_attempts_total})", flush=True)
                    elif final_response.get('live_metrics', {}).get('away_power_play_pct') is None:
                        print(f"⚠️ API_SERVER FINAL: away_pp_attempts_total=0, cannot calculate PP%", flush=True)
                
                if home_period_stats_final and isinstance(home_period_stats_final, dict):
                    home_pp_goals_total = sum(home_period_stats_final.get('pp_goals', [0]))
                    home_pp_attempts_total = sum(home_period_stats_final.get('pp_attempts', [0]))
                    print(f"🔍 API_SERVER FINAL: home_pp_goals_total={home_pp_goals_total}, home_pp_attempts_total={home_pp_attempts_total}", flush=True)
                    if home_pp_attempts_total > 0:
                        final_response['live_metrics']['home_power_play_pct'] = (home_pp_goals_total / home_pp_attempts_total) * 100
                        print(f"✅✅✅ API_SERVER FINAL: Calculated home_power_play_pct from period stats: {final_response['live_metrics']['home_power_play_pct']:.1f}% (goals={home_pp_goals_total}, attempts={home_pp_attempts_total})", flush=True)
                    elif final_response.get('live_metrics', {}).get('home_power_play_pct') is None:
                        print(f"⚠️ API_SERVER FINAL: home_pp_attempts_total=0, cannot calculate PP%", flush=True)
                
                # Calculate Faceoff Percentage from period stats
                # Period stats have 'fo_pct' (faceoff percentage per period), not wins/total
                if away_period_stats_final and isinstance(away_period_stats_final, dict):
                    # Try to get faceoff_wins and faceoff_total first (if they exist)
                    away_fo_wins_total = sum(away_period_stats_final.get('faceoff_wins', [0]))
                    away_fo_total = sum(away_period_stats_final.get('faceoff_total', [0]))
                    
                    if away_fo_total > 0:
                        # Calculate from wins/total
                        final_response['live_metrics']['away_faceoff_pct'] = (away_fo_wins_total / away_fo_total) * 100
                        print(f"✅✅✅ API_SERVER FINAL: Calculated away_faceoff_pct from wins/total: {final_response['live_metrics']['away_faceoff_pct']:.1f}% (wins={away_fo_wins_total}, total={away_fo_total})", flush=True)
                    else:
                        # Fallback: Average the fo_pct percentages from each period
                        away_fo_pct_list = away_period_stats_final.get('fo_pct', [])
                        print(f"🔍 API_SERVER FINAL: away_fo_pct_list={away_fo_pct_list}", flush=True)
                        if away_fo_pct_list and len(away_fo_pct_list) > 0:
                            # Filter out None values and 50.0 defaults (likely means no faceoffs)
                            valid_pcts = [p for p in away_fo_pct_list if p is not None and p != 50.0]
                            if valid_pcts:
                                final_response['live_metrics']['away_faceoff_pct'] = sum(valid_pcts) / len(valid_pcts)
                                print(f"✅✅✅ API_SERVER FINAL: Calculated away_faceoff_pct from fo_pct average: {final_response['live_metrics']['away_faceoff_pct']:.1f}% (from {len(valid_pcts)} periods)", flush=True)
                            elif final_response.get('live_metrics', {}).get('away_faceoff_pct') is None:
                                print(f"⚠️ API_SERVER FINAL: No valid fo_pct data, cannot calculate away_faceoff_pct", flush=True)
                        elif final_response.get('live_metrics', {}).get('away_faceoff_pct') is None:
                            print(f"⚠️ API_SERVER FINAL: No faceoff data in period stats, cannot calculate away_faceoff_pct", flush=True)
                
                if home_period_stats_final and isinstance(home_period_stats_final, dict):
                    home_fo_wins_total = sum(home_period_stats_final.get('faceoff_wins', [0]))
                    home_fo_total = sum(home_period_stats_final.get('faceoff_total', [0]))
                    
                    if home_fo_total > 0:
                        # Calculate from wins/total
                        final_response['live_metrics']['home_faceoff_pct'] = (home_fo_wins_total / home_fo_total) * 100
                        print(f"✅✅✅ API_SERVER FINAL: Calculated home_faceoff_pct from wins/total: {final_response['live_metrics']['home_faceoff_pct']:.1f}% (wins={home_fo_wins_total}, total={home_fo_total})", flush=True)
                    else:
                        # Fallback: Average the fo_pct percentages from each period
                        home_fo_pct_list = home_period_stats_final.get('fo_pct', [])
                        print(f"🔍 API_SERVER FINAL: home_fo_pct_list={home_fo_pct_list}", flush=True)
                        if home_fo_pct_list and len(home_fo_pct_list) > 0:
                            # Filter out None values and 50.0 defaults (likely means no faceoffs)
                            valid_pcts = [p for p in home_fo_pct_list if p is not None and p != 50.0]
                            if valid_pcts:
                                final_response['live_metrics']['home_faceoff_pct'] = sum(valid_pcts) / len(valid_pcts)
                                print(f"✅✅✅ API_SERVER FINAL: Calculated home_faceoff_pct from fo_pct average: {final_response['live_metrics']['home_faceoff_pct']:.1f}% (from {len(valid_pcts)} periods)", flush=True)
                            elif final_response.get('live_metrics', {}).get('home_faceoff_pct') is None:
                                print(f"⚠️ API_SERVER FINAL: No valid fo_pct data, cannot calculate home_faceoff_pct", flush=True)
                        elif final_response.get('live_metrics', {}).get('home_faceoff_pct') is None:
                            print(f"⚠️ API_SERVER FINAL: No faceoff data in period stats, cannot calculate home_faceoff_pct", flush=True)
            except Exception as e:
                print(f"⚠️ API_SERVER FINAL: Error calculating percentages from period stats: {e}", flush=True)
                import traceback
                traceback.print_exc()
        
        # FINAL CHECK: Ensure period_stats is in the response
        # (final_response was already created above via deep copy)
        
        # CRITICAL: Ensure period_stats exists at top level
        if 'period_stats' not in final_response:
            final_response['period_stats'] = []
        elif not isinstance(final_response.get('period_stats'), list):
            print(f"⚠️ WARNING: period_stats is not a list, converting")
            final_response['period_stats'] = []
        
        # CRITICAL: Don't overwrite live_metrics if it exists - it has the extracted values!
        if 'live_metrics' not in final_response:
            final_response['live_metrics'] = {}
        elif not isinstance(final_response.get('live_metrics'), dict):
            # Only recreate if it's not a dict
            final_response['live_metrics'] = {}
        
        # CRITICAL: Ensure period_stats is also in live_metrics
        if 'period_stats' not in final_response['live_metrics']:
            # Use period_stats from top level if available, otherwise empty array
            final_response['live_metrics']['period_stats'] = final_response.get('period_stats', [])
        
        # CRITICAL: Ensure period_stats is always an array and sync between top level and live_metrics
        if not isinstance(final_response['live_metrics'].get('period_stats'), list):
            final_response['live_metrics']['period_stats'] = []
        # Sync: if live_metrics has period_stats, ensure top level also has it
        if final_response['live_metrics'].get('period_stats'):
            final_response['period_stats'] = final_response['live_metrics']['period_stats']
        
        # Physical stats will be extracted in the single final block before return
        
        # FINAL SAFEGUARD: Force percentages to None if totals are 0 (prevent 50% defaults)
        # BUT: For FINAL/OFF games, preserve percentages extracted from boxscore (they're accurate even if opportunities=0)
        game_state_final_check = final_response.get('game_state') or final_response.get('live_metrics', {}).get('game_state', '')
        is_final_game = game_state_final_check in ['FINAL', 'OFF']
        
        # Debug: Check what percentages we have before overwriting
        print(f"🔍 BEFORE FINAL SAFEGUARD: away_power_play_pct={final_response.get('live_metrics', {}).get('away_power_play_pct')}, home_power_play_pct={final_response.get('live_metrics', {}).get('home_power_play_pct')}", flush=True)
        print(f"🔍 BEFORE FINAL SAFEGUARD: away_faceoff_pct={final_response.get('live_metrics', {}).get('away_faceoff_pct')}, home_faceoff_pct={final_response.get('live_metrics', {}).get('home_faceoff_pct')}", flush=True)
        print(f"🔍 BEFORE FINAL SAFEGUARD: is_final_game={is_final_game}, game_state={game_state_final_check}", flush=True)
        
        # Only force to None if game is not FINAL and totals are 0
        # For FINAL games, percentages from boxscore are accurate even if opportunities=0
        if not is_final_game:
            if final_response.get('live_metrics', {}).get('away_faceoff_total', 0) == 0:
                final_response['live_metrics']['away_faceoff_pct'] = None
            if final_response.get('live_metrics', {}).get('home_faceoff_total', 0) == 0:
                final_response['live_metrics']['home_faceoff_pct'] = None
            if final_response.get('live_metrics', {}).get('away_power_play_opportunities', 0) == 0:
                final_response['live_metrics']['away_power_play_pct'] = None
            if final_response.get('live_metrics', {}).get('home_power_play_opportunities', 0) == 0:
                final_response['live_metrics']['home_power_play_pct'] = None
        else:
            # For FINAL games, only set to None if percentage is actually None/0 and wasn't extracted from boxscore
            # If it was extracted from boxscore, it will be a valid number (even if 0.0)
            # CRITICAL: Don't overwrite if we already have a value (it was extracted from boxscore)
            print(f"✅ FINAL game detected, preserving boxscore-extracted percentages", flush=True)
            # Only set to None if the value is actually missing (not extracted)
            if final_response.get('live_metrics', {}).get('away_power_play_pct') is None:
                print(f"⚠️ FINAL: away_power_play_pct is None, but game is FINAL - this shouldn't happen if extraction worked", flush=True)
            if final_response.get('live_metrics', {}).get('home_power_play_pct') is None:
                print(f"⚠️ FINAL: home_power_play_pct is None, but game is FINAL - this shouldn't happen if extraction worked", flush=True)
            if final_response.get('live_metrics', {}).get('away_faceoff_pct') is None:
                print(f"⚠️ FINAL: away_faceoff_pct is None, but game is FINAL - this shouldn't happen if extraction worked", flush=True)
            if final_response.get('live_metrics', {}).get('home_faceoff_pct') is None:
                print(f"⚠️ FINAL: home_faceoff_pct is None, but game is FINAL - this shouldn't happen if extraction worked", flush=True)
        
        # Debug: Check what percentages we have after the safeguard
        print(f"🔍 AFTER FINAL SAFEGUARD: away_power_play_pct={final_response.get('live_metrics', {}).get('away_power_play_pct')}, home_power_play_pct={final_response.get('live_metrics', {}).get('home_power_play_pct')}", flush=True)
        print(f"🔍 AFTER FINAL SAFEGUARD: away_faceoff_pct={final_response.get('live_metrics', {}).get('away_faceoff_pct')}, home_faceoff_pct={final_response.get('live_metrics', {}).get('home_faceoff_pct')}", flush=True)
        
        # Also check if percentages are 50.0 (likely a default) and totals are 0, force to None
        # BUT: For FINAL games, don't overwrite boxscore-extracted percentages
        if not is_final_game:
            if final_response.get('live_metrics', {}).get('away_faceoff_pct') == 50.0 and final_response.get('live_metrics', {}).get('away_faceoff_total', 0) == 0:
                final_response['live_metrics']['away_faceoff_pct'] = None
                print(f"⚠️ FINAL: FORCED away_faceoff_pct from 50.0 to None (total=0)", flush=True)
            if final_response.get('live_metrics', {}).get('home_faceoff_pct') == 50.0 and final_response.get('live_metrics', {}).get('home_faceoff_total', 0) == 0:
                final_response['live_metrics']['home_faceoff_pct'] = None
                print(f"⚠️ FINAL: FORCED home_faceoff_pct from 50.0 to None (total=0)", flush=True)
            if final_response.get('live_metrics', {}).get('away_power_play_pct') == 50.0 and final_response.get('live_metrics', {}).get('away_power_play_opportunities', 0) == 0:
                final_response['live_metrics']['away_power_play_pct'] = None
                print(f"⚠️ FINAL: FORCED away_power_play_pct from 50.0 to None (opportunities=0)", flush=True)
            if final_response.get('live_metrics', {}).get('home_power_play_pct') == 50.0 and final_response.get('live_metrics', {}).get('home_power_play_opportunities', 0) == 0:
                final_response['live_metrics']['home_power_play_pct'] = None
                print(f"⚠️ FINAL: FORCED home_power_play_pct from 50.0 to None (opportunities=0)", flush=True)
        
        # Ensure game_state is in the response (for frontend and our calculation)
        # Check prediction first (where predict_live_game puts it), then live_metrics
        if 'game_state' not in final_response:
            if 'game_state' in prediction:
                final_response['game_state'] = prediction.get('game_state')
                print(f"✅ Set game_state from prediction: {final_response['game_state']}")
            elif live_metrics and 'game_state' in live_metrics:
                final_response['game_state'] = live_metrics.get('game_state')
                print(f"✅ Set game_state from live_metrics: {final_response['game_state']}")
            elif live_metrics and isinstance(live_metrics.get('boxscore'), dict):
                final_response['game_state'] = live_metrics.get('boxscore', {}).get('gameState', '')
                print(f"✅ Set game_state from live_metrics.boxscore: {final_response['game_state']}")
        
        # Also ensure time_remaining is correct for FINAL games
        if final_response.get('game_state') in ['OFF', 'FINAL']:
            final_response['time_remaining'] = '00:00'
            if 'live_metrics' in final_response:
                final_response['live_metrics']['time_remaining'] = '00:00'
            print(f"✅ Set time_remaining to '00:00' for FINAL game")
        
        print(f"✅ FINAL CHECK - period_stats in response: {'period_stats' in final_response}, length: {len(final_response.get('period_stats', []))}")
        print(f"✅ FINAL CHECK - live_metrics.period_stats in response: {'period_stats' in final_response.get('live_metrics', {})}, length: {len(final_response.get('live_metrics', {}).get('period_stats', []))}")
        print(f"✅ FINAL CHECK - game_state in response: {'game_state' in final_response}, value: {final_response.get('game_state')}")
        
        # For completed games, calculate win probability based on actual game metrics
        # This uses the same formula/model from the auto post reports
        try:
            print(f"🔍 Checking for postgame win probability calculation for game {game_id}...", flush=True)
            
            # Check game state from multiple sources
            game_state = None
            game_data = None
            
            # Try to get game state from multiple sources
            # First check final_response (top level)
            if 'game_state' in final_response:
                game_state = final_response.get('game_state')
                print(f"🔍 Game state from final_response: {game_state}", flush=True)
            
            # Also check live_metrics (top level)
            if not game_state and live_metrics and 'game_state' in live_metrics:
                game_state = live_metrics.get('game_state')
                print(f"🔍 Game state from live_metrics: {game_state}", flush=True)
            
            # Also check live_metrics.boxscore.gameState (nested)
            if not game_state and live_metrics and isinstance(live_metrics.get('boxscore'), dict):
                game_state = live_metrics.get('boxscore', {}).get('gameState', '')
                if game_state:
                    print(f"🔍 Game state from live_metrics.boxscore.gameState: {game_state}", flush=True)
            
            # Check if we have period_stats with 3 periods (indicates game is complete)
            period_stats_count = len(final_response.get('period_stats', []))
            print(f"🔍 Period stats count: {period_stats_count}", flush=True)
            print(f"🔍 final_response keys: {list(final_response.keys())[:30]}", flush=True)
            
            # Calculate win probability for completed games ONLY
            # Don't calculate for live games - that's handled separately below
            has_3_periods = period_stats_count >= 3
            is_off_or_final = game_state in ['OFF', 'FINAL'] if game_state else False
            # Only calculate postgame if game is actually finished (not live)
            should_calculate = is_off_or_final and has_3_periods
            
            print(f"🔍 Should calculate win probability: {should_calculate}", flush=True)
            print(f"   - game_state: '{game_state}' (in ['OFF', 'FINAL']: {is_off_or_final})", flush=True)
            print(f"   - period_stats_count: {period_stats_count} (>= 3: {has_3_periods})", flush=True)
            
            # Only force calculation if game is actually finished (not live)
            # Don't force for live games - they'll use the live calculation below
            if has_3_periods and is_off_or_final and not should_calculate:
                print(f"⚠️ WARNING: Has 3 periods and is FINAL but should_calculate is False, forcing calculation", flush=True)
                should_calculate = True
            
            if should_calculate:
                # Fetch comprehensive game data for calculation
                print(f"🔍 Fetching comprehensive game data for win probability calculation...", flush=True)
                game_data = live_predictor.api.get_comprehensive_game_data(game_id)
                if game_data:
                    boxscore = game_data.get('game_center', {}).get('boxscore', {}) or game_data.get('boxscore', {})
                    if not game_state:
                        game_state = boxscore.get('gameState', '')
                    print(f"🔍 Game state from boxscore: {game_state}", flush=True)
                
                if game_data:
                    print(f"🔍 Game appears completed, calculating win probability using report generator...", flush=True)
                    try:
                        # Normalize game_data structure
                        normalized_game_data = game_data.copy()
                        
                        if 'boxscore' not in normalized_game_data:
                            if 'game_center' in normalized_game_data and 'boxscore' in normalized_game_data['game_center']:
                                normalized_game_data['boxscore'] = normalized_game_data['game_center']['boxscore']
                                print(f"🔍 Moved boxscore to top level from game_center", flush=True)
                        
                        if 'play_by_play' not in normalized_game_data:
                            if 'game_center' in normalized_game_data and 'play_by_play' in normalized_game_data['game_center']:
                                normalized_game_data['play_by_play'] = normalized_game_data['game_center']['play_by_play']
                        
                        print(f"🔍 Game data structure - Has boxscore: {'boxscore' in normalized_game_data}, Has play_by_play: {'play_by_play' in normalized_game_data}", flush=True)
                        
                        # Call the actual calculate_win_probability from report generator
                        win_prob = live_predictor.report_generator.calculate_win_probability(normalized_game_data)
                        print(f"🔍 calculate_win_probability returned: {win_prob} (type: {type(win_prob)})", flush=True)
                        
                        if win_prob and isinstance(win_prob, dict):
                            away_prob = win_prob.get('away_probability')
                            home_prob = win_prob.get('home_probability')
                            
                            print(f"🔍 away_probability: {away_prob}, home_probability: {home_prob}", flush=True)
                            
                            if away_prob is not None and home_prob is not None:
                                final_response['postgame_win_probability'] = {
                                    'away_probability': float(away_prob),
                                    'home_probability': float(home_prob)
                                }
                                print(f"✅ SUCCESS: Calculated postgame win probability - Away {away_prob:.1f}% / Home {home_prob:.1f}%", flush=True)
                            else:
                                print(f"⚠️ Win prob dict exists but missing probability values", flush=True)
                        else:
                            print(f"⚠️ calculate_win_probability returned: {win_prob} (type: {type(win_prob)})", flush=True)
                    except Exception as calc_error:
                        print(f"❌ ERROR in calculate_win_probability: {calc_error}", flush=True)
                        import traceback
                        traceback.print_exc()
                else:
                    print(f"⚠️ Could not get game_data for win prob calculation (required for calculate_win_probability)", flush=True)
            else:
                print(f"🔍 Game is not completed (state: {game_state}, periods: {period_stats_count}), skipping win prob calculation", flush=True)
        except Exception as e:
            print(f"⚠️ Could not calculate postgame win probability: {e}", flush=True)
            import traceback
            traceback.print_exc()
            # Don't fail the request if this calculation fails
        
        # Calculate live win probability for LIVE games
        # FIRST: Try to extract from play_by_play_with_likelihood (most accurate, calculated per play)
        # SECOND: Fall back to calculate_win_probability() method
        print(f"🔍🔍🔍 ENTERING live win probability calculation block for game {game_id}", flush=True)
        try:
            # Get game_state from multiple sources to ensure we catch live games
            game_state_for_live = final_response.get('game_state')
            print(f"🔍 Initial game_state_for_live from final_response: {game_state_for_live}", flush=True)
            if not game_state_for_live and 'live_metrics' in final_response:
                game_state_for_live = final_response['live_metrics'].get('game_state')
                print(f"🔍 Got game_state_for_live from live_metrics: {game_state_for_live}", flush=True)
            if not game_state_for_live and prediction and 'live_metrics' in prediction:
                game_state_for_live = prediction['live_metrics'].get('game_state')
                print(f"🔍 Got game_state_for_live from prediction live_metrics: {game_state_for_live}", flush=True)
            
            # Also check if we have current_period (indicates live game)
            has_current_period = final_response.get('live_metrics', {}).get('current_period') is not None
            is_not_final = game_state_for_live not in ['OFF', 'FINAL'] if game_state_for_live else True
            
            is_live = (game_state_for_live in ['LIVE', 'CRIT']) or (has_current_period and is_not_final)
            print(f"🔍 Live win prob check - game_state: {game_state_for_live}, has_current_period: {has_current_period}, is_not_final: {is_not_final}, is_live: {is_live}", flush=True)
            
            if is_live:
                # FIRST: Try to extract latest likelihood from play_by_play_with_likelihood
                play_by_play_likelihood = final_response.get('live_metrics', {}).get('play_by_play_with_likelihood')
                if not play_by_play_likelihood and prediction and 'live_metrics' in prediction:
                    play_by_play_likelihood = prediction.get('live_metrics', {}).get('play_by_play_with_likelihood')
                
                if play_by_play_likelihood and isinstance(play_by_play_likelihood, list) and len(play_by_play_likelihood) > 0:
                    # Get the last play (most recent) which has the current likelihood
                    last_play = play_by_play_likelihood[-1]
                    if last_play and 'likelihood' in last_play:
                        latest_likelihood = last_play['likelihood']
                        away_prob = latest_likelihood.get('away_probability')
                        home_prob = latest_likelihood.get('home_probability')
                        
                        if away_prob is not None and home_prob is not None:
                            final_response['live_win_probability'] = {
                                'away_probability': float(away_prob),
                                'home_probability': float(home_prob)
                            }
                            print(f"✅ SUCCESS: Extracted live win probability from play_by_play_with_likelihood (latest play) - Away {away_prob:.1f}% / Home {home_prob:.1f}%", flush=True)
                        else:
                            print(f"⚠️ Latest play has likelihood but missing probability values", flush=True)
                    else:
                        print(f"⚠️ Latest play in play_by_play_with_likelihood doesn't have likelihood", flush=True)
                else:
                    print(f"⚠️ No play_by_play_with_likelihood available, falling back to calculate_win_probability", flush=True)
                    
                    # FALLBACK: Use calculate_win_probability method
                    print(f"🔍 Calculating live win probability for game {game_id} using report generator method...", flush=True)
                    
                    # Fetch comprehensive game data to use the exact same calculation method
                    game_data_for_calc = live_predictor.api.get_comprehensive_game_data(game_id)
                    if game_data_for_calc:
                        # Normalize game_data structure (same as postgame calculation)
                        normalized_game_data = game_data_for_calc.copy()
                        
                        if 'boxscore' not in normalized_game_data:
                            if 'game_center' in normalized_game_data and 'boxscore' in normalized_game_data['game_center']:
                                normalized_game_data['boxscore'] = normalized_game_data['game_center']['boxscore']
                                print(f"🔍 Moved boxscore to top level from game_center for live calc", flush=True)
                        
                        if 'play_by_play' not in normalized_game_data:
                            if 'game_center' in normalized_game_data and 'play_by_play' in normalized_game_data['game_center']:
                                normalized_game_data['play_by_play'] = normalized_game_data['game_center']['play_by_play']
                        
                        print(f"🔍 Game data structure for live calc - Has boxscore: {'boxscore' in normalized_game_data}, Has play_by_play: {'play_by_play' in normalized_game_data}", flush=True)
                        
                        # Call the EXACT SAME calculate_win_probability method from report generator
                        # This uses the same methods: _calculate_game_scores(), _calculate_xg_from_plays(), etc.
                        win_prob = live_predictor.report_generator.calculate_win_probability(normalized_game_data)
                        print(f"🔍 calculate_win_probability (live) returned: {win_prob} (type: {type(win_prob)})", flush=True)
                        
                        if win_prob and isinstance(win_prob, dict):
                            away_prob = win_prob.get('away_probability')
                            home_prob = win_prob.get('home_probability')
                            
                            print(f"🔍 live away_probability: {away_prob}, home_probability: {home_prob}", flush=True)
                            
                            if away_prob is not None and home_prob is not None:
                                final_response['live_win_probability'] = {
                                    'away_probability': float(away_prob),
                                    'home_probability': float(home_prob)
                                }
                                print(f"✅ SUCCESS: Calculated live win probability using report generator - Away {away_prob:.1f}% / Home {home_prob:.1f}%", flush=True)
                            else:
                                print(f"⚠️ Win prob dict exists but missing probability values", flush=True)
                        else:
                            print(f"⚠️ calculate_win_probability (live) returned: {win_prob} (type: {type(win_prob)})", flush=True)
                    else:
                        print(f"⚠️ Could not get game_data for live win prob calculation", flush=True)
        except Exception as e:
            print(f"⚠️ Could not calculate live win probability: {e}", flush=True)
            import traceback
            traceback.print_exc()
            # Don't fail the request if this calculation fails
        
        # SINGLE FINAL EXTRACTION: Extract physical stats RIGHT BEFORE return
        # This is the ONLY extraction block - runs unconditionally as the last step
        print(f"🔍🔍🔍 FINAL EXTRACTION: Starting extraction for game {game_id}...", flush=True)
        try:
            from nhl_api_client import NHLAPIClient
            api_return = NHLAPIClient()
            boxscore_return = api_return.get_game_boxscore(game_id)
            print(f"🔍 ABSOLUTE FINAL: boxscore exists={bool(boxscore_return)}, has pbg={'playerByGameStats' in boxscore_return if boxscore_return else False}", flush=True)
            if boxscore_return and 'playerByGameStats' in boxscore_return:
                pbg_return = boxscore_return['playerByGameStats']
                if 'awayTeam' in pbg_return and 'homeTeam' in pbg_return:
                    away_pl_return = (pbg_return['awayTeam'].get('forwards', []) or []) + (pbg_return['awayTeam'].get('defense', []) or [])
                    home_pl_return = (pbg_return['homeTeam'].get('forwards', []) or []) + (pbg_return['homeTeam'].get('defense', []) or [])
                    print(f"🔍 ABSOLUTE FINAL: away_pl={len(away_pl_return)}, home_pl={len(home_pl_return)}", flush=True)
                    if 'live_metrics' not in final_response:
                        final_response['live_metrics'] = {}
                    # FORCE SET - always overwrite with boxscore values
                    final_response['live_metrics']['away_hits'] = sum(p.get('hits', 0) for p in away_pl_return)
                    final_response['live_metrics']['home_hits'] = sum(p.get('hits', 0) for p in home_pl_return)
                    final_response['live_metrics']['away_pim'] = sum(p.get('pim', 0) for p in away_pl_return)
                    final_response['live_metrics']['home_pim'] = sum(p.get('pim', 0) for p in home_pl_return)
                    final_response['live_metrics']['away_blocked_shots'] = sum(p.get('blockedShots', 0) for p in away_pl_return)
                    final_response['live_metrics']['home_blocked_shots'] = sum(p.get('blockedShots', 0) for p in home_pl_return)
                    final_response['live_metrics']['away_giveaways'] = sum(p.get('giveaways', 0) for p in away_pl_return)
                    final_response['live_metrics']['home_giveaways'] = sum(p.get('giveaways', 0) for p in home_pl_return)
                    final_response['live_metrics']['away_takeaways'] = sum(p.get('takeaways', 0) for p in away_pl_return)
                    final_response['live_metrics']['home_takeaways'] = sum(p.get('takeaways', 0) for p in home_pl_return)
                    if boxscore_return.get('awayTeam', {}).get('sog'):
                        final_response['live_metrics']['away_shots'] = int(boxscore_return['awayTeam']['sog'])
                    if boxscore_return.get('homeTeam', {}).get('sog'):
                        final_response['live_metrics']['home_shots'] = int(boxscore_return['homeTeam']['sog'])
                    print(f"✅✅✅ ABSOLUTE FINAL BEFORE RETURN: Set away_hits={final_response['live_metrics']['away_hits']}, blocked={final_response['live_metrics']['away_blocked_shots']}, gv={final_response['live_metrics']['away_giveaways']}", flush=True)
                else:
                    print(f"⚠️ ABSOLUTE FINAL: Missing awayTeam or homeTeam", flush=True)
            else:
                print(f"⚠️ ABSOLUTE FINAL: boxscore or playerByGameStats missing", flush=True)
        except Exception as e:
            print(f"❌ ABSOLUTE FINAL BEFORE RETURN failed: {e}", flush=True)
            import traceback
            traceback.print_exc()
        
        # FINAL FINAL FIX: Convert any integer shooters in final_response shots_data (absolute last chance)
        if 'shots_data' in final_response and final_response['shots_data']:
            shots_data_final = final_response['shots_data']
            print(f"🔍 FINAL_FINAL: Processing {len(shots_data_final)} shots in final_response", flush=True)
            
            # Get boxscore for lookup
            try:
                from nhl_api_client import NHLAPIClient
                api_client_final = NHLAPIClient()
                game_center_final = api_client_final.get_game_center(game_id)
                if game_center_final and 'boxscore' in game_center_final:
                    boxscore_final = game_center_final['boxscore']
                    player_by_game_stats_final = boxscore_final.get('playerByGameStats', {}) if boxscore_final else {}
                    
                    for shot in shots_data_final:
                        if 'shooter' in shot and isinstance(shot['shooter'], int):
                            shooter_id_final = shot['shooter']
                            name_found_final = None
                            
                            # Look up in boxscore (same method as top performers)
                            if player_by_game_stats_final:
                                for team_key in ['awayTeam', 'homeTeam']:
                                    team_players = player_by_game_stats_final.get(team_key, {})
                                    for position_group in ['forwards', 'defense', 'goalies']:
                                        players = team_players.get(position_group, [])
                                        for player in players:
                                            p_id = player.get('playerId') or player.get('id') or player.get('playerID')
                                            if p_id == shooter_id_final or str(p_id) == str(shooter_id_final):
                                                # Get name - EXACT SAME METHOD AS TOP PERFORMERS
                                                name = ''
                                                name_field = player.get('name', '')
                                                if isinstance(name_field, dict):
                                                    name = name_field.get('default', '')
                                                elif isinstance(name_field, str):
                                                    name = name_field
                                                
                                                if not name:
                                                    firstName = player.get('firstName', {}).get('default', '') if isinstance(player.get('firstName'), dict) else player.get('firstName', '')
                                                    lastName = player.get('lastName', {}).get('default', '') if isinstance(player.get('lastName'), dict) else player.get('lastName', '')
                                                    name = f"{firstName} {lastName}".strip()
                                                
                                                if name:
                                                    name_found_final = name
                                                    break
                                        if name_found_final:
                                            break
                                    if name_found_final:
                                        break
                            
                            if name_found_final:
                                shot['shooter'] = name_found_final
                                shot['shooterName'] = name_found_final
                                print(f"✅✅✅ FINAL_FINAL: Converted INT {shooter_id_final} to name '{name_found_final}'", flush=True)
                            else:
                                shot['shooter'] = f"Player #{shooter_id_final}"
                                shot['shooterName'] = shot['shooter']
                                print(f"⚠️ FINAL_FINAL: INT {shooter_id_final} not found, using fallback", flush=True)
            except Exception as e:
                print(f"⚠️ FINAL_FINAL fix failed: {e}", flush=True)
        
        print(f"🚀🚀🚀 RETURNING response for game_id={game_id}", flush=True)
        print(f"   Final away_hits: {final_response.get('live_metrics', {}).get('away_hits')}", flush=True)
        print(f"   Final away_blocked_shots: {final_response.get('live_metrics', {}).get('away_blocked_shots')}", flush=True)
        print(f"   live_win_probability in response: {'live_win_probability' in final_response}", flush=True)
        if 'live_win_probability' in final_response:
            print(f"   live_win_probability value: {final_response['live_win_probability']}", flush=True)
        print(f"   postgame_win_probability in response: {'postgame_win_probability' in final_response}", flush=True)
        if 'postgame_win_probability' in final_response:
            print(f"   postgame_win_probability value: {final_response['postgame_win_probability']}", flush=True)
        print(f"   play_by_play_with_likelihood in live_metrics: {'play_by_play_with_likelihood' in final_response.get('live_metrics', {})}", flush=True)
        if 'play_by_play_with_likelihood' in final_response.get('live_metrics', {}):
            pbp_len = len(final_response['live_metrics']['play_by_play_with_likelihood'])
            print(f"   play_by_play_with_likelihood length: {pbp_len}", flush=True)
        return jsonify(final_response)
    except Exception as e:
        print(f"Error in live-game endpoint: {e}")
        import traceback
        traceback.print_exc()
        # Even on error, return period_stats as empty array so frontend doesn't break
        error_response = {"error": str(e), "period_stats": [], "live_metrics": {"period_stats": []}}
        return jsonify(error_response), 500

if __name__ == '__main__':
    import sys
    
    # Set up file logging for easier debugging
    log_file = os.path.join(DATA_DIR, 'api_server.log')
    
    # Create a class that writes to both file and stdout
    class TeeOutput:
        def __init__(self, *files):
            self.files = files
        def write(self, obj):
            for f in self.files:
                f.write(obj)
                f.flush()
        def flush(self):
            for f in self.files:
                f.flush()
    
    # Redirect stdout and stderr to both file and console
    log_f = open(log_file, 'a', encoding='utf-8')
    sys.stdout = TeeOutput(sys.stdout, log_f)
    sys.stderr = TeeOutput(sys.stderr, log_f)
    
    print("🏒 NHL Analytics API Server")
    print("=" * 50)
    print(f"Data directory: {DATA_DIR}")
    print(f"Log file: {log_file}")
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
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting server on http://localhost:{port}")
    print()
    
    app.run(debug=False, host='0.0.0.0', port=port)
