# Self-Learning Win Probability Model

## Overview

This is a separate system that learns from its own win probability predictions and game outcomes. It runs alongside the existing post-game reports **without affecting them whatsoever**.

## How It Works

### 1. **Prediction Recording**
- When games finish, the model makes win probability predictions using current metrics
- Predictions are stored with all the metrics used (xG, high danger chances, shot attempts, etc.)
- Each prediction includes the model weights used at the time

### 2. **Outcome Tracking**
- After games finish, the model records the actual winner
- Calculates prediction accuracy (how confident we were in the correct outcome)
- Updates the prediction record with the outcome

### 3. **Model Learning**
- Analyzes which metrics were most predictive
- Adjusts model weights based on prediction accuracy
- Continuously improves over time

## Files

- `self_learning_model.py` - Core model implementation
- `self_learning_runner.py` - Runner for processing games
- `self_learning_integration.py` - Integration script for GitHub Actions
- `win_probability_predictions.json` - Data storage file

## Current Status

✅ **Working and Tested**
- Successfully processed 4 games from yesterday
- Current accuracy: 54.1% (better than random 50%)
- Model is learning and improving

## Integration with GitHub Actions

The self-learning model can be integrated into the GitHub Actions workflow by adding this line to the workflow:

```yaml
- name: Update Self-Learning Model
  run: python3 nhl_postgame_reports/self_learning_integration.py
```

This runs **after** the main post-game reports are generated and posted, so it doesn't interfere with the current system.

## Data Structure

Each prediction record contains:
```json
{
  "game_id": "2025020072",
  "date": "2025-10-17",
  "away_team": "TBL",
  "home_team": "DET",
  "predicted_away_win_prob": 51.7,
  "predicted_home_win_prob": 48.3,
  "actual_winner": "home",
  "metrics_used": {
    "away_xg": 3.39,
    "home_xg": 2.77,
    "away_hdc": 0,
    "home_hdc": 0,
    "away_shots": 0,
    "home_shots": 0,
    "away_fo_pct": 50,
    "home_fo_pct": 50,
    "model_weights": {...}
  },
  "prediction_accuracy": 0.483,
  "timestamp": "2025-10-18T14:37:33.041968"
}
```

## Future Enhancements

1. **Advanced Learning Algorithms**
   - Implement more sophisticated ML models
   - Add neural networks for complex pattern recognition

2. **Situational Awareness**
   - Learn that different metrics matter in different situations
   - Score state, time remaining, team-specific adjustments

3. **Real-time Predictions**
   - Make predictions during live games
   - Update predictions as the game progresses

4. **Performance Analytics**
   - Track model performance over time
   - Identify when the model is most/least accurate

## Usage

### Manual Testing
```bash
# Test the model
python3 nhl_postgame_reports/self_learning_runner.py

# Run daily update
python3 nhl_postgame_reports/self_learning_integration.py
```

### Integration with GitHub Actions
Add to your workflow file:
```yaml
- name: Update Self-Learning Model
  run: python3 nhl_postgame_reports/self_learning_integration.py
```

## Important Notes

- **Does NOT affect current post-game reports**
- **Runs independently** of the main workflow
- **Stores data locally** in `win_probability_predictions.json`
- **Can be safely disabled** without affecting anything else
- **Learns from actual game outcomes** to improve predictions

The system is designed to be completely separate and non-intrusive while providing valuable learning capabilities for win probability prediction.
