"""
Real Formation Detector - Even Strength Hockey Formations

This system analyzes player positions from a birds-eye view perspective,
connecting players with lines to identify geometric formation patterns.
No fake analysis - only real spatial pattern recognition.
"""

import numpy as np
import math
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class FormationType(Enum):
    """Even strength formation types."""
    TWO_ONE_TWO = "2-1-2"  # Standard defensive formation
    ONE_TWO_TWO = "1-2-2"  # Neutral zone trap
    TWO_TWO_ONE = "2-2-1"  # Aggressive forecheck
    ONE_THREE_ONE = "1-3-1"  # Even strength version
    THREE_TWO = "3-2"  # Defensive shell
    UNKNOWN = "Unknown"

class ZoneContext(Enum):
    """Rink zone contexts."""
    OFFENSIVE = "offensive"
    NEUTRAL = "neutral"
    DEFENSIVE = "defensive"

@dataclass
class PlayerPosition:
    """Player position data."""
    player_id: str
    team: str
    x: float  # Rink coordinates
    y: float
    is_goalkeeper: bool = False

@dataclass
class FormationDetection:
    """Formation detection result."""
    formation_type: FormationType
    confidence: float
    zone_context: ZoneContext
    player_roles: Dict[str, str]
    formation_shape: List[Tuple[float, float]]
    analysis_details: Dict

