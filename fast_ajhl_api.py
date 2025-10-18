#!/usr/bin/env python3
"""
Fast AJHL API - Serves data from database
No real-time scraping, just fast database queries
"""

import sqlite3
import json
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Fast AJHL API",
    description="Fast API serving AJHL data from database",
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

def get_db_connection():
    """Get database connection"""
    return sqlite3.connect('ajhl_comprehensive.db')

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Fast AJHL API - Database Powered",
        "version": "1.0.0",
        "description": "Fast API serving AJHL data from database (updated daily at 3:30 AM Eastern)",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "teams": "/teams",
            "team": "/teams/{team_id}",
            "players": "/players",
            "player_search": "/players/search/{name}",
            "team_players": "/teams/{team_id}/players",
            "league_stats": "/league/stats"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get counts
        cursor.execute("SELECT COUNT(*) FROM teams")
        team_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM players")
        player_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "teams_in_db": team_count,
            "players_in_db": player_count,
            "last_updated": "Daily at 3:30 AM Eastern"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/teams")
async def get_teams():
    """Get all teams from database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT team_id, team_name, city, province, hudl_id, active, last_updated
            FROM teams
            ORDER BY team_name
        """)
        
        teams = []
        for row in cursor.fetchall():
            teams.append({
                "team_id": row[0],
                "team_name": row[1],
                "city": row[2],
                "province": row[3],
                "hudl_id": row[4],
                "active": bool(row[5]),
                "last_updated": row[6]
            })
        
        conn.close()
        
        return {
            "success": True,
            "teams": teams,
            "total_teams": len(teams),
            "league": "AJHL"
        }
    except Exception as e:
        logger.error(f"Error getting teams: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/teams/{team_id}")
async def get_team(team_id: str):
    """Get specific team from database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT team_id, team_name, city, province, hudl_id, active, last_updated
            FROM teams
            WHERE team_id = ?
        """, (team_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail=f"Team {team_id} not found")
        
        return {
            "success": True,
            "team": {
                "team_id": row[0],
                "team_name": row[1],
                "city": row[2],
                "province": row[3],
                "hudl_id": row[4],
                "active": bool(row[5]),
                "last_updated": row[6]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting team {team_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/players")
async def get_all_players():
    """Get all players from database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT p.player_id, p.team_id, p.name, p.position, p.metrics, p.last_updated,
                   t.team_name
            FROM players p
            JOIN teams t ON p.team_id = t.team_id
            ORDER BY t.team_name, p.name
        """)
        
        players = []
        for row in cursor.fetchall():
            try:
                metrics = json.loads(row[4]) if row[4] else {}
            except:
                metrics = {}
            
            players.append({
                "player_id": row[0],
                "team_id": row[1],
                "name": row[2],
                "position": row[3],
                "metrics": metrics,
                "team_name": row[6],
                "last_updated": row[5]
            })
        
        conn.close()
        
        return {
            "success": True,
            "players": players,
            "total_players": len(players),
            "league": "AJHL"
        }
    except Exception as e:
        logger.error(f"Error getting all players: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/players/search/{name}")
async def search_players(name: str):
    """Search for players by name"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT p.player_id, p.team_id, p.name, p.position, p.metrics, p.last_updated,
                   t.team_name
            FROM players p
            JOIN teams t ON p.team_id = t.team_id
            WHERE LOWER(p.name) LIKE LOWER(?)
            ORDER BY t.team_name, p.name
        """, (f"%{name}%",))
        
        players = []
        for row in cursor.fetchall():
            try:
                metrics = json.loads(row[4]) if row[4] else {}
            except:
                metrics = {}
            
            players.append({
                "player_id": row[0],
                "team_id": row[1],
                "name": row[2],
                "position": row[3],
                "metrics": metrics,
                "team_name": row[6],
                "last_updated": row[5]
            })
        
        conn.close()
        
        return {
            "success": True,
            "players": players,
            "total_players": len(players),
            "search_term": name,
            "league": "AJHL"
        }
    except Exception as e:
        logger.error(f"Error searching players: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/teams/{team_id}/players")
async def get_players_by_team(team_id: str):
    """Get players for a specific team"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get team info
        cursor.execute("SELECT team_name FROM teams WHERE team_id = ?", (team_id,))
        team_row = cursor.fetchone()
        
        if not team_row:
            raise HTTPException(status_code=404, detail=f"Team {team_id} not found")
        
        # Get players
        cursor.execute("""
            SELECT player_id, team_id, name, position, metrics, last_updated
            FROM players
            WHERE team_id = ?
            ORDER BY name
        """, (team_id,))
        
        players = []
        for row in cursor.fetchall():
            try:
                metrics = json.loads(row[4]) if row[4] else {}
            except:
                metrics = {}
            
            players.append({
                "player_id": row[0],
                "team_id": row[1],
                "name": row[2],
                "position": row[3],
                "metrics": metrics,
                "team_name": team_row[0],
                "last_updated": row[5]
            })
        
        conn.close()
        
        return {
            "success": True,
            "team_id": team_id,
            "team_name": team_row[0],
            "players": players,
            "total_players": len(players)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting players for team {team_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/league/stats")
async def get_league_stats():
    """Get league-wide statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM teams")
        total_teams = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM teams WHERE active = 1")
        active_teams = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM players")
        total_players = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "success": True,
            "league": "AJHL",
            "total_teams": total_teams,
            "active_teams": active_teams,
            "total_players": total_players,
            "last_updated": "Daily at 3:30 AM Eastern"
        }
    except Exception as e:
        logger.error(f"Error getting league stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("🚀 Starting Fast AJHL API...")
    print("✅ Database-powered (no real-time scraping)")
    print("✅ Updated daily at 3:30 AM Eastern")
    print("✅ Lightning fast responses")
    print()
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
