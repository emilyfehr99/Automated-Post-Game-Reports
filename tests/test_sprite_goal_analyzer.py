import pytest
from analyzers.sprite_goal_analyzer import SpriteGoalAnalyzer

def test_sprite_goal_analyzer_goal_orientation():
    analyzer = SpriteGoalAnalyzer()
    
    # Test right goal
    mock_right_sprite = [
        {'onIce': {'1': {'id': 1, 'x': 2200, 'y': 500}}}
    ]
    assert analyzer._get_target_goal_x(mock_right_sprite) == 2250
    
    # Test left goal
    mock_left_sprite = [
        {'onIce': {'1': {'id': 1, 'x': 180, 'y': 500}}}
    ]
    assert analyzer._get_target_goal_x(mock_left_sprite) == 150

def test_sprite_goal_analyzer_traffic_bounds():
    mock_game_data = {
        'id': '2025020536',
        'awayTeam': {'id': 16, 'abbrev': 'CHI'},
        'homeTeam': {'id': 8, 'abbrev': 'MTL'},
        'plays': [
            {
                'typeDescKey': 'goal',
                'eventId': 101,
                'details': {
                    'eventOwnerTeamId': 16,
                    'xCoord': 80,
                    'yCoord': 5,
                    'shotType': 'Tip-In',
                    'assist1PlayerId': 1234
                }
            }
        ]
    }
    
    analyzer = SpriteGoalAnalyzer(game_data=mock_game_data)
    # Mock get_sprite_data to return None so it exercises official PBP fallback
    analyzer.get_sprite_data = lambda g, e: None
    
    res = analyzer.analyze_game_goals_by_team('2025020536', game_data=mock_game_data)
    assert res is not None
    chi_stats = res['stats'][16]
    assert chi_stats['total_goals'] == 1
    assert 0.0 <= chi_stats['net_front_traffic_pct'] <= 100.0
    assert chi_stats['net_front_traffic_pct'] == 100.0
