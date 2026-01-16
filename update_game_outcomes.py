#!/usr/bin/env python3
"""
Update Game Outcomes
-------------------
This script checks for past predictions that don't have an outcome (actual_winner)
and queries the NHL API to see if the game has been played. If so, it updates
the prediction record with the final score and winner.

This ensures the model performance metrics (accuracy, etc.) remain up-to-date.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from nhl_api_client import NHLAPIClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def update_game_outcomes():
    """Update valid predictions with actual game outcomes"""
    predictions_file = Path('data/win_probability_predictions_v2.json')
    if not predictions_file.exists():
        # Fallback to root directory
        predictions_file = Path('win_probability_predictions_v2.json')
    
    if not predictions_file.exists():
        logger.error(f"Predictions file not found at {predictions_file}")
        return False
        
    logger.info(f"Checking for game updates in {predictions_file}...")
    
    with open(predictions_file, 'r') as f:
        data = json.load(f)
        
    predictions = data.get('predictions', [])
    updated_count = 0
    
    client = NHLAPIClient()
    
    # Identify games that need updates (past date, no actual_winner)
    today = datetime.now().strftime('%Y-%m-%d')
    
    for pred in predictions:
        # Skip if already has an outcome (checking actual_winner explicitly)
        if pred.get('actual_winner'):
            continue
            
        game_date = pred.get('date')
        game_id = pred.get('game_id')
        
        if not game_date or not game_id:
            continue
            
        # Only check if game date is in the past or today
        if game_date > today:
            continue
            
        logger.info(f"Checking status for game {game_id} ({pred.get('away_team')} @ {pred.get('home_team')}) on {game_date}...")
        
        try:
            # We can use the cached schedule fetching from client if available, 
            # or just fetch the game data directly since we have the ID
            game_data = client.get_comprehensive_game_data(str(game_id))
            
            if not game_data:
                logger.warning(f"Could not fetch data for game {game_id}")
                continue
                
            game_state = 'Unknown'
            
            # Check game state from various possible locations in response
            if 'game_center' in game_data and game_data['game_center']:
                game_state = game_data['game_center'].get('gameState', 'Unknown')
            elif 'boxscore' in game_data and game_data['boxscore']:
                # Boxscore often doesn't have explicit state, but if it has scores and periods, it might be done
                # Usually we rely on game_center for state
                pass
                
            # If we used the schedule endpoint (not used here directly), we'd have explicit state
            # Let's try to determine winner from scores if available
            boxscore = game_data.get('boxscore', {})
            
            if boxscore:
                away_score = boxscore.get('awayTeam', {}).get('score')
                home_score = boxscore.get('homeTeam', {}).get('score')
                
                # Check if game is final (approximate check if state missing)
                # If we have valid scores and it's a past date, safe to assume it's done?
                # Better to be safe. NHL API usually returns 'OFF' or 'FINAL' in gameState
                
                is_complete = False
                if game_state in ['FINAL', 'OFF', 'OFFICIAL']:
                    is_complete = True
                elif game_date < today and away_score is not None and home_score is not None:
                    # If it's a past date and we have scores, assume complete
                    is_complete = True
                
                if is_complete and away_score is not None and home_score is not None:
                    actual_winner = None
                    if away_score > home_score:
                        actual_winner = pred.get('away_team') # Use tracked abbrev to match
                    elif home_score > away_score:
                        actual_winner = pred.get('home_team')
                    else:
                        actual_winner = 'TIE' # Rare/Impossible in regular season usually
                        
                    # Normalize abbreviations if needed (sometimes API uses different ones)
                    # We trust the prediction record's team abbrevs for consistency
                    
                    # Update the prediction record
                    pred['actual_winner'] = actual_winner
                    pred['actual_away_score'] = away_score
                    pred['actual_home_score'] = home_score
                    
                    # Calculate accuracy for this single prediction reference
                    predicted_winner = pred.get('predicted_winner')
                    is_correct = (predicted_winner == actual_winner)
                    pred['prediction_accuracy'] = 1.0 if is_correct else 0.0
                    
                    updated_count += 1
                    logger.info(f"✅ Updated: {pred['away_team']} {away_score}-{home_score} {pred['home_team']} (Winner: {actual_winner})")
        
        except Exception as e:
            logger.error(f"Error checking game {game_id}: {e}")
            continue
            
    if updated_count > 0:
        logger.info(f"Saving {updated_count} updated game outcomes to {predictions_file}...")
        
        # Save backup first
        backup_file = predictions_file.parent / f"{predictions_file.stem}_backup.json"
        try:
            with open(backup_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not create backup file: {e}")
            
        # Save updates
        with open(predictions_file, 'w') as f:
            json.dump(data, f, indent=2)
            
        logger.info("Successfully saved updates.")
    else:
        logger.info("No completed games found needing updates.")
        
    return True

if __name__ == "__main__":
    update_game_outcomes()
