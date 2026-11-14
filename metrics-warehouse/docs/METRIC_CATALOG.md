# Personal Metrics Warehouse — Catalog

Grain: **team**, **skater**, **goalie**. Sources: NHL PBP, Last Line of Defense hub, InStat (when auth works).

Schema: PBP microstats `schema_version` **3**.

## Stores

| File | Grain | Source |
|------|-------|--------|
| `curated/teams_season.json` | team | APGR advanced + microstats + Edge |
| `curated/teams/nhl_pbp_microstats.json` | team | NHL PBP microstats v3 |
| `curated/skaters_season.json` | player | NHL PBP microstats v3 |
| `curated/skaters/instat_season_flat.json` | player | InStat gear-1 + warehouse aliases |
| `curated/goalies_season.json` | goalie | **Last Line of Defense** full hub |
| `curated/goalies/instat_league.json` | goalie | InStat gear-9 summaries |
| `curated/goalies/instat_aggs.json` | goalie | LLD charted InStat aggs |
| `curated/manifest.json` | index | build status |

Published views also copy to `automated-post-game-reports/data/metrics_warehouse/`.

## Team / skater (NHL PBP — automated daily, schema v3)

**Core:** turnover rate by zone · positive/failed touch proxies · forecheck recoveries (OZ takeaways) · controlled entries/exits · dump-ins + landing bins · SC off rush/entry · slot drives (carry/pass) · DZ recovery→exit · rush shots · entry shots · hits/blocks (skater)

**v3 additions:**
- Dump-in recovery %
- SC off dump vs carry (+ shares / per-entry)
- Zone TO → shot against % (by zone)
- Slot-drive conversion (→ shot / SC / goal)
- DZ retrieval → controlled exit %
- Failed entries / failed exits — overall, by lane (L/M/R), by type (dump/controlled/…)
- Entry denials + forced failed exits (opp side)
- Score-state splits (tied / leading / trailing)
- Forecheck pressure composite (0–100)

## InStat flat skater aliases (wired on ingest / re-enrich)

| Alias | Gear source |
|-------|-------------|
| `carry_in_pct` | EN+ENP / (EN+ENP+END) |
| `battles_engaged` | BRS (volume; win% needs action PBP) |
| `entries_stickhandle` / `entries_pass` / `entries_dump` | EN / ENP / END |
| `dump_ins` / `dump_outs` | DI / DO |
| `takeaways_oz` / `takeaways_dz` | TA (OZ) / TA (DZ) |
| `oz_recoveries` / `dz_recoveries` | OZRT / DZRT |
| `loose_puck_recoveries` | LPR |
| `failed_attacks` | FA |
| `forecheck_recoveries_proxy` | TA (OZ) or OZRT |

## Goalie — Last Line of Defense (automated via hub ingest)

Full hub fields including GSAx, danger, rebound, EV/PP/SH, Edge, InStat charted posture when present.

## Daily automation

**Primary:** `nhl-goalie-hub` → `.github/workflows/daily-metrics-warehouse.yml`  
Cron `20 4,16 * * *` UTC. Uses `INSTAT_*` / `HUDL_*` secrets.
