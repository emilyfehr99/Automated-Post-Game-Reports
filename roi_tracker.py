
import json
from pathlib import Path
from datetime import datetime

class ROITracker:
    def __init__(self, history_file='data/win_probability_predictions_v2.json'):
        self.history_file = Path(history_file)
        if not self.history_file.exists():
            self.history_file = Path('win_probability_predictions_v2.json')
            
    def calculate_roi(self):
        """Analyze historical predictions to calculate theoretical ROI"""
        if not self.history_file.exists():
            return {"error": "History file not found"}
            
        try:
            with open(self.history_file, 'r') as f:
                data = json.load(f)
            
            predictions = data.get('predictions', [])
            completed_games = [p for p in predictions if 'actual_winner' in p or ('actual_home_score' in p and 'actual_away_score' in p)]
            
            if not completed_games:
                return {"error": "No completed games with outcomes found"}
                
            total_invested = 0.0
            total_return = 0.0
            win_count = 0
            loss_count = 0
            
            for p in completed_games:
                units = p.get('suggested_units', 0.0)
                if units <= 0:
                    continue
                    
                total_invested += units
                
                # Determine winner
                actual_winner = p.get('actual_winner')
                if not actual_winner:
                    h_score = p.get('actual_home_score', 0)
                    a_score = p.get('actual_away_score', 0)
                    if h_score > a_score:
                        actual_winner = p.get('home_team')
                    elif a_score > h_score:
                        actual_winner = p.get('away_team')
                
                if not actual_winner:
                    continue
                    
                predicted_winner = p.get('predicted_winner')
                ml = p.get('odds_taken') # We should store the ML when predicting
                
                if not ml:
                    # Fallback or skip if no odds recorded
                    continue
                
                # Decimal odds conversion
                decimal_odds = (ml / 100 + 1) if ml > 0 else (100 / abs(ml) + 1)
                
                if predicted_winner == actual_winner:
                    total_return += units * decimal_odds
                    win_count += 1
                else:
                    loss_count += 1
            
            roi = ((total_return - total_invested) / total_invested * 100) if total_invested > 0 else 0
            
            return {
                "total_invested": round(total_invested, 2),
                "total_return": round(total_return, 2),
                "net_profit": round(total_return - total_invested, 2),
                "roi_pct": round(roi, 2),
                "win_rate": round(win_count / (win_count + loss_count) * 100, 2) if (win_count + loss_count) > 0 else 0,
                "sample_size": win_count + loss_count
            }
            
        except Exception as e:
            return {"error": str(e)}

if __name__ == "__main__":
    tracker = ROITracker()
    stats = tracker.calculate_roi()
    print(json.dumps(stats, indent=2))
