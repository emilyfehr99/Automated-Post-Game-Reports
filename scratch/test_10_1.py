import json
import sys
sys.path.append('.')
from models.score_prediction_model import ScorePredictionModel

model = ScorePredictionModel()
pred = model.predict_score('UTA', 'VGK', is_playoff=True, series_status={'pace_offset': -1.67})
print(json.dumps(pred, indent=2))
