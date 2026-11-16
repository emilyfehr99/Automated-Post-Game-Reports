#!/usr/bin/env python3
"""
Unified Hockey Data & Analytics Engine (Pipelines Runner)
Consolidates Team, Season, Skater, Goalie, Prospect, and PWHL workflows
into a single orchestrated, dependency-driven pipeline.
"""

import os
import sys
import json
import time
import argparse
import subprocess
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Locations of sibling workspaces if running in unified local environment
GOALIE_HUB_DIR = Path(os.getenv("GOALIE_HUB_ROOT", str(BASE_DIR / "nhl-goalie-hub")))
if not GOALIE_HUB_DIR.exists():
    candidate = BASE_DIR.parent / "nhl-goalie-hub"
    if candidate.exists():
        GOALIE_HUB_DIR = candidate

SCRAPING_DIR = Path(os.getenv("AUTOMATED_SCRAPING_ROOT", str(BASE_DIR / "automated-scraping")))
if not SCRAPING_DIR.exists():
    candidate = BASE_DIR.parent / "automated-scraping"
    if candidate.exists():
        SCRAPING_DIR = candidate


class PipelineLogger:
    @staticmethod
    def header(title: str):
        border = "=" * 70
        print(f"\n{border}\n🏒  {title.upper()}\n{border}", flush=True)

    @staticmethod
    def stage(num: int, title: str):
        print(f"\n▶ [Stage {num}] {title}", flush=True)

    @staticmethod
    def success(msg: str):
        print(f"  ✓ {msg}", flush=True)

    @staticmethod
    def warn(msg: str):
        print(f"  ⚠️ {msg}", flush=True)

    @staticmethod
    def error(msg: str):
        print(f"  ❌ {msg}", flush=True)


