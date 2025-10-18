#!/usr/bin/env python3
"""
AJHL Team Configuration
Configuration for all Alberta Junior Hockey League teams and their Hudl Instat identifiers
"""

# AJHL Teams 2024-25 Season
# Note: Team IDs will need to be discovered through Hudl Instat platform
AJHL_TEAMS = {
    "brooks_bandits": {
        "team_name": "Brooks Bandits",
        "city": "Brooks",
        "hudl_team_id": None,  # To be discovered
        "league": "AJHL",
        "division": "South",
        "active": True
    },
    "calgary_canucks": {
        "team_name": "Calgary Canucks", 
        "city": "Calgary",
        "hudl_team_id": None,  # To be discovered
        "league": "AJHL",
        "division": "South",
        "active": True
    },
    "camrose_kodiaks": {
        "team_name": "Camrose Kodiaks",
        "city": "Camrose", 
        "hudl_team_id": None,  # To be discovered
        "league": "AJHL",
        "division": "South",
        "active": True
    },
    "drumheller_dragons": {
        "team_name": "Drumheller Dragons",
        "city": "Drumheller",
        "hudl_team_id": None,  # To be discovered
        "league": "AJHL", 
        "division": "South",
        "active": True
    },
    "okotoks_oilers": {
        "team_name": "Okotoks Oilers",
        "city": "Okotoks",
        "hudl_team_id": None,  # To be discovered
        "league": "AJHL",
        "division": "South", 
        "active": True
    },
    "olds_grizzlys": {
        "team_name": "Olds Grizzlys",
        "city": "Olds",
        "hudl_team_id": None,  # To be discovered
        "league": "AJHL",
        "division": "South",
        "active": True
    },
    "blackfalds_bulldogs": {
        "team_name": "Blackfalds Bulldogs",
        "city": "Blackfalds",
        "hudl_team_id": None,  # To be discovered
        "league": "AJHL",
        "division": "South",
        "active": True
    },
    "canmore_eagles": {
        "team_name": "Canmore Eagles",
        "city": "Canmore",
        "hudl_team_id": None,  # To be discovered
        "league": "AJHL",
        "division": "South",
        "active": True
    },
    "sherwood_park_crusaders": {
        "team_name": "Sherwood Park Crusaders",
        "city": "Sherwood Park",
        "hudl_team_id": None,  # To be discovered
        "league": "AJHL",
        "division": "North",
        "active": True
    },
    "spruce_grove_saints": {
        "team_name": "Spruce Grove Saints",
        "city": "Spruce Grove",
        "hudl_team_id": None,  # To be discovered
        "league": "AJHL",
        "division": "North",
        "active": True
    },
    "st_albert_steel": {
        "team_name": "St. Albert Steel",
        "city": "St. Albert",
        "hudl_team_id": None,  # To be discovered
        "league": "AJHL",
        "division": "North",
        "active": True
    },
    "strathcona_chiefs": {
        "team_name": "Strathcona Chiefs",
        "city": "Strathcona County",
        "hudl_team_id": None,  # To be discovered
        "league": "AJHL",
        "division": "North",
        "active": True
    },
    "whitecourt_wolverines": {
        "team_name": "Whitecourt Wolverines",
        "city": "Whitecourt",
        "hudl_team_id": None,  # To be discovered
        "league": "AJHL",
        "division": "North",
        "active": True
    },
    "bonnyville_pontiacs": {
        "team_name": "Bonnyville Pontiacs",
        "city": "Bonnyville",
        "hudl_team_id": None,  # To be discovered
        "league": "AJHL",
        "division": "North",
        "active": True
    },
    "drayton_valley_thunder": {
        "team_name": "Drayton Valley Thunder",
        "city": "Drayton Valley",
        "hudl_team_id": None,  # To be discovered
        "league": "AJHL",
        "division": "North",
        "active": True
    },
    "fort_mcmurray_oil_barons": {
        "team_name": "Fort McMurray Oil Barons",
        "city": "Fort McMurray",
        "hudl_team_id": None,  # To be discovered
        "league": "AJHL",
        "division": "North",
        "active": True
    },
    "grande_prairie_storm": {
        "team_name": "Grande Prairie Storm",
        "city": "Grande Prairie",
        "hudl_team_id": None,  # To be discovered
        "league": "AJHL",
        "division": "North",
        "active": True
    },
    "lloydminster_bobcats": {
        "team_name": "Lloydminster Bobcats",
        "city": "Lloydminster",
        "hudl_team_id": "21479",  # Known from existing system
        "league": "AJHL",
        "division": "North",
        "active": True
    }
}

