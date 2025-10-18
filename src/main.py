#!/usr/bin/env python3
"""
NHL Post-Game Report Generator
Generates comprehensive PDF reports for NHL games using the NHL API
"""

import os
import sys
from datetime import datetime
from nhl_api_client import NHLAPIClient
from pdf_report_generator import PostGameReportGenerator

def main():
    """Main function to generate NHL post-game report"""
    print("🏒 NHL Post-Game Report Generator 🏒")
    print("=" * 50)
    
    # Initialize NHL API client
    print("Initializing NHL API client...")
    nhl_client = NHLAPIClient()
    
    try:
        # Find the most recent Stanley Cup Finals game between FLA and EDM
        print("Searching for recent Florida Panthers vs Edmonton Oilers game...")
        game_id = nhl_client.get_stanley_cup_finals_game()
        
        if not game_id:
            print("❌ No recent game found between FLA and EDM")
            print("Trying to find any recent game for demonstration...")
            
            # Try to find any recent game for demonstration
            game_id = nhl_client.find_recent_game('FLA', 'EDM', days_back=365)
            
            if not game_id:
                print("❌ No games found. Creating a sample report with mock data...")
                game_data = create_sample_game_data()
            else:
                print(f"✅ Found game ID: {game_id}")
                game_data = nhl_client.get_comprehensive_game_data(game_id)
        else:
            print(f"✅ Found Stanley Cup Finals game ID: {game_id}")
            game_data = nhl_client.get_comprehensive_game_data(game_id)
        
        # Generate the PDF report
        print("Generating PDF report...")
        generator = PostGameReportGenerator()
        
        # Create output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"nhl_postgame_report_{timestamp}.pdf"
        
        # Generate the report
        generator.generate_report(game_data, output_filename)
        
        print(f"✅ Report generated successfully: {output_filename}")
        print(f"📁 File location: {os.path.abspath(output_filename)}")
        
    except Exception as e:
        print(f"❌ Error generating report: {str(e)}")
        print("Creating sample report with mock data...")
        
        try:
            game_data = create_sample_game_data()
            generator = PostGameReportGenerator()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"nhl_postgame_report_sample_{timestamp}.pdf"
            
            generator.generate_report(game_data, output_filename)
            print(f"✅ Sample report generated: {output_filename}")
            
        except Exception as sample_error:
            print(f"❌ Error generating sample report: {str(sample_error)}")
            sys.exit(1)

def create_sample_game_data():
    """Create sample game data for demonstration purposes"""
    return {
        'game_center': {
            'game': {
                'gameDate': '2024-06-15',
                'awayTeamScore': 3,
                'homeTeamScore': 2,
                'awayTeamScoreByPeriod': [1, 1, 1, 0],
                'homeTeamScoreByPeriod': [0, 1, 1, 0]
            },
            'awayTeam': {
                'abbrev': 'FLA',
                'name': 'Florida Panthers'
            },
            'homeTeam': {
                'abbrev': 'EDM',
                'name': 'Edmonton Oilers'
            },
            'venue': {
                'default': 'Rogers Place'
            },
            'plays': [
                {
                    'typeDescKey': 'goal',
                    'periodNumber': 1,
                    'timeInPeriod': '12:34',
                    'team': {'abbrev': 'FLA'},
                    'scorer': {'name': 'Aleksander Barkov'},
                    'players': [
                        {'playerType': 'assist', 'name': 'Sam Reinhart'},
                        {'playerType': 'assist', 'name': 'Carter Verhaeghe'}
                    ],
                    'score': '1-0'
                },
                {
                    'typeDescKey': 'goal',
                    'periodNumber': 2,
                    'timeInPeriod': '8:45',
                    'team': {'abbrev': 'EDM'},
                    'scorer': {'name': 'Connor McDavid'},
                    'players': [
                        {'playerType': 'assist', 'name': 'Leon Draisaitl'}
                    ],
                    'score': '1-1'
                },
                {
                    'typeDescKey': 'goal',
                    'periodNumber': 2,
                    'timeInPeriod': '15:22',
                    'team': {'abbrev': 'FLA'},
                    'scorer': {'name': 'Sam Reinhart'},
                    'players': [
                        {'playerType': 'assist', 'name': 'Aleksander Barkov'}
                    ],
                    'score': '2-1'
                },
                {
                    'typeDescKey': 'goal',
                    'periodNumber': 3,
                    'timeInPeriod': '6:18',
                    'team': {'abbrev': 'EDM'},
                    'scorer': {'name': 'Zach Hyman'},
                    'players': [
                        {'playerType': 'assist', 'name': 'Connor McDavid'},
                        {'playerType': 'assist', 'name': 'Evan Bouchard'}
                    ],
                    'score': '2-2'
                },
                {
                    'typeDescKey': 'goal',
                    'periodNumber': 3,
                    'timeInPeriod': '18:45',
                    'team': {'abbrev': 'FLA'},
                    'scorer': {'name': 'Carter Verhaeghe'},
                    'players': [
                        {'playerType': 'assist', 'name': 'Sam Reinhart'}
                    ],
                    'score': '3-2'
                }
            ]
        },
        'boxscore': {
            'awayTeam': {
                'abbrev': 'FLA',
                'score': 3,
                'sog': 28,
                'powerPlayConversion': '1/3',
                'penaltyMinutes': 8,
                'hits': 24,
                'faceoffWins': 32,
                'blockedShots': 18,
                'giveaways': 12,
                'takeaways': 8,
                'players': [
                    {
                        'name': 'Aleksander Barkov',
                        'position': 'C',
                        'stats': {'goals': 1, 'assists': 1, 'shots': 4}
                    },
                    {
                        'name': 'Sam Reinhart',
                        'position': 'RW',
                        'stats': {'goals': 1, 'assists': 2, 'shots': 5}
                    },
                    {
                        'name': 'Carter Verhaeghe',
                        'position': 'LW',
                        'stats': {'goals': 1, 'assists': 1, 'shots': 3}
                    },
                    {
                        'name': 'Sergei Bobrovsky',
                        'position': 'G',
                        'stats': {
                            'shotsAgainst': 32,
                            'saves': 30,
                            'goalsAgainst': 2,
                            'timeOnIce': '60:00'
                        }
                    }
                ]
            },
            'homeTeam': {
                'abbrev': 'EDM',
                'score': 2,
                'sog': 32,
                'powerPlayConversion': '0/2',
                'penaltyMinutes': 6,
                'hits': 28,
                'faceoffWins': 28,
                'blockedShots': 22,
                'giveaways': 15,
                'takeaways': 10,
                'players': [
                    {
                        'name': 'Connor McDavid',
                        'position': 'C',
                        'stats': {'goals': 1, 'assists': 1, 'shots': 6}
                    },
                    {
                        'name': 'Leon Draisaitl',
                        'position': 'C',
                        'stats': {'goals': 0, 'assists': 1, 'shots': 4}
                    },
                    {
                        'name': 'Zach Hyman',
                        'position': 'LW',
                        'stats': {'goals': 1, 'assists': 0, 'shots': 5}
                    },
                    {
                        'name': 'Stuart Skinner',
                        'position': 'G',
                        'stats': {
                            'shotsAgainst': 28,
                            'saves': 25,
                            'goalsAgainst': 3,
                            'timeOnIce': '58:45'
                        }
                    }
                ]
            }
        }
    }

if __name__ == "__main__":
    main()
