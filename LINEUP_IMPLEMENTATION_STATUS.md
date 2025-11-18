# Lineup/Injury Implementation Status

## ✅ Phase 1: Goalie Confirmation (IMPLEMENTED)

### What's Done
- **LineupService** created (`lineup_service.py`)
- Checks NHL API boxscore data for confirmed starting goalies
- Caches results for 4 hours (prevents redundant API calls)
- Integrated into prediction pipeline (`prediction_interface.py`)
- Updates goalie GSAX calculation to use confirmed goalies when available
- Falls back to predicted starters if confirmation unavailable

### How It Works
1. Before predictions, checks for confirmed goalies via `LineupService.get_confirmed_goalie()`
2. If confirmed goalie found → uses that goalie's GSAX directly
3. If not confirmed → uses predicted starter (rotation patterns, B2B, etc.)
4. Results cached to avoid repeated API calls

### Timing
- **Available**: ~30 minutes before game time (when boxscore data becomes available)
- **Best use**: Update predictions 1-2 hours before game time

### Expected Impact
- **+2-3% accuracy** when goalies are confirmed
- Eliminates goalie uncertainty (60-70% confidence → 95%+)

---

## 📋 Phase 2: Key Player Injuries (PLACEHOLDER - READY FOR IMPLEMENTATION)

### Structure in Place
- `LineupService.get_injured_players()` - returns list of injured players
- `LineupService.calculate_injury_impact()` - calculates team strength adjustment

### What's Needed
1. **Data Source**: 
   - Option A: Scrape NHL.com team injury pages
   - Option B: Twitter scraping for beat writer reports
   - Option C: Paid API (Rotowire/Rotogrinders)

2. **Player Value Database**:
   - Map players to impact tiers (star, good, role player)
   - Could use WAR/GAR metrics or simple top-scorer lists

3. **Integration**:
   - Call `get_injured_players()` before predictions
   - Adjust team strength metrics (GS, xG expectations)
   - Pass to correlation model in metrics

### Expected Impact
- **+2-3% accuracy** when key injuries are tracked
- Especially valuable for star player injuries

---

## 📋 Phase 3: Full Lineup (PLACEHOLDER - FUTURE)

### Structure in Place
- `LineupService.get_confirmed_lineup()` - placeholder method

### What's Needed
1. Extract full forward lines and defense pairings from NHL API
2. Track power play units
3. Adjust predictions based on lineup quality
4. More complex than Phase 2, lower ROI

### Expected Impact
- **+1-2% accuracy** incremental over Phase 2

---

## Implementation Roadmap

### Quick Wins (Do First)
1. ✅ **Phase 1: Goalie Confirmation** - DONE
2. **Enhance Phase 1**: Add Twitter scraping fallback for earlier confirmation (~2-4 hours before game)

### Medium Priority
3. **Phase 2: Injury Tracking** - Scrape NHL.com or Twitter for injuries
4. **Player Impact Database** - Build star/good/role player tiers

### Long-term
5. **Phase 3: Full Lineup** - If ROI justifies complexity

---

## Current Usage

The lineup service is **automatically active** in:
- `prediction_interface.py` - Daily predictions check for confirmed goalies
- `run_predictions_for_date.py` - Historical date predictions use lineup service

**To manually test:**
```python
from lineup_service import LineupService
service = LineupService()
goalie = service.get_confirmed_goalie('BOS', '2025020001', '2025-10-31')
```

---

## Notes

- **Cache**: Lineup data cached in `lineup_cache.json` (4-hour validity)
- **Fallback**: If no confirmation available, uses existing goalie prediction logic
- **No breaking changes**: All changes are backward compatible

