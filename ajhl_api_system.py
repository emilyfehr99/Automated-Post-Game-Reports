#!/usr/bin/env python3
"""
AJHL API System
RESTful API for AJHL data collection and management
"""

import json
import time
import logging
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import httpx
from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
import schedule
import threading
from ajhl_team_config import get_active_teams, get_teams_with_hudl_ids
from ajhl_robust_scraper import AJHLRobustScraper, ScrapingMethod
from ajhl_notification_system import AJHLNotificationSystem
from ajhl_shared_account_manager import get_shared_scraper, add_shared_account, get_shared_account_status
from ajhl_api_keys import validate_api_key, generate_api_key, get_default_api_key

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./ajhl_api.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Security
security = HTTPBearer()

# Pydantic models
class TeamData(BaseModel):
    team_id: str
    team_name: str
    city: str
    division: str
    hudl_team_id: Optional[str] = None
    last_updated: Optional[datetime] = None
    data_available: bool = False

class GameData(BaseModel):
    game_id: str
    team_id: str
    opponent: str
    game_date: datetime
    home_away: str
    result: Optional[str] = None
    data_files: List[str] = []
    last_updated: datetime

class PlayerData(BaseModel):
    player_id: str
    team_id: str
    name: str
    position: str
    stats: Dict[str, Any] = {}
    last_updated: datetime

class DataCollectionRequest(BaseModel):
    team_ids: List[str] = []
    collection_type: str = "full"  # full, games_only, players_only
    force_refresh: bool = False

class NotificationConfig(BaseModel):
    email: Dict[str, Any] = {}
    sms: Dict[str, Any] = {}
    push: Dict[str, Any] = {}
    discord: Dict[str, Any] = {}
    slack: Dict[str, Any] = {}

class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.now)

# Database models
class Team(Base):
    __tablename__ = "teams"
    
    team_id = Column(String, primary_key=True)
    team_name = Column(String, nullable=False)
    city = Column(String, nullable=False)
    division = Column(String, nullable=False)
    hudl_team_id = Column(String, nullable=True)
    last_updated = Column(DateTime, default=func.now())
    data_available = Column(Boolean, default=False)

class Game(Base):
    __tablename__ = "games"
    
    game_id = Column(String, primary_key=True)
    team_id = Column(String, nullable=False)
    opponent = Column(String, nullable=False)
    game_date = Column(DateTime, nullable=False)
    home_away = Column(String, nullable=False)
    result = Column(String, nullable=True)
    data_files = Column(Text, nullable=True)  # JSON string
    last_updated = Column(DateTime, default=func.now())

class Player(Base):
    __tablename__ = "players"
    
    player_id = Column(String, primary_key=True)
    team_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    position = Column(String, nullable=False)
    stats = Column(Text, nullable=True)  # JSON string
    last_updated = Column(DateTime, default=func.now())

class DataCollectionLog(Base):
    __tablename__ = "data_collection_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(String, nullable=False)
    collection_type = Column(String, nullable=False)
    status = Column(String, nullable=False)  # success, failed, in_progress
    message = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=func.now())

