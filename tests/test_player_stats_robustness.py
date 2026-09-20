"""Player-level GS inputs: BLK ownership, SOG includes goals, new player IDs."""

from __future__ import annotations

from pdf_report_generator import PostGameReportGenerator


def _gen():
    return PostGameReportGenerator.__new__(PostGameReportGenerator)


def test_localized_name_handles_str_and_dict():
    gen = _gen()
    assert gen._localized_name("Auston") == "Auston"
    assert gen._localized_name({"default": "Matthews"}) == "Matthews"
    assert gen._localized_name(None, "X") == "X"


def test_roster_map_merges_boxscore_and_landing_callups():
    gen = _gen()
    play_by_play = {
        "rosterSpots": [
            {
                "playerId": 1,
                "firstName": {"default": "Known"},
                "lastName": {"default": "Player"},
                "sweaterNumber": 9,
                "positionCode": "C",
                "teamId": 10,
            }
        ],
        "plays": [],
    }
    game_data = {
        "boxscore": {
            "awayTeam": {"id": 10},
            "homeTeam": {"id": 8},
            "playerByGameStats": {
                "awayTeam": {
                    "forwards": [
                        {
                            "playerId": 2,
                            "name": {"default": "Call Up"},
                            "sweaterNumber": 71,
                            "position": "C",
                        }
                    ],
                    "defense": [],
                    "goalies": [],
                },
                "homeTeam": {"forwards": [], "defense": [], "goalies": []},
            },
        },
        "landing": {
            "summary": {
                "scoring": [
                    {
                        "goals": [
                            {
                                "playerId": 3,
                                "firstName": {"default": "Emergency"},
                                "lastName": {"default": "Callup"},
                                "teamId": 10,
                                "assists": [],
                            }
                        ]
                    }
                ]
            }
        },
    }
    roster = gen._create_player_roster_map(play_by_play, game_data)
    assert roster[1]["name"] == "Known Player"
    assert roster[2]["name"] == "Call Up"
    assert roster[3]["name"] == "Emergency Callup"


def test_player_stats_credits_blocker_not_shooter():
    gen = _gen()
    game_data = {
        "boxscore": {
            "awayTeam": {"id": 10, "abbrev": "TOR"},
            "homeTeam": {"id": 8, "abbrev": "MTL"},
        },
        "play_by_play": {
            "rosterSpots": [
                {
                    "playerId": 100,
                    "firstName": {"default": "Block"},
                    "lastName": {"default": "Er"},
                    "sweaterNumber": 2,
                    "positionCode": "D",
                    "teamId": 10,
                },
                {
                    "playerId": 200,
                    "firstName": {"default": "Shoot"},
                    "lastName": {"default": "Er"},
                    "sweaterNumber": 9,
                    "positionCode": "C",
                    "teamId": 8,
                },
            ],
            "plays": [
                {
                    "typeDescKey": "blocked-shot",
                    "details": {
                        "eventOwnerTeamId": 8,  # shooter team
                        "shootingPlayerId": 200,
                        "blockingPlayerId": 100,
                    },
                }
            ],
        },
    }
    away = gen._calculate_player_stats_from_play_by_play(game_data, "awayTeam")
    home = gen._calculate_player_stats_from_play_by_play(game_data, "homeTeam")
    assert away[100]["blockedShots"] == 1
    assert home[200]["blockedShots"] == 0


