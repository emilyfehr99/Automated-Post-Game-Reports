#!/usr/bin/env python3
"""
F1 API Explorer - A tool to explore the OpenF1 API endpoints
"""

import requests
import json
import pandas as pd
from datetime import datetime
import time

class F1APIExplorer:
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
    
    def get_meetings(self, year=2024):
        """Get all meetings for a given year"""
        print(f"📅 Fetching meetings for {year}...")
        data = self.get_data("meetings", {"year": year})
        if data:
            print(f"Found {len(data)} meetings in {year}")
            return data
        return []
    
    def get_sessions(self, meeting_key=None, year=2024):
        """Get sessions for a meeting or year"""
        print(f"🏁 Fetching sessions...")
        params = {"year": year}
        if meeting_key:
            params["meeting_key"] = meeting_key
        
        data = self.get_data("sessions", params)
        if data:
            print(f"Found {len(data)} sessions")
            return data
        return []
    
    def get_drivers(self, session_key=None):
        """Get driver information"""
        print(f"👨‍🏁 Fetching driver information...")
        params = {}
        if session_key:
            params["session_key"] = session_key
        
        data = self.get_data("drivers", params)
        if data:
            print(f"Found {len(data)} drivers")
            return data
        return []
    
    def get_weather(self, meeting_key=None, session_key=None):
        """Get weather data"""
        print(f"🌤️ Fetching weather data...")
        params = {}
        if meeting_key:
            params["meeting_key"] = meeting_key
        if session_key:
            params["session_key"] = session_key
        
        data = self.get_data("weather", params)
        if data:
            print(f"Found {len(data)} weather records")
            return data
        return []
    
    def get_car_data(self, session_key=None, driver_number=None, limit=10):
        """Get car telemetry data"""
        print(f"🚗 Fetching car telemetry data...")
        params = {}
        if session_key:
            params["session_key"] = session_key
        if driver_number:
            params["driver_number"] = driver_number
        
        data = self.get_data("car_data", params)
        if data:
            # Limit results for display
            limited_data = data[:limit] if len(data) > limit else data
            print(f"Found {len(data)} car data records (showing {len(limited_data)})")
            return limited_data
        return []
    
    def get_laps(self, session_key=None, driver_number=None, limit=10):
        """Get lap data"""
        print(f"⏱️ Fetching lap data...")
        params = {}
        if session_key:
            params["session_key"] = session_key
        if driver_number:
            params["driver_number"] = driver_number
        
        data = self.get_data("laps", params)
        if data:
            limited_data = data[:limit] if len(data) > limit else data
            print(f"Found {len(data)} lap records (showing {len(limited_data)})")
            return limited_data
        return []
    
    def get_team_radio(self, session_key=None, driver_number=None, limit=5):
        """Get team radio communications"""
        print(f"📻 Fetching team radio data...")
        params = {}
        if session_key:
            params["session_key"] = session_key
        if driver_number:
            params["driver_number"] = driver_number
        
        data = self.get_data("team_radio", params)
        if data:
            limited_data = data[:limit] if len(data) > limit else data
            print(f"Found {len(data)} radio records (showing {len(limited_data)})")
            return limited_data
        return []
    
    def explore_latest_data(self):
        """Explore the most recent available data"""
        print("🔍 Exploring latest F1 data...\n")
        
        # Get latest meetings
        meetings = self.get_meetings(2024)
        if not meetings:
            print("No meetings found for 2024, trying 2023...")
            meetings = self.get_meetings(2023)
        
        if meetings:
            latest_meeting = meetings[-1]  # Get the most recent meeting
            print(f"\n📍 Latest meeting: {latest_meeting.get('meeting_name', 'Unknown')}")
            print(f"   Date: {latest_meeting.get('date_start', 'Unknown')}")
            print(f"   Meeting Key: {latest_meeting.get('meeting_key', 'Unknown')}")
            
            # Get sessions for this meeting
            sessions = self.get_sessions(meeting_key=latest_meeting.get('meeting_key'))
            if sessions:
                latest_session = sessions[-1]
                print(f"\n🏁 Latest session: {latest_session.get('session_name', 'Unknown')}")
                print(f"   Session Key: {latest_session.get('session_key', 'Unknown')}")
                
                session_key = latest_session.get('session_key')
                
                # Get drivers for this session
                drivers = self.get_drivers(session_key=session_key)
                if drivers:
                    print(f"\n👨‍🏁 Drivers in this session:")
                    for driver in drivers[:5]:  # Show first 5 drivers
                        print(f"   #{driver.get('driver_number', '?')} - {driver.get('full_name', 'Unknown')} ({driver.get('team_name', 'Unknown')})")
                
                # Get some sample data
                print(f"\n🚗 Sample car telemetry:")
                car_data = self.get_car_data(session_key=session_key, limit=3)
                if car_data:
                    for record in car_data:
                        print(f"   Driver #{record.get('driver_number', '?')}: Speed={record.get('speed', '?')} km/h, Gear={record.get('n_gear', '?')}, Throttle={record.get('throttle', '?')}%")
                
                print(f"\n⏱️ Sample lap data:")
                lap_data = self.get_laps(session_key=session_key, limit=3)
                if lap_data:
                    for record in lap_data:
                        print(f"   Driver #{record.get('driver_number', '?')}: Lap {record.get('lap_number', '?')}, Time={record.get('lap_duration', '?')}s")
                
                print(f"\n📻 Sample team radio:")
                radio_data = self.get_team_radio(session_key=session_key, limit=2)
                if radio_data:
                    for record in radio_data:
                        print(f"   Driver #{record.get('driver_number', '?')}: {record.get('date', 'Unknown time')}")
    
    def save_data_to_csv(self, data, filename):
        """Save data to CSV file"""
        if data:
            df = pd.DataFrame(data)
            df.to_csv(filename, index=False)
            print(f"💾 Data saved to {filename}")
        else:
            print("❌ No data to save")

def main():
    explorer = F1APIExplorer()
    
    print("🏎️ F1 API Explorer")
    print("=" * 50)
    
    # Explore latest data
    explorer.explore_latest_data()
    
    print("\n" + "=" * 50)
    print("🎯 Available endpoints to explore:")
    print("• meetings - Race weekend information")
    print("• sessions - Practice, qualifying, race sessions")
    print("• drivers - Driver information and teams")
    print("• car_data - Real-time telemetry (speed, throttle, etc.)")
    print("• laps - Lap timing and performance data")
    print("• weather - Track weather conditions")
    print("• team_radio - Radio communications")
    print("• position - Race positions")
    print("• pit - Pit stop data")
    print("• intervals - Time gaps between drivers")
    print("• stints - Tire stint information")
    print("• race_control - Race control messages")
    print("• overtakes - Overtaking data (beta)")
    print("• starting_grid - Starting positions (beta)")
    print("• session_result - Session results (beta)")
    
    print("\n💡 Try modifying the script to explore specific endpoints!")
    print("📚 Full documentation: https://openf1.org")

if __name__ == "__main__":
    main()