class UnifiedHockeyEngine:
    def __init__(self, mode: str = "all", dry_run: bool = False, game_id: str = None):
        self.mode = mode
        self.dry_run = dry_run
        self.game_id = game_id
        self.start_time = time.time()
        self.summary = {
            "mode": mode,
            "dry_run": dry_run,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "stages_executed": [],
            "completed_games": [],
            "goalie_cards_posted": [],
            "pwhl_status": "skipped",
            "prospects_status": "skipped",
            "warehouse_status": "skipped"
        }

    def run_subcommand(self, cmd: list, cwd: Path = None, timeout: int = 600, env: dict = None) -> bool:
        cwd = cwd or BASE_DIR
        try:
            res = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout, env=env)
            if res.returncode == 0:
                return True
            else:
                PipelineLogger.warn(f"Command {' '.join(cmd[:3])}... returned exit code {res.returncode}")
                if res.stderr:
                    for line in res.stderr.strip().splitlines()[-3:]:
                        print(f"     [err] {line}")
                return False
        except subprocess.TimeoutExpired:
            PipelineLogger.error(f"Command timed out ({timeout}s): {' '.join(cmd[:3])}")
            return False
        except Exception as e:
            PipelineLogger.error(f"Execution error: {e}")
            return False

    def stage_1_live_games_and_reports(self) -> list[str]:
        """Runs the NHL Game Monitor and generates Postgame Reports & Team Metrics."""
        PipelineLogger.stage(1, "Live Games Monitor & Postgame Reports")
        completed_games = []

        try:
            from github_actions_runner import GitHubActionsRunner
            runner = GitHubActionsRunner()

            games = runner.get_todays_games()
            for game in games:
                gid = str(game.get("id"))
                state = game.get("gameState", "")
                if state in ("FINAL", "OFF") and gid not in runner.processed_games:
                    completed_games.append(gid)

            PipelineLogger.success(f"Found {len(games)} games checked ({len(completed_games)} newly completed to process)")

            if not self.dry_run:
                runner.run()
            else:
                PipelineLogger.success(f"[DRY-RUN] Would process completed games: {completed_games}")

            self.summary["completed_games"] = completed_games
            self.summary["stages_executed"].append("stage_1_reports")
        except Exception as e:
            PipelineLogger.error(f"Stage 1 encountered error: {e}")

        return completed_games

    def stage_2_goalie_cards(self, game_ids: list[str]):
        """Generates & Posts InStat Goalie Cards using the zero-overflow 2x Retina generator."""
        PipelineLogger.stage(2, "InStat Goalie Cards Generation & Distribution")

        tool_script = GOALIE_HUB_DIR / "tools" / "auto_post_instat_goalie_cards.py"
        if not tool_script.exists():
            PipelineLogger.warn(f"Goalie card tool not found at {tool_script}; skipping")
            return

        cmd = [sys.executable, str(tool_script)]
        if self.dry_run:
            cmd.append("--dry-run")

        if game_ids:
            for gid in game_ids:
                print(f"  🎨 Generating goalie cards for Game {gid}...")
                run_cmd = cmd + ["--game", str(gid)]
                self.run_subcommand(run_cmd, cwd=GOALIE_HUB_DIR, timeout=240)
        else:
            print("  🎨 Checking for recent unposted goalie cards...")
            run_cmd = cmd + ["--days", "2", "--max-posts", "3"]
            self.run_subcommand(run_cmd, cwd=GOALIE_HUB_DIR, timeout=300)

        self.summary["stages_executed"].append("stage_2_goalie_cards")

    def stage_3_daily_predictions(self):
        """Runs the Starting Goalie Consensus & Game Outcome Predictions."""
        PipelineLogger.stage(3, "Daily NHL Predictions & Starting Goalies")

        pred_script = BASE_DIR / "daily_prediction_notifier.py"
        if pred_script.exists():
            print("  🔮 Executing starting goalies consensus and match predictions...")
            cmd = [sys.executable, str(pred_script)]
            if self.dry_run:
                cmd.append("--dry-run")
            success = self.run_subcommand(cmd, timeout=360)
            if success:
                PipelineLogger.success("Daily predictions calculated & dispatched")
                self.summary["stages_executed"].append("stage_3_predictions")
        else:
            PipelineLogger.warn(f"Predictions script not found at {pred_script}")

    def stage_4_pwhl_sync(self):
        """Syncs PWHL player vitals, game logs, and action photo index."""
        PipelineLogger.stage(4, "PWHL Data & Action Store Sync")

        if not SCRAPING_DIR.exists():
            PipelineLogger.warn(f"automated-scraping not found at {SCRAPING_DIR}; skipping PWHL")
            return

        pwhl_script = SCRAPING_DIR / "scripts" / "refresh_pwhl_store_metrics.py"
        if pwhl_script.exists():
            print("  🏒 Refreshing PWHL store vitals and metrics...")
            success = self.run_subcommand([sys.executable, str(pwhl_script)], cwd=SCRAPING_DIR, timeout=300)
            if success:
                PipelineLogger.success("PWHL store updated")
                self.summary["pwhl_status"] = "success"
                self.summary["stages_executed"].append("stage_4_pwhl")
        else:
            PipelineLogger.warn(f"PWHL script not found at {pwhl_script}")

    def stage_5_prospects_sync(self):
        """Scrapes and compiles CHL, NCAA, and European prospect feeds."""
        PipelineLogger.stage(5, "Prospect Feeds & Draft Ranking Sync")

        if not SCRAPING_DIR.exists():
            PipelineLogger.warn(f"automated-scraping not found at {SCRAPING_DIR}; skipping Prospects")
            return

        prospect_script = SCRAPING_DIR / "generate_prospects.py"
        if prospect_script.exists():
            print("  ⭐ Generating prospect cards and tracking logs...")
            success = self.run_subcommand([sys.executable, str(prospect_script)], cwd=SCRAPING_DIR, timeout=400)
            if success:
                PipelineLogger.success("Prospects dataset updated")
                self.summary["prospects_status"] = "success"
                self.summary["stages_executed"].append("stage_5_prospects")
        else:
            PipelineLogger.warn(f"Prospects script not found at {prospect_script}")

    def stage_6_metrics_warehouse(self):
        """Aggregates all modules into the curated Metrics Warehouse."""
        PipelineLogger.stage(6, "Unified Metrics Warehouse Consolidation")

        wh_script = GOALIE_HUB_DIR / "metrics-warehouse" / "pipelines" / "daily_refresh.py"
        if not wh_script.exists():
            wh_script = GOALIE_HUB_DIR / "metrics-warehouse" / "pipelines" / "build_warehouse.py"

        if wh_script.exists():
            print("  🏛️ Compiling curated warehouse (teams + skaters + goalies + microstats)...")
            env = os.environ.copy()
            env["METRICS_WAREHOUSE_ROOT"] = str(GOALIE_HUB_DIR / "metrics-warehouse")
            env["APGR_ROOT"] = str(BASE_DIR)
            env["LLD_ROOT"] = str(GOALIE_HUB_DIR)
            env["AUTOMATED_SCRAPING_ROOT"] = str(SCRAPING_DIR)

            success = self.run_subcommand([sys.executable, str(wh_script)], cwd=GOALIE_HUB_DIR, timeout=600, env=env)
            if success:
                PipelineLogger.success("Metrics Warehouse successfully refreshed & curated")
                self.summary["warehouse_status"] = "success"
                self.summary["stages_executed"].append("stage_6_warehouse")
        else:
            PipelineLogger.warn("Metrics warehouse pipeline script not found")

    def run(self):
        PipelineLogger.header(f"Unified Hockey Pipeline [Mode: {self.mode}]")

        active_games = []

        if self.mode in ("all", "games", "cards"):
            active_games = self.stage_1_live_games_and_reports()
            self.stage_2_goalie_cards(active_games)

        if self.mode in ("all", "predictions"):
            self.stage_3_daily_predictions()

        if self.mode in ("all", "pwhl"):
            self.stage_4_pwhl_sync()

        if self.mode in ("all", "prospects"):
            self.stage_5_prospects_sync()

        if self.mode in ("all", "warehouse"):
            self.stage_6_metrics_warehouse()

        elapsed = time.time() - self.start_time
        self.summary["elapsed_seconds"] = round(elapsed, 2)
        PipelineLogger.header(f"Pipeline Completed in {elapsed:.1f}s")
        print(json.dumps(self.summary, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Unified Hockey Data & Analytics Engine")
    parser.add_argument(
        "--mode",
        choices=["all", "games", "cards", "predictions", "pwhl", "prospects", "warehouse"],
        default="all",
        help="Pipeline execution scope (default: all)"
    )
    parser.add_argument("--dry-run", action="store_true", help="Run without posting to social channels")
    parser.add_argument("--game-id", type=str, default=None, help="Specific NHL Game ID to target")
    args = parser.parse_args()

    engine = UnifiedHockeyEngine(mode=args.mode, dry_run=args.dry_run, game_id=args.game_id)
    engine.run()


if __name__ == "__main__":
    main()
