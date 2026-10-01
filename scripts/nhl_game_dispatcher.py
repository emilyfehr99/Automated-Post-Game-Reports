"""
NHL Live Game Watcher & GitHub Actions Trigger
Monitors live NHL scores and dispatches a GitHub Action workflow run
as soon as any game transitions to FINAL or OFF.

Usage:
    python3 scripts/nhl_game_dispatcher.py
"""

import json
import os
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

# Repo info
REPO_OWNER = "emilyfehr99"
REPO_NAME = "Automated-Post-Game-Reports"
STATE_FILE = Path("data/dispatcher_state.json")
POLL_INTERVAL_LIVE = 45     # Poll every 45s when games are live/critical
POLL_INTERVAL_IDLE = 300    # Poll every 5m when no games are live


def get_live_scores():
    """Fetch live scores from NHL API"""
    url = "https://api-web.nhle.com/v1/score/now"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Error fetching NHL scores: {e}")
        return None


def load_notified_games():
    """Load IDs of games already triggered for dispatch"""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r") as f:
                data = json.load(f)
                return set(data.get("notified_games", []))
        except Exception:
            pass
    return set()


def save_notified_games(notified_games):
    """Save IDs of notified games"""
    try:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(STATE_FILE, "w") as f:
            json.dump({"notified_games": list(notified_games)}, f, indent=2)
    except Exception as e:
        print(f"⚠️ Could not save dispatcher state: {e}")


def trigger_github_dispatch(game_id, away, home):
    """Dispatch 'game-finished' event to GitHub Actions"""
    github_token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    
    # Try using gh CLI first if token is not explicitly in env
    try:
        import subprocess
        result = subprocess.run(
            [
                "gh", "api",
                f"repos/{REPO_OWNER}/{REPO_NAME}/dispatches",
                "--input", "-"
            ],
            input=json.dumps({"event_type": "game-finished"}).encode("utf-8"),
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"🚀 [DISPATCH SUCCESS] Triggered GitHub Action for {away} @ {home} (ID: {game_id}) via gh CLI")
            return True
    except Exception:
        pass

    # Fallback to direct HTTP request with GITHUB_TOKEN
    if not github_token:
        print("⚠️ No GitHub token or gh CLI found to send repository_dispatch.")
        return False

    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/dispatches"
    payload = json.dumps({"event_type": "game-finished"}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "NHL-Game-Dispatcher"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status in (200, 204):
                print(f"🚀 [DISPATCH SUCCESS] Triggered GitHub Action for {away} @ {home} (ID: {game_id})")
                return True
    except Exception as e:
        print(f"❌ Failed to dispatch event to GitHub: {e}")
    return False


def run_loop():
    print("=" * 60)
    print("🏒 NHL Game Dispatcher -> GitHub Actions")
    print(f"🎯 Target Repo: {REPO_OWNER}/{REPO_NAME}")
    print("=" * 60)

    notified_games = load_notified_games()

    while True:
        data = get_live_scores()
        has_live_games = False

        if data and "games" in data:
            games = data["games"]
            for game in games:
                game_id = str(game.get("id"))
                state = game.get("gameState", "UNKNOWN")
                away = game.get("awayTeam", {}).get("abbrev", "AWAY")
                home = game.get("homeTeam", {}).get("abbrev", "HOME")

                if state in ("LIVE", "CRIT"):
                    has_live_games = True

                if state in ("FINAL", "OFF") and game_id not in notified_games:
                    print(f"\n🔔 Game Finished: {away} @ {home} (ID: {game_id}) [State: {state}]")
                    if trigger_github_dispatch(game_id, away, home):
                        notified_games.add(game_id)
                        save_notified_games(notified_games)

        sleep_time = POLL_INTERVAL_LIVE if has_live_games else POLL_INTERVAL_IDLE
        time.sleep(sleep_time)


if __name__ == "__main__":
    run_loop()
