#!/usr/bin/env python3
"""
Goal Route Analyzer
Extracts and processes puck trajectories from NHL sprite data to identify common goal-scoring routes
"""

import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from sprite_parser import get_sprite_data
from sklearn.cluster import DBSCAN
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GoalRouteAnalyzer:
    """Analyzes goal-scoring routes using sprite tracking data"""
    
    def __init__(self):
        self.trajectories = []
        
    def extract_goal_trajectory(self, sprite_data: List[Dict]) -> Optional[List[Tuple[float, float]]]:
        """
        Extract puck path from sprite frames leading to goal
        
        Args:
            sprite_data: List of sprite frames from NHL API
            
        Returns:
            List of (x, y) coordinates representing puck movement, or None if invalid
        """
        if not sprite_data or len(sprite_data) < 3:
            return None
            
        puck_positions = []
        
        for frame in sprite_data:
            on_ice = frame.get('onIce', {})
            
            # Puck is typically ID 1
            for player_id, data in on_ice.items():
                if str(player_id) == '1':  # Puck
                    x = data.get('x')
                    y = data.get('y')
                    if x is not None and y is not None:
                        puck_positions.append((float(x), float(y)))
                        
        # Filter out trajectories that are too short (likely incomplete data)
        if len(puck_positions) < 3:
            return None
            
        return puck_positions
    
    def calculate_trajectory_features(self, path: List[Tuple[float, float]]) -> Dict:
        """
        Calculate features of a trajectory for analysis
        
        Args:
            path: List of (x, y) coordinates
            
        Returns:
            Dictionary of trajectory features
        """
        if not path or len(path) < 2:
            return {}
            
        # Start and end points
        start_x, start_y = path[0]
        end_x, end_y = path[-1]
        
        # Calculate total distance traveled
        total_distance = 0
        for i in range(len(path) - 1):
            x1, y1 = path[i]
            x2, y2 = path[i + 1]
            total_distance += np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        
        # Calculate straight-line distance (release to goal)
        straight_distance = np.sqrt((end_x - start_x)**2 + (end_y - start_y)**2)
        
        # Calculate path curvature (ratio of actual to straight distance)
        curvature = total_distance / straight_distance if straight_distance > 0 else 1.0
        
        # Determine lateral movement (east-west)
        lateral_movement = abs(end_y - start_y)
        
        # Determine longitudinal movement (north-south, towards goal)
        longitudinal_movement = abs(end_x - start_x)
        
        return {
            'start_point': (start_x, start_y),
            'end_point': (end_x, end_y),
            'release_distance': straight_distance,
            'path_length': total_distance,
            'curvature': curvature,
            'lateral_movement': lateral_movement,
            'longitudinal_movement': longitudinal_movement,
            'num_frames': len(path)
        }
    
    def aggregate_trajectories(self, game_ids: List[str], team_filter: Optional[str] = None) -> List[Dict]:
        """
        Collect all goal trajectories across multiple games
        
        Args:
            game_ids: List of NHL game IDs to process
            team_filter: Optional team abbreviation to filter by
            
        Returns:
            List of trajectory dictionaries with metadata
        """
        from nhl_api_client import NHLAPIClient
        
        api = NHLAPIClient()
        all_trajectories = []
        
        for game_id in game_ids:
            logger.info(f"Processing game {game_id}")
            
            try:
                # Get play-by-play data
                pbp_data = api.get_play_by_play(game_id)
                if not pbp_data:
                    continue
                    
                plays = pbp_data.get('plays', [])
                
                for play in plays:
                    # Only process goals
                    if play.get('typeDescKey') != 'goal':
                        continue
                    
                    event_id = play.get('eventId')
                    if not event_id:
                        continue
                    
                    # Get team info
                    details = play.get('details', {})
                    scoring_team = details.get('eventOwnerTeamId')
                    
                    # Apply team filter if specified
                    if team_filter and scoring_team != team_filter:
                        continue
                    
                    # Fetch sprite data for this goal
                    sprite_data = get_sprite_data(game_id, event_id)
                    if not sprite_data:
                        continue
                    
                    # Extract trajectory
                    trajectory = self.extract_goal_trajectory(sprite_data)
                    if not trajectory:
                        continue
                    
                    # Calculate features
                    features = self.calculate_trajectory_features(trajectory)
                    
                    # Store trajectory with metadata
                    trajectory_record = {
                        'trajectory_id': f"{game_id}_ev{event_id}",
                        'game_id': game_id,
                        'event_id': event_id,
                        'team': scoring_team,
                        'path': trajectory,
                        **features
                    }
                    
                    all_trajectories.append(trajectory_record)
                    
            except Exception as e:
                logger.error(f"Error processing game {game_id}: {e}")
                continue
        
        logger.info(f"Extracted {len(all_trajectories)} goal trajectories")
        return all_trajectories
    
    def cluster_routes(self, trajectories: List[Dict], eps: float = 15.0, min_samples: int = 2) -> Dict:
        """
        Group similar trajectories to identify common patterns
        
        Args:
            trajectories: List of trajectory dictionaries
            eps: Maximum distance between samples for clustering
            min_samples: Minimum samples in a cluster
            
        Returns:
            Dictionary mapping cluster IDs to trajectory lists
        """
        if not trajectories:
            return {}
        
        # Extract features for clustering (start point, end point, curvature)
        features = []
        for traj in trajectories:
            start_x, start_y = traj['start_point']
            end_x, end_y = traj['end_point']
            curvature = traj['curvature']
            
            features.append([start_x, start_y, end_x, end_y, curvature * 10])  # Scale curvature
        
        features_array = np.array(features)
        
        # Perform DBSCAN clustering
        clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(features_array)
        labels = clustering.labels_
        
        # Group trajectories by cluster
        clusters = {}
        for idx, label in enumerate(labels):
            if label == -1:  # Noise
                continue
            
            if label not in clusters:
                clusters[label] = []
            
            clusters[label].append(trajectories[idx])
        
        # Sort clusters by size (most common routes first)
        sorted_clusters = dict(sorted(clusters.items(), key=lambda x: len(x[1]), reverse=True))
        
        logger.info(f"Identified {len(sorted_clusters)} common route patterns")
        return sorted_clusters
    
    def save_trajectories(self, trajectories: List[Dict], output_path: str):
        """Save trajectories to JSON file"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(trajectories, f, indent=2)
        
        logger.info(f"Saved {len(trajectories)} trajectories to {output_path}")
    
    def load_trajectories(self, input_path: str) -> List[Dict]:
        """Load trajectories from JSON file"""
        with open(input_path, 'r') as f:
            trajectories = json.load(f)
        
        logger.info(f"Loaded {len(trajectories)} trajectories from {input_path}")
        return trajectories


if __name__ == "__main__":
    # Example usage
    analyzer = GoalRouteAnalyzer()
    
    # Test with a few games
    test_games = ["2025020300", "2025020275", "2025020018"]
    
    trajectories = analyzer.aggregate_trajectories(test_games, team_filter="COL")
    
    if trajectories:
        analyzer.save_trajectories(trajectories, "data/goal_trajectories_COL.json")
        
        # Cluster routes
        clusters = analyzer.cluster_routes(trajectories)
        
        print(f"\nFound {len(clusters)} common route patterns:")
        for cluster_id, routes in clusters.items():
            print(f"  Cluster {cluster_id}: {len(routes)} goals")
