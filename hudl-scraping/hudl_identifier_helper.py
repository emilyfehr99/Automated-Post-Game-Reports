#!/usr/bin/env python3
"""
Hudl Identifier Helper
Utilities for working with Hudl's unique identifiers for players, teams, and leagues
"""

import json
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class HudlIdentifier:
    """Represents a Hudl identifier"""
    type: str  # 'player', 'team', 'game', 'league'
    value: str
    name: str
    metadata: Dict[str, Any] = None

class HudlIdentifierHelper:
    """Helper class for working with Hudl identifiers"""
    
    def __init__(self):
        """Initialize the identifier helper"""
        self.identifiers = {
            'players': {},
            'teams': {},
            'games': {},
            'leagues': {}
        }
        
        # Known Bobcats identifiers
        self.known_identifiers = {
            'teams': {
                '21479': {
                    'name': 'Bobcats',
                    'type': 'team',
                    'league': 'hockey'
                }
            }
        }
    
    def add_identifier(self, identifier: HudlIdentifier):
        """Add a new identifier to the collection"""
        if identifier.type in self.identifiers:
            self.identifiers[identifier.type][identifier.value] = {
                'name': identifier.name,
                'metadata': identifier.metadata or {}
            }
    
    def get_identifier(self, identifier_type: str, value: str) -> Optional[Dict]:
        """Get identifier information by type and value"""
        if identifier_type in self.identifiers:
            return self.identifiers[identifier_type].get(value)
        return None
    
    def find_identifier_by_name(self, identifier_type: str, name: str) -> Optional[str]:
        """Find identifier value by name"""
        if identifier_type in self.identifiers:
            for value, data in self.identifiers[identifier_type].items():
                if data['name'].lower() == name.lower():
                    return value
        return None
    
    def extract_identifiers_from_data(self, data: Any, data_type: str = "unknown") -> List[HudlIdentifier]:
        """Extract Hudl identifiers from raw data"""
        identifiers = []
        
        if isinstance(data, dict):
            # Look for common identifier patterns
            id_patterns = {
                'player': ['player_id', 'id', 'hudl_player_id', 'athlete_id'],
                'team': ['team_id', 'id', 'hudl_team_id'],
                'game': ['game_id', 'id', 'hudl_game_id', 'match_id'],
                'league': ['league_id', 'id', 'hudl_league_id', 'competition_id']
            }
            
            for identifier_type, patterns in id_patterns.items():
                for pattern in patterns:
                    if pattern in data and data[pattern]:
                        identifier = HudlIdentifier(
                            type=identifier_type,
                            value=str(data[pattern]),
                            name=data.get('name', f"Unknown {identifier_type}"),
                            metadata={'source': data_type, 'pattern': pattern}
                        )
                        identifiers.append(identifier)
                        break
        
        return identifiers
    
    def build_identifier_mapping(self, team_data: Dict) -> Dict[str, Any]:
        """Build a comprehensive mapping of all identifiers found in team data"""
        mapping = {
            'team': {},
            'players': {},
            'games': {},
            'leagues': {},
            'summary': {
                'total_identifiers': 0,
                'by_type': {}
            }
        }
        
        # Extract team identifier
        if 'team_id' in team_data:
            mapping['team'] = {
                'id': team_data['team_id'],
                'name': team_data.get('team_name', 'Unknown Team')
            }
        
        # Extract player identifiers
        if 'players' in team_data:
            for player in team_data['players']:
                player_id = self._extract_id(player, ['player_id', 'id', 'hudl_player_id'])
                if player_id:
                    mapping['players'][player_id] = {
                        'name': player.get('name', 'Unknown Player'),
                        'position': player.get('position', 'Unknown'),
                        'number': player.get('number', 'Unknown')
                    }
        
        # Extract game identifiers
        if 'games' in team_data:
            for game in team_data['games']:
                game_id = self._extract_id(game, ['game_id', 'id', 'hudl_game_id'])
                if game_id:
                    mapping['games'][game_id] = {
                        'date': game.get('date', 'Unknown'),
                        'opponent': game.get('opponent', 'Unknown'),
                        'score': game.get('score', 'Unknown')
                    }
        
        # Count identifiers
        for identifier_type in ['team', 'players', 'games', 'leagues']:
            count = len(mapping[identifier_type])
            mapping['summary']['by_type'][identifier_type] = count
            mapping['summary']['total_identifiers'] += count
        
        return mapping
    
    def _extract_id(self, data: Dict, id_fields: List[str]) -> Optional[str]:
        """Extract ID from data using multiple field names"""
        for field in id_fields:
            if field in data and data[field]:
                return str(data[field])
        return None
    
    def generate_identifier_report(self, team_data: Dict) -> str:
        """Generate a human-readable report of all identifiers"""
        mapping = self.build_identifier_mapping(team_data)
        
        report = []
        report.append("🏒 Hudl Identifier Report")
        report.append("=" * 50)
        
        # Team information
        if mapping['team']:
            report.append(f"\n📊 Team:")
            report.append(f"  ID: {mapping['team']['id']}")
            report.append(f"  Name: {mapping['team']['name']}")
        
        # Player information
        if mapping['players']:
            report.append(f"\n👥 Players ({len(mapping['players'])}):")
            for player_id, player_data in mapping['players'].items():
                report.append(f"  {player_id}: {player_data['name']} ({player_data['position']})")
        
        # Game information
        if mapping['games']:
            report.append(f"\n🏆 Games ({len(mapping['games'])}):")
            for game_id, game_data in mapping['games'].items():
                report.append(f"  {game_id}: {game_data['date']} vs {game_data['opponent']}")
        
        # Summary
        report.append(f"\n📈 Summary:")
        report.append(f"  Total Identifiers: {mapping['summary']['total_identifiers']}")
        for identifier_type, count in mapping['summary']['by_type'].items():
            if count > 0:
                report.append(f"  {identifier_type.title()}: {count}")
        
        return "\n".join(report)
    
    def save_identifiers(self, filename: str = "hudl_identifiers.json"):
        """Save all identifiers to a JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.identifiers, f, indent=2)
        return filename
    
    def load_identifiers(self, filename: str = "hudl_identifiers.json"):
        """Load identifiers from a JSON file"""
        try:
            with open(filename, 'r') as f:
                self.identifiers = json.load(f)
            return True
        except FileNotFoundError:
            return False

def main():
    """Example usage of the identifier helper"""
    print("🆔 Hudl Identifier Helper")
    print("=" * 40)
    
    helper = HudlIdentifierHelper()
    
    # Example team data with identifiers
    sample_data = {
        'team_id': '21479',
        'team_name': 'Bobcats',
        'players': [
            {'player_id': '12345', 'name': 'John Smith', 'position': 'Forward', 'number': '12'},
            {'player_id': '12346', 'name': 'Mike Johnson', 'position': 'Defense', 'number': '5'},
            {'player_id': '12347', 'name': 'Sarah Wilson', 'position': 'Goalie', 'number': '1'}
        ],
        'games': [
            {'game_id': 'g001', 'date': '2024-01-15', 'opponent': 'Eagles', 'score': '3-2'},
            {'game_id': 'g002', 'date': '2024-01-22', 'opponent': 'Hawks', 'score': '1-4'}
        ]
    }
    
    # Build identifier mapping
    mapping = helper.build_identifier_mapping(sample_data)
    print(json.dumps(mapping, indent=2))
    
    # Generate report
    report = helper.generate_identifier_report(sample_data)
    print(f"\n{report}")
    
    # Save identifiers
    filename = helper.save_identifiers()
    print(f"\n💾 Identifiers saved to: {filename}")

if __name__ == "__main__":
    main()
