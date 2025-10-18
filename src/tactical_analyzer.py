import numpy as np
from typing import Dict, List, Tuple, Optional
import math
from dataclasses import dataclass
from enum import Enum

class Zone(Enum):
    OFFENSIVE = "OZ"
    DEFENSIVE = "DZ" 
    NEUTRAL = "NZ"

class FormationType(Enum):
    # Forecheck systems
    FORECHECK_1_2_2 = "1-2-2 Forecheck"
    FORECHECK_1_3_1 = "1-3-1 Forecheck"
    FORECHECK_2_1_2 = "2-1-2 Forecheck"
    FORECHECK_2_2_1 = "2-2-1 Forecheck"
    FORECHECK_3_2 = "3-2 Forecheck"
    
    # Neutral zone systems
    NZ_1_3_1 = "1-3-1 Neutral Zone"
    NZ_1_2_2 = "1-2-2 Neutral Zone"
    NZ_2_1_2 = "2-1-2 Neutral Zone"
    NZ_2_2_1 = "2-2-1 Neutral Zone"
    
    # Defensive systems
    DEFENSE_BOX = "Box Defense"
    DEFENSE_DIAMOND = "Diamond Defense"
    DEFENSE_TRIANGLE = "Triangle Defense"
    DEFENSE_1_3_1 = "1-3-1 Defense"
    
    # Power play formations
    PP_1_3_1 = "1-3-1 Power Play"
    PP_2_1_2 = "2-1-2 Power Play"
    PP_UMBRELLA = "Umbrella Power Play"
    
    # Penalty kill formations
    PK_BOX = "Box Penalty Kill"
    PK_DIAMOND = "Diamond Penalty Kill"
    PK_TRIANGLE = "Triangle Penalty Kill"
    
    # Other formations
    BREAKOUT = "Breakout Formation"
    RUSH = "Rush Formation"
    UNKNOWN = "Unknown Formation"

@dataclass
class Formation:
    formation_type: FormationType
    confidence: float
    players_involved: List[int]
    zone: Zone
    description: str

