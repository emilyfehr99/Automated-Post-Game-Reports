#!/usr/bin/env python3
"""
AJHL Teams Configuration
All teams in the Alberta Junior Hockey League with their Hudl team IDs
"""

AJHL_TEAMS = {
    "21479": {
        "team_name": "Lloydminster Bobcats",
        "city": "Lloydminster",
        "province": "AB",
        "hudl_team_id": "21479",
        "is_active": True
    },
    "21480": {
        "team_name": "Brooks Bandits", 
        "city": "Brooks",
        "province": "AB",
        "hudl_team_id": "21480",
        "is_active": True
    },
    "21481": {
        "team_name": "Okotoks Oilers",
        "city": "Okotoks", 
        "province": "AB",
        "hudl_team_id": "21481",
        "is_active": True
    },
    "21482": {
        "team_name": "Calgary Canucks",
        "city": "Calgary",
        "province": "AB", 
        "hudl_team_id": "21482",
        "is_active": True
    },
    "21483": {
        "team_name": "Camrose Kodiaks",
        "city": "Camrose",
        "province": "AB",
        "hudl_team_id": "21483", 
        "is_active": True
    },
    "21484": {
        "team_name": "Canmore Eagles",
        "city": "Canmore",
        "province": "AB",
        "hudl_team_id": "21484",
        "is_active": True
    },
    "21485": {
        "team_name": "Drumheller Dragons",
        "city": "Drumheller",
        "province": "AB",
        "hudl_team_id": "21485",
        "is_active": True
    },
    "21486": {
        "team_name": "Fort McMurray Oil Barons",
        "city": "Fort McMurray",
        "province": "AB",
        "hudl_team_id": "21486",
        "is_active": True
    },
    "21487": {
        "team_name": "Grande Prairie Storm",
        "city": "Grande Prairie", 
        "province": "AB",
        "hudl_team_id": "21487",
        "is_active": True
    },
    "21488": {
        "team_name": "Olds Grizzlys",
        "city": "Olds",
        "province": "AB",
        "hudl_team_id": "21488",
        "is_active": True
    },
    "21489": {
        "team_name": "Sherwood Park Crusaders",
        "city": "Sherwood Park",
        "province": "AB",
        "hudl_team_id": "21489",
        "is_active": True
    },
    "21490": {
        "team_name": "Spruce Grove Saints",
        "city": "Spruce Grove",
        "province": "AB",
        "hudl_team_id": "21490",
        "is_active": True
    },
    "21491": {
        "team_name": "Whitecourt Wolverines",
        "city": "Whitecourt",
        "province": "AB",
        "hudl_team_id": "21491",
        "is_active": True
    }
}

def get_all_teams():
    """Get all AJHL teams"""
    return AJHL_TEAMS

def get_team_by_id(team_id):
    """Get team by ID"""
    return AJHL_TEAMS.get(team_id)

def get_active_teams():
    """Get all active teams"""
    return {tid: team for tid, team in AJHL_TEAMS.items() if team.get("is_active", True)}

def get_team_names():
    """Get all team names"""
    return [team["team_name"] for team in AJHL_TEAMS.values()]

def get_team_ids():
    """Get all team IDs"""
    return list(AJHL_TEAMS.keys())
