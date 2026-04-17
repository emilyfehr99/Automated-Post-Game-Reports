import requests
import json
import time
import random
import sys
import argparse
import hashlib
import math
from datetime import datetime, timezone
from pathlib import Path
from collections import Counter, defaultdict

# Allow running locally without needing PYTHONPATH set
_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_DIR = _SCRIPT_DIR.parent
sys.path.insert(0, str(_PROJECT_DIR))
sys.path.insert(0, str(_PROJECT_DIR / "models"))

from playoff_predictor import PlayoffSeriesPredictor

BASE_URL = 'https://api-web.nhle.com/v1'

def fetch_standings(date: str = "now"):
    try:
        r = requests.get(f'{BASE_URL}/standings/{date}', timeout=20)
        if r.status_code == 200:
            return r.json().get('standings', [])
    except:
        return []
    return []

def build_round1_bracket_from_standings(standings):
    east = [s for s in standings if s['conferenceAbbrev'] == 'E']
    west = [s for s in standings if s['conferenceAbbrev'] == 'W']
    
    def get_conference_bracket(conf_teams):
        divisions = sorted(list(set([t['divisionAbbrev'] for t in conf_teams])))
        div_teams = {d: sorted([t for t in conf_teams if t['divisionAbbrev'] == d], 
                               key=lambda x: x['points'], reverse=True) for d in divisions}
        
        qualifier_ids = set()
        for d in divisions:
            top3 = div_teams[d][:3]
            for t in top3: qualifier_ids.add(t['teamAbbrev']['default'])
            
        rem_teams = sorted([t for t in conf_teams if t['teamAbbrev']['default'] not in qualifier_ids], 
                           key=lambda x: x['points'], reverse=True)
        wildcards = rem_teams[:2]
        
        div_winners = sorted([div_teams[d][0] for d in divisions], key=lambda x: x['points'], reverse=True)
        
        bracket = []
        # Match 1: DivWinner1 vs WC2
        bracket.append({
            "away": wildcards[1]['teamAbbrev']['default'],
            "home": div_winners[0]['teamAbbrev']['default'],
            "label": "R1-M1",
        })
        # Match 2: DivWinner1's Division 2nd vs 3rd
        dw1_div = div_winners[0]['divisionAbbrev']
        bracket.append({
            "away": div_teams[dw1_div][2]['teamAbbrev']['default'],
            "home": div_teams[dw1_div][1]['teamAbbrev']['default'],
            "label": f"R1-{dw1_div}2v3",
        })
        # Match 3: DivWinner2 vs WC1
        bracket.append({
            "away": wildcards[0]['teamAbbrev']['default'],
            "home": div_winners[1]['teamAbbrev']['default'],
            "label": "R1-M2",
        })
        # Match 4: DivWinner2's Division 2nd vs 3rd
        dw2_div = div_winners[1]['divisionAbbrev']
        bracket.append({
            "away": div_teams[dw2_div][2]['teamAbbrev']['default'],
            "home": div_teams[dw2_div][1]['teamAbbrev']['default'],
            "label": f"R1-{dw2_div}2v3",
        })
            
        return bracket

    return {"East": get_conference_bracket(east), "West": get_conference_bracket(west)}