class TacticalAnalyzer:
    def __init__(self, rink_coordinates: Dict):
        """
        Initialize tactical analyzer with rink coordinates
        
        Args:
            rink_coordinates: Dictionary containing rink boundary coordinates
        """
        self.rink_coords = rink_coordinates
        self.blue_line_y = None
        self.center_line_y = None
        self._extract_rink_lines()
        
    def _extract_rink_lines(self):
        """Extract blue line and center line Y coordinates from rink coordinates"""
        if 'blue_lines' in self.rink_coords:
            # Use provided blue line coordinates
            self.blue_line_y = self.rink_coords['blue_lines']
        else:
            # Estimate blue lines based on rink dimensions
            rink_height = self.rink_coords.get('height', 200)
            self.blue_line_y = [rink_height * 0.25, rink_height * 0.75]
        
        # Center line is middle of rink
        rink_height = self.rink_coords.get('height', 200)
        self.center_line_y = rink_height / 2
    
    def determine_zone(self, y_position: float) -> Zone:
        """Determine which zone a position is in based on Y coordinate"""
        if y_position < min(self.blue_line_y):
            return Zone.OFFENSIVE
        elif y_position > max(self.blue_line_y):
            return Zone.DEFENSIVE
        else:
            return Zone.NEUTRAL
    
    def analyze_team_formation(self, team_players: List[Dict], zone: Zone) -> Formation:
        """
        Analyze the formation of a team in a specific zone
        
        Args:
            team_players: List of player dictionaries with positions
            zone: Current zone (OZ/DZ/NZ)
            
        Returns:
            Formation object with detected system
        """
        if not team_players or len(team_players) < 3:
            return Formation(
                formation_type=FormationType.UNKNOWN,
                confidence=0.0,
                players_involved=[],
                zone=zone,
                description="Insufficient players for formation analysis"
            )
        
        # Extract player positions
        positions = []
        for player in team_players:
            if 'rink_position' in player and player['rink_position']:
                x, y = player['rink_position']
                positions.append((x, y, player.get('id', 0)))
        
        if len(positions) < 3:
            return Formation(
                formation_type=FormationType.UNKNOWN,
                confidence=0.0,
                players_involved=[],
                zone=zone,
                description="Insufficient positioned players"
            )
        
        # Analyze formation based on zone
        if zone == Zone.OFFENSIVE:
            return self._analyze_forecheck_formation(positions)
        elif zone == Zone.NEUTRAL:
            return self._analyze_neutral_zone_formation(positions)
        elif zone == Zone.DEFENSIVE:
            return self._analyze_defensive_formation(positions)
        else:
            return Formation(
                formation_type=FormationType.UNKNOWN,
                confidence=0.0,
                players_involved=[p[2] for p in positions],
                zone=zone,
                description="Unknown zone"
            )
    
    def _analyze_forecheck_formation(self, positions: List[Tuple]) -> Formation:
        """Analyze forecheck formation in offensive zone"""
        # Sort players by Y position (closest to goal first)
        sorted_positions = sorted(positions, key=lambda p: p[1], reverse=True)
        
        # Count players in different zones
        deep_players = [p for p in positions if p[1] > np.mean([pos[1] for pos in positions])]
        mid_players = [p for p in positions if abs(p[1] - np.mean([pos[1] for pos in positions])) < 20]
        high_players = [p for p in positions if p[1] < np.mean([pos[1] for pos in positions])]
        
        # Analyze horizontal distribution
        left_players = [p for p in positions if p[0] < np.mean([pos[0] for pos in positions]) - 15]
        right_players = [p for p in positions if p[0] > np.mean([pos[0] for pos in positions]) + 15]
        center_players = [p for p in positions if abs(p[0] - np.mean([pos[0] for pos in positions])) <= 15]
        
        # Determine formation based on player distribution
        if len(deep_players) == 1 and len(mid_players) == 3 and len(high_players) == 1:
            if len(left_players) == 2 and len(right_players) == 2:
                return Formation(
                    formation_type=FormationType.FORECHECK_1_2_2,
                    confidence=0.85,
                    players_involved=[p[2] for p in positions],
                    zone=Zone.OFFENSIVE,
                    description="1-2-2 Forecheck: 1 deep, 2 mid-left, 2 mid-right, 1 high"
                )
        
        if len(deep_players) == 1 and len(mid_players) == 3 and len(high_players) == 1:
            if len(center_players) >= 2:
                return Formation(
                    formation_type=FormationType.FORECHECK_1_3_1,
                    confidence=0.80,
                    players_involved=[p[2] for p in positions],
                    zone=Zone.OFFENSIVE,
                    description="1-3-1 Forecheck: 1 deep, 3 mid-center, 1 high"
                )
        
        if len(deep_players) == 2 and len(mid_players) == 1 and len(high_players) == 2:
            return Formation(
                formation_type=FormationType.FORECHECK_2_1_2,
                confidence=0.75,
                players_involved=[p[2] for p in positions],
                zone=Zone.OFFENSIVE,
                description="2-1-2 Forecheck: 2 deep, 1 mid, 2 high"
            )
        
        # Default forecheck
        return Formation(
            formation_type=FormationType.FORECHECK_1_2_2,
            confidence=0.60,
            players_involved=[p[2] for p in positions],
            zone=Zone.OFFENSIVE,
            description="Standard forecheck formation"
        )
    
    def _analyze_neutral_zone_formation(self, positions: List[Tuple]) -> Formation:
        """Analyze neutral zone formation"""
        # Sort by Y position
        sorted_positions = sorted(positions, key=lambda p: p[1])
        
        # Count players in different zones
        back_players = [p for p in positions if p[1] < np.mean([pos[1] for pos in positions]) - 15]
        mid_players = [p for p in positions if abs(p[1] - np.mean([pos[1] for pos in positions])) <= 15]
        forward_players = [p for p in positions if p[1] > np.mean([pos[1] for pos in positions]) + 15]
        
        # Analyze horizontal distribution
        left_players = [p for p in positions if p[0] < np.mean([pos[0] for pos in positions]) - 15]
        right_players = [p for p in positions if p[0] > np.mean([pos[0] for pos in positions]) + 15]
        center_players = [p for p in positions if abs(p[0] - np.mean([pos[0] for pos in positions])) <= 15]
        
        if len(back_players) == 1 and len(mid_players) == 3 and len(forward_players) == 1:
            if len(center_players) >= 2:
                return Formation(
                    formation_type=FormationType.NZ_1_3_1,
                    confidence=0.85,
                    players_involved=[p[2] for p in positions],
                    zone=Zone.NEUTRAL,
                    description="1-3-1 Neutral Zone: 1 back, 3 center, 1 forward"
                )
        
        if len(back_players) == 1 and len(mid_players) == 2 and len(forward_players) == 2:
            if len(left_players) == 2 and len(right_players) == 2:
                return Formation(
                    formation_type=FormationType.NZ_1_2_2,
                    confidence=0.80,
                    players_involved=[p[2] for p in positions],
                    zone=Zone.NEUTRAL,
                    description="1-2-2 Neutral Zone: 1 back, 2 mid, 2 forward"
                )
        
        # Default neutral zone
        return Formation(
            formation_type=FormationType.NZ_1_2_2,
            confidence=0.65,
            players_involved=[p[2] for p in positions],
            zone=Zone.NEUTRAL,
            description="Standard neutral zone formation"
        )
    
    def _analyze_defensive_formation(self, positions: List[Tuple]) -> Formation:
        """Analyze defensive zone formation"""
        # Calculate center of defensive zone
        center_x = np.mean([p[0] for p in positions])
        center_y = np.mean([p[1] for p in positions])
        
        # Calculate distances from center
        distances = [(p, math.sqrt((p[0] - center_x)**2 + (p[1] - center_y)**2)) for p in positions]
        sorted_distances = sorted(distances, key=lambda x: x[1])
        
        # Check for box formation (4 players roughly in corners)
        if len(positions) >= 4:
            corner_players = []
            for p in positions:
                # Check if player is in corner region
                if (p[0] < center_x - 20 and p[1] < center_y - 20) or \
                   (p[0] > center_x + 20 and p[1] < center_y - 20) or \
                   (p[0] < center_x - 20 and p[1] > center_y + 20) or \
                   (p[0] > center_x + 20 and p[1] > center_y + 20):
                    corner_players.append(p)
            
            if len(corner_players) >= 3:
                return Formation(
                    formation_type=FormationType.DEFENSE_BOX,
                    confidence=0.85,
                    players_involved=[p[2] for p in positions],
                    zone=Zone.DEFENSIVE,
                    description="Box Defense: Players positioned in defensive corners"
                )
        
        # Check for diamond formation
        if len(positions) >= 4:
            # Look for 1 high, 2 mid, 1 low pattern
            high_players = [p for p in positions if p[1] < center_y - 15]
            mid_players = [p for p in positions if abs(p[1] - center_y) <= 15]
            low_players = [p for p in positions if p[1] > center_y + 15]
            
            if len(high_players) == 1 and len(mid_players) == 2 and len(low_players) == 1:
                return Formation(
                    formation_type=FormationType.DEFENSE_DIAMOND,
                    confidence=0.80,
                    players_involved=[p[2] for p in positions],
                    zone=Zone.DEFENSIVE,
                    description="Diamond Defense: 1 high, 2 mid, 1 low"
                )
        
        # Default defensive formation
        return Formation(
            formation_type=FormationType.DEFENSE_BOX,
            confidence=0.60,
            players_involved=[p[2] for p in positions],
            zone=Zone.DEFENSIVE,
            description="Standard defensive formation"
        )
    
    def analyze_frame_tactics(self, frame_data: Dict) -> Dict:
        """
        Analyze tactics for a single frame
        
        Args:
            frame_data: Frame data containing player information
            
        Returns:
            Dictionary with tactical analysis for both teams
        """
        if 'players' not in frame_data:
            return {}
        
        # Separate players by team
        team_a_players = []
        team_b_players = []
        
        for player in frame_data['players']:
            if 'team' in player:
                if player['team'] == 'A':
                    team_a_players.append(player)
                elif player['team'] == 'B':
                    team_b_players.append(player)
        
        # Analyze formations for each team
        team_a_formation = None
        team_b_formation = None
        
        if team_a_players:
            # Determine which zone Team A is in
            avg_y = np.mean([p.get('rink_position', [0, 0])[1] for p in team_a_players if p.get('rink_position')])
            zone_a = self.determine_zone(avg_y)
            team_a_formation = self.analyze_team_formation(team_a_players, zone_a)
        
        if team_b_players:
            # Determine which zone Team B is in
            avg_y = np.mean([p.get('rink_position', [0, 0])[1] for p in team_b_players if p.get('rink_position')])
            zone_b = self.determine_zone(avg_y)
            team_b_formation = self.analyze_team_formation(team_b_players, zone_b)
        
        return {
            'frame_number': frame_data.get('frame_number', 0),
            'team_a': {
                'formation': team_a_formation,
                'zone': team_a_formation.zone if team_a_formation else None,
                'player_count': len(team_a_players)
            },
            'team_b': {
                'formation': team_b_formation,
                'zone': team_b_formation.zone if team_b_formation else None,
                'player_count': len(team_b_players)
            }
        }
    
    def get_formation_summary(self, all_tactics: List[Dict]) -> Dict:
        """
        Get summary of formations used throughout the game
        
        Args:
            all_tactics: List of tactical analysis for all frames
            
        Returns:
            Summary of formations used by each team
        """
        team_a_formations = {}
        team_b_formations = {}
        
        for frame_tactics in all_tactics:
            if 'team_a' in frame_tactics and frame_tactics['team_a']['formation']:
                formation = frame_tactics['team_a']['formation']
                formation_name = formation.formation_type.value
                if formation_name not in team_a_formations:
                    team_a_formations[formation_name] = {
                        'count': 0,
                        'zones': set(),
                        'confidence_avg': 0.0
                    }
                team_a_formations[formation_name]['count'] += 1
                team_a_formations[formation_name]['zones'].add(formation.zone.value)
                team_a_formations[formation_name]['confidence_avg'] += formation.confidence
            
            if 'team_b' in frame_tactics and frame_tactics['team_b']['formation']:
                formation = frame_tactics['team_b']['formation']
                formation_name = formation.formation_type.value
                if formation_name not in team_b_formations:
                    team_b_formations[formation_name] = {
                        'count': 0,
                        'zones': set(),
                        'confidence_avg': 0.0
                    }
                team_b_formations[formation_name]['count'] += 1
                team_b_formations[formation_name]['zones'].add(formation.zone.value)
                team_b_formations[formation_name]['confidence_avg'] += formation.confidence
        
        # Calculate average confidence
        for formations in [team_a_formations, team_b_formations]:
            for formation_name, data in formations.items():
                if data['count'] > 0:
                    data['confidence_avg'] /= data['count']
                    data['zones'] = list(data['zones'])
        
        return {
            'team_a': team_a_formations,
            'team_b': team_b_formations
        }
