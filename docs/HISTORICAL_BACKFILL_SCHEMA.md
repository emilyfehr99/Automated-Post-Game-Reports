# Historical backfill schema (multi-season post-game-report metrics)

Goal: store **regular-season** (gameType=2) metrics for multiple seasons using the same feature extraction logic as the automated post-game reports, so we can train “regular season → playoff success” models on rich microstats (GS, DZ shots, xG, HDC, NZT, etc.).

## Directory layout

All historical artifacts live under:

`automated-post-game-reports/data/historical/<SEASON>/`

Where `<SEASON>` is an 8-digit season string like `20222023`.

### Files

- **Raw cache** (optional but recommended for reproducibility)
  - `raw/gamecenter/<GAME_ID>.json`
    - JSON payload from `GET https://api-web.nhle.com/v1/gamecenter/<GAME_ID>/boxscore` and `/play-by-play` (combined).

- **Processed per-team-game rows** (append-only)
  - `team_game_rows.jsonl`
    - JSONL: one record per **team per game** (so 2 rows/game).
    - Contains the same metrics keys produced by `utils/generate_real_team_stats.py`’s `calculate_game_metrics()` (plus metadata like date, game_id, season, venue, opponent).

- **Processed summary aggregates** (overwrites on each rebuild)
  - `team_season_aggregate.json`
    - One object keyed by team abbrev with aggregate features (means/sums) over the season.
    - This is the primary “training table” for season-level playoff success modeling.

- **Bookkeeping**
  - `processed_game_ids.json`
    - `{"games": ["2022020001", ...]}` for incremental backfills.
  - `backfill_meta.json`
    - `{ "season": "...", "updated_at": "...", "source": "...", "notes": ... }`

## Why JSONL for per-game rows?

- Works well with Git commits (append-only, chunkable).
- Lets you backfill in slices (month/date range) without rewriting a huge file.
- You can later convert to Parquet if you want, but JSONL keeps dependencies minimal.

## Training target options

For “regular season → playoff success” you can label each team-season with:

- `won_cup` (1 per season)
- `made_final`, `made_conf_final`, `made_round2`, `made_playoffs`

These labels should be derived from `GET /v1/playoff-bracket/<YEAR_END>` for each season.

