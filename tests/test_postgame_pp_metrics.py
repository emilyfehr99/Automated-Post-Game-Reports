"""NHL postgame period/Final metrics must match NHL right-rail logic."""

from __future__ import annotations

from pdf_report_generator import PostGameReportGenerator


def test_pp_advantage_parsing():
    assert PostGameReportGenerator._pp_advantage_from_situation("1451", "home") == 1
    assert PostGameReportGenerator._pp_advantage_from_situation("1451", "away") == 0
    assert PostGameReportGenerator._pp_advantage_from_situation("1541", "away") == 1
    assert PostGameReportGenerator._pp_advantage_from_situation("1551", "home") == 0
    assert PostGameReportGenerator._pp_advantage_from_situation("1560", "home") == 0  # EN, not PP


def test_reconcile_sparse_pbp_uses_official():
    gen = PostGameReportGenerator.__new__(PostGameReportGenerator)
    game_data = {
        "right_rail": {
            "teamGameStats": [
                {"category": "powerPlay", "awayValue": "1/4", "homeValue": "2/5"},
            ]
        }
    }
    g, a = gen._reconcile_pp_with_official([0, 0, 0], [0, 0, 0], game_data, "away")
    assert sum(g) == 1 and sum(a) == 4
    g, a = gen._reconcile_pp_with_official([0, 0, 0], [0, 0, 0], game_data, "home")
    assert sum(g) == 2 and sum(a) == 5


def test_reconcile_trims_period_boundary_overcount():
    gen = PostGameReportGenerator.__new__(PostGameReportGenerator)
    game_data = {
        "right_rail": {
            "teamGameStats": [
                {"category": "powerPlay", "awayValue": "0/3", "homeValue": "1/6"},
            ]
        }
    }
    g, a = gen._reconcile_pp_with_official([0, 1, 0], [2, 6, 2], game_data, "home")
    assert sum(g) == 1
    assert sum(a) == 6


def test_final_counting_prefers_right_rail():
    gen = PostGameReportGenerator.__new__(PostGameReportGenerator)
    game_data = {
        "right_rail": {
            "teamGameStats": [
                {"category": "sog", "awayValue": 28, "homeValue": 24},
                {"category": "pim", "awayValue": 16, "homeValue": 18},
                {"category": "blockedShots", "awayValue": 17, "homeValue": 11},
                {"category": "hits", "awayValue": 18, "homeValue": 29},
                {"category": "giveaways", "awayValue": 14, "homeValue": 18},
                {"category": "takeaways", "awayValue": 4, "homeValue": 2},
                {"category": "powerPlay", "awayValue": "0/4", "homeValue": "0/3"},
                {"category": "faceoffWins", "awayValue": "28/55", "homeValue": "27/55"},
            ]
        }
    }
    period = {
        "shots": [10, 10, 5],
        "pim": [2, 2, 2],
        "hits": [5, 5, 5],
        "bs": [1, 1, 1],
        "gv": [1, 1, 1],
        "tk": [1, 0, 0],
        "pp_goals": [0, 0, 0],
        "pp_attempts": [1, 1, 1],
        "fo_wins": [10, 10, 5],
        "fo_total": [20, 20, 10],
        "fo_pct": [50.0, 50.0, 50.0],
    }
    final = gen._final_counting_stats(game_data, "away", period, None)
    assert final["shots"] == 28
    assert final["pim"] == 16
    assert final["bs"] == 17
    assert final["pp"] == "0/4"
    assert abs(final["fo_pct"] - (28 / 55 * 100)) < 0.05


def test_weighted_fo_pct_not_mean_of_periods():
    gen = PostGameReportGenerator.__new__(PostGameReportGenerator)
    period = {"fo_wins": [8, 0], "fo_total": [10, 2], "fo_pct": [80.0, 0.0]}
    assert abs(gen._weighted_fo_pct(period) - (8 / 12 * 100)) < 0.01
    naive_mean = sum(period["fo_pct"]) / 2
    assert abs(naive_mean - 40.0) < 0.01
    assert abs(gen._weighted_fo_pct(period) - naive_mean) > 1.0


def test_weighted_corsi_pct_not_mean_of_periods():
    gen = PostGameReportGenerator.__new__(PostGameReportGenerator)
    period = {
        "corsi_for": [40, 5],
        "corsi_against": [10, 20],
        "corsi_pct": [80.0, 20.0],
    }
    # Weighted: 45/(45+30)=60%; naive mean of pcts = 50%
    assert abs(gen._weighted_corsi_pct(period) - 60.0) < 0.01
