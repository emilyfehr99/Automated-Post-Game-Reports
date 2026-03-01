import json
from score_prediction_model import ScorePredictionModel

model = ScorePredictionModel()
with open('data/win_probability_predictions_v2.json', 'r') as f:
    data = json.load(f)

predictions = data.get('predictions', [])
completed = [p for p in predictions if p.get('actual_winner') and p.get('actual_winner') not in ('', None)]

correct = 0
for pred in completed:
    away = pred.get('away_team')
    home = pred.get('home_team')
    actual = pred.get('actual_winner')
    # Run the raw model
    res = model.predict_score(away, home)
    away_score = res['away_score']
    home_score = res['home_score']
    away_xg = res['away_xg']
    home_xg = res['home_xg']
    
    predicted_winner = away if away_xg >= home_xg else home
    actual_winner = away if actual == away or actual == "away" else home
    
    if predicted_winner == actual_winner:
        correct += 1

print(f"Momentum Model Accuracy: {correct}/{len(completed)} = {correct/len(completed):.1%}")
