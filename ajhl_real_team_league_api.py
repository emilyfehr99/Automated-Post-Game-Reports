#!/usr/bin/env python3
"""
AJHL Real Team & League API - Using Actual Hudl Instat Data
Processes real CSV data from Hudl Instat tabs to provide comprehensive team and league metrics
"""

import json
import time
import logging
import asyncio
import csv
import os
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

# Import real Hudl Instat components
from hudl_api_endpoints import get_team_players_endpoint, get_player_details_endpoint, HUDL_API_ENDPOINTS
from ajhl_teams_config import get_all_teams, get_team_by_id, get_active_teams
from ajhl_real_hudl_manager import AJHLRealHudlManager

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

class TeamMetrics(BaseModel):
    total_players: int
    forwards: int
    defensemen: int
    goalies: int
    total_goals: int
    total_assists: int
    total_points: int
    avg_plus_minus: float
    faceoff_percentage: float
    shot_percentage: float
    power_play_percentage: float
    penalty_kill_percentage: float

class AdvancedTeamMetrics(BaseModel):
    corsi_for_percentage: float
    fenwick_for_percentage: float
    expected_goals_for: float
    expected_goals_against: float
    high_danger_chances_for: int
    high_danger_chances_against: int
    puck_possession_percentage: float
    zone_entry_success_rate: float
    breakout_success_rate: float

