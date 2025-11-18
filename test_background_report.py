#!/usr/bin/env python3
"""
Test script to generate a post-game report with crumpled paper background
"""

import os
import sys
from pdf_report_generator import PostGameReportGenerator

def create_mock_game_data():
    """Create mock game data for testing the background"""
    return {
        'gameData': {
            'game': {
                'pk': 2025020083,
                'season': '20252026',
                'type': 'R',
                'gameDate': '2025-10-19T02:00:00Z'
            },
            'teams': {
                'away': {
                    'id': 25,
                    'name': 'Dallas Stars',
                    'abbreviation': 'DAL'
                },
                'home': {
                    'id': 19,
                    'name': 'St. Louis Blues',
                    'abbreviation': 'STL'
                }
            }
        },
        'boxscore': {
            'teams': {
                'away': {
                    'team': {'id': 25, 'name': 'Dallas Stars', 'abbreviation': 'DAL'},
                    'teamStats': {
                        'teamSkaterStats': {
                            'goals': 3,
                            'shots': 28,
                            'hits': 22,
                            'pim': 8,
                            'powerPlayGoals': 1,
                            'powerPlayOpportunities': 3,
                            'faceOffWinPercentage': 52.3,
                            'blocked': 12,
                            'takeaways': 8,
                            'giveaways': 6
                        }
                    }
                },
                'home': {
                    'team': {'id': 19, 'name': 'St. Louis Blues', 'abbreviation': 'STL'},
                    'teamStats': {
                        'teamSkaterStats': {
                            'goals': 2,
                            'shots': 31,
                            'hits': 18,
                            'pim': 10,
                            'powerPlayGoals': 0,
                            'powerPlayOpportunities': 4,
                            'faceOffWinPercentage': 47.7,
                            'blocked': 15,
                            'takeaways': 6,
                            'giveaways': 8
                        }
                    }
                }
            }
        },
        'liveData': {
            'plays': {
                'allPlays': [
                    {
                        'about': {
                            'eventIdx': 1,
                            'eventId': 1,
                            'period': 1,
                            'periodType': 'REGULAR',
                            'ordinalNum': '1st',
                            'periodTime': '00:15',
                            'periodTimeRemaining': '19:45',
                            'dateTime': '2025-10-19T02:00:15Z'
                        },
                        'result': {
                            'event': 'Goal',
                            'eventCode': 'DAL1',
                            'eventTypeId': 'GOAL',
                            'description': 'DAL Goal - Tyler Seguin (1) Wrist Shot, assists: Joe Pavelski (1)'
                        },
                        'team': {'id': 25, 'name': 'Dallas Stars', 'abbreviation': 'DAL'},
                        'players': [
                            {'player': {'id': 8475798, 'fullName': 'Tyler Seguin'}, 'playerType': 'Scorer'},
                            {'player': {'id': 8470612, 'fullName': 'Joe Pavelski'}, 'playerType': 'Assist'}
                        ],
                        'coordinates': {'x': 15, 'y': 8},
                        'details': {'xCoord': 15, 'yCoord': 8, 'zoneCode': 'O'}
                    }
                ]
            }
        }
    }

def test_background_report():
    """Generate a test report with the crumpled paper background"""
    
    # Initialize the report generator
    generator = PostGameReportGenerator()
    
    # Create mock game data
    game_data = create_mock_game_data()
    game_id = "2025020083"
    
    # Generate output filename
    output_filename = f"test_background_report_{game_id}.pdf"
    
    print(f"Generating test report with background: {output_filename}")
    
    try:
        # Generate the report
        generator.generate_report(game_data, output_filename, game_id)
        print(f"✅ Test report generated successfully: {output_filename}")
        
        # Check if file exists and get size
        if os.path.exists(output_filename):
            file_size = os.path.getsize(output_filename)
            print(f"📄 File size: {file_size:,} bytes")
            print(f"📁 Full path: {os.path.abspath(output_filename)}")
        else:
            print("❌ Report file was not created")
            
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_background_report()