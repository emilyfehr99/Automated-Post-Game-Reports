# 🎯 Expected Goals (xG) Model Improvement Plan

**Date:** October 15, 2025  
**Current Status:** Simple rule-based xG model  
**Goal:** Build a more sophisticated xG model using NHL play-by-play data

---

## 📊 Research Summary

### Key Insights from Hockey-Statistics.com Model:

**Their Approach:**
- Built baseline model from 5v5 shot location (FSh% per grid box)
- Applied multiplicative adjustments for various factors
- Formula: `xG = (xG_base) × (Rebound) × (Rush) × (Shot Type) × (Score State) × (Rink) × (Season)`

**Their Adjustments (5v5):**
- **Rebound:** 2.130× (shots within 2 seconds of previous shot)
- **Rush:** 1.671× (shots within 4 seconds of neutral/defensive zone event)
- **Shot Types:**
  - Snap: 1.137×
  - Slap: 1.168×
  - Wrist: 0.865×
  - Tip-In: 0.697×
  - Deflected: 0.683×
  - Backhand: 0.657×
  - Wrap-around: 0.356×
- **Score State:** Varies (0.953× to 1.107×)
- **Log Loss:** 0.1925 (5v5), 0.2098 (all strengths)
- **AUC:** 0.7720 (5v5), 0.7634 (all strengths)

### Key Insights from Evolving-Hockey:
- Uses gradient boosting models
- Includes player tracking data when available
- Focus on both descriptive (past) and predictive (future) accuracy
- Similar performance metrics to Hockey-Statistics

### Key Insights from Hockey Analysis Comparison:
- Most public models achieve ~0.77 AUC and ~0.20 log loss
- Marginal differences between models
- Shot location is the most important variable

---

## 🔍 Current Model Analysis

### What We Have Now:
```python
def _calculate_expected_goals(self, x_coord, y_coord, zone, shot_type, event_type):
    # Distance-based xG (4 tiers: <20ft, 20-35ft, 35-50ft, >50ft)
    # Angle adjustment (4 tiers: 0-15°, 15-30°, 30-45°, >45°)
    # Zone multiplier (O=1.5/1.2/0.8, N=0.3, D=0.1)
    # Shot type multiplier
    # Event type multiplier (shot-on-goal=1.0, miss=0.7, block=0.5)
```

### Strengths:
✅ Simple and interpretable  
✅ Uses distance and angle  
✅ Accounts for shot type  
✅ Fast to compute  

### Weaknesses:
❌ Not trained on actual data (arbitrary multipliers)  
❌ No rebound detection  
❌ No rush detection  
❌ No strength state differentiation (5v5, PP, PK)  
❌ No time-based factors  
❌ Coarse distance/angle bins  
❌ No score state consideration  

---

## 🎯 Available Data from NHL API

From play-by-play data, we have access to:

### Spatial Data:
✅ `xCoord`, `yCoord` - Shot coordinates  
✅ `zoneCode` - Zone (O/N/D)  

### Shot Details:
✅ `shotType` - Type of shot (wrist, slap, snap, backhand, tip-in, deflected, wrap-around)  
✅ `typeDescKey` - Event type (shot-on-goal, missed-shot, blocked-shot, goal)  

### Game Context:
✅ `situationCode` - Strength state (e.g., "1551" = 5v5)  
✅ `timeInPeriod` - Time of event  
✅ `period` - Period number  
✅ Game score (can derive score state)  

### Player Data:
✅ `shootingPlayerId` - Who took the shot  
✅ `goalieInNetId` - Goalie facing the shot  

### Event Sequence:
✅ Previous events (can derive rebounds, rushes, passes)  
✅ Time between events  

### What We DON'T Have:
❌ Player positions/locations (beyond shooter)  
❌ Puck speed  
❌ Shot release type  
❌ Traffic/screen indicators  
❌ Pass reception location  

---

## 💡 Improvement Ideas (Feasibility Ranking)

