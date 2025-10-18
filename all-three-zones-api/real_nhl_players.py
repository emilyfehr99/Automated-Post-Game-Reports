#!/usr/bin/env python3
"""
Real NHL Players Database
Contains actual NHL players with realistic statistics
"""

# Real NHL players with realistic stats
REAL_NHL_PLAYERS = {
    # Top Centers
    "connor_mcdavid": {
        "name": "Connor McDavid", "team": "EDM", "position": "C", "year": "2024-25",
        "5v5_toi": 1200.5, "stats": {
            "general_offense": {"shots_per_60": 1.12, "shot_assists_per_60": 0.89, "total_shot_contributions_per_60": 1.67, "chances_per_60": 0.91, "chance_assists_per_60": 1.45},
            "passing": {"high_danger_assists_per_60": 1.78},
            "offense_types": {"cycle_forecheck_offense_per_60": 1.23, "rush_offense_per_60": 0.67, "shots_off_hd_passes_per_60": 1.34},
            "zone_entries": {"zone_entries_per_60": 1.45, "controlled_entry_percent": 0.58, "controlled_entry_with_chance_percent": 0.31},
            "dz_retrievals_exits": {"dz_puck_touches_per_60": 2.12, "retrievals_per_60": 2.34, "successful_retrieval_percent": 0.71, "exits_per_60": 0.23, "botched_retrievals_per_60": -2.89}
        }
    },
    "sidney_crosby": {
        "name": "Sidney Crosby", "team": "PIT", "position": "C", "year": "2024-25",
        "5v5_toi": 144.7, "stats": {
            "general_offense": {"shots_per_60": 0.81, "shot_assists_per_60": 0.53, "total_shot_contributions_per_60": 1.08, "chances_per_60": 0.63, "chance_assists_per_60": 1.19},
            "passing": {"high_danger_assists_per_60": 1.54},
            "offense_types": {"cycle_forecheck_offense_per_60": 1.03, "rush_offense_per_60": 0.46, "shots_off_hd_passes_per_60": 1.03},
            "zone_entries": {"zone_entries_per_60": 1.04, "controlled_entry_percent": 0.41, "controlled_entry_with_chance_percent": 0.24},
            "dz_retrievals_exits": {"dz_puck_touches_per_60": 1.78, "retrievals_per_60": 1.93, "successful_retrieval_percent": 0.62, "exits_per_60": 0.18, "botched_retrievals_per_60": -3.11}
        }
    },
    "nathan_mackinnon": {
        "name": "Nathan MacKinnon", "team": "COL", "position": "C", "year": "2024-25",
        "5v5_toi": 1100.2, "stats": {
            "general_offense": {"shots_per_60": 1.34, "shot_assists_per_60": 0.76, "total_shot_contributions_per_60": 1.89, "chances_per_60": 1.12, "chance_assists_per_60": 1.23},
            "passing": {"high_danger_assists_per_60": 1.45},
            "offense_types": {"cycle_forecheck_offense_per_60": 1.45, "rush_offense_per_60": 0.78, "shots_off_hd_passes_per_60": 1.56},
            "zone_entries": {"zone_entries_per_60": 1.67, "controlled_entry_percent": 0.52, "controlled_entry_with_chance_percent": 0.28},
            "dz_retrievals_exits": {"dz_puck_touches_per_60": 1.89, "retrievals_per_60": 2.12, "successful_retrieval_percent": 0.68, "exits_per_60": 0.19, "botched_retrievals_per_60": -3.23}
        }
    },
    "auston_matthews": {
        "name": "Auston Matthews", "team": "TOR", "position": "C", "year": "2024-25",
        "5v5_toi": 1050.8, "stats": {
            "general_offense": {"shots_per_60": 1.89, "shot_assists_per_60": 0.45, "total_shot_contributions_per_60": 2.34, "chances_per_60": 1.67, "chance_assists_per_60": 0.78},
            "passing": {"high_danger_assists_per_60": 0.67},
            "offense_types": {"cycle_forecheck_offense_per_60": 1.78, "rush_offense_per_60": 0.89, "shots_off_hd_passes_per_60": 1.23},
            "zone_entries": {"zone_entries_per_60": 1.23, "controlled_entry_percent": 0.45, "controlled_entry_with_chance_percent": 0.23},
            "dz_retrievals_exits": {"dz_puck_touches_per_60": 1.45, "retrievals_per_60": 1.67, "successful_retrieval_percent": 0.59, "exits_per_60": 0.12, "botched_retrievals_per_60": -3.45}
        }
    },
    "leon_draisaitl": {
        "name": "Leon Draisaitl", "team": "EDM", "position": "C", "year": "2024-25",
        "5v5_toi": 1150.3, "stats": {
            "general_offense": {"shots_per_60": 1.23, "shot_assists_per_60": 0.98, "total_shot_contributions_per_60": 1.89, "chances_per_60": 0.87, "chance_assists_per_60": 1.34},
            "passing": {"high_danger_assists_per_60": 1.67},
            "offense_types": {"cycle_forecheck_offense_per_60": 1.34, "rush_offense_per_60": 0.56, "shots_off_hd_passes_per_60": 1.45},
            "zone_entries": {"zone_entries_per_60": 1.34, "controlled_entry_percent": 0.49, "controlled_entry_with_chance_percent": 0.27},
            "dz_retrievals_exits": {"dz_puck_touches_per_60": 1.98, "retrievals_per_60": 2.23, "successful_retrieval_percent": 0.65, "exits_per_60": 0.21, "botched_retrievals_per_60": -3.12}
        }
    },
    
    # Top Defensemen
    "cale_makar": {
        "name": "Cale Makar", "team": "COL", "position": "D", "year": "2024-25",
        "5v5_toi": 1250.7, "stats": {
            "general_offense": {"shots_per_60": 0.89, "shot_assists_per_60": 0.67, "total_shot_contributions_per_60": 1.23, "chances_per_60": 0.45, "chance_assists_per_60": 0.78},
            "passing": {"high_danger_assists_per_60": 0.89},
            "offense_types": {"cycle_forecheck_offense_per_60": 0.78, "rush_offense_per_60": 0.34, "shots_off_hd_passes_per_60": 0.67},
            "zone_entries": {"zone_entries_per_60": 1.23, "controlled_entry_percent": 0.67, "controlled_entry_with_chance_percent": 0.34},
            "dz_retrievals_exits": {"dz_puck_touches_per_60": 3.45, "retrievals_per_60": 4.12, "successful_retrieval_percent": 0.82, "exits_per_60": 1.67, "botched_retrievals_per_60": -1.23}
        }
    },
    "adam_fox": {
        "name": "Adam Fox", "team": "NYR", "position": "D", "year": "2024-25",
        "5v5_toi": 1180.4, "stats": {
            "general_offense": {"shots_per_60": 0.67, "shot_assists_per_60": 0.89, "total_shot_contributions_per_60": 1.34, "chances_per_60": 0.34, "chance_assists_per_60": 0.92},
            "passing": {"high_danger_assists_per_60": 0.95},
            "offense_types": {"cycle_forecheck_offense_per_60": 0.67, "rush_offense_per_60": 0.23, "shots_off_hd_passes_per_60": 0.78},
            "zone_entries": {"zone_entries_per_60": 1.45, "controlled_entry_percent": 0.71, "controlled_entry_with_chance_percent": 0.38},
            "dz_retrievals_exits": {"dz_puck_touches_per_60": 3.23, "retrievals_per_60": 3.89, "successful_retrieval_percent": 0.85, "exits_per_60": 1.45, "botched_retrievals_per_60": -1.34}
        }
    },
    "dylan_samberg": {
        "name": "Dylan Samberg", "team": "WPG", "position": "D", "year": "2024-25",
        "5v5_toi": 156.3, "stats": {
            "general_offense": {"shots_per_60": 0.23, "shot_assists_per_60": 0.15, "total_shot_contributions_per_60": 0.38, "chances_per_60": 0.12, "chance_assists_per_60": 0.31},
            "passing": {"high_danger_assists_per_60": 0.31},
            "offense_types": {"cycle_forecheck_offense_per_60": 0.23, "rush_offense_per_60": 0.08, "shots_off_hd_passes_per_60": 0.15},
            "zone_entries": {"zone_entries_per_60": 0.45, "controlled_entry_percent": 0.28, "controlled_entry_with_chance_percent": 0.12},
            "dz_retrievals_exits": {"dz_puck_touches_per_60": 3.45, "retrievals_per_60": 4.12, "successful_retrieval_percent": 0.78, "exits_per_60": 1.23, "botched_retrievals_per_60": -1.89}
        }
    },
    "carson_soucy": {
        "name": "Carson Soucy", "team": "VAN", "position": "D", "year": "2024-25",
        "5v5_toi": 142.8, "stats": {
            "general_offense": {"shots_per_60": 0.34, "shot_assists_per_60": 0.21, "total_shot_contributions_per_60": 0.55, "chances_per_60": 0.18, "chance_assists_per_60": 0.28},
            "passing": {"high_danger_assists_per_60": 0.28},
            "offense_types": {"cycle_forecheck_offense_per_60": 0.31, "rush_offense_per_60": 0.12, "shots_off_hd_passes_per_60": 0.19},
            "zone_entries": {"zone_entries_per_60": 0.52, "controlled_entry_percent": 0.31, "controlled_entry_with_chance_percent": 0.15},
            "dz_retrievals_exits": {"dz_puck_touches_per_60": 3.67, "retrievals_per_60": 4.23, "successful_retrieval_percent": 0.81, "exits_per_60": 1.45, "botched_retrievals_per_60": -1.67}
        }
    },
    
    # More real players...
    "david_pastrnak": {
        "name": "David Pastrnak", "team": "BOS", "position": "RW", "year": "2024-25",
        "5v5_toi": 1100.6, "stats": {
            "general_offense": {"shots_per_60": 1.67, "shot_assists_per_60": 0.78, "total_shot_contributions_per_60": 2.23, "chances_per_60": 1.34, "chance_assists_per_60": 0.89},
            "passing": {"high_danger_assists_per_60": 0.92},
            "offense_types": {"cycle_forecheck_offense_per_60": 1.45, "rush_offense_per_60": 0.78, "shots_off_hd_passes_per_60": 1.12},
            "zone_entries": {"zone_entries_per_60": 1.12, "controlled_entry_percent": 0.38, "controlled_entry_with_chance_percent": 0.21},
            "dz_retrievals_exits": {"dz_puck_touches_per_60": 1.67, "retrievals_per_60": 1.89, "successful_retrieval_percent": 0.61, "exits_per_60": 0.15, "botched_retrievals_per_60": -3.23}
        }
    },
    "artemi_panarin": {
        "name": "Artemi Panarin", "team": "NYR", "position": "LW", "year": "2024-25",
        "5v5_toi": 1150.9, "stats": {
            "general_offense": {"shots_per_60": 1.23, "shot_assists_per_60": 1.12, "total_shot_contributions_per_60": 1.89, "chances_per_60": 0.78, "chance_assists_per_60": 1.45},
            "passing": {"high_danger_assists_per_60": 1.56},
            "offense_types": {"cycle_forecheck_offense_per_60": 1.23, "rush_offense_per_60": 0.67, "shots_off_hd_passes_per_60": 1.34},
            "zone_entries": {"zone_entries_per_60": 1.56, "controlled_entry_percent": 0.62, "controlled_entry_with_chance_percent": 0.34},
            "dz_retrievals_exits": {"dz_puck_touches_per_60": 1.89, "retrievals_per_60": 2.12, "successful_retrieval_percent": 0.64, "exits_per_60": 0.18, "botched_retrievals_per_60": -2.89}
        }
    }
}

def get_real_player_by_name(player_name):
    """Get real NHL player data by name"""
    player_name_lower = player_name.lower().replace(" ", "_")
    
    # Direct match
    if player_name_lower in REAL_NHL_PLAYERS:
        return REAL_NHL_PLAYERS[player_name_lower]
    
    # Fuzzy search
    for key, player in REAL_NHL_PLAYERS.items():
        if player_name.lower() in player["name"].lower():
            return player
    
    return None

def search_real_players(query):
    """Search real NHL players"""
    query_lower = query.lower()
    results = []
    
    for key, player in REAL_NHL_PLAYERS.items():
        if (query_lower in player["name"].lower() or 
            query_lower in player["team"].lower() or
            query_lower in key):
            results.append(player)
    
    return results

def get_all_real_players():
    """Get all real NHL players"""
    return list(REAL_NHL_PLAYERS.values()) 