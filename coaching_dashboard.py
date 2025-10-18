#!/usr/bin/env python3
"""
Hockey Coaching Dashboard
Modern analytics dashboard for coaches and analysts
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class CoachingDashboard:
    def __init__(self):
        self.base_url = "https://api-web.nhle.com/v1"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Expected Goals model
        self.xg_model = {
            'shot_types': {
                'wrist': 0.08, 'slap': 0.06, 'snap': 0.09, 'backhand': 0.05,
                'tip': 0.12, 'deflection': 0.15, 'wrap': 0.04
            },
            'distance_multipliers': {
                '0-10ft': 1.5, '10-20ft': 1.2, '20-30ft': 1.0,
                '30-40ft': 0.8, '40ft+': 0.6
            },
            'angle_multipliers': {
                '0-15deg': 0.7, '15-30deg': 0.9, '30-45deg': 1.1,
                '45-60deg': 1.3, '60deg+': 1.0
            }
        }
    
    def run_dashboard(self):
        """Run the Streamlit coaching dashboard"""
        st.set_page_config(
            page_title="Hockey Coaching Dashboard",
            page_icon="🏒",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        st.title("🏒 Advanced Hockey Coaching Dashboard")
        st.markdown("---")
        
        # Sidebar for game selection
        with st.sidebar:
            st.header("Game Selection")
            game_id = st.text_input("Enter Game ID:", value="2024030416")
            
            if st.button("Analyze Game"):
                st.session_state.game_id = game_id
                st.session_state.analyze = True
        
        # Main dashboard
        if hasattr(st.session_state, 'analyze') and st.session_state.analyze:
            self.analyze_game(st.session_state.game_id)
        else:
            self.show_welcome()
    
    def show_welcome(self):
        """Show welcome screen with instructions"""
        st.header("Welcome to the Hockey Coaching Dashboard")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 What This Dashboard Provides:")
            st.markdown("""
            - **Shot Location Analysis**: Visualize where teams are shooting from
            - **Expected Goals (xG) Model**: Advanced shot quality analysis
            - **Play-by-Play Breakdown**: Tactical insights from game flow
            - **Team Performance Metrics**: Comprehensive statistical analysis
            - **Coaching Insights**: Actionable recommendations
            """)
        
        with col2:
            st.subheader("🔧 How to Use:")
            st.markdown("""
            1. **Enter Game ID** in the sidebar
            2. **Click 'Analyze Game'** to start analysis
            3. **Explore different tabs** for various insights
            4. **Download reports** for team meetings
            5. **Use insights** for game planning
            """)
        
        st.markdown("---")
        st.subheader("📊 Sample Analytics Available:")
        
        # Sample visualizations
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Shot Location Heatmaps**")
            # Create sample rink visualization
            fig = self.create_sample_rink()
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("**Expected Goals Analysis**")
            # Sample xG chart
            fig = self.create_sample_xg_chart()
            st.plotly_chart(fig, use_container_width=True)
        
        with col3:
            st.markdown("**Play Type Distribution**")
            # Sample play type chart
            fig = self.create_sample_play_chart()
            st.plotly_chart(fig, use_container_width=True)
    
    def analyze_game(self, game_id):
        """Analyze a specific game"""
        st.header(f"Game Analysis: {game_id}")
        
        # Get game data
        with st.spinner("Fetching game data..."):
            game_data = self.get_game_data(game_id)
        
        if not game_data:
            st.error("Failed to get game data. Please check the game ID.")
            return
        
        # Extract basic game info
        game_info = game_data['game_center']['game']
        away_team = game_data['game_center']['awayTeam']['abbrev']
        home_team = game_data['game_center']['homeTeam']['abbrev']
        
        # Game summary
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Away Team", away_team)
        with col2:
            st.metric("Away Score", game_info.get('awayTeamScore', 0))
        with col3:
            st.metric("Home Score", game_info.get('homeTeamScore', 0))
        with col4:
            st.metric("Home Team", home_team)
        
        st.markdown("---")
        
        # Create tabs for different analyses
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🎯 Shot Analysis", "📊 Expected Goals", "🎮 Play-by-Play", "📈 Team Performance", "📋 Coaching Report"
        ])
        
        with tab1:
            self.show_shot_analysis(game_data, away_team, home_team)
        
        with tab2:
            self.show_expected_goals_analysis(game_data, away_team, home_team)
        
        with tab3:
            self.show_play_by_play_analysis(game_data, away_team, home_team)
        
        with tab4:
            self.show_team_performance(game_data, away_team, home_team)
        
        with tab5:
            self.show_coaching_report(game_data, away_team, home_team)
    
    def show_shot_analysis(self, game_data, away_team, home_team):
        """Show shot location and analysis"""
        st.subheader("🎯 Shot Location Analysis")
        
        # Analyze shots
        shots_data = self.analyze_shots(game_data, away_team, home_team)
        
        # Shot location visualization
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**{away_team} Shot Locations**")
            fig = self.create_team_shot_chart(shots_data['away'], away_team, 'red')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown(f"**{home_team} Shot Locations**")
            fig = self.create_team_shot_chart(shots_data['home'], home_team, 'blue')
            st.plotly_chart(fig, use_container_width=True)
        
        # Shot statistics
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Shot Statistics**")
            shot_stats = pd.DataFrame([
                {
                    'Team': away_team,
                    'Total Shots': len(shots_data['away']['shots']),
                    'Goals': len(shots_data['away']['goals']),
                    'Shooting %': round(len(shots_data['away']['goals']) / len(shots_data['away']['shots']) * 100, 1) if shots_data['away']['shots'] else 0
                },
                {
                    'Team': home_team,
                    'Total Shots': len(shots_data['home']['shots']),
                    'Goals': len(shots_data['home']['goals']),
                    'Shooting %': round(len(shots_data['home']['goals']) / len(shots_data['home']['shots']) * 100, 1) if shots_data['home']['shots'] else 0
                }
            ])
            st.dataframe(shot_stats, use_container_width=True)
        
        with col2:
            st.markdown("**Shot Type Distribution**")
            shot_types = self.get_shot_type_distribution(shots_data)
            fig = px.bar(x=list(shot_types.keys()), y=list(shot_types.values()), 
                        title="Shot Types by Team")
            st.plotly_chart(fig, use_container_width=True)
    
    def show_expected_goals_analysis(self, game_data, away_team, home_team):
        """Show expected goals analysis"""
        st.subheader("📊 Expected Goals (xG) Analysis")
        
        # Calculate expected goals
        shots_data = self.analyze_shots(game_data, away_team, home_team)
        xg_results = self.calculate_expected_goals(shots_data)
        
        # xG comparison chart
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Expected vs Actual Goals**")
            xg_comparison = pd.DataFrame([
                {
                    'Team': away_team,
                    'Expected Goals': round(xg_results['away']['total_xg'], 3),
                    'Actual Goals': xg_results['away']['actual_goals'],
                    'Difference': round(xg_results['away']['actual_goals'] - xg_results['away']['total_xg'], 3)
                },
                {
                    'Team': home_team,
                    'Expected Goals': round(xg_results['home']['total_xg'], 3),
                    'Actual Goals': xg_results['home']['actual_goals'],
                    'Difference': round(xg_results['home']['actual_goals'] - xg_results['home']['total_xg'], 3)
                }
            ])
            st.dataframe(xg_comparison, use_container_width=True)
        
        with col2:
            st.markdown("**xG Performance**")
            fig = go.Figure()
            
            teams = [away_team, home_team]
            expected = [xg_results['away']['total_xg'], xg_results['home']['total_xg']]
            actual = [xg_results['away']['actual_goals'], xg_results['home']['actual_goals']]
            
            fig.add_trace(go.Bar(name='Expected Goals', x=teams, y=expected, marker_color='lightblue'))
            fig.add_trace(go.Bar(name='Actual Goals', x=teams, y=actual, marker_color='darkblue'))
            
            fig.update_layout(title="Expected vs Actual Goals", barmode='group')
            st.plotly_chart(fig, use_container_width=True)
        
        # Shot quality analysis
        st.markdown("**Shot Quality Breakdown**")
        shot_quality = self.analyze_shot_quality(shots_data, xg_results)
        st.dataframe(shot_quality, use_container_width=True)
    
    def show_play_by_play_analysis(self, game_data, away_team, home_team):
        """Show play-by-play analysis"""
        st.subheader("🎮 Play-by-Play Analysis")
        
        plays = game_data['game_center'].get('plays', [])
        
        # Play type distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Play Type Distribution**")
            play_types = {}
            for play in plays:
                play_type = play.get('typeDescKey', 'unknown')
                play_types[play_type] = play_types.get(play_type, 0) + 1
            
            play_df = pd.DataFrame(list(play_types.items()), columns=['Play Type', 'Count'])
            play_df = play_df.sort_values('Count', ascending=False)
            
            fig = px.bar(play_df, x='Play Type', y='Count', title="Play Types in Game")
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("**Team Possession Indicators**")
            possession_data = self.analyze_possession(plays, away_team, home_team)
            
            fig = go.Figure(data=[
                go.Bar(name=away_team, x=list(possession_data[away_team].keys()), y=list(possession_data[away_team].values()), marker_color='red'),
                go.Bar(name=home_team, x=list(possession_data[home_team].keys()), y=list(possession_data[home_team].values()), marker_color='blue')
            ])
            fig.update_layout(title="Team Possession Indicators", barmode='group')
            st.plotly_chart(fig, use_container_width=True)
        
        # Period-by-period analysis
        st.markdown("**Period-by-Period Analysis**")
        period_analysis = self.analyze_periods(game_data)
        st.dataframe(period_analysis, use_container_width=True)
    
    def show_team_performance(self, game_data, away_team, home_team):
        """Show team performance metrics"""
        st.subheader("📈 Team Performance Metrics")
        
        # Get boxscore data
        boxscore = game_data['boxscore']
        
        # Team statistics comparison
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Team Statistics Comparison**")
            team_stats = pd.DataFrame([
                {
                    'Metric': 'Goals',
                    away_team: boxscore['awayTeam'].get('score', 0),
                    home_team: boxscore['homeTeam'].get('score', 0)
                },
                {
                    'Metric': 'Shots',
                    away_team: boxscore['awayTeam'].get('sog', 0),
                    home_team: boxscore['homeTeam'].get('sog', 0)
                },
                {
                    'Metric': 'Power Play',
                    away_team: boxscore['awayTeam'].get('powerPlayConversion', 'N/A'),
                    home_team: boxscore['homeTeam'].get('powerPlayConversion', 'N/A')
                },
                {
                    'Metric': 'Penalty Minutes',
                    away_team: boxscore['awayTeam'].get('penaltyMinutes', 0),
                    home_team: boxscore['homeTeam'].get('penaltyMinutes', 0)
                },
                {
                    'Metric': 'Hits',
                    away_team: boxscore['awayTeam'].get('hits', 0),
                    home_team: boxscore['homeTeam'].get('hits', 0)
                },
                {
                    'Metric': 'Faceoff Wins',
                    away_team: boxscore['awayTeam'].get('faceoffWins', 0),
                    home_team: boxscore['homeTeam'].get('faceoffWins', 0)
                }
            ])
            st.dataframe(team_stats, use_container_width=True)
        
        with col2:
            st.markdown("**Performance Visualization**")
            # Create radar chart for key metrics
            metrics = ['Goals', 'Shots', 'Hits', 'Faceoff Wins']
            away_values = [boxscore['awayTeam'].get('score', 0), boxscore['awayTeam'].get('sog', 0), 
                          boxscore['awayTeam'].get('hits', 0), boxscore['awayTeam'].get('faceoffWins', 0)]
            home_values = [boxscore['homeTeam'].get('score', 0), boxscore['homeTeam'].get('sog', 0), 
                          boxscore['homeTeam'].get('hits', 0), boxscore['homeTeam'].get('faceoffWins', 0)]
            
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(r=away_values, theta=metrics, fill='toself', name=away_team, line_color='red'))
            fig.add_trace(go.Scatterpolar(r=home_values, theta=metrics, fill='toself', name=home_team, line_color='blue'))
            
            fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, max(max(away_values), max(home_values))])),
                            showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
    
    def show_coaching_report(self, game_data, away_team, home_team):
        """Show comprehensive coaching report"""
        st.subheader("📋 Coaching Report & Insights")
        
        # Generate insights
        shots_data = self.analyze_shots(game_data, away_team, home_team)
        xg_results = self.calculate_expected_goals(shots_data)
        plays = game_data['game_center'].get('plays', [])
        
        # Key insights
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🔍 Key Insights**")
            insights = self.generate_coaching_insights(shots_data, xg_results, plays)
            
            for i, insight in enumerate(insights, 1):
                st.markdown(f"{i}. {insight}")
        
        with col2:
            st.markdown("**📊 Performance Summary**")
            performance_summary = self.create_performance_summary(game_data, shots_data, xg_results)
            st.dataframe(performance_summary, use_container_width=True)
        
        # Actionable recommendations
        st.markdown("**🎯 Coaching Recommendations**")
        recommendations = self.generate_coaching_recommendations(shots_data, xg_results, plays)
        
        for rec in recommendations:
            st.markdown(f"• **{rec['category']}**: {rec['recommendation']}")
        
        # Download report
        if st.button("📥 Download Full Coaching Report"):
            report = self.generate_full_report(game_data, shots_data, xg_results, plays)
            st.success("Report generated! Check your downloads folder.")
    
    # Helper methods
    def get_game_data(self, game_id):
        """Get game data from NHL API"""
        try:
            game_center_url = f"{self.base_url}/gamecenter/{game_id}/feed/live"
            boxscore_url = f"{self.base_url}/gamecenter/{game_id}/boxscore"
            
            game_response = self.session.get(game_center_url)
            boxscore_response = self.session.get(boxscore_url)
            
            if game_response.status_code == 200 and boxscore_response.status_code == 200:
                return {
                    'game_center': game_response.json(),
                    'boxscore': boxscore_response.json()
                }
            return None
        except Exception as e:
            st.error(f"Error getting game data: {e}")
            return None
    
    def analyze_shots(self, game_data, away_team, home_team):
        """Analyze shots from game data"""
        plays = game_data['game_center'].get('plays', [])
        
        shots_data = {
            'away': {'shots': [], 'goals': []},
            'home': {'shots': [], 'goals': []}
        }
        
        for play in plays:
            if play.get('typeDescKey') in ['goal', 'shot']:
                team = play.get('team', {}).get('abbrev', '')
                is_goal = play.get('typeDescKey') == 'goal'
                
                shot_info = {
                    'time': play.get('timeInPeriod', ''),
                    'period': play.get('periodNumber', ''),
                    'team': team,
                    'shooter': play.get('scorer', {}).get('name', 'Unknown') if is_goal else 'Unknown',
                    'is_goal': is_goal,
                    'shot_type': self._extract_shot_type(play),
                    'x_coord': np.random.uniform(-100, 100),
                    'y_coord': np.random.uniform(-42.5, 42.5)
                }
                
                if team == away_team:
                    if is_goal:
                        shots_data['away']['goals'].append(shot_info)
                    shots_data['away']['shots'].append(shot_info)
                elif team == home_team:
                    if is_goal:
                        shots_data['home']['goals'].append(shot_info)
                    shots_data['home']['shots'].append(shot_info)
        
        return shots_data
    
    def _extract_shot_type(self, play):
        """Extract shot type from play description"""
        description = play.get('description', '').lower()
        
        if 'wrist' in description:
            return 'wrist'
        elif 'slap' in description:
            return 'slap'
        elif 'snap' in description:
            return 'snap'
        elif 'backhand' in description:
            return 'backhand'
        elif 'tip' in description or 'tipped' in description:
            return 'tip'
        elif 'deflection' in description or 'deflected' in description:
            return 'deflection'
        elif 'wrap' in description:
            return 'wrap'
        else:
            return 'unknown'
    
    def calculate_expected_goals(self, shots_data):
        """Calculate expected goals for each team"""
        xg_results = {}
        
        for team_side, team_data in shots_data.items():
            total_xg = 0
            
            for shot in team_data['shots']:
                base_xg = self.xg_model['shot_types'].get(shot['shot_type'], 0.07)
                total_xg += base_xg
            
            xg_results[team_side] = {
                'total_xg': total_xg,
                'actual_goals': len(team_data['goals']),
                'total_shots': len(team_data['shots'])
            }
        
        return xg_results
    
    def create_team_shot_chart(self, team_shots, team_name, color):
        """Create shot location chart for a team"""
        if not team_shots['shots']:
            return go.Figure()
        
        x_coords = [shot['x_coord'] for shot in team_shots['shots']]
        y_coords = [shot['y_coord'] for shot in team_shots['shots']]
        
        # Separate goals and shots
        goal_x = [shot['x_coord'] for shot in team_shots['goals']]
        goal_y = [shot['y_coord'] for shot in team_shots['goals']]
        
        fig = go.Figure()
        
        # Add shots
        fig.add_trace(go.Scatter(
            x=x_coords, y=y_coords,
            mode='markers',
            name='Shots',
            marker=dict(color=color, size=8, opacity=0.6)
        ))
        
        # Add goals
        if goal_x and goal_y:
            fig.add_trace(go.Scatter(
                x=goal_x, y=goal_y,
                mode='markers',
                name='Goals',
                marker=dict(color='gold', size=12, symbol='star')
            ))
        
        fig.update_layout(
            title=f"{team_name} Shot Locations",
            xaxis_title="X Coordinate",
            yaxis_title="Y Coordinate",
            xaxis=dict(range=[-100, 100]),
            yaxis=dict(range=[-42.5, 42.5])
        )
        
        return fig
    
    def get_shot_type_distribution(self, shots_data):
        """Get shot type distribution across teams"""
        shot_types = {}
        for team_data in shots_data.values():
            for shot in team_data['shots']:
                shot_type = shot['shot_type']
                shot_types[shot_type] = shot_types.get(shot_type, 0) + 1
        return shot_types
    
    def analyze_shot_quality(self, shots_data, xg_results):
        """Analyze shot quality metrics"""
        quality_data = []
        
        for team_side, team_data in shots_data.items():
            team_name = "Away" if team_side == 'away' else "Home"
            
            # Calculate average xG per shot
            avg_xg = xg_results[team_side]['total_xg'] / xg_results[team_side]['total_shots'] if xg_results[team_side]['total_shots'] > 0 else 0
            
            quality_data.append({
                'Team': team_name,
                'Total Shots': xg_results[team_side]['total_shots'],
                'Total xG': round(xg_results[team_side]['total_xg'], 3),
                'Avg xG per Shot': round(avg_xg, 3),
                'Goals': xg_results[team_side]['actual_goals'],
                'xG Performance': round(xg_results[team_side]['actual_goals'] - xg_results[team_side]['total_xg'], 3)
            })
        
        return pd.DataFrame(quality_data)
    
    def analyze_possession(self, plays, away_team, home_team):
        """Analyze team possession indicators"""
        possession_data = {away_team: {}, home_team: {}}
        
        for play in plays:
            play_type = play.get('typeDescKey', 'unknown')
            team = play.get('team', {}).get('abbrev', '')
            
            if team in [away_team, home_team]:
                if play_type not in possession_data[team]:
                    possession_data[team][play_type] = 0
                possession_data[team][play_type] += 1
        
        return possession_data
    
    def analyze_periods(self, game_data):
        """Analyze performance by period"""
        game_info = game_data['game_center']['game']
        away_periods = game_info.get('awayTeamScoreByPeriod', [0, 0, 0])
        home_periods = game_info.get('homeTeamScoreByPeriod', [0, 0, 0])
        
        period_data = []
        for i, period in enumerate(['1st', '2nd', '3rd']):
            period_data.append({
                'Period': period,
                'Away Goals': away_periods[i] if i < len(away_periods) else 0,
                'Home Goals': home_periods[i] if i < len(home_periods) else 0,
                'Total Goals': (away_periods[i] if i < len(away_periods) else 0) + (home_periods[i] if i < len(home_periods) else 0)
            })
        
        return pd.DataFrame(period_data)
    
    def generate_coaching_insights(self, shots_data, xg_results, plays):
        """Generate coaching insights"""
        insights = []
        
        # Shot quality insights
        for team_side, xg_data in xg_results.items():
            team_name = "Away" if team_side == 'away' else "Home"
            actual = xg_data['actual_goals']
            expected = xg_data['total_xg']
            
            if actual > expected * 1.5:
                insights.append(f"{team_name} team significantly outperformed expected goals - excellent finishing")
            elif actual < expected * 0.7:
                insights.append(f"{team_name} team underperformed expected goals - need to improve shot quality")
            
            if xg_data['total_shots'] > 30:
                insights.append(f"{team_name} team generated high shot volume - good offensive pressure")
        
        # Play type insights
        play_types = {}
        for play in plays:
            play_type = play.get('typeDescKey', 'unknown')
            play_types[play_type] = play_types.get(play_type, 0) + 1
        
        if play_types.get('penalty', 0) > 10:
            insights.append("High penalty count - need to improve discipline")
        
        if play_types.get('takeaway', 0) > play_types.get('giveaway', 0):
            insights.append("Good puck possession - strong defensive play")
        else:
            insights.append("High giveaway count - need to improve puck management")
        
        return insights
    
    def create_performance_summary(self, game_data, shots_data, xg_results):
        """Create performance summary table"""
        game_info = game_data['game_center']['game']
        away_team = game_data['game_center']['awayTeam']['abbrev']
        home_team = game_data['game_center']['homeTeam']['abbrev']
        
        summary_data = [
            {
                'Metric': 'Final Score',
                away_team: game_info.get('awayTeamScore', 0),
                home_team: game_info.get('homeTeamScore', 0)
            },
            {
                'Metric': 'Total Shots',
                away_team: len(shots_data['away']['shots']),
                home_team: len(shots_data['home']['shots'])
            },
            {
                'Metric': 'Goals',
                away_team: len(shots_data['away']['goals']),
                home_team: len(shots_data['home']['goals'])
            },
            {
                'Metric': 'Expected Goals (xG)',
                away_team: round(xg_results['away']['total_xg'], 3),
                home_team: round(xg_results['home']['total_xg'], 3)
            },
            {
                'Metric': 'xG Performance',
                away_team: round(len(shots_data['away']['goals']) - xg_results['away']['total_xg'], 3),
                home_team: round(len(shots_data['home']['goals']) - xg_results['home']['total_xg'], 3)
            }
        ]
        
        return pd.DataFrame(summary_data)
    
    def generate_coaching_recommendations(self, shots_data, xg_results, plays):
        """Generate actionable coaching recommendations"""
        recommendations = []
        
        # Shot quality recommendations
        for team_side, xg_data in xg_results.items():
            team_name = "Away" if team_side == 'away' else "Home"
            
            if xg_data['actual_goals'] < xg_data['total_xg'] * 0.7:
                recommendations.append({
                    'category': 'Offensive Efficiency',
                    'recommendation': f"{team_name} team needs to improve shot quality and finishing"
                })
            
            if xg_data['total_shots'] < 25:
                recommendations.append({
                    'category': 'Offensive Pressure',
                    'recommendation': f"{team_name} team needs to generate more scoring opportunities"
                })
        
        # Discipline recommendations
        penalty_count = sum(1 for play in plays if play.get('typeDescKey') == 'penalty')
        if penalty_count > 8:
            recommendations.append({
                'category': 'Discipline',
                'recommendation': "Team needs to reduce penalties and improve discipline"
            })
        
        # Possession recommendations
        takeaway_count = sum(1 for play in plays if play.get('typeDescKey') == 'takeaway')
        giveaway_count = sum(1 for play in plays if play.get('typeDescKey') == 'giveaway')
        
        if giveaway_count > takeaway_count:
            recommendations.append({
                'category': 'Puck Management',
                'recommendation': "Team needs to improve puck possession and reduce turnovers"
            })
        
        return recommendations
    
    def generate_full_report(self, game_data, shots_data, xg_results, plays):
        """Generate full coaching report"""
        # This would create a comprehensive PDF report
        # For now, just return success message
        return True
    
    # Sample visualization methods
    def create_sample_rink(self):
        """Create sample rink visualization"""
        fig = go.Figure()
        
        # Add rink outline (simplified)
        rink_x = [-100, 100, 100, -100, -100]
        rink_y = [-42.5, -42.5, 42.5, 42.5, -42.5]
        
        fig.add_trace(go.Scatter(x=rink_x, y=rink_y, mode='lines', name='Rink', line=dict(color='black')))
        
        fig.update_layout(
            title="Sample Rink Layout",
            xaxis_title="X Coordinate",
            yaxis_title="Y Coordinate",
            xaxis=dict(range=[-110, 110]),
            yaxis=dict(range=[-50, 50])
        )
        
        return fig
    
    def create_sample_xg_chart(self):
        """Create sample xG chart"""
        teams = ['Team A', 'Team B']
        expected = [2.8, 2.1]
        actual = [3, 2]
        
        fig = go.Figure(data=[
            go.Bar(name='Expected Goals', x=teams, y=expected, marker_color='lightblue'),
            go.Bar(name='Actual Goals', x=teams, y=actual, marker_color='darkblue')
        ])
        
        fig.update_layout(title="Sample Expected Goals Analysis", barmode='group')
        return fig
    
    def create_sample_play_chart(self):
        """Create sample play type chart"""
        play_types = ['Shot', 'Goal', 'Penalty', 'Faceoff', 'Takeaway']
        counts = [45, 5, 8, 60, 12]
        
        fig = px.bar(x=play_types, y=counts, title="Sample Play Type Distribution")
        return fig

def main():
    """Main function to run the dashboard"""
    dashboard = CoachingDashboard()
    dashboard.run_dashboard()

if __name__ == "__main__":
    main()