def test_goals_count_as_sog_for_game_score():
    gen = _gen()
    game_data = {
        "boxscore": {
            "awayTeam": {"id": 10, "abbrev": "TOR"},
            "homeTeam": {"id": 8, "abbrev": "MTL"},
        },
        "play_by_play": {
            "rosterSpots": [
                {
                    "playerId": 100,
                    "firstName": {"default": "Goal"},
                    "lastName": {"default": "Scorer"},
                    "sweaterNumber": 16,
                    "positionCode": "C",
                    "teamId": 10,
                }
            ],
            "plays": [
                {
                    "typeDescKey": "goal",
                    "details": {
                        "eventOwnerTeamId": 10,
                        "scoringPlayerId": 100,
                    },
                },
                {
                    "typeDescKey": "shot-on-goal",
                    "details": {
                        "eventOwnerTeamId": 10,
                        "shootingPlayerId": 100,
                    },
                },
            ],
        },
    }
    away = gen._calculate_player_stats_from_play_by_play(game_data, "awayTeam")
    assert away[100]["goals"] == 1
    assert away[100]["sog"] == 2  # goal + shot-on-goal
    # Dom: 0.75*G + 0.075*SOG = 0.75 + 0.15 = 0.90
    assert abs(away[100]["gameScore"] - 0.90) < 0.001


def test_faceoff_losses_credited_to_losing_team():
    gen = _gen()
    game_data = {
        "boxscore": {
            "awayTeam": {"id": 10, "abbrev": "TOR"},
            "homeTeam": {"id": 8, "abbrev": "MTL"},
        },
        "play_by_play": {
            "rosterSpots": [
                {
                    "playerId": 100,
                    "firstName": {"default": "Win"},
                    "lastName": {"default": "Ner"},
                    "sweaterNumber": 91,
                    "positionCode": "C",
                    "teamId": 10,
                },
                {
                    "playerId": 200,
                    "firstName": {"default": "Los"},
                    "lastName": {"default": "Er"},
                    "sweaterNumber": 14,
                    "positionCode": "C",
                    "teamId": 8,
                },
            ],
            "plays": [
                {
                    "typeDescKey": "faceoff",
                    "details": {
                        "eventOwnerTeamId": 10,
                        "winningPlayerId": 100,
                        "losingPlayerId": 200,
                    },
                }
            ],
        },
    }
    away = gen._calculate_player_stats_from_play_by_play(game_data, "awayTeam")
    home = gen._calculate_player_stats_from_play_by_play(game_data, "homeTeam")
    assert away[100]["faceoffWins"] == 1
    assert away[100]["faceoffTotal"] == 1
    assert home[200]["faceoffWins"] == 0
    assert home[200]["faceoffTotal"] == 1


def test_unknown_player_id_still_gets_stat_credit():
    gen = _gen()
    # Stub resolver so unit test does not hit the network
    gen._resolve_unknown_player = lambda pid, team_id=None: gen._roster_entry(
        pid, first_name="New", last_name="Callup", team_id=team_id or 10
    )
    game_data = {
        "boxscore": {
            "awayTeam": {"id": 10, "abbrev": "TOR"},
            "homeTeam": {"id": 8, "abbrev": "MTL"},
        },
        "play_by_play": {
            "rosterSpots": [],  # brand-new ID absent from rosterSpots
            "plays": [
                {
                    "typeDescKey": "shot-on-goal",
                    "details": {
                        "eventOwnerTeamId": 10,
                        "shootingPlayerId": 9999999,
                    },
                }
            ],
        },
    }
    away = gen._calculate_player_stats_from_play_by_play(game_data, "awayTeam")
    assert 9999999 in away
    assert away[9999999]["sog"] == 1
    assert "Callup" in away[9999999]["name"]


