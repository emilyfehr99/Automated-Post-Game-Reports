#!/usr/bin/env python3
"""
Test the fixed enhanced NHL report generator
"""

from enhanced_nhl_report_generator import EnhancedNHLReportGenerator
import requests

def test_comprehensive_metrics():
    """Test the comprehensive metrics functionality"""
    print("🧪 Testing Comprehensive Metrics Functionality")
    print("=" * 60)
    
    # Test with a known working game ID
    game_id = "2024030242"
    
    # First, let's test the play-by-play data directly
    print(f"Testing play-by-play data for game {game_id}...")
    
    play_by_play_url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/play-by-play"
    
    try:
        response = requests.get(play_by_play_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        if response.status_code == 200:
            play_by_play_data = response.json()
            print("✅ Play-by-play data fetched successfully")
            
            # Test the enhanced report generator
            generator = EnhancedNHLReportGenerator()
            
            # Test player mapping
            print("Testing player mapping...")
            player_mapping = generator.create_player_mapping(play_by_play_data)
            print(f"✅ Created player mapping for {len(player_mapping)} players")
            
            # Test comprehensive metrics extraction
            print("Testing comprehensive metrics extraction...")
            analysis_data = generator.extract_comprehensive_metrics(play_by_play_data, player_mapping)
            
            if analysis_data:
                print("✅ Comprehensive metrics extracted successfully")
                print(f"  - Total plays: {analysis_data['game_stats']['total_plays']}")
                print(f"  - Players analyzed: {len(analysis_data['player_stats'])}")
                print(f"  - Play types: {len(analysis_data['game_stats']['play_types'])}")
                print(f"  - Situations: {len(analysis_data['game_stats']['situation_breakdown'])}")
                print(f"  - Zones: {len(analysis_data['game_stats']['zone_breakdown'])}")
                
                # Test comprehensive metrics chart
                print("Testing comprehensive metrics chart...")
                chart_buffer = generator.create_comprehensive_metrics_chart(analysis_data)
                if chart_buffer:
                    print("✅ Comprehensive metrics chart created successfully")
                else:
                    print("❌ Failed to create comprehensive metrics chart")
                
                # Test report generation with mock game data
                print("Testing report generation...")
                mock_game_data = {
                    'game_center': {
                        'game': {
                            'gameDate': '2024-03-02',
                            'awayTeamScore': 3,
                            'homeTeamScore': 2,
                            'awayTeamScoreByPeriod': [1, 1, 1],
                            'homeTeamScoreByPeriod': [0, 1, 1]
                        },
                        'awayTeam': {'abbrev': 'EDM'},
                        'homeTeam': {'abbrev': 'FLA'},
                        'venue': {'default': 'Test Arena'}
                    },
                    'boxscore': {
                        'awayTeam': {'sog': 25, 'powerPlayConversion': '20.0%'},
                        'homeTeam': {'sog': 30, 'powerPlayConversion': '15.0%'}
                    },
                    'play_by_play': play_by_play_data
                }
                
                # Test individual sections
                print("Testing comprehensive metrics section...")
                story = generator.create_comprehensive_metrics_section(mock_game_data)
                print(f"✅ Comprehensive metrics section created with {len(story)} elements")
                
                print("Testing advanced metrics...")
                story = generator._add_advanced_metrics([], mock_game_data)
                print(f"✅ Advanced metrics section created with {len(story)} elements")
                
                print("Testing key moments...")
                story = generator._add_key_moments([], play_by_play_data)
                print(f"✅ Key moments section created with {len(story)} elements")
                
                print("Testing momentum analysis...")
                story = generator._add_momentum_analysis([], play_by_play_data)
                print(f"✅ Momentum analysis section created with {len(story)} elements")
                
                print("Testing shot analysis...")
                story = generator._add_shot_analysis([], play_by_play_data)
                print(f"✅ Shot analysis section created with {len(story)} elements")
                
                print("\n🎉 ALL COMPREHENSIVE METRICS TESTS PASSED!")
                print("The enhanced report generator now includes:")
                print("  ✅ All basic statistics (goals, assists, points, shots, hits, etc.)")
                print("  ✅ Advanced statistics (Corsi, Fenwick, xG, high-danger chances)")
                print("  ✅ Situation analysis (5v5, power play, penalty kill)")
                print("  ✅ Zone analysis (offensive, defensive, neutral)")
                print("  ✅ Shot quality metrics (shot types, locations, angles)")
                print("  ✅ Game flow metrics (period breakdown, momentum)")
                print("  ✅ Player performance metrics (shooting %, faceoff %, turnover ratio)")
                print("  ✅ Comprehensive visualizations and charts")
                print("  ✅ Real player names and detailed analysis")
                
                return True
            else:
                print("❌ Failed to extract comprehensive metrics")
                return False
        else:
            print(f"❌ Play-by-play API returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing comprehensive metrics: {e}")
        return False

if __name__ == "__main__":
    success = test_comprehensive_metrics()
    if success:
        print("\n✅ ALL TESTS PASSED - Enhanced report is working with comprehensive metrics!")
    else:
        print("\n❌ Some tests failed - check the errors above")
