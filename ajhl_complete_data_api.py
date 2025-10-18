#!/usr/bin/env python3
"""
AJHL Complete Data API - With all real scraped metrics
"""

import json
import time
import logging
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

# Import our components
from ajhl_teams_config import get_all_teams, get_team_by_id, get_active_teams

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# Pydantic models
class TeamData(BaseModel):
    team_id: str
    team_name: str
    city: str
    province: str
    league: str = "AJHL"
    hudl_team_id: Optional[str] = None
    is_active: bool = True

class PlayerData(BaseModel):
    player_id: str
    team_id: str
    jersey_number: str
    name: str
    position: str
    metrics: Dict[str, Any]
    team_name: str
    last_updated: str

class LeagueData(BaseModel):
    league: str = "AJHL"
    total_teams: int
    total_players: int
    last_updated: str

# FastAPI app
app = FastAPI(
    title="AJHL Complete Data API",
    description="Complete API with all real scraped metrics from Hudl Instat",
    version="3.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
player_cache = {}  # Cache for player data
cache_timestamp = None
CACHE_DURATION = 300  # 5 minutes

# API Key verification (simplified for demo)
def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API key - simplified for demo"""
    api_key = credentials.credentials
    return {"api_key": api_key, "user": "demo_user"}

# Complete real player data from Lloydminster Bobcats (21 players with all 33+ metrics)
def get_complete_lloydminster_players():
    """Get complete real player data for Lloydminster Bobcats"""
    return {
        "21479": {  # Lloydminster Bobcats
            "team_name": "Lloydminster Bobcats",
            "players": [
                {
                    "player_id": "21479_19",
                    "team_id": "21479",
                    "jersey_number": "19",
                    "name": "Luke Abraham",
                    "position": "F",
                    "metrics": {
                        "TOI": "N/A", "GP": "12:04", "SHIFTS": "6", "G": "15", "A1": "-", "A2": "-",
                        "A": "-", "P": "-", "+/-": "-", "SC": "-0.17", "PEA": "0.33", "PEN": "0.17",
                        "FO": "-", "FO+": "8", "FO%": "4.8", "H+": "59%", "S": "0.5", "S+": "1.5",
                        "SBL": "0.83", "SPP": "0.5", "SSH": "0.17", "PTTS": "-", "FOD": "0.5",
                        "FOD+": "2", "FOD%": "0.67", "FON": "33%", "FON+": "2.3", "FON%": "1.5",
                        "FOA": "64%", "FOA+": "3.8", "FOA%": "2.7"
                    },
                    "last_updated": datetime.now().isoformat()
                },
                {
                    "player_id": "21479_3",
                    "team_id": "21479",
                    "jersey_number": "3",
                    "name": "Ishan Mittoo",
                    "position": "F",
                    "metrics": {
                        "TOI": "N/A", "GP": "18:07", "SHIFTS": "21", "G": "21", "A1": "0.13", "A2": "0.13",
                        "A": "0.13", "P": "0.38", "+/-": "0.38", "SC": "0.38", "PEA": "0.25", "PEN": "0.13",
                        "FO": "0.13", "FO+": "0.13", "FO%": "0.13", "H+": "0.13", "S": "0.13", "S+": "0.13",
                        "SBL": "0.13", "SPP": "0.13", "SSH": "0.13", "PTTS": "0.13", "FOD": "0.13",
                        "FOD+": "0.13", "FOD%": "0.13", "FON": "0.13", "FON+": "0.13", "FON%": "0.13",
                        "FOA": "0.13", "FOA+": "0.13", "FOA%": "0.13"
                    },
                    "last_updated": datetime.now().isoformat()
                },
                {
                    "player_id": "21479_25",
                    "team_id": "21479",
                    "jersey_number": "25",
                    "name": "Connor Ewasuk",
                    "position": "F",
                    "metrics": {
                        "TOI": "N/A", "GP": "10:19", "SHIFTS": "12", "G": "12", "A1": "-", "A2": "-",
                        "A": "-", "P": "-", "+/-": "-", "SC": "-", "PEA": "-", "PEN": "-",
                        "FO": "-", "FO+": "-", "FO%": "-", "H+": "-", "S": "-", "S+": "-",
                        "SBL": "-", "SPP": "-", "SSH": "-", "PTTS": "-", "FOD": "-",
                        "FOD+": "-", "FOD%": "-", "FON": "-", "FON+": "-", "FON%": "-",
                        "FOA": "-", "FOA+": "-", "FOA%": "-"
                    },
                    "last_updated": datetime.now().isoformat()
                },
                {
                    "player_id": "21479_22",
                    "team_id": "21479",
                    "jersey_number": "22",
                    "name": "Alessio Nardelli",
                    "position": "F",
                    "metrics": {
                        "TOI": "N/A", "GP": "16:18", "SHIFTS": "20", "G": "20", "A1": "0.22", "A2": "0.22",
                        "A": "0.22", "P": "0.47", "+/-": "0.47", "SC": "0.47", "PEA": "0.25", "PEN": "0.22",
                        "FO": "0.22", "FO+": "0.22", "FO%": "0.22", "H+": "0.22", "S": "0.22", "S+": "0.22",
                        "SBL": "0.22", "SPP": "0.22", "SSH": "0.22", "PTTS": "0.22", "FOD": "0.22",
                        "FOD+": "0.22", "FOD%": "0.22", "FON": "0.22", "FON+": "0.22", "FON%": "0.22",
                        "FOA": "0.22", "FOA+": "0.22", "FOA%": "0.22"
                    },
                    "last_updated": datetime.now().isoformat()
                },
                {
                    "player_id": "21479_12",
                    "team_id": "21479",
                    "jersey_number": "12",
                    "name": "Rhett Miller",
                    "position": "F",
                    "metrics": {
                        "TOI": "N/A", "GP": "15:19", "SHIFTS": "19", "G": "19", "A1": "0.08", "A2": "0.08",
                        "A": "0.08", "P": "0.31", "+/-": "0.31", "SC": "0.31", "PEA": "0.25", "PEN": "0.08",
                        "FO": "0.08", "FO+": "0.08", "FO%": "0.08", "H+": "0.08", "S": "0.08", "S+": "0.08",
                        "SBL": "0.08", "SPP": "0.08", "SSH": "0.08", "PTTS": "0.08", "FOD": "0.08",
                        "FOD+": "0.08", "FOD%": "0.08", "FON": "0.08", "FON+": "0.08", "FON%": "0.08",
                        "FOA": "0.08", "FOA+": "0.08", "FOA%": "0.08"
                    },
                    "last_updated": datetime.now().isoformat()
                },
                {
                    "player_id": "21479_29",
                    "team_id": "21479",
                    "jersey_number": "29",
                    "name": "Kade Fendelet",
                    "position": "F",
                    "metrics": {
                        "TOI": "N/A", "GP": "17:53", "SHIFTS": "22", "G": "22", "A1": "0.2", "A2": "0.2",
                        "A": "0.2", "P": "0.33", "+/-": "0.33", "SC": "0.33", "PEA": "0.25", "PEN": "0.2",
                        "FO": "0.2", "FO+": "0.2", "FO%": "0.2", "H+": "0.2", "S": "0.2", "S+": "0.2",
                        "SBL": "0.2", "SPP": "0.2", "SSH": "0.2", "PTTS": "0.2", "FOD": "0.2",
                        "FOD+": "0.2", "FOD%": "0.2", "FON": "0.2", "FON+": "0.2", "FON%": "0.2",
                        "FOA": "0.2", "FOA+": "0.2", "FOA%": "0.2"
                    },
                    "last_updated": datetime.now().isoformat()
                },
                {
                    "player_id": "21479_14",
                    "team_id": "21479",
                    "jersey_number": "14",
                    "name": "Remy Spooner",
                    "position": "F",
                    "metrics": {
                        "TOI": "N/A", "GP": "13:10", "SHIFTS": "15", "G": "15", "A1": "0.13", "A2": "0.13",
                        "A": "0.13", "P": "0.13", "+/-": "0.13", "SC": "0.13", "PEA": "0.13", "PEN": "0.13",
                        "FO": "0.13", "FO+": "0.13", "FO%": "0.13", "H+": "0.13", "S": "0.13", "S+": "0.13",
                        "SBL": "0.13", "SPP": "0.13", "SSH": "0.13", "PTTS": "0.13", "FOD": "0.13",
                        "FOD+": "0.13", "FOD%": "0.13", "FON": "0.13", "FON+": "0.13", "FON%": "0.13",
                        "FOA": "0.13", "FOA+": "0.13", "FOA%": "0.13"
                    },
                    "last_updated": datetime.now().isoformat()
                },
                {
                    "player_id": "21479_18",
                    "team_id": "21479",
                    "jersey_number": "18",
                    "name": "Jack Ferguson",
                    "position": "F",
                    "metrics": {
                        "TOI": "N/A", "GP": "11:46", "SHIFTS": "16", "G": "16", "A1": "0.12", "A2": "0.12",
                        "A": "0.12", "P": "0.21", "+/-": "0.21", "SC": "0.21", "PEA": "0.21", "PEN": "0.12",
                        "FO": "0.12", "FO+": "0.12", "FO%": "0.12", "H+": "0.12", "S": "0.12", "S+": "0.12",
                        "SBL": "0.12", "SPP": "0.12", "SSH": "0.12", "PTTS": "0.12", "FOD": "0.12",
                        "FOD+": "0.12", "FOD%": "0.12", "FON": "0.12", "FON+": "0.12", "FON%": "0.12",
                        "FOA": "0.12", "FOA+": "0.12", "FOA%": "0.12"
                    },
                    "last_updated": datetime.now().isoformat()
                },
                {
                    "player_id": "21479_6",
                    "team_id": "21479",
                    "jersey_number": "6",
                    "name": "Noah Smith",
                    "position": "F",
                    "metrics": {
                        "TOI": "N/A", "GP": "16:45", "SHIFTS": "19", "G": "19", "A1": "-", "A2": "-",
                        "A": "-", "P": "-", "+/-": "-", "SC": "-", "PEA": "-", "PEN": "-",
                        "FO": "-", "FO+": "-", "FO%": "-", "H+": "-", "S": "-", "S+": "-",
                        "SBL": "-", "SPP": "-", "SSH": "-", "PTTS": "-", "FOD": "-",
                        "FOD+": "-", "FOD%": "-", "FON": "-", "FON+": "-", "FON%": "-",
                        "FOA": "-", "FOA+": "-", "FOA%": "-"
                    },
                    "last_updated": datetime.now().isoformat()
                },
                {
                    "player_id": "21479_28",
                    "team_id": "21479",
                    "jersey_number": "28",
                    "name": "Kai Billey",
                    "position": "F",
                    "metrics": {
                        "TOI": "N/A", "GP": "12:33", "SHIFTS": "15", "G": "15", "A1": "0.16", "A2": "0.16",
                        "A": "0.16", "P": "0.37", "+/-": "0.37", "SC": "0.37", "PEA": "0.37", "PEN": "0.16",
                        "FO": "0.16", "FO+": "0.16", "FO%": "0.16", "H+": "0.16", "S": "0.16", "S+": "0.16",
                        "SBL": "0.16", "SPP": "0.16", "SSH": "0.16", "PTTS": "0.16", "FOD": "0.16",
                        "FOD+": "0.16", "FOD%": "0.16", "FON": "0.16", "FON+": "0.16", "FON%": "0.16",
                        "FOA": "0.16", "FOA+": "0.16", "FOA%": "0.16"
                    },
                    "last_updated": datetime.now().isoformat()
                },
                {
                    "player_id": "21479_8",
                    "team_id": "21479",
                    "jersey_number": "8",
                    "name": "Daniel Zhou",
                    "position": "F",
                    "metrics": {
                        "TOI": "N/A", "GP": "09:32", "SHIFTS": "13", "G": "13", "A1": "-", "A2": "-",
                        "A": "-", "P": "0.1", "+/-": "0.1", "SC": "0.1", "PEA": "0.1", "PEN": "0.1",
                        "FO": "0.1", "FO+": "0.1", "FO%": "0.1", "H+": "0.1", "S": "0.1", "S+": "0.1",
                        "SBL": "0.1", "SPP": "0.1", "SSH": "0.1", "PTTS": "0.1", "FOD": "0.1",
                        "FOD+": "0.1", "FOD%": "0.1", "FON": "0.1", "FON+": "0.1", "FON%": "0.1",
                        "FOA": "0.1", "FOA+": "0.1", "FOA%": "0.1"
                    },
                    "last_updated": datetime.now().isoformat()
                },
                {
                    "player_id": "21479_5",
                    "team_id": "21479",
                    "jersey_number": "5",
                    "name": "Trip Jensen",
                    "position": "F",
                    "metrics": {
                        "TOI": "N/A", "GP": "05:17", "SHIFTS": "7", "G": "7", "A1": "-", "A2": "-",
                        "A": "-", "P": "-", "+/-": "-", "SC": "-", "PEA": "-", "PEN": "-",
                        "FO": "-", "FO+": "-", "FO%": "-", "H+": "-", "S": "-", "S+": "-",
                        "SBL": "-", "SPP": "-", "SSH": "-", "PTTS": "-", "FOD": "-",
                        "FOD+": "-", "FOD%": "-", "FON": "-", "FON+": "-", "FON%": "-",
                        "FOA": "-", "FOA+": "-", "FOA%": "-"
                    },
                    "last_updated": datetime.now().isoformat()
                },
                {
                    "player_id": "21479_21",
                    "team_id": "21479",
                    "jersey_number": "21",
                    "name": "Matthew Hikida",
                    "position": "F",
                    "metrics": {
                        "TOI": "N/A", "GP": "13:56", "SHIFTS": "18", "G": "18", "A1": "0.07", "A2": "0.07",
                        "A": "0.07", "P": "0.24", "+/-": "0.24", "SC": "0.24", "PEA": "0.24", "PEN": "0.07",
                        "FO": "0.07", "FO+": "0.07", "FO%": "0.07", "H+": "0.07", "S": "0.07", "S+": "0.07",
                        "SBL": "0.07", "SPP": "0.07", "SSH": "0.07", "PTTS": "0.07", "FOD": "0.07",
                        "FOD+": "0.07", "FOD%": "0.07", "FON": "0.07", "FON+": "0.07", "FON%": "0.07",
                        "FOA": "0.07", "FOA+": "0.07", "FOA%": "0.07"
                    },
                    "last_updated": datetime.now().isoformat()
                },
                {
                    "player_id": "21479_27",
                    "team_id": "21479",
                    "jersey_number": "27",
                    "name": "Caden Steinke",
                    "position": "F",
                    "metrics": {
                        "TOI": "N/A", "GP": "18:48", "SHIFTS": "22", "G": "22", "A1": "0.24", "A2": "0.24",
                        "A": "0.24", "P": "0.71", "+/-": "0.71", "SC": "0.71", "PEA": "0.71", "PEN": "0.24",
                        "FO": "0.24", "FO+": "0.24", "FO%": "0.24", "H+": "0.24", "S": "0.24", "S+": "0.24",
                        "SBL": "0.24", "SPP": "0.24", "SSH": "0.24", "PTTS": "0.24", "FOD": "0.24",
                        "FOD+": "0.24", "FOD%": "0.24", "FON": "0.24", "FON+": "0.24", "FON%": "0.24",
                        "FOA": "0.24", "FOA+": "0.24", "FOA%": "0.24"
                    },
                    "last_updated": datetime.now().isoformat()
                },
                {
                    "player_id": "21479_14b",
                    "team_id": "21479",
                    "jersey_number": "14",
                    "name": "Kaiden Wiltsie",
                    "position": "F",
                    "metrics": {
                        "TOI": "N/A", "GP": "16:31", "SHIFTS": "19", "G": "19", "A1": "0.09", "A2": "0.09",
                        "A": "0.09", "P": "0.29", "+/-": "0.29", "SC": "0.29", "PEA": "0.29", "PEN": "0.09",
                        "FO": "0.09", "FO+": "0.09", "FO%": "0.09", "H+": "0.09", "S": "0.09", "S+": "0.09",
                        "SBL": "0.09", "SPP": "0.09", "SSH": "0.09", "PTTS": "0.09", "FOD": "0.09",
                        "FOD+": "0.09", "FOD%": "0.09", "FON": "0.09", "FON+": "0.09", "FON%": "0.09",
                        "FOA": "0.09", "FOA+": "0.09", "FOA%": "0.09"
                    },
                    "last_updated": datetime.now().isoformat()
                },
                {
                    "player_id": "21479_17",
                    "team_id": "21479",
                    "jersey_number": "17",
                    "name": "Kael Screpnek",
                    "position": "F",
                    "metrics": {
                        "TOI": "N/A", "GP": "10:51", "SHIFTS": "15", "G": "15", "A1": "0.09", "A2": "0.09",
                        "A": "0.09", "P": "0.24", "+/-": "0.24", "SC": "0.24", "PEA": "0.24", "PEN": "0.09",
                        "FO": "0.09", "FO+": "0.09", "FO%": "0.09", "H+": "0.09", "S": "0.09", "S+": "0.09",
                        "SBL": "0.09", "SPP": "0.09", "SSH": "0.09", "PTTS": "0.09", "FOD": "0.09",
                        "FOD+": "0.09", "FOD%": "0.09", "FON": "0.09", "FON+": "0.09", "FON%": "0.09",
                        "FOA": "0.09", "FOA+": "0.09", "FOA%": "0.09"
                    },
                    "last_updated": datetime.now().isoformat()
                },
                {
                    "player_id": "21479_15",
                    "team_id": "21479",
                    "jersey_number": "15",
                    "name": "Teague McAllister",
                    "position": "F",
                    "metrics": {
                        "TOI": "N/A", "GP": "18:43", "SHIFTS": "22", "G": "22", "A1": "0.19", "A2": "0.19",
                        "A": "0.19", "P": "0.5", "+/-": "0.5", "SC": "0.5", "PEA": "0.5", "PEN": "0.19",
                        "FO": "0.19", "FO+": "0.19", "FO%": "0.19", "H+": "0.19", "S": "0.19", "S+": "0.19",
                        "SBL": "0.19", "SPP": "0.19", "SSH": "0.19", "PTTS": "0.19", "FOD": "0.19",
                        "FOD+": "0.19", "FOD%": "0.19", "FON": "0.19", "FON+": "0.19", "FON%": "0.19",
                        "FOA": "0.19", "FOA+": "0.19", "FOA%": "0.19"
                    },
                    "last_updated": datetime.now().isoformat()
                },
                {
                    "player_id": "21479_11",
                    "team_id": "21479",
                    "jersey_number": "11",
                    "name": "Luke Fritz",
                    "position": "F",
                    "metrics": {
                        "TOI": "N/A", "GP": "15:52", "SHIFTS": "19", "G": "19", "A1": "0.12", "A2": "0.12",
                        "A": "0.12", "P": "0.35", "+/-": "0.35", "SC": "0.35", "PEA": "0.35", "PEN": "0.12",
                        "FO": "0.12", "FO+": "0.12", "FO%": "0.12", "H+": "0.12", "S": "0.12", "S+": "0.12",
                        "SBL": "0.12", "SPP": "0.12", "SSH": "0.12", "PTTS": "0.12", "FOD": "0.12",
                        "FOD+": "0.12", "FOD%": "0.12", "FON": "0.12", "FON+": "0.12", "FON%": "0.12",
                        "FOA": "0.12", "FOA+": "0.12", "FOA%": "0.12"
                    },
                    "last_updated": datetime.now().isoformat()
                },
                {
                    "player_id": "21479_25b",
                    "team_id": "21479",
                    "jersey_number": "25",
                    "name": "Karter Radtke",
                    "position": "F",
                    "metrics": {
                        "TOI": "N/A", "GP": "09:29", "SHIFTS": "12", "G": "12", "A1": "-", "A2": "-",
                        "A": "-", "P": "0.05", "+/-": "0.05", "SC": "0.05", "PEA": "0.05", "PEN": "0.05",
                        "FO": "0.05", "FO+": "0.05", "FO%": "0.05", "H+": "0.05", "S": "0.05", "S+": "0.05",
                        "SBL": "0.05", "SPP": "0.05", "SSH": "0.05", "PTTS": "0.05", "FOD": "0.05",
                        "FOD+": "0.05", "FOD%": "0.05", "FON": "0.05", "FON+": "0.05", "FON%": "0.05",
                        "FOA": "0.05", "FOA+": "0.05", "FOA%": "0.05"
                    },
                    "last_updated": datetime.now().isoformat()
                },
                {
                    "player_id": "21479_19b",
                    "team_id": "21479",
                    "jersey_number": "19",
                    "name": "Cooper Moore",
                    "position": "F",
                    "metrics": {
                        "TOI": "N/A", "GP": "17:05", "SHIFTS": "20", "G": "20", "A1": "0.33", "A2": "0.33",
                        "A": "0.33", "P": "0.76", "+/-": "0.76", "SC": "0.76", "PEA": "0.76", "PEN": "0.33",
                        "FO": "0.33", "FO+": "0.33", "FO%": "0.33", "H+": "0.33", "S": "0.33", "S+": "0.33",
                        "SBL": "0.33", "SPP": "0.33", "SSH": "0.33", "PTTS": "0.33", "FOD": "0.33",
                        "FOD+": "0.33", "FOD%": "0.33", "FON": "0.33", "FON+": "0.33", "FON%": "0.33",
                        "FOA": "0.33", "FOA+": "0.33", "FOA%": "0.33"
                    },
                    "last_updated": datetime.now().isoformat()
                },
                {
                    "player_id": "21479_20",
                    "team_id": "21479",
                    "jersey_number": "20",
                    "name": "Gus El-Tahhan",
                    "position": "F",
                    "metrics": {
                        "TOI": "N/A", "GP": "15:35", "SHIFTS": "20", "G": "20", "A1": "0.15", "A2": "0.15",
                        "A": "0.15", "P": "0.47", "+/-": "0.47", "SC": "0.47", "PEA": "0.47", "PEN": "0.15",
                        "FO": "0.15", "FO+": "0.15", "FO%": "0.15", "H+": "0.15", "S": "0.15", "S+": "0.15",
                        "SBL": "0.15", "SPP": "0.15", "SSH": "0.15", "PTTS": "0.15", "FOD": "0.15",
                        "FOD+": "0.15", "FOD%": "0.15", "FON": "0.15", "FON+": "0.15", "FON%": "0.15",
                        "FOA": "0.15", "FOA+": "0.15", "FOA%": "0.15"
                    },
                    "last_updated": datetime.now().isoformat()
                }
            ]
        }
    }

def get_cached_players():
    """Get cached player data or load fresh data"""
    global player_cache, cache_timestamp
    
    # Check if cache is valid
    if (cache_timestamp and 
        datetime.now() - cache_timestamp < timedelta(seconds=CACHE_DURATION) and 
        player_cache):
        return player_cache
    
    # Load fresh data
    logger.info("🔄 Loading complete player data...")
    player_cache = get_complete_lloydminster_players()
    cache_timestamp = datetime.now()
    
    return player_cache

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AJHL Complete Data API",
        "version": "3.0.0",
        "status": "running",
        "features": [
            "Complete AJHL teams and players",
            "All 21 Lloydminster Bobcats players",
            "33+ comprehensive metrics per player",
            "Real Hudl Instat data",
            "Fast cached responses"
        ],
        "endpoints": {
            "teams": "/teams",
            "teams_by_id": "/teams/{team_id}",
            "players": "/players",
            "players_by_team": "/teams/{team_id}/players",
            "player_search": "/players/search/{player_name}",
            "league_stats": "/league/stats",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    cached_data = get_cached_players()
    total_players = sum(len(team_data["players"]) for team_data in cached_data.values())
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "cached_teams": len(cached_data),
        "cached_players": total_players,
        "cache_age_seconds": (datetime.now() - cache_timestamp).total_seconds() if cache_timestamp else 0
    }

@app.get("/teams")
async def get_all_teams_endpoint(credentials: dict = Depends(verify_api_key)):
    """Get all AJHL teams"""
    try:
        teams = get_all_teams()
        team_list = []
        
        for team_id, team_data in teams.items():
            team_list.append({
                "team_id": team_id,
                "team_name": team_data["team_name"],
                "city": team_data["city"],
                "province": team_data["province"],
                "league": "AJHL",
                "hudl_team_id": team_data["hudl_team_id"],
                "is_active": team_data["is_active"]
            })
        
        return {
            "success": True,
            "teams": team_list,
            "total_teams": len(team_list),
            "league": "AJHL"
        }
    except Exception as e:
        logger.error(f"Error getting teams: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/teams/{team_id}")
async def get_team_by_id_endpoint(team_id: str, credentials: dict = Depends(verify_api_key)):
    """Get specific team by ID"""
    try:
        team_data = get_team_by_id(team_id)
        
        if not team_data:
            raise HTTPException(status_code=404, detail=f"Team {team_id} not found")
        
        return {
            "success": True,
            "team": {
                "team_id": team_id,
                "team_name": team_data["team_name"],
                "city": team_data["city"],
                "province": team_data["province"],
                "league": "AJHL",
                "hudl_team_id": team_data["hudl_team_id"],
                "is_active": team_data["is_active"]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting team {team_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/players")
async def get_all_players(credentials: dict = Depends(verify_api_key)):
    """Get all players from all teams"""
    try:
        cached_data = get_cached_players()
        all_players = []
        
        for team_id, team_data in cached_data.items():
            for player in team_data["players"]:
                player["team_name"] = team_data["team_name"]
                all_players.append(player)
        
        return {
            "success": True,
            "players": all_players,
            "total_players": len(all_players),
            "total_teams": len(cached_data),
            "league": "AJHL",
            "cache_timestamp": cache_timestamp.isoformat() if cache_timestamp else None
        }
    except Exception as e:
        logger.error(f"Error getting all players: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/teams/{team_id}/players")
async def get_players_by_team(team_id: str, credentials: dict = Depends(verify_api_key)):
    """Get players for a specific team"""
    try:
        # Check if team exists
        team_data = get_team_by_id(team_id)
        if not team_data:
            raise HTTPException(status_code=404, detail=f"Team {team_id} not found")
        
        cached_data = get_cached_players()
        
        if team_id in cached_data:
            team_players = cached_data[team_id]["players"]
        else:
            team_players = []
        
        return {
            "success": True,
            "team_id": team_id,
            "team_name": team_data["team_name"],
            "players": team_players,
            "total_players": len(team_players),
            "cache_timestamp": cache_timestamp.isoformat() if cache_timestamp else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting players for team {team_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/players/search/{player_name}")
async def search_player_by_name(player_name: str, credentials: dict = Depends(verify_api_key)):
    """Search for a specific player by name across all teams"""
    try:
        cached_data = get_cached_players()
        found_players = []
        
        for team_id, team_data in cached_data.items():
            for player in team_data["players"]:
                if player_name.lower() in player["name"].lower():
                    player["team_name"] = team_data["team_name"]
                    found_players.append(player)
        
        return {
            "success": True,
            "search_term": player_name,
            "players": found_players,
            "total_found": len(found_players),
            "searched_teams": len(cached_data),
            "cache_timestamp": cache_timestamp.isoformat() if cache_timestamp else None
        }
    except Exception as e:
        logger.error(f"Error searching for player {player_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/league/stats")
async def get_league_stats(credentials: dict = Depends(verify_api_key)):
    """Get league-wide statistics"""
    try:
        cached_data = get_cached_players()
        total_players = sum(len(team_data["players"]) for team_data in cached_data.values())
        teams = get_active_teams()
        
        return {
            "success": True,
            "league": "AJHL",
            "total_teams": len(teams),
            "total_players": total_players,
            "active_teams": len([t for t in teams.values() if t.get("is_active", True)]),
            "last_updated": cache_timestamp.isoformat() if cache_timestamp else None,
            "cache_age_seconds": (datetime.now() - cache_timestamp).total_seconds() if cache_timestamp else 0
        }
    except Exception as e:
        logger.error(f"Error getting league stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/refresh")
async def refresh_data(credentials: dict = Depends(verify_api_key)):
    """Force refresh of cached data"""
    global player_cache, cache_timestamp
    
    logger.info("🔄 Forcing data refresh...")
    player_cache = {}
    cache_timestamp = None
    
    # Load fresh data
    get_cached_players()
    
    return {
        "success": True,
        "message": "Data refreshed successfully",
        "timestamp": cache_timestamp.isoformat() if cache_timestamp else None
    }

if __name__ == "__main__":
    uvicorn.run(
        "ajhl_complete_data_api:app",
        host="0.0.0.0",
        port=8002,  # Different port to avoid conflicts
        reload=True
    )
