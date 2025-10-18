#!/usr/bin/env python3
"""
F1 Professional Dashboard - Sky Sports F1 Style Technical Analysis
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

class F1ProfessionalDashboard:
    def __init__(self, driver_number=16, driver_name="Charles LECLERC"):
        self.base_url = "https://api.openf1.org/v1"
        self.session = requests.Session()
        self.driver_number = driver_number
        self.driver_name = driver_name
        self.team = "Ferrari"
        
        # Professional F1 color scheme
        self.colors = {
            'ferrari_red': '#DC143C',
            'gold': '#FFD700',
            'black': '#000000',
            'white': '#FFFFFF',
            'gray': '#808080',
            'light_gray': '#F5F5F5'
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
        print(f"🏎️ Collecting {self.driver_name} data...")
        
        # Get all 2024 race sessions
        sessions = self.get_data("sessions", {"year": 2024})
        if not sessions:
            return False
        
        race_sessions = [s for s in sessions if s.get('session_name') == 'Race']
        print(f"📊 Found {len(race_sessions)} race sessions")
        
        # Collect data for first 10 races to avoid rate limits
        for session in race_sessions[:10]:
            session_key = session.get('session_key')
            meeting_key = session.get('meeting_key')
            
            # Get meeting info
            meetings = self.get_data("meetings", {"meeting_key": meeting_key})
            meeting_name = meetings[0].get('meeting_name', 'Unknown') if meetings else 'Unknown'
            
            # Collect data with rate limiting
            self._collect_session_data(session_key, meeting_name)
            import time
            time.sleep(0.5)  # Rate limiting
        
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
    
    def create_professional_dashboard(self):
        """Create a professional F1 technical analysis dashboard"""
        print("\n📊 Creating Professional F1 Dashboard...")
        
        # Create the main dashboard
        fig = make_subplots(
            rows=3, cols=3,
            subplot_titles=[
                'Performance Overview', 'Race Results Trend', 'Lap Time Analysis',
                'Track Performance', 'Weather Impact', 'Pit Stop Strategy',
                'Consistency Metrics', 'Position Changes', 'Key Insights'
            ],
            specs=[
                [{"type": "indicator"}, {"type": "scatter"}, {"type": "histogram"}],
                [{"type": "bar"}, {"type": "scatter"}, {"type": "bar"}],
                [{"type": "bar"}, {"type": "scatter"}, {"type": "table"}]
            ],
            vertical_spacing=0.1,
            horizontal_spacing=0.1
        )
        
        # 1. Performance Overview (Gauge)
        self._add_performance_gauge(fig, row=1, col=1)
        
        # 2. Race Results Trend
        self._add_race_trend(fig, row=1, col=2)
        
        # 3. Lap Time Distribution
        self._add_lap_time_distribution(fig, row=1, col=3)
        
        # 4. Track Performance
        self._add_track_performance(fig, row=2, col=1)
        
        # 5. Weather Impact
        self._add_weather_impact(fig, row=2, col=2)
        
        # 6. Pit Stop Strategy
        self._add_pit_stop_analysis(fig, row=2, col=3)
        
        # 7. Consistency Metrics
        self._add_consistency_metrics(fig, row=3, col=1)
        
        # 8. Position Changes
        self._add_position_changes(fig, row=3, col=2)
        
        # 9. Key Insights Table
        self._add_insights_table(fig, row=3, col=3)
        
        # Update layout
        fig.update_layout(
            title=dict(
                text=f"<b>F1 Technical Analysis: {self.driver_name}</b><br><sub>2024 Season Performance Dashboard</sub>",
                x=0.5,
                font=dict(size=24, color=self.colors['black'])
            ),
            height=1000,
            showlegend=False,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Arial", size=12, color=self.colors['black'])
        )
        
        # Save the dashboard
        fig.write_html("f1_professional_dashboard.html")
        print("✅ Professional F1 Dashboard saved as 'f1_professional_dashboard.html'")
        
        return fig
    
    def _add_performance_gauge(self, fig, row, col):
        """Add performance gauge"""
        if not self.position_data:
            return
        
        # Calculate average position
        positions = []
        for session_key, df in self.position_data.items():
            if not df.empty:
                final_pos = df.iloc[-1]
                positions.append(final_pos['position'])
        
        if positions:
            avg_position = np.mean(positions)
            
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number+delta",
                    value=avg_position,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Average Position", 'font': {'size': 16}},
                    gauge={
                        'axis': {'range': [None, 20], 'tickwidth': 1, 'tickcolor': "darkblue"},
                        'bar': {'color': self.colors['ferrari_red']},
                        'bgcolor': "white",
                        'borderwidth': 2,
                        'bordercolor': "gray",
                        'steps': [
                            {'range': [0, 5], 'color': "lightgreen"},
                            {'range': [5, 10], 'color': "yellow"},
                            {'range': [10, 20], 'color': "lightcoral"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 5
                        }
                    }
                ),
                row=row, col=col
            )
    
    def _add_race_trend(self, fig, row, col):
        """Add race results trend"""
        if not self.position_data:
            return
        
        race_results = []
        for session_key, df in self.position_data.items():
            if not df.empty:
                final_pos = df.iloc[-1]
                race_results.append({
                    'race': final_pos['meeting_name'],
                    'position': final_pos['position'],
                    'date': pd.to_datetime(final_pos['date'])
                })
        
        if race_results:
            results_df = pd.DataFrame(race_results)
            results_df = results_df.sort_values('date')
            
            # Color points based on performance
            colors = []
            for pos in results_df['position']:
                if pos == 1:
                    colors.append('gold')
                elif pos <= 3:
                    colors.append('silver')
                elif pos <= 10:
                    colors.append(self.colors['ferrari_red'])
                else:
                    colors.append('gray')
            
            fig.add_trace(
                go.Scatter(
                    x=list(range(len(results_df))),
                    y=results_df['position'],
                    mode='lines+markers',
                    name="Race Results",
                    line=dict(color=self.colors['ferrari_red'], width=3),
                    marker=dict(size=10, color=colors, line=dict(width=2, color='black')),
                    text=results_df['race'],
                    hovertemplate="<b>%{text}</b><br>Position: %{y}<extra></extra>"
                ),
                row=row, col=col
            )
            
            fig.update_yaxes(title_text="Position", row=row, col=col, autorange="reversed")
            fig.update_xaxes(title_text="Race Number", row=row, col=col)
    
    def _add_lap_time_distribution(self, fig, row, col):
        """Add lap time distribution"""
        if not self.lap_data:
            return
        
        all_laps = []
        for session_key, df in self.lap_data.items():
            valid_laps = df[df['lap_duration'].notna()]
            if not valid_laps.empty:
                all_laps.extend(valid_laps['lap_duration'].tolist())
        
        if all_laps:
            fig.add_trace(
                go.Histogram(
                    x=all_laps,
                    nbinsx=30,
                    name="Lap Time Distribution",
                    marker_color=self.colors['ferrari_red'],
                    opacity=0.7
                ),
                row=row, col=col
            )
            
            fig.update_xaxes(title_text="Lap Time (seconds)", row=row, col=col)
            fig.update_yaxes(title_text="Frequency", row=row, col=col)
    
    def _add_track_performance(self, fig, row, col):
        """Add track performance analysis"""
        if not self.lap_data:
            return
        
        track_performance = []
        for session_key, df in self.lap_data.items():
            valid_laps = df[df['lap_duration'].notna()]
            if not valid_laps.empty:
                # Get final position
                final_position = None
                if session_key in self.position_data:
                    pos_df = self.position_data[session_key]
                    if not pos_df.empty:
                        final_position = pos_df.iloc[-1]['position']
                
                if final_position:
                    track_performance.append({
                        'track': df.iloc[0]['meeting_name'],
                        'avg_lap_time': valid_laps['lap_duration'].mean(),
                        'final_position': final_position
                    })
        
        if track_performance:
            perf_df = pd.DataFrame(track_performance)
            perf_df = perf_df.sort_values('final_position')
            
            # Color bars based on position
            colors = []
            for pos in perf_df['final_position']:
                if pos == 1:
                    colors.append('gold')
                elif pos <= 3:
                    colors.append('silver')
                elif pos <= 10:
                    colors.append(self.colors['ferrari_red'])
                else:
                    colors.append('gray')
            
            fig.add_trace(
                go.Bar(
                    x=perf_df['track'],
                    y=perf_df['final_position'],
                    name="Track Performance",
                    marker_color=colors,
                    text=perf_df['final_position'],
                    textposition='auto'
                ),
                row=row, col=col
            )
            
            fig.update_yaxes(title_text="Final Position", row=row, col=col, autorange="reversed")
            fig.update_xaxes(title_text="Track", row=row, col=col, tickangle=45)
    
    def _add_weather_impact(self, fig, row, col):
        """Add weather impact analysis"""
        if not self.weather_data or not self.lap_data:
            return
        
        weather_performance = []
        for session_key in self.weather_data.keys():
            if session_key in self.lap_data:
                weather_df = self.weather_data[session_key]
                lap_df = self.lap_data[session_key]
                
                if not weather_df.empty and not lap_df.empty:
                    avg_temp = weather_df['air_temperature'].mean()
                    valid_laps = lap_df[lap_df['lap_duration'].notna()]
                    
                    if not valid_laps.empty:
                        avg_lap_time = valid_laps['lap_duration'].mean()
                        
                        # Get final position
                        final_position = None
                        if session_key in self.position_data:
                            pos_df = self.position_data[session_key]
                            if not pos_df.empty:
                                final_position = pos_df.iloc[-1]['position']
                        
                        if final_position:
                            weather_performance.append({
                                'temperature': avg_temp,
                                'position': final_position,
                                'track': weather_df.iloc[0]['meeting_name']
                            })
        
        if weather_performance:
            weather_df = pd.DataFrame(weather_performance)
            
            fig.add_trace(
                go.Scatter(
                    x=weather_df['temperature'],
                    y=weather_df['position'],
                    mode='markers+text',
                    name="Weather Impact",
                    marker=dict(size=15, color=self.colors['ferrari_red']),
                    text=weather_df['track'],
                    textposition="top center",
                    hovertemplate="<b>%{text}</b><br>Temperature: %{x}°C<br>Position: %{y}<extra></extra>"
                ),
                row=row, col=col
            )
            
            fig.update_xaxes(title_text="Temperature (°C)", row=row, col=col)
            fig.update_yaxes(title_text="Final Position", row=row, col=col, autorange="reversed")
    
    def _add_pit_stop_analysis(self, fig, row, col):
        """Add pit stop analysis"""
        if not self.pit_data:
            return
        
        pit_analysis = []
        for session_key, df in self.pit_data.items():
            if not df.empty:
                pit_analysis.append({
                    'track': df.iloc[0]['meeting_name'],
                    'pit_count': len(df),
                    'avg_pit_time': df['pit_duration'].mean() if 'pit_duration' in df.columns else None
                })
        
        if pit_analysis:
            pit_df = pd.DataFrame(pit_analysis)
            
            fig.add_trace(
                go.Bar(
                    x=pit_df['track'],
                    y=pit_df['pit_count'],
                    name="Pit Stops per Race",
                    marker_color=self.colors['gold'],
                    text=pit_df['pit_count'],
                    textposition='auto'
                ),
                row=row, col=col
            )
            
            fig.update_yaxes(title_text="Number of Pit Stops", row=row, col=col)
            fig.update_xaxes(title_text="Track", row=row, col=col, tickangle=45)
    
    def _add_consistency_metrics(self, fig, row, col):
        """Add consistency metrics"""
        if not self.lap_data:
            return
        
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
                    'cv': cv
                })
        
        if consistency_data:
            cons_df = pd.DataFrame(consistency_data)
            cons_df = cons_df.sort_values('consistency')
            
            fig.add_trace(
                go.Bar(
                    x=cons_df['track'],
                    y=cons_df['consistency'],
                    name="Lap Consistency",
                    marker_color=self.colors['ferrari_red'],
                    text=cons_df['consistency'].round(2),
                    textposition='auto'
                ),
                row=row, col=col
            )
            
            fig.update_yaxes(title_text="Lap Time Std Dev (seconds)", row=row, col=col)
            fig.update_xaxes(title_text="Track", row=row, col=col, tickangle=45)
    
    def _add_position_changes(self, fig, row, col):
        """Add position changes during races"""
        if not self.position_data:
            return
        
        # Show position changes for a few races
        race_count = 0
        for session_key, df in self.position_data.items():
            if race_count >= 3:  # Show only first 3 races
                break
            
            if not df.empty and len(df) > 1:
                fig.add_trace(
                    go.Scatter(
                        x=list(range(len(df))),
                        y=df['position'],
                        mode='lines+markers',
                        name=df.iloc[0]['meeting_name'],
                        line=dict(width=2),
                        marker=dict(size=6)
                    ),
                    row=row, col=col
                )
                race_count += 1
        
        fig.update_yaxes(title_text="Position", row=row, col=col, autorange="reversed")
        fig.update_xaxes(title_text="Lap", row=row, col=col)
    
    def _add_insights_table(self, fig, row, col):
        """Add key insights table"""
        insights = self._generate_insights()
        
        # Create table data
        table_data = []
        for category, items in insights.items():
            for item in items:
                table_data.append([category, item])
        
        if table_data:
            fig.add_trace(
                go.Table(
                    header=dict(
                        values=['Category', 'Insight'],
                        fill_color=self.colors['ferrari_red'],
                        font=dict(color='white', size=12),
                        align='left'
                    ),
                    cells=dict(
                        values=list(zip(*table_data)),
                        fill_color='white',
                        font=dict(color='black', size=10),
                        align='left',
                        height=25
                    )
                ),
                row=row, col=col
            )
    
    def _generate_insights(self):
        """Generate key insights"""
        insights = {
            'Performance': [],
            'Strengths': [],
            'Areas for Improvement': [],
            'Technical Notes': []
        }
        
        if self.position_data:
            positions = []
            for session_key, df in self.position_data.items():
                if not df.empty:
                    positions.append(df.iloc[-1]['position'])
            
            if positions:
                avg_position = np.mean(positions)
                podium_count = len([p for p in positions if p <= 3])
                podium_rate = (podium_count / len(positions)) * 100
                
                insights['Performance'].append(f"Average Position: {avg_position:.1f}")
                insights['Performance'].append(f"Podium Rate: {podium_rate:.1f}%")
                
                if podium_rate > 40:
                    insights['Strengths'].append("High podium consistency")
                
                if avg_position > 6:
                    insights['Areas for Improvement'].append("Race pace optimization needed")
        
        if self.lap_data:
            all_laps = []
            for session_key, df in self.lap_data.items():
                valid_laps = df[df['lap_duration'].notna()]
                if not valid_laps.empty:
                    all_laps.extend(valid_laps['lap_duration'].tolist())
            
            if all_laps:
                lap_consistency = np.std(all_laps)
                if lap_consistency > 5:
                    insights['Areas for Improvement'].append("Lap time consistency")
                else:
                    insights['Strengths'].append("Excellent lap consistency")
        
        insights['Technical Notes'].append("Data from 2024 season")
        insights['Technical Notes'].append("Ferrari SF-24 chassis")
        insights['Technical Notes'].append("Analysis based on race sessions")
        
        return insights
    
    def generate_summary_report(self):
        """Generate a comprehensive summary report"""
        print(f"\n📋 F1 TECHNICAL ANALYSIS REPORT: {self.driver_name}")
        print("=" * 60)
        
        if not self.position_data:
            print("❌ No data available for analysis")
            return
        
        # Performance Summary
        positions = []
        for session_key, df in self.position_data.items():
            if not df.empty:
                positions.append(df.iloc[-1]['position'])
        
        if positions:
            avg_position = np.mean(positions)
            podium_count = len([p for p in positions if p <= 3])
            podium_rate = (podium_count / len(positions)) * 100
            wins = len([p for p in positions if p == 1])
            
            print(f"🏆 PERFORMANCE SUMMARY:")
            print(f"   • Total Races: {len(positions)}")
            print(f"   • Average Position: {avg_position:.1f}")
            print(f"   • Podium Finishes: {podium_count} ({podium_rate:.1f}%)")
            print(f"   • Race Wins: {wins}")
            
            # Championship points
            points_system = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}
            total_points = sum(points_system.get(p, 0) for p in positions)
            print(f"   • Championship Points: {total_points}")
        
        # Lap Analysis
        if self.lap_data:
            all_laps = []
            for session_key, df in self.lap_data.items():
                valid_laps = df[df['lap_duration'].notna()]
                if not valid_laps.empty:
                    all_laps.extend(valid_laps['lap_duration'].tolist())
            
            if all_laps:
                fastest_lap = min(all_laps)
                avg_lap = np.mean(all_laps)
                lap_consistency = np.std(all_laps)
                
                print(f"\n⏱️ LAP ANALYSIS:")
                print(f"   • Fastest Lap: {fastest_lap:.3f}s")
                print(f"   • Average Lap Time: {avg_lap:.3f}s")
                print(f"   • Lap Consistency (std): {lap_consistency:.3f}s")
        
        # Pit Stop Analysis
        if self.pit_data:
            total_pits = sum(len(df) for df in self.pit_data.values())
            avg_pits_per_race = total_pits / len(self.pit_data) if self.pit_data else 0
            
            print(f"\n🔧 PIT STOP ANALYSIS:")
            print(f"   • Total Pit Stops: {total_pits}")
            print(f"   • Average per Race: {avg_pits_per_race:.1f}")
        
        # Weather Analysis
        if self.weather_data:
            print(f"\n🌤️ WEATHER DATA:")
            print(f"   • Sessions with Weather Data: {len(self.weather_data)}")
        
        print(f"\n🎯 KEY INSIGHTS:")
        insights = self._generate_insights()
        for category, items in insights.items():
            if items:
                print(f"   {category}:")
                for item in items:
                    print(f"     • {item}")

def main():
    # Create professional dashboard for Charles Leclerc
    dashboard = F1ProfessionalDashboard(driver_number=16, driver_name="Charles LECLERC")
    
    # Collect data
    if dashboard.collect_driver_data():
        # Generate summary report
        dashboard.generate_summary_report()
        
        # Create professional dashboard
        dashboard.create_professional_dashboard()
        
        print(f"\n🎉 F1 Professional Analysis Complete!")
        print(f"📊 Open 'f1_professional_dashboard.html' in your browser to view the interactive dashboard")
        print(f"🔗 This dashboard provides Sky Sports F1 style technical analysis")
    else:
        print("❌ Failed to collect data")

if __name__ == "__main__":
    main()


