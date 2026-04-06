#!/usr/bin/env python3
"""
RotoWire NHL Data Scraper
Extracts daily lineups, injuries, starting goalies, and betting odds
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
from typing import Dict, List, Optional

class RotoWireScraper:
    def __init__(self):
        self.base_url = "https://www.rotowire.com/hockey/nhl-lineups.php"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def scrape_daily_data(self) -> Dict:
        """Scrape all daily NHL data from RotoWire"""
        try:
            response = self.session.get(self.base_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            games = []
            
            # Find all game cards (RotoWire typically uses lineup__box or similar)
            game_cards = soup.find_all('div', class_=['lineup__box', 'is-nhl'])
            
            if not game_cards:
                # Try alternative selectors
                game_cards = soup.find_all('div', attrs={'data-sport': 'NHL'})
            
            seen_matchups = set()
            for card in game_cards:
                game_data = self._parse_game_card(card)
                if game_data:
                    # Deduplicate by matchup
                    matchup = f"{game_data['away_team']}@{game_data['home_team']}"
                    if matchup not in seen_matchups:
                        games.append(game_data)
                        seen_matchups.add(matchup)
            
            return {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'games': games,
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error scraping RotoWire: {e}")
            return {'date': datetime.now().strftime('%Y-%m-%d'), 'games': [], 'error': str(e)}
    
    def _parse_game_card(self, card) -> Optional[Dict]:
        """Parse a single game card to extract all relevant data"""
        try:
            game_data = {}
            
            # Extract team abbreviations
            teams = card.find_all('div', class_='lineup__abbr')
            if len(teams) >= 2:
                game_data['away_team'] = teams[0].text.strip()
                game_data['home_team'] = teams[1].text.strip()
            
            # Extract team records
            records = card.find_all('span', class_='lineup__wl')
            if len(records) >= 2:
                game_data['away_record'] = records[0].text.strip()
                game_data['home_record'] = records[1].text.strip()
            
            # Extract starting goalies from lineup__player-highlight
            goalie_sections = card.find_all('div', class_='lineup__player-highlight-name')
            if len(goalie_sections) >= 2:
                away_goalie = goalie_sections[0].find('a')
                home_goalie = goalie_sections[1].find('a')
                game_data['away_goalie'] = away_goalie.text.strip() if away_goalie else 'TBD'
                game_data['home_goalie'] = home_goalie.text.strip() if home_goalie else 'TBD'
                
                # Check if goalies are confirmed
                confirmed_status = card.find_all('div', class_='is-confirmed')
                game_data['away_goalie_confirmed'] = len(confirmed_status) > 0
                game_data['home_goalie_confirmed'] = len(confirmed_status) > 1
            
            # Extract betting odds (usually in lineup__odds section)
            odds_section = card.find('div', class_='lineup__odds')
            if odds_section:
                game_data['odds'] = self._parse_odds(odds_section)
            
            # Extract injuries from lineup__injuries
            injury_section = card.find('div', class_='lineup__injuries')
            if injury_section:
                game_data['injuries'] = self._parse_injuries(injury_section)
            
            # Extract game time
            time_elem = card.find('div', class_='lineup__time')
            if time_elem:
                game_data['game_time'] = time_elem.text.strip()
            
            # Extract lineups
            lineup_lists = card.find_all('ul', class_='lineup__list')
            if len(lineup_lists) >= 2:
                game_data['away_lineup'] = self._parse_lineup(lineup_lists[0])
                game_data['home_lineup'] = self._parse_lineup(lineup_lists[1])
            
            return game_data if 'away_team' in game_data and 'home_team' in game_data else None
            
        except Exception as e:
            print(f"Error parsing game card: {e}")
            return None
    
    def _parse_lineup(self, lineup_list) -> Dict:
        """Parse a team's lineup from the lineup list"""
        lineup = {
            'forwards': [],
            'defense': [],
            'power_play_1': [],
            'power_play_2': []
        }
        
        try:
            current_section = None
            players = lineup_list.find_all('li', class_='lineup__player')
            titles = lineup_list.find_all('li', class_='lineup__title')
            
            # Parse power play units
            for title in titles:
                title_text = title.text.strip()
                if 'POWER PLAY #1' in title_text:
                    # Get next 5 players after this title
                    pp1_players = []
                    next_elem = title.find_next_sibling('li', class_='lineup__player')
                    while next_elem and len(pp1_players) < 5:
                        player_link = next_elem.find('a')
                        pos_elem = next_elem.find('div', class_='lineup__pos')
                        if player_link:
                            pp1_players.append({
                                'name': player_link.text.strip(),
                                'position': pos_elem.text.strip() if pos_elem else 'Unknown'
                            })
                        next_elem = next_elem.find_next_sibling('li', class_='lineup__player')
                    lineup['power_play_1'] = pp1_players
                    
                elif 'POWER PLAY #2' in title_text:
                    # Get next 5 players
                    pp2_players = []
                    next_elem = title.find_next_sibling('li', class_='lineup__player')
                    while next_elem and len(pp2_players) < 5:
                        player_link = next_elem.find('a')
                        pos_elem = next_elem.find('div', class_='lineup__pos')
                        if player_link:
                            pp2_players.append({
                                'name': player_link.text.strip(),
                                'position': pos_elem.text.strip() if pos_elem else 'Unknown'
                            })
                        next_elem = next_elem.find_next_sibling('li', class_='lineup__player')
                    lineup['power_play_2'] = pp2_players
            
            # Separate forwards and defense from all players
            for player in players:
                player_link = player.find('a')
                pos_elem = player.find('div', class_='lineup__pos')
                if player_link and pos_elem:
                    position = pos_elem.text.strip()
                    player_data = {
                        'name': player_link.text.strip(),
                        'position': position
                    }
                    
                    if position in ['C', 'LW', 'RW', 'W']:
                        lineup['forwards'].append(player_data)
                    elif position in ['LD', 'RD', 'D']:
                        lineup['defense'].append(player_data)
                        
        except Exception as e:
            print(f"Error parsing lineup: {e}")
        
        return lineup
    
    def _parse_odds(self, odds_section) -> Dict:
        """Parse betting odds from the odds section"""
        odds = {}
        try:
            # RotoWire format: "LINE TBL -250" and "O/U 5.5 Goals"
            odds_items = odds_section.find_all('div', class_='lineup__odds-item')
            
            for item in odds_items:
                text = item.text.strip()
                if 'LINE' in text:
                    # Extract moneyline (e.g., "LINE TBL -250")
                    parts = text.replace('LINE', '').strip().split()
                    if len(parts) >= 2:
                        odds['favorite_team'] = parts[0]
                        odds['moneyline'] = parts[1]
                elif 'O/U' in text or 'OVER/UNDER' in text:
                    # Extract total (e.g., "O/U 5.5 Goals")
                    parts = text.replace('O/U', '').replace('OVER/UNDER', '').replace('Goals', '').strip()
                    odds['total'] = parts
                
        except Exception as e:
            print(f"Error parsing odds: {e}")
        
        return odds
    
    def _parse_injuries(self, injury_section) -> List[Dict]:
        """Parse injury reports"""
        injuries = []
        try:
            # RotoWire uses lineup__inj class for injury items
            injury_items = injury_section.find_all('li', class_='lineup__inj')
            
            for item in injury_items:
                player_link = item.find('a')
                status_elem = item.find('span', class_='lineup__inj-status')
                
                if player_link:
                    injury = {
                        'player': player_link.text.strip(),
                        'status': status_elem.text.strip() if status_elem else 'Unknown',
                        'team': 'Unknown'  # Will be inferred from context
                    }
                    injuries.append(injury)
                    
        except Exception as e:
            print(f"Error parsing injuries: {e}")
        
        return injuries
    
    def get_game_by_teams(self, away_team: str, home_team: str) -> Optional[Dict]:
        """Get specific game data by team abbreviations"""
        data = self.scrape_daily_data()
        
        for game in data.get('games', []):
            if (game.get('away_team', '').upper() == away_team.upper() and 
                game.get('home_team', '').upper() == home_team.upper()):
                return game
        
        return None

if __name__ == "__main__":
    scraper = RotoWireScraper()
    data = scraper.scrape_daily_data()
    
    print(f"📊 RotoWire NHL Data - {data['date']}")
    print(f"Found {len(data.get('games', []))} games")
    
    for i, game in enumerate(data.get('games', []), 1):
        print(f"\n🏒 Game {i}: {game.get('away_team', 'N/A')} @ {game.get('home_team', 'N/A')}")
        print(f"   Goalies: {game.get('away_goalie', 'TBD')} vs {game.get('home_goalie', 'TBD')}")
        if 'odds' in game:
            print(f"   Odds: {game['odds']}")
        if 'injuries' in game and game['injuries']:
            print(f"   Injuries: {len(game['injuries'])} players")
