#!/usr/bin/env python3
"""
Analyze Team Report Structure - Extract detailed structure of each component
"""
import ast
import inspect
from team_report_generator import TeamReportGenerator

def analyze_component_structure():
    """Extract and display the structure of each report component"""
    
    gen = TeamReportGenerator()
    
    # Component creation methods
    components = {
        'Header Image': gen.create_header_image,
        'Team Summary': gen.create_team_summary_section,
        'Home/Away Comparison Table': gen.create_home_away_comparison,
        'Period Performance Table': gen.create_period_by_period_table,
        'Performance Trend Graph': gen.create_performance_trend_graph,
        'Movement Patterns Table': gen.create_movement_patterns_visualization,
        'Player Stats Section': gen.create_player_stats_section,
        'Clutch Performance Box': gen.create_clutch_performance_box,
    }
    
    print("=" * 80)
    print("TEAM REPORT COMPONENT STRUCTURE ANALYSIS")
    print("=" * 80)
    print()
    
    # Read the source file to extract detailed structure
    with open('team_report_generator.py', 'r') as f:
        source = f.read()
    
    # Extract structure for each component
    structures = {
        'Header Image (create_header_image)': {
            'type': 'Image Component',
            'size': '756 x 180 points',
            'components': [
                'Team logo (240x212px)',
                'NHL logo (212x184px)',
                'Full team name (RussoOne-Regular, 110pt)',
                'Subtitle: "Team Report | 25/26 Regular Season" (43pt)',
                'Grey line separator'
            ],
            'positioning': 'Absolute top of page'
        },
        
        'Team Summary Section (create_team_summary_section)': {
            'type': 'Spacer (minimal)',
            'height': '4 points',
            'note': 'Minimal section - record info moved to home/away table'
        },
        
        'Home/Away Comparison Table (create_home_away_comparison)': {
            'type': 'Table',
            'title': 'HOME VS AWAY COMPARISON',
            'title_style': {
                'background': 'Team color',
                'font': 'RussoOne-Regular, 10pt, Bold',
                'text_color': 'White',
                'padding': '6pt top/bottom, 8pt left/right'
            },
            'columns': [
                'Venue', 'Record', 'GF', 'S', 'CF%', 'PP%', 'PIM', 'Hits', 
                'FO%', 'BLK', 'GV', 'TK', 'GS', 'xG', 'NZT', 'NZTSA', 
                'OZS', 'NZS', 'DZS', 'FC', 'Rush', 'WinsAX'
            ],
            'num_columns': 22,
            'column_widths': [
                '0.5"', '0.4"', '0.35"', '0.35"', '0.4"', '0.35"', '0.35"', 
                '0.35"', '0.4"', '0.35"', '0.35"', '0.35"', '0.35"', '0.4"', 
                '0.35"', '0.4"', '0.35"', '0.35"', '0.35"', '0.35"', '0.35"', '0.4"'
            ],
            'rows': ['Header row (team color)', 'Home row (beige)', 'Away row (lightgrey)'],
            'row_style': {
                'header': {
                    'background': 'Team color',
                    'font': 'RussoOne-Regular, 7pt',
                    'text_color': 'White',
                    'padding': '8pt bottom'
                },
                'data_rows': {
                    'font': 'RussoOne-Regular, 6pt',
                    'padding': '4pt top/bottom',
                    'alternating_colors': 'beige/lightgrey'
                }
            },
            'data_sources': {
                'Record': 'From NHL standings API',
                'GF': 'Average goals per game',
                'S': 'Average shots per game',
                'CF%': 'Average Corsi For percentage',
                'PP%': 'Average power play percentage',
                'PIM': 'Average penalty minutes per game',
                'Hits': 'Average hits per game',
                'FO%': 'Average faceoff win percentage',
                'BLK': 'Average blocks per game',
                'GV': 'Average giveaways per game',
                'TK': 'Average takeaways per game',
                'GS': 'Average Game Score per game',
                'xG': 'Average Expected Goals per game',
                'NZT': 'Average Neutral Zone Turnovers per game',
                'NZTSA': 'Average NZ Turnovers to Shots Against per game',
                'OZS': 'Average Offensive Zone Shots per game',
                'NZS': 'Average Neutral Zone Shots per game',
                'DZS': 'Average Defensive Zone Shots per game',
                'FC': 'Average Faceoff Cycle SOG per game',
                'Rush': 'Average Rush SOG per game',
                'WinsAX': 'Wins Above Expected count'
            }
        },
        
        'Period Performance Table (create_period_by_period_table)': {
            'type': 'Table',
            'title': 'PERIOD PERFORMANCE',
            'title_style': {
                'background': 'Team color',
                'font': 'RussoOne-Regular, 10pt, Bold',
                'text_color': 'White',
                'padding': '6pt top/bottom, 8pt left/right'
            },
            'columns': [
                'Period', 'GF', 'S', 'CF%', 'PP', 'PIM', 'Hits', 'FO%', 
                'BLK', 'GV', 'TK', 'GS', 'xG', 'NZT', 'NZTSA', 'OZS', 
                'NZS', 'DZS', 'FC', 'Rush'
            ],
            'num_columns': 20,
            'column_widths': [
                '0.4"', '0.35"', '0.35"', '0.4"', '0.35"', '0.35"', 
                '0.35"', '0.4"', '0.35"', '0.35"', '0.35"', '0.35"', 
                '0.4"', '0.35"', '0.4"', '0.35"', '0.35"', '0.35"', 
                '0.35"', '0.35"'
            ],
            'rows': ['Header row (team color)', 'Period 1 (beige)', 'Period 2 (lightgrey)', 'Period 3 (beige)'],
            'row_style': {
                'header': {
                    'font': 'RussoOne-Regular, 7pt',
                    'padding': '8pt bottom'
                },
                'data_rows': {
                    'font': 'RussoOne-Regular, 6.5pt',
                    'padding': '4pt top/bottom',
                    'alternating_colors': 'beige/lightgrey'
                }
            },
            'data_calculation': {
                'GF': 'Total goals scored in period (sum)',
                'S': 'Average shots per game in period',
                'CF%': 'Average Corsi For percentage in period',
                'PP': 'Total PP goals / Total PP attempts (format: "goals/attempts")',
                'PIM': 'Average penalty minutes per game in period',
                'Hits': 'Average hits per game in period',
                'FO%': 'Average faceoff win percentage in period',
                'BLK': 'Average blocks per game in period',
                'GV': 'Average giveaways per game in period',
                'TK': 'Average takeaways per game in period',
                'GS': 'Average Game Score per game in period',
                'xG': 'Average Expected Goals per game in period',
                'NZT': 'Average Neutral Zone Turnovers per game in period',
                'NZTSA': 'Average NZ Turnovers to Shots Against per game in period',
                'OZS': 'Average Offensive Zone Shots per game in period',
                'NZS': 'Average Neutral Zone Shots per game in period',
                'DZS': 'Average Defensive Zone Shots per game in period',
                'FC': 'Average Faceoff Cycle SOG per game in period',
                'Rush': 'Average Rush SOG per game in period'
            }
        },
        
        'Performance Trend Graph (create_performance_trend_graph)': {
            'type': 'Matplotlib Line Chart',
            'dimensions': '3.75" width x 2.5" height',
            'chart_type': 'Dual-axis plot',
            'left_axis': {
                'label': 'Goals / Expected Goals',
                'data_series': [
                    {'name': 'GF', 'type': 'line', 'marker': 'o', 'color': 'green', 'alpha': 0.7},
                    {'name': 'GA', 'type': 'line', 'marker': 's', 'color': 'red', 'alpha': 0.7},
                    {'name': 'xGF', 'type': 'line', 'marker': '^', 'color': 'blue', 'linestyle': '--', 'alpha': 0.7},
                    {'name': 'Avg GF', 'type': 'horizontal line', 'color': 'green', 'linestyle': ':', 'alpha': 0.5},
                    {'name': 'Avg GA', 'type': 'horizontal line', 'color': 'red', 'linestyle': ':', 'alpha': 0.5}
                ]
            },
            'right_axis': {
                'label': 'Cumulative Win %',
                'data_series': [
                    {'name': 'Win %', 'type': 'line', 'color': 'purple', 'alpha': 0.8, 'fill': True, 'fill_alpha': 0.2},
                    {'name': '50% line', 'type': 'horizontal line', 'color': 'purple', 'linestyle': ':', 'alpha': 0.3}
                ],
                'y_limit': [0, 100]
            },
            'x_axis': {
                'label': 'Game Number',
                'data': 'Sequential game numbers (1, 2, 3, ...)'
            },
            'features': [
                'Transparent background',
                'Grid enabled (alpha 0.3, dashed)',
                'Legend in upper left',
                'RussoOne-Regular font (if available)',
                'Title: "{team} Performance Trends"'
            ],
            'positioning': {
                'x_offset': '3cm from left edge',
                'y_position': '1cm above top players table',
                'rendering': 'Absolute positioning via LeftAlignedImage Flowable'
            }
        },
        
        'Movement Patterns Table (create_movement_patterns_visualization)': {
            'type': 'Table',
            'title': 'MOVEMENT PATTERNS',
            'title_style': {
                'background': 'Team color',
                'font': 'RussoOne-Regular, 10pt, Bold',
                'text_color': 'White',
                'padding': '6pt top/bottom, 8pt left/right'
            },
            'columns': [
                'Venue',
                'Cross-Ice Puck\nMovement Pre-Shot',
                'Shot Distance\nFrom Goal'
            ],
            'num_columns': 3,
            'column_widths': ['0.8"', '1.3"', '1.3"'],
            'rows': ['Header row (team color)', 'Home row (beige)', 'Away row (lightgrey)'],
            'classification': {
                'Lateral Movement (Cross-Ice)': {
                    'Stationary': 'avg_feet == 0',
                    'Minor': '0 < avg_feet < 10',
                    'Cross-ice': '10 <= avg_feet < 20',
                    'Wide-lane': '20 <= avg_feet < 35',
                    'Full-width': 'avg_feet >= 35'
                },
                'Longitudinal Movement (Shot Distance)': {
                    'Stationary': 'avg_feet == 0',
                    'Close-range': '0 < avg_feet < 15',
                    'Mid-range': '15 <= avg_feet < 30',
                    'Extended': '30 <= avg_feet < 50',
                    'Long-range': 'avg_feet >= 50'
                }
            },
            'data_source': 'Average lateral/longitudinal movement metrics from AdvancedMetricsAnalyzer',
            'positioning': {
                'x_offset': '10cm from left edge (right of trends graph)',
                'y_position': '1cm above top players table (aligned with graph)',
                'rendering': 'Absolute positioning via CenteredShiftFlowable'
            }
        },
        
        'Player Stats Section (create_player_stats_section)': {
            'type': 'Table',
            'title': 'TOP & BOTTOM 3 PLAYERS (GS + xG)',
            'title_style': {
                'background': 'Team color',
                'font': 'RussoOne-Regular, 10pt',
                'text_color': 'White',
                'padding': '6pt top/bottom',
                'width': '7.5"'
            },
            'columns': ['Rank', 'Player', 'GP', 'GS/G', 'xG/G', 'GS+xG/G'],
            'num_columns': 6,
            'column_widths': ['0.4"', '1.5"', '0.4"', '0.6"', '0.6"', '0.7"'],
            'rows': [
                'Header row (grey background, whitesmoke text)',
                'Rank 1 (beige)',
                'Rank 2 (beige)',
                'Rank 3 (beige)',
                'Bottom rank (lightgrey)',
                '2nd from bottom (lightgrey)',
                '3rd from bottom (lightgrey)'
            ],
            'row_style': {
                'header': {
                    'background': 'Grey',
                    'text_color': 'Whitesmoke',
                    'font': 'RussoOne-Regular, 7pt',
                    'padding': '8pt bottom'
                },
                'top_3': {
                    'background': 'Beige',
                    'font': 'RussoOne-Regular, 7pt'
                },
                'bottom_3': {
                    'background': 'Lightgrey',
                    'font': 'RussoOne-Regular, 7pt'
                }
            },
            'filtering': {
                'minimum_games': 3,
                'exclude_goalies': True,
                'sort_by': 'avg_gs_plus_xg (descending)'
            },
            'data_calculation': {
                'GP': 'Number of games played',
                'GS/G': 'Total Game Score / Games Played',
                'xG/G': 'Total Expected Goals / Games Played',
                'GS+xG/G': 'Average of (GS + xG) per game'
            }
        },
        
        'Clutch Performance Box (create_clutch_performance_box)': {
            'type': 'Two-row Table (Box)',
            'title': 'CLUTCH PERFORMANCE',
            'dimensions': '1.8" width',
            'rows': [
                {
                    'content': 'CLUTCH PERFORMANCE',
                    'style': {
                        'background': 'Team color',
                        'text_color': 'White',
                        'font': 'RussoOne-Regular, 9pt',
                        'padding': '6pt top/bottom, 8pt left/right',
                        'alignment': 'Center'
                    }
                },
                {
                    'content': 'League rank (e.g., "15th rank")',
                    'style': {
                        'background': 'White',
                        'text_color': 'Black',
                        'font': 'RussoOne-Regular, 13pt',
                        'padding': '8pt all sides',
                        'alignment': 'Center'
                    }
                }
            ],
            'border': {
                'color': 'Team color',
                'width': '1pt',
                'style': 'Solid'
            },
            'metrics': {
                'third_period_goals': 'Total goals scored in 3rd period',
                'one_goal_games': 'Games decided by 1 goal',
                'one_goal_wins': 'Wins in one-goal games',
                'one_goal_win_pct': '(one_goal_wins / one_goal_games) * 100',
                'clutch_score': '(third_period_goals * 2) + (one_goal_win_pct * 0.5)',
                'league_rank': 'Estimated rank (1-32) based on clutch_score'
            },
            'note': 'Rank is estimated - would need league-wide data for accurate ranking'
        }
    }
    
    # Print detailed structure
    for component_name, structure in structures.items():
        print(f"\n{'=' * 80}")
        print(f"COMPONENT: {component_name}")
        print('=' * 80)
        
        for key, value in structure.items():
            if isinstance(value, dict):
                print(f"\n{key.upper()}:")
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, (dict, list)):
                        print(f"  {sub_key}:")
                        for item in (sub_value if isinstance(sub_value, list) else [sub_value]):
                            if isinstance(item, dict):
                                for k, v in item.items():
                                    print(f"    {k}: {v}")
                            else:
                                print(f"    {item}")
                    else:
                        print(f"  {sub_key}: {sub_value}")
            elif isinstance(value, list):
                print(f"\n{key.upper()}:")
                for item in value:
                    print(f"  - {item}")
            else:
                print(f"{key}: {value}")
        
        print()
    
    # Print component order
    print("\n" + "=" * 80)
    print("COMPONENT RENDERING ORDER")
    print("=" * 80)
    print("""
1. Header Image (absolute top)
2. Team Summary Section (4pt spacer)
3. Home/Away Comparison Table
4. Period Performance Table
5. Performance Trend Graph (absolute positioned, left side)
6. Player Stats Section (with spacer offset)
7. Clutch Performance Box (with spacer offset)
8. Movement Patterns Table (absolute positioned, right side)
    """)
    
    # Print styling constants
    print("\n" + "=" * 80)
    print("STYLING CONSTANTS")
    print("=" * 80)
    print("""
Fonts:
  - Primary: RussoOne-Regular
  - Fallback: Helvetica-Bold (if RussoOne not available)

Team Colors: (RGB values defined per team)
  - NYR: Color(0/255, 56/255, 168/255) - Blue

Table Colors:
  - Header: Team color background, white text
  - Alternating rows: Beige / Lightgrey
  - Borders: Black, 0.5pt width

Page Settings:
  - Page size: Letter (8.5" x 11")
  - Margins: 72pt (1") left/right, 0pt top, 18pt bottom
  - Frame: 612pt width x 756pt height, starting at (0, 18)
  - Background: Paper.png (if exists)
    """)

if __name__ == '__main__':
    analyze_component_structure()

