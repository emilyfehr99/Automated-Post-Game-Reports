#!/usr/bin/env python3
"""
Hudl Instat API Endpoints Discovery
Based on analysis of the main.bundle.js file
"""

# Key API endpoints discovered from the JavaScript bundle
HUDL_API_ENDPOINTS = {
    # Player and team statistics
    "scout_team_players_stat_new_scout": "scout_team_players_stat_new_scout",
    "scout_player_matches_stat_new_scout": "scout_player_matches_stat_new_scout", 
    "scout_overview_team_players": "scout_overview_team_players",
    "scout_overview_player_inf": "scout_overview_player_inf",
    "scout_overview_player_career": "scout_overview_player_career",
    "scout_overview_player_matches": "scout_overview_player_matches",
    "scout_overview_player_matches_stat": "scout_overview_player_matches_stat",
    "scout_overview_players_skills": "scout_overview_players_skills",
    
    # Match and game data
    "scout_overview_matches": "scout_overview_matches",
    "scout_overview_matches_stat": "scout_overview_matches_stat",
    "scout_match_inf": "scout_match_inf",
    "scout_match_players_stat_new_scout": "scout_match_players_stat_new_scout",
    "scout_match_units_stat_new_scout": "scout_match_units_stat_new_scout",
    "scout_players_in_match": "scout_players_in_match",
    
    # Team information
    "scout_overview_team_inf": "scout_overview_team_inf",
    "scout_team_season_list": "scout_team_season_list",
    "scout_team_units_stat_new_scout": "scout_team_units_stat_new_scout",
    
    # Shot maps and faceoffs
    "scout_match_map_shoot_match_new_scout": "scout_match_map_shoot_match_new_scout",
    "scout_match_map_shoot_player_new_scout": "scout_match_map_shoot_player_new_scout", 
    "scout_match_map_shoot_team_new_scout": "scout_match_map_shoot_team_new_scout",
    "scout_match_map_faceoffs_match_new_scout": "scout_match_map_faceoffs_match_new_scout",
    "scout_match_map_faceoffs_player_new_scout": "scout_match_map_faceoffs_player_new_scout",
    "scout_match_map_faceoffs_team_new_scout": "scout_match_map_faceoffs_team_new_scout",
    
    # Export functionality
    "scout_export_params": "scout_export_params",
    
    # Search and filtering
    "scout_get_players_teams_by_params": "scout_get_players_teams_by_params",
    "scout_flag_search": "scout_flag_search",
    
    # Tournament information
    "scout_tournament_inf": "scout_tournament_inf",
    
    # Video and episodes
    "scout_ask_episodes_xxx": "scout_ask_episodes_xxx",
    "scout_ask_videocuts_new": "scout_ask_videocuts_new",
    "scout_ask_videocuts_buttons_with_count": "scout_ask_videocuts_buttons_with_count",
    "scout_ask_buttons_for_videocuts_block": "scout_ask_buttons_for_videocuts_block",
    "scout_ask_params_for_matches_table_new_scout": "scout_ask_params_for_matches_table_new_scout"
}

# Base URLs discovered
HUDL_BASE_URLS = {
    "instat_scout": "https://new.instatscout.com",
    "metropole_videoplayer": "https://app.metropole.com/app/metropole/videoplayer/video/playlists",
    "assets": "https://assets.hudl.com"
}

# Tab structure from the bundle
HUDL_TABS = {
    "overview": {"name": "tabs_overview", "to": ""},
    "games": {"name": "tabs_games_hockey", "to": "games"},
    "skaters": {"name": "tabs_skaters", "to": "skaters"},
    "goalies": {"name": "tabs_goalies", "to": "goalies"},
    "lines": {"name": "tabs_lines", "to": "lines"},
    "shots": {"name": "tabs_shots", "to": "shots"},
    "faceoffs_chart": {"name": "tabs_faceoffs_chart", "to": "faceoffs_chart"},
    "episode_search": {"name": "tabs_episode_search", "to": "episode_search"},
    "career": {"name": "tabs_career", "to": "career"}
}

# Language options
HUDL_LANGUAGES = [
    {"className": "ru", "id": 0, "locale": "ru", "title": "Русский"},
    {"className": "gb", "id": 1, "locale": "en", "title": "English"},
    {"className": "fr", "id": 7, "locale": "fr", "title": "Français"},
    {"className": "de", "id": 8, "locale": "de", "title": "Deutsch"},
    {"className": "pl", "id": 13, "locale": "pl", "title": "Polska"},
    {"className": "cz", "id": 14, "locale": "cs", "title": "Čeština"},
    {"className": "se", "id": 28, "locale": "sv", "title": "Svenska"},
    {"className": "fi", "id": 29, "locale": "fi", "title": "Suomi"}
]

# Key constants and configurations
HUDL_CONFIG = {
    "field_dimensions": {
        "blueLine": 38.14,
        "fieldLength": 61,
        "fieldLengthDivision": 0.61,
        "fieldWidth": 30
    },
    "export_formats": ["CSV", "Excel", "PDF"],
    "max_players_per_team": 50,
    "max_teams_per_league": 20
}

def get_api_endpoint(endpoint_name: str) -> str:
    """Get the full API endpoint URL"""
    if endpoint_name in HUDL_API_ENDPOINTS:
        return f"{HUDL_BASE_URLS['instat_scout']}/api/{HUDL_API_ENDPOINTS[endpoint_name]}"
    return None

def get_team_players_endpoint(team_id: str) -> str:
    """Get the team players statistics endpoint"""
    return f"{HUDL_BASE_URLS['instat_scout']}/api/scout_team_players_stat_new_scout?team_id={team_id}"

def get_player_details_endpoint(player_id: str) -> str:
    """Get the player details endpoint"""
    return f"{HUDL_BASE_URLS['instat_scout']}/api/scout_overview_player_inf?player_id={player_id}"

def get_export_endpoint(team_id: str, format: str = "CSV") -> str:
    """Get the export endpoint for team data"""
    return f"{HUDL_BASE_URLS['instat_scout']}/api/scout_export_params?team_id={team_id}&format={format}"

# Print all discovered endpoints
if __name__ == "__main__":
    print("🔍 Discovered Hudl Instat API Endpoints:")
    print("=" * 50)
    
    for category, endpoints in {
        "Player & Team Stats": [
            "scout_team_players_stat_new_scout",
            "scout_player_matches_stat_new_scout", 
            "scout_overview_team_players",
            "scout_overview_player_inf"
        ],
        "Match Data": [
            "scout_overview_matches",
            "scout_match_inf",
            "scout_match_players_stat_new_scout"
        ],
        "Shot Maps & Faceoffs": [
            "scout_match_map_shoot_match_new_scout",
            "scout_match_map_faceoffs_match_new_scout"
        ],
        "Export & Search": [
            "scout_export_params",
            "scout_get_players_teams_by_params"
        ]
    }.items():
        print(f"\n📊 {category}:")
        for endpoint in endpoints:
            url = get_api_endpoint(endpoint)
            if url:
                print(f"  • {endpoint}: {url}")
    
    print(f"\n🌐 Base URLs:")
    for name, url in HUDL_BASE_URLS.items():
        print(f"  • {name}: {url}")
    
    print(f"\n📋 Available Tabs:")
    for tab, config in HUDL_TABS.items():
        print(f"  • {tab}: {config['to']}")
