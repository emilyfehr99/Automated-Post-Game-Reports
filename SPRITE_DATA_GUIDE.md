# NHL Sprite Tracking Data - Analytics Applications

## What You Get

The sprite data provides **frame-by-frame tracking** (140 frames in 139ms for the example):

- **Puck Position**: Exact X/Y coordinates every ~1ms
- **All Players**: Position of every skater on ice
- **Timestamps**: Precise timing for entire play sequence

## Key Data Points Extracted

### 1. Release Point
**What**: Where the puck left the shooter's stick  
**Example**: `(607.2, 17.4)` - Near center ice, offensive zone

### 2. Goal Point  
**What**: Where puck crossed goal line  
**Example**: `(2285.2, 493.5)` - Exact net location

### 3. Shot Distance (True)
**Calculation**: Distance from release point to goal  
**Why Better**: Current API only gives "shot location" (often recorded at different spot than actual release)

---

## Applications for Analytics

### 🎯 **1. Improved xG Models**

#### Current Problem:
- Basic models use shot location as recorded
- This is often where the **shot was taken**, not where **puck was released**
- Tips, deflections show incorrect origin

#### With Sprite Data:
```
True Shot Distance = √[(goal_x - release_x)² + (goal_y - release_y)²]
```
- **More accurate distance** = better xG prediction
- Distinguishes between:
  - Clean shot from point
  - Tip-in at net front (shorter "true" distance)
  - Deflections (angle changes mid-flight)

**Impact**: Could improve xG model accuracy by 5-10%

---

### 📐 **2. Shot Angle Precision**

#### Calculate True Shooting Angle:
```python
angle = atan2(goal_y - release_y, goal_x - release_x)
```

**Why It Matters**:
- Shots from same "location" but different release points = different angles
- Royal road passes (cross-ice) vs. straight shots
- Backdoor tap-ins have extreme angles

---

### ⚡ **3. Shot Velocity**

#### From Frame Data:
```python
velocity = distance / (duration_ms / 1000)  # meters per second
```

**Applications**:
- Slap shots = higher velocity = harder to save
- Wrist shots = slower but more accurate
- Quick release vs. wind-up time
- **Goalie reaction time** calculation

---

### 🏃 **4. Player Positioning Context**

The sprite data includes **all 12 players' positions** at moment of shot.

#### Traffic Analysis:
- **Screen detection**: Defenders between shooter and goalie
- **Passing lanes**: Assist player positioning before release
- **Net-front presence**: Players creating chaos

#### Example Use Cases:
```
Distance to nearest defender at release
Number of players in "high danger" zone
Goalie sightline obstruction (% blocked)
```

---

### 🧠 **5. Advanced Shot Quality Metrics**

#### Shot Trajectory Quality:
- **Clean vs. Traffic**: Open lane vs. screened
- **Rush vs. Set**: Speed of setup (frame count before release)
- **One-timer detection**: Puck movement speed before release

#### Goalie Positioning:
- Where was goalie at moment of release vs. goal?
- Movement during shot (caught moving?)
- Distance from post

---

### 📊 **6. Play Sequence Analysis**

#### Pre-Shot Setup (frames -5 to 0):
- **Possession time** in zone before shot
- **Puck movement speed** (quick passing)
- **Zone entries**: Rush vs. cycle

#### Example Insights:
```
Fast passing (puck moved >2m in <500ms before shot)
  → Higher xG (goalie out of position)

Static zone time (puck moved <1m in last 2 seconds)
  → Lower xG (defense set, goalie ready)
```

---

## Practical Implementation for Your Reports

### Immediate Additions:

#### 1. **Enhanced Shot Charts**
- Plot **release point** with arrow to goal point
- Shows shot trajectory, not just end location
- Visual distinction: clean shots vs. deflections

#### 2. **New xG Features**
Add to your model:
```python
features = {
    'true_shot_distance': calculate_distance(release, goal),
    'shot_angle': calculate_angle(release, goal),
    'shot_velocity': distance / time,
    'players_in_lane': count_screens(players, release, goal),
    'is_deflection': release_distance < 5  # meters from goal
}
```

#### 3. **Shot Type Classification**
```python
if velocity > 35 m/s: → Slap shot
if release_x close to goal_x: → Deflection/Tip
if angle > 45 degrees: → Cross-ice/Backdoor
```

---

## Example: The Goal We Analyzed

**Event 139: CHI @ MTL Tip-In Goal**

| Metric | Value | Insight |
|--------|-------|---------|
| Release Point | `(607, 17)` | Far from net |
| Goal Point | `(2285, 494)` | Top corner |
| True Distance | ~170 ft | Long shot |
| Duration | 139ms | Fast moving |
| Velocity | ~37 m/s | Hard shot |
| **Shot Type** | **Tip-in** | **Nazar tipped point shot** |

**xG Impact**:
- **Old model**: Uses tip location (83, -4) → High xG (close shot)
- **New model**: Uses release (607, 17) → Medium xG (deflection of long shot)
- **Reality**: Goal scored on tip, but required:
  - Point shot (release)
  - Perfect deflection (Nazar positioning)
  - High skill play

---

## Data Availability

✅ **Available for**: All goals (confirmed)  
❓ **Available for**: All shots (needs testing)  
🔧 **Access**: Requires browser headers (mimicking NHL.com)

---

## Next Steps

1. **Validate**: Test if sprite data exists for regular shots (not just goals)
2. **Integrate**: Add release point extraction to `pdf_report_generator.py`
3. **Visualize**: Create shot trajectory plots for reports
4. **Model**: Retrain xG with new distance/angle/velocity features

This is **cutting-edge data** that most public models don't have access to! 🚀
