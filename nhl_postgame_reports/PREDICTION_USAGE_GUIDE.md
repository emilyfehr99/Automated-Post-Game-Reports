# 🎯 NHL Win Probability Prediction Tool

## How to Use the Prediction Interface

### **Method 1: Command Line (Quick Predictions)**

```bash
# Make a prediction between two teams
python3 nhl_postgame_reports/prediction_interface.py TBL DET
python3 nhl_postgame_reports/prediction_interface.py BOS COL
python3 nhl_postgame_reports/prediction_interface.py TOR EDM
```

**Example Output:**
```
🔮 Making prediction: BOS @ DET
==================================================
📊 PREDICTION RESULTS:
   BOS: 54.5%
   DET: 45.5%

📈 METRICS USED:
   Expected Goals: BOS 3.1 vs DET 2.3
   High Danger Chances: BOS 4.2 vs DET 2.9
   Shot Attempts: BOS 32.1 vs DET 27.1
   Faceoff %: BOS 54.3% vs DET 49.8%

🎯 MODEL WEIGHTS:
   xG Weight: 40.0%
   High Danger Weight: 30.0%
   Shot Attempts Weight: 20.0%
   Faceoff Weight: 5.0%
```

### **Method 2: Interactive Mode**

```bash
# Start interactive mode
python3 nhl_postgame_reports/prediction_interface.py
```

Then choose from the menu:
1. **Make prediction** - Enter two team abbreviations
2. **List teams** - See all available NHL teams
3. **View model stats** - Check how well the model is performing
4. **Exit** - Quit the program

### **Method 3: Integration with Self-Learning Model**

The predictions you make are automatically stored and can be used for learning:

```bash
# Update the model with new games and learn from your predictions
python3 nhl_postgame_reports/self_learning_runner.py
```

## 🏒 Available Teams

| Abbrev | Team | Abbrev | Team |
|--------|------|--------|------|
| ANA | Anaheim Ducks | ARI | Arizona Coyotes |
| BOS | Boston Bruins | BUF | Buffalo Sabres |
| CGY | Calgary Flames | CAR | Carolina Hurricanes |
| CHI | Chicago Blackhawks | COL | Colorado Avalanche |
| CBJ | Columbus Blue Jackets | DAL | Dallas Stars |
| DET | Detroit Red Wings | EDM | Edmonton Oilers |
| FLA | Florida Panthers | LAK | Los Angeles Kings |
| MIN | Minnesota Wild | MTL | Montreal Canadiens |
| NSH | Nashville Predators | NJD | New Jersey Devils |
| NYI | New York Islanders | NYR | New York Rangers |
| OTT | Ottawa Senators | PHI | Philadelphia Flyers |
| PIT | Pittsburgh Penguins | SJS | San Jose Sharks |
| SEA | Seattle Kraken | STL | St. Louis Blues |
| TBL | Tampa Bay Lightning | TOR | Toronto Maple Leafs |
| UTA | Utah Hockey Club | VAN | Vancouver Canucks |
| VGK | Vegas Golden Knights | WSH | Washington Capitals |
| WPG | Winnipeg Jets | | |

## 🧠 How It Works

### **Prediction Process:**
1. **Team Stats Analysis** - Gets recent performance metrics for both teams
2. **Weighted Scoring** - Uses the self-learning model's weights to score each team
3. **Probability Calculation** - Converts scores to win probabilities
4. **Learning Storage** - Saves prediction for future model improvement

### **Metrics Used:**
- **Expected Goals (xG)** - 40% weight
- **High Danger Chances** - 30% weight  
- **Shot Attempts** - 20% weight
- **Faceoff Percentage** - 5% weight
- **Other Metrics** - 5% weight

### **Model Learning:**
- **Stores Predictions** - Every prediction is saved with metrics used
- **Tracks Outcomes** - When games finish, actual winners are recorded
- **Calculates Accuracy** - Measures how confident the model was in correct outcomes
- **Improves Weights** - Adjusts which metrics matter most based on results

## 📊 Current Model Performance

```bash
# Check how well the model is performing
python3 -c "
import sys
sys.path.append('nhl_postgame_reports')
from nhl_postgame_reports.self_learning_model import SelfLearningWinProbabilityModel
model = SelfLearningWinProbabilityModel()
stats = model.get_model_stats()
print(f'Model accuracy: {stats[\"average_accuracy\"]:.1%}')
"
```

## 🎯 Example Usage Scenarios

### **Scenario 1: Quick Game Prediction**
```bash
# Before a game starts, get a prediction
python3 nhl_postgame_reports/prediction_interface.py TBL DET
```

### **Scenario 2: Multiple Predictions**
```bash
# Make several predictions for the day
python3 nhl_postgame_reports/prediction_interface.py BOS COL
python3 nhl_postgame_reports/prediction_interface.py TOR EDM
python3 nhl_postgame_reports/prediction_interface.py VGK SEA
```

### **Scenario 3: Check Model Performance**
```bash
# See how well the model is doing
python3 nhl_postgame_reports/self_learning_runner.py
```

### **Scenario 4: Interactive Exploration**
```bash
# Use interactive mode to explore different matchups
python3 nhl_postgame_reports/prediction_interface.py
# Then choose option 1 to make predictions
# Choose option 2 to see all teams
# Choose option 3 to check model stats
```

## 🔮 Future Enhancements

The prediction tool can be enhanced with:

1. **Real Team Stats** - Fetch actual recent team performance data
2. **Situational Factors** - Home/away, back-to-back games, injuries
3. **Live Updates** - Update predictions during games
4. **Historical Analysis** - Show how teams have performed against each other
5. **Confidence Intervals** - Show uncertainty in predictions

## 💡 Tips for Best Results

1. **Use Recent Data** - The model learns from recent games
2. **Check Model Stats** - Monitor accuracy to see if predictions are improving
3. **Make Regular Predictions** - More data helps the model learn better
4. **Compare with Outcomes** - See how well your predictions match reality

The prediction tool is designed to be simple to use while providing valuable insights into NHL game outcomes!
