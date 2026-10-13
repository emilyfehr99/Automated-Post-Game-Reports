#!/usr/bin/env python3
"""
Daily NHL Edge Data Scraper
Runs every morning to get fresh Edge data for daily predictions
"""

import hashlib
import json
import os
from datetime import datetime, timezone, timedelta

import pandas as pd
import requests
from bs4 import BeautifulSoup


class DailyEdgeDataScraper:
    def __init__(self):
        self.base_url = "https://puckalytics.com/reports/edge/"
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.data_file = "data/nhl_edge_data.json"
        self.max_cache_age_hours = float(os.environ.get("EDGE_CACHE_MAX_HOURS", "6"))

    def _cache_is_fresh(self) -> bool:
        if os.environ.get("FORCE_EDGE_REFRESH", "").lower() in ("1", "true", "yes"):
            return False
        if not os.path.exists(self.data_file):
            return False
        try:
            with open(self.data_file, "r") as f:
                data = json.load(f)
            scraped_at = data.get("scraped_at")
            if not scraped_at:
                return False
            ts = datetime.fromisoformat(scraped_at)
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            age = datetime.now(timezone.utc) - ts.astimezone(timezone.utc)
            if age <= timedelta(hours=self.max_cache_age_hours) and data.get("team_stats"):
                print(
                    f"⚡ Edge cache fresh ({age.total_seconds()/3600:.1f}h old) — skipping scrape"
                )
                return True
        except Exception:
            return False
        return False

    def scrape_daily_edge_data(self):
        """Scrape fresh NHL Edge data daily with optimized session and parsing"""
        print("🏒 DAILY NHL EDGE DATA SCRAPING")
        print(f"📅 Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
        print("=" * 50)

        if self._cache_is_fresh():
            return True

        try:
            response = self.session.get(self.base_url, timeout=8)
            response.raise_for_status()
            body = response.content  # bytes for stable hashing
            content_hash = hashlib.sha256(body).hexdigest()

            # Skip rewrite if remote payload unchanged.
            if os.path.exists(self.data_file):
                try:
                    with open(self.data_file, "r") as f:
                        prev = json.load(f)
                    if prev.get("content_hash") == content_hash and prev.get("team_stats"):
                        prev["scraped_at"] = datetime.now(timezone.utc).isoformat()
                        with open(self.data_file, "w") as f:
                            json.dump(prev, f, separators=(",", ":"))
                        print("⚡ Remote Edge payload unchanged — refreshed scraped_at only")
                        return True
                except Exception:
                    pass

            text = response.text
            edge_data = []

            # Fast C-optimized table parsing via pandas if available
            try:
                tables = pd.read_html(text, attrs={"id": "table-report-edge"})
                if tables:
                    edge_data = tables[0].to_dict(orient="records")
            except Exception:
                edge_data = []

            # Fallback to BeautifulSoup if pandas parse missed (lxml if available)
            if not edge_data:
                try:
                    soup = BeautifulSoup(text, "lxml")
                except Exception:
                    soup = BeautifulSoup(text, "html.parser")
                table = soup.find("table", id="table-report-edge")

                if not table:
                    print("⚠️ Could not find Edge data table on remote, preserving cached data.")
                    return os.path.exists(self.data_file)

                headers_row = table.find("thead").find("tr")
                headers = [th.get_text().strip() for th in headers_row.find_all("th")]
                data_rows = table.find("tbody").find_all("tr")

                for row in data_rows:
                    cells = row.find_all("td")
                    player_data = {}
                    for j, cell in enumerate(cells):
                        if j < len(headers):
                            value = cell.get_text().strip()
                            try:
                                if "." in value and value.replace(".", "", 1).isdigit():
                                    value = float(value)
                                elif value.isdigit():
                                    value = int(value)
                            except Exception:
                                pass
                            player_data[headers[j]] = value
                    edge_data.append(player_data)

            print(f"📊 Processed {len(edge_data)} players with Edge data")

            team_edge_stats = self.calculate_team_edge_stats(edge_data)

            output_data = {
                "scraped_at": datetime.now(timezone.utc).isoformat(),
                "content_hash": content_hash,
                "total_players": len(edge_data),
                "player_data": edge_data,
                "team_stats": team_edge_stats,
            }

            os.makedirs(os.path.dirname(self.data_file) or ".", exist_ok=True)
            # Compact JSON — Edge files are large; indent=2 was pure write overhead.
            with open(self.data_file, "w") as f:
                json.dump(output_data, f, separators=(",", ":"))

            print(f"💾 Saved Edge data to {self.data_file}")
            print(f"✅ Calculated stats for {len(team_edge_stats)} teams")
            return True

        except Exception as e:
            print(f"⚠️ Warning scraping Edge data: {e}. Using cached fallback if available.")
            return os.path.exists(self.data_file)

    def calculate_team_edge_stats(self, edge_data):
        """Calculate team-level Edge statistics for predictions (aggregates only)."""
        team_stats = {}

        for player in edge_data:
            team = player.get("Team", "")
            if not team:
                continue

            if team not in team_stats:
                team_stats[team] = {
                    "total_distance": 0.0,
                    "avg_speed": 0.0,
                    "max_speed": 0.0,
                    "total_bursts": 0.0,
                    "player_count": 0,
                }

            stats = team_stats[team]
            stats["player_count"] += 1

            distance = player.get("Distance Skated", 0)
            avg_speed = player.get("Average Speed", 0)
            top_speed = player.get("Top Speed", 0)
            bursts = player.get("Bursts>20 per mile", 0)

            if isinstance(distance, (int, float)):
                stats["total_distance"] += distance
            if isinstance(avg_speed, (int, float)):
                stats["avg_speed"] += avg_speed
            if isinstance(top_speed, (int, float)):
                stats["max_speed"] = max(stats["max_speed"], top_speed)
            if isinstance(bursts, (int, float)):
                stats["total_bursts"] += bursts

        for stats in team_stats.values():
            n = stats["player_count"] or 1
            stats["avg_distance"] = stats["total_distance"] / n
            stats["avg_speed"] = stats["avg_speed"] / n
            stats["avg_bursts"] = stats["total_bursts"] / n
            stats["speed_score"] = min(stats["avg_speed"] / 10.0, 1.0)
            stats["distance_score"] = min(stats["avg_distance"] / 20.0, 1.0)
            stats["burst_score"] = min(stats["avg_bursts"] / 2.0, 1.0)
            stats["edge_advantage"] = (
                stats["speed_score"] * 0.5
                + stats["distance_score"] * 0.3
                + stats["burst_score"] * 0.2
            )

        return team_stats

    def get_team_edge_advantage(self, team1, team2):
        """Calculate Edge advantage between two teams for predictions"""
        try:
            with open(self.data_file, "r") as f:
                data = json.load(f)

            team_stats = data.get("team_stats", {})
            team1_stats = team_stats.get(team1, {})
            team2_stats = team_stats.get(team2, {})

            if not team1_stats or not team2_stats:
                return 0.0

            team1_advantage = team1_stats.get("edge_advantage", 0.5)
            team2_advantage = team2_stats.get("edge_advantage", 0.5)
            advantage = team1_advantage - team2_advantage
            return advantage * 0.05

        except Exception as e:
            print(f"❌ Error getting team Edge advantage: {e}")
            return 0.0


def main():
    """Main function for daily Edge data scraping"""
    scraper = DailyEdgeDataScraper()
    success = scraper.scrape_daily_edge_data()

    if success:
        print("\n🎉 DAILY EDGE DATA SCRAPING COMPLETE!")
        print("=" * 50)
        print("✅ Fresh NHL Edge data scraped")
        print("✅ Team statistics calculated")
        print("✅ Ready for daily predictions")
        advantage = scraper.get_team_edge_advantage("COL", "SJS")
        print(
            f"\n🧪 Colorado vs San Jose Edge advantage: {advantage:.3f} "
            f"({advantage*100:+.1f}% win probability impact)"
        )
    else:
        print("\n❌ DAILY EDGE DATA SCRAPING FAILED")
        print("Will use cached data or default values")


if __name__ == "__main__":
    main()
