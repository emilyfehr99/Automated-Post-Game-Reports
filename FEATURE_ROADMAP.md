# NHL Analytics Feature Roadmap
*Tracking possible features to add to the game report system*

---

## 🎯 Sprite Data Features (Frame-by-Frame Tracking)

### ✅ Currently Available
- [x] Sprite data extraction script (`sprite_parser.py`)
- [x] Release point & goal point coordinates
- [x] Frame count & shot duration

### 🚀 High Priority Additions

#### 1. Shot Trajectory Visualization
**What**: Arrow overlay on shot charts showing puck path from release → goal
- [ ] Parse release point from sprite data for all goals
- [ ] Calculate trajectory angle and distance
- [ ] Add arrow graphics to PDF report shot charts
- [ ] Color-code: Clean shots (blue), Deflections (red), Tips (orange)

**Impact**: Visual storytelling - see how goals were actually scored

---

#### 2. True Shot Distance/Angle (xG Enhancement)
**What**: Use actual release point instead of recorded shot location
- [ ] Extract release coordinates for all shots with sprite data
- [ ] Calculate true Euclidean distance to goal
- [ ] Calculate true shooting angle from release point
- [ ] Integrate into xG model as new features

**Impact**: 5-10% improvement in xG model accuracy

---

#### 3. Shot Velocity Calculation
**What**: Speed of puck from release to goal
- [ ] Calculate: distance / (duration_ms / 1000)
- [ ] Classify: Slap shot (>35 m/s), Wrist (20-35), Backhand (<20)
- [ ] Add to xG features (faster = harder to save)
- [ ] Display in report: "Shot Speed: 95 mph"

**Impact**: Better shot quality assessment

---

#### 4. Traffic & Screen Detection
**What**: Identify defenders between shooter and goalie
- [ ] Extract all player positions at moment of release
- [ ] Count players in "shooting lane" (release → goal path)
- [ ] Measure closest defender distance to shooter
- [ ] Flag "screened shot" if defender within 2m of lane

**Impact**: Context for "lucky" goals vs. high-skill plays

---

#### 5. Goalie Movement Analysis
**What**: Track goalie position during shot
- [ ] Extract goalie position at release frame
- [ ] Extract goalie position at goal frame
- [ ] Calculate movement distance (caught moving?)
- [ ] Measure angle to post (positioning grade)

**Impact**: Identify goalie errors vs. unstoppable shots

---

#### 6. Shot Type Auto-Classification
**What**: Machine learning to identify shot types from sprite patterns
- [ ] Features: velocity, release distance, deflection flag
- [ ] Classify: Slap, Wrist, Snap, Tip, Deflection, Backhand
- [ ] Add confidence score to reports
- [ ] Compare to API's `shotType` field (validate)

**Impact**: Automated, accurate shot type labeling

---

## 🔄 Passing Data Features

### ✅ Status: **CONFIRMED - Available in Sprite Data!**

**Validation Results** (Game 2025020536, Event 139):
- ✅ Detected 2 passes in pre-goal sequence: `91 → 48 → Goal`
- ✅ Method: Track closest player to puck frame-by-frame
- ✅ Possession changes indicate pass events
- ✅ Matches official assist data from API

**How It Works**:
```
Frame 1: Player #91 closest to puck (possessor)
Frame 50: Player #48 closest to puck → PASS detected (91→48)
Frame 100: Puck at net → Goal
```

### Implemented Features:

#### 7. Pass Sequence Tracking ⭐ HIGH VALUE
**What**: Track puck movement leading to goal
- [ ] Build possession detection algorithm (closest player to puck)
- [ ] Map pass chain before shot (A → B → C → goal) 
- [ ] Calculate pass speed (puck movement per frame)
- [ ] Identify "royal road" goals (X-coord change >40 units = cross-ice)
- [ ] Count passes in sequence (1-touch vs. multi-pass goals)
- [ ] Display in report: "Goal: 3-pass sequence, Royal Road assist"

**Technical Notes**:
```python
# Detect possession change
if closest_player_to_puck != previous_closest:
    passes.append((previous_player, current_player, timestamp))
```

**Impact**: Credit playmakers, identify team tactics, differentiate rush vs. cycle goals

---

