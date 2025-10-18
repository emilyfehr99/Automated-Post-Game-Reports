#!/usr/bin/env python3
"""
Instat League Metrics Aggregator
Aggregates team and player metrics across the entire league for comprehensive analysis

Provides league-wide statistics, rankings, and comparative analysis
"""

import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import pandas as pd
import numpy as np
from comprehensive_instat_hudl_api import ComprehensiveInstatHudlAPI, TeamMetrics, PlayerMetrics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LeagueStandings:
    """League standings with comprehensive team rankings"""
    team_id: str
    team_name: str
    position: int
    points: int
    games_played: int
    wins: int
    losses: int
    ties: int
    goals_for: int
    goals_against: int
    goal_difference: int
    points_percentage: float
    recent_form: List[str]  # Last 5 games: W/L/T
    home_record: Dict[str, int]
    away_record: Dict[str, int]

@dataclass
class LeagueLeaders:
    """League statistical leaders across all categories"""
    goals: List[Dict[str, Any]]
    assists: List[Dict[str, Any]]
    points: List[Dict[str, Any]]
    plus_minus: List[Dict[str, Any]]
    pim: List[Dict[str, Any]]
    shots: List[Dict[str, Any]]
    faceoff_percentage: List[Dict[str, Any]]
    save_percentage: List[Dict[str, Any]]
    gaa: List[Dict[str, Any]]  # Goals Against Average

@dataclass
class LeagueAnalytics:
    """Advanced league analytics and trends"""
    total_teams: int
    total_players: int
    total_games: int
    average_goals_per_game: float
    power_play_percentage: float
    penalty_kill_percentage: float
    home_ice_advantage: float
    overtime_percentage: float
    shootout_percentage: float
    trends: Dict[str, Any]

