# Metrics Warehouse (personal)

Team + skater + goalie metric store for private use.

## Scheduled run (source of truth)

GitHub Actions on **nhl-goalie-hub**: `.github/workflows/daily-metrics-warehouse.yml`

- Cron `20 4,16 * * *` UTC (+ workflow_dispatch)
- InStat via same secrets as goalie hub (`INSTAT_*`, `HUDL_*`, dedicated account)
- Writes `metrics-warehouse/curated/*` and publishes to APGR `data/metrics_warehouse/`

## Local / APGR hook

```bash
python3 pipelines/daily_refresh.py
```

`daily_refresh` runs live InStat when auth is present (JWT env, auth.json, or header cache). It does **not** skip InStat just because `CI=true`.

Vendored copies: `nhl-goalie-hub/metrics-warehouse/`, `automated-post-game-reports/metrics-warehouse/`.

See `docs/METRIC_CATALOG.md`.
