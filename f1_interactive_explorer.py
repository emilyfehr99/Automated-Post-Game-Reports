#!/usr/bin/env python3
"""
F1 Interactive Explorer - Interactive exploration of F1 API data
"""

import requests
import json
import pandas as pd
from datetime import datetime

class F1InteractiveExplorer:
    def __init__(self):
        self.base_url = "https://api.openf1.org/v1"
        self.session = requests.Session()
    
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
    
    def get_race_results(self, session_key):
        """Get race results for a specific session"""
        print(f"🏆 Getting race results for session {session_key}...")
        
        # Try to get position data at the end of the race
        positions = self.get_data("position", {"session_key": session_key})
        if positions:
            # Get the latest positions (assuming they're sorted by time)
            df = pd.DataFrame(positions)
            if not df.empty:
                # Get the last recorded position for each driver
                latest_positions = df.groupby('driver_number').last().reset_index()
                latest_positions = latest_positions.sort_values('position')
                
                print(f"\n🏁 Race Results:")
                print(latest_positions[['position', 'driver_number']].to_string(index=False))
                return latest_positions
        return None
    
    def get_driver_lap_times(self, session_key, driver_number):
        """Get lap times for a specific driver"""
        print(f"⏱️ Getting lap times for driver #{driver_number}...")
        
        laps = self.get_data("laps", {"session_key": session_key, "driver_number": driver_number})
        if laps:
            df = pd.DataFrame(laps)
            if 'lap_duration' in df.columns:
                # Filter out None values and show lap times
                valid_laps = df[df['lap_duration'].notna()]
                if not valid_laps.empty:
                    print(f"\nLap times for driver #{driver_number}:")
                    print(valid_laps[['lap_number', 'lap_duration']].to_string(index=False))
                    return valid_laps
        return None
    
    def get_weather_during_race(self, session_key):
        """Get weather data during a race"""
        print(f"🌤️ Getting weather data for session {session_key}...")
        
        weather = self.get_data("weather", {"session_key": session_key})
        if weather:
            df = pd.DataFrame(weather)
            if not df.empty:
                print(f"\nWeather during session:")
                print(df[['date', 'air_temperature', 'track_temperature', 'humidity', 'wind_speed']].to_string(index=False))
                return df
        return None
    
    def get_pit_stop_analysis(self, session_key):
        """Analyze pit stops for a session"""
        print(f"🔧 Analyzing pit stops for session {session_key}...")
        
        pit_stops = self.get_data("pit", {"session_key": session_key})
        if pit_stops:
            df = pd.DataFrame(pit_stops)
            if not df.empty:
                print(f"\nPit Stop Analysis:")
                print(f"Total pit stops: {len(df)}")
                
                # Group by driver
                driver_pits = df.groupby('driver_number').size().reset_index(name='pit_count')
                print(f"\nPit stops per driver:")
                print(driver_pits.to_string(index=False))
                
                # Show pit durations if available
                if 'pit_duration' in df.columns:
                    valid_durations = df[df['pit_duration'].notna()]
                    if not valid_durations.empty:
                        print(f"\nPit stop durations:")
                        print(valid_durations[['driver_number', 'pit_duration']].to_string(index=False))
                
                return df
        return None
    
    def get_team_radio_highlights(self, session_key, limit=5):
        """Get team radio highlights"""
        print(f"📻 Getting team radio highlights for session {session_key}...")
        
        radio = self.get_data("team_radio", {"session_key": session_key})
        if radio:
            df = pd.DataFrame(radio)
            if not df.empty:
                print(f"\nTeam Radio Highlights (showing {min(limit, len(df))} of {len(df)}):")
                print(df[['driver_number', 'date']].head(limit).to_string(index=False))
                return df
        return None
    
    def analyze_race_session(self, session_key):
        """Comprehensive analysis of a race session"""
        print(f"🏎️ COMPREHENSIVE RACE ANALYSIS")
        print(f"Session Key: {session_key}")
        print("=" * 60)
        
        # Get session info
        sessions = self.get_data("sessions", {"session_key": session_key})
        if sessions:
            session_info = sessions[0]
            print(f"Session: {session_info.get('session_name', 'Unknown')}")
            print(f"Date: {session_info.get('date_start', 'Unknown')}")
            print(f"Meeting: {session_info.get('meeting_key', 'Unknown')}")
        
        # Get drivers for this session
        drivers = self.get_data("drivers", {"session_key": session_key})
        if drivers:
            print(f"\n👨‍🏁 Drivers in this session:")
            for driver in drivers:
                print(f"   #{driver.get('driver_number', '?')} - {driver.get('full_name', 'Unknown')} ({driver.get('team_name', 'Unknown')})")
        
        # Get race results
        self.get_race_results(session_key)
        
        # Get weather data
        self.get_weather_during_race(session_key)
        
        # Get pit stop analysis
        self.get_pit_stop_analysis(session_key)
        
        # Get team radio highlights
        self.get_team_radio_highlights(session_key)
        
        # Get lap times for top 3 drivers (if we have position data)
        positions = self.get_data("position", {"session_key": session_key})
        if positions:
            df = pd.DataFrame(positions)
            if not df.empty:
                latest_positions = df.groupby('driver_number').last().reset_index()
                top_3 = latest_positions.nsmallest(3, 'position')['driver_number'].tolist()
                
                print(f"\n⏱️ Lap times for top 3 drivers:")
                for driver_num in top_3:
                    self.get_driver_lap_times(session_key, driver_num)
                    print()  # Add spacing
    
    def explore_specific_race(self, race_name="Abu Dhabi Grand Prix"):
        """Explore a specific race by name"""
        print(f"🔍 Looking for {race_name}...")
        
        # Find the meeting
        meetings = self.get_data("meetings", {"year": 2024})
        if meetings:
            target_meeting = None
            for meeting in meetings:
                if race_name.lower() in meeting.get('meeting_name', '').lower():
                    target_meeting = meeting
                    break
            
            if target_meeting:
                print(f"Found: {target_meeting.get('meeting_name')}")
                meeting_key = target_meeting.get('meeting_key')
                
                # Get sessions for this meeting
                sessions = self.get_data("sessions", {"meeting_key": meeting_key})
                if sessions:
                    # Find the race session
                    race_session = None
                    for session in sessions:
                        if session.get('session_name') == 'Race':
                            race_session = session
                            break
                    
                    if race_session:
                        session_key = race_session.get('session_key')
                        self.analyze_race_session(session_key)
                    else:
                        print("No race session found for this meeting")
                else:
                    print("No sessions found for this meeting")
            else:
                print(f"Race '{race_name}' not found in 2024")
                print("Available races:")
                for meeting in meetings:
                    print(f"  - {meeting.get('meeting_name')}")
    
    def quick_stats(self):
        """Get quick statistics about available data"""
        print("📊 QUICK STATS")
        print("=" * 30)
        
        # Count meetings
        meetings = self.get_data("meetings", {"year": 2024})
        if meetings:
            print(f"🏁 Meetings in 2024: {len(meetings)}")
        
        # Count sessions
        sessions = self.get_data("sessions", {"year": 2024})
        if sessions:
            print(f"🏎️ Sessions in 2024: {len(sessions)}")
        
        # Count drivers
        drivers = self.get_data("drivers", {"session_key": "latest"})
        if drivers:
            print(f"👨‍🏁 Current drivers: {len(drivers)}")
        
        # Count lap records
        laps = self.get_data("laps", {"year": 2024})
        if laps:
            print(f"⏱️ Lap records in 2024: {len(laps)}")
        
        # Count weather records
        weather = self.get_data("weather", {"year": 2024})
        if weather:
            print(f"🌤️ Weather records in 2024: {len(weather)}")
        
        # Count radio records
        radio = self.get_data("team_radio", {"year": 2024})
        if radio:
            print(f"📻 Radio records in 2024: {len(radio)}")

def main():
    explorer = F1InteractiveExplorer()
    
    print("🏎️ F1 INTERACTIVE EXPLORER")
    print("=" * 50)
    
    # Show quick stats
    explorer.quick_stats()
    
    print("\n" + "=" * 50)
    print("🎯 Let's explore some specific races!")
    
    # Explore Abu Dhabi Grand Prix (last race of 2024)
    explorer.explore_specific_race("Abu Dhabi Grand Prix")
    
    print("\n" + "=" * 50)
    print("💡 Try exploring other races by modifying the script!")
    print("Available races in 2024:")
    meetings = explorer.get_data("meetings", {"year": 2024})
    if meetings:
        for meeting in meetings[-5:]:  # Show last 5 races
            print(f"  - {meeting.get('meeting_name')}")

if __name__ == "__main__":
    main()


