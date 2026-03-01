import requests
import json
import time

def scrape_vegas_odds():
    """Scrapes NHL moneylines from a public odds aggregator."""
    # We use Action Network's public feed as it has no auth and provides consensus
    url = "https://api.actionnetwork.com/web/v1/scoreboard/nhl"
    
    odds_data = {}
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        
        games = data.get('games', [])
        for game in games:
            away = game.get('teams', [])[0].get('abbr')
            home = game.get('teams', [])[1].get('abbr')
            
            # They use standard abbreviations thankfully
            if not away or not home:
                continue
                
            odds = game.get('odds', [])
            if not odds:
                continue
                
            # Grab consensus moneyline
            consensus = next((o for o in odds if o.get('book_id') == 15), None) # 15 is often consensus/DraftKings
            if not consensus:
                consensus = odds[0] # Fallback to first available
                
            away_ml = consensus.get('ml_away')
            home_ml = consensus.get('ml_home')
            
            if not away_ml or not home_ml:
                continue
                
            def to_implied(odds):
                o = float(odds)
                if o > 0:
                    return 100 / (o + 100)
                else:
                    return -o / (-o + 100)
                    
            away_prob = to_implied(away_ml)
            home_prob = to_implied(home_ml)
            
            # Remove vig
            total_prob = away_prob + home_prob
            away_true = away_prob / total_prob
            home_true = home_prob / total_prob
            
            odds_data[f"{away}_vs_{home}"] = {
                'away_prob': away_true,
                'home_prob': home_true,
                'away_american': away_ml,
                'home_american': home_ml,
                'timestamp': time.time(),
                'provider': 'ActionNetwork'
            }
            
    except Exception as e:
        print(f"Error scraping odds: {e}")
        
    return odds_data

if __name__ == '__main__':
    odds = scrape_vegas_odds()
    print(json.dumps(odds, indent=2))