def fetch_playoff_series_state(season: str):
    """
    Returns mapping keyed by frozenset({teamA, teamB}) -> {teamA: winsA, teamB: winsB}

    Uses NHL web endpoint:
      GET /v1/playoff-series/carousel/{season}/
    where season is like 20252026.
    """
    url = f"{BASE_URL}/playoff-series/carousel/{season}/"
    try:
        r = requests.get(url, timeout=20)
        if r.status_code != 200:
            return {}
        data = r.json()
    except Exception:
        return {}

    series_map = {}

    # The payload shape can vary; we scan for likely series objects with two teams + wins.
    def walk(obj):
        if isinstance(obj, dict):
            yield obj
            for v in obj.values():
                yield from walk(v)
        elif isinstance(obj, list):
            for x in obj:
                yield from walk(x)

    for node in walk(data):
        # try common shapes
        t1 = node.get("team1") if isinstance(node, dict) else None
        t2 = node.get("team2") if isinstance(node, dict) else None
        if not isinstance(t1, dict) or not isinstance(t2, dict):
            continue

        ab1 = t1.get("abbrev") or (t1.get("teamAbbrev", {}) if isinstance(t1.get("teamAbbrev"), dict) else {}).get("default")
        ab2 = t2.get("abbrev") or (t2.get("teamAbbrev", {}) if isinstance(t2.get("teamAbbrev"), dict) else {}).get("default")

        if not ab1 or not ab2:
            continue

        w1 = t1.get("wins") or t1.get("seriesWins") or t1.get("winCount")
        w2 = t2.get("wins") or t2.get("seriesWins") or t2.get("winCount")

        try:
            w1 = int(w1)
            w2 = int(w2)
        except Exception:
            continue

        key = frozenset({ab1, ab2})
        # Prefer the largest total-wins entry if duplicates exist
        existing = series_map.get(key)
        if not existing or (existing.get(ab1, 0) + existing.get(ab2, 0)) < (w1 + w2):
            series_map[key] = {ab1: w1, ab2: w2}

    return series_map


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run_tournament_monte_carlo(iterations=100000, season: str = "20252026", bracket_out: Path | None = None, predictions_out: Path | None = None):
    predictor = PlayoffSeriesPredictor()
    standings = fetch_standings("now")
    if not standings:
        print('Error fetching standings.')
        return
        
    bracket = build_round1_bracket_from_standings(standings)

    if bracket_out:
        bracket_out.parent.mkdir(parents=True, exist_ok=True)
        with bracket_out.open("w") as f:
            json.dump(bracket, f, indent=2)
    
    # Trackers for advancement
    advancement = defaultdict(lambda: Counter()) # team -> {round_number: wins}

    # Track opponent paths by round: opponent_counts[round][team][opp] += 1
    opponent_counts = {
        1: defaultdict(lambda: Counter()),
        2: defaultdict(lambda: Counter()),
        3: defaultdict(lambda: Counter()),
        4: defaultdict(lambda: Counter()),
    }
    round_appearances = {
        1: Counter(),
        2: Counter(),
        3: Counter(),
        4: Counter(),
    }
    
    # Pre-cache game win probs to speed up sims
    prob_cache = {}

    series_state = fetch_playoff_series_state(season) if season else {}
        
    def get_series_constants(away, home, round_no: int):
        key = (int(round_no), tuple(sorted([away, home])))
        if key not in prob_cache:
            # Get consistent win probs for this matchup (round-aware priors)
            p_away_at_home = predictor.calculate_game_win_prob(away, home, playoff_round=round_no)
            p_home_at_away = predictor.calculate_game_win_prob(home, away, playoff_round=round_no)
            p_away_at_away = 1 - p_home_at_away
            prob_cache[key] = (away, home, p_away_at_home, p_away_at_away)
        return prob_cache[key]

    def get_series_current_wins(away, home):
        key = frozenset({away, home})
        s = series_state.get(key)
        if not s:
            return 0, 0
        return int(s.get(away, 0)), int(s.get(home, 0))

    def record_matchup(round_no: int, team_a: str, team_b: str):
        opponent_counts[round_no][team_a][team_b] += 1
        opponent_counts[round_no][team_b][team_a] += 1
        round_appearances[round_no][team_a] += 1
        round_appearances[round_no][team_b] += 1

    def get_series_winner(round_no: int, away, home):
        a_team, h_team, p_ath, p_ata = get_series_constants(away, home, round_no)
        record_matchup(round_no, a_team, h_team)
        
        a_wins, h_wins = get_series_current_wins(a_team, h_team)
        # H-H-A-A-H-A-H
        games_played = a_wins + h_wins
        venues = ['h','h','a','a','h','a','h'][games_played:]
        for venue in venues:
            p = p_ath if venue == 'h' else p_ata
            if random.random() < p:
                a_wins += 1
            else:
                h_wins += 1
            if a_wins == 4 or h_wins == 4:
                winner = a_team if a_wins == 4 else h_team
                return winner

    print(f"🏒 STARTING {iterations:,} TOURNAMENT SIMULATIONS (High-Fidelity xG Mode)...")
    start_time = time.time()
    
    for _ in range(iterations):
        # Round 1 (Division Semis)
        e_r1_winners = [get_series_winner(1, m["away"], m["home"]) for m in bracket["East"]]
        w_r1_winners = [get_series_winner(1, m["away"], m["home"]) for m in bracket["West"]]
        
        for w in e_r1_winners + w_r1_winners: advancement[w][1] += 1
        
        # Round 2 (Division Finals)
        e_r2_winners = [
            get_series_winner(2, e_r1_winners[0], e_r1_winners[1]),
            get_series_winner(2, e_r1_winners[2], e_r1_winners[3])
        ]
        w_r2_winners = [
            get_series_winner(2, w_r1_winners[0], w_r1_winners[1]),
            get_series_winner(2, w_r1_winners[2], w_r1_winners[3])
        ]
        
        for w in e_r2_winners + w_r2_winners: advancement[w][2] += 1
        
        # Round 3 (Conference Finals)
        e_r3_winner = get_series_winner(3, e_r2_winners[0], e_r2_winners[1])
        w_r3_winner = get_series_winner(3, w_r2_winners[0], w_r2_winners[1])
        
        advancement[e_r3_winner][3] += 1
        advancement[w_r3_winner][3] += 1
        
        # Round 4 (Stanley Cup Finals)
        cup_winner = get_series_winner(4, e_r3_winner, w_r3_winner)
        advancement[cup_winner][4] += 1
        
    duration = time.time() - start_time
    print(f"✅ Simulation Complete in {duration:.1f}s\n")
    
    # Reporting
    print(f"{'Team':<5} | {'R2%':>6} | {'R3%':>6} | {'Finals%':>7} | {'CUP WIN%':>9}")
    print("-" * 50)
    
    final_results = []
    for team in advancement:
        stats = advancement[team]
        final_results.append({
            'team': team,
            'r2': stats[1] / iterations,
            'r3': stats[2] / iterations,
            'fin': stats[3] / iterations,
            'cup': stats[4] / iterations
        })
    
    final_results.sort(key=lambda x: x['cup'], reverse=True)
    for res in final_results:
        print(f"{res['team']:<5} | {res['r2']:>6.1%} | {res['r3']:>6.1%} | {res['fin']:>7.1%} | {res['cup']:>9.2%}")

    # Export JSON for consumption
    if predictions_out:
        # Round 1 series odds (computed via simulate_series, respecting current wins)
        series_odds = {"East": [], "West": []}
        for conf in ["East", "West"]:
            for m in bracket[conf]:
                aw = m["away"]
                hm = m["home"]
                a_w, h_w = get_series_current_wins(aw, hm)
                r = predictor.simulate_series(
                    aw,
                    hm,
                    away_wins=a_w,
                    home_wins=h_w,
                    simulations=min(25000, max(5000, iterations // 4)),
                    playoff_round=1,
                )
                series_odds[conf].append({
                    "away": aw,
                    "home": hm,
                    "label": m.get("label"),
                    "current_wins": {"away": a_w, "home": h_w},
                    "away_series_win_prob": r["away_series_win_prob"],
                    "home_series_win_prob": r["home_series_win_prob"],
                    "avg_remaining_games": r.get("avg_remaining_games"),
                    "winner_projection": r.get("winner_projection"),
                })

        predictions_out.parent.mkdir(parents=True, exist_ok=True)

        # Basic provenance for the key input files we expect in repo
        data_dir = Path("data")
        inputs = {}
        for p in [
            data_dir / "season_2025_2026_team_stats.json",
            data_dir / "team_advanced_metrics.json",
            data_dir / "team_edge_profiles.json",
            data_dir / "nhl_edge_data.json",
            data_dir / "cup_prior_current.json",
            data_dir / "reg_season_playoff_round_models_5yr.json",
            data_dir / "reg_season_team_features_current.json",
        ]:
            if p.exists():
                try:
                    inputs[str(p)] = {
                        "mtime_utc": datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).isoformat(),
                        "sha256": _sha256_file(p),
                        "bytes": p.stat().st_size,
                    }
                except Exception:
                    pass

        # Build a full bracket format (structure + Round 1 computed odds).
        # Later rounds are represented structurally by the winner-feeds.
        bracket_tree = {
            "East": {
                "R1": [m for m in bracket["East"]],
                "R2": [
                    {"label": "R2-E1", "feeds_from": ["East.R1[0]", "East.R1[1]"]},
                    {"label": "R2-E2", "feeds_from": ["East.R1[2]", "East.R1[3]"]},
                ],
                "R3": [{"label": "ECF", "feeds_from": ["East.R2[0]", "East.R2[1]"]}],
            },
            "West": {
                "R1": [m for m in bracket["West"]],
                "R2": [
                    {"label": "R2-W1", "feeds_from": ["West.R1[0]", "West.R1[1]"]},
                    {"label": "R2-W2", "feeds_from": ["West.R1[2]", "West.R1[3]"]},
                ],
                "R3": [{"label": "WCF", "feeds_from": ["West.R2[0]", "West.R2[1]"]}],
            },
            "Final": [{"label": "SCF", "feeds_from": ["East.R3[0]", "West.R3[0]"]}],
        }

        # Opponent path distributions by round (conditional on reaching that round)
        opponent_paths = {}
        for rnd in [1, 2, 3, 4]:
            opponent_paths[str(rnd)] = {}
            for team, opp_ctr in opponent_counts[rnd].items():
                denom = round_appearances[rnd].get(team, 0)
                if denom <= 0:
                    continue
                dist = {opp: (cnt / denom) for opp, cnt in opp_ctr.items() if cnt > 0}
                opponent_paths[str(rnd)][team] = dist

        # Path difficulty index:
        # expected difficulty = sum_r E[-log(P(win series vs likely opponent at that round))]
        # higher = harder path
        series_prob_cache = {}

        def get_series_win_prob(team_a: str, team_b: str, rnd: int) -> float:
            # Canonical order: alphabetically first team is always "away" in simulate_series cache.
            away_abbr, home_abbr = sorted([team_a, team_b])
            key = (int(rnd), away_abbr, home_abbr)
            if key not in series_prob_cache:
                a_w, h_w = get_series_current_wins(away_abbr, home_abbr)
                r = predictor.simulate_series(
                    away_abbr,
                    home_abbr,
                    away_wins=a_w,
                    home_wins=h_w,
                    simulations=8000,
                    playoff_round=rnd,
                )
                series_prob_cache[key] = (
                    float(r["away_series_win_prob"]),
                    float(r["home_series_win_prob"]),
                )
            p_away, p_home = series_prob_cache[key]
            return p_away if team_a == away_abbr else p_home

        def team_strength(team: str) -> float:
            # Use the same playoff DNA modifier the model uses (already derived from historical weight calibration)
            try:
                return float(predictor.get_team_playoff_modifier(team))
            except Exception:
                return 0.0

        path_difficulty = {}
        for team in advancement.keys():
            idx = 0.0
            per_round = {}
            for rnd in [1, 2, 3, 4]:
                dist = opponent_paths.get(str(rnd), {}).get(team, {})
                if not dist:
                    continue
                # Expected -log(p) for this round
                e = 0.0
                e_strength = 0.0
                for opp, prob_opp in dist.items():
                    pwin = max(1e-6, min(1 - 1e-6, get_series_win_prob(team, opp, rnd)))
                    e += prob_opp * (-math.log(pwin))
                    e_strength += prob_opp * team_strength(opp)
                per_round[str(rnd)] = {"expected_neglog_p": e, "expected_opp_strength": e_strength}
                idx += e
            path_difficulty[team] = {"index": idx, "by_round": per_round}

        payload = {
            "meta": {
                "generated_at_utc": datetime.now(timezone.utc).isoformat(),
                "iterations": int(iterations),
                "season": season,
                "source": "simulate_2026_playoffs_master.py",
            },
            "bracket": bracket,
            "bracket_tree": bracket_tree,
            "round1_series_odds": series_odds,
            "advancement_probabilities": final_results,
            "opponent_paths": opponent_paths,
            "path_difficulty": path_difficulty,
            "inputs": inputs,
        }
        with predictions_out.open("w") as f:
            json.dump(payload, f, indent=2)
        print(f"\n📝 Wrote playoff predictions JSON -> {predictions_out}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run 2026 NHL playoff bracket simulations and export JSON.")
    parser.add_argument("--iterations", type=int, default=100000)
    parser.add_argument("--season", type=str, default="20252026", help="Season string for playoff-series endpoint (e.g. 20252026)")
    parser.add_argument("--bracket-out", type=str, default="data/official_2026_bracket_current.json")
    parser.add_argument("--predictions-out", type=str, default="data/playoff_predictions_2026.json")
    args = parser.parse_args()

    sys.setrecursionlimit(2000)
    run_tournament_monte_carlo(
        iterations=args.iterations,
        season=args.season,
        bracket_out=Path(args.bracket_out) if args.bracket_out else None,
        predictions_out=Path(args.predictions_out) if args.predictions_out else None,
    )