### 🟢 HIGH PRIORITY (Easy & High Impact):

1. **Data-Driven Baseline Model**
   - Scrape historical NHL data (2019-2024)
   - Create grid-based baseline like Hockey-Statistics
   - Calculate actual FSh% (Fenwick Shooting %) per location
   - **Impact:** Major - replaces arbitrary multipliers with real data
   - **Effort:** Medium - need to build data collection pipeline

2. **Rebound Detection**
   - Identify shots within 2-3 seconds of previous shot
   - Apply ~2× multiplier (backed by research)
   - **Impact:** High - rebounds are much more dangerous
   - **Effort:** Low - just need to track previous event timing

3. **Rush Shot Detection**
   - Identify shots within 4 seconds of neutral/defensive zone event
   - Apply ~1.7× multiplier
   - **Impact:** High - rush chances are dangerous
   - **Effort:** Low - track event zones and timing

4. **Strength State Differentiation**
   - Build separate models for 5v5, 4v4, 3v3, 5v4, 5v3, 4v5
   - Power play shots are more dangerous
   - **Impact:** High - different game states have very different scoring rates
   - **Effort:** Medium - need to parse situationCode properly

5. **Improved Distance/Angle Calculation**
   - Use continuous values instead of bins
   - Use actual shooting percentage curves from data
   - **Impact:** Medium-High - more accurate location modeling
   - **Effort:** Low - just refine existing calculation

### 🟡 MEDIUM PRIORITY (Moderate Effort, Good Impact):

6. **Score State Adjustment**
   - Teams play differently when leading/trailing
   - Apply multipliers based on goal differential
   - **Impact:** Medium - affects shot quality
   - **Effort:** Low - just need to track game score

7. **Shot Type Refinements**
   - Use data-driven multipliers from historical data
   - Currently using arbitrary values
   - **Impact:** Medium - shot types matter
   - **Effort:** Medium - need to analyze historical shot types

8. **Time Since Last Event**
   - Quick shots after events can catch goalies out of position
   - Different from rebounds (any event, not just shots)
   - **Impact:** Medium - goalie positioning matters
   - **Effort:** Low - track all event timing

9. **Angle Change Detection**
   - Compare shot location to previous event location
   - Large angle changes challenge goalies
   - **Impact:** Medium - lateral movement is hard for goalies
   - **Effort:** Medium - need to track previous event coordinates

10. **Period/Time Effects**
    - Scoring rates may vary by period or game time
    - Fatigue effects in 3rd period
    - **Impact:** Low-Medium - small effect
    - **Effort:** Low - just add period/time variables

### 🔴 LOW PRIORITY (High Effort or Low Impact):

11. **Pre-Shot Movement Detection**
    - Track sequences of events leading to shot
    - Passing sequences, carries, etc.
    - **Impact:** Medium - but hard to model without tracking data
    - **Effort:** High - complex sequence modeling

12. **Rink Bias Adjustment**
    - Some arenas have measurement biases
    - **Impact:** Low - small effect
    - **Effort:** Medium - need to model each arena

13. **Season Trends**
    - Rules changes, equipment changes over time
    - **Impact:** Low - we're focused on recent data
    - **Effort:** Low - just add season variable

14. **Player Shooting Skill**
    - DON'T include in xG model (by design)
    - xG should be quality of chance, not shooter
    - Use for GAx (Goals Above xG) calculations instead
    - **Impact:** N/A - intentionally excluded
    - **Effort:** N/A

---

## 🎯 Recommended Implementation Plan

### Phase 1: Data Collection & Baseline (Week 1)
1. Build scraper for historical NHL play-by-play data (2019-2024)
2. Create coordinate grid system (e.g., 2ft × 2ft boxes)
3. Calculate baseline FSh% per grid location for each strength state
4. Validate against known models

