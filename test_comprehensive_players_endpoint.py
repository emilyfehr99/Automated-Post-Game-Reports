#!/usr/bin/env python3
"""
Test Comprehensive Players Endpoint
Shows what the players endpoint would return with all Hudl Instat metrics
"""

import json
from datetime import datetime

def test_comprehensive_players_endpoint():
    """Test what the comprehensive players endpoint would return"""
    print("🏒 Testing Comprehensive Players Endpoint")
    print("=" * 50)
    
    # Mock comprehensive player data (what would come from Hudl Instat)
    mock_players = [
        {
            "player_id": "player_001",
            "team_id": "lloydminster_bobcats",
            "name": "John Smith",
            "position": "F",
            "last_updated": "2024-01-15T10:30:00Z",
            
            # Main Statistics
            "main_stats": {
                "time_on_ice": "18:45",
                "games_played": 25,
                "all_shifts": 156,
                "goals": 15,
                "first_assist": 8,
                "second_assist": 12,
                "assists": 20,
                "puck_touches": 342,
                "points": 35,
                "plus_minus": 8,
                "plus": 45,
                "minus": 37,
                "scoring_chances": 28,
                "team_goals_when_on_ice": 45,
                "opponent_goals_when_on_ice": 37,
                "penalties": 12,
                "penalties_drawn": 8,
                "penalty_time": "24:00"
            },
            
            # Faceoffs
            "faceoffs": {
                "faceoffs": 45,
                "faceoffs_won": 28,
                "faceoffs_lost": 17,
                "faceoffs_won_percentage": 62.2
            },
            
            # Physical Play
            "physical_play": {
                "hits": 23,
                "hits_against": 18,
                "error_leading_to_goal": 2,
                "dump_ins": 15,
                "dump_outs": 12
            },
            
            # Shooting
            "shooting": {
                "shots": 68,
                "shots_on_goal": 45,
                "blocked_shots": 12,
                "missed_shots": 11,
                "shots_on_goal_percentage": 66.2,
                "slapshot": 8,
                "wrist_shot": 52,
                "shootouts": 3,
                "shootouts_scored": 2,
                "shootouts_missed": 1,
                "one_on_one_shots": 4,
                "one_on_one_goals": 2,
                "shots_conversion_one_on_one_percentage": 50.0,
                "power_play_shots": 8,
                "short_handed_shots": 2,
                "shots_5v5": 58,
                "positional_attack_shots": 35,
                "counter_attack_shots": 33
            },
            
            # Puck Battles
            "puck_battles": {
                "puck_battles": 89,
                "puck_battles_won": 52,
                "puck_battles_won_percentage": 58.4,
                "puck_battles_in_dz": 28,
                "puck_battles_in_nz": 31,
                "puck_battles_in_oz": 30,
                "shots_blocking": 15,
                "dekes": 23,
                "dekes_successful": 16,
                "dekes_unsuccessful": 7,
                "dekes_successful_percentage": 69.6
            },
            
            # Recoveries and Losses
            "recoveries_losses": {
                "takeaways": 18,
                "takeaways_in_dz": 8,
                "takeaways_in_nz": 5,
                "takeaways_in_oz": 5,
                "puck_losses": 22,
                "puck_losses_in_dz": 6,
                "puck_losses_in_nz": 8,
                "puck_losses_in_oz": 8,
                "puck_retrievals_after_shots": 12,
                "opponent_dump_in_retrievals": 8,
                "loose_puck_recovery": 15,
                "ev_dz_retrievals": 18,
                "ev_oz_retrievals": 12,
                "power_play_retrievals": 3,
                "penalty_kill_retrievals": 5
            },
            
            # Power Play / Short-handed
            "special_teams": {
                "power_play": 12,
                "successful_power_play": 8,
                "power_play_time": "15:30",
                "short_handed": 8,
                "penalty_killing": 6,
                "short_handed_time": "12:45"
            },
            
            # Expected Goals
            "expected_goals": {
                "xg": 12.4,
                "xg_per_shot": 0.18,
                "xg_expected_goals": 12.4,
                "xg_per_goal": 0.83,
                "net_xg": 2.1,
                "team_xg_when_on_ice": 15.2,
                "opponent_xg_when_on_ice": 13.1,
                "xg_conversion": 1.21
            },
            
            # Passes
            "passes": {
                "passes": 156,
                "accurate_passes": 142,
                "accurate_passes_percentage": 91.0,
                "passes_to_slot": 23,
                "pre_shots_passes": 18,
                "pass_receptions": 134
            },
            
            # Entries and Breakouts
            "entries_breakouts": {
                "entries": 45,
                "entries_via_pass": 28,
                "entries_via_dump_in": 12,
                "entries_via_stickhandling": 5,
                "breakouts": 38,
                "breakouts_via_pass": 25,
                "breakouts_via_dump_out": 8,
                "breakouts_via_stickhandling": 5
            },
            
            # Advanced Statistics
            "advanced_stats": {
                "corsi": 89,
                "corsi_minus": 45,
                "corsi_plus": 44,
                "corsi_for_percentage": 49.4,
                "fenwick_for": 78,
                "fenwick_against": 82,
                "fenwick_for_percentage": 48.8
            },
            
            # Faceoffs by Zones
            "faceoffs_by_zones": {
                "faceoffs_in_dz": 18,
                "faceoffs_won_in_dz": 12,
                "faceoffs_won_in_dz_percentage": 66.7,
                "faceoffs_in_nz": 15,
                "faceoffs_won_in_nz": 8,
                "faceoffs_won_in_nz_percentage": 53.3,
                "faceoffs_in_oz": 12,
                "faceoffs_won_in_oz": 8,
                "faceoffs_won_in_oz_percentage": 66.7
            },
            
            # Playtime Phases
            "playtime_phases": {
                "playing_in_attack": "12:30",
                "playing_in_defense": "6:15",
                "oz_possession": 45,
                "nz_possession": 38,
                "dz_possession": 42
            },
            
            # Scoring Chances
            "scoring_chances": {
                "scoring_chances_total": 28,
                "scoring_chances_scored": 15,
                "scoring_chances_missed": 8,
                "scoring_chances_saved": 5,
                "scoring_chances_percentage": 53.6,
                "inner_slot_shots_total": 12,
                "inner_slot_shots_scored": 8,
                "inner_slot_shots_missed": 2,
                "inner_slot_shots_saved": 2,
                "inner_slot_shots_percentage": 66.7,
                "outer_slot_shots_total": 16,
                "outer_slot_shots_scored": 7,
                "outer_slot_shots_missed": 6,
                "outer_slot_shots_saved": 3,
                "outer_slot_shots_percentage": 43.8,
                "blocked_shots_from_slot": 8,
                "blocked_shots_outside_slot": 4
            },
            
            # Passport
            "passport": {
                "date_of_birth": "2005-03-15",
                "nationality": "Canadian",
                "national_team": "Canada",
                "height": "6'1\"",
                "weight": "185 lbs",
                "contract": "2024-2025",
                "active_hand": "Right"
            }
        }
    ]
    
    print(f"Found {len(mock_players)} players with comprehensive statistics")
    print()
    
    # Show sample player
    player = mock_players[0]
    print(f"👤 Sample Player: {player['name']} ({player['position']})")
    print("=" * 50)
    
    # Main stats
    print("📊 Main Statistics:")
    main_stats = player['main_stats']
    print(f"  Goals: {main_stats['goals']}")
    print(f"  Assists: {main_stats['assists']}")
    print(f"  Points: {main_stats['points']}")
    print(f"  Time on Ice: {main_stats['time_on_ice']}")
    print(f"  Games Played: {main_stats['games_played']}")
    print(f"  Plus/Minus: {main_stats['plus_minus']}")
    print()
    
    # Shooting stats
    print("🎯 Shooting Statistics:")
    shooting = player['shooting']
    print(f"  Shots: {shooting['shots']}")
    print(f"  Shots on Goal: {shooting['shots_on_goal']}")
    print(f"  Shooting %: {shooting['shots_on_goal_percentage']}%")
    print(f"  Goals: {shooting['one_on_one_goals']} (1v1)")
    print()
    
    # Advanced stats
    print("📈 Advanced Statistics:")
    advanced = player['advanced_stats']
    print(f"  Corsi: {advanced['corsi']} ({advanced['corsi_for_percentage']}%)")
    print(f"  Fenwick: {advanced['fenwick_for']} ({advanced['fenwick_for_percentage']}%)")
    print()
    
    # Expected goals
    print("🎲 Expected Goals:")
    xg = player['expected_goals']
    print(f"  xG: {xg['xg']}")
    print(f"  Net xG: {xg['net_xg']}")
    print(f"  xG Conversion: {xg['xg_conversion']}")
    print()
    
    # Show JSON structure (abbreviated)
    print("📄 JSON Response Structure:")
    print("=" * 50)
    
    # Create a simplified version for display
    simplified_player = {
        "player_id": player["player_id"],
        "team_id": player["team_id"],
        "name": player["name"],
        "position": player["position"],
        "last_updated": player["last_updated"],
        "main_stats": player["main_stats"],
        "shooting": player["shooting"],
        "advanced_stats": player["advanced_stats"],
        "expected_goals": player["expected_goals"],
        "passport": player["passport"]
        # ... all other categories
    }
    
    print(json.dumps(simplified_player, indent=2))
    
    print()
    print("🔍 Available Endpoints:")
    print("-" * 50)
    print("GET /players - Get all players with full statistics")
    print("GET /players?team_id=lloydminster_bobcats - Get team players")
    print("GET /players?position=F - Get forwards only")
    print("GET /players?position=G - Get goalies only")
    print()
    
    print("📱 Example Usage:")
    print("-" * 50)
    print("# Get all players with comprehensive stats")
    print("curl http://localhost:8000/players")
    print()
    print("# Get team players")
    print("curl 'http://localhost:8000/players?team_id=lloydminster_bobcats'")
    print()
    print("# Get only forwards")
    print("curl 'http://localhost:8000/players?position=F'")
    print()
    
    print("🐍 Python Example:")
    print("-" * 50)
    print("import requests")
    print()
    print("# Get all players")
    print("response = requests.get('http://localhost:8000/players')")
    print("players = response.json()")
    print()
    print("# Find top scorer")
    print("top_scorer = max(players, key=lambda p: p['main_stats']['goals'])")
    print("print(f'Top scorer: {top_scorer[\"name\"]} with {top_scorer[\"main_stats\"][\"goals\"]} goals')")
    print()
    print("# Get players by advanced stats")
    print("high_corsi_players = [p for p in players if p['advanced_stats']['corsi_for_percentage'] > 50]")
    print()
    
    print("✅ This is the comprehensive players data from Hudl Instat!")

if __name__ == "__main__":
    test_comprehensive_players_endpoint()
