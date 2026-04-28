import sys, os
sys.path.append('scrapers')
from rotowire_scraper import RotoWireScraper

def check_rotowire():
    scraper = RotoWireScraper()
    data = scraper.scrape_daily_data()
    games = data.get('games', [])
    print(f"RotoWire Games Found: {len(games)}")
    for g in games:
        print(f"{g['away_team']} @ {g['home_team']}")

if __name__ == "__main__":
    check_rotowire()
