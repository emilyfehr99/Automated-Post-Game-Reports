#!/usr/bin/env python3
"""
Aggregate Goal Trajectories Across Season
Collects all goal trajectories from processed games and generates visualizations
"""

import json
from pathlib import Path
from goal_route_analyzer import GoalRouteAnalyzer
from rink_heatmap_generator import RinkHeatmapGenerator
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_all_game_ids(processed_games_file: str = "processed_games.json") -> list:
    """Extract all game IDs from processed_games.json"""
    try:
        with open(processed_games_file, 'r') as f:
            data = json.load(f)
        
        # Handle both {"games": [...]} and {...} structures
        if isinstance(data, dict):
            if 'games' in data:
                game_ids = data['games']
            else:
                game_ids = list(data.keys())
        else:
            game_ids = data
        
        logger.info(f"Found {len(game_ids)} processed games")
        return game_ids
    except Exception as e:
        logger.error(f"Error loading processed games: {e}")
        return []


def aggregate_season_trajectories(team: str = None, max_games: int = None):
    """
    Aggregate goal trajectories across all processed games
    
    Args:
        team: Optional team filter (e.g., 'COL')
        max_games: Optional limit on number of games to process (for testing)
    """
    # Get all game IDs
    game_ids = get_all_game_ids()
    
    if not game_ids:
        logger.error("No games found to process")
        return
    
    if max_games:
        game_ids = game_ids[:max_games]
        logger.info(f"Limited to {max_games} games for testing")
    
    # Initialize analyzer
    analyzer = GoalRouteAnalyzer()
    
    # Aggregate trajectories
    logger.info(f"Aggregating trajectories from {len(game_ids)} games...")
    trajectories = analyzer.aggregate_trajectories(game_ids, team_filter=team)
    
    if not trajectories:
        logger.warning("No trajectories extracted")
        return
    
    # Save trajectories
    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)
    
    team_suffix = f"_{team}" if team else "_all_teams"
    trajectory_file = output_dir / f"goal_trajectories{team_suffix}.json"
    analyzer.save_trajectories(trajectories, str(trajectory_file))
    
    # Cluster routes
    logger.info("Clustering routes to identify patterns...")
    clusters = analyzer.cluster_routes(trajectories)
    
    # Generate visualizations
    logger.info("Generating heatmap visualization...")
    generator = RinkHeatmapGenerator()
    
    team_name = team if team else "All Teams"
    viz_path = output_dir / f"goal_routes{team_suffix}.png"
    
    generator.plot_hybrid_visualization(
        trajectories, 
        clusters, 
        team=team_name,
        output_path=str(viz_path)
    )
    
    # Print summary statistics
    print("\n" + "="*60)
    print(f"Goal Route Analysis Summary - {team_name}")
    print("="*60)
    print(f"Total Goals Analyzed: {len(trajectories)}")
    print(f"Route Patterns Identified: {len(clusters)}")
    
    if clusters:
        print("\nTop 5 Most Common Routes:")
        for i, (cluster_id, routes) in enumerate(list(clusters.items())[:5]):
            pct = (len(routes) / len(trajectories)) * 100
            avg_distance = sum(r['release_distance'] for r in routes) / len(routes)
            print(f"  {i+1}. Pattern {cluster_id}: {len(routes)} goals ({pct:.1f}%) - Avg distance: {avg_distance:.1f}ft")
    
    print(f"\nVisualization saved to: {viz_path}")
    print(f"Trajectory data saved to: {trajectory_file}")
    print("="*60)


if __name__ == "__main__":
    import sys
    
    # Parse command line arguments
    team_filter = None
    max_games = None
    
    if len(sys.argv) > 1:
        team_filter = sys.argv[1].upper()
        print(f"Filtering for team: {team_filter}")
    
    if len(sys.argv) > 2:
        max_games = int(sys.argv[2])
        print(f"Processing max {max_games} games")
    
    # Run aggregation
    aggregate_season_trajectories(team=team_filter, max_games=max_games)
