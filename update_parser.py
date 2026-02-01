
import re
import os

NEW_FUNCTION = r'''@app.route('/api/player-stats', methods=['GET'])
def get_player_stats():
    """Get player stats from MoneyPuck - Comprehensive Dynamic Parsing"""
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
                games_played = int(row['games_played']) if row.get('games_played') else 0
                
                # 1. Base Identity Fields
                player = {
                    'name': row.get('name', ''),
                    'team': row.get('team', ''),
                    'position': row.get('position', ''),
                    'season': int(row['season']) if row.get('season') else int(season),
                    'playerId': int(row['playerId']) if row.get('playerId') else None,
                    'games_played': games_played
                }

                # 2. Dynamic Parsing of ALL metrics
                for key, value in row.items():
                    # Skip identity fields and empty values
                    if key in ['name', 'team', 'position', 'season', 'playerId', 'games_played', 'situation']:
                        continue
                    if not value:
                        continue
                        
                    # Parse numeric values
                    try:
                        val_float = float(value)
                        
                        # Store raw value (int if possible, else round float)
                        if val_float.is_integer():
                            player[key] = int(val_float)
                        else:
                            player[key] = round(val_float, 2)
                            
                        # 3. Calculate Per-Game Averages for cumulative stats
                        # Logic: if key looks like a cumulative count, divide by GP
                        cumulative_keys = [
                            'goals', 'assists', 'points', 'shots', 'hits', 'icetime', 
                            'takeaways', 'giveaways', 'blockedShotAttempts', 'penalityMinutes',
                            'faceOffsWon', 'faceoffsWon', 'faceoffsLost', 'shifts',
                            'gameScore'
                        ]
                        
                        is_cumulative = (
                            key.startswith('I_F_') or 
                            key.startswith('OnIce_F_') or 
                            key.startswith('OnIce_A_') or
                            key.startswith('OffIce_') or
                            key in cumulative_keys
                        )
                        
                        # Skip percentages/ratios/ranks/ids for per-game calc
                        skip_pg = ['Percentage', 'Pct', 'rate', 'Rank', 'Id', 'season']
                        if any(s in key for s in skip_pg):
                            is_cumulative = False
                            
                        if is_cumulative and games_played > 0:
                            player[f"{key}_per_game"] = round(val_float / games_played, 2)
                            
                    except ValueError:
                        # Keep string values
                        player[key] = value

                # 4. Aliases for Frontend Compatibility
                # Ensure essential fields exist with expected names
                aliases = {
                    'hits': 'I_F_hits',
                    'blocks': 'I_F_blockedShotAttempts', 
                    'pim': 'I_F_penalityMinutes',
                    'takeaways': 'I_F_takeaways',
                    'giveaways': 'I_F_giveaways',
                    'xgoals': 'I_F_xGoals',
                    'shots': 'I_F_shotsOnGoal',
                    'shot_attempts': 'I_F_shotAttempts',
                    'shots_blocked': 'shotsBlockedByPlayer'
                }
                
                for alias, source in aliases.items():
                    if source in player:
                        player[alias] = player[source]
                        if f"{source}_per_game" in player:
                            player[f"{alias}_per_game"] = player[f"{source}_per_game"]
                            
                # Special calculations
                if 'I_F_faceOffsWon' in player: player['faceoffsWon'] = player['I_F_faceOffsWon']
                
                # Faceoff PCT alias
                fo_won = player.get('faceOffsWon', 0)
                fo_lost = player.get('faceoffsLost', 0)
                if (fo_won + fo_lost) > 0:
                    player['fo_pct'] = round((fo_won / (fo_won + fo_lost)) * 100, 1)
                else:
                    player['fo_pct'] = 0.0

                players_data.append(player)
        
        return jsonify(players_data)
        
    except Exception as e:
        print(f"Error fetching player stats: {e}")
        return jsonify({'error': str(e)}), 500'''

def update_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Regex to capture the existing function
    # Looks for @app.route... def get_player_stats... up to the next @app.route
    pattern = r"@app\.route\('/api/player-stats', methods=\['GET'\]\).*?def get_player_stats\(\):.*?(?=@app\.route|if __name__ == '__main__')"
    
    # Check if we can find it
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        print(f"Could not find get_player_stats in {filepath}")
        return

    new_content = content.replace(match.group(0), NEW_FUNCTION + "\n\n")
    
    with open(filepath, 'w') as f:
        f.write(new_content)
    print(f"Updated {filepath}")

# Update both files
update_file('api/app.py')
update_file('api_server.py')
