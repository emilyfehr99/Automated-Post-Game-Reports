#!/usr/bin/env python3
"""
F1 Technical Analysis Dashboard - Professional F1 Analytics
Think Sky Sports F1 technical analysis meets data science
"""

import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.offline as pyo
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

class F1TechnicalAnalysis:
    def __init__(self, driver_number=16, driver_name="Charles LECLERC"):
        self.base_url = "https://api.openf1.org/v1"
        self.session = requests.Session()
        self.driver_number = driver_number
        self.driver_name = driver_name
        self.team = "Ferrari"
        
        # Professional color scheme
        self.colors = {
            'primary': '#DC143C',  # Ferrari Red
            'secondary': '#FFD700',  # Gold
            'accent': '#000000',  # Black
            'background': '#F5F5F5',
            'text': '#333333'
        }
        
        # Data storage
        self.race_data = {}
        self.lap_data = {}
        self.position_data = {}
        self.weather_data = {}
        self.pit_data = {}
        
    def get_data(self, endpoint, params=None):
        """Generic method to fetch data from any endpoint"""
        url = f"{self.base_url}/{endpoint}"
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from {endpoint}: {e}")
            return None
    
    def collect_driver_data(self):
        """Collect comprehensive data for the driver"""
        print(f"🏎️ Collecting {self.driver_name} technical data...")
        
        # Get all 2024 race sessions
        sessions = self.get_data("sessions", {"year": 2024})
        if not sessions:
            return False
        
        race_sessions = [s for s in sessions if s.get('session_name') == 'Race']
        print(f"📊 Analyzing {len(race_sessions)} race sessions")
        
        for session in race_sessions:
            session_key = session.get('session_key')
            meeting_key = session.get('meeting_key')
            
            # Get meeting info
            meetings = self.get_data("meetings", {"meeting_key": meeting_key})
            meeting_name = meetings[0].get('meeting_name', 'Unknown') if meetings else 'Unknown'
            
            # Collect data with rate limiting
            self._collect_session_data(session_key, meeting_name)
            import time
            time.sleep(0.3)  # Rate limiting
        
        return True
    
    def _collect_session_data(self, session_key, meeting_name):
        """Collect all data for a specific session"""
        # Lap data
        laps = self.get_data("laps", {"session_key": session_key, "driver_number": self.driver_number})
        if laps:
            df = pd.DataFrame(laps)
            df['meeting_name'] = meeting_name
            self.lap_data[session_key] = df
        
        # Position data
        positions = self.get_data("position", {"session_key": session_key, "driver_number": self.driver_number})
        if positions:
            df = pd.DataFrame(positions)
            df['meeting_name'] = meeting_name
            self.position_data[session_key] = df
        
        # Weather data
        weather = self.get_data("weather", {"session_key": session_key})
        if weather:
            df = pd.DataFrame(weather)
            df['meeting_name'] = meeting_name
            self.weather_data[session_key] = df
        
        # Pit data
        pits = self.get_data("pit", {"session_key": session_key, "driver_number": self.driver_number})
        if pits:
            df = pd.DataFrame(pits)
            df['meeting_name'] = meeting_name
            self.pit_data[session_key] = df
    
    def generate_technical_insights(self):
        """Generate professional technical insights"""
        print(f"\n🔬 TECHNICAL ANALYSIS: {self.driver_name}")
        print("=" * 60)
        
        insights = {
            'performance_summary': self._analyze_performance_summary(),
            'consistency_analysis': self._analyze_consistency(),
            'track_characteristics': self._analyze_track_characteristics(),
            'weather_sensitivity': self._analyze_weather_sensitivity(),
            'strategy_effectiveness': self._analyze_strategy_effectiveness(),
            'pressure_performance': self._analyze_pressure_performance(),
            'improvement_areas': self._identify_improvement_areas(),
            'strengths': self._identify_strengths()
        }
        
        return insights
    
    def _analyze_performance_summary(self):
        """Analyze overall performance metrics"""
        if not self.position_data:
            return {}
        
        # Calculate key metrics
        all_positions = []
        for session_key, df in self.position_data.items():
            if not df.empty:
                final_pos = df.iloc[-1]
                all_positions.append({
                    'meeting_name': final_pos['meeting_name'],
                    'position': final_pos['position'],
                    'date': pd.to_datetime(final_pos['date'])
                })
        
        if not all_positions:
            return {}
        
        results_df = pd.DataFrame(all_positions)
        results_df = results_df.sort_values('date')
        
        # Calculate metrics
        avg_position = results_df['position'].mean()
        podium_rate = len(results_df[results_df['position'] <= 3]) / len(results_df) * 100
        points_rate = len(results_df[results_df['position'] <= 10]) / len(results_df) * 100
        
        # Championship points
        points_system = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}
        results_df['points'] = results_df['position'].map(points_system).fillna(0)
        total_points = results_df['points'].sum()
        
        return {
            'avg_position': avg_position,
            'podium_rate': podium_rate,
            'points_rate': points_rate,
            'total_points': total_points,
            'total_races': len(results_df),
            'wins': len(results_df[results_df['position'] == 1]),
            'podiums': len(results_df[results_df['position'] <= 3])
        }
    
    def _analyze_consistency(self):
        """Analyze driving consistency"""
        if not self.lap_data:
            return {}
        
        consistency_data = []
        for session_key, df in self.lap_data.items():
            valid_laps = df[df['lap_duration'].notna()]
            if len(valid_laps) > 10:  # Need sufficient data
                consistency = valid_laps['lap_duration'].std()
                avg_lap = valid_laps['lap_duration'].mean()
                cv = (consistency / avg_lap) * 100  # Coefficient of variation
                
                consistency_data.append({
                    'track': df.iloc[0]['meeting_name'],
                    'consistency': consistency,
                    'cv': cv,
                    'avg_lap': avg_lap
                })
        
        if not consistency_data:
            return {}
        
        cons_df = pd.DataFrame(consistency_data)
        avg_consistency = cons_df['consistency'].mean()
        avg_cv = cons_df['cv'].mean()
        
        # Identify most/least consistent tracks
        most_consistent = cons_df.loc[cons_df['consistency'].idxmin()]
        least_consistent = cons_df.loc[cons_df['consistency'].idxmax()]
        
        return {
            'avg_consistency': avg_consistency,
            'avg_cv': avg_cv,
            'most_consistent_track': most_consistent['track'],
            'least_consistent_track': least_consistent['track'],
            'consistency_rank': self._rank_consistency(cons_df)
        }
    
    def _analyze_track_characteristics(self):
        """Analyze performance by track characteristics"""
        if not self.lap_data:
            return {}
        
        track_analysis = []
        for session_key, df in self.lap_data.items():
            valid_laps = df[df['lap_duration'].notna()]
            if not valid_laps.empty:
                # Get position data for this race
                if session_key in self.position_data:
                    pos_df = self.position_data[session_key]
                    if not pos_df.empty:
                        final_position = pos_df.iloc[-1]['position']
                        
                        track_analysis.append({
                            'track': df.iloc[0]['meeting_name'],
                            'avg_lap_time': valid_laps['lap_duration'].mean(),
                            'fastest_lap': valid_laps['lap_duration'].min(),
                            'final_position': final_position,
                            'track_type': self._classify_track(df.iloc[0]['meeting_name'])
                        })
        
        if not track_analysis:
            return {}
        
        track_df = pd.DataFrame(track_analysis)
        
        # Analyze by track type
        track_type_performance = track_df.groupby('track_type').agg({
            'final_position': 'mean',
            'avg_lap_time': 'mean'
        }).round(2)
        
        return {
            'track_type_performance': track_type_performance.to_dict(),
            'best_track_type': track_type_performance['final_position'].idxmin(),
            'worst_track_type': track_type_performance['final_position'].idxmax(),
            'track_analysis': track_df
        }
    
    def _analyze_weather_sensitivity(self):
        """Analyze performance sensitivity to weather conditions"""
        if not self.weather_data or not self.lap_data:
            return {}
        
        weather_performance = []
        for session_key in self.weather_data.keys():
            if session_key in self.lap_data:
                weather_df = self.weather_data[session_key]
                lap_df = self.lap_data[session_key]
                
                if not weather_df.empty and not lap_df.empty:
                    # Get weather conditions
                    avg_temp = weather_df['air_temperature'].mean()
                    avg_humidity = weather_df['humidity'].mean()
                    avg_wind = weather_df['wind_speed'].mean()
                    rainfall = weather_df['rainfall'].sum() > 0
                    
                    # Get performance
                    valid_laps = lap_df[lap_df['lap_duration'].notna()]
                    if not valid_laps.empty:
                        avg_lap_time = valid_laps['lap_duration'].mean()
                        
                        # Get final position
                        final_position = None
                        if session_key in self.position_data:
                            pos_df = self.position_data[session_key]
                            if not pos_df.empty:
                                final_position = pos_df.iloc[-1]['position']
                        
                        weather_performance.append({
                            'track': weather_df.iloc[0]['meeting_name'],
                            'temp': avg_temp,
                            'humidity': avg_humidity,
                            'wind': avg_wind,
                            'rainfall': rainfall,
                            'avg_lap_time': avg_lap_time,
                            'final_position': final_position
                        })
        
        if not weather_performance:
            return {}
        
        weather_df = pd.DataFrame(weather_performance)
        
        # Analyze temperature sensitivity
        temp_correlation = weather_df['temp'].corr(weather_df['final_position'])
        humidity_correlation = weather_df['humidity'].corr(weather_df['final_position'])
        
        # Wet vs dry performance
        wet_races = weather_df[weather_df['rainfall'] == True]
        dry_races = weather_df[weather_df['rainfall'] == False]
        
        wet_avg_pos = wet_races['final_position'].mean() if not wet_races.empty else None
        dry_avg_pos = dry_races['final_position'].mean() if not dry_races.empty else None
        
        return {
            'temp_sensitivity': temp_correlation,
            'humidity_sensitivity': humidity_correlation,
            'wet_performance': wet_avg_pos,
            'dry_performance': dry_avg_pos,
            'weather_advantage': 'Wet' if wet_avg_pos and dry_avg_pos and wet_avg_pos < dry_avg_pos else 'Dry'
        }
    
    def _analyze_strategy_effectiveness(self):
        """Analyze pit stop and strategy effectiveness"""
        if not self.pit_data or not self.position_data:
            return {}
        
        strategy_analysis = []
        for session_key in self.pit_data.keys():
            if session_key in self.position_data:
                pit_df = self.pit_data[session_key]
                pos_df = self.position_data[session_key]
                
                if not pit_df.empty and not pos_df.empty:
                    # Analyze pit stops
                    num_pits = len(pit_df)
                    avg_pit_time = pit_df['pit_duration'].mean() if 'pit_duration' in pit_df.columns else None
                    
                    # Analyze position changes
                    start_pos = pos_df.iloc[0]['position']
                    end_pos = pos_df.iloc[-1]['position']
                    position_change = start_pos - end_pos  # Positive = gained positions
                    
                    strategy_analysis.append({
                        'track': pit_df.iloc[0]['meeting_name'],
                        'num_pits': num_pits,
                        'avg_pit_time': avg_pit_time,
                        'position_change': position_change,
                        'start_pos': start_pos,
                        'end_pos': end_pos
                    })
        
        if not strategy_analysis:
            return {}
        
        strategy_df = pd.DataFrame(strategy_analysis)
        
        # Calculate strategy effectiveness
        avg_position_gain = strategy_df['position_change'].mean()
        avg_pits_per_race = strategy_df['num_pits'].mean()
        
        # Best strategy races
        best_strategy = strategy_df.loc[strategy_df['position_change'].idxmax()]
        worst_strategy = strategy_df.loc[strategy_df['position_change'].idxmin()]
        
        return {
            'avg_position_gain': avg_position_gain,
            'avg_pits_per_race': avg_pits_per_race,
            'best_strategy_race': best_strategy['track'],
            'worst_strategy_race': worst_strategy['track'],
            'strategy_effectiveness': 'Positive' if avg_position_gain > 0 else 'Negative'
        }
    
    def _analyze_pressure_performance(self):
        """Analyze performance under pressure"""
        if not self.position_data:
            return {}
        
        # Define pressure situations
        pressure_races = []
        for session_key, df in self.position_data.items():
            if not df.empty:
                final_pos = df.iloc[-1]
                meeting_name = final_pos['meeting_name']
                
                # Define pressure situations
                is_home_race = 'Monaco' in meeting_name  # Leclerc's home race
                is_championship_race = final_pos['position'] <= 3  # Podium pressure
                is_recovery_race = len(df) > 1 and df.iloc[0]['position'] > df.iloc[-1]['position']  # Gained positions
                
                pressure_races.append({
                    'track': meeting_name,
                    'final_position': final_pos['position'],
                    'is_home_race': is_home_race,
                    'is_championship_race': is_championship_race,
                    'is_recovery_race': is_recovery_race
                })
        
        if not pressure_races:
            return {}
        
        pressure_df = pd.DataFrame(pressure_races)
        
        # Analyze pressure performance
        home_race_performance = pressure_df[pressure_df['is_home_race']]['final_position'].mean()
        championship_performance = pressure_df[pressure_df['is_championship_race']]['final_position'].mean()
        recovery_performance = pressure_df[pressure_df['is_recovery_race']]['final_position'].mean()
        
        return {
            'home_race_avg': home_race_performance,
            'championship_avg': championship_performance,
            'recovery_avg': recovery_performance,
            'pressure_handling': 'Strong' if home_race_performance < 5 else 'Needs Improvement'
        }
    
    def _identify_improvement_areas(self):
        """Identify areas for improvement"""
        insights = []
        
        # Analyze consistency
        if self.lap_data:
            all_consistency = []
            for session_key, df in self.lap_data.items():
                valid_laps = df[df['lap_duration'].notna()]
                if len(valid_laps) > 10:
                    consistency = valid_laps['lap_duration'].std()
                    all_consistency.append(consistency)
            
            if all_consistency:
                avg_consistency = np.mean(all_consistency)
                if avg_consistency > 5.0:  # High lap time variation
                    insights.append("Lap time consistency needs improvement")
        
        # Analyze qualifying vs race performance
        if self.position_data:
            positions = [df.iloc[-1]['position'] for df in self.position_data.values() if not df.empty]
            avg_position = np.mean(positions)
            if avg_position > 6:
                insights.append("Race pace could be improved")
        
        # Analyze weather sensitivity
        weather_insights = self._analyze_weather_sensitivity()
        if weather_insights and weather_insights.get('temp_sensitivity', 0) > 0.3:
            insights.append("Performance sensitive to temperature changes")
        
        return insights
    
    def _identify_strengths(self):
        """Identify driver strengths"""
        strengths = []
        
        # Analyze podium rate
        if self.position_data:
            positions = [df.iloc[-1]['position'] for df in self.position_data.values() if not df.empty]
            podium_rate = len([p for p in positions if p <= 3]) / len(positions) * 100
            if podium_rate > 40:
                strengths.append(f"High podium rate ({podium_rate:.1f}%)")
        
        # Analyze recovery ability
        recovery_races = 0
        for session_key, df in self.position_data.items():
            if len(df) > 1:
                start_pos = df.iloc[0]['position']
                end_pos = df.iloc[-1]['position']
                if end_pos < start_pos:  # Gained positions
                    recovery_races += 1
        
        if recovery_races > len(self.position_data) * 0.3:
            strengths.append("Strong recovery and overtaking ability")
        
        # Analyze track versatility
        track_insights = self._analyze_track_characteristics()
        if track_insights and track_insights.get('track_type_performance'):
            track_performance = track_insights['track_type_performance']['final_position']
            if len(track_performance) > 2:  # Performs well on multiple track types
                strengths.append("Versatile across different track types")
        
        return strengths
    
    def _classify_track(self, track_name):
        """Classify track by characteristics"""
        track_classifications = {
            'High Speed': ['Monza', 'Silverstone', 'Spa', 'Baku'],
            'Technical': ['Monaco', 'Singapore', 'Hungary'],
            'Power': ['Monza', 'Spa', 'Silverstone'],
            'Downforce': ['Monaco', 'Singapore', 'Hungary']
        }
        
        for category, tracks in track_classifications.items():
            if any(track in track_name for track in tracks):
                return category
        return 'Mixed'
    
    def _rank_consistency(self, cons_df):
        """Rank consistency performance"""
        cons_df['consistency_rank'] = cons_df['consistency'].rank(ascending=True)
        return cons_df[['track', 'consistency_rank']].to_dict('records')
    
    def create_professional_dashboard(self):
        """Create a professional F1 technical analysis dashboard"""
        print("\n📊 Creating Professional F1 Technical Dashboard...")
        
        # Generate insights
        insights = self.generate_technical_insights()
        
        # Create the dashboard
        fig = make_subplots(
            rows=4, cols=3,
            subplot_titles=[
                'Performance Summary', 'Consistency Analysis', 'Track Characteristics',
                'Weather Sensitivity', 'Strategy Effectiveness', 'Pressure Performance',
                'Lap Time Distribution', 'Position Trends', 'Pit Stop Analysis',
                'Key Insights', 'Strengths & Weaknesses', 'Technical Recommendations'
            ],
            specs=[
                [{"type": "indicator"}, {"type": "bar"}, {"type": "bar"}],
                [{"type": "scatter"}, {"type": "bar"}, {"type": "indicator"}],
                [{"type": "histogram"}, {"type": "scatter"}, {"type": "bar"}],
                [{"type": "table"}, {"type": "table"}, {"type": "table"}]
            ],
            vertical_spacing=0.08,
            horizontal_spacing=0.08
        )
        
        # 1. Performance Summary (Indicator)
        if insights.get('performance_summary'):
            perf = insights['performance_summary']
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number+delta",
                    value=perf['avg_position'],
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Average Position"},
                    gauge={'axis': {'range': [None, 20]},
                           'bar': {'color': self.colors['primary']},
                           'steps': [{'range': [0, 5], 'color': "lightgray"},
                                    {'range': [5, 10], 'color': "gray"}],
                           'threshold': {'line': {'color': "red", 'width': 4},
                                       'thickness': 0.75, 'value': 5}}
                ),
                row=1, col=1
            )
        
        # 2. Consistency Analysis
        if insights.get('consistency_analysis'):
            cons = insights['consistency_analysis']
            if 'consistency_rank' in cons:
                tracks = [item['track'] for item in cons['consistency_rank']]
                ranks = [item['consistency_rank'] for item in cons['consistency_rank']]
                
                fig.add_trace(
                    go.Bar(x=tracks, y=ranks, name="Consistency Rank",
                          marker_color=self.colors['primary']),
                    row=1, col=2
                )
        
        # 3. Track Characteristics
        if insights.get('track_characteristics'):
            track_perf = insights['track_characteristics']['track_type_performance']
            if 'final_position' in track_perf:
                track_types = list(track_perf['final_position'].keys())
                avg_positions = list(track_perf['final_position'].values())
                
                fig.add_trace(
                    go.Bar(x=track_types, y=avg_positions, name="Avg Position by Track Type",
                          marker_color=self.colors['secondary']),
                    row=1, col=3
                )
        
        # 4. Weather Sensitivity
        if insights.get('weather_sensitivity'):
            weather = insights['weather_sensitivity']
            # Create a scatter plot showing temperature vs performance
            fig.add_trace(
                go.Scatter(x=[1, 2, 3], y=[weather.get('temp_sensitivity', 0), 
                                          weather.get('humidity_sensitivity', 0), 0],
                          mode='markers+text',
                          text=['Temp', 'Humidity', 'Wind'],
                          name="Weather Sensitivity",
                          marker=dict(size=15, color=self.colors['primary'])),
                row=2, col=1
            )
        
        # 5. Strategy Effectiveness
        if insights.get('strategy_effectiveness'):
            strategy = insights['strategy_effectiveness']
            fig.add_trace(
                go.Bar(x=['Position Gain', 'Pits/Race'], 
                      y=[strategy.get('avg_position_gain', 0), 
                         strategy.get('avg_pits_per_race', 0)],
                      name="Strategy Metrics",
                      marker_color=self.colors['accent']),
                row=2, col=2
            )
        
        # 6. Pressure Performance
        if insights.get('pressure_performance'):
            pressure = insights['pressure_performance']
            fig.add_trace(
                go.Indicator(
                    mode="number+gauge",
                    value=pressure.get('home_race_avg', 0),
                    title={'text': "Home Race Performance"},
                    gauge={'axis': {'range': [0, 20]},
                           'bar': {'color': self.colors['primary']}}
                ),
                row=2, col=3
            )
        
        # 7. Lap Time Distribution
        if self.lap_data:
            all_laps = []
            for session_key, df in self.lap_data.items():
                valid_laps = df[df['lap_duration'].notna()]
                if not valid_laps.empty:
                    all_laps.extend(valid_laps['lap_duration'].tolist())
            
            if all_laps:
                fig.add_trace(
                    go.Histogram(x=all_laps, name="Lap Time Distribution",
                               marker_color=self.colors['primary']),
                    row=3, col=1
                )
        
        # 8. Position Trends
        if self.position_data:
            positions = []
            races = []
            for session_key, df in self.position_data.items():
                if not df.empty:
                    final_pos = df.iloc[-1]
                    positions.append(final_pos['position'])
                    races.append(final_pos['meeting_name'])
            
            if positions:
                fig.add_trace(
                    go.Scatter(x=list(range(len(positions))), y=positions,
                              mode='lines+markers', name="Position Trend",
                              line=dict(color=self.colors['primary'], width=3)),
                    row=3, col=2
                )
        
        # 9. Pit Stop Analysis
        if self.pit_data:
            pit_counts = []
            tracks = []
            for session_key, df in self.pit_data.items():
                if not df.empty:
                    pit_counts.append(len(df))
                    tracks.append(df.iloc[0]['meeting_name'])
            
            if pit_counts:
                fig.add_trace(
                    go.Bar(x=tracks, y=pit_counts, name="Pit Stops per Race",
                          marker_color=self.colors['secondary']),
                    row=3, col=3
                )
        
        # 10-12. Text-based insights
        insights_text = self._format_insights_text(insights)
        
        for i, (title, content) in enumerate(insights_text.items()):
            fig.add_trace(
                go.Scatter(x=[0], y=[0], mode='text',
                          text=[content], textfont=dict(size=10),
                          showlegend=False),
                row=4, col=i+1
            )
        
        # Update layout
        fig.update_layout(
            title=f"F1 Technical Analysis: {self.driver_name} - 2024 Season",
            title_x=0.5,
            title_font_size=20,
            height=1200,
            showlegend=False,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        # Save the dashboard
        fig.write_html("f1_technical_dashboard.html")
        print("✅ Professional F1 Technical Dashboard saved as 'f1_technical_dashboard.html'")
        
        return fig
    
    def _format_insights_text(self, insights):
        """Format insights into readable text"""
        text_insights = {}
        
        # Key Insights
        key_insights = []
        if insights.get('performance_summary'):
            perf = insights['performance_summary']
            key_insights.append(f"• {perf['podium_rate']:.1f}% podium rate")
            key_insights.append(f"• {perf['total_points']} championship points")
            key_insights.append(f"• {perf['wins']} race wins")
        
        text_insights['Key Insights'] = '<br>'.join(key_insights)
        
        # Strengths & Weaknesses
        strengths_weaknesses = []
        if insights.get('strengths'):
            strengths_weaknesses.extend([f"✅ {s}" for s in insights['strengths']])
        if insights.get('improvement_areas'):
            strengths_weaknesses.extend([f"⚠️ {s}" for s in insights['improvement_areas']])
        
        text_insights['Strengths & Weaknesses'] = '<br>'.join(strengths_weaknesses)
        
        # Technical Recommendations
        recommendations = [
            "🔧 Focus on lap time consistency",
            "🌡️ Adapt strategy for weather changes",
            "🏁 Optimize pit stop timing",
            "📊 Analyze sector-specific performance"
        ]
        text_insights['Technical Recommendations'] = '<br>'.join(recommendations)
        
        return text_insights
    
    def generate_executive_summary(self):
        """Generate an executive summary for the analysis"""
        insights = self.generate_technical_insights()
        
        print(f"\n📋 EXECUTIVE SUMMARY: {self.driver_name}")
        print("=" * 60)
        
        if insights.get('performance_summary'):
            perf = insights['performance_summary']
            print(f"🏆 PERFORMANCE OVERVIEW:")
            print(f"   • Average Position: {perf['avg_position']:.1f}")
            print(f"   • Podium Rate: {perf['podium_rate']:.1f}%")
            print(f"   • Championship Points: {perf['total_points']}")
            print(f"   • Race Wins: {perf['wins']}")
        
        if insights.get('strengths'):
            print(f"\n✅ KEY STRENGTHS:")
            for strength in insights['strengths']:
                print(f"   • {strength}")
        
        if insights.get('improvement_areas'):
            print(f"\n⚠️ IMPROVEMENT AREAS:")
            for area in insights['improvement_areas']:
                print(f"   • {area}")
        
        if insights.get('weather_sensitivity'):
            weather = insights['weather_sensitivity']
            print(f"\n🌤️ WEATHER SENSITIVITY:")
            print(f"   • Temperature Correlation: {weather.get('temp_sensitivity', 0):.3f}")
            print(f"   • Weather Advantage: {weather.get('weather_advantage', 'Unknown')}")
        
        print(f"\n🎯 STRATEGIC RECOMMENDATIONS:")
        print(f"   • Focus on consistency training")
        print(f"   • Optimize weather adaptation strategies")
        print(f"   • Enhance pit stop coordination")
        print(f"   • Develop track-specific setups")

def main():
    # Create technical analysis for Charles Leclerc
    analysis = F1TechnicalAnalysis(driver_number=16, driver_name="Charles LECLERC")
    
    # Collect data
    if analysis.collect_driver_data():
        # Generate insights
        analysis.generate_executive_summary()
        
        # Create professional dashboard
        analysis.create_professional_dashboard()
        
        print(f"\n🎉 F1 Technical Analysis Complete!")
        print(f"📊 Open 'f1_technical_dashboard.html' in your browser to view the interactive dashboard")
    else:
        print("❌ Failed to collect data")

if __name__ == "__main__":
    main()


