#!/usr/bin/env python3
"""
Hudl Instat Data Mapping
Maps where each comprehensive metric comes from in the actual Hudl Instat tabs
"""

from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class MetricSource:
    """Represents where a metric comes from in Hudl Instat"""
    tab: str
    section: str
    description: str
    export_format: str
    priority: int

class HudlInstatDataMapper:
    """Maps comprehensive player metrics to their Hudl Instat sources"""
    
    def __init__(self):
        """Initialize the data mapper"""
        self.metric_sources = self._define_metric_sources()
    
    def _define_metric_sources(self) -> Dict[str, MetricSource]:
        """Define where each comprehensive metric comes from"""
        
        sources = {
            # Main Statistics - from SKATERS tab
            "time_on_ice": MetricSource("SKATERS", "Main Stats", "Time on ice per game", "CSV", 1),
            "games_played": MetricSource("SKATERS", "Main Stats", "Total games played", "CSV", 1),
            "all_shifts": MetricSource("SKATERS", "Main Stats", "Total shifts taken", "CSV", 1),
            "goals": MetricSource("SKATERS", "Main Stats", "Goals scored", "CSV", 1),
            "first_assist": MetricSource("SKATERS", "Main Stats", "Primary assists", "CSV", 1),
            "second_assist": MetricSource("SKATERS", "Main Stats", "Secondary assists", "CSV", 1),
            "assists": MetricSource("SKATERS", "Main Stats", "Total assists", "CSV", 1),
            "puck_touches": MetricSource("SKATERS", "Main Stats", "Puck touches", "CSV", 1),
            "points": MetricSource("SKATERS", "Main Stats", "Total points", "CSV", 1),
            "plus_minus": MetricSource("SKATERS", "Main Stats", "Plus/minus rating", "CSV", 1),
            "plus": MetricSource("SKATERS", "Main Stats", "Plus events", "CSV", 1),
            "minus": MetricSource("SKATERS", "Main Stats", "Minus events", "CSV", 1),
            "scoring_chances": MetricSource("SKATERS", "Main Stats", "Scoring chances created", "CSV", 1),
            "team_goals_when_on_ice": MetricSource("SKATERS", "Main Stats", "Team goals when on ice", "CSV", 1),
            "opponent_goals_when_on_ice": MetricSource("SKATERS", "Main Stats", "Opponent goals when on ice", "CSV", 1),
            "penalties": MetricSource("SKATERS", "Main Stats", "Penalties taken", "CSV", 1),
            "penalties_drawn": MetricSource("SKATERS", "Main Stats", "Penalties drawn", "CSV", 1),
            "penalty_time": MetricSource("SKATERS", "Main Stats", "Total penalty minutes", "CSV", 1),
            
            # Faceoffs - from SKATERS tab
            "faceoffs": MetricSource("SKATERS", "Faceoff Stats", "Total faceoffs taken", "CSV", 1),
            "faceoffs_won": MetricSource("SKATERS", "Faceoff Stats", "Faceoffs won", "CSV", 1),
            "faceoffs_lost": MetricSource("SKATERS", "Faceoff Stats", "Faceoffs lost", "CSV", 1),
            "faceoffs_won_percentage": MetricSource("SKATERS", "Faceoff Stats", "Faceoff win percentage", "CSV", 1),
            "faceoffs_in_dz": MetricSource("SKATERS", "Zone Faceoffs", "Faceoffs in defensive zone", "CSV", 2),
            "faceoffs_in_nz": MetricSource("SKATERS", "Zone Faceoffs", "Faceoffs in neutral zone", "CSV", 2),
            "faceoffs_in_oz": MetricSource("SKATERS", "Zone Faceoffs", "Faceoffs in offensive zone", "CSV", 2),
            
            # Physical Play - from SKATERS tab
            "hits": MetricSource("SKATERS", "Physical Play", "Hits delivered", "CSV", 1),
            "hits_against": MetricSource("SKATERS", "Physical Play", "Hits received", "CSV", 1),
            "error_leading_to_goal": MetricSource("SKATERS", "Physical Play", "Errors leading to goals", "CSV", 1),
            "dump_ins": MetricSource("SKATERS", "Physical Play", "Dump-ins", "CSV", 1),
            "dump_outs": MetricSource("SKATERS", "Physical Play", "Dump-outs", "CSV", 1),
            
            # Shooting - from SKATERS tab
            "shots": MetricSource("SKATERS", "Shooting Stats", "Total shots", "CSV", 1),
            "shots_on_goal": MetricSource("SKATERS", "Shooting Stats", "Shots on goal", "CSV", 1),
            "blocked_shots": MetricSource("SKATERS", "Shooting Stats", "Blocked shots", "CSV", 1),
            "missed_shots": MetricSource("SKATERS", "Shooting Stats", "Missed shots", "CSV", 1),
            "shots_on_goal_percentage": MetricSource("SKATERS", "Shooting Stats", "Shooting percentage", "CSV", 1),
            "slapshot": MetricSource("SKATERS", "Shot Types", "Slap shots", "CSV", 2),
            "wrist_shot": MetricSource("SKATERS", "Shot Types", "Wrist shots", "CSV", 2),
            "shootouts": MetricSource("SKATERS", "Shootouts", "Shootout attempts", "CSV", 2),
            "shootouts_scored": MetricSource("SKATERS", "Shootouts", "Shootout goals", "CSV", 2),
            "shootouts_missed": MetricSource("SKATERS", "Shootouts", "Shootout misses", "CSV", 2),
            "one_on_one_shots": MetricSource("SKATERS", "Situations", "1-on-1 shots", "CSV", 2),
            "one_on_one_goals": MetricSource("SKATERS", "Situations", "1-on-1 goals", "CSV", 2),
            "power_play_shots": MetricSource("SKATERS", "Situations", "Power play shots", "CSV", 2),
            "short_handed_shots": MetricSource("SKATERS", "Situations", "Short-handed shots", "CSV", 2),
            "shots_5v5": MetricSource("SKATERS", "Situations", "5v5 shots", "CSV", 2),
            "positional_attack_shots": MetricSource("SKATERS", "Attack Types", "Positional attack shots", "CSV", 2),
            "counter_attack_shots": MetricSource("SKATERS", "Attack Types", "Counter-attack shots", "CSV", 2),
            
            # Puck Battles - from SKATERS tab
            "puck_battles": MetricSource("SKATERS", "Puck Battles", "Total puck battles", "CSV", 1),
            "puck_battles_won": MetricSource("SKATERS", "Puck Battles", "Puck battles won", "CSV", 1),
            "puck_battles_won_percentage": MetricSource("SKATERS", "Puck Battles", "Puck battle win %", "CSV", 1),
            "puck_battles_in_dz": MetricSource("SKATERS", "Puck Battles", "Puck battles in DZ", "CSV", 2),
            "puck_battles_in_nz": MetricSource("SKATERS", "Puck Battles", "Puck battles in NZ", "CSV", 2),
            "puck_battles_in_oz": MetricSource("SKATERS", "Puck Battles", "Puck battles in OZ", "CSV", 2),
            "shots_blocking": MetricSource("SKATERS", "Puck Battles", "Shots blocked", "CSV", 2),
            "dekes": MetricSource("SKATERS", "Puck Battles", "Deke attempts", "CSV", 2),
            "dekes_successful": MetricSource("SKATERS", "Puck Battles", "Successful dekes", "CSV", 2),
            "dekes_unsuccessful": MetricSource("SKATERS", "Puck Battles", "Unsuccessful dekes", "CSV", 2),
            
            # Recoveries and Losses - from SKATERS tab
            "takeaways": MetricSource("SKATERS", "Recoveries", "Takeaways", "CSV", 1),
            "takeaways_in_dz": MetricSource("SKATERS", "Recoveries", "Takeaways in DZ", "CSV", 2),
            "takeaways_in_nz": MetricSource("SKATERS", "Recoveries", "Takeaways in NZ", "CSV", 2),
            "takeaways_in_oz": MetricSource("SKATERS", "Recoveries", "Takeaways in OZ", "CSV", 2),
            "puck_losses": MetricSource("SKATERS", "Recoveries", "Puck losses", "CSV", 1),
            "puck_losses_in_dz": MetricSource("SKATERS", "Recoveries", "Puck losses in DZ", "CSV", 2),
            "puck_losses_in_nz": MetricSource("SKATERS", "Recoveries", "Puck losses in NZ", "CSV", 2),
            "puck_losses_in_oz": MetricSource("SKATERS", "Recoveries", "Puck losses in OZ", "CSV", 2),
            "puck_retrievals_after_shots": MetricSource("SKATERS", "Recoveries", "Puck retrievals after shots", "CSV", 2),
            "opponent_dump_in_retrievals": MetricSource("SKATERS", "Recoveries", "Opponent dump-in retrievals", "CSV", 2),
            "loose_puck_recovery": MetricSource("SKATERS", "Recoveries", "Loose puck recovery", "CSV", 2),
            "ev_dz_retrievals": MetricSource("SKATERS", "Recoveries", "EV DZ retrievals", "CSV", 2),
            "ev_oz_retrievals": MetricSource("SKATERS", "Recoveries", "EV OZ retrievals", "CSV", 2),
            "power_play_retrievals": MetricSource("SKATERS", "Recoveries", "Power play retrievals", "CSV", 2),
            "penalty_kill_retrievals": MetricSource("SKATERS", "Recoveries", "Penalty kill retrievals", "CSV", 2),
            
            # Special Teams - from SKATERS tab
            "power_play": MetricSource("SKATERS", "Special Teams", "Power play opportunities", "CSV", 1),
            "successful_power_play": MetricSource("SKATERS", "Special Teams", "Successful power plays", "CSV", 1),
            "power_play_time": MetricSource("SKATERS", "Special Teams", "Power play time", "CSV", 1),
            "short_handed": MetricSource("SKATERS", "Special Teams", "Short-handed situations", "CSV", 1),
            "penalty_killing": MetricSource("SKATERS", "Special Teams", "Penalty killing", "CSV", 1),
            "short_handed_time": MetricSource("SKATERS", "Special Teams", "Short-handed time", "CSV", 1),
            
            # Expected Goals - from SKATERS tab
            "xg": MetricSource("SKATERS", "Expected Goals", "Expected goals", "CSV", 1),
            "xg_per_shot": MetricSource("SKATERS", "Expected Goals", "xG per shot", "CSV", 1),
            "xg_expected_goals": MetricSource("SKATERS", "Expected Goals", "Expected goals total", "CSV", 1),
            "xg_per_goal": MetricSource("SKATERS", "Expected Goals", "xG per goal", "CSV", 1),
            "net_xg": MetricSource("SKATERS", "Expected Goals", "Net xG", "CSV", 1),
            "team_xg_when_on_ice": MetricSource("SKATERS", "Expected Goals", "Team xG when on ice", "CSV", 1),
            "opponent_xg_when_on_ice": MetricSource("SKATERS", "Expected Goals", "Opponent xG when on ice", "CSV", 1),
            "xg_conversion": MetricSource("SKATERS", "Expected Goals", "xG conversion", "CSV", 1),
            
            # Passes - from SKATERS tab
            "passes": MetricSource("SKATERS", "Passing", "Total passes", "CSV", 1),
            "accurate_passes": MetricSource("SKATERS", "Passing", "Accurate passes", "CSV", 1),
            "accurate_passes_percentage": MetricSource("SKATERS", "Passing", "Pass accuracy %", "CSV", 1),
            "passes_to_slot": MetricSource("SKATERS", "Passing", "Passes to slot", "CSV", 2),
            "pre_shots_passes": MetricSource("SKATERS", "Passing", "Pre-shot passes", "CSV", 2),
            "pass_receptions": MetricSource("SKATERS", "Passing", "Pass receptions", "CSV", 2),
            
            # Entries and Breakouts - from SKATERS tab
            "entries": MetricSource("SKATERS", "Zone Play", "Zone entries", "CSV", 1),
            "entries_via_pass": MetricSource("SKATERS", "Zone Play", "Entries via pass", "CSV", 2),
            "entries_via_dump_in": MetricSource("SKATERS", "Zone Play", "Entries via dump in", "CSV", 2),
            "entries_via_stickhandling": MetricSource("SKATERS", "Zone Play", "Entries via stickhandling", "CSV", 2),
            "breakouts": MetricSource("SKATERS", "Zone Play", "Zone breakouts", "CSV", 1),
            "breakouts_via_pass": MetricSource("SKATERS", "Zone Play", "Breakouts via pass", "CSV", 2),
            "breakouts_via_dump_out": MetricSource("SKATERS", "Zone Play", "Breakouts via dump out", "CSV", 2),
            "breakouts_via_stickhandling": MetricSource("SKATERS", "Zone Play", "Breakouts via stickhandling", "CSV", 2),
            
            # Advanced Statistics - from SKATERS tab
            "corsi": MetricSource("SKATERS", "Advanced Stats", "Corsi", "CSV", 1),
            "corsi_minus": MetricSource("SKATERS", "Advanced Stats", "Corsi-", "CSV", 1),
            "corsi_plus": MetricSource("SKATERS", "Advanced Stats", "Corsi+", "CSV", 1),
            "corsi_for_percentage": MetricSource("SKATERS", "Advanced Stats", "Corsi for %", "CSV", 1),
            "fenwick_for": MetricSource("SKATERS", "Advanced Stats", "Fenwick for", "CSV", 1),
            "fenwick_against": MetricSource("SKATERS", "Advanced Stats", "Fenwick against", "CSV", 1),
            "fenwick_for_percentage": MetricSource("SKATERS", "Advanced Stats", "Fenwick for %", "CSV", 1),
            
            # Playtime Phases - from SKATERS tab
            "playing_in_attack": MetricSource("SKATERS", "Playtime", "Time in attack", "CSV", 2),
            "playing_in_defense": MetricSource("SKATERS", "Playtime", "Time in defense", "CSV", 2),
            "oz_possession": MetricSource("SKATERS", "Playtime", "OZ possession", "CSV", 2),
            "nz_possession": MetricSource("SKATERS", "Playtime", "NZ possession", "CSV", 2),
            "dz_possession": MetricSource("SKATERS", "Playtime", "DZ possession", "CSV", 2),
            
            # Scoring Chances - from SKATERS tab
            "scoring_chances_total": MetricSource("SKATERS", "Scoring Chances", "Total scoring chances", "CSV", 1),
            "scoring_chances_scored": MetricSource("SKATERS", "Scoring Chances", "Scoring chances scored", "CSV", 1),
            "scoring_chances_missed": MetricSource("SKATERS", "Scoring Chances", "Scoring chances missed", "CSV", 1),
            "scoring_chances_saved": MetricSource("SKATERS", "Scoring Chances", "Scoring chances saved", "CSV", 1),
            "scoring_chances_percentage": MetricSource("SKATERS", "Scoring Chances", "Scoring chances %", "CSV", 1),
            "inner_slot_shots_total": MetricSource("SKATERS", "Slot Shots", "Inner slot shots total", "CSV", 2),
            "inner_slot_shots_scored": MetricSource("SKATERS", "Slot Shots", "Inner slot shots scored", "CSV", 2),
            "inner_slot_shots_missed": MetricSource("SKATERS", "Slot Shots", "Inner slot shots missed", "CSV", 2),
            "inner_slot_shots_saved": MetricSource("SKATERS", "Slot Shots", "Inner slot shots saved", "CSV", 2),
            "outer_slot_shots_total": MetricSource("SKATERS", "Slot Shots", "Outer slot shots total", "CSV", 2),
            "outer_slot_shots_scored": MetricSource("SKATERS", "Slot Shots", "Outer slot shots scored", "CSV", 2),
            "outer_slot_shots_missed": MetricSource("SKATERS", "Slot Shots", "Outer slot shots missed", "CSV", 2),
            "outer_slot_shots_saved": MetricSource("SKATERS", "Slot Shots", "Outer slot shots saved", "CSV", 2),
            "blocked_shots_from_slot": MetricSource("SKATERS", "Slot Shots", "Blocked shots from slot", "CSV", 2),
            "blocked_shots_outside_slot": MetricSource("SKATERS", "Slot Shots", "Blocked shots outside slot", "CSV", 2),
            
            # Passport - from SKATERS tab
            "date_of_birth": MetricSource("SKATERS", "Player Info", "Date of birth", "CSV", 1),
            "nationality": MetricSource("SKATERS", "Player Info", "Nationality", "CSV", 1),
            "national_team": MetricSource("SKATERS", "Player Info", "National team", "CSV", 1),
            "height": MetricSource("SKATERS", "Player Info", "Height", "CSV", 1),
            "weight": MetricSource("SKATERS", "Player Info", "Weight", "CSV", 1),
            "contract": MetricSource("SKATERS", "Player Info", "Contract", "CSV", 1),
            "active_hand": MetricSource("SKATERS", "Player Info", "Active hand", "CSV", 1),
        }
        
        return sources
    
    def get_metrics_by_tab(self) -> Dict[str, List[str]]:
        """Get all metrics organized by Hudl Instat tab"""
        tab_metrics = {}
        
        for metric, source in self.metric_sources.items():
            if source.tab not in tab_metrics:
                tab_metrics[source.tab] = []
            tab_metrics[source.tab].append(metric)
        
        return tab_metrics
    
    def get_metrics_by_priority(self) -> Dict[int, List[str]]:
        """Get all metrics organized by priority"""
        priority_metrics = {}
        
        for metric, source in self.metric_sources.items():
            if source.priority not in priority_metrics:
                priority_metrics[source.priority] = []
            priority_metrics[source.priority].append(metric)
        
        return priority_metrics
    
    def get_tab_data_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Get data requirements for each tab"""
        tab_requirements = {}
        
        for tab in ["OVERVIEW", "GAMES", "SKATERS", "GOALIES", "LINES", "SHOT MAP", "FACEOFFS", "EPISODES SEARCH"]:
            tab_metrics = [metric for metric, source in self.metric_sources.items() if source.tab == tab]
            
            tab_requirements[tab] = {
                "metrics_count": len(tab_metrics),
                "metrics": tab_metrics,
                "sections": list(set(source.section for metric, source in self.metric_sources.items() if source.tab == tab)),
                "export_formats": list(set(source.export_format for metric, source in self.metric_sources.items() if source.tab == tab)),
                "priority_1_metrics": len([m for m in tab_metrics if self.metric_sources[m].priority == 1]),
                "priority_2_metrics": len([m for m in tab_metrics if self.metric_sources[m].priority == 2])
            }
        
        return tab_requirements
    
    def get_comprehensive_data_plan(self) -> Dict[str, Any]:
        """Get a comprehensive data collection plan"""
        return {
            "total_metrics": len(self.metric_sources),
            "tabs_required": list(set(source.tab for source in self.metric_sources.values())),
            "tab_requirements": self.get_tab_data_requirements(),
            "priority_breakdown": self.get_metrics_by_priority(),
            "data_sources": {
                metric: {
                    "tab": source.tab,
                    "section": source.section,
                    "description": source.description,
                    "export_format": source.export_format,
                    "priority": source.priority
                }
                for metric, source in self.metric_sources.items()
            }
        }

def main():
    """Main function to demonstrate the data mapping"""
    print("🏒 Hudl Instat Comprehensive Data Mapping")
    print("=" * 60)
    
    mapper = HudlInstatDataMapper()
    plan = mapper.get_comprehensive_data_plan()
    
    print(f"📊 Total Metrics: {plan['total_metrics']}")
    print(f"📋 Tabs Required: {', '.join(plan['tabs_required'])}")
    print()
    
    print("📋 Tab Requirements:")
    print("-" * 40)
    for tab, requirements in plan['tab_requirements'].items():
        print(f"{tab}:")
        print(f"  Metrics: {requirements['metrics_count']}")
        print(f"  Sections: {', '.join(requirements['sections'])}")
        print(f"  Priority 1: {requirements['priority_1_metrics']}")
        print(f"  Priority 2: {requirements['priority_2_metrics']}")
        print()
    
    print("🎯 Priority Breakdown:")
    print("-" * 40)
    for priority, metrics in plan['priority_breakdown'].items():
        print(f"Priority {priority}: {len(metrics)} metrics")
        if priority == 1:
            print(f"  Examples: {', '.join(metrics[:5])}...")
        print()
    
    print("✅ This shows exactly where each metric comes from in Hudl Instat!")

if __name__ == "__main__":
    main()
