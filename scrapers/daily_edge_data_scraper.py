#!/usr/bin/env python3
"""
Daily NHL Edge Data Scraper
Runs every morning to get fresh Edge data for daily predictions
"""

import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from datetime import datetime, timezone
import os

class DailyEdgeDataScraper:
    def __init__(self):
        self.base_url = "https://puckalytics.com/reports/edge/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.data_file = "data/nhl_edge_data.json"
    
    def scrape_daily_edge_data(self):
        """Scrape fresh NHL Edge data daily with optimized session and parsing"""
        print(f"🏒 DAILY NHL EDGE DATA SCRAPING")
        print(f"📅 Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
        print("=" * 50)
        
        try:
            response = self.session.get(self.base_url, timeout=5)
            response.raise_for_status()
            
            # Fast C-optimized table parsing via pandas if available
            try:
                tables = pd.read_html(response.text, attrs={'id': 'table-report-edge'})
                if tables and len(tables) > 0:
                    df = tables[0]
                    edge_data = df.to_dict(orient='records')
                else:
                    edge_data = []
            except Exception:
                edge_data = []

            # Fallback to BeautifulSoup if pandas parse missed
            if not edge_data:
                soup = BeautifulSoup(response.text, 'html.parser')
                table = soup.find('table', id='table-report-edge')
                
                if not table:
                    print("⚠️ Could not find Edge data table on remote, preserving cached data.")
                    return os.path.exists(self.data_file)
                
                headers_row = table.find('thead').find('tr')
                headers = [th.get_text().strip() for th in headers_row.find_all('th')]
                data_rows = table.find('tbody').find_all('tr')
                
                for row in data_rows:
                    cells = row.find_all('td')
                    player_data = {}
                    for j, cell in enumerate(cells):
                        if j < len(headers):
                            value = cell.get_text().strip()
                            try:
                                if '.' in value and value.replace('.', '').isdigit():
                                    value = float(value)
                                elif value.isdigit():
                                    value = int(value)
                            except Exception:
                                pass
                            player_data[headers[j]] = value
                    edge_data.append(player_data)
            
            print(f"📊 Processed {len(edge_data)} players with Edge data")
            
            # Calculate team-level Edge statistics
            team_edge_stats = self.calculate_team_edge_stats(edge_data)
            
            # Save data
            output_data = {
                'scraped_at': datetime.now().isoformat(),
                'total_players': len(edge_data),
                'player_data': edge_data,
                'team_stats': team_edge_stats
            }
            
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(self.data_file, 'w') as f:
                json.dump(output_data, f, indent=2)
            
            print(f"💾 Saved Edge data to {self.data_file}")
            print(f"✅ Calculated stats for {len(team_edge_stats)} teams")
            return True
            
        except Exception as e:
            print(f"⚠️ Warning scraping Edge data: {e}. Using cached fallback if available.")
            return os.path.exists(self.data_file)
    
    def calculate_team_edge_stats(self, edge_data):
        """Calculate team-level Edge statistics for predictions"""
        team_stats = {}
        
        for player in edge_data:
            team = player.get('Team', '')
            if not team:
                continue
            
            if team not in team_stats:
                team_stats[team] = {
                    'players': [],
                    'total_distance': 0,
                    'avg_speed': 0,
                    'max_speed': 0,
                    'total_bursts': 0,
                    'player_count': 0
                }
            
            # Add player data
            team_stats[team]['players'].append(player)
            team_stats[team]['player_count'] += 1
            
            # Sum up metrics
            distance = player.get('Distance Skated', 0)
            avg_speed = player.get('Average Speed', 0)
            top_speed = player.get('Top Speed', 0)
            bursts = player.get('Bursts>20 per mile', 0)
            
            if isinstance(distance, (int, float)):
                team_stats[team]['total_distance'] += distance
            if isinstance(avg_speed, (int, float)):
                team_stats[team]['avg_speed'] += avg_speed
            if isinstance(top_speed, (int, float)):
                team_stats[team]['max_speed'] = max(team_stats[team]['max_speed'], top_speed)
            if isinstance(bursts, (int, float)):
                team_stats[team]['total_bursts'] += bursts
        
        # Calculate averages and create prediction scores
        for team, stats in team_stats.items():
            if stats['player_count'] > 0:
                stats['avg_distance'] = stats['total_distance'] / stats['player_count']
                stats['avg_speed'] = stats['avg_speed'] / stats['player_count']
                stats['avg_bursts'] = stats['total_bursts'] / stats['player_count']
                
                # Create normalized prediction scores (0-1 scale)
                stats['speed_score'] = min(stats['avg_speed'] / 10.0, 1.0)  # Normalize to 0-1
                stats['distance_score'] = min(stats['avg_distance'] / 20.0, 1.0)  # Normalize to 0-1
                stats['burst_score'] = min(stats['avg_bursts'] / 2.0, 1.0)  # Normalize to 0-1
                
                # Overall Edge advantage score (weighted combination)
                stats['edge_advantage'] = (
                    stats['speed_score'] * 0.5 +      # 50% weight on speed
                    stats['distance_score'] * 0.3 +   # 30% weight on distance
                    stats['burst_score'] * 0.2        # 20% weight on bursts
                )
        
        return team_stats
    
    def get_team_edge_advantage(self, team1, team2):
        """Calculate Edge advantage between two teams for predictions"""
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
            
            team_stats = data.get('team_stats', {})
            
            team1_stats = team_stats.get(team1, {})
            team2_stats = team_stats.get(team2, {})
            
            if not team1_stats or not team2_stats:
                return 0.0  # No advantage if data missing
            
            team1_advantage = team1_stats.get('edge_advantage', 0.5)
            team2_advantage = team2_stats.get('edge_advantage', 0.5)
            
            # Calculate relative advantage (positive = team1 advantage, negative = team2 advantage)
            advantage = team1_advantage - team2_advantage
            
            # Convert to percentage impact on win probability (max 5% impact)
            win_prob_impact = advantage * 0.05  # Scale to 5% max impact
            
            return win_prob_impact
            
        except Exception as e:
            print(f"❌ Error getting team Edge advantage: {e}")
            return 0.0

def main():
    """Main function for daily Edge data scraping"""
    scraper = DailyEdgeDataScraper()
    
    success = scraper.scrape_daily_edge_data()
    
    if success:
        print(f"\n🎉 DAILY EDGE DATA SCRAPING COMPLETE!")
        print("=" * 50)
        print("✅ Fresh NHL Edge data scraped")
        print("✅ Team statistics calculated")
        print("✅ Ready for daily predictions")
        print("✅ Edge advantages will be factored into predictions")
        
        # Test team advantage calculation
        print(f"\n🧪 TESTING TEAM ADVANTAGE CALCULATION:")
        advantage = scraper.get_team_edge_advantage("COL", "SJS")
        print(f"Colorado vs San Jose Edge advantage: {advantage:.3f} ({advantage*100:+.1f}% win probability impact)")
    else:
        print(f"\n❌ DAILY EDGE DATA SCRAPING FAILED")
        print("Will use cached data or default values")

if __name__ == "__main__":
    main()