#### 8. Zone Entry Quality ⭐ **VALIDATED - Extractable!**
**What**: How team entered offensive zone before goal
- [x] Detect blue line crossing in sprite data (X-coordinate threshold ~700)
- [x] Classify: Controlled carry (player has puck), Dump-in (no player near puck)
- [ ] Measure entry speed (distance covered in frames before/after entry)
- [ ] Track passes immediately after entry
- [ ] Correlate entry type with goal outcome

**Detection Logic**:
```python
BLUE_LINE_X = 700  # Approximate offensive blue line
if prev_puck_x < BLUE_LINE_X and curr_puck_x >= BLUE_LINE_X:
    # Zone entry detected!
    if player_within_30_units: → "Controlled Entry"
    else: → "Dump-In"
```

**Status**: ✅ Tested and working! Blue line crossings ARE detectable in 140-second sprite sequences.

**Impact**: Identify which entry strategies lead to goals (controlled = higher success rate)

---

## 📊 Advanced Metrics

#### 9. Pre-Shot Possession Time
**What**: How long puck was in zone before shot
- [ ] Use sprite timestamps to track zone time
- [ ] Classify: Rush (<3s), Quick cycle (3-10s), Extended (>10s)
- [ ] Correlate with xG/success rate

---

#### 10. Net-Front Presence Score
**What**: Quantify "chaos" around the net
- [ ] Count offensive players within "home plate" area
- [ ] Track defender positions (boxing out?)
- [ ] Calculate "battle won" score for goals

---

## 🎨 Visualization Additions

#### 11. Animated Shot Heatmaps
**What**: Show shot locations with trajectories
- [ ] Plot all shots on ice rink graphic
- [ ] Add arrows from release → goal for goals
- [ ] Size dots by xG value
- [ ] Color by outcome (goal/save/miss)

---

#### 12. Player Positioning Snapshots
**What**: Freeze-frame at moment of goal
- [ ] All 12 players + goalie positions from sprite
- [ ] Highlight scorer, assists, screens
- [ ] Overlay on rink diagram in PDF

---

## 🧠 ML Model Enhancements

#### 13. Retrain xG with Sprite Features
**New Features**:
- [ ] True shot distance (not API location)
- [ ] True shot angle
- [ ] Shot velocity
- [ ] Screened flag (traffic count)
- [ ] Goalie movement distance
- [ ] Shot type confidence

**Training**:
- [ ] Pull historical sprite data (season to date)
- [ ] Extract features for all goals + saves
- [ ] Retrain model architecture
- [ ] A/B test old vs. new model

---

## 🔧 Technical Debt

#### 14. Sprite Data Pipeline
- [ ] Cache sprite data to avoid repeated API calls
- [ ] Handle missing sprite data gracefully (older games)
- [ ] Add retry logic for 403 errors
- [ ] Batch processing for historical analysis

---

#### 15. Data Validation
- [ ] Compare sprite release point vs. API `xCoord/yCoord`
- [ ] Validate shot type classification accuracy
- [ ] Cross-check assist players in sprite vs. API
- [ ] Measure sprite data availability (% of games/shots)

---

## 📈 Reporting Features

#### 16. Shot Quality Report Card
**Display in PDF**:
- Average shot distance (true vs. API)
- Shot velocity distribution
- Traffic % (screened shots)
- Shot type breakdown with icons

---

#### 17. Team Tactics Insights
**Example Callouts**:
- "CHI averaged 3 passes before shooting (team avg: 1.8)"
- "MTL allowed 78% of shots from Royal Road position"
- "Goalie caught moving on 4 of 6 goals against"

---

## 🎯 Quick Wins (Easiest First)

### Phase 1 (This Week)
1. ✅ Sprite data extraction working
2. [ ] Add true shot distance to xG calculation
3. [ ] Display shot velocity in reports

### Phase 2 (Next Week)
4. [ ] Shot trajectory arrows on charts
5. [ ] Traffic detection (screened shots)
6. [ ] Shot type auto-classification

### Phase 3 (Later)
7. [ ] Passing sequence tracking (if data found)
8. [ ] Full xG model retrain
9. [ ] Animated visualizations

---

## 📝 Notes
- Sprite data requires browser headers to access
- Not all shots may have sprite data (testing needed)
- Historical data availability unknown (how far back?)
- Check if real-time sprite data available during live games

---

*Last Updated: 2025-12-21*
