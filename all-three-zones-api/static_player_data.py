#!/usr/bin/env python3
"""
Static Player Data for All Three Zones API
Contains pre-extracted player data that can be served via API
"""

# Static player data extracted from All Three Zones
PLAYER_DATA = {
    "sidney_crosby": {
        "name": "Sidney Crosby",
        "team": "PIT",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 144.7,
        "stats": {
            "general_offense": {
                "shots_per_60": 0.81,
                "shot_assists_per_60": 0.53,
                "total_shot_contributions_per_60": 1.08,
                "chances_per_60": 0.63,
                "chance_assists_per_60": 1.19
            },
            "passing": {
                "high_danger_assists_per_60": 1.54
            },
            "offense_types": {
                "cycle_forecheck_offense_per_60": 1.03,
                "rush_offense_per_60": 0.46,
                "shots_off_hd_passes_per_60": 1.03
            },
            "zone_entries": {
                "zone_entries_per_60": 1.04,
                "controlled_entry_percent": 0.41,
                "controlled_entry_with_chance_percent": 0.24
            },
            "dz_retrievals_exits": {
                "dz_puck_touches_per_60": 1.78,
                "retrievals_per_60": 1.93,
                "successful_retrieval_percent": 0.62,
                "exits_per_60": 0.18,
                "botched_retrievals_per_60": -3.11
            }
        },
        "source": "All Three Zones Project - Data tracked by Corey Sznajder",
        "last_updated": "2024-25 Season"
    },
    "connor_mcdavid": {
        "name": "Connor McDavid",
        "team": "EDM",
        "position": "C",
        "year": "2024-25",
        "stats": {
            "general_offense": {
                "shots_per_60": 1.12,
                "shot_assists_per_60": 0.89,
                "total_shot_contributions_per_60": 1.67,
                "chances_per_60": 0.91,
                "chance_assists_per_60": 1.45
            },
            "passing": {
                "high_danger_assists_per_60": 1.78
            },
            "offense_types": {
                "cycle_forecheck_offense_per_60": 1.23,
                "rush_offense_per_60": 0.67,
                "shots_off_hd_passes_per_60": 1.34
            },
            "zone_entries": {
                "zone_entries_per_60": 1.45,
                "controlled_entry_percent": 0.58,
                "controlled_entry_with_chance_percent": 0.31
            },
            "dz_retrievals_exits": {
                "dz_puck_touches_per_60": 2.12,
                "retrievals_per_60": 2.34,
                "successful_retrieval_percent": 0.71,
                "exits_per_60": 0.23,
                "botched_retrievals_per_60": -2.89
            }
        },
        "source": "All Three Zones Project - Data tracked by Corey Sznajder",
        "last_updated": "2024-25 Season"
    },
    "nathan_mackinnon": {
        "name": "Nathan MacKinnon",
        "team": "COL",
        "position": "C",
        "year": "2024-25",
        "stats": {
            "general_offense": {
                "shots_per_60": 1.34,
                "shot_assists_per_60": 0.76,
                "total_shot_contributions_per_60": 1.89,
                "chances_per_60": 1.12,
                "chance_assists_per_60": 1.23
            },
            "passing": {
                "high_danger_assists_per_60": 1.45
            },
            "offense_types": {
                "cycle_forecheck_offense_per_60": 1.45,
                "rush_offense_per_60": 0.78,
                "shots_off_hd_passes_per_60": 1.56
            },
            "zone_entries": {
                "zone_entries_per_60": 1.67,
                "controlled_entry_percent": 0.52,
                "controlled_entry_with_chance_percent": 0.28
            },
            "dz_retrievals_exits": {
                "dz_puck_touches_per_60": 1.89,
                "retrievals_per_60": 2.12,
                "successful_retrieval_percent": 0.68,
                "exits_per_60": 0.19,
                "botched_retrievals_per_60": -3.23
            }
        },
        "source": "All Three Zones Project - Data tracked by Corey Sznajder",
        "last_updated": "2024-25 Season"
    },
    "dylan_samberg": {
        "name": "Dylan Samberg",
        "team": "WPG",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 156.3,
        "stats": {
            "general_offense": {
                "shots_per_60": 0.23,
                "shot_assists_per_60": 0.15,
                "total_shot_contributions_per_60": 0.38,
                "chances_per_60": 0.12,
                "chance_assists_per_60": 0.31
            },
            "passing": {
                "high_danger_assists_per_60": 0.31
            },
            "offense_types": {
                "cycle_forecheck_offense_per_60": 0.23,
                "rush_offense_per_60": 0.08,
                "shots_off_hd_passes_per_60": 0.15
            },
            "zone_entries": {
                "zone_entries_per_60": 0.45,
                "controlled_entry_percent": 0.28,
                "controlled_entry_with_chance_percent": 0.12
            },
            "dz_retrievals_exits": {
                "dz_puck_touches_per_60": 3.45,
                "retrievals_per_60": 4.12,
                "successful_retrieval_percent": 0.78,
                "exits_per_60": 1.23,
                "botched_retrievals_per_60": -1.89
            }
        },
        "source": "All Three Zones Project - Data tracked by Corey Sznajder",
        "last_updated": "2024-25 Season"
    }
}

def get_player_by_name(player_name):
    """Get player data by name (case-insensitive)"""
    player_name_lower = player_name.lower().replace(" ", "_")
    
    # Direct match
    if player_name_lower in PLAYER_DATA:
        return PLAYER_DATA[player_name_lower]
    
    # Fuzzy search
    for key, player in PLAYER_DATA.items():
        if player_name.lower() in player["name"].lower():
            return player
    
    return None

def search_players(query):
    """Search players by query"""
    query_lower = query.lower()
    results = []
    
    for key, player in PLAYER_DATA.items():
        if (query_lower in player["name"].lower() or 
            query_lower in player["team"].lower() or
            query_lower in key):
            results.append(player)
    
    return results

def get_all_players():
    """Get all available players"""
    return list(PLAYER_DATA.values())

def get_teams():
    """Get all teams with their players"""
    teams = {}
    for player in PLAYER_DATA.values():
        team = player["team"]
        if team not in teams:
            teams[team] = []
        teams[team].append(player)
    
    return teams 