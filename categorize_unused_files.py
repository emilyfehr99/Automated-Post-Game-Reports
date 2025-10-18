#!/usr/bin/env python3
"""
Categorize unused files by their purpose and identify truly orphaned files
"""

import os
import re
from collections import defaultdict

def categorize_file(filename):
    """Categorize a file based on its name and likely purpose."""
    filename_lower = filename.lower()
    
    # NHL/Logo related
    if any(word in filename_lower for word in ['logo', 'nhl', 'team_logo']):
        return 'NHL/Logo Analysis'
    
    # API related
    if any(word in filename_lower for word in ['api', 'client', 'extractor', 'scraper']):
        return 'API/Data Extraction'
    
    # Analytics/Reports
    if any(word in filename_lower for word in ['analytics', 'analysis', 'report', 'comprehensive', 'advanced']):
        return 'Analytics/Reports'
    
    # Debug/Test files
    if any(word in filename_lower for word in ['debug', 'test', 'check', 'verify']):
        return 'Debug/Test Files'
    
    # Dashboard/Visualization
    if any(word in filename_lower for word in ['dashboard', 'visualization', 'plot', 'chart']):
        return 'Dashboard/Visualization'
    
    # Data processing
    if any(word in filename_lower for word in ['data', 'collector', 'processor', 'metrics']):
        return 'Data Processing'
    
    # Hudl related
    if 'hudl' in filename_lower:
        return 'Hudl Integration'
    
    # AJHL related
    if 'ajhl' in filename_lower:
        return 'AJHL System'
    
    # Network/Monitoring
    if any(word in filename_lower for word in ['network', 'capture', 'monitor', 'notification']):
        return 'Network/Monitoring'
    
    # Database
    if any(word in filename_lower for word in ['database', 'table', 'create']):
        return 'Database Operations'
    
    return 'Other'

def main():
    # First 50 unused files from our analysis
    unused_files = [
        'actual_logo_report.py', 'advanced_api_client.py', 'advanced_hockey_analytics.py',
        'advanced_nhl_analytics.py', 'advanced_notification.py', 'ajhl_api_with_hudl_scraper.py',
        'ajhl_complete_data_api.py', 'ajhl_complete_metrics_api.py', 'ajhl_complete_system.py',
        'ajhl_complete_system_with_notifications.py', 'ajhl_comprehensive_api.py',
        'ajhl_comprehensive_api_no_auth.py', 'ajhl_direct_site_api.py', 'ajhl_fast_api.py',
        'ajhl_real_team_league_api.py', 'analyze_export_buttons.py', 'analyze_game.py',
        'api_data_extractor.py', 'api_vs_scraping_analysis.py', 'automated_network_capture.py',
        'beautiful_goalie_dashboard.py', 'browser_api_interceptor.py', 'check_alternative_nhl_apis.py',
        'check_daily_updates.py', 'check_real_logo_urls.py', 'clean_professional_dashboard.py',
        'coaching_dashboard.py', 'comprehensive_goalie_dashboard.py', 'comprehensive_metrics_analysis.py',
        'comprehensive_metrics_scraper.py', 'comprehensive_player_data_extractor.py',
        'comprehensive_real_logo_report.py', 'console_log_extractor.py', 'create_all_team_logos.py',
        'create_comprehensive_player_database.py', 'create_detailed_players_table.py',
        'create_fast_visualization.py', 'daily_data_collector.py', 'daily_metrics_collector.py',
        'data_collection_analysis.py', 'database_summary.py', 'debug_api_structure.py',
        'debug_details.py', 'debug_html_extraction.py', 'debug_hudl_auth.py', 'debug_logos.py',
        'debug_metrics_extraction.py', 'debug_player_data.py', 'debug_roster.py', 'debug_team_logos.py'
    ]
    
    # Categorize files
    categories = defaultdict(list)
    for file in unused_files:
        category = categorize_file(file)
        categories[category].append(file)
    
    print("="*80)
    print("CATEGORIZATION OF FIRST 50 UNUSED FILES")
    print("="*80)
    
    for category, files in sorted(categories.items()):
        print(f"\n📁 {category} ({len(files)} files):")
        for file in files:
            print(f"  • {file}")
    
    print(f"\n📊 SUMMARY:")
    print(f"  Total files analyzed: {len(unused_files)}")
    for category, files in sorted(categories.items()):
        print(f"  {category}: {len(files)} files")
    
    # Identify truly orphaned files (not part of active systems)
    print(f"\n🗑️  TRULY ORPHANED FILES (safe to delete):")
    
    truly_orphaned = []
    for file in unused_files:
        category = categorize_file(file)
        # These categories are likely orphaned
        if category in ['Debug/Test Files', 'Other']:
            truly_orphaned.append(file)
        # Some specific files that are clearly old/duplicate
        elif any(word in file.lower() for word in ['old', 'backup', 'test_', 'debug_', 'check_']):
            truly_orphaned.append(file)
    
    for file in truly_orphaned:
        print(f"  • {file}")
    
    print(f"\n💡 RECOMMENDATIONS:")
    print(f"  • Safe to delete immediately: {len(truly_orphaned)} files")
    print(f"  • Review before deleting: {len(unused_files) - len(truly_orphaned)} files")
    print(f"  • Focus on consolidating duplicate functionality")

if __name__ == "__main__":
    main()