def test_sparse_pbp_falls_back_to_boxscore_player_sog():
    gen = _gen()
    gen._right_rail_value = lambda game_data, category, team_side: 16 if team_side == "away" else 19
    game_data = {
        "boxscore": {
            "awayTeam": {"id": 10, "abbrev": "VGK"},
            "homeTeam": {"id": 26, "abbrev": "LAK"},
            "playerByGameStats": {
                "awayTeam": {
                    "forwards": [
                        {
                            "playerId": 1,
                            "name": {"default": "A. Player"},
                            "goals": 2,
                            "assists": 1,
                            "sog": 4,
                            "hits": 1,
                            "blockedShots": 0,
                            "pim": 0,
                            "sweaterNumber": 7,
                            "position": "C",
                        },
                        {
                            "playerId": 2,
                            "name": {"default": "B. Helper"},
                            "goals": 0,
                            "assists": 1,
                            "sog": 1,
                            "hits": 0,
                            "blockedShots": 0,
                            "pim": 0,
                            "sweaterNumber": 9,
                            "position": "C",
                        },
                    ],
                    "defense": [],
                    "goalies": [],
                },
                "homeTeam": {"forwards": [], "defense": [], "goalies": []},
            },
        },
        "landing": {"summary": {"scoring": []}},
        "play_by_play": {
            "rosterSpots": [],
            # Truncated feed: goals only — but assist1/assist2 are real
            "plays": [
                {
                    "typeDescKey": "goal",
                    "eventId": 101,
                    "details": {
                        "eventOwnerTeamId": 10,
                        "scoringPlayerId": 1,
                        "assist1PlayerId": 2,
                        "assist2PlayerId": None,
                    },
                },
                {
                    "typeDescKey": "goal",
                    "eventId": 102,
                    "details": {
                        "eventOwnerTeamId": 10,
                        "scoringPlayerId": 1,
                        "assist1PlayerId": None,
                        "assist2PlayerId": None,
                    },
                },
                {
                    "typeDescKey": "faceoff",
                    "details": {
                        "eventOwnerTeamId": 10,
                        "winningPlayerId": 1,
                        "losingPlayerId": 99,
                    },
                },
            ],
        },
    }
    assert gen._pbp_player_feed_is_sparse(game_data) is True
    away = gen._calculate_player_stats_from_play_by_play(game_data, "awayTeam")
    assert away[1]["sog"] == 4
    assert away[1]["goals"] == 2
    # Real A1/A2 from PBP — not all assists treated as primary
    assert away[2]["primaryAssists"] == 1
    assert away[2]["secondaryAssists"] == 0
    assert away[1]["primaryAssists"] == 0
    # Real FO from the one faceoff event (not invented from FO%)
    assert away[1]["faceoffWins"] == 1
    assert away[1]["faceoffTotal"] == 1


def test_null_landing_pp_map_does_not_raise():
    gen = _gen()
    game_data = {"landing": None, "boxscore": {}, "play_by_play": {}}
    assert gen._pp_goal_event_ids(game_data) == set()


def test_goalie_analyzer_uses_boxscore_sa_and_real_xg():
    from analyzers.goalie_analytics_analyzer import GoalieAnalyticsAnalyzer

    game_data = {
        "boxscore": {
            "playerByGameStats": {
                "awayTeam": {
                    "goalies": [
                        {
                            "playerId": 100,
                            "shotsAgainst": 20,
                            "goalsAgainst": 2,
                            "saves": 18,
                            "toi": "60:00",
                        }
                    ]
                },
                "homeTeam": {"goalies": []},
            }
        },
        "play_by_play": {
            "plays": [
                {
                    "typeDescKey": "shot-on-goal",
                    "timeInPeriod": "01:00",
                    "periodDescriptor": {"number": 1},
                    "situationCode": "1551",
                    "details": {
                        "eventOwnerTeamId": 8,
                        "goalieInNetId": 100,
                        "xCoord": 75,
                        "yCoord": 5,
                        "shotType": "wrist",
                        "zoneCode": "O",
                    },
                },
                {
                    "typeDescKey": "goal",
                    "timeInPeriod": "02:00",
                    "periodDescriptor": {"number": 1},
                    "situationCode": "1551",
                    "details": {
                        "eventOwnerTeamId": 8,
                        "goalieInNetId": 100,
                        "xCoord": 80,
                        "yCoord": 2,
                        "shotType": "wrist",
                        "zoneCode": "O",
                    },
                },
            ]
        },
    }
    analyzer = GoalieAnalyticsAnalyzer(1, game_data=game_data)
    stats = analyzer.analyze_goalies()
    assert 100 in stats
    assert stats[100]["shots"] == 20  # boxscore SA
    assert stats[100]["goals"] == 2
    assert isinstance(stats[100]["GSAx"], (int, float))

