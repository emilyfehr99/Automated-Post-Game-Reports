#!/usr/bin/env python3
"""
Multi-Source NHL Starting Goalie Consensus Engine
Aggregates starting goalie announcements from:
1. Daily Faceoff (DFO - Primary confirmation & beat reporter source)
2. RotoWire (Lineups and confirmation flags)
3. NHL Official Web API (GameCenter roster confirmation)
"""
from typing import Dict, List, Optional, Any
import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

TEAM_NAME_TO_ABBR = {
    'Anaheim Ducks': 'ANA', 'Arizona Coyotes': 'ARI', 'Boston Bruins': 'BOS',
    'Buffalo Sabres': 'BUF', 'Calgary Flames': 'CGY', 'Carolina Hurricanes': 'CAR',
    'Chicago Blackhawks': 'CHI', 'Colorado Avalanche': 'COL', 'Columbus Blue Jackets': 'CBJ',
    'Dallas Stars': 'DAL', 'Detroit Red Wings': 'DET', 'Edmonton Oilers': 'EDM',
    'Florida Panthers': 'FLA', 'Los Angeles Kings': 'LAK', 'Minnesota Wild': 'MIN',
    'Montreal Canadiens': 'MTL', 'Montréal Canadiens': 'MTL', 'Nashville Predators': 'NSH',
    'New Jersey Devils': 'NJD', 'New York Islanders': 'NYI', 'New York Rangers': 'NYR',
    'Ottawa Senators': 'OTT', 'Philadelphia Flyers': 'PHI', 'Pittsburgh Penguins': 'PIT',
    'San Jose Sharks': 'SJS', 'Seattle Kraken': 'SEA', 'St. Louis Blues': 'STL',
    'Tampa Bay Lightning': 'TBL', 'Toronto Maple Leafs': 'TOR', 'Utah Hockey Club': 'UTA',
    'Utah Mammoth': 'UTA', 'Vancouver Canucks': 'VAN', 'Vegas Golden Knights': 'VGK',
    'Washington Capitals': 'WSH', 'Winnipeg Jets': 'WPG'
}

# Slugs to ABBR for Daily Faceoff
TEAM_SLUG_TO_ABBR = {
    'anaheim-ducks': 'ANA', 'boston-bruins': 'BOS', 'buffalo-sabres': 'BUF',
    'calgary-flames': 'CGY', 'carolina-hurricanes': 'CAR', 'chicago-blackhawks': 'CHI',
    'colorado-avalanche': 'COL', 'columbus-blue-jackets': 'CBJ', 'dallas-stars': 'DAL',
    'detroit-red-wings': 'DET', 'edmonton-oilers': 'EDM', 'florida-panthers': 'FLA',
    'los-angeles-kings': 'LAK', 'minnesota-wild': 'MIN', 'montreal-canadiens': 'MTL',
    'nashville-predators': 'NSH', 'new-jersey-devils': 'NJD', 'new-york-islanders': 'NYI',
    'new-york-rangers': 'NYR', 'ottawa-senators': 'OTT', 'philadelphia-flyers': 'PHI',
    'pittsburgh-penguins': 'PIT', 'san-jose-sharks': 'SJS', 'seattle-kraken': 'SEA',
    'st-louis-blues': 'STL', 'tampa-bay-lightning': 'TBL', 'toronto-maple-leafs': 'TOR',
    'utah-hockey-club': 'UTA', 'vancouver-canucks': 'VAN', 'vegas-golden-knights': 'VGK',
    'washington-capitals': 'WSH', 'winnipeg-jets': 'WPG'
}

class StartingGoaliesScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

    def scrape_daily_faceoff(self) -> Dict[str, Dict[str, Any]]:
        """Scrape Daily Faceoff starting goalies via Next.js structured data."""
        results = {}
        try:
            url = 'https://www.dailyfaceoff.com/starting-goalies'
            resp = self.session.get(url, timeout=10)
            if resp.status_code != 200:
                return results

            soup = BeautifulSoup(resp.text, 'html.parser')
            next_data = soup.find('script', id='__NEXT_DATA__')
            if not next_data:
                return results

            payload = json.loads(next_data.string)
            games = payload.get('props', {}).get('pageProps', {}).get('data', [])

            for g in games:
                away_slug = g.get('awayTeamSlug', '')
                home_slug = g.get('homeTeamSlug', '')
                away_abbr = TEAM_SLUG_TO_ABBR.get(away_slug) or TEAM_NAME_TO_ABBR.get(g.get('awayTeamName', ''))
                home_abbr = TEAM_SLUG_TO_ABBR.get(home_slug) or TEAM_NAME_TO_ABBR.get(g.get('homeTeamName', ''))

                if not away_abbr or not home_abbr:
                    continue

                away_goalie = g.get('awayGoalieName') or 'TBD'
                home_goalie = g.get('homeGoalieName') or 'TBD'
                away_status = (g.get('awayNewsStrengthName') or 'Unconfirmed').strip()
                home_status = (g.get('homeNewsStrengthName') or 'Unconfirmed').strip()
                away_confirmed = 'confirm' in away_status.lower()
                home_confirmed = 'confirm' in home_status.lower()

                matchup_key = f"{away_abbr}@{home_abbr}"
                results[matchup_key] = {
                    'away_team': away_abbr,
                    'home_team': home_abbr,
                    'away_goalie': away_goalie,
                    'home_goalie': home_goalie,
                    'away_goalie_confirmed': away_confirmed,
                    'home_goalie_confirmed': home_confirmed,
                    'away_status_text': away_status,
                    'home_status_text': home_status,
                    'away_source': g.get('awayNewsSourceName', ''),
                    'home_source': g.get('homeNewsSourceName', ''),
                    'source': 'DailyFaceoff'
                }
        except Exception as e:
            print(f"⚠️ Daily Faceoff scrape error: {e}")
        return results

    def scrape_rotowire(self) -> Dict[str, Dict[str, Any]]:
        """Scrape RotoWire lineups for starting goalies."""
        results = {}
        try:
            try:
                from scrapers.rotowire_scraper import RotoWireScraper
            except ImportError:
                from rotowire_scraper import RotoWireScraper
            rw = RotoWireScraper()
            data = rw.scrape_daily_data()
            for g in data.get('games', []):
                away_abbr = g.get('away_team')
                home_abbr = g.get('home_team')
                if away_abbr and home_abbr:
                    key = f"{away_abbr}@{home_abbr}"
                    results[key] = {
                        'away_team': away_abbr,
                        'home_team': home_abbr,
                        'away_goalie': g.get('away_goalie', 'TBD'),
                        'home_goalie': g.get('home_goalie', 'TBD'),
                        'away_goalie_confirmed': bool(g.get('away_goalie_confirmed')),
                        'home_goalie_confirmed': bool(g.get('home_goalie_confirmed')),
                        'away_lineup': g.get('away_lineup'),
                        'home_lineup': g.get('home_lineup'),
                        'injuries': g.get('injuries', []),
                        'odds': g.get('odds'),
                        'source': 'RotoWire'
                    }
        except Exception as e:
            print(f"⚠️ RotoWire scrape error: {e}")
        return results

    def get_consensus_goalies(self) -> List[Dict[str, Any]]:
        """
        Merge Daily Faceoff + RotoWire into a unified, highest-confidence consensus.
        """
        dfo_data = self.scrape_daily_faceoff()
        rw_data = self.scrape_rotowire()

        all_keys = list(dict.fromkeys(list(dfo_data.keys()) + list(rw_data.keys())))
        consensus_games = []

        for key in all_keys:
            dfo = dfo_data.get(key, {})
            rw = rw_data.get(key, {})

            away_team = dfo.get('away_team') or rw.get('away_team')
            home_team = dfo.get('home_team') or rw.get('home_team')

            # Away Goalie resolution
            away_g = dfo.get('away_goalie')
            if not away_g or away_g == 'TBD':
                away_g = rw.get('away_goalie', 'TBD')

            away_conf = bool(dfo.get('away_goalie_confirmed') or rw.get('away_goalie_confirmed'))

            # Home Goalie resolution
            home_g = dfo.get('home_goalie')
            if not home_g or home_g == 'TBD':
                home_g = rw.get('home_goalie', 'TBD')

            home_conf = bool(dfo.get('home_goalie_confirmed') or rw.get('home_goalie_confirmed'))

            game_obj = {
                'away_team': away_team,
                'home_team': home_team,
                'away_goalie': away_g,
                'home_goalie': home_g,
                'away_goalie_confirmed': away_conf,
                'home_goalie_confirmed': home_conf,
                'away_status_text': dfo.get('away_status_text') or ('Confirmed' if away_conf else 'Projected'),
                'home_status_text': dfo.get('home_status_text') or ('Confirmed' if home_conf else 'Projected'),
                'away_source': dfo.get('away_source', ''),
                'home_source': dfo.get('home_source', ''),
                'away_lineup': rw.get('away_lineup'),
                'home_lineup': rw.get('home_lineup'),
                'injuries': rw.get('injuries', []),
                'odds': rw.get('odds')
            }
            consensus_games.append(game_obj)

        return consensus_games

if __name__ == '__main__':
    scraper = StartingGoaliesScraper()
    games = scraper.get_consensus_goalies()
    print(f"✅ Found {len(games)} consensus matchups:")
    for g in games:
        print(f"  {g['away_team']} ({g['away_goalie']} [{'CONFIRMED' if g['away_goalie_confirmed'] else 'EXPECTED'}]) @ {g['home_team']} ({g['home_goalie']} [{'CONFIRMED' if g['home_goalie_confirmed'] else 'EXPECTED'}])")
