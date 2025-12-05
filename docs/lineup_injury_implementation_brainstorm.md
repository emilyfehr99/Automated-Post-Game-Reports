# Confirmed Lineup/Injury Implementation - Brainstorming

## Current State
- Model predicts starting goalies based on rotation patterns, B2B switches, opponent strength
- No injury/lineup data currently used
- Goalie predictions are probabilistic (rotation heuristics)

## Data Sources to Consider

### 1. NHL Official API
- **Lineup Data**: Check if NHL API provides confirmed lineups (often ~1-2 hours before game)
- **Injury Reports**: Official NHL injury reports
- **Game Day Scratches**: Available closer to game time

### 2. External APIs/Services
- **The Score/ESPN APIs**: May have injury/lineup data
- **Rotowire/Rotogrinders**: Scraping (if allowed) or paid API access
- **Twitter/X**: Team beat writers often post confirmed lineups ~2-4 hours before game

### 3. Web Scraping
- NHL.com team pages for injury reports
- Daily Faceoff / other lineup sites
- Reddit r/hockey game day threads (unreliable but sometimes early)

## Implementation Approach

### Phase 1: Goalie Confirmation (Easiest Win)
**Timing**: ~2 hours before game time
- Check NHL API for confirmed starting goalies (if available)
- Fallback: Twitter scraping for team beat writers
- Impact: Reduces goalie uncertainty from ~60-70% confidence to 95%+

### Phase 2: Key Player Injuries (Medium Priority)
**Timing**: Morning skate reports (4-6 hours before game)
- Track injury status for:
  - Top 6 forwards (especially goal scorers)
  - Top 4 defensemen
  - Starting goalie
- Impact: 2-5% accuracy boost if key player out

### Phase 3: Full Lineup (Lower Priority)
**Timing**: 1-2 hours before game
- Confirmed lines/pairings
- Power play units
- Impact: Smaller (1-2% accuracy), but useful for in-game predictions

## Technical Implementation Ideas

### Option A: Pre-Game Check Script
- Run ~2-4 hours before each game
- Fetch confirmed lineups from NHL API or scrape
- Update predictions in real-time if available
- Store in database/cache for model access

### Option B: Enhanced Prediction Interface
- Add `use_confirmed_lineups=True` flag
- If confirmed lineup available, override goalie prediction
- Adjust team strength metrics if key players out
- Recalculate prediction with confirmed data

### Option C: Separate Lineup Service
- Microservice that polls for lineup data
- Updates every 15-30 minutes on game days
- Model queries this service before final prediction
- More reliable but requires infrastructure

## Specific Features to Add

### 1. Goalie Confirmation
```python
def get_confirmed_starter(team: str, game_date: str) -> Optional[str]:
    # Check NHL API first
    # Fallback to Twitter scraping
    # Return goalie name or None
```

### 2. Injury Impact Scoring
```python
def calculate_injury_impact(team: str, injured_players: List[str]) -> float:
    # Map players to impact tiers (star, good, role player)
    # Calculate % of team's production out
    # Return adjustment factor (0.95-1.0)
```

### 3. Lineup Strength Adjustment
```python
def adjust_prediction_for_lineups(pred: Dict, away_lineup: Lineup, home_lineup: Lineup) -> Dict:
    # Adjust team strength metrics based on missing players
    # Recalculate GS, xG expectations
    # Return updated prediction
```

## Challenges & Solutions

### Challenge 1: Data Availability
- **Problem**: NHL API may not have confirmed lineups early enough
- **Solution**: Multi-source approach (API → Twitter → Fallback to prediction)

### Challenge 2: Injury Status Ambiguity
- **Problem**: "Game-time decision" vs "Out" vs "Questionable"
- **Solution**: Weight predictions by confidence level (50% if questionable, 0% if out)

### Challenge 3: Player Value Quantification
- **Problem**: How much does losing a specific player affect team strength?
- **Solution**: 
  - Use player WAR/GAR metrics if available
  - Historical win% with/without player
  - Simple tier system (star, top-6, role player)

### Challenge 4: Timing
- **Problem**: Predictions run in morning, lineups confirmed later
- **Solution**: 
  - Two-stage predictions: initial (morning) and final (2 hours before)
  - Discord bot to send updates if lineups change predictions significantly

## Recommended Implementation Order

1. **Quick Win**: Goalie confirmation check (~2 hours before game)
   - Biggest impact (goalie is ~10-15% of prediction)
   - Relatively simple (check one piece of data)

2. **Medium Effort**: Star player injury tracking
   - Focus on top scorers/goalies
   - Use simple tier system (star out = -3%, good player = -1.5%)

3. **Long-term**: Full lineup service
   - Most accurate but requires ongoing maintenance
   - Best ROI after basics are working

## Expected Impact

- **Goalie Confirmation Only**: +2-3% accuracy
- **Goalie + Star Injuries**: +4-6% accuracy  
- **Full Lineup Service**: +5-8% accuracy

Total potential: Move from 74.9% → 80-83% accuracy

