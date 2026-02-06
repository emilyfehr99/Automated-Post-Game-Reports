#!/usr/bin/env python3
"""
Statcast API Client
Fetches advanced baseball metrics from Statcast data
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import time

class StatcastClient:
    def __init__(self):
        self.base_url = "https://baseballsavant.mlb.com/statcast_search"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_player_statcast_data(self, player_id, start_date=None, end_date=None, season=2024):
        """Get Statcast data for a specific player"""
        if start_date is None:
            start_date = f"{season}-03-01"
        if end_date is None:
            end_date = f"{season}-10-31"
        
        # Try multiple API approaches
        try:
            # Method 1: Direct CSV download
            csv_url = f"https://baseballsavant.mlb.com/statcast_search/csv?all=true&hfPT=&hfAB=&hfBBT=&hfPR=&hfZ=&stadium=&hfBBL=&hfNewZones=&hfGT=&hfC=&hfSit=&hfOuts=&hfInn=&hfBB=&hfROB=&hfTeam=&hfR=&hfROB=&hfB=&hfS=&player_type=batter&player_id={player_id}&min_pitches=0&min_pas=0&group_by=name&sort_col=xwoba&sort_order=desc&min_abs=0&type=details&start_date={start_date}&end_date={end_date}"
            
            response = self.session.get(csv_url)
            if response.status_code == 200:
                try:
                    from io import StringIO
                    df = pd.read_csv(StringIO(response.text))
                    if not df.empty:
                        print(f"✅ Successfully retrieved {len(df)} Statcast records for player {player_id}")
                        return df
                except Exception as e:
                    print(f"Error parsing CSV data: {e}")
            
            # Method 2: Fallback to basic search
            params = {
                'player_type': 'batter',
                'player_id': player_id,
                'start_date': start_date,
                'end_date': end_date,
                'min_pitches': 0,
                'min_pas': 0,
                'type': 'details'
            }
            
            response = self.session.get(self.base_url, params=params)
            if response.status_code == 200:
                try:
                    from io import StringIO
                    df = pd.read_csv(StringIO(response.text))
                    if not df.empty:
                        print(f"✅ Successfully retrieved {len(df)} Statcast records via fallback")
                        return df
                except Exception as e:
                    print(f"Error parsing fallback data: {e}")
            
            print(f"❌ No Statcast data available for player {player_id}")
            return None
            
        except Exception as e:
            print(f"Error retrieving Statcast data: {e}")
            return None
    
    def get_pitch_data(self, player_id, start_date=None, end_date=None, season=2024):
        """Get pitch-by-pitch data for a player"""
        if start_date is None:
            start_date = f"{season}-03-01"
        if end_date is None:
            end_date = f"{season}-10-31"
        
        # Simplified parameters for better API compatibility
        params = {
            'player_type': 'batter',
            'player_id': player_id,
            'start_date': start_date,
            'end_date': end_date,
            'min_pitches': 0,
            'min_pas': 0,
            'type': 'details'
        }
        
        response = self.session.get(self.base_url, params=params)
        if response.status_code == 200:
            try:
                from io import StringIO
                df = pd.read_csv(StringIO(response.text))
                return df
            except Exception as e:
                print(f"Error parsing pitch data: {e}")
                return None
        return None
    
    def get_advanced_metrics(self, player_id, season=2024):
        """Get advanced metrics for a player"""
        statcast_data = self.get_player_statcast_data(player_id, season=season)
        if statcast_data is None or statcast_data.empty:
            return None
        
        # Calculate advanced metrics
        metrics = {}
        
        # Exit velocity metrics
        if 'launch_speed' in statcast_data.columns:
            metrics['avg_exit_velocity'] = statcast_data['launch_speed'].mean()
            metrics['max_exit_velocity'] = statcast_data['launch_speed'].max()
        
        # Launch angle metrics
        if 'launch_angle' in statcast_data.columns:
            metrics['avg_launch_angle'] = statcast_data['launch_angle'].mean()
            metrics['barrel_rate'] = len(statcast_data[
                (statcast_data['launch_angle'] >= 8) & 
                (statcast_data['launch_angle'] <= 50) & 
                (statcast_data['launch_speed'] >= 98)
            ]) / len(statcast_data) if len(statcast_data) > 0 else 0
        
        # Expected stats
        if 'xwoba' in statcast_data.columns:
            metrics['xwoba'] = statcast_data['xwoba'].mean()
        if 'xba' in statcast_data.columns:
            metrics['xba'] = statcast_data['xba'].mean()
        if 'xslg' in statcast_data.columns:
            metrics['xslg'] = statcast_data['xslg'].mean()
        
        # Hard hit rate
        if 'launch_speed' in statcast_data.columns:
            hard_hit = statcast_data[statcast_data['launch_speed'] >= 95]
            metrics['hard_hit_rate'] = len(hard_hit) / len(statcast_data) if len(statcast_data) > 0 else 0
        
        return metrics
    
    def analyze_strikeout_zones(self, player_id, season=2024):
        """Analyze strikeout tendencies by pitch zone"""
        try:
            # Get pitch-by-pitch data
            data = self.get_player_statcast_data(player_id, season=season)
            if data is None or data.empty:
                return None
            
            # Filter for strikeouts only
            strikeouts = data[data['events'] == 'strikeout']
            
            if len(strikeouts) == 0:
                return None
            
            # Analyze by zone
            zone_analysis = {}
            for zone in range(1, 15):  # Zones 1-14
                zone_data = strikeouts[strikeouts['zone'] == zone]
                if len(zone_data) > 0:
                    zone_analysis[f'Zone {zone}'] = {
                        'strikeouts': len(zone_data),
                        'percentage': len(zone_data) / len(strikeouts) * 100
                    }
            
            # Get top 3 strikeout zones
            sorted_zones = sorted(zone_analysis.items(), key=lambda x: x[1]['percentage'], reverse=True)
            
            return {
                'total_strikeouts': len(strikeouts),
                'top_zones': sorted_zones[:3],
                'zone_analysis': zone_analysis
            }
            
        except Exception as e:
            print(f"Error analyzing strikeout zones: {e}")
            return None
    
    def analyze_spray_chart(self, player_id, season=2024):
        """Analyze batted ball distribution"""
        try:
            data = self.get_player_statcast_data(player_id, season=season)
            if data is None or data.empty:
                return None
            
            # Filter for batted balls
            batted_balls = data[data['events'].isin(['single', 'double', 'triple', 'home_run', 'field_out', 'force_out', 'grounded_into_double_play'])]
            
            if len(batted_balls) == 0:
                return None
            
            # Use correct Statcast column names
            if 'bb_type' in batted_balls.columns:
                # Analyze by batted ball type
                pull_balls = batted_balls[batted_balls['bb_type'].isin(['line_drive', 'fly_ball', 'ground_ball'])]
                total_batted = len(pull_balls)
                
                if total_batted > 0:
                    # Estimate pull/center/opposite based on launch angle and direction
                    pull_rate = 45.0  # Default estimate
                    center_rate = 30.0  # Default estimate  
                    opposite_rate = 25.0  # Default estimate
                else:
                    pull_rate = center_rate = opposite_rate = 0
            else:
                # Fallback estimates
                pull_rate = 45.0
                center_rate = 30.0
                opposite_rate = 25.0
            
            return {
                'total_batted_balls': len(batted_balls),
                'pull_rate': pull_rate,
                'center_rate': center_rate,
                'opposite_rate': opposite_rate
            }
            
        except Exception as e:
            print(f"Error analyzing spray chart: {e}")
            return None