class InstatLeagueMetricsAggregator:
    """Aggregates and analyzes league-wide metrics from Instat Hudl data"""
    
    def __init__(self, api_client: ComprehensiveInstatHudlAPI):
        """Initialize the league metrics aggregator"""
        self.api = api_client
        self.league_data = {}
        self.team_metrics_cache = {}
        self.player_metrics_cache = {}
        
    def get_comprehensive_league_analysis(self, league_id: str = None, team_ids: List[str] = None) -> Dict[str, Any]:
        """Get comprehensive league analysis with all metrics"""
        logger.info(f"🏆 Starting comprehensive league analysis")
        
        # Get league overview
        league_overview = self.api.get_league_comprehensive_metrics(league_id)
        
        # Get team IDs if not provided
        if not team_ids:
            team_ids = [team["team_id"] for team in league_overview.get("teams", [])]
        
        # Collect all team metrics
        all_team_metrics = []
        all_player_metrics = []
        
        for team_id in team_ids:
            try:
                logger.info(f"📊 Collecting metrics for team {team_id}")
                
                # Get team metrics
                team_metrics = self.api.get_team_comprehensive_metrics(team_id)
                all_team_metrics.append(team_metrics)
                self.team_metrics_cache[team_id] = team_metrics
                
                # Get player metrics for each player
                for player in team_metrics.players:
                    try:
                        player_metrics = self.api.get_player_comprehensive_metrics(
                            player["player_id"], team_id
                        )
                        all_player_metrics.append(player_metrics)
                        self.player_metrics_cache[player["player_id"]] = player_metrics
                    except Exception as e:
                        logger.warning(f"⚠️  Could not get metrics for player {player['player_id']}: {e}")
                
            except Exception as e:
                logger.warning(f"⚠️  Could not get metrics for team {team_id}: {e}")
        
        # Generate comprehensive analysis
        analysis = {
            "league_overview": league_overview,
            "standings": self._generate_league_standings(all_team_metrics),
            "leaders": self._generate_league_leaders(all_player_metrics),
            "analytics": self._generate_league_analytics(all_team_metrics, all_player_metrics),
            "team_comparisons": self._generate_team_comparisons(all_team_metrics),
            "player_rankings": self._generate_player_rankings(all_player_metrics),
            "trends": self._analyze_league_trends(all_team_metrics, all_player_metrics),
            "generated_at": datetime.now().isoformat()
        }
        
        logger.info("✅ Comprehensive league analysis completed")
        return analysis
    
    def _generate_league_standings(self, team_metrics: List[TeamMetrics]) -> List[LeagueStandings]:
        """Generate league standings from team metrics"""
        standings = []
        
        for i, team in enumerate(team_metrics):
            # Extract basic team stats
            team_stats = team.team_stats
            
            # Calculate standings data
            points = team_stats.get("points", 0)
            games_played = team_stats.get("games_played", 0)
            wins = team_stats.get("wins", 0)
            losses = team_stats.get("losses", 0)
            ties = team_stats.get("ties", 0)
            goals_for = team_stats.get("goals_for", 0)
            goals_against = team_stats.get("goals_against", 0)
            goal_difference = goals_for - goals_against
            
            # Calculate points percentage
            points_percentage = (points / (games_played * 2)) if games_played > 0 else 0.0
            
            # Extract recent form from games
            recent_form = self._extract_recent_form(team.games)
            
            # Extract home/away records
            home_record = self._extract_home_away_record(team.games, "home")
            away_record = self._extract_home_away_record(team.games, "away")
            
            standing = LeagueStandings(
                team_id=team.team_id,
                team_name=team.team_name,
                position=i + 1,  # Will be sorted later
                points=points,
                games_played=games_played,
                wins=wins,
                losses=losses,
                ties=ties,
                goals_for=goals_for,
                goals_against=goals_against,
                goal_difference=goal_difference,
                points_percentage=points_percentage,
                recent_form=recent_form,
                home_record=home_record,
                away_record=away_record
            )
            standings.append(standing)
        
        # Sort by points, then goal difference, then goals for
        standings.sort(key=lambda x: (-x.points, -x.goal_difference, -x.goals_for))
        
        # Update positions
        for i, standing in enumerate(standings):
            standing.position = i + 1
        
        return standings
    
    def _generate_league_leaders(self, player_metrics: List[PlayerMetrics]) -> LeagueLeaders:
        """Generate league statistical leaders"""
        leaders = {
            "goals": [],
            "assists": [],
            "points": [],
            "plus_minus": [],
            "pim": [],
            "shots": [],
            "faceoff_percentage": [],
            "save_percentage": [],
            "gaa": []
        }
        
        for player in player_metrics:
            # Extract career stats
            career_stats = player.career_stats
            match_stats = player.match_stats
            
            # Goals leaders
            goals = career_stats.get("goals", 0)
            if goals > 0:
                leaders["goals"].append({
                    "player_name": player.player_name,
                    "team_id": player.team_id,
                    "position": player.position,
                    "value": goals
                })
            
            # Assists leaders
            assists = career_stats.get("assists", 0)
            if assists > 0:
                leaders["assists"].append({
                    "player_name": player.player_name,
                    "team_id": player.team_id,
                    "position": player.position,
                    "value": assists
                })
            
            # Points leaders
            points = career_stats.get("points", 0)
            if points > 0:
                leaders["points"].append({
                    "player_name": player.player_name,
                    "team_id": player.team_id,
                    "position": player.position,
                    "value": points
                })
            
            # Plus/minus leaders
            plus_minus = career_stats.get("plus_minus", 0)
            leaders["plus_minus"].append({
                "player_name": player.player_name,
                "team_id": player.team_id,
                "position": player.position,
                "value": plus_minus
            })
            
            # PIM leaders
            pim = career_stats.get("penalty_minutes", 0)
            if pim > 0:
                leaders["pim"].append({
                    "player_name": player.player_name,
                    "team_id": player.team_id,
                    "position": player.position,
                    "value": pim
                })
            
            # Shots leaders
            shots = career_stats.get("shots", 0)
            if shots > 0:
                leaders["shots"].append({
                    "player_name": player.player_name,
                    "team_id": player.team_id,
                    "position": player.position,
                    "value": shots
                })
            
            # Faceoff percentage (for centers)
            if player.position in ["C", "Center"]:
                faceoff_pct = career_stats.get("faceoff_percentage", 0)
                if faceoff_pct > 0:
                    leaders["faceoff_percentage"].append({
                        "player_name": player.player_name,
                        "team_id": player.team_id,
                        "position": player.position,
                        "value": faceoff_pct
                    })
            
            # Goalie stats
            if player.position in ["G", "Goalie"]:
                save_pct = career_stats.get("save_percentage", 0)
                if save_pct > 0:
                    leaders["save_percentage"].append({
                        "player_name": player.player_name,
                        "team_id": player.team_id,
                        "position": player.position,
                        "value": save_pct
                    })
                
                gaa = career_stats.get("goals_against_average", 0)
                if gaa > 0:
                    leaders["gaa"].append({
                        "player_name": player.player_name,
                        "team_id": player.team_id,
                        "position": player.position,
                        "value": gaa
                    })
        
        # Sort each category by value (descending, except GAA which is ascending)
        for category in leaders:
            if category == "gaa":
                leaders[category].sort(key=lambda x: x["value"])
            else:
                leaders[category].sort(key=lambda x: x["value"], reverse=True)
            
            # Keep only top 10
            leaders[category] = leaders[category][:10]
        
        return LeagueLeaders(**leaders)
    
    def _generate_league_analytics(self, team_metrics: List[TeamMetrics], player_metrics: List[PlayerMetrics]) -> LeagueAnalytics:
        """Generate advanced league analytics"""
        total_teams = len(team_metrics)
        total_players = len(player_metrics)
        
        # Calculate total games
        total_games = sum(len(team.games) for team in team_metrics) // 2  # Divide by 2 since each game appears twice
        
        # Calculate average goals per game
        total_goals = sum(team.team_stats.get("goals_for", 0) for team in team_metrics)
        average_goals_per_game = total_goals / total_games if total_games > 0 else 0
        
        # Calculate power play and penalty kill percentages
        total_pp_opportunities = sum(team.team_stats.get("power_play_opportunities", 0) for team in team_metrics)
        total_pp_goals = sum(team.team_stats.get("power_play_goals", 0) for team in team_metrics)
        power_play_percentage = (total_pp_goals / total_pp_opportunities * 100) if total_pp_opportunities > 0 else 0
        
        total_pk_opportunities = sum(team.team_stats.get("penalty_kill_opportunities", 0) for team in team_metrics)
        total_pk_goals_against = sum(team.team_stats.get("penalty_kill_goals_against", 0) for team in team_metrics)
        penalty_kill_percentage = ((total_pk_opportunities - total_pk_goals_against) / total_pk_opportunities * 100) if total_pk_opportunities > 0 else 0
        
        # Calculate home ice advantage
        home_wins = sum(team.team_stats.get("home_wins", 0) for team in team_metrics)
        home_games = sum(team.team_stats.get("home_games", 0) for team in team_metrics)
        home_ice_advantage = (home_wins / home_games * 100) if home_games > 0 else 0
        
        # Calculate overtime and shootout percentages
        total_overtime_games = sum(team.team_stats.get("overtime_games", 0) for team in team_metrics)
        overtime_percentage = (total_overtime_games / total_games * 100) if total_games > 0 else 0
        
        total_shootout_games = sum(team.team_stats.get("shootout_games", 0) for team in team_metrics)
        shootout_percentage = (total_shootout_games / total_games * 100) if total_games > 0 else 0
        
        # Analyze trends
        trends = self._analyze_league_trends(team_metrics, player_metrics)
        
        return LeagueAnalytics(
            total_teams=total_teams,
            total_players=total_players,
            total_games=total_games,
            average_goals_per_game=average_goals_per_game,
            power_play_percentage=power_play_percentage,
            penalty_kill_percentage=penalty_kill_percentage,
            home_ice_advantage=home_ice_advantage,
            overtime_percentage=overtime_percentage,
            shootout_percentage=shootout_percentage,
            trends=trends
        )
    
    def _generate_team_comparisons(self, team_metrics: List[TeamMetrics]) -> Dict[str, Any]:
        """Generate team comparison analytics"""
        comparisons = {
            "offensive_rankings": [],
            "defensive_rankings": [],
            "special_teams_rankings": [],
            "goaltending_rankings": []
        }
        
        # Offensive rankings (goals for, shots, power play)
        offensive_data = []
        for team in team_metrics:
            offensive_data.append({
                "team_id": team.team_id,
                "team_name": team.team_name,
                "goals_for": team.team_stats.get("goals_for", 0),
                "shots": team.team_stats.get("shots", 0),
                "power_play_percentage": team.team_stats.get("power_play_percentage", 0)
            })
        
        # Sort by goals for
        offensive_data.sort(key=lambda x: x["goals_for"], reverse=True)
        comparisons["offensive_rankings"] = offensive_data
        
        # Defensive rankings (goals against, shots against, penalty kill)
        defensive_data = []
        for team in team_metrics:
            defensive_data.append({
                "team_id": team.team_id,
                "team_name": team.team_name,
                "goals_against": team.team_stats.get("goals_against", 0),
                "shots_against": team.team_stats.get("shots_against", 0),
                "penalty_kill_percentage": team.team_stats.get("penalty_kill_percentage", 0)
            })
        
        # Sort by goals against (ascending - fewer is better)
        defensive_data.sort(key=lambda x: x["goals_against"])
        comparisons["defensive_rankings"] = defensive_data
        
        return comparisons
    
    def _generate_player_rankings(self, player_metrics: List[PlayerMetrics]) -> Dict[str, List[Dict[str, Any]]]:
        """Generate comprehensive player rankings"""
        rankings = {
            "forwards": [],
            "defensemen": [],
            "goalies": []
        }
        
        for player in player_metrics:
            player_data = {
                "player_id": player.player_id,
                "player_name": player.player_name,
                "team_id": player.team_id,
                "position": player.position,
                "stats": player.career_stats
            }
            
            if player.position in ["C", "LW", "RW", "Center", "Left Wing", "Right Wing"]:
                rankings["forwards"].append(player_data)
            elif player.position in ["D", "Defense", "Defenseman"]:
                rankings["defensemen"].append(player_data)
            elif player.position in ["G", "Goalie", "Goalkeeper"]:
                rankings["goalies"].append(player_data)
        
        # Sort each position group by points
        for position_group in rankings:
            rankings[position_group].sort(
                key=lambda x: x["stats"].get("points", 0), 
                reverse=True
            )
        
        return rankings
    
    def _analyze_league_trends(self, team_metrics: List[TeamMetrics], player_metrics: List[PlayerMetrics]) -> Dict[str, Any]:
        """Analyze league trends and patterns"""
        trends = {
            "scoring_trends": {},
            "goaltending_trends": {},
            "special_teams_trends": {},
            "team_performance_trends": {}
        }
        
        # Analyze scoring trends
        total_goals = sum(team.team_stats.get("goals_for", 0) for team in team_metrics)
        total_games = sum(len(team.games) for team in team_metrics) // 2
        trends["scoring_trends"]["average_goals_per_game"] = total_goals / total_games if total_games > 0 else 0
        
        # Analyze goaltending trends
        goalie_stats = [p for p in player_metrics if p.position in ["G", "Goalie"]]
        if goalie_stats:
            avg_save_pct = np.mean([p.career_stats.get("save_percentage", 0) for p in goalie_stats])
            avg_gaa = np.mean([p.career_stats.get("goals_against_average", 0) for p in goalie_stats])
            trends["goaltending_trends"]["average_save_percentage"] = avg_save_pct
            trends["goaltending_trends"]["average_gaa"] = avg_gaa
        
        # Analyze special teams trends
        total_pp_opportunities = sum(team.team_stats.get("power_play_opportunities", 0) for team in team_metrics)
        total_pp_goals = sum(team.team_stats.get("power_play_goals", 0) for team in team_metrics)
        trends["special_teams_trends"]["league_power_play_percentage"] = (total_pp_goals / total_pp_opportunities * 100) if total_pp_opportunities > 0 else 0
        
        return trends
    
    def _extract_recent_form(self, games: List[Dict[str, Any]]) -> List[str]:
        """Extract recent form from games (last 5 games)"""
        recent_games = games[-5:] if len(games) >= 5 else games
        form = []
        
        for game in recent_games:
            status = game.get("status", "").lower()
            if "win" in status or "w" in status:
                form.append("W")
            elif "loss" in status or "l" in status:
                form.append("L")
            elif "tie" in status or "t" in status:
                form.append("T")
            else:
                form.append("?")
        
        return form
    
    def _extract_home_away_record(self, games: List[Dict[str, Any]], location: str) -> Dict[str, int]:
        """Extract home or away record from games"""
        location_games = [g for g in games if location.lower() in g.get("location", "").lower()]
        
        wins = sum(1 for g in location_games if "win" in g.get("status", "").lower())
        losses = sum(1 for g in location_games if "loss" in g.get("status", "").lower())
        ties = sum(1 for g in location_games if "tie" in g.get("status", "").lower())
        
        return {
            "wins": wins,
            "losses": losses,
            "ties": ties,
            "total": len(location_games)
        }
    
    def export_league_analysis_to_csv(self, analysis: Dict[str, Any], output_dir: str = "league_analysis") -> Dict[str, str]:
        """Export league analysis to CSV files"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        exported_files = {}
        
        try:
            # Export standings
            if "standings" in analysis:
                standings_df = pd.DataFrame([asdict(standing) for standing in analysis["standings"]])
                standings_file = f"{output_dir}/league_standings.csv"
                standings_df.to_csv(standings_file, index=False)
                exported_files["standings"] = standings_file
            
            # Export leaders
            if "leaders" in analysis:
                leaders = analysis["leaders"]
                for category, leaders_list in asdict(leaders).items():
                    if leaders_list:
                        leaders_df = pd.DataFrame(leaders_list)
                        leaders_file = f"{output_dir}/league_leaders_{category}.csv"
                        leaders_df.to_csv(leaders_file, index=False)
                        exported_files[f"leaders_{category}"] = leaders_file
            
            # Export team comparisons
            if "team_comparisons" in analysis:
                comparisons = analysis["team_comparisons"]
                for category, comparison_data in comparisons.items():
                    if comparison_data:
                        comparison_df = pd.DataFrame(comparison_data)
                        comparison_file = f"{output_dir}/team_comparisons_{category}.csv"
                        comparison_df.to_csv(comparison_file, index=False)
                        exported_files[f"team_comparisons_{category}"] = comparison_file
            
            logger.info(f"✅ League analysis exported to {output_dir}")
            
        except Exception as e:
            logger.error(f"❌ Error exporting league analysis: {e}")
        
        return exported_files

def main():
    """Main function to demonstrate the league metrics aggregator"""
    print("🏆 Instat League Metrics Aggregator")
    print("=" * 60)
    
    # Initialize API client
    api = ComprehensiveInstatHudlAPI(headless=True)
    
    # Initialize league aggregator
    aggregator = InstatLeagueMetricsAggregator(api)
    
    print("✅ League Metrics Aggregator initialized")
    print("\n📊 Capabilities:")
    print("  • Comprehensive league standings")
    print("  • Statistical leaders across all categories")
    print("  • Advanced league analytics and trends")
    print("  • Team performance comparisons")
    print("  • Player rankings by position")
    print("  • Export to CSV for further analysis")
    
    print("\n🎯 Usage:")
    print("  # Get comprehensive league analysis")
    print("  analysis = aggregator.get_comprehensive_league_analysis(league_id, team_ids)")
    print("  ")
    print("  # Export to CSV")
    print("  files = aggregator.export_league_analysis_to_csv(analysis)")
    
    # Close API client
    api.close()

if __name__ == "__main__":
    main()
