#!/usr/bin/env python3
"""
AJHL Fast API - Optimized for speed with caching and background processing
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
    title="AJHL Fast API",
    description="High-performance API for all AJHL teams and players",
    version="2.0.0"
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

# Sample player data (would be replaced with real scraping)
def get_sample_players_data():
    """Get comprehensive sample player data for all teams"""
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
                        "TOI": "12:04", "GP": "6", "SHIFTS": "15", "G": "0", "A1": "0", "A2": "0",
                        "A": "0", "P": "0", "+/-": "0", "SC": "-0.17", "PEA": "0.33", "PEN": "0.17",
                        "FO": "0", "FO+": "8", "FO%": "4.8", "H+": "59%", "S": "0.5", "S+": "1.5",
                        "SBL": "0.83", "SPP": "0.5", "SSH": "0.17", "PTTS": "0", "FOD": "0.5",
                        "FOD+": "2", "FOD%": "0.67", "FON": "33%", "FON+": "2.3", "FON%": "1.5",
                        "FOA": "64%", "FOA+": "3.8", "FOA%": "2.7"
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
                        "TOI": "16:18", "GP": "60", "SHIFTS": "20", "G": "12", "A1": "15", "A2": "13",
                        "A": "28", "P": "40", "+/-": "10", "SC": "0.2", "PEA": "0.25", "PEN": "0.22",
                        "FO": "45", "FO+": "23", "FO%": "51.1", "H+": "67%", "S": "2.1", "S+": "1.8",
                        "SBL": "1.2", "SPP": "0.8", "SSH": "0.3", "PTTS": "12", "FOD": "18",
                        "FOD+": "9", "FOD%": "50.0", "FON": "15", "FON+": "8", "FON%": "53.3",
                        "FOA": "12", "FOA+": "6", "FOA%": "50.0"
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
                        "TOI": "18:07", "GP": "24", "SHIFTS": "21", "G": "8", "A1": "6", "A2": "3",
                        "A": "9", "P": "17", "+/-": "-3", "SC": "0.33", "PEA": "0.25", "PEN": "0.13",
                        "FO": "32", "FO+": "16", "FO%": "50.0", "H+": "45%", "S": "1.8", "S+": "1.5",
                        "SBL": "0.9", "SPP": "0.6", "SSH": "0.2", "PTTS": "8", "FOD": "12",
                        "FOD+": "6", "FOD%": "50.0", "FON": "10", "FON+": "5", "FON%": "50.0",
                        "FOA": "10", "FOA+": "5", "FOA%": "50.0"
                    },
                    "last_updated": datetime.now().isoformat()
                }
            ]
        },
        "21480": {  # Brooks Bandits
            "team_name": "Brooks Bandits",
            "players": [
                {
                    "player_id": "21480_7",
                    "team_id": "21480",
                    "jersey_number": "7",
                    "name": "Sample Player 1",
                    "position": "F",
                    "metrics": {
                        "TOI": "15:30", "GP": "25", "SHIFTS": "18", "G": "10", "A1": "8", "A2": "5",
                        "A": "13", "P": "23", "+/-": "5", "SC": "0.4", "PEA": "0.3", "PEN": "0.2"
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
    logger.info("🔄 Loading fresh player data...")
    player_cache = get_sample_players_data()
    cache_timestamp = datetime.now()
    
    return player_cache

# Helper functions for team analysis
def calculate_team_metrics(team_players):
    """Calculate comprehensive team metrics from player data"""
    if not team_players:
        return {
            "total_players": 0,
            "forwards": 0,
            "defensemen": 0,
            "goalies": 0,
            "avg_toi": "0:00",
            "total_goals": 0,
            "total_assists": 0,
            "total_points": 0,
            "avg_plus_minus": 0.0,
            "total_faceoffs": 0,
            "faceoff_percentage": 0.0,
            "total_shots": 0.0,
            "avg_shot_percentage": 0.0
        }
    
    forwards = [p for p in team_players if p["position"] == "F"]
    defensemen = [p for p in team_players if p["position"] == "D"]
    goalies = [p for p in team_players if p["position"] == "G"]
    
    # Calculate totals
    total_goals = sum(int(p["metrics"].get("G", 0)) for p in team_players)
    total_assists = sum(int(p["metrics"].get("A", 0)) for p in team_players)
    total_points = total_goals + total_assists
    total_plus_minus = sum(int(p["metrics"].get("+/-", 0)) for p in team_players)
    total_faceoffs = sum(int(p["metrics"].get("FO", 0)) for p in team_players)
    total_faceoff_wins = sum(int(p["metrics"].get("FO+", 0)) for p in team_players)
    total_shots = sum(float(p["metrics"].get("S", 0)) for p in team_players)
    
    # Calculate averages
    avg_plus_minus = round(total_plus_minus / len(team_players), 2) if team_players else 0
    faceoff_percentage = round((total_faceoff_wins / total_faceoffs * 100), 1) if total_faceoffs > 0 else 0
    avg_shot_percentage = round((total_goals / total_shots * 100), 1) if total_shots > 0 else 0
    
    # Calculate average TOI
    total_toi_minutes = 0
    for player in team_players:
        toi_str = player["metrics"].get("TOI", "0:00")
        if ":" in toi_str:
            minutes, seconds = map(int, toi_str.split(":"))
            total_toi_minutes += minutes + (seconds / 60)
    
    avg_toi_minutes = total_toi_minutes / len(team_players) if team_players else 0
    avg_toi = f"{int(avg_toi_minutes)}:{int((avg_toi_minutes % 1) * 60):02d}"
    
    return {
        "total_players": len(team_players),
        "forwards": len(forwards),
        "defensemen": len(defensemen),
        "goalies": len(goalies),
        "avg_toi": avg_toi,
        "total_goals": total_goals,
        "total_assists": total_assists,
        "total_points": total_points,
        "avg_plus_minus": avg_plus_minus,
        "total_faceoffs": total_faceoffs,
        "faceoff_percentage": faceoff_percentage,
        "total_shots": round(total_shots, 1),
        "avg_shot_percentage": avg_shot_percentage
    }

def get_top_performers(team_players, metric="P", top_n=5):
    """Get top performers by a specific metric"""
    if not team_players:
        return []
    
    # Sort by metric (points by default)
    sorted_players = sorted(team_players, 
                           key=lambda x: int(x["metrics"].get(metric, 0)), 
                           reverse=True)
    
    top_performers = []
    for player in sorted_players[:top_n]:
        top_performers.append({
            "name": player["name"],
            "jersey_number": player["jersey_number"],
            "position": player["position"],
            "value": int(player["metrics"].get(metric, 0)),
            "goals": int(player["metrics"].get("G", 0)),
            "assists": int(player["metrics"].get("A", 0)),
            "points": int(player["metrics"].get("P", 0)),
            "plus_minus": int(player["metrics"].get("+/-", 0)),
            "toi": player["metrics"].get("TOI", "0:00")
        })
    
    return top_performers

def analyze_team_depth(team_players):
    """Analyze team depth by position"""
    forwards = [p for p in team_players if p["position"] == "F"]
    defensemen = [p for p in team_players if p["position"] == "D"]
    goalies = [p for p in team_players if p["position"] == "G"]
    
    # Sort forwards by points
    forwards_sorted = sorted(forwards, key=lambda x: int(x["metrics"].get("P", 0)), reverse=True)
    
    # Sort defensemen by points
    defensemen_sorted = sorted(defensemen, key=lambda x: int(x["metrics"].get("P", 0)), reverse=True)
    
    # Sort goalies by games played (as proxy for usage)
    goalies_sorted = sorted(goalies, key=lambda x: int(x["metrics"].get("GP", 0)), reverse=True)
    
    return {
        "forwards": {
            "total": len(forwards),
            "top_line": [{"name": f["name"], "jersey": f["jersey_number"], "points": int(f["metrics"].get("P", 0))} for f in forwards_sorted[:3]],
            "second_line": [{"name": f["name"], "jersey": f["jersey_number"], "points": int(f["metrics"].get("P", 0))} for f in forwards_sorted[3:6]],
            "third_line": [{"name": f["name"], "jersey": f["jersey_number"], "points": int(f["metrics"].get("P", 0))} for f in forwards_sorted[6:9]]
        },
        "defensemen": {
            "total": len(defensemen),
            "top_pair": [{"name": d["name"], "jersey": d["jersey_number"], "points": int(d["metrics"].get("P", 0))} for d in defensemen_sorted[:2]],
            "second_pair": [{"name": d["name"], "jersey": d["jersey_number"], "points": int(d["metrics"].get("P", 0))} for d in defensemen_sorted[2:4]],
            "third_pair": [{"name": d["name"], "jersey": d["jersey_number"], "points": int(d["metrics"].get("P", 0))} for d in defensemen_sorted[4:6]]
        },
        "goalies": {
            "total": len(goalies),
            "starter": {"name": goalies_sorted[0]["name"], "jersey": goalies_sorted[0]["jersey_number"], "gp": int(goalies_sorted[0]["metrics"].get("GP", 0))} if goalies_sorted else None,
            "backup": {"name": goalies_sorted[1]["name"], "jersey": goalies_sorted[1]["jersey_number"], "gp": int(goalies_sorted[1]["metrics"].get("GP", 0))} if len(goalies_sorted) > 1 else None
        }
    }

def calculate_league_rankings(all_teams_data):
    """Calculate league-wide team rankings"""
    team_stats = []
    
    for team_id, team_data in all_teams_data.items():
        players = team_data["players"]
        metrics = calculate_team_metrics(players)
        
        team_stats.append({
            "team_id": team_id,
            "team_name": team_data["team_name"],
            "total_points": metrics["total_points"],
            "total_goals": metrics["total_goals"],
            "faceoff_percentage": metrics["faceoff_percentage"],
            "avg_plus_minus": metrics["avg_plus_minus"],
            "total_players": metrics["total_players"]
        })
    
    # Sort by different metrics
    rankings = {
        "by_points": sorted(team_stats, key=lambda x: x["total_points"], reverse=True),
        "by_goals": sorted(team_stats, key=lambda x: x["total_goals"], reverse=True),
        "by_faceoff_percentage": sorted(team_stats, key=lambda x: x["faceoff_percentage"], reverse=True),
        "by_plus_minus": sorted(team_stats, key=lambda x: x["avg_plus_minus"], reverse=True)
    }
    
    return rankings

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AJHL Fast API",
        "version": "2.0.0",
        "status": "running",
        "features": [
            "All AJHL teams and players",
            "Fast cached responses",
            "Player search across all teams",
            "Comprehensive player metrics",
            "Real-time data updates"
        ],
        "endpoints": {
            "teams": "/teams",
            "teams_by_id": "/teams/{team_id}",
            "players": "/players",
            "players_by_team": "/teams/{team_id}/players",
            "player_search": "/players/search/{player_name}",
            "league_stats": "/league/stats",
            "team_comparison": "/teams/compare/{team1_id}/{team2_id}",
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
    """Get comprehensive team data including player metrics and team statistics"""
    try:
        team_data = get_team_by_id(team_id)
        
        if not team_data:
            raise HTTPException(status_code=404, detail=f"Team {team_id} not found")
        
        # Get team players
        cached_data = get_cached_players()
        team_players = cached_data.get(team_id, {}).get("players", [])
        
        # Calculate team metrics
        team_metrics = calculate_team_metrics(team_players)
        
        # Get top performers
        top_scorers = get_top_performers(team_players, "P", 5)
        top_goal_scorers = get_top_performers(team_players, "G", 5)
        top_assists = get_top_performers(team_players, "A", 5)
        
        # Analyze team depth
        depth_analysis = analyze_team_depth(team_players)
        
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
            "team_metrics": team_metrics,
            "performance_analysis": {
                "top_scorers": top_scorers,
                "top_goal_scorers": top_goal_scorers,
                "top_assists": top_assists
            },
            "depth_analysis": depth_analysis,
            "roster_summary": {
                "total_players": len(team_players),
                "forwards": len([p for p in team_players if p["position"] == "F"]),
                "defensemen": len([p for p in team_players if p["position"] == "D"]),
                "goalies": len([p for p in team_players if p["position"] == "G"])
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
    """Get comprehensive league-wide statistics and rankings"""
    try:
        cached_data = get_cached_players()
        total_players = sum(len(team_data["players"]) for team_data in cached_data.values())
        teams = get_active_teams()
        
        # Calculate league-wide metrics
        all_players = []
        for team_data in cached_data.values():
            all_players.extend(team_data["players"])
        
        # League totals
        league_totals = {
            "total_goals": sum(int(p["metrics"].get("G", 0)) for p in all_players),
            "total_assists": sum(int(p["metrics"].get("A", 0)) for p in all_players),
            "total_points": sum(int(p["metrics"].get("P", 0)) for p in all_players),
            "total_faceoffs": sum(int(p["metrics"].get("FO", 0)) for p in all_players),
            "total_faceoff_wins": sum(int(p["metrics"].get("FO+", 0)) for p in all_players),
            "total_shots": sum(float(p["metrics"].get("S", 0)) for p in all_players)
        }
        
        # Calculate league averages
        league_averages = {
            "avg_goals_per_team": round(league_totals["total_goals"] / len(cached_data), 1) if cached_data else 0,
            "avg_points_per_team": round(league_totals["total_points"] / len(cached_data), 1) if cached_data else 0,
            "avg_players_per_team": round(total_players / len(cached_data), 1) if cached_data else 0,
            "league_faceoff_percentage": round((league_totals["total_faceoff_wins"] / league_totals["total_faceoffs"] * 100), 1) if league_totals["total_faceoffs"] > 0 else 0,
            "league_shot_percentage": round((league_totals["total_goals"] / league_totals["total_shots"] * 100), 1) if league_totals["total_shots"] > 0 else 0
        }
        
        # Get team rankings
        team_rankings = calculate_league_rankings(cached_data)
        
        # Get league leaders
        league_leaders = {
            "top_scorers": sorted(all_players, key=lambda x: int(x["metrics"].get("P", 0)), reverse=True)[:10],
            "top_goal_scorers": sorted(all_players, key=lambda x: int(x["metrics"].get("G", 0)), reverse=True)[:10],
            "top_assists": sorted(all_players, key=lambda x: int(x["metrics"].get("A", 0)), reverse=True)[:10],
            "top_plus_minus": sorted(all_players, key=lambda x: int(x["metrics"].get("+/-", 0)), reverse=True)[:10]
        }
        
        # Position breakdown
        forwards = [p for p in all_players if p["position"] == "F"]
        defensemen = [p for p in all_players if p["position"] == "D"]
        goalies = [p for p in all_players if p["position"] == "G"]
        
        position_breakdown = {
            "forwards": {
                "count": len(forwards),
                "avg_points": round(sum(int(f["metrics"].get("P", 0)) for f in forwards) / len(forwards), 1) if forwards else 0,
                "avg_goals": round(sum(int(f["metrics"].get("G", 0)) for f in forwards) / len(forwards), 1) if forwards else 0
            },
            "defensemen": {
                "count": len(defensemen),
                "avg_points": round(sum(int(d["metrics"].get("P", 0)) for d in defensemen) / len(defensemen), 1) if defensemen else 0,
                "avg_goals": round(sum(int(d["metrics"].get("G", 0)) for d in defensemen) / len(defensemen), 1) if defensemen else 0
            },
            "goalies": {
                "count": len(goalies),
                "avg_games_played": round(sum(int(g["metrics"].get("GP", 0)) for g in goalies) / len(goalies), 1) if goalies else 0
            }
        }
        
        return {
            "success": True,
            "league": "AJHL",
            "overview": {
                "total_teams": len(teams),
                "total_players": total_players,
                "active_teams": len([t for t in teams.values() if t.get("is_active", True)]),
                "last_updated": cache_timestamp.isoformat() if cache_timestamp else None,
                "cache_age_seconds": (datetime.now() - cache_timestamp).total_seconds() if cache_timestamp else 0
            },
            "league_totals": league_totals,
            "league_averages": league_averages,
            "team_rankings": team_rankings,
            "league_leaders": league_leaders,
            "position_breakdown": position_breakdown
        }
    except Exception as e:
        logger.error(f"Error getting league stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/teams/compare/{team1_id}/{team2_id}")
async def compare_teams(team1_id: str, team2_id: str, credentials: dict = Depends(verify_api_key)):
    """Compare two teams head-to-head"""
    try:
        # Get team data
        team1_data = get_team_by_id(team1_id)
        team2_data = get_team_by_id(team2_id)
        
        if not team1_data:
            raise HTTPException(status_code=404, detail=f"Team {team1_id} not found")
        if not team2_data:
            raise HTTPException(status_code=404, detail=f"Team {team2_id} not found")
        
        # Get team players
        cached_data = get_cached_players()
        team1_players = cached_data.get(team1_id, {}).get("players", [])
        team2_players = cached_data.get(team2_id, {}).get("players", [])
        
        # Calculate metrics for both teams
        team1_metrics = calculate_team_metrics(team1_players)
        team2_metrics = calculate_team_metrics(team2_players)
        
        # Compare metrics
        comparison = {
            "total_points": {
                "team1": team1_metrics["total_points"],
                "team2": team2_metrics["total_points"],
                "winner": team1_id if team1_metrics["total_points"] > team2_metrics["total_points"] else team2_id
            },
            "total_goals": {
                "team1": team1_metrics["total_goals"],
                "team2": team2_metrics["total_goals"],
                "winner": team1_id if team1_metrics["total_goals"] > team2_metrics["total_goals"] else team2_id
            },
            "faceoff_percentage": {
                "team1": team1_metrics["faceoff_percentage"],
                "team2": team2_metrics["faceoff_percentage"],
                "winner": team1_id if team1_metrics["faceoff_percentage"] > team2_metrics["faceoff_percentage"] else team2_id
            },
            "avg_plus_minus": {
                "team1": team1_metrics["avg_plus_minus"],
                "team2": team2_metrics["avg_plus_minus"],
                "winner": team1_id if team1_metrics["avg_plus_minus"] > team2_metrics["avg_plus_minus"] else team2_id
            }
        }
        
        return {
            "success": True,
            "comparison": {
                "team1": {
                    "team_id": team1_id,
                    "team_name": team1_data["team_name"],
                    "metrics": team1_metrics
                },
                "team2": {
                    "team_id": team2_id,
                    "team_name": team2_data["team_name"],
                    "metrics": team2_metrics
                },
                "head_to_head": comparison
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing teams {team1_id} vs {team2_id}: {e}")
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
        "ajhl_fast_api:app",
        host="0.0.0.0",
        port=8001,  # Different port to avoid conflicts
        reload=True
    )