# Create tables
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI(
    title="AJHL Data Collection API",
    description="RESTful API for AJHL hockey data collection and management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
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
scraper = None
notification_system = None
collection_scheduler = None
is_running = False

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency to verify API key
def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API key using the key manager"""
    api_key = credentials.credentials
    validated_key = validate_api_key(api_key)
    
    if not validated_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return validated_key

# API Endpoints

@app.get("/", response_model=APIResponse)
async def root():
    """Root endpoint with API information"""
    return APIResponse(
        success=True,
        message="AJHL Data Collection API",
        data={
            "version": "1.0.0",
            "status": "running",
            "endpoints": {
                "teams": "/teams",
                "games": "/games",
                "players": "/players",
                "collect": "/collect",
                "status": "/status",
                "docs": "/docs"
            }
        }
    )

@app.get("/teams", response_model=List[TeamData])
async def get_teams(db: Session = Depends(get_db)):
    """Get all teams"""
    teams = db.query(Team).all()
    return [TeamData(
        team_id=team.team_id,
        team_name=team.team_name,
        city=team.city,
        division=team.division,
        hudl_team_id=team.hudl_team_id,
        last_updated=team.last_updated,
        data_available=team.data_available
    ) for team in teams]

@app.get("/teams/{team_id}", response_model=TeamData)
async def get_team(team_id: str, db: Session = Depends(get_db)):
    """Get specific team"""
    team = db.query(Team).filter(Team.team_id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    return TeamData(
        team_id=team.team_id,
        team_name=team.team_name,
        city=team.city,
        division=team.division,
        hudl_team_id=team.hudl_team_id,
        last_updated=team.last_updated,
        data_available=team.data_available
    )

@app.get("/games", response_model=List[GameData])
async def get_games(
    team_id: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get games with optional filtering"""
    query = db.query(Game)
    
    if team_id:
        query = query.filter(Game.team_id == team_id)
    
    games = query.offset(offset).limit(limit).all()
    
    return [GameData(
        game_id=game.game_id,
        team_id=game.team_id,
        opponent=game.opponent,
        game_date=game.game_date,
        home_away=game.home_away,
        result=game.result,
        data_files=json.loads(game.data_files) if game.data_files else [],
        last_updated=game.last_updated
    ) for game in games]

@app.get("/games/{game_id}", response_model=GameData)
async def get_game(game_id: str, db: Session = Depends(get_db)):
    """Get specific game"""
    game = db.query(Game).filter(Game.game_id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    return GameData(
        game_id=game.game_id,
        team_id=game.team_id,
        opponent=game.opponent,
        game_date=game.game_date,
        home_away=game.home_away,
        result=game.result,
        data_files=json.loads(game.data_files) if game.data_files else [],
        last_updated=game.last_updated
    )

@app.get("/players", response_model=List[PlayerData])
async def get_players(
    team_id: Optional[str] = None,
    position: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get players with optional filtering"""
    query = db.query(Player)
    
    if team_id:
        query = query.filter(Player.team_id == team_id)
    if position:
        query = query.filter(Player.position == position)
    
    players = query.offset(offset).limit(limit).all()
    
    return [PlayerData(
        player_id=player.player_id,
        team_id=player.team_id,
        name=player.name,
        position=player.position,
        stats=json.loads(player.stats) if player.stats else {},
        last_updated=player.last_updated
    ) for player in players]

@app.post("/collect", response_model=APIResponse)
async def collect_data(
    request: DataCollectionRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key)
):
    """Trigger data collection for specified teams"""
    global scraper, is_running
    
    if is_running:
        return APIResponse(
            success=False,
            message="Data collection already in progress"
        )
    
    if not scraper:
        return APIResponse(
            success=False,
            message="Scraper not initialized"
        )
    
    # Start background collection
    background_tasks.add_task(
        run_data_collection,
        request.team_ids,
        request.collection_type,
        request.force_refresh
    )
    
    return APIResponse(
        success=True,
        message=f"Data collection started for {len(request.team_ids)} teams"
    )

@app.get("/collect/status", response_model=APIResponse)
async def get_collection_status():
    """Get current collection status"""
    global is_running
    
    return APIResponse(
        success=True,
        message="Collection status",
        data={
            "is_running": is_running,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.post("/collect/stop", response_model=APIResponse)
async def stop_collection(api_key: str = Depends(verify_api_key)):
    """Stop current data collection"""
    global is_running
    
    is_running = False
    
    return APIResponse(
        success=True,
        message="Data collection stopped"
    )

@app.get("/status", response_model=APIResponse)
async def get_system_status():
    """Get system health status"""
    global scraper, notification_system, is_running
    
    return APIResponse(
        success=True,
        message="System status",
        data={
            "scraper_initialized": scraper is not None,
            "notification_system_initialized": notification_system is not None,
            "collection_running": is_running,
            "timestamp": datetime.now().isoformat(),
            "uptime": "N/A"  # Could implement uptime tracking
        }
    )

@app.get("/notifications/config", response_model=NotificationConfig)
async def get_notification_config(api_key: str = Depends(verify_api_key)):
    """Get notification configuration"""
    global notification_system
    
    if not notification_system:
        raise HTTPException(status_code=503, detail="Notification system not initialized")
    
    return NotificationConfig(**notification_system.config)

@app.post("/notifications/config", response_model=APIResponse)
async def update_notification_config(
    config: NotificationConfig,
    api_key: str = Depends(verify_api_key)
):
    """Update notification configuration"""
    global notification_system
    
    if not notification_system:
        raise HTTPException(status_code=503, detail="Notification system not initialized")
    
    # Update configuration
    notification_system.config.update(config.dict())
    
    # Save to file
    with open("notification_config.json", "w") as f:
        json.dump(notification_system.config, f, indent=2)
    
    return APIResponse(
        success=True,
        message="Notification configuration updated"
    )

@app.post("/notifications/test", response_model=APIResponse)
async def test_notifications(api_key: str = Depends(verify_api_key)):
    """Test notification system"""
    global notification_system
    
    if not notification_system:
        raise HTTPException(status_code=503, detail="Notification system not initialized")
    
    try:
        notification_system.test_notifications()
        return APIResponse(
            success=True,
            message="Notification test completed"
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"Notification test failed: {str(e)}"
        )

@app.get("/data/files/{team_id}")
async def get_data_files(team_id: str):
    """Download data files for a team"""
    # Implementation for file download
    pass

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Background tasks
async def run_data_collection(team_ids: List[str], collection_type: str, force_refresh: bool):
    """Background task for data collection"""
    global is_running
    
    is_running = True
    
    try:
        logger.info(f"Starting data collection for teams: {team_ids}")
        
        for team_id in team_ids:
            if not is_running:
                break
            
            logger.info(f"Collecting data for team: {team_id}")
            
            # Get scraper from shared account pool
            scraper = get_shared_scraper()
            if not scraper:
                logger.error("No available scraper in shared account pool")
                continue
            
            try:
                # Use scraper to collect data
                result = scraper.scrape_team_data(team_id)
                
                if result.success:
                    # Store data in database
                    await store_team_data(team_id, result.data)
                    logger.info(f"Successfully collected data for team: {team_id}")
                else:
                    logger.error(f"Failed to collect data for team: {team_id} - {result.error}")
            except Exception as e:
                logger.error(f"Error collecting data for team {team_id}: {e}")
            finally:
                # Release scraper back to pool
                # Note: In a real implementation, you'd track the session ID
                pass
        
        logger.info("Data collection completed")
        
    except Exception as e:
        logger.error(f"Error in data collection: {e}")
    finally:
        is_running = False

async def store_team_data(team_id: str, data: Dict[str, Any]):
    """Store team data in database"""
    db = SessionLocal()
    
    try:
        # Update team record
        team = db.query(Team).filter(Team.team_id == team_id).first()
        if team:
            team.last_updated = datetime.now()
            team.data_available = True
            db.commit()
        
        # Store games data
        if "games" in data:
            for game_data in data["games"]:
                game = Game(
                    game_id=game_data.get("game_id", f"{team_id}_{datetime.now().timestamp()}"),
                    team_id=team_id,
                    opponent=game_data.get("opponent", ""),
                    game_date=datetime.fromisoformat(game_data.get("date", datetime.now().isoformat())),
                    home_away=game_data.get("home_away", ""),
                    result=game_data.get("result"),
                    data_files=json.dumps(game_data.get("data_files", []))
                )
                db.merge(game)
        
        # Store players data
        if "players" in data:
            for player_data in data["players"]:
                player = Player(
                    player_id=player_data.get("player_id", f"{team_id}_{player_data.get('name', 'unknown')}"),
                    team_id=team_id,
                    name=player_data.get("name", ""),
                    position=player_data.get("position", ""),
                    stats=json.dumps(player_data.get("stats", {}))
                )
                db.merge(player)
        
        db.commit()
        
    except Exception as e:
        logger.error(f"Error storing team data: {e}")
        db.rollback()
    finally:
        db.close()

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global notification_system
    
    logger.info("🚀 Starting AJHL API System...")
    
    # Initialize notification system
    notification_system = AJHLNotificationSystem()
    
    # Load teams into database
    await load_teams_into_database()
    
    # Add shared Hudl account
    try:
        from hudl_credentials import HUDL_USERNAME, HUDL_PASSWORD
        session_id = add_shared_account(HUDL_USERNAME, HUDL_PASSWORD)
        logger.info(f"✅ Added shared Hudl account: {session_id}")
    except ImportError:
        logger.warning("⚠️  No Hudl credentials found. Please create hudl_credentials.py")
    
    logger.info("✅ AJHL API System started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global scraper, is_running
    
    logger.info("🛑 Shutting down AJHL API System...")
    
    is_running = False
    
    if scraper:
        scraper.close()
    
    logger.info("✅ AJHL API System shutdown complete")

async def load_teams_into_database():
    """Load teams from configuration into database"""
    db = SessionLocal()
    
    try:
        teams = get_active_teams()
        
        for team_id, team_data in teams.items():
            team = Team(
                team_id=team_id,
                team_name=team_data["team_name"],
                city=team_data["city"],
                division=team_data["division"],
                hudl_team_id=team_data.get("hudl_team_id"),
                data_available=False
            )
            db.merge(team)
        
        db.commit()
        logger.info(f"✅ Loaded {len(teams)} teams into database")
        
    except Exception as e:
        logger.error(f"❌ Error loading teams: {e}")
    finally:
        db.close()

# Scheduler for automatic data collection
def start_scheduler():
    """Start the data collection scheduler"""
    global collection_scheduler
    
    def scheduled_collection():
        """Scheduled data collection task"""
        if not is_running:
            logger.info("Running scheduled data collection...")
            # Trigger collection for all teams
            asyncio.create_task(run_data_collection(
                team_ids=list(get_active_teams().keys()),
                collection_type="full",
                force_refresh=False
            ))
    
    # Schedule collection every 6 hours
    schedule.every(6).hours.do(scheduled_collection)
    
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    collection_scheduler = threading.Thread(target=run_scheduler, daemon=True)
    collection_scheduler.start()
    logger.info("✅ Data collection scheduler started")

if __name__ == "__main__":
    # Start scheduler
    start_scheduler()
    
    # Run the API
    uvicorn.run(
        "ajhl_api_system:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
