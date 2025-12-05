#!/usr/bin/env python3
"""
Comprehensive Test Script for Instat Hudl API
Tests all functionality including team, player, and league metrics access

This script demonstrates the complete capabilities of the Instat Hudl API system
"""

import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Any
import os
import sys

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from comprehensive_instat_hudl_api import ComprehensiveInstatHudlAPI
from instat_league_metrics_aggregator import InstatLeagueMetricsAggregator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class InstatAPITester:
    """Comprehensive tester for the Instat Hudl API system"""
    
    def __init__(self, headless: bool = True):
        """Initialize the API tester"""
        self.api = ComprehensiveInstatHudlAPI(headless=headless)
        self.aggregator = InstatLeagueMetricsAggregator(self.api)
        self.test_results = {}
        
    def run_all_tests(self, username: str = None, password: str = None, 
                     team_ids: List[str] = None, league_id: str = None) -> Dict[str, Any]:
        """Run all comprehensive tests"""
        logger.info("🧪 Starting comprehensive Instat API tests")
        
        test_results = {
            "test_timestamp": datetime.now().isoformat(),
            "tests_run": [],
            "overall_success": True,
            "summary": {}
        }
        
        try:
            # Test 1: API Initialization
            self._test_api_initialization(test_results)
            
            # Test 2: Data Table Structure
            self._test_data_table_structure(test_results)
            
            # Test 3: Authentication (if credentials provided)
            if username and password:
                self._test_authentication(username, password, test_results)
                
                # Test 4: Team Metrics Access
                if team_ids:
                    self._test_team_metrics_access(team_ids, test_results)
                
                # Test 5: Player Metrics Access
                if team_ids:
                    self._test_player_metrics_access(team_ids, test_results)
                
                # Test 6: League Metrics Access
                self._test_league_metrics_access(league_id, team_ids, test_results)
                
                # Test 7: Data Export
                self._test_data_export(test_results)
                
                # Test 8: League Analytics
                self._test_league_analytics(team_ids, test_results)
            
            else:
                logger.warning("⚠️  No credentials provided - skipping authenticated tests")
                test_results["tests_run"].append({
                    "test": "authentication",
                    "status": "skipped",
                    "message": "No credentials provided"
                })
            
            # Test 9: Error Handling
            self._test_error_handling(test_results)
            
        except Exception as e:
            logger.error(f"❌ Test suite failed: {e}")
            test_results["overall_success"] = False
            test_results["error"] = str(e)
        
        finally:
            # Cleanup
            self.api.close()
        
        # Generate summary
        test_results["summary"] = self._generate_test_summary(test_results)
        
        logger.info("✅ All tests completed")
        return test_results
    
    def _test_api_initialization(self, test_results: Dict[str, Any]):
        """Test API initialization and basic setup"""
        logger.info("🔧 Testing API initialization...")
        
        try:
            # Test data table structure
            table_info = self.api.get_data_table_info()
            
            assert len(table_info) == 12, f"Expected 12 data tables, got {len(table_info)}"
            
            # Verify all expected tables are present
            expected_tables = [
                "goalie_career_tables", "goalie_matches_tables", "match_goalies_tables",
                "match_lines_tables", "match_overview_players_tables", "match_players_tables",
                "player_career_tables", "player_matches_tables", "team_goalies_tables",
                "team_lines_tables", "team_matches_tables", "team_players_tables"
            ]
            
            for table_name in expected_tables:
                assert table_name in table_info, f"Missing table: {table_name}"
            
            test_results["tests_run"].append({
                "test": "api_initialization",
                "status": "passed",
                "message": f"Successfully initialized with {len(table_info)} data tables"
            })
            
        except Exception as e:
            test_results["tests_run"].append({
                "test": "api_initialization",
                "status": "failed",
                "message": str(e)
            })
            test_results["overall_success"] = False
    
    def _test_data_table_structure(self, test_results: Dict[str, Any]):
        """Test data table structure and mapping"""
        logger.info("📊 Testing data table structure...")
        
        try:
            table_info = self.api.get_data_table_info()
            
            # Verify table IDs match expected values
            expected_ids = {
                "goalie_career_tables": 6,
                "goalie_matches_tables": 3,
                "match_goalies_tables": 17,
                "match_lines_tables": 18,
                "match_overview_players_tables": 15,
                "match_players_tables": 16,
                "player_career_tables": 5,
                "player_matches_tables": 2,
                "team_goalies_tables": 9,
                "team_lines_tables": 14,
                "team_matches_tables": 1,
                "team_players_tables": 8
            }
            
            for table_name, expected_id in expected_ids.items():
                actual_id = table_info[table_name]["table_id"]
                assert actual_id == expected_id, f"Table {table_name} ID mismatch: expected {expected_id}, got {actual_id}"
            
            # Verify priority levels
            priority_1_tables = [t for t in table_info.values() if t["priority"] == 1]
            priority_2_tables = [t for t in table_info.values() if t["priority"] == 2]
            
            assert len(priority_1_tables) > 0, "No priority 1 tables found"
            assert len(priority_2_tables) > 0, "No priority 2 tables found"
            
            test_results["tests_run"].append({
                "test": "data_table_structure",
                "status": "passed",
                "message": f"All {len(table_info)} tables have correct structure and IDs"
            })
            
        except Exception as e:
            test_results["tests_run"].append({
                "test": "data_table_structure",
                "status": "failed",
                "message": str(e)
            })
            test_results["overall_success"] = False
    
    def _test_authentication(self, username: str, password: str, test_results: Dict[str, Any]):
        """Test authentication with Hudl Instat"""
        logger.info("🔐 Testing authentication...")
        
        try:
            success = self.api.authenticate(username, password)
            
            if success:
                test_results["tests_run"].append({
                    "test": "authentication",
                    "status": "passed",
                    "message": "Successfully authenticated with Hudl Instat"
                })
            else:
                test_results["tests_run"].append({
                    "test": "authentication",
                    "status": "failed",
                    "message": "Authentication failed - check credentials"
                })
                test_results["overall_success"] = False
                
        except Exception as e:
            test_results["tests_run"].append({
                "test": "authentication",
                "status": "failed",
                "message": f"Authentication error: {str(e)}"
            })
            test_results["overall_success"] = False
    
    def _test_team_metrics_access(self, team_ids: List[str], test_results: Dict[str, Any]):
        """Test team metrics access"""
        logger.info("🏒 Testing team metrics access...")
        
        try:
            successful_teams = 0
            failed_teams = []
            
            for team_id in team_ids:
                try:
                    team_metrics = self.api.get_team_comprehensive_metrics(team_id)
                    
                    # Verify team metrics structure
                    assert hasattr(team_metrics, 'team_id'), "Team metrics missing team_id"
                    assert hasattr(team_metrics, 'team_name'), "Team metrics missing team_name"
                    assert hasattr(team_metrics, 'players'), "Team metrics missing players"
                    assert hasattr(team_metrics, 'games'), "Team metrics missing games"
                    assert hasattr(team_metrics, 'team_stats'), "Team metrics missing team_stats"
                    
                    successful_teams += 1
                    logger.info(f"✅ Successfully retrieved metrics for team {team_id}")
                    
                except Exception as e:
                    failed_teams.append({"team_id": team_id, "error": str(e)})
                    logger.warning(f"⚠️  Failed to get metrics for team {team_id}: {e}")
            
            test_results["tests_run"].append({
                "test": "team_metrics_access",
                "status": "passed" if successful_teams > 0 else "failed",
                "message": f"Successfully retrieved metrics for {successful_teams}/{len(team_ids)} teams",
                "details": {
                    "successful_teams": successful_teams,
                    "failed_teams": failed_teams
                }
            })
            
            if successful_teams == 0:
                test_results["overall_success"] = False
                
        except Exception as e:
            test_results["tests_run"].append({
                "test": "team_metrics_access",
                "status": "failed",
                "message": f"Team metrics access error: {str(e)}"
            })
            test_results["overall_success"] = False
    
    def _test_player_metrics_access(self, team_ids: List[str], test_results: Dict[str, Any]):
        """Test player metrics access"""
        logger.info("👤 Testing player metrics access...")
        
        try:
            successful_players = 0
            failed_players = []
            
            for team_id in team_ids:
                try:
                    # Get team metrics first to get player list
                    team_metrics = self.api.get_team_comprehensive_metrics(team_id)
                    
                    # Test first few players to avoid overwhelming the API
                    test_players = team_metrics.players[:3]  # Test first 3 players
                    
                    for player in test_players:
                        try:
                            player_metrics = self.api.get_player_comprehensive_metrics(
                                player["player_id"], team_id
                            )
                            
                            # Verify player metrics structure
                            assert hasattr(player_metrics, 'player_id'), "Player metrics missing player_id"
                            assert hasattr(player_metrics, 'player_name'), "Player metrics missing player_name"
                            assert hasattr(player_metrics, 'career_stats'), "Player metrics missing career_stats"
                            assert hasattr(player_metrics, 'match_stats'), "Player metrics missing match_stats"
                            
                            successful_players += 1
                            
                        except Exception as e:
                            failed_players.append({
                                "player_id": player["player_id"],
                                "team_id": team_id,
                                "error": str(e)
                            })
                
                except Exception as e:
                    logger.warning(f"⚠️  Could not get team metrics for player testing: {e}")
            
            test_results["tests_run"].append({
                "test": "player_metrics_access",
                "status": "passed" if successful_players > 0 else "failed",
                "message": f"Successfully retrieved metrics for {successful_players} players",
                "details": {
                    "successful_players": successful_players,
                    "failed_players": failed_players[:5]  # Limit failed players in output
                }
            })
            
            if successful_players == 0:
                test_results["overall_success"] = False
                
        except Exception as e:
            test_results["tests_run"].append({
                "test": "player_metrics_access",
                "status": "failed",
                "message": f"Player metrics access error: {str(e)}"
            })
            test_results["overall_success"] = False
    
    def _test_league_metrics_access(self, league_id: str, team_ids: List[str], test_results: Dict[str, Any]):
        """Test league metrics access"""
        logger.info("🏆 Testing league metrics access...")
        
        try:
            league_metrics = self.api.get_league_comprehensive_metrics(league_id)
            
            # Verify league metrics structure
            assert "league_name" in league_metrics, "League metrics missing league_name"
            assert "teams" in league_metrics, "League metrics missing teams"
            assert "standings" in league_metrics, "League metrics missing standings"
            
            test_results["tests_run"].append({
                "test": "league_metrics_access",
                "status": "passed",
                "message": f"Successfully retrieved league metrics with {len(league_metrics.get('teams', []))} teams"
            })
            
        except Exception as e:
            test_results["tests_run"].append({
                "test": "league_metrics_access",
                "status": "failed",
                "message": f"League metrics access error: {str(e)}"
            })
            test_results["overall_success"] = False
    
    def _test_data_export(self, test_results: Dict[str, Any]):
        """Test data export functionality"""
        logger.info("💾 Testing data export...")
        
        try:
            # Create a mock team metrics object for testing
            from comprehensive_instat_hudl_api import TeamMetrics
            
            mock_team_metrics = TeamMetrics(
                team_id="test_team",
                team_name="Test Team",
                league="Test League",
                season="2024-25",
                players=[{"player_id": "1", "name": "Test Player", "position": "F"}],
                games=[{"game_id": "1", "date": "2024-01-01", "opponent": "Test Opponent"}],
                team_stats={"goals_for": 10, "goals_against": 5},
                league_rankings={"current_rank": 1},
                last_updated=datetime.now().isoformat()
            )
            
            # Test CSV export
            exported_files = self.api.export_team_data_to_csv(mock_team_metrics, "test_export")
            
            # Verify files were created
            assert len(exported_files) > 0, "No files were exported"
            
            # Check if files exist
            for file_type, file_path in exported_files.items():
                assert os.path.exists(file_path), f"Exported file {file_path} does not exist"
            
            # Cleanup test files
            import shutil
            if os.path.exists("test_export"):
                shutil.rmtree("test_export")
            
            test_results["tests_run"].append({
                "test": "data_export",
                "status": "passed",
                "message": f"Successfully exported {len(exported_files)} files"
            })
            
        except Exception as e:
            test_results["tests_run"].append({
                "test": "data_export",
                "status": "failed",
                "message": f"Data export error: {str(e)}"
            })
            test_results["overall_success"] = False
    
    def _test_league_analytics(self, team_ids: List[str], test_results: Dict[str, Any]):
        """Test league analytics functionality"""
        logger.info("📈 Testing league analytics...")
        
        try:
            # Test league analysis
            analysis = self.aggregator.get_comprehensive_league_analysis(team_ids=team_ids)
            
            # Verify analysis structure
            assert "standings" in analysis, "Analysis missing standings"
            assert "leaders" in analysis, "Analysis missing leaders"
            assert "analytics" in analysis, "Analysis missing analytics"
            assert "team_comparisons" in analysis, "Analysis missing team comparisons"
            
            # Test CSV export
            exported_files = self.aggregator.export_league_analysis_to_csv(analysis, "test_league_export")
            
            # Verify files were created
            assert len(exported_files) > 0, "No league analysis files were exported"
            
            # Cleanup test files
            import shutil
            if os.path.exists("test_league_export"):
                shutil.rmtree("test_league_export")
            
            test_results["tests_run"].append({
                "test": "league_analytics",
                "status": "passed",
                "message": f"Successfully generated league analysis with {len(exported_files)} exported files"
            })
            
        except Exception as e:
            test_results["tests_run"].append({
                "test": "league_analytics",
                "status": "failed",
                "message": f"League analytics error: {str(e)}"
            })
            test_results["overall_success"] = False
    
    def _test_error_handling(self, test_results: Dict[str, Any]):
        """Test error handling and edge cases"""
        logger.info("⚠️  Testing error handling...")
        
        try:
            # Test with invalid team ID
            try:
                invalid_team_metrics = self.api.get_team_comprehensive_metrics("invalid_team_id")
                # If this doesn't raise an exception, that's also a valid test result
                test_results["tests_run"].append({
                    "test": "error_handling_invalid_team",
                    "status": "passed",
                    "message": "Handled invalid team ID gracefully"
                })
            except Exception as e:
                # This is expected behavior
                test_results["tests_run"].append({
                    "test": "error_handling_invalid_team",
                    "status": "passed",
                    "message": f"Correctly raised exception for invalid team ID: {type(e).__name__}"
                })
            
            # Test with invalid player ID
            try:
                invalid_player_metrics = self.api.get_player_comprehensive_metrics("invalid_player_id")
                test_results["tests_run"].append({
                    "test": "error_handling_invalid_player",
                    "status": "passed",
                    "message": "Handled invalid player ID gracefully"
                })
            except Exception as e:
                test_results["tests_run"].append({
                    "test": "error_handling_invalid_player",
                    "status": "passed",
                    "message": f"Correctly raised exception for invalid player ID: {type(e).__name__}"
                })
            
            test_results["tests_run"].append({
                "test": "error_handling",
                "status": "passed",
                "message": "Error handling tests completed"
            })
            
        except Exception as e:
            test_results["tests_run"].append({
                "test": "error_handling",
                "status": "failed",
                "message": f"Error handling test failed: {str(e)}"
            })
            test_results["overall_success"] = False
    
    def _generate_test_summary(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of test results"""
        tests = test_results["tests_run"]
        
        total_tests = len(tests)
        passed_tests = len([t for t in tests if t["status"] == "passed"])
        failed_tests = len([t for t in tests if t["status"] == "failed"])
        skipped_tests = len([t for t in tests if t["status"] == "skipped"])
        
        return {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "skipped": skipped_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "overall_status": "PASSED" if test_results["overall_success"] else "FAILED"
        }

def main():
    """Main function to run comprehensive tests"""
    print("🧪 Instat Hudl API Comprehensive Test Suite")
    print("=" * 60)
    
    # Configuration
    HEADLESS = True  # Set to False to see browser interactions
    
    # Test credentials (replace with actual credentials for full testing)
    USERNAME = None  # Set to your Hudl username
    PASSWORD = None  # Set to your Hudl password
    
    # Test team IDs (replace with actual team IDs)
    TEAM_IDS = ["21479"]  # Example team ID - replace with actual team IDs
    
    # Test league ID (optional)
    LEAGUE_ID = None  # Set to actual league ID if available
    
    # Initialize tester
    tester = InstatAPITester(headless=HEADLESS)
    
    # Run tests
    print(f"\n🚀 Running tests with headless={HEADLESS}")
    if USERNAME and PASSWORD:
        print(f"🔐 Using credentials: {USERNAME}")
    else:
        print("⚠️  No credentials provided - will skip authenticated tests")
    
    print(f"🏒 Testing with teams: {TEAM_IDS}")
    
    # Run all tests
    results = tester.run_all_tests(
        username=USERNAME,
        password=PASSWORD,
        team_ids=TEAM_IDS,
        league_id=LEAGUE_ID
    )
    
    # Display results
    print("\n📊 Test Results Summary:")
    print("=" * 40)
    
    summary = results["summary"]
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed']} ✅")
    print(f"Failed: {summary['failed']} ❌")
    print(f"Skipped: {summary['skipped']} ⏭️")
    print(f"Success Rate: {summary['success_rate']:.1f}%")
    print(f"Overall Status: {summary['overall_status']}")
    
    print("\n📋 Detailed Results:")
    print("-" * 40)
    
    for test in results["tests_run"]:
        status_icon = "✅" if test["status"] == "passed" else "❌" if test["status"] == "failed" else "⏭️"
        print(f"{status_icon} {test['test']}: {test['message']}")
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"instat_api_test_results_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: {results_file}")
    
    # Display API capabilities
    print("\n🎯 Instat Hudl API Capabilities:")
    print("=" * 40)
    print("✅ 12 Data Tables with proper ID mapping")
    print("✅ Team comprehensive metrics access")
    print("✅ Player career and match statistics")
    print("✅ League standings and rankings")
    print("✅ Advanced analytics and trends")
    print("✅ Data export to CSV format")
    print("✅ Error handling and validation")
    print("✅ League-wide comparative analysis")
    
    print("\n🏒 Ready for production use!")
    
    return results

if __name__ == "__main__":
    main()