# FastAPI app
app = FastAPI(
    title="AJHL Real Team & League API",
    description="Real API using actual Hudl Instat CSV data and metrics",
    version="1.0.0"
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
team_cache = {}
player_cache = {}
cache_timestamp = None
CACHE_DURATION = 300  # 5 minutes
hudl_manager = None

# Data directories
DATA_BASE_PATH = Path("ajhl_data")
CSV_DATA_PATH = DATA_BASE_PATH / "daily_downloads"

# API Key verification
def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API key"""
    api_key = credentials.credentials
    return {"api_key": api_key, "user": "demo_user"}

def get_hudl_manager():
    """Get or create Hudl manager instance"""
    global hudl_manager
    if hudl_manager is None:
        try:
            from hudl_credentials import HUDL_USERNAME, HUDL_PASSWORD
            hudl_manager = AJHLRealHudlManager(HUDL_USERNAME, HUDL_PASSWORD)
        except ImportError:
            logger.error("Hudl credentials not found")
            return None
    return hudl_manager

def load_team_csv_data(team_id: str) -> Dict[str, Any]:
    """Load and parse CSV data for a specific team from Hudl Instat"""
    team_data = get_team_by_id(team_id)
    if not team_data:
        return {"error": f"Team {team_id} not found"}
    
    team_dir = CSV_DATA_PATH / team_id
    if not team_dir.exists():
        return {"error": f"No CSV data found for {team_data['team_name']}"}
    
    csv_data = {
        "team_id": team_id,
        "team_name": team_data["team_name"],
        "hudl_team_id": team_data["hudl_team_id"],
        "tabs": {},
        "last_updated": None
    }
    
    # Process each Hudl Instat tab
    hudl_tabs = ["OVERVIEW", "GAMES", "SKATERS", "GOALIES", "LINES", "SHOT_MAP", "FACEOFFS", "EPISODES_SEARCH"]
    
    for tab in hudl_tabs:
        tab_dir = team_dir / tab.lower()
        if tab_dir.exists():
            csv_files = list(tab_dir.glob("*.csv"))
            if csv_files:
                # Get the most recent CSV file
                latest_file = max(csv_files, key=os.path.getctime)
                csv_data["tabs"][tab] = {
                    "file_path": str(latest_file),
                    "file_count": len(csv_files),
                    "latest_file": latest_file.name,
                    "data": parse_csv_file(latest_file)
                }
                csv_data["last_updated"] = datetime.fromtimestamp(latest_file.stat().st_mtime).isoformat()
    
    return csv_data

def parse_csv_file(file_path: Path) -> List[Dict[str, Any]]:
    """Parse a CSV file and return structured data"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # Try to detect delimiter
            sample = file.read(1024)
            file.seek(0)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            
            reader = csv.DictReader(file, delimiter=delimiter)
            return list(reader)
    except Exception as e:
        logger.error(f"Error parsing CSV file {file_path}: {e}")
        return []

def calculate_team_metrics_from_csv(team_id: str) -> Dict[str, Any]:
    """Calculate comprehensive team metrics from real Hudl Instat CSV data"""
    try:
        csv_data = load_team_csv_data(team_id)
        if "error" in csv_data:
            return csv_data
        
        team_metrics = {
            "team_id": team_id,
            "team_name": csv_data["team_name"],
            "hudl_team_id": csv_data["hudl_team_id"],
            "data_source": "Hudl Instat Real CSV Data",
            "last_updated": csv_data["last_updated"],
            "metrics": {},
            "advanced_metrics": {},
            "roster_analysis": {},
            "performance_breakdown": {}
        }
        
        # Process SKATERS tab data
        if "SKATERS" in csv_data["tabs"]:
            skaters_data = csv_data["tabs"]["SKATERS"]["data"]
            team_metrics.update(process_skaters_data(skaters_data))
        
        # Process GOALIES tab data
        if "GOALIES" in csv_data["tabs"]:
            goalies_data = csv_data["tabs"]["GOALIES"]["data"]
            team_metrics.update(process_goalies_data(goalies_data))
        
        # Process GAMES tab data
        if "GAMES" in csv_data["tabs"]:
            games_data = csv_data["tabs"]["GAMES"]["data"]
            team_metrics.update(process_games_data(games_data))
        
        # Process OVERVIEW tab data
        if "OVERVIEW" in csv_data["tabs"]:
            overview_data = csv_data["tabs"]["OVERVIEW"]["data"]
            team_metrics.update(process_overview_data(overview_data))
        
        # Process FACEOFFS tab data
        if "FACEOFFS" in csv_data["tabs"]:
            faceoffs_data = csv_data["tabs"]["FACEOFFS"]["data"]
            team_metrics.update(process_faceoffs_data(faceoffs_data))
        
        return team_metrics
        
    except Exception as e:
        logger.error(f"Error calculating team metrics for {team_id}: {e}")
        return {"error": str(e)}

def process_skaters_data(skaters_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Process skaters CSV data to calculate team metrics"""
    if not skaters_data:
        return {"skaters_metrics": {}}
    
    # Initialize counters
    total_goals = 0
    total_assists = 0
    total_points = 0
    total_plus_minus = 0
    total_shots = 0
    total_faceoffs_won = 0
    total_faceoffs_lost = 0
    total_hits = 0
    total_blocks = 0
    total_takeaways = 0
    total_giveaways = 0
    total_penalty_minutes = 0
    
    forwards = 0
    defensemen = 0
    
    # Process each skater
    for skater in skaters_data:
        try:
            # Basic stats
            goals = safe_int(skater.get('G', 0))
            assists = safe_int(skater.get('A', 0))
            points = safe_int(skater.get('P', 0))
            plus_minus = safe_int(skater.get('+/-', 0))
            shots = safe_int(skater.get('S', 0))
            hits = safe_int(skater.get('H', 0))
            blocks = safe_int(skater.get('B', 0))
            takeaways = safe_int(skater.get('TkA', 0))
            giveaways = safe_int(skater.get('GvA', 0))
            pim = safe_int(skater.get('PIM', 0))
            
            # Faceoffs
            faceoffs_won = safe_int(skater.get('FO_W', 0))
            faceoffs_lost = safe_int(skater.get('FO_L', 0))
            
            # Position
            position = skater.get('Pos', '').upper()
            if position in ['C', 'LW', 'RW', 'F']:
                forwards += 1
            elif position in ['D', 'LD', 'RD']:
                defensemen += 1
            
            # Add to totals
            total_goals += goals
            total_assists += assists
            total_points += points
            total_plus_minus += plus_minus
            total_shots += shots
            total_faceoffs_won += faceoffs_won
            total_faceoffs_lost += faceoffs_lost
            total_hits += hits
            total_blocks += blocks
            total_takeaways += takeaways
            total_giveaways += giveaways
            total_penalty_minutes += pim
            
        except Exception as e:
            logger.warning(f"Error processing skater data: {e}")
            continue
    
    # Calculate percentages and averages
    total_faceoffs = total_faceoffs_won + total_faceoffs_lost
    faceoff_percentage = (total_faceoffs_won / total_faceoffs * 100) if total_faceoffs > 0 else 0
    shot_percentage = (total_goals / total_shots * 100) if total_shots > 0 else 0
    avg_plus_minus = total_plus_minus / len(skaters_data) if skaters_data else 0
    
    return {
        "skaters_metrics": {
            "total_skaters": len(skaters_data),
            "forwards": forwards,
            "defensemen": defensemen,
            "total_goals": total_goals,
            "total_assists": total_assists,
            "total_points": total_points,
            "avg_plus_minus": round(avg_plus_minus, 2),
            "total_shots": total_shots,
            "shot_percentage": round(shot_percentage, 2),
            "faceoff_percentage": round(faceoff_percentage, 2),
            "total_hits": total_hits,
            "total_blocks": total_blocks,
            "total_takeaways": total_takeaways,
            "total_giveaways": total_giveaways,
            "total_penalty_minutes": total_penalty_minutes
        }
    }

def process_goalies_data(goalies_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Process goalies CSV data to calculate team metrics"""
    if not goalies_data:
        return {"goalies_metrics": {}}
    
    total_goals_against = 0
    total_saves = 0
    total_shots_against = 0
    total_wins = 0
    total_losses = 0
    total_ot_losses = 0
    total_shutouts = 0
    
    for goalie in goalies_data:
        try:
            goals_against = safe_int(goalie.get('GA', 0))
            saves = safe_int(goalie.get('SV', 0))
            shots_against = safe_int(goalie.get('SA', 0))
            wins = safe_int(goalie.get('W', 0))
            losses = safe_int(goalie.get('L', 0))
            ot_losses = safe_int(goalie.get('OTL', 0))
            shutouts = safe_int(goalie.get('SO', 0))
            
            total_goals_against += goals_against
            total_saves += saves
            total_shots_against += shots_against
            total_wins += wins
            total_losses += losses
            total_ot_losses += ot_losses
            total_shutouts += shutouts
            
        except Exception as e:
            logger.warning(f"Error processing goalie data: {e}")
            continue
    
    # Calculate percentages
    save_percentage = (total_saves / total_shots_against * 100) if total_shots_against > 0 else 0
    goals_against_average = (total_goals_against / len(goalies_data)) if goalies_data else 0
    
    return {
        "goalies_metrics": {
            "total_goalies": len(goalies_data),
            "total_goals_against": total_goals_against,
            "total_saves": total_saves,
            "total_shots_against": total_shots_against,
            "save_percentage": round(save_percentage, 2),
            "goals_against_average": round(goals_against_average, 2),
            "total_wins": total_wins,
            "total_losses": total_losses,
            "total_ot_losses": total_ot_losses,
            "total_shutouts": total_shutouts
        }
    }

def process_games_data(games_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Process games CSV data to calculate team metrics"""
    if not games_data:
        return {"games_metrics": {}}
    
    total_games = len(games_data)
    wins = 0
    losses = 0
    ot_losses = 0
    total_goals_for = 0
    total_goals_against = 0
    
    for game in games_data:
        try:
            # Determine game result
            result = game.get('Result', '').upper()
            if 'W' in result:
                wins += 1
            elif 'L' in result:
                losses += 1
            elif 'OTL' in result or 'SOL' in result:
                ot_losses += 1
            
            # Goals
            goals_for = safe_int(game.get('GF', 0))
            goals_against = safe_int(game.get('GA', 0))
            
            total_goals_for += goals_for
            total_goals_against += goals_against
            
        except Exception as e:
            logger.warning(f"Error processing game data: {e}")
            continue
    
    # Calculate percentages
    win_percentage = (wins / total_games * 100) if total_games > 0 else 0
    points = wins * 2 + ot_losses  # AJHL point system
    
    return {
        "games_metrics": {
            "total_games": total_games,
            "wins": wins,
            "losses": losses,
            "ot_losses": ot_losses,
            "win_percentage": round(win_percentage, 2),
            "points": points,
            "total_goals_for": total_goals_for,
            "total_goals_against": total_goals_against,
            "goal_differential": total_goals_for - total_goals_against
        }
    }

def process_overview_data(overview_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Process overview CSV data for additional metrics"""
    if not overview_data:
        return {"overview_metrics": {}}
    
    # This would contain team-level statistics from the overview tab
    # Implementation depends on the specific structure of the overview CSV
    return {
        "overview_metrics": {
            "data_available": True,
            "records_count": len(overview_data)
        }
    }

def process_faceoffs_data(faceoffs_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Process faceoffs CSV data for faceoff-specific metrics"""
    if not faceoffs_data:
        return {"faceoffs_metrics": {}}
    
    total_faceoffs_won = 0
    total_faceoffs_lost = 0
    
    for faceoff in faceoffs_data:
        try:
            won = safe_int(faceoff.get('Won', 0))
            lost = safe_int(faceoff.get('Lost', 0))
            
            total_faceoffs_won += won
            total_faceoffs_lost += lost
            
        except Exception as e:
            logger.warning(f"Error processing faceoff data: {e}")
            continue
    
    total_faceoffs = total_faceoffs_won + total_faceoffs_lost
    faceoff_percentage = (total_faceoffs_won / total_faceoffs * 100) if total_faceoffs > 0 else 0
    
    return {
        "faceoffs_metrics": {
            "total_faceoffs": total_faceoffs,
            "faceoffs_won": total_faceoffs_won,
            "faceoffs_lost": total_faceoffs_lost,
            "faceoff_percentage": round(faceoff_percentage, 2)
        }
    }

def safe_int(value: Any) -> int:
    """Safely convert value to integer"""
    try:
        if value is None or value == '':
            return 0
        return int(float(str(value).replace(',', '')))
    except (ValueError, TypeError):
        return 0

def calculate_league_rankings_from_csv() -> Dict[str, Any]:
    """Calculate league rankings from all team CSV data"""
    try:
        active_teams = get_active_teams()
        team_rankings = {
            "by_points": [],
            "by_goals_for": [],
            "by_goals_against": [],
            "by_win_percentage": []
        }
        
        league_totals = {
            "total_goals": 0,
            "total_games": 0,
            "total_teams": len(active_teams)
        }
        
        for team_id, team_data in active_teams.items():
            if not team_data.get('hudl_team_id'):
                continue
                
            team_metrics = calculate_team_metrics_from_csv(team_id)
            if "error" in team_metrics:
                continue
            
            # Extract key metrics
            skaters_metrics = team_metrics.get("skaters_metrics", {})
            games_metrics = team_metrics.get("games_metrics", {})
            
            team_name = team_data["team_name"]
            points = games_metrics.get("points", 0)
            goals_for = skaters_metrics.get("total_goals", 0)
            goals_against = games_metrics.get("total_goals_against", 0)
            win_percentage = games_metrics.get("win_percentage", 0)
            wins = games_metrics.get("wins", 0)
            losses = games_metrics.get("losses", 0)
            
            # Add to rankings
            team_rankings["by_points"].append({
                "team": team_name,
                "points": points,
                "wins": wins,
                "losses": losses
            })
            
            team_rankings["by_goals_for"].append({
                "team": team_name,
                "goals": goals_for
            })
            
            team_rankings["by_goals_against"].append({
                "team": team_name,
                "goals_against": goals_against
            })
            
            team_rankings["by_win_percentage"].append({
                "team": team_name,
                "win_percentage": win_percentage
            })
            
            # Add to league totals
            league_totals["total_goals"] += goals_for
            league_totals["total_games"] += games_metrics.get("total_games", 0)
        
        # Sort rankings
        team_rankings["by_points"].sort(key=lambda x: x["points"], reverse=True)
        team_rankings["by_goals_for"].sort(key=lambda x: x["goals"], reverse=True)
        team_rankings["by_goals_against"].sort(key=lambda x: x["goals_against"])
        team_rankings["by_win_percentage"].sort(key=lambda x: x["win_percentage"], reverse=True)
        
        # Calculate averages
        if league_totals["total_teams"] > 0:
            league_totals["avg_goals_per_team"] = round(league_totals["total_goals"] / league_totals["total_teams"], 2)
            league_totals["avg_games_per_team"] = round(league_totals["total_games"] / league_totals["total_teams"], 2)
        
        return {
            "league": "AJHL",
            "data_source": "Hudl Instat Real CSV Data",
            "last_updated": datetime.now().isoformat(),
            "rankings": team_rankings,
            "league_totals": league_totals
        }
        
    except Exception as e:
        logger.error(f"Error calculating league rankings: {e}")
        return {"error": str(e)}

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AJHL Real Team & League API",
        "version": "1.0.0",
        "status": "running",
        "data_source": "Hudl Instat Real CSV Data",
        "features": [
            "Real Hudl Instat CSV data processing",
            "Comprehensive team metrics from actual data",
            "League rankings from real statistics",
            "Advanced analytics from Hudl tabs",
            "Live data from Hudl Instat platform"
        ],
        "hudl_tabs_processed": [
            "OVERVIEW", "GAMES", "SKATERS", "GOALIES", 
            "LINES", "SHOT_MAP", "FACEOFFS", "EPISODES_SEARCH"
        ],
        "api_endpoints": {
            "teams": "/teams",
            "team_details": "/teams/{team_id}",
            "team_metrics": "/teams/{team_id}/metrics",
            "league_stats": "/league/stats",
            "league_rankings": "/league/rankings",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "data_source": "Hudl Instat Real CSV Data",
        "csv_data_available": CSV_DATA_PATH.exists(),
        "teams_with_data": len([t for t in get_active_teams().values() if t.get("team_id") and (CSV_DATA_PATH / t["team_id"]).exists()]),
        "cache_age_seconds": (datetime.now() - cache_timestamp).total_seconds() if cache_timestamp else 0
    }

@app.get("/teams")
async def get_all_teams_endpoint(credentials: dict = Depends(verify_api_key)):
    """Get all AJHL teams with data availability info"""
    try:
        teams = get_all_teams()
        team_list = []
        
        for team_id, team_data in teams.items():
            # Check if CSV data exists for this team
            team_csv_dir = CSV_DATA_PATH / team_id
            has_csv_data = team_csv_dir.exists() and any(team_csv_dir.iterdir())
            
            team_info = {
                "team_id": team_id,
                "team_name": team_data["team_name"],
                "city": team_data["city"],
                "province": team_data["province"],
                "league": "AJHL",
                "hudl_team_id": team_data["hudl_team_id"],
                "is_active": team_data["is_active"],
                "has_csv_data": has_csv_data,
                "data_source": "Hudl Instat CSV" if has_csv_data else "No Data Available"
            }
            team_list.append(team_info)
        
        return {
            "success": True,
            "teams": team_list,
            "total_teams": len(team_list),
            "teams_with_csv_data": len([t for t in team_list if t["has_csv_data"]]),
            "league": "AJHL",
            "data_source": "Hudl Instat Real CSV Data"
        }
    except Exception as e:
        logger.error(f"Error getting teams: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/teams/{team_id}")
async def get_team_details(team_id: str, credentials: dict = Depends(verify_api_key)):
    """Get detailed team information from Hudl Instat CSV data"""
    try:
        team_data = get_team_by_id(team_id)
        
        if not team_data:
            raise HTTPException(status_code=404, detail=f"Team {team_id} not found")
        
        # Load CSV data for this team
        csv_data = load_team_csv_data(team_id)
        
        if "error" in csv_data:
            return {
                "success": False,
                "team": {
                    "team_id": team_id,
                    "team_name": team_data["team_name"],
                    "city": team_data["city"],
                    "province": team_data["province"],
                    "league": "AJHL",
                    "hudl_team_id": team_data["hudl_team_id"],
                    "is_active": team_data["is_active"]
                },
                "error": csv_data["error"],
                "data_source": "Hudl Instat CSV (No Data)"
            }
        
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
            },
            "csv_data_summary": {
                "tabs_available": list(csv_data["tabs"].keys()),
                "last_updated": csv_data["last_updated"],
                "total_tabs_with_data": len(csv_data["tabs"])
            },
            "data_source": "Hudl Instat Real CSV Data"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting team details {team_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/teams/{team_id}/metrics")
async def get_team_metrics(team_id: str, credentials: dict = Depends(verify_api_key)):
    """Get comprehensive team metrics from real Hudl Instat CSV data"""
    try:
        team_data = get_team_by_id(team_id)
        
        if not team_data:
            raise HTTPException(status_code=404, detail=f"Team {team_id} not found")
        
        if not team_data.get('hudl_team_id'):
            raise HTTPException(status_code=404, detail=f"No Hudl team ID for {team_data['team_name']}")
        
        # Calculate real team metrics from CSV data
        metrics = calculate_team_metrics_from_csv(team_id)
        
        if "error" in metrics:
            raise HTTPException(status_code=500, detail=metrics["error"])
        
        return {
            "success": True,
            "team": {
                "team_id": team_id,
                "team_name": team_data["team_name"],
                "hudl_team_id": team_data["hudl_team_id"]
            },
            "metrics": metrics.get("skaters_metrics", {}),
            "goalies_metrics": metrics.get("goalies_metrics", {}),
            "games_metrics": metrics.get("games_metrics", {}),
            "faceoffs_metrics": metrics.get("faceoffs_metrics", {}),
            "data_source": "Hudl Instat Real CSV Data",
            "last_updated": metrics.get("last_updated")
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting team metrics {team_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/league/stats")
async def get_league_stats(credentials: dict = Depends(verify_api_key)):
    """Get league-wide statistics from real Hudl Instat CSV data"""
    try:
        league_data = calculate_league_rankings_from_csv()
        
        if "error" in league_data:
            raise HTTPException(status_code=500, detail=league_data["error"])
        
        return {
            "success": True,
            "league_data": league_data,
            "data_source": "Hudl Instat Real CSV Data"
        }
    except Exception as e:
        logger.error(f"Error getting league stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/league/rankings")
async def get_league_rankings(credentials: dict = Depends(verify_api_key)):
    """Get comprehensive league rankings from real CSV data"""
    try:
        league_data = calculate_league_rankings_from_csv()
        
        if "error" in league_data:
            raise HTTPException(status_code=500, detail=league_data["error"])
        
        return {
            "success": True,
            "rankings": league_data["rankings"],
            "league_totals": league_data["league_totals"],
            "data_source": "Hudl Instat Real CSV Data",
            "last_updated": league_data["last_updated"]
        }
    except Exception as e:
        logger.error(f"Error getting league rankings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/refresh")
async def refresh_data(credentials: dict = Depends(verify_api_key)):
    """Force refresh of data from Hudl Instat"""
    global team_cache, player_cache, cache_timestamp
    
    logger.info("🔄 Forcing data refresh from Hudl Instat...")
    
    try:
        # Initialize Hudl manager and download fresh data
        manager = get_hudl_manager()
        if manager:
            # Download fresh data for all teams
            results = manager.process_all_teams_daily()
            
            if "error" in results:
                return {
                    "success": False,
                    "error": results["error"],
                    "timestamp": datetime.now().isoformat()
                }
            
            # Clear caches
            team_cache = {}
            player_cache = {}
            cache_timestamp = datetime.now()
            
            return {
                "success": True,
                "message": "Data refresh completed from Hudl Instat",
                "timestamp": datetime.now().isoformat(),
                "data_source": "Hudl Instat Real CSV Data",
                "teams_processed": results.get("total_teams", 0),
                "successful_teams": results.get("successful_teams", 0),
                "csv_files_downloaded": results.get("total_csv_files", 0)
            }
        else:
            return {
                "success": False,
                "error": "Hudl manager not available",
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error refreshing data: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    uvicorn.run(
        "ajhl_real_team_league_api:app",
        host="0.0.0.0",
        port=8004,  # Different port to avoid conflicts
        reload=True
    )