# NHL Daily Microstats Catalog

Daily predictions (`daily-nhl-predictions.yml` → `fast_maintenance` → `TeamAdvancedMetricsBuilder`) now compute a PBP microstats layer into `data/team_advanced_metrics.json` under each team’s `microstats` object.

## Your list — status

| Metric | Daily status | How |
|--------|--------------|-----|
| Turnover rate per zone | **Automated** | Giveaways O/N/D → per-game rates |
| Positive vs failed touches by zone | **Proxy** | Positive ≈ takeaway/shot/hit; failed ≈ giveaway (not InStat touch tags) |
| Forecheck recoveries | **Proxy** | OZ takeaways |
| Controlled exits | **Proxy** | D→N/O with possession-family first event |
| Controlled entries | **Automated** | Dump-in research `entry_kind` |
| Dump-ins | **Automated** | Non-controlled first OZ touch |
| Dump-in locations | **Automated** | Corner / rim / deep slot / short NZ |
| Scoring chances off the rush | **Automated** | SC (≤25 ft) within 6s of possession change |
| Puck battle win rate by zone | **Missing** | Needs InStat/tracking |
| Slot driving plays | **Proxy** | Slot arrival ≤5s after own outside-slot event (carry vs pass by player id) |
| DZ recovery → DZ exit rate | **Proxy** | DZ takeaway → N/O within 12s |
| Scoring chances off entries | **Automated** | SC within 10s of entry |

## Already on the daily path (related)

- Rush / FC / NZT / NZTSA season features (`generate_real_team_stats`)
- Edge speed / distance / bursts
- Rebounds, DZ/HD giveaways, slot blocks, EX→EN / EN→S timings
- Cycle shots / forecheck_turnovers proxies (`ExperimentalMetricsAnalyzer`)

## InStat-only (Clarkson/analytics-metrics — not NHL daily)

Battles won/lost by zone, true FC recoveries, passes to slot, entry denials, carry-in %, exit off retrieval % (tagged), dump-in chances, FC-to-shot %, royal road, positive/failed vendor touches.

Canonical defs: `analytics-metrics/docs/CANONICAL_DEFINITIONS.md`.

## Code

- Calculator: `analyzers/nhl_pbp_microstats.py`
- Wiring: `analyzers/team_advanced_metrics_builder.py` (`microstats_schema_version`)
- Research source: `nhl-dump-in-research/analysis.py`

## Personal warehouse (team + skater + goalie)

See `/Users/emilyfehr8/CascadeProjects/metrics-warehouse/` — daily via `fast_maintenance` → `pipelines/daily_refresh.py`.

| Store | Path |
|-------|------|
| Teams | `metrics-warehouse/curated/teams_season.json` |
| Skaters (NHL PBP) | `…/curated/skaters_season.json` |
| Goalies (Last Line of Defense) | `…/curated/goalies_season.json` |
| InStat skaters/goalies | `…/curated/skaters/instat_*`, `…/curated/goalies/instat_*` |
| APGR publish | `automated-post-game-reports/data/metrics_warehouse/` |
