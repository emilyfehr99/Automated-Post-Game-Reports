#!/usr/bin/env python3
import json
import argparse
from pathlib import Path

def generate_report(team_a, team_b):
    metrics_path = Path('data/team_advanced_metrics.json')
    edge_path = Path('data/team_edge_profiles.json')
    
    if not metrics_path.exists() or not edge_path.exists():
        print("❌ Error: Missing high-fidelity data. Run a backfill and edge scrape first.")
        return

    with open(metrics_path) as f:
        metrics = json.load(f)
    with open(edge_path) as f:
        edge = json.load(f)

    def get_team_data(abbrev):
        t = metrics['teams'].get(abbrev, {})
        e = edge.get(abbrev, {})
        g_list = [g for g in metrics['goalies'].values() if g['team'] == abbrev]
        starter = sorted(g_list, key=lambda x: x['games'], reverse=True)[0] if g_list else {}
        return t, e, starter

    m1, e1, g1 = get_team_data(team_a)
    m2, e2, g2 = get_team_data(team_b)

    if not m1 or not m2:
        print(f"❌ Error: Missing data for {team_a} or {team_b}.")
        return

    print(f"\n# 🏅 Strategic Pre-Series Report: {team_a} vs {team_b}")
    print(f"**High-Fidelity Tactical Breakdown | 2026 Stanley Cup Playoffs**")
    print("-" * 60)

    print(f"\n## 🛡️  {team_a} Strategic Keys to Victory")
    
    # 1. Persistence & Transition
    if m1.get('avg_en_to_s', 0) > m2.get('avg_en_to_s', 0) + 2:
        print(f"> [!TIP]\n> **EXPLOIT PERSISTENCE**: {team_a} possesses an elite cycle advantage (avg {m1.get('avg_en_to_s'):.1f}s). Trap {team_b} in long shifts to exhaust their defensive rotation.")
    
    if e1.get('avg_top_speed', 0) > e2.get('avg_top_speed', 0) + 0.3:
        print(f"> [!IMPORTANT]\n> **PULL INTO TRACK MEET**: {team_a} has a definitive speed edge ({e1.get('avg_top_speed'):.1f} mph). Force high-event transition hockey to expose {team_b}'s recovery speed.")

    # 2. Defensive Integrity (Vulnerability Mapping)
    if m2.get('hd_pizzas_per_game', 0) > 2.4:
        print(f"> [!CAUTION]\n> **ATTACK THE SLOT**: {team_b} is prone to high-danger turnovers (avg {m2.get('hd_pizzas_per_game'):.2f} slot-giveaways/gm). Aggressive forecheck in the high slot will yield high-danger looks.")

    # 3. Goaltending Battle
    if g1.get('gsax_per_game', 0) > g2.get('gsax_per_game', 0) + 0.1:
        print(f"> [!NOTE]\n> **GOALIE EDGE**: {g1.get('name')} is significantly out-performing the field ({g1.get('gsax_per_game'):.3f} GSAX/gm). Favor high-danger volume; the math favors you in the expected save battle.")

    print(f"\n---")
    print(f"🔗 **Data Layers Active**: xG-based GSAX, Tactical PBP Sequences (ENtoS/EXtoEN), NHL Edge Telemetry")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a high-fidelity pre-series strategic report.")
    parser.add_argument("--home", required=True, help="Home team abbreviation")
    parser.add_argument("--away", required=True, help="Away team abbreviation")
    args = parser.parse_args()
    
    generate_report(args.home.upper(), args.away.upper())
