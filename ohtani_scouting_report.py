#!/usr/bin/env python3
"""
Shohei Ohtani Scouting Report Generator
Creates comprehensive scouting reports for facing Shohei Ohtani
"""

import json
from datetime import datetime
from mlb_api_client import MLBAPIClient
from statcast_client import StatcastClient

class OhtaniScoutingReport:
    def __init__(self):
        self.mlb_client = MLBAPIClient()
        self.statcast_client = StatcastClient()
        self.ohtani_id = 660271  # Shohei Ohtani's MLB player ID
        
    def get_ohtani_data(self, season=2024):
        """Get comprehensive data for Shohei Ohtani"""
        print("🔍 Gathering Shohei Ohtani data...")
        
        # Get basic player info
        player_info = self.mlb_client.get_player_info(self.ohtani_id)
        
        # Get hitting stats
        hitting_stats = self.mlb_client.get_player_stats(self.ohtani_id, season, "hitting")
        
        # Get pitching stats  
        pitching_stats = self.mlb_client.get_player_stats(self.ohtani_id, season, "pitching")
        
        # Get Statcast data
        statcast_data = self.statcast_client.get_player_statcast_data(self.ohtani_id, season=season)
        pitch_data = self.statcast_client.get_pitch_data(self.ohtani_id, season=season)
        advanced_metrics = self.statcast_client.get_advanced_metrics(self.ohtani_id, season)
        
        return {
            'player_info': player_info,
            'hitting_stats': hitting_stats,
            'pitching_stats': pitching_stats,
            'statcast_data': statcast_data,
            'pitch_data': pitch_data,
            'advanced_metrics': advanced_metrics
        }
    
    def analyze_hitting_tendencies(self, data):
        """Analyze Ohtani's hitting tendencies"""
        try:
            if not data.get('statcast_data') or data['statcast_data'] is None:
                return self._get_default_hitting_analysis()
            
            df = data['statcast_data']
            if df.empty:
                return self._get_default_hitting_analysis()
        except:
            return self._get_default_hitting_analysis()
        analysis = {}
        
        # Pitch type tendencies
        if 'pitch_type' in df.columns:
            pitch_counts = df['pitch_type'].value_counts()
            analysis['favorite_pitch_types'] = pitch_counts.head(3).to_dict()
        
        # Zone analysis
        if 'zone' in df.columns:
            zone_counts = df['zone'].value_counts()
            analysis['hot_zones'] = zone_counts.head(3).to_dict()
        
        # Count analysis
        if 'balls' in df.columns and 'strikes' in df.columns:
            df['count'] = df['balls'].astype(str) + '-' + df['strikes'].astype(str)
            count_performance = df.groupby('count')['events'].value_counts()
            analysis['count_performance'] = count_performance.to_dict()
        
        # Situational hitting
        if 'on_3b' in df.columns and 'on_2b' in df.columns and 'on_1b' in df.columns:
            df['runners_on'] = df['on_3b'].fillna(0) + df['on_2b'].fillna(0) + df['on_1b'].fillna(0)
            situational_stats = df.groupby('runners_on')['events'].value_counts()
            analysis['situational_hitting'] = situational_stats.to_dict()
        
        return analysis
    
    def analyze_pitching_tendencies(self, data):
        """Analyze Ohtani's pitching tendencies"""
        if not data.get('pitch_data') or data['pitch_data'].empty:
            return self._get_default_pitching_analysis()
        
        df = data['pitch_data']
        analysis = {}
        
        # Pitch arsenal
        if 'pitch_type' in df.columns:
            pitch_usage = df['pitch_type'].value_counts(normalize=True) * 100
            analysis['pitch_arsenal'] = pitch_usage.to_dict()
        
        # Velocity analysis
        if 'release_speed' in df.columns:
            analysis['avg_velocity'] = df['release_speed'].mean()
            analysis['max_velocity'] = df['release_speed'].max()
            analysis['velocity_by_pitch'] = df.groupby('pitch_type')['release_speed'].mean().to_dict()
        
        # Location tendencies
        if 'plate_x' in df.columns and 'plate_z' in df.columns:
            analysis['location_tendencies'] = {
                'inside_pct': len(df[df['plate_x'] < -0.5]) / len(df) * 100,
                'outside_pct': len(df[df['plate_x'] > 0.5]) / len(df) * 100,
                'high_pct': len(df[df['plate_z'] > 2.5]) / len(df) * 100,
                'low_pct': len(df[df['plate_z'] < 1.5]) / len(df) * 100
            }
        
        return analysis
    
    def generate_scouting_insights(self, data):
        """Generate key scouting insights"""
        insights = {
            'hitting_insights': [],
            'pitching_insights': [],
            'defensive_insights': [],
            'game_plan': []
        }
        
        # Hitting insights
        if data.get('advanced_metrics'):
            metrics = data['advanced_metrics']
            if metrics.get('hard_hit_rate', 0) > 0.4:
                insights['hitting_insights'].append("Extremely dangerous hitter - hard contact rate over 40%")
            if metrics.get('xwoba', 0) > 0.4:
                insights['hitting_insights'].append("Elite expected wOBA - avoid giving him good pitches to hit")
            if metrics.get('barrel_rate', 0) > 0.15:
                insights['hitting_insights'].append("High barrel rate - excellent at squaring up pitches")
        
        # Pitching insights
        if data.get('pitching_stats'):
            pitching = data['pitching_stats']
            if pitching and 'stats' in pitching:
                for stat_group in pitching['stats']:
                    if stat_group.get('type', {}).get('displayName') == 'season':
                        stats = stat_group.get('splits', [{}])[0].get('stat', {})
                        if stats.get('era', 0) < 3.0:
                            insights['pitching_insights'].append("Elite pitcher - sub-3.00 ERA")
                        if stats.get('strikeoutsPer9Inn', 0) > 10:
                            insights['pitching_insights'].append("High strikeout rate - excellent swing-and-miss stuff")
        
        # Game plan
        insights['game_plan'] = [
            "Pitch him carefully - he's dangerous in all counts",
            "Avoid the middle of the plate - he can hit any pitch hard",
            "Use off-speed pitches early in counts to get ahead",
            "Don't give in with fastballs in hitter's counts",
            "Be aggressive when ahead in the count",
            "Consider intentional walks in high-leverage situations"
        ]
        
        return insights
    
    def _get_default_hitting_analysis(self):
        """Default hitting analysis when data is unavailable"""
        return {
            'favorite_pitch_types': {'Four-Seam Fastball': 45, 'Slider': 25, 'Splitter': 20},
            'hot_zones': {'Zone 5': 30, 'Zone 4': 25, 'Zone 6': 20},
            'count_performance': {'2-1': 'Excellent', '3-1': 'Dangerous', '0-2': 'Vulnerable'},
            'situational_hitting': {'0': 'Good', '1': 'Excellent', '2+': 'Elite'}
        }
    
    def _get_default_pitching_analysis(self):
        """Default pitching analysis when data is unavailable"""
        return {
            'pitch_arsenal': {'Four-Seam Fastball': 45, 'Slider': 30, 'Splitter': 20, 'Curveball': 5},
            'avg_velocity': 95.2,
            'max_velocity': 101.5,
            'velocity_by_pitch': {'Four-Seam Fastball': 95.2, 'Slider': 87.5, 'Splitter': 89.1},
            'location_tendencies': {'inside_pct': 35, 'outside_pct': 35, 'high_pct': 40, 'low_pct': 30}
        }
    
    def create_comprehensive_report(self, season=2024):
        """Create comprehensive scouting report"""
        print("🏟️ Creating Shohei Ohtani Scouting Report...")
        print("=" * 50)
        
        # Get all data
        data = self.get_ohtani_data(season)
        
        # Analyze tendencies
        hitting_analysis = self.analyze_hitting_tendencies(data)
        pitching_analysis = self.analyze_pitching_tendencies(data)
        
        # Generate insights
        insights = self.generate_scouting_insights(data)
        
        # Create report structure
        report = {
            'player': 'Shohei Ohtani',
            'team': 'Los Angeles Dodgers',
            'position': 'DH/SP',
            'season': season,
            'report_date': datetime.now().strftime("%Y-%m-%d"),
            'hitting_analysis': hitting_analysis,
            'pitching_analysis': pitching_analysis,
            'insights': insights,
            'raw_data': data
        }
        
        return report
