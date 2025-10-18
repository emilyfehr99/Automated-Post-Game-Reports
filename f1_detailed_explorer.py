#!/usr/bin/env python3
"""
F1 Detailed Explorer - Focused exploration of specific F1 API endpoints
"""

import requests
import json
import pandas as pd
from datetime import datetime

class F1DetailedExplorer:
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
    
    def explore_drivers(self):
        """Explore driver data in detail"""
        print("👨‍🏁 DRIVER EXPLORATION")
        print("=" * 50)
        
        # Get drivers from a recent session
        drivers = self.get_data("drivers", {"session_key": "latest"})
        if drivers:
            print(f"Found {len(drivers)} drivers")
            
            # Create a nice table
            df = pd.DataFrame(drivers)
            print("\nDriver Information:")
            print(df[['driver_number', 'full_name', 'team_name', 'country_code']].to_string(index=False))
            
            # Save to CSV
            df.to_csv('f1_drivers.csv', index=False)
            print(f"\n💾 Driver data saved to f1_drivers.csv")
            
            return drivers
        return []
    
    def explore_meetings(self, year=2024):
        """Explore meeting/race data"""
        print(f"\n📅 MEETING EXPLORATION ({year})")
        print("=" * 50)
        
        meetings = self.get_data("meetings", {"year": year})
        if meetings:
            print(f"Found {len(meetings)} meetings in {year}")
            
            df = pd.DataFrame(meetings)
            print("\nMeeting Information:")
            print(df[['meeting_name', 'date_start', 'meeting_key']].to_string(index=False))
            
            # Save to CSV
            df.to_csv(f'f1_meetings_{year}.csv', index=False)
            print(f"\n💾 Meeting data saved to f1_meetings_{year}.csv")
            
            return meetings
        return []
    
    def explore_sessions(self, meeting_key=None):
        """Explore session data"""
        print(f"\n🏁 SESSION EXPLORATION")
        print("=" * 50)
        
        params = {}
        if meeting_key:
            params["meeting_key"] = meeting_key
        else:
            params["year"] = 2024
        
        sessions = self.get_data("sessions", params)
        if sessions:
            print(f"Found {len(sessions)} sessions")
            
            df = pd.DataFrame(sessions)
            print("\nSession Information:")
            print(df[['session_name', 'date_start', 'meeting_key', 'session_key']].to_string(index=False))
            
            # Save to CSV
            df.to_csv('f1_sessions.csv', index=False)
            print(f"\n💾 Session data saved to f1_sessions.csv")
            
            return sessions
        return []
    
    def explore_laps(self, session_key=None, limit=20):
        """Explore lap data with more details"""
        print(f"\n⏱️ LAP DATA EXPLORATION")
        print("=" * 50)
        
        params = {}
        if session_key:
            params["session_key"] = session_key
        else:
            params["year"] = 2024
        
        laps = self.get_data("laps", params)
        if laps:
            print(f"Found {len(laps)} lap records")
            
            # Filter out None values and show interesting data
            df = pd.DataFrame(laps)
            
            # Show some interesting columns
            interesting_cols = ['driver_number', 'lap_number', 'lap_duration', 'is_pit_out_lap', 'stint']
            available_cols = [col for col in interesting_cols if col in df.columns]
            
            if available_cols:
                print(f"\nLap Data (showing first {limit} records):")
                print(df[available_cols].head(limit).to_string(index=False))
            
            # Save to CSV
            df.to_csv('f1_laps.csv', index=False)
            print(f"\n💾 Lap data saved to f1_laps.csv")
            
            return laps
        return []
    
    def explore_weather(self, meeting_key=None):
        """Explore weather data"""
        print(f"\n🌤️ WEATHER EXPLORATION")
        print("=" * 50)
        
        params = {}
        if meeting_key:
            params["meeting_key"] = meeting_key
        else:
            params["year"] = 2024
        
        weather = self.get_data("weather", params)
        if weather:
            print(f"Found {len(weather)} weather records")
            
            df = pd.DataFrame(weather)
            print("\nWeather Data:")
            print(df[['date', 'air_temperature', 'track_temperature', 'humidity', 'wind_speed']].head(10).to_string(index=False))
            
            # Save to CSV
            df.to_csv('f1_weather.csv', index=False)
            print(f"\n💾 Weather data saved to f1_weather.csv")
            
            return weather
        return []
    
    def explore_team_radio(self, session_key=None, limit=10):
        """Explore team radio data"""
        print(f"\n📻 TEAM RADIO EXPLORATION")
        print("=" * 50)
        
        params = {}
        if session_key:
            params["session_key"] = session_key
        else:
            params["year"] = 2024
        
        radio = self.get_data("team_radio", params)
        if radio:
            print(f"Found {len(radio)} radio records")
            
            df = pd.DataFrame(radio)
            print("\nTeam Radio Data:")
            print(df[['driver_number', 'date', 'recording_url']].head(limit).to_string(index=False))
            
            # Save to CSV
            df.to_csv('f1_team_radio.csv', index=False)
            print(f"\n💾 Team radio data saved to f1_team_radio.csv")
            
            return radio
        return []
    
    def explore_positions(self, session_key=None, limit=20):
        """Explore position data"""
        print(f"\n🏆 POSITION EXPLORATION")
        print("=" * 50)
        
        params = {}
        if session_key:
            params["session_key"] = session_key
        else:
            params["year"] = 2024
        
        positions = self.get_data("position", params)
        if positions:
            print(f"Found {len(positions)} position records")
            
            df = pd.DataFrame(positions)
            print("\nPosition Data:")
            print(df[['driver_number', 'date', 'position']].head(limit).to_string(index=False))
            
            # Save to CSV
            df.to_csv('f1_positions.csv', index=False)
            print(f"\n💾 Position data saved to f1_positions.csv")
            
            return positions
        return []
    
    def explore_pit_stops(self, session_key=None, limit=20):
        """Explore pit stop data"""
        print(f"\n🔧 PIT STOP EXPLORATION")
        print("=" * 50)
        
        params = {}
        if session_key:
            params["session_key"] = session_key
        else:
            params["year"] = 2024
        
        pit_stops = self.get_data("pit", params)
        if pit_stops:
            print(f"Found {len(pit_stops)} pit stop records")
            
            df = pd.DataFrame(pit_stops)
            print("\nPit Stop Data:")
            print(df[['driver_number', 'date', 'pit_duration']].head(limit).to_string(index=False))
            
            # Save to CSV
            df.to_csv('f1_pit_stops.csv', index=False)
            print(f"\n💾 Pit stop data saved to f1_pit_stops.csv")
            
            return pit_stops
        return []
    
    def run_full_exploration(self):
        """Run a comprehensive exploration of all endpoints"""
        print("🏎️ F1 DETAILED API EXPLORATION")
        print("=" * 60)
        
        # Get some basic data first
        meetings = self.explore_meetings(2024)
        sessions = self.explore_sessions()
        drivers = self.explore_drivers()
        
        # Explore other endpoints
        self.explore_laps()
        self.explore_weather()
        self.explore_team_radio()
        self.explore_positions()
        self.explore_pit_stops()
        
        print(f"\n🎉 Exploration complete!")
        print(f"📁 Check the generated CSV files for detailed data")
        print(f"🔗 Full API documentation: https://openf1.org")

def main():
    explorer = F1DetailedExplorer()
    explorer.run_full_exploration()

if __name__ == "__main__":
    main()