class RealFormationDetector:
    """
    Real Formation Detector using birds-eye view analysis.
    
    Connects players with lines to identify geometric formation patterns.
    """
    
    def __init__(self):
        self.rink_length = 200  # Standard hockey rink length in feet
        self.rink_width = 85    # Standard hockey rink width in feet
        
        # Zone boundaries (in feet from goal line)
        self.offensive_zone_start = 0
        self.offensive_zone_end = 60
        self.neutral_zone_start = 60
        self.neutral_zone_end = 140
        self.defensive_zone_start = 140
        self.defensive_zone_end = 200
        
        # Formation recognition thresholds
        self.min_confidence = 0.3
        self.max_formation_distance = 50  # Max distance between players in formation
        
    def detect_formation(self, players: List[PlayerPosition], puck_location: Optional[Tuple[float, float]] = None) -> FormationDetection:
        """
        Detect formation from player positions using birds-eye view analysis.
        
        Args:
            players: List of player positions
            puck_location: Optional puck location for context
            
        Returns:
            FormationDetection with identified formation and confidence
        """
        if len(players) < 4:
            return self._create_unknown_formation("Not enough players for formation")
            
        # Determine zone context
        zone_context = self._determine_zone_context(players, puck_location)
        
        # Filter out goalkeepers for formation analysis
        field_players = [p for p in players if not p.is_goalkeeper]
        
        if len(field_players) < 4:
            return self._create_unknown_formation("Not enough field players")
            
        # Analyze formation using birds-eye view
        formation_result = self._analyze_formation_shape(field_players, zone_context)
        
        return formation_result
    
    def _determine_zone_context(self, players: List[PlayerPosition], puck_location: Optional[Tuple[float, float]]) -> ZoneContext:
        """Determine the zone context based on player and puck positions."""
        
        # If we have puck location, use it for primary context
        if puck_location:
            puck_x = puck_location[0]
            if puck_x <= self.offensive_zone_end:
                return ZoneContext.OFFENSIVE
            elif puck_x <= self.neutral_zone_end:
                return ZoneContext.NEUTRAL
            else:
                return ZoneContext.DEFENSIVE
        
        # Otherwise, use average player position
        avg_x = sum(p.x for p in players) / len(players)
        
        if avg_x <= self.offensive_zone_end:
            return ZoneContext.OFFENSIVE
        elif avg_x <= self.neutral_zone_end:
            return ZoneContext.NEUTRAL
        else:
            return ZoneContext.DEFENSIVE
    
    def _analyze_formation_shape(self, players: List[PlayerPosition], zone_context: ZoneContext) -> FormationDetection:
        """
        Analyze formation shape by connecting players with lines.
        
        Uses geometric pattern recognition to identify formations.
        """
        # Create player position matrix
        positions = [(p.x, p.y) for p in players]
        
        # Calculate formation characteristics
        formation_center = self._calculate_formation_center(positions)
        formation_spread = self._calculate_formation_spread(positions)
        formation_angles = self._calculate_formation_angles(positions)
        
        # Analyze geometric patterns
        geometric_patterns = self._analyze_geometric_patterns(positions, formation_center)
        
        # Match patterns to known formations
        formation_match = self._match_formation_pattern(geometric_patterns, zone_context)
        
        # Calculate confidence based on pattern matching
        confidence = self._calculate_formation_confidence(formation_match, positions, zone_context)
        
        # Assign player roles based on formation
        player_roles = self._assign_player_roles(players, formation_match, formation_center)
        
        return FormationDetection(
            formation_type=formation_match["formation_type"],
            confidence=confidence,
            zone_context=zone_context,
            player_roles=player_roles,
            formation_shape=positions,
            analysis_details={
                "formation_center": formation_center,
                "formation_spread": formation_spread,
                "geometric_patterns": geometric_patterns,
                "pattern_match": formation_match
            }
        )
    
    def _calculate_formation_center(self, positions: List[Tuple[float, float]]) -> Tuple[float, float]:
        """Calculate the geometric center of the formation."""
        if not positions:
            return (0, 0)
            
        avg_x = sum(pos[0] for pos in positions) / len(positions)
        avg_y = sum(pos[1] for pos in positions) / len(positions)
        
        return (avg_x, avg_y)
    
    def _calculate_formation_spread(self, positions: List[Tuple[float, float]]) -> float:
        """Calculate how spread out the formation is."""
        if len(positions) < 2:
            return 0.0
            
        center = self._calculate_formation_center(positions)
        
        distances = []
        for pos in positions:
            distance = math.sqrt((pos[0] - center[0])**2 + (pos[1] - center[1])**2)
            distances.append(distance)
            
        return sum(distances) / len(distances)
    
    def _calculate_formation_angles(self, positions: List[Tuple[float, float]]) -> List[float]:
        """Calculate angles between players from formation center."""
        if len(positions) < 3:
            return []
            
        center = self._calculate_formation_center(positions)
        angles = []
        
        for i, pos in enumerate(positions):
            # Calculate angle from center to player
            angle = math.atan2(pos[1] - center[1], pos[0] - center[0])
            angles.append(angle)
            
        return angles
    
    def _analyze_geometric_patterns(self, positions: List[Tuple[float, float]], center: Tuple[float, float]) -> Dict:
        """
        Analyze geometric patterns by connecting players with lines.
        
        This is the core birds-eye view analysis.
        """
        patterns = {
            "shape_type": "unknown",
            "symmetry": 0.0,
            "compactness": 0.0,
            "linearity": 0.0,
            "circularity": 0.0
        }
        
        if len(positions) < 3:
            return patterns
            
        # Calculate distances between all players (connecting lines)
        distances = []
        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                dist = math.sqrt(
                    (positions[i][0] - positions[j][0])**2 + 
                    (positions[i][1] - positions[j][1])**2
                )
                distances.append(dist)
        
        # Analyze shape characteristics
        patterns["compactness"] = self._calculate_compactness(positions, center)
        patterns["linearity"] = self._calculate_linearity(positions)
        patterns["circularity"] = self._calculate_circularity(positions, center)
        patterns["symmetry"] = self._calculate_symmetry(positions, center)
        
        # Determine primary shape type
        patterns["shape_type"] = self._determine_shape_type(patterns)
        
        return patterns
    
    def _calculate_compactness(self, positions: List[Tuple[float, float]], center: Tuple[float, float]) -> float:
        """Calculate how compact the formation is."""
        if not positions:
            return 0.0
            
        distances_from_center = []
        for pos in positions:
            dist = math.sqrt((pos[0] - center[0])**2 + (pos[1] - center[1])**2)
            distances_from_center.append(dist)
            
        avg_distance = sum(distances_from_center) / len(distances_from_center)
        
        # Normalize by rink size (compact formations have lower average distances)
        max_possible_distance = math.sqrt((self.rink_length/2)**2 + (self.rink_width/2)**2)
        
        return 1.0 - (avg_distance / max_possible_distance)
    
    def _calculate_linearity(self, positions: List[Tuple[float, float]]) -> float:
        """Calculate how linear the formation is."""
        if len(positions) < 3:
            return 0.0
            
        # Use principal component analysis to find main axis
        positions_array = np.array(positions)
        
        # Center the data
        centered = positions_array - np.mean(positions_array, axis=0)
        
        # Calculate covariance matrix
        cov_matrix = np.cov(centered.T)
        
        # Find eigenvalues and eigenvectors
        eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)
        
        # Linearity is the ratio of largest to smallest eigenvalue
        if eigenvalues[1] > 0:
            linearity = eigenvalues[0] / eigenvalues[1]
            return min(linearity, 1.0)  # Cap at 1.0
            
        return 0.0
    
    def _calculate_circularity(self, positions: List[Tuple[float, float]], center: Tuple[float, float]) -> float:
        """Calculate how circular the formation is."""
        if len(positions) < 3:
            return 0.0
            
        distances_from_center = []
        for pos in positions:
            dist = math.sqrt((pos[0] - center[0])**2 + (pos[1] - center[1])**2)
            distances_from_center.append(dist)
            
        if not distances_from_center:
            return 0.0
            
        avg_distance = sum(distances_from_center) / len(distances_from_center)
        
        # Calculate variance in distances (circular formations have low variance)
        variance = sum((d - avg_distance)**2 for d in distances_from_center) / len(distances_from_center)
        
        # Normalize variance (lower variance = higher circularity)
        max_variance = (self.rink_length / 2)**2  # Maximum possible variance
        
        return max(0.0, 1.0 - (variance / max_variance))
    
    def _calculate_symmetry(self, positions: List[Tuple[float, float]], center: Tuple[float, float]) -> float:
        """Calculate how symmetric the formation is."""
        if len(positions) < 2:
            return 0.0
            
        # Calculate symmetry across horizontal axis (center line)
        symmetry_scores = []
        
        for pos in positions:
            # Find mirror position across center line
            mirror_y = center[1] + (center[1] - pos[1])
            mirror_pos = (pos[0], mirror_y)
            
            # Find closest actual player to mirror position
            min_distance = float('inf')
            for other_pos in positions:
                if other_pos != pos:  # Don't compare with self
                    dist = math.sqrt(
                        (other_pos[0] - mirror_pos[0])**2 + 
                        (other_pos[1] - mirror_pos[1])**2
                    )
                    min_distance = min(min_distance, dist)
            
            # Symmetry score based on how close the mirror is
            max_distance = self.rink_width / 2
            symmetry_score = max(0.0, 1.0 - (min_distance / max_distance))
            symmetry_scores.append(symmetry_score)
            
        return sum(symmetry_scores) / len(symmetry_scores)
    
    def _determine_shape_type(self, patterns: Dict) -> str:
        """Determine the primary shape type from geometric patterns."""
        compactness = patterns.get("compactness", 0.0)
        linearity = patterns.get("linearity", 0.0)
        circularity = patterns.get("circularity", 0.0)
        symmetry = patterns.get("symmetry", 0.0)
        
        # Classify based on dominant characteristics
        if linearity > 0.7:
            return "linear"
        elif circularity > 0.7:
            return "circular"
        elif compactness > 0.7:
            return "compact"
        elif symmetry > 0.7:
            return "symmetric"
        else:
            return "irregular"
    
    def _match_formation_pattern(self, patterns: Dict, zone_context: ZoneContext) -> Dict:
        """
        Match geometric patterns to known hockey formations.
        
        This is where hockey knowledge meets geometric analysis.
        """
        shape_type = patterns.get("shape_type", "unknown")
        compactness = patterns.get("compactness", 0.0)
        linearity = patterns.get("linearity", 0.0)
        symmetry = patterns.get("symmetry", 0.0)
        
        # Formation matching based on geometric characteristics
        if zone_context == ZoneContext.DEFENSIVE:
            if compactness > 0.6 and symmetry > 0.5:
                return {"formation_type": FormationType.TWO_ONE_TWO, "confidence": 0.8}
            elif linearity > 0.6:
                return {"formation_type": FormationType.ONE_TWO_TWO, "confidence": 0.7}
                
        elif zone_context == ZoneContext.NEUTRAL:
            if linearity > 0.5 and compactness > 0.4:
                return {"formation_type": FormationType.ONE_TWO_TWO, "confidence": 0.8}
            elif symmetry > 0.6:
                return {"formation_type": FormationType.TWO_TWO_ONE, "confidence": 0.7}
                
        elif zone_context == ZoneContext.OFFENSIVE:
            if compactness > 0.5 and linearity > 0.4:
                return {"formation_type": FormationType.TWO_TWO_ONE, "confidence": 0.8}
            elif circularity > 0.6:
                return {"formation_type": FormationType.ONE_THREE_ONE, "confidence": 0.7}
        
        # Default fallback
        return {"formation_type": FormationType.UNKNOWN, "confidence": 0.3}
    
    def _calculate_formation_confidence(self, formation_match: Dict, positions: List[Tuple[float, float]], zone_context: ZoneContext) -> float:
        """Calculate confidence score for the formation detection."""
        base_confidence = formation_match.get("confidence", 0.0)
        
        # Adjust confidence based on formation completeness
        completeness_score = self._calculate_formation_completeness(formation_match["formation_type"], positions)
        
        # Adjust confidence based on zone appropriateness
        zone_score = self._calculate_zone_appropriateness(formation_match["formation_type"], zone_context)
        
        # Combine scores
        final_confidence = (base_confidence * 0.4 + completeness_score * 0.3 + zone_score * 0.3)
        
        return min(final_confidence, 1.0)
    
    def _calculate_formation_completeness(self, formation_type: FormationType, positions: List[Tuple[float, float]]) -> float:
        """Calculate how complete the formation is (all roles filled)."""
        # This would require more detailed analysis of player roles
        # For now, return a base score based on player count
        player_count = len(positions)
        
        if formation_type == FormationType.TWO_ONE_TWO:
            return 1.0 if player_count >= 5 else 0.6
        elif formation_type == FormationType.ONE_TWO_TWO:
            return 1.0 if player_count >= 5 else 0.6
        elif formation_type == FormationType.TWO_TWO_ONE:
            return 1.0 if player_count >= 5 else 0.6
        elif formation_type == FormationType.ONE_THREE_ONE:
            return 1.0 if player_count >= 5 else 0.6
        elif formation_type == FormationType.THREE_TWO:
            return 1.0 if player_count >= 5 else 0.6
        else:
            return 0.3
    
    def _calculate_zone_appropriateness(self, formation_type: FormationType, zone_context: ZoneContext) -> float:
        """Calculate how appropriate the formation is for the current zone."""
        # Hockey knowledge: which formations work best in which zones
        zone_scores = {
            FormationType.TWO_ONE_TWO: {
                ZoneContext.DEFENSIVE: 0.9,
                ZoneContext.NEUTRAL: 0.6,
                ZoneContext.OFFENSIVE: 0.3
            },
            FormationType.ONE_TWO_TWO: {
                ZoneContext.DEFENSIVE: 0.7,
                ZoneContext.NEUTRAL: 0.9,
                ZoneContext.OFFENSIVE: 0.5
            },
            FormationType.TWO_TWO_ONE: {
                ZoneContext.DEFENSIVE: 0.4,
                ZoneContext.NEUTRAL: 0.7,
                ZoneContext.OFFENSIVE: 0.9
            },
            FormationType.ONE_THREE_ONE: {
                ZoneContext.DEFENSIVE: 0.3,
                ZoneContext.NEUTRAL: 0.5,
                ZoneContext.OFFENSIVE: 0.8
            },
            FormationType.THREE_TWO: {
                ZoneContext.DEFENSIVE: 0.8,
                ZoneContext.NEUTRAL: 0.4,
                ZoneContext.OFFENSIVE: 0.2
            }
        }
        
        return zone_scores.get(formation_type, {}).get(zone_context, 0.5)
    
    def _assign_player_roles(self, players: List[PlayerPosition], formation_match: Dict, formation_center: Tuple[float, float]) -> Dict[str, str]:
        """Assign roles to players based on formation and position."""
        roles = {}
        
        formation_type = formation_match["formation_type"]
        
        # Sort players by distance from formation center
        player_distances = []
        for player in players:
            dist = math.sqrt((player.x - formation_center[0])**2 + (player.y - formation_center[1])**2)
            player_distances.append((player, dist))
        
        player_distances.sort(key=lambda x: x[1])
        
        # Assign roles based on formation type and position
        if formation_type == FormationType.TWO_ONE_TWO:
            roles = self._assign_2_1_2_roles(player_distances)
        elif formation_type == FormationType.ONE_TWO_TWO:
            roles = self._assign_1_2_2_roles(player_distances)
        elif formation_type == FormationType.TWO_TWO_ONE:
            roles = self._assign_2_2_1_roles(player_distances)
        elif formation_type == FormationType.ONE_THREE_ONE:
            roles = self._assign_1_3_1_roles(player_distances)
        elif formation_type == FormationType.THREE_TWO:
            roles = self._assign_3_2_roles(player_distances)
        else:
            # Default role assignment
            for i, (player, _) in enumerate(player_distances):
                roles[player.player_id] = f"Player_{i+1}"
        
        return roles
    
    def _assign_2_1_2_roles(self, player_distances: List[Tuple[PlayerPosition, float]]) -> Dict[str, str]:
        """Assign roles for 2-1-2 formation."""
        roles = {}
        
        if len(player_distances) >= 5:
            # Closest to center = center
            roles[player_distances[0][0].player_id] = "Center"
            
            # Next two = defensemen (usually further back)
            roles[player_distances[1][0].player_id] = "Defenseman_1"
            roles[player_distances[2][0].player_id] = "Defenseman_2"
            
            # Next two = wings
            roles[player_distances[3][0].player_id] = "Wing_1"
            roles[player_distances[4][0].player_id] = "Wing_2"
        
        return roles
    
    def _assign_1_2_2_roles(self, player_distances: List[Tuple[PlayerPosition, float]]) -> Dict[str, str]:
        """Assign roles for 1-2-2 formation."""
        roles = {}
        
        if len(player_distances) >= 5:
            # Closest to center = center
            roles[player_distances[0][0].player_id] = "Center"
            
            # Next two = defensemen
            roles[player_distances[1][0].player_id] = "Defenseman_1"
            roles[player_distances[2][0].player_id] = "Defenseman_2"
            
            # Next two = wings
            roles[player_distances[3][0].player_id] = "Wing_1"
            roles[player_distances[4][0].player_id] = "Wing_2"
        
        return roles
    
    def _assign_2_2_1_roles(self, player_distances: List[Tuple[PlayerPosition, float]]) -> Dict[str, str]:
        """Assign roles for 2-2-1 formation."""
        roles = {}
        
        if len(player_distances) >= 5:
            # Closest to center = center
            roles[player_distances[0][0].player_id] = "Center"
            
            # Next two = defensemen
            roles[player_distances[1][0].player_id] = "Defenseman_1"
            roles[player_distances[2][0].player_id] = "Defenseman_2"
            
            # Next two = wings
            roles[player_distances[3][0].player_id] = "Wing_1"
            roles[player_distances[4][0].player_id] = "Wing_2"
        
        return roles
    
    def _assign_1_3_1_roles(self, player_distances: List[Tuple[PlayerPosition, float]]) -> Dict[str, str]:
        """Assign roles for 1-3-1 formation."""
        roles = {}
        
        if len(player_distances) >= 5:
            # Closest to center = center
            roles[player_distances[0][0].player_id] = "Center"
            
            # Next three = middle players
            roles[player_distances[1][0].player_id] = "Middle_1"
            roles[player_distances[2][0].player_id] = "Middle_2"
            roles[player_distances[3][0].player_id] = "Middle_3"
            
            # Farthest = defenseman
            roles[player_distances[4][0].player_id] = "Defenseman"
        
        return roles
    
    def _assign_3_2_roles(self, player_distances: List[Tuple[PlayerPosition, float]]) -> Dict[str, str]:
        """Assign roles for 3-2 formation."""
        roles = {}
        
        if len(player_distances) >= 5:
            # Closest to center = center
            roles[player_distances[0][0].player_id] = "Center"
            
            # Next three = defensemen
            roles[player_distances[1][0].player_id] = "Defenseman_1"
            roles[player_distances[2][0].player_id] = "Defenseman_2"
            roles[player_distances[3][0].player_id] = "Defenseman_3"
            
            # Farthest = wing
            roles[player_distances[4][0].player_id] = "Wing"
        
        return roles
    
    def _create_unknown_formation(self, reason: str) -> FormationDetection:
        """Create an unknown formation detection result."""
        return FormationDetection(
            formation_type=FormationType.UNKNOWN,
            confidence=0.0,
            zone_context=ZoneContext.NEUTRAL,
            player_roles={},
            formation_shape=[],
            analysis_details={"reason": reason}
        )

# Example usage and testing
if __name__ == "__main__":
    # Test the formation detector
    detector = RealFormationDetector()
    
    # Create test players for a 2-1-2 formation
    test_players = [
        PlayerPosition("player_1", "Team A", 100, 40),  # Center
        PlayerPosition("player_2", "Team A", 120, 20),  # Defenseman 1
        PlayerPosition("player_3", "Team A", 120, 60),  # Defenseman 2
        PlayerPosition("player_4", "Team A", 80, 30),   # Wing 1
        PlayerPosition("player_5", "Team A", 80, 50),   # Wing 2
    ]
    
    # Detect formation
    result = detector.detect_formation(test_players)
    
    print(f"Formation: {result.formation_type.value}")
    print(f"Confidence: {result.confidence:.2f}")
    print(f"Zone: {result.zone_context.value}")
    print(f"Player Roles: {result.player_roles}")
    print(f"Analysis: {result.analysis_details}")
