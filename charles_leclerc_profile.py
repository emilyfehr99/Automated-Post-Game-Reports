#!/usr/bin/env python3
"""
Charles Leclerc Driver Profile - Comprehensive Analytics Dashboard
"""

import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

class CharlesLeclercProfile:
    def __init__(self):
        self.base_url = "https://api.openf1.org/v1"
        self.session = requests.Session()
        self.driver_number = 16  # Charles Leclerc's number
        self.driver_name = "Charles LECLERC"
        self.team = "Ferrari"
        
        # Data storage
        self.race_data = {}
        self.qualifying_data = {}
        self.lap_data = {}
        self.position_data = {}
        self.weather_data = {}
        self.pit_data = {}
        
    def get_data(self, endpoint, params=None):
        """Generic method to fetch data from any endpoint"""
        url = f"{self.base_url}/{endpoint}"
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from {endpoint}: {e}")
            return None
    
    def collect_all_data(self):
        """Collect all available data for Charles Leclerc"""
        print("🏎️ Collecting Charles Leclerc data...")
        
        # Get all 2024 sessions
        sessions = self.get_data("sessions", {"year": 2024})
        if not sessions:
            print("❌ Could not fetch sessions data")
            return
        
        print(f"📊 Found {len(sessions)} sessions in 2024")
        
        # Filter for race sessions only
        race_sessions = [s for s in sessions if s.get('session_name') == 'Race']
        print(f"🏁 Found {len(race_sessions)} race sessions")
        
        # Collect data for each race
        for session in race_sessions:
            session_key = session.get('session_key')
            meeting_key = session.get('meeting_key')
            session_name = session.get('session_name')
            
            print(f"📈 Processing {session_name} - Session {session_key}")
            
            # Get meeting info
            meetings = self.get_data("meetings", {"meeting_key": meeting_key})
            meeting_name = meetings[0].get('meeting_name', 'Unknown') if meetings else 'Unknown'
            
            # Collect different types of data
            self._collect_lap_data(session_key, meeting_name)
            self._collect_position_data(session_key, meeting_name)
            self._collect_weather_data(session_key, meeting_name)
            self._collect_pit_data(session_key, meeting_name)
            
            # Add small delay to avoid rate limiting
            import time
            time.sleep(0.5)
    
    def _collect_lap_data(self, session_key, meeting_name):
        """Collect lap data for Charles Leclerc"""
        laps = self.get_data("laps", {"session_key": session_key, "driver_number": self.driver_number})
        if laps:
            df = pd.DataFrame(laps)
            df['meeting_name'] = meeting_name
            df['session_key'] = session_key
            self.lap_data[session_key] = df
    
    def _collect_position_data(self, session_key, meeting_name):
        """Collect position data for Charles Leclerc"""
        positions = self.get_data("position", {"session_key": session_key, "driver_number": self.driver_number})
        if positions:
            df = pd.DataFrame(positions)
            df['meeting_name'] = meeting_name
            df['session_key'] = session_key
            self.position_data[session_key] = df
    
    def _collect_weather_data(self, session_key, meeting_name):
        """Collect weather data for the session"""
        weather = self.get_data("weather", {"session_key": session_key})
        if weather:
            df = pd.DataFrame(weather)
            df['meeting_name'] = meeting_name
            df['session_key'] = session_key
            self.weather_data[session_key] = df
    
    def _collect_pit_data(self, session_key, meeting_name):
        """Collect pit stop data for Charles Leclerc"""
        pits = self.get_data("pit", {"session_key": session_key, "driver_number": self.driver_number})
        if pits:
            df = pd.DataFrame(pits)
            df['meeting_name'] = meeting_name
            df['session_key'] = session_key
            self.pit_data[session_key] = df
    
    def analyze_race_results(self):
        """Analyze race results and consistency"""
        print("\n🏆 RACE RESULTS ANALYSIS")
        print("=" * 50)
        
        if not self.position_data:
            print("❌ No position data available")
            return
        
        # Combine all position data
        all_positions = []
        for session_key, df in self.position_data.items():
            if not df.empty:
                # Get final position (last recorded position)
                final_pos = df.iloc[-1]
                all_positions.append({
                    'meeting_name': final_pos['meeting_name'],
                    'session_key': session_key,
                    'final_position': final_pos['position'],
                    'date': final_pos['date']
                })
        
        if not all_positions:
            print("❌ No race results found")
            return
        
        results_df = pd.DataFrame(all_positions)
        results_df = results_df.sort_values('date')
        
        # Calculate statistics
        avg_position = results_df['final_position'].mean()
        podium_finishes = len(results_df[results_df['final_position'] <= 3])
        points_finishes = len(results_df[results_df['final_position'] <= 10])
        total_races = len(results_df)
        
        print(f"📊 Race Statistics:")
        print(f"   Total Races: {total_races}")
        print(f"   Average Position: {avg_position:.1f}")
        print(f"   Podium Finishes: {podium_finishes} ({podium_finishes/total_races*100:.1f}%)")
        print(f"   Points Finishes: {points_finishes} ({points_finishes/total_races*100:.1f}%)")
        
        # Show individual race results
        print(f"\n🏁 Race Results:")
        for _, race in results_df.iterrows():
            position_emoji = "🥇" if race['final_position'] == 1 else "🥈" if race['final_position'] == 2 else "🥉" if race['final_position'] == 3 else "🏁"
            print(f"   {position_emoji} {race['meeting_name']}: P{race['final_position']}")
        
        return results_df
    
    def analyze_lap_performance(self):
        """Analyze lap time performance"""
        print("\n⏱️ LAP PERFORMANCE ANALYSIS")
        print("=" * 50)
        
        if not self.lap_data:
            print("❌ No lap data available")
            return
        
        # Combine all lap data
        all_laps = []
        for session_key, df in self.lap_data.items():
            if not df.empty:
                # Filter valid lap times
                valid_laps = df[df['lap_duration'].notna()].copy()
                if not valid_laps.empty:
                    valid_laps['meeting_name'] = df.iloc[0]['meeting_name']
                    all_laps.append(valid_laps)
        
        if not all_laps:
            print("❌ No valid lap data found")
            return
        
        combined_laps = pd.concat(all_laps, ignore_index=True)
        
        # Calculate lap time statistics
        fastest_lap = combined_laps['lap_duration'].min()
        avg_lap_time = combined_laps['lap_duration'].mean()
        lap_consistency = combined_laps['lap_duration'].std()
        
        print(f"📊 Lap Time Statistics:")
        print(f"   Fastest Lap: {fastest_lap:.3f}s")
        print(f"   Average Lap Time: {avg_lap_time:.3f}s")
        print(f"   Lap Consistency (std): {lap_consistency:.3f}s")
        
        # Analyze by track
        track_stats = combined_laps.groupby('meeting_name')['lap_duration'].agg(['min', 'mean', 'std', 'count']).round(3)
        track_stats.columns = ['Fastest', 'Average', 'Consistency', 'Laps']
        
        print(f"\n🏁 Performance by Track:")
        print(track_stats.to_string())
        
        return combined_laps
    
    def analyze_weather_impact(self):
        """Analyze performance in different weather conditions"""
        print("\n🌤️ WEATHER IMPACT ANALYSIS")
        print("=" * 50)
        
        if not self.weather_data or not self.lap_data:
            print("❌ No weather or lap data available")
            return
        
        # Combine weather and lap data
        weather_impact = []
        
        for session_key in self.weather_data.keys():
            if session_key in self.lap_data:
                weather_df = self.weather_data[session_key]
                lap_df = self.lap_data[session_key]
                
                if not weather_df.empty and not lap_df.empty:
                    # Get average weather conditions
                    avg_temp = weather_df['air_temperature'].mean()
                    avg_humidity = weather_df['humidity'].mean()
                    avg_wind = weather_df['wind_speed'].mean()
                    
                    # Get lap performance
                    valid_laps = lap_df[lap_df['lap_duration'].notna()]
                    if not valid_laps.empty:
                        avg_lap_time = valid_laps['lap_duration'].mean()
                        fastest_lap = valid_laps['lap_duration'].min()
                        
                        weather_impact.append({
                            'meeting_name': weather_df.iloc[0]['meeting_name'],
                            'avg_temp': avg_temp,
                            'avg_humidity': avg_humidity,
                            'avg_wind': avg_wind,
                            'avg_lap_time': avg_lap_time,
                            'fastest_lap': fastest_lap
                        })
        
        if not weather_impact:
            print("❌ No weather impact data found")
            return
        
        impact_df = pd.DataFrame(weather_impact)
        
        print(f"📊 Weather Impact Analysis:")
        print(f"   Temperature Range: {impact_df['avg_temp'].min():.1f}°C - {impact_df['avg_temp'].max():.1f}°C")
        print(f"   Humidity Range: {impact_df['avg_humidity'].min():.1f}% - {impact_df['avg_humidity'].max():.1f}%")
        print(f"   Wind Range: {impact_df['avg_wind'].min():.1f} - {impact_df['avg_wind'].max():.1f} m/s")
        
        # Show performance by weather conditions
        print(f"\n🌡️ Performance by Temperature:")
        temp_performance = impact_df.groupby(pd.cut(impact_df['avg_temp'], bins=3))['avg_lap_time'].mean()
        print(temp_performance.to_string())
        
        return impact_df
    
    def analyze_pit_stops(self):
        """Analyze pit stop performance"""
        print("\n🔧 PIT STOP ANALYSIS")
        print("=" * 50)
        
        if not self.pit_data:
            print("❌ No pit stop data available")
            return
        
        # Combine all pit data
        all_pits = []
        for session_key, df in self.pit_data.items():
            if not df.empty:
                all_pits.append(df)
        
        if not all_pits:
            print("❌ No pit stop data found")
            return
        
        combined_pits = pd.concat(all_pits, ignore_index=True)
        
        # Calculate pit stop statistics
        total_pits = len(combined_pits)
        avg_pit_time = combined_pits['pit_duration'].mean() if 'pit_duration' in combined_pits.columns else None
        fastest_pit = combined_pits['pit_duration'].min() if 'pit_duration' in combined_pits.columns else None
        
        print(f"📊 Pit Stop Statistics:")
        print(f"   Total Pit Stops: {total_pits}")
        if avg_pit_time:
            print(f"   Average Pit Time: {avg_pit_time:.1f}s")
        if fastest_pit:
            print(f"   Fastest Pit Stop: {fastest_pit:.1f}s")
        
        # Show pit stops by race
        print(f"\n🏁 Pit Stops by Race:")
        pit_summary = combined_pits.groupby('meeting_name').size().reset_index(name='pit_count')
        for _, race in pit_summary.iterrows():
            print(f"   {race['meeting_name']}: {race['pit_count']} stops")
        
        return combined_pits
    
    def create_visualizations(self):
        """Create comprehensive visualizations"""
        print("\n📊 CREATING VISUALIZATIONS")
        print("=" * 50)
        
        # Set up the plotting style
        plt.style.use('seaborn-v0_8')
        fig = plt.figure(figsize=(20, 15))
        
        # 1. Race Results Trend
        if self.position_data:
            ax1 = plt.subplot(3, 3, 1)
            self._plot_race_results_trend(ax1)
        
        # 2. Lap Time Distribution
        if self.lap_data:
            ax2 = plt.subplot(3, 3, 2)
            self._plot_lap_time_distribution(ax2)
        
        # 3. Performance by Track
        if self.lap_data:
            ax3 = plt.subplot(3, 3, 3)
            self._plot_performance_by_track(ax3)
        
        # 4. Weather Impact
        if self.weather_data and self.lap_data:
            ax4 = plt.subplot(3, 3, 4)
            self._plot_weather_impact(ax4)
        
        # 5. Position Changes During Race
        if self.position_data:
            ax5 = plt.subplot(3, 3, 5)
            self._plot_position_changes(ax5)
        
        # 6. Pit Stop Analysis
        if self.pit_data:
            ax6 = plt.subplot(3, 3, 6)
            self._plot_pit_stop_analysis(ax6)
        
        # 7. Lap Time Consistency
        if self.lap_data:
            ax7 = plt.subplot(3, 3, 7)
            self._plot_lap_consistency(ax7)
        
        # 8. Championship Points Simulation
        ax8 = plt.subplot(3, 3, 8)
        self._plot_championship_points(ax8)
        
        # 9. Performance Summary
        ax9 = plt.subplot(3, 3, 9)
        self._plot_performance_summary(ax9)
        
        plt.tight_layout()
        plt.savefig('charles_leclerc_profile.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("✅ Visualizations saved as 'charles_leclerc_profile.png'")
    
    def _plot_race_results_trend(self, ax):
        """Plot race results trend over time"""
        all_positions = []
        for session_key, df in self.position_data.items():
            if not df.empty:
                final_pos = df.iloc[-1]
                all_positions.append({
                    'meeting_name': final_pos['meeting_name'],
                    'position': final_pos['position'],
                    'date': pd.to_datetime(final_pos['date'])
                })
        
        if all_positions:
            results_df = pd.DataFrame(all_positions)
            results_df = results_df.sort_values('date')
            
            ax.plot(range(len(results_df)), results_df['position'], 'o-', linewidth=2, markersize=8)
            ax.set_title('Race Results Trend', fontsize=14, fontweight='bold')
            ax.set_xlabel('Race Number')
            ax.set_ylabel('Finishing Position')
            ax.set_ylim(0, 21)
            ax.invert_yaxis()  # Lower position numbers are better
            ax.grid(True, alpha=0.3)
    
    def _plot_lap_time_distribution(self, ax):
        """Plot lap time distribution"""
        all_laps = []
        for session_key, df in self.lap_data.items():
            valid_laps = df[df['lap_duration'].notna()]
            if not valid_laps.empty:
                all_laps.extend(valid_laps['lap_duration'].tolist())
        
        if all_laps:
            ax.hist(all_laps, bins=30, alpha=0.7, color='red', edgecolor='black')
            ax.set_title('Lap Time Distribution', fontsize=14, fontweight='bold')
            ax.set_xlabel('Lap Time (seconds)')
            ax.set_ylabel('Frequency')
            ax.grid(True, alpha=0.3)
    
    def _plot_performance_by_track(self, ax):
        """Plot performance by track"""
        track_performance = []
        for session_key, df in self.lap_data.items():
            valid_laps = df[df['lap_duration'].notna()]
            if not valid_laps.empty:
                track_performance.append({
                    'track': df.iloc[0]['meeting_name'],
                    'avg_lap_time': valid_laps['lap_duration'].mean()
                })
        
        if track_performance:
            perf_df = pd.DataFrame(track_performance)
            perf_df = perf_df.sort_values('avg_lap_time')
            
            bars = ax.bar(range(len(perf_df)), perf_df['avg_lap_time'], color='red', alpha=0.7)
            ax.set_title('Average Lap Time by Track', fontsize=14, fontweight='bold')
            ax.set_xlabel('Track')
            ax.set_ylabel('Average Lap Time (seconds)')
            ax.set_xticks(range(len(perf_df)))
            ax.set_xticklabels(perf_df['track'], rotation=45, ha='right')
            ax.grid(True, alpha=0.3)
    
    def _plot_weather_impact(self, ax):
        """Plot weather impact on performance"""
        weather_impact = []
        for session_key in self.weather_data.keys():
            if session_key in self.lap_data:
                weather_df = self.weather_data[session_key]
                lap_df = self.lap_data[session_key]
                
                if not weather_df.empty and not lap_df.empty:
                    avg_temp = weather_df['air_temperature'].mean()
                    valid_laps = lap_df[lap_df['lap_duration'].notna()]
                    if not valid_laps.empty:
                        avg_lap_time = valid_laps['lap_duration'].mean()
                        weather_impact.append({'temp': avg_temp, 'lap_time': avg_lap_time})
        
        if weather_impact:
            impact_df = pd.DataFrame(weather_impact)
            ax.scatter(impact_df['temp'], impact_df['lap_time'], s=100, alpha=0.7, color='red')
            ax.set_title('Temperature vs Lap Time', fontsize=14, fontweight='bold')
            ax.set_xlabel('Temperature (°C)')
            ax.set_ylabel('Average Lap Time (seconds)')
            ax.grid(True, alpha=0.3)
    
    def _plot_position_changes(self, ax):
        """Plot position changes during races"""
        # This would show position changes during individual races
        ax.text(0.5, 0.5, 'Position Changes\nDuring Races', ha='center', va='center', 
                transform=ax.transAxes, fontsize=12)
        ax.set_title('Position Changes', fontsize=14, fontweight='bold')
    
    def _plot_pit_stop_analysis(self, ax):
        """Plot pit stop analysis"""
        if self.pit_data:
            all_pits = []
            for session_key, df in self.pit_data.items():
                if not df.empty and 'pit_duration' in df.columns:
                    all_pits.extend(df['pit_duration'].tolist())
            
            if all_pits:
                ax.hist(all_pits, bins=10, alpha=0.7, color='red', edgecolor='black')
                ax.set_title('Pit Stop Duration Distribution', fontsize=14, fontweight='bold')
                ax.set_xlabel('Pit Stop Duration (seconds)')
                ax.set_ylabel('Frequency')
                ax.grid(True, alpha=0.3)
            else:
                ax.text(0.5, 0.5, 'No Pit Stop\nDuration Data', ha='center', va='center', 
                        transform=ax.transAxes, fontsize=12)
        else:
            ax.text(0.5, 0.5, 'No Pit Stop\nData Available', ha='center', va='center', 
                    transform=ax.transAxes, fontsize=12)
        ax.set_title('Pit Stop Analysis', fontsize=14, fontweight='bold')
    
    def _plot_lap_consistency(self, ax):
        """Plot lap consistency analysis"""
        track_consistency = []
        for session_key, df in self.lap_data.items():
            valid_laps = df[df['lap_duration'].notna()]
            if not valid_laps.empty and len(valid_laps) > 5:
                consistency = valid_laps['lap_duration'].std()
                track_consistency.append({
                    'track': df.iloc[0]['meeting_name'],
                    'consistency': consistency
                })
        
        if track_consistency:
            cons_df = pd.DataFrame(track_consistency)
            cons_df = cons_df.sort_values('consistency')
            
            bars = ax.bar(range(len(cons_df)), cons_df['consistency'], color='red', alpha=0.7)
            ax.set_title('Lap Consistency by Track', fontsize=14, fontweight='bold')
            ax.set_xlabel('Track')
            ax.set_ylabel('Lap Time Standard Deviation')
            ax.set_xticks(range(len(cons_df)))
            ax.set_xticklabels(cons_df['track'], rotation=45, ha='right')
            ax.grid(True, alpha=0.3)
        else:
            ax.text(0.5, 0.5, 'Insufficient Data\nfor Consistency\nAnalysis', ha='center', va='center', 
                    transform=ax.transAxes, fontsize=12)
    
    def _plot_championship_points(self, ax):
        """Plot championship points simulation"""
        # Simulate championship points based on race results
        points_system = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}
        
        all_positions = []
        for session_key, df in self.position_data.items():
            if not df.empty:
                final_pos = df.iloc[-1]
                all_positions.append({
                    'meeting_name': final_pos['meeting_name'],
                    'position': final_pos['position'],
                    'date': pd.to_datetime(final_pos['date'])
                })
        
        if all_positions:
            results_df = pd.DataFrame(all_positions)
            results_df = results_df.sort_values('date')
            results_df['points'] = results_df['position'].map(points_system).fillna(0)
            results_df['cumulative_points'] = results_df['points'].cumsum()
            
            ax.plot(range(len(results_df)), results_df['cumulative_points'], 'o-', 
                   linewidth=2, markersize=8, color='red')
            ax.set_title('Championship Points Progression', fontsize=14, fontweight='bold')
            ax.set_xlabel('Race Number')
            ax.set_ylabel('Cumulative Points')
            ax.grid(True, alpha=0.3)
    
    def _plot_performance_summary(self, ax):
        """Plot performance summary"""
        # Create a summary of key metrics
        summary_text = f"""
CHARLES LECLERC - 2024 SEASON SUMMARY

🏁 Races: {len(self.position_data)}
⏱️ Total Laps: {sum(len(df[df['lap_duration'].notna()]) for df in self.lap_data.values())}
🔧 Pit Stops: {sum(len(df) for df in self.pit_data.values())}
🌤️ Weather Sessions: {len(self.weather_data)}

📊 Key Statistics:
• Average Position: {np.mean([df.iloc[-1]['position'] for df in self.position_data.values() if not df.empty]):.1f}
• Podium Finishes: {len([df for df in self.position_data.values() if not df.empty and df.iloc[-1]['position'] <= 3])}
• Points Finishes: {len([df for df in self.position_data.values() if not df.empty and df.iloc[-1]['position'] <= 10])}

🏎️ Team: {self.team}
👨‍🏁 Driver Number: #{self.driver_number}
        """
        
        ax.text(0.05, 0.95, summary_text, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.8))
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        ax.set_title('Performance Summary', fontsize=14, fontweight='bold')
    
    def generate_report(self):
        """Generate comprehensive driver profile report"""
        print("🏎️ CHARLES LECLERC - COMPREHENSIVE DRIVER PROFILE")
        print("=" * 60)
        
        # Collect all data
        self.collect_all_data()
        
        # Run all analyses
        race_results = self.analyze_race_results()
        lap_performance = self.analyze_lap_performance()
        weather_impact = self.analyze_weather_impact()
        pit_analysis = self.analyze_pit_stops()
        
        # Create visualizations
        self.create_visualizations()
        
        # Save data to CSV files
        if race_results is not None:
            race_results.to_csv('charles_leclerc_race_results.csv', index=False)
            print("💾 Race results saved to 'charles_leclerc_race_results.csv'")
        
        if lap_performance is not None:
            lap_performance.to_csv('charles_leclerc_lap_data.csv', index=False)
            print("💾 Lap data saved to 'charles_leclerc_lap_data.csv'")
        
        if weather_impact is not None:
            weather_impact.to_csv('charles_leclerc_weather_impact.csv', index=False)
            print("💾 Weather impact data saved to 'charles_leclerc_weather_impact.csv'")
        
        if pit_analysis is not None:
            pit_analysis.to_csv('charles_leclerc_pit_stops.csv', index=False)
            print("💾 Pit stop data saved to 'charles_leclerc_pit_stops.csv'")
        
        print("\n🎉 Charles Leclerc profile analysis complete!")
        print("📊 Check the generated visualizations and CSV files for detailed insights.")

def main():
    profile = CharlesLeclercProfile()
    profile.generate_report()

if __name__ == "__main__":
    main()


