import json
from pathlib import Path
from datetime import datetime

file_path = Path('data/win_probability_predictions_v2.json')

try:
    with open(file_path, 'r') as f:
        data = json.load(f)
        predictions = data.get('predictions', [])
        
        print(f"Total predictions: {len(predictions)}")
        
        if predictions:
            # Sort by date just in case
            predictions.sort(key=lambda x: x.get('date', ''))
            
            print("\nLast 10 predictions:")
            for p in predictions[-10:]:
                print(f"Date: {p.get('date')}, Game: {p.get('away_team')} @ {p.get('home_team')}, Winner: {p.get('actual_winner')}, Predicted: {p.get('predicted_winner')}")
        
        # Check specific stats
        perf = data.get('model_performance', {})
        print(f"\nStored Performance: {perf}")

except Exception as e:
    print(f"Error reading file: {e}")
