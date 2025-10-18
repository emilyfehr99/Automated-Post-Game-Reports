from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import os
import logging
from dotenv import load_dotenv

from a3z_scraper import AllThreeZonesScraper, PlayerData
from comprehensive_player_data import get_player_by_name, search_players, get_all_players, get_teams, get_players_by_position, get_players_by_team, get_player_count

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="All Three Zones API",
    description="API for accessing All Three Zones hockey data",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API responses
class PlayerResponse(BaseModel):
    name: str
    team: str
    position: str
    games_played: int
    stats: Dict[str, Any]

class TeamResponse(BaseModel):
    team_name: str
    stats: Dict[str, Any]

class ErrorResponse(BaseModel):
    error: str
    message: str

# Global scraper instance
scraper = None

def get_scraper():
    """Dependency to get scraper instance"""
    global scraper
    if scraper is None:
        try:
            scraper = AllThreeZonesScraper()
        except Exception as e:
            logger.error(f"Failed to initialize scraper: {e}")
            raise HTTPException(status_code=500, detail="Failed to initialize scraper")
    return scraper

@app.on_event("startup")
async def startup_event():
    """Initialize scraper on startup"""
    global scraper
    try:
        scraper = AllThreeZonesScraper()
        logger.info("Scraper initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize scraper on startup: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown"""
    global scraper
    if scraper:
        scraper.close()
        logger.info("Scraper closed successfully")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "All Three Zones API",
        "version": "1.0.0",
        "endpoints": {
            "players": "/players",
            "player": "/players/{player_name}",
            "teams": "/teams",
            "team": "/teams/{team_name}",
            "health": "/health"
        }
    }

@app.get("/health", response_model=Dict[str, str])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "API is running"}

@app.get("/players", response_model=List[Dict[str, Any]])
async def get_players(
    player_name: Optional[str] = Query(None, description="Filter by player name"),
    team: Optional[str] = Query(None, description="Filter by team name")
):
    """Get player data with optional filtering"""
    try:
        # Get all players from static data
        all_players = get_all_players()
        
        # Filter by name if provided
        if player_name:
            all_players = [p for p in all_players if player_name.lower() in p["name"].lower()]
        
        # Filter by team if provided
        if team:
            all_players = [p for p in all_players if team.upper() in p["team"].upper()]
        
        return all_players
        
    except Exception as e:
        logger.error(f"Error getting players: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get player data: {str(e)}")

@app.get("/players/{player_name}", response_model=Dict[str, Any])
async def get_player(player_name: str):
    """Get data for a specific player"""
    try:
        player = get_player_by_name(player_name)
        
        if not player:
            raise HTTPException(status_code=404, detail=f"Player '{player_name}' not found")
        
        return player
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting player {player_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get player data: {str(e)}")

@app.get("/teams", response_model=Dict[str, Any])
async def get_teams(team_name: Optional[str] = Query(None, description="Filter by team name")):
    """Get team data with optional filtering"""
    try:
        from comprehensive_player_data import get_teams as get_comp_teams
        teams_data = get_comp_teams()
        
        if team_name:
            # Return specific team if it exists
            if team_name.upper() in teams_data:
                return {team_name.upper(): teams_data[team_name.upper()]}
            else:
                return {}
        else:
            # Return all teams
            return teams_data
        
    except Exception as e:
        logger.error(f"Error getting teams: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get team data: {str(e)}")

@app.get("/players/position/{position}", response_model=List[Dict[str, Any]])
async def get_players_by_position_endpoint(position: str):
    """Get all players by position (C, LW, RW, D, G)"""
    try:
        from comprehensive_player_data import get_players_by_position as get_comp_players_by_pos
        players = get_comp_players_by_pos(position)
        return players
        
    except Exception as e:
        logger.error(f"Error getting players by position: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get players by position: {str(e)}")

@app.get("/players/team/{team}", response_model=List[Dict[str, Any]])
async def get_players_by_team_endpoint(team: str):
    """Get all players by team"""
    try:
        from comprehensive_player_data import get_players_by_team as get_comp_players_by_team
        players = get_comp_players_by_team(team)
        return players
        
    except Exception as e:
        logger.error(f"Error getting players by team: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get players by team: {str(e)}")

@app.get("/stats", response_model=Dict[str, Any])
async def get_database_stats():
    """Get database statistics"""
    try:
        from comprehensive_player_data import get_teams as get_comp_teams, get_players_by_position as get_comp_players_by_pos, get_player_count as get_comp_player_count
        teams_data = get_comp_teams()
        return {
            "total_players": get_comp_player_count(),
            "total_teams": len(teams_data),
            "forwards": len(get_comp_players_by_pos("C")) + len(get_comp_players_by_pos("LW")) + len(get_comp_players_by_pos("RW")),
            "defensemen": len(get_comp_players_by_pos("D")),
            "goalies": len(get_comp_players_by_pos("G")),
            "teams": list(teams_data.keys())
        }
        
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get database stats: {str(e)}")

@app.get("/teams/{team_name}", response_model=TeamResponse)
async def get_team(
    team_name: str,
    scraper_instance: AllThreeZonesScraper = Depends(get_scraper)
):
    """Get data for a specific team"""
    try:
        team_data = scraper_instance.get_team_data(team_name=team_name)
        
        if not team_data:
            raise HTTPException(status_code=404, detail=f"Team '{team_name}' not found")
        
        return TeamResponse(
            team_name=team_name,
            stats=team_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting team {team_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get team data: {str(e)}")

@app.get("/search", response_model=List[Dict[str, Any]])
async def search_players(query: str = Query(..., description="Search query for players")):
    """Search for players by name"""
    try:
        from comprehensive_player_data import search_players as search_comp_players
        results = search_comp_players(query)
        return results
        
    except Exception as e:
        logger.error(f"Error searching players: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search players: {str(e)}")

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "message": str(exc)}
    )

if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    # Run the API
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    ) 