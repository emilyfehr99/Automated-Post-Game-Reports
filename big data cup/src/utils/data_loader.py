"""Data loading utilities for Big Data Cup 2025 analysis."""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import re

class DataLoader:
    """Loads and preprocesses Big Data Cup 2025 data."""
    
    def __init__(self, data_dir: str):
        """Initialize with data directory path."""
        self.data_dir = Path(data_dir)
        
    def convert_time_to_seconds(self, time_str: str) -> float:
        """Convert 'MM:SS' or 'M:SS' time string to seconds."""
        if pd.isna(time_str) or time_str == '':
            return 0.0
        
        time_str = str(time_str).strip()
        
        # Handle formats like "19:58", "1:46", "0:00"
        parts = time_str.split(':')
        if len(parts) == 2:
            try:
                minutes = int(parts[0])
                seconds = int(parts[1])
                return minutes * 60 + seconds
            except:
                return 0.0
        return 0.0
    
    def load_events(self, game_file: str, full_path: str = None) -> pd.DataFrame:
        """Load events CSV file."""
        # Use full path if provided (from game dict)
        if full_path:
            file_path = Path(full_path)
        elif Path(game_file).is_absolute():
            file_path = Path(game_file)
        else:
            # Try in data_dir first
            file_path = self.data_dir / game_file
            # If not found, search recursively
            if not file_path.exists():
                matches = list(self.data_dir.glob(f"**/{game_file}"))
                if matches:
                    file_path = matches[0]
        
        if not file_path.exists():
            return pd.DataFrame()
        
        try:
            df = pd.read_csv(file_path)
        
            # Convert clock to seconds
            if 'Clock' in df.columns:
                df['Clock_Seconds'] = df['Clock'].apply(self.convert_time_to_seconds)
            
            return df
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return pd.DataFrame()
    
    def load_tracking(self, game_file: str, sample_rate: int = 10) -> pd.DataFrame:
        """Load tracking CSV file, optionally sampling."""
        file_path = self.data_dir / game_file
        if not file_path.exists():
            return pd.DataFrame()
        
        df = pd.read_csv(file_path)
        
        # Sample for performance if needed
        if sample_rate > 1:
            df = df.iloc[::sample_rate].copy()
        
        # Convert clock to seconds
        if 'Game Clock' in df.columns:
            df['Clock_Seconds'] = df['Game Clock'].apply(self.convert_time_to_seconds)
        elif 'Clock' in df.columns:
            df['Clock_Seconds'] = df['Clock'].apply(self.convert_time_to_seconds)
        
        # Filter out puck entries
        df = df[df['Player or Puck'] == 'Player'].copy()
        
        return df
    
    def load_shifts(self, game_file: str) -> pd.DataFrame:
        """Load shifts CSV file."""
        file_path = self.data_dir / game_file
        if not file_path.exists():
            return pd.DataFrame()
        
        df = pd.read_csv(file_path)
        
        # Convert times to seconds
        if 'start_clock' in df.columns:
            df['Start_Seconds'] = df['start_clock'].apply(self.convert_time_to_seconds)
        if 'end_clock' in df.columns:
            df['End_Seconds'] = df['end_clock'].apply(self.convert_time_to_seconds)
        
        return df
    
    def get_all_games(self) -> List[Dict[str, str]]:
        """Get list of all available games."""
        games = []
        # Try different patterns - also search in subdirectories
        event_files = (list(self.data_dir.glob("*Events.csv")) + 
                      list(self.data_dir.glob("*events.csv")) +
                      list(self.data_dir.glob("**/*Events.csv")) +
                      list(self.data_dir.glob("**/*events.csv")))
        
        # Remove duplicates
        event_files = list(set(event_files))
        
        # If still empty, try listing all CSV files
        if not event_files:
            all_csvs = list(self.data_dir.glob("**/*.csv"))
            event_files = [f for f in all_csvs if "Event" in f.name]
        
        for event_file in event_files:
            # Extract game identifier - get the date/team pattern before "-Events"
            stem = event_file.stem
            if "-Events" in stem:
                base_name = stem.replace("-Events", "")
            elif ".Events" in stem:
                base_name = stem.replace(".Events", "")
            else:
                # Extract pattern before any Event-related text
                parts = stem.split(".")
                base_pattern = ".".join(parts[:3]) if len(parts) >= 3 else parts[0]
                base_name = base_pattern
            
            # Find matching files - try multiple patterns
            tracking_file = None
            shifts_file = None
            
            # Try different naming patterns - search in same directory as events file first
            event_dir = event_file.parent
            
            patterns_to_try = [
                f"{base_name}-Tracking.csv",
                f"{base_name}.Tracking.csv",
            ]
            
            # Try exact matches in same directory
            for pattern in patterns_to_try:
                candidate = event_dir / pattern
                if candidate.exists():
                    tracking_file = candidate
                    break
            
            # Try glob patterns in same directory
            if not tracking_file:
                pattern_match = base_name.split('.')[0] if '.' in base_name else base_name.split('-')[0]
                matches = list(event_dir.glob(f"{pattern_match}*Tracking.csv"))
                if matches:
                    tracking_file = matches[0]
            
            # Try recursive search
            if not tracking_file:
                matches = list(self.data_dir.glob(f"**/{pattern_match}*Tracking.csv"))
                if matches:
                    tracking_file = matches[0]
            
            # Try shifts - search in same directory as events file
            patterns_to_try = [
                f"{base_name}-Shifts.csv",
                f"{base_name}.Shifts.csv",
            ]
            
            for pattern in patterns_to_try:
                candidate = event_dir / pattern
                if candidate.exists():
                    shifts_file = candidate
                    break
            
            # Try glob patterns
            if not shifts_file:
                pattern_match = base_name.split('.')[0] if '.' in base_name else base_name.split('-')[0]
                matches = list(event_dir.glob(f"{pattern_match}*Shifts.csv"))
                if matches:
                    shifts_file = matches[0]
            
            # Try recursive search
            if not shifts_file:
                matches = list(self.data_dir.glob(f"**/{pattern_match}*Shifts.csv"))
                if matches:
                    shifts_file = matches[0]
            
            # Store full paths or relative paths
            events_path = str(event_file.relative_to(self.data_dir)) if event_file.is_relative_to(self.data_dir) else event_file.name
            tracking_path = None
            shifts_path = None
            
            if tracking_file and tracking_file.exists():
                tracking_path = str(tracking_file.relative_to(self.data_dir)) if tracking_file.is_relative_to(self.data_dir) else tracking_file.name
            
            if shifts_file and shifts_file.exists():
                shifts_path = str(shifts_file.relative_to(self.data_dir)) if shifts_file.is_relative_to(self.data_dir) else shifts_file.name
            
            games.append({
                'game_id': base_name if 'base_name' in locals() else stem,
                'events': events_path,
                'tracking': tracking_path,
                'shifts': shifts_path,
                'events_full_path': str(event_file)  # Store full path for loading
            })
        
        return games
    
    def get_player_positions_at_time(self, tracking_df: pd.DataFrame, period: int, 
                                     clock_seconds: float, tolerance: float = 2.0) -> Dict[str, Tuple[float, float, str]]:
        """Get all player positions at a specific time.
        
        Returns: Dict mapping player_id -> (x, y, team)
        """
        # Filter by period and time window
        mask = (
            (tracking_df['Period'] == period) &
            (np.abs(tracking_df['Clock_Seconds'] - clock_seconds) <= tolerance)
        )
        
        frame_data = tracking_df[mask].copy()
        
        if frame_data.empty:
            return {}
        
        # Get latest frame in window
        latest_frame = frame_data.groupby('Player Id').apply(
            lambda x: x.iloc[x['Clock_Seconds'].abs().argmin()]
        )
        
        positions = {}
        for _, row in latest_frame.iterrows():
            player_id = str(row['Player Id'])
            team = str(row.get('Team', 'Unknown'))
            x = float(row.get('Rink Location X (Feet)', 0))
            y = float(row.get('Rink Location Y (Feet)', 0))
            
            positions[player_id] = (x, y, team)
        
        return positions
    
    def get_puck_position_at_time(self, tracking_df: pd.DataFrame, period: int,
                                  clock_seconds: float, tolerance: float = 2.0) -> Optional[Tuple[float, float]]:
        """Get puck position at a specific time."""
        # Need to load full tracking with puck
        file_path = None
        for f in self.data_dir.glob("*Tracking.csv"):
            if f.name in str(tracking_df):
                file_path = f
                break
        
        if not file_path:
            return None
        
        # Load full tracking
        df_full = pd.read_csv(file_path)
        if 'Game Clock' in df_full.columns:
            df_full['Clock_Seconds'] = df_full['Game Clock'].apply(self.convert_time_to_seconds)
        
        # Filter for puck
        puck_data = df_full[df_full['Player or Puck'] == 'Puck'].copy()
        
        mask = (
            (puck_data['Period'] == period) &
            (np.abs(puck_data['Clock_Seconds'] - clock_seconds) <= tolerance)
        )
        
        frame_data = puck_data[mask]
        if frame_data.empty:
            return None
        
        latest = frame_data.iloc[frame_data['Clock_Seconds'].abs().argmin()]
        x = float(latest.get('Rink Location X (Feet)', 0))
        y = float(latest.get('Rink Location Y (Feet)', 0))
        
        return (x, y) if not (np.isnan(x) or np.isnan(y)) else None