### Phase 2: Basic Adjustments (Week 1-2)
1. Add rebound detection (2 sec window)
2. Add rush detection (4 sec + zone change)
3. Add strength state models (5v5, PP, PK, etc.)
4. Add score state adjustments
5. Validate improvements with log loss & AUC

### Phase 3: Advanced Features (Week 2-3)
1. Add time since last event
2. Add angle change from previous event
3. Refine shot type multipliers with data
4. Add period/time effects
5. Final validation and testing

### Phase 4: Integration & Deployment (Week 3-4)
1. Replace current xG model in codebase
2. Update reports to use new xG values
3. Test on recent games
4. Monitor for issues
5. Document model version and performance

---

## 📈 Success Metrics

### Model Performance Goals:
- **Log Loss:** < 0.21 (competitive with public models)
- **AUC:** > 0.76 (competitive with public models)
- **Calibration:** xG totals should match actual goals over large samples

### Validation Tests:
1. **Descriptive:** GSAx rankings should match expert opinion
2. **Predictive:** Team xGF% should predict future GF% (R² > 0.45)
3. **Stability:** Model should be consistent across different time periods

---

## 🔧 Technical Considerations

### Model Type Options:

**Option A: Multiplicative Adjustment Model** (Hockey-Statistics approach)
- ✅ Simple, interpretable
- ✅ Fast to compute
- ✅ Easy to update individual components
- ❌ Assumes independence of factors
- **Recommendation:** Start here

**Option B: Logistic Regression**
- ✅ Probabilistic output
- ✅ Can model interactions
- ✅ Well understood
- ❌ Need careful feature engineering
- **Recommendation:** Try after Option A

**Option C: Gradient Boosting (XGBoost, LightGBM)**
- ✅ State-of-the-art performance
- ✅ Captures complex interactions
- ❌ Less interpretable
- ❌ Slower to compute
- ❌ Requires more data and tuning
- **Recommendation:** Future enhancement

### Data Storage:
- Store historical play-by-play in SQLite database
- Cache baseline xG grid in JSON/CSV for fast lookup
- Version control xG model parameters

### Code Architecture:
```python
class ImprovedXGModel:
    def __init__(self):
        self.baseline_grid = self.load_baseline()  # FSh% per location
        self.adjustments = self.load_adjustments()  # Multipliers
    
    def calculate_xg(self, shot_data):
        # 1. Get baseline from location
        base_xg = self.get_baseline_xg(shot_data['x'], shot_data['y'], 
                                        shot_data['strength_state'])
        
        # 2. Apply adjustments
        rebound_adj = self.get_rebound_adjustment(shot_data, previous_events)
        rush_adj = self.get_rush_adjustment(shot_data, previous_events)
        shot_type_adj = self.get_shot_type_adjustment(shot_data['shot_type'])
        score_adj = self.get_score_adjustment(shot_data['score_differential'])
        
        # 3. Combine
        final_xg = base_xg * rebound_adj * rush_adj * shot_type_adj * score_adj
        
        return min(final_xg, 0.95)  # Cap at 95%
```

---

## 🚧 Challenges & Limitations

1. **Data Quality:** NHL API has some errors/inconsistencies
2. **Historical Data:** May need to handle different API versions over time
3. **Computation Time:** Grid-based lookup should be fast, but need to test at scale
4. **Model Complexity:** Balance between accuracy and interpretability
5. **No Tracking Data:** Can't model player positions, traffic, etc.

---

## 📚 References

1. Hockey-Statistics.com - Building an xG model v1.0
2. Evolving-Hockey - Expected Goals Model
3. Hockey Analysis - Comparison of Public xG Models
4. NHL API Documentation

---

## ✅ Next Steps

1. **Brainstorm Review** ← WE ARE HERE
2. Get user approval on approach
3. Start Phase 1: Data collection
4. Build prototype
5. Test and iterate

**Question for User:** 
- Which phases should we prioritize?
- Should we start with Phase 1 (data collection) or implement quick wins (rebounds, rushes) first?
- Any specific features you want prioritized?
