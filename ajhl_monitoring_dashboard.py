#!/usr/bin/env python3
"""
AJHL Monitoring Dashboard
Comprehensive monitoring and reporting system for AJHL data collection
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.offline as pyo
from ajhl_team_config import DATA_DIRECTORIES, get_active_teams

class AJHLMonitoringDashboard:
    """Monitoring dashboard for AJHL data collection system"""
    
    def __init__(self):
        """Initialize the monitoring dashboard"""
        self.base_path = Path(DATA_DIRECTORIES['base_path'])
        self.setup_directories()
    
    def setup_directories(self):
        """Setup monitoring directories"""
        monitoring_dir = self.base_path / 'monitoring'
        monitoring_dir.mkdir(parents=True, exist_ok=True)
        
        self.dashboard_dir = monitoring_dir / 'dashboards'
        self.dashboard_dir.mkdir(exist_ok=True)
    
    def load_scheduler_stats(self) -> Dict:
        """Load scheduler statistics"""
        stats_path = self.base_path / DATA_DIRECTORIES['logs'] / 'scheduler_stats.json'
        
        if stats_path.exists():
            with open(stats_path, 'r') as f:
                return json.load(f)
        return {}
    
    def load_daily_reports(self, days: int = 30) -> List[Dict]:
        """Load daily reports for the last N days"""
        reports = []
        reports_dir = self.base_path / DATA_DIRECTORIES['reports']
        
        if not reports_dir.exists():
            return reports
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for report_file in reports_dir.glob('daily_summary_*.json'):
            try:
                with open(report_file, 'r') as f:
                    report = json.load(f)
                    report_date = datetime.strptime(report['date'], '%Y-%m-%d')
                    if report_date >= cutoff_date:
                        reports.append(report)
            except Exception as e:
                print(f"Error loading report {report_file}: {e}")
        
        return sorted(reports, key=lambda x: x['date'])
    
    def get_team_data_summary(self) -> Dict:
        """Get summary of data for all teams"""
        team_summaries = {}
        
        for team_id, team_data in get_active_teams().items():
            team_dir = self.base_path / DATA_DIRECTORIES['daily_downloads'] / team_id
            
            if team_dir.exists():
                csv_files = list(team_dir.glob('*.csv'))
                
                team_summaries[team_id] = {
                    'team_name': team_data['team_name'],
                    'city': team_data['city'],
                    'division': team_data['division'],
                    'hudl_team_id': team_data['hudl_team_id'],
                    'total_files': len(csv_files),
                    'latest_file': None,
                    'oldest_file': None,
                    'data_size_mb': 0
                }
                
                if csv_files:
                    # Get file timestamps
                    file_times = [(f, f.stat().st_mtime) for f in csv_files]
                    latest_file = max(file_times, key=lambda x: x[1])[0]
                    oldest_file = min(file_times, key=lambda x: x[1])[0]
                    
                    team_summaries[team_id]['latest_file'] = latest_file.name
                    team_summaries[team_id]['oldest_file'] = oldest_file.name
                    
                    # Calculate total size
                    total_size = sum(f.stat().st_size for f in csv_files)
                    team_summaries[team_id]['data_size_mb'] = total_size / (1024 * 1024)
        
        return team_summaries
    
    def create_success_rate_chart(self, reports: List[Dict]) -> str:
        """Create success rate chart"""
        if not reports:
            return None
        
        dates = [report['date'] for report in reports]
        success_rates = []
        
        for report in reports:
            total_teams = report['total_teams']
            successful_teams = report['successful_teams']
            success_rate = (successful_teams / total_teams) * 100 if total_teams > 0 else 0
            success_rates.append(success_rate)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=success_rates,
            mode='lines+markers',
            name='Success Rate',
            line=dict(color='#2E8B57', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title='Daily Collection Success Rate',
            xaxis_title='Date',
            yaxis_title='Success Rate (%)',
            yaxis=dict(range=[0, 100]),
            template='plotly_white',
            font=dict(family="Courier New, monospace", size=12)
        )
        
        chart_path = self.dashboard_dir / 'success_rate_chart.html'
        pyo.plot(fig, filename=str(chart_path), auto_open=False)
        return str(chart_path)
    
    def create_team_data_chart(self, team_summaries: Dict) -> str:
        """Create team data volume chart"""
        teams = list(team_summaries.keys())
        file_counts = [team_summaries[team]['total_files'] for team in teams]
        team_names = [team_summaries[team]['team_name'] for team in teams]
        
        fig = go.Figure(data=[
            go.Bar(
                x=team_names,
                y=file_counts,
                marker_color='#4169E1',
                text=file_counts,
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title='CSV Files per Team',
            xaxis_title='Team',
            yaxis_title='Number of Files',
            template='plotly_white',
            font=dict(family="Courier New, monospace", size=12),
            xaxis_tickangle=-45
        )
        
        chart_path = self.dashboard_dir / 'team_data_chart.html'
        pyo.plot(fig, filename=str(chart_path), auto_open=False)
        return str(chart_path)
    
    def create_processing_time_chart(self, reports: List[Dict]) -> str:
        """Create processing time chart"""
        if not reports:
            return None
        
        dates = [report['date'] for report in reports]
        processing_times = [report['processing_time_minutes'] for report in reports]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=processing_times,
            mode='lines+markers',
            name='Processing Time',
            line=dict(color='#FF6347', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title='Daily Processing Time',
            xaxis_title='Date',
            yaxis_title='Processing Time (minutes)',
            template='plotly_white',
            font=dict(family="Courier New, monospace", size=12)
        )
        
        chart_path = self.dashboard_dir / 'processing_time_chart.html'
        pyo.plot(fig, filename=str(chart_path), auto_open=False)
        return str(chart_path)
    
    def create_division_comparison_chart(self, team_summaries: Dict) -> str:
        """Create division comparison chart"""
        divisions = {}
        
        for team_id, team_data in team_summaries.items():
            division = team_data['division']
            if division not in divisions:
                divisions[division] = {'teams': 0, 'files': 0, 'size_mb': 0}
            
            divisions[division]['teams'] += 1
            divisions[division]['files'] += team_data['total_files']
            divisions[division]['size_mb'] += team_data['data_size_mb']
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Files per Division', 'Data Size per Division'),
            specs=[[{"type": "bar"}, {"type": "bar"}]]
        )
        
        division_names = list(divisions.keys())
        file_counts = [divisions[div]['files'] for div in division_names]
        data_sizes = [divisions[div]['size_mb'] for div in division_names]
        
        fig.add_trace(
            go.Bar(x=division_names, y=file_counts, name='Files', marker_color='#32CD32'),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Bar(x=division_names, y=data_sizes, name='Size (MB)', marker_color='#FF4500'),
            row=1, col=2
        )
        
        fig.update_layout(
            title='Division Comparison',
            template='plotly_white',
            font=dict(family="Courier New, monospace", size=12)
        )
        
        chart_path = self.dashboard_dir / 'division_comparison_chart.html'
        pyo.plot(fig, filename=str(chart_path), auto_open=False)
        return str(chart_path)
    
    def generate_html_dashboard(self) -> str:
        """Generate comprehensive HTML dashboard"""
        # Load data
        scheduler_stats = self.load_scheduler_stats()
        daily_reports = self.load_daily_reports(30)
        team_summaries = self.get_team_data_summary()
        
        # Create charts
        success_chart = self.create_success_rate_chart(daily_reports)
        team_chart = self.create_team_data_chart(team_summaries)
        time_chart = self.create_processing_time_chart(daily_reports)
        division_chart = self.create_division_comparison_chart(team_summaries)
        
        # Generate HTML
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>AJHL Data Collection Dashboard</title>
            <style>
                body {{
                    font-family: 'Courier New', monospace;
                    margin: 20px;
                    background-color: #f5f5f5;
                }}
                .header {{
                    background-color: #2c3e50;
                    color: white;
                    padding: 20px;
                    border-radius: 10px;
                    margin-bottom: 20px;
                }}
                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                .stat-card {{
                    background-color: white;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .chart-container {{
                    background-color: white;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    margin-bottom: 20px;
                }}
                .team-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }}
                .team-table th, .team-table td {{
                    border: 1px solid #ddd;
                    padding: 12px;
                    text-align: left;
                }}
                .team-table th {{
                    background-color: #f2f2f2;
                }}
                .status-success {{ color: #28a745; }}
                .status-warning {{ color: #ffc107; }}
                .status-danger {{ color: #dc3545; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🏒 AJHL Data Collection Dashboard</h1>
                <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>📊 Scheduler Stats</h3>
                    <p><strong>Total Runs:</strong> {scheduler_stats.get('total_runs', 0)}</p>
                    <p><strong>Successful:</strong> {scheduler_stats.get('successful_runs', 0)}</p>
                    <p><strong>Failed:</strong> {scheduler_stats.get('failed_runs', 0)}</p>
                    <p><strong>Success Rate:</strong> {(scheduler_stats.get('successful_runs', 0) / max(scheduler_stats.get('total_runs', 1), 1) * 100):.1f}%</p>
                </div>
                
                <div class="stat-card">
                    <h3>🏆 Team Coverage</h3>
                    <p><strong>Total Teams:</strong> {len(get_active_teams())}</p>
                    <p><strong>Teams with Data:</strong> {len([t for t in team_summaries.values() if t['total_files'] > 0])}</p>
                    <p><strong>Teams with Hudl IDs:</strong> {len([t for t in team_summaries.values() if t['hudl_team_id']])}</p>
                </div>
                
                <div class="stat-card">
                    <h3>📁 Data Volume</h3>
                    <p><strong>Total Files:</strong> {sum(t['total_files'] for t in team_summaries.values())}</p>
                    <p><strong>Total Size:</strong> {sum(t['data_size_mb'] for t in team_summaries.values()):.1f} MB</p>
                    <p><strong>Avg Files/Team:</strong> {sum(t['total_files'] for t in team_summaries.values()) / max(len(team_summaries), 1):.1f}</p>
                </div>
                
                <div class="stat-card">
                    <h3>⏰ Recent Activity</h3>
                    <p><strong>Last Run:</strong> {scheduler_stats.get('last_run', 'Never')}</p>
                    <p><strong>Next Run:</strong> {scheduler_stats.get('next_run', 'Unknown')}</p>
                    <p><strong>Recent Reports:</strong> {len(daily_reports)}</p>
                </div>
            </div>
            
            <div class="chart-container">
                <h2>📈 Daily Success Rate</h2>
                {f'<iframe src="{success_chart}" width="100%" height="400"></iframe>' if success_chart else '<p>No data available</p>'}
            </div>
            
            <div class="chart-container">
                <h2>📊 Team Data Volume</h2>
                {f'<iframe src="{team_chart}" width="100%" height="400"></iframe>' if team_chart else '<p>No data available</p>'}
            </div>
            
            <div class="chart-container">
                <h2>⏱️ Processing Time Trends</h2>
                {f'<iframe src="{time_chart}" width="100%" height="400"></iframe>' if time_chart else '<p>No data available</p>'}
            </div>
            
            <div class="chart-container">
                <h2>🏆 Division Comparison</h2>
                {f'<iframe src="{division_chart}" width="100%" height="400"></iframe>' if division_chart else '<p>No data available</p>'}
            </div>
            
            <div class="chart-container">
                <h2>👥 Team Status</h2>
                <table class="team-table">
                    <tr>
                        <th>Team</th>
                        <th>City</th>
                        <th>Division</th>
                        <th>Hudl ID</th>
                        <th>Files</th>
                        <th>Size (MB)</th>
                        <th>Status</th>
                    </tr>
        """
        
        for team_id, team_data in team_summaries.items():
            status_class = "status-success" if team_data['total_files'] > 0 else "status-warning"
            status_text = "✅ Active" if team_data['total_files'] > 0 else "⚠️ No Data"
            
            html_content += f"""
                    <tr>
                        <td>{team_data['team_name']}</td>
                        <td>{team_data['city']}</td>
                        <td>{team_data['division']}</td>
                        <td>{team_data['hudl_team_id'] or 'Not Found'}</td>
                        <td>{team_data['total_files']}</td>
                        <td>{team_data['data_size_mb']:.1f}</td>
                        <td class="{status_class}">{status_text}</td>
                    </tr>
            """
        
        html_content += """
                </table>
            </div>
        </body>
        </html>
        """
        
        # Save dashboard
        dashboard_path = self.dashboard_dir / f'ajhl_dashboard_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
        with open(dashboard_path, 'w') as f:
            f.write(html_content)
        
        return str(dashboard_path)
    
    def generate_summary_report(self) -> str:
        """Generate text summary report"""
        scheduler_stats = self.load_scheduler_stats()
        daily_reports = self.load_daily_reports(7)  # Last 7 days
        team_summaries = self.get_team_data_summary()
        
        report = f"""
AJHL Data Collection Summary Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}

SCHEDULER STATISTICS:
- Total Runs: {scheduler_stats.get('total_runs', 0)}
- Successful Runs: {scheduler_stats.get('successful_runs', 0)}
- Failed Runs: {scheduler_stats.get('failed_runs', 0)}
- Success Rate: {(scheduler_stats.get('successful_runs', 0) / max(scheduler_stats.get('total_runs', 1), 1) * 100):.1f}%
- Last Run: {scheduler_stats.get('last_run', 'Never')}
- Next Run: {scheduler_stats.get('next_run', 'Unknown')}

TEAM COVERAGE:
- Total Teams: {len(get_active_teams())}
- Teams with Data: {len([t for t in team_summaries.values() if t['total_files'] > 0])}
- Teams with Hudl IDs: {len([t for t in team_summaries.values() if t['hudl_team_id']])}

DATA VOLUME:
- Total CSV Files: {sum(t['total_files'] for t in team_summaries.values())}
- Total Data Size: {sum(t['data_size_mb'] for t in team_summaries.values()):.1f} MB
- Average Files per Team: {sum(t['total_files'] for t in team_summaries.values()) / max(len(team_summaries), 1):.1f}

RECENT ACTIVITY (Last 7 Days):
"""
        
        if daily_reports:
            for report_data in daily_reports[-3:]:  # Last 3 days
                report += f"""
- {report_data['date']}: {report_data['successful_teams']}/{report_data['total_teams']} teams successful
  Files: {report_data['total_csv_files']}, Time: {report_data['processing_time_minutes']:.1f} min
"""
        else:
            report += "- No recent activity data available\n"
        
        report += f"""
TEAM STATUS:
"""
        
        for team_id, team_data in team_summaries.items():
            status = "✅" if team_data['total_files'] > 0 else "⚠️"
            hudl_status = "✅" if team_data['hudl_team_id'] else "❌"
            report += f"{status} {team_data['team_name']} ({team_data['city']}) - {team_data['total_files']} files, Hudl ID: {hudl_status}\n"
        
        # Save report
        report_path = self.dashboard_dir / f'ajhl_summary_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        with open(report_path, 'w') as f:
            f.write(report)
        
        return str(report_path)

def main():
    """Generate monitoring dashboard and reports"""
    print("📊 AJHL Monitoring Dashboard")
    print("=" * 40)
    
    dashboard = AJHLMonitoringDashboard()
    
    # Generate HTML dashboard
    print("🎨 Generating HTML dashboard...")
    html_path = dashboard.generate_html_dashboard()
    print(f"✅ Dashboard saved to: {html_path}")
    
    # Generate summary report
    print("📄 Generating summary report...")
    report_path = dashboard.generate_summary_report()
    print(f"✅ Report saved to: {report_path}")
    
    print("\n📊 Dashboard complete!")

if __name__ == "__main__":
    main()