# Data collection profiles for AJHL teams
AJHL_DATA_PROFILES = {
    'comprehensive': {
        'shifts': ['All shifts', 'Even strength shifts', 'Power play shifts', 'Penalty kill shifts'],
        'main_stats': ['Goals', 'Assists', 'Penalties', 'Hits', 'Plus/Minus'],
        'shots': ['Shots', 'Shots on goal', 'Blocked shots', 'Missed shots'],
        'passes': ['Passes', 'Accurate passes', 'Inaccurate passes', 'Passes to the slot'],
        'puck_battles': ['Puck battles', 'Puck battles won', 'Puck battles lost'],
        'entries_breakouts': ['Entries', 'Breakouts', 'Faceoffs', 'Faceoffs won', 'Faceoffs lost'],
        'goalie': ['Goals against', 'Shots against', 'Saves', 'Save percentage']
    },
    'daily_analytics': {
        'shifts': ['All shifts', 'Even strength shifts'],
        'main_stats': ['Goals', 'Assists', 'Penalties'],
        'shots': ['Shots', 'Shots on goal'],
        'passes': ['Passes', 'Accurate passes'],
        'entries_breakouts': ['Faceoffs', 'Faceoffs won', 'Faceoffs lost']
    },
    'goalie_focused': {
        'goalie': ['Goals against', 'Shots against', 'Saves', 'Save percentage'],
        'shots': ['Shots', 'Shots on goal'],
        'main_stats': ['Penalties']
    }
}

# Directory structure for data storage
DATA_DIRECTORIES = {
    'base_path': '/Users/emilyfehr8/CascadeProjects/ajhl_data',
    'daily_downloads': 'daily_downloads',
    'processed_data': 'processed_data', 
    'reports': 'reports',
    'logs': 'logs',
    'backups': 'backups'
}

# Scheduling configuration
SCHEDULE_CONFIG = {
    'daily_run_time': '06:00',  # 6 AM daily
    'timezone': 'America/Edmonton',
    'retry_attempts': 3,
    'retry_delay_minutes': 30,
    'max_concurrent_teams': 3,  # Process 3 teams at a time to avoid overwhelming Hudl
    'team_delay_seconds': 60    # Wait 1 minute between team processing
}

def get_active_teams():
    """Get list of active AJHL teams"""
    return {team_id: team_data for team_id, team_data in AJHL_TEAMS.items() if team_data['active']}

def get_team_by_id(team_id: str):
    """Get team data by team ID"""
    return AJHL_TEAMS.get(team_id)

def get_teams_by_division(division: str):
    """Get teams by division (North/South)"""
    return {team_id: team_data for team_id, team_data in AJHL_TEAMS.items() 
            if team_data['division'] == division and team_data['active']}

def get_teams_with_hudl_ids():
    """Get teams that have discovered Hudl team IDs"""
    return {team_id: team_data for team_id, team_data in AJHL_TEAMS.items() 
            if team_data['hudl_team_id'] and team_data['active']}

def update_team_hudl_id(team_id: str, hudl_team_id: str):
    """Update a team's Hudl team ID"""
    if team_id in AJHL_TEAMS:
        AJHL_TEAMS[team_id]['hudl_team_id'] = hudl_team_id
        return True
    return False

def get_data_profile(profile_name: str = 'comprehensive'):
    """Get data collection profile"""
    return AJHL_DATA_PROFILES.get(profile_name, AJHL_DATA_PROFILES['comprehensive'])

if __name__ == "__main__":
    print("🏒 AJHL Team Configuration")
    print("=" * 50)
    print(f"Total teams: {len(AJHL_TEAMS)}")
    print(f"Active teams: {len(get_active_teams())}")
    print(f"Teams with Hudl IDs: {len(get_teams_with_hudl_ids())}")
    
    print(f"\n📊 Teams by Division:")
    for division in ['North', 'South']:
        teams = get_teams_by_division(division)
        print(f"  {division}: {len(teams)} teams")
        for team_id, team_data in teams.items():
            hudl_status = "✅" if team_data['hudl_team_id'] else "❌"
            print(f"    {hudl_status} {team_data['team_name']} ({team_data['city']})")
    
    print(f"\n🔧 Data Profiles Available:")
    for profile_name in AJHL_DATA_PROFILES.keys():
        print(f"  - {profile_name}")
    
    print(f"\n📁 Data Storage:")
    for key, path in DATA_DIRECTORIES.items():
        print(f"  {key}: {path}")
