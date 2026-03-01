import json

with open("data/win_probability_predictions_v2.json", "r") as f:
    data = json.load(f)

for i in (0, -1):
    print(f"Prediction {i}:")
    for k, v in data['predictions'][i].items():
        if k != 'metrics_used':
            print(f"  {k}: {v}")
