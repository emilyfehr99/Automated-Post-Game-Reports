#!/usr/bin/env python3
"""All Three Zones Real Player Database"""

import random
import json

# Real All Three Zones Players
REAL_ALL_THREE_ZONES_PLAYERS = {
    "trevor van_riemsdyk": {
        "name": "Trevor\u00a0van Riemsdyk",
        "team": "ANA",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 172.2,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.09,
                        "shot_assists_per_60": 0.42,
                        "total_shot_contributions_per_60": 1.51,
                        "chances_per_60": 1.26,
                        "chance_assists_per_60": 0.49
                },
                "passing": {
                        "high_danger_assists_per_60": 0.43
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.08,
                        "rush_offense_per_60": 0.62,
                        "shots_off_hd_passes_per_60": 0.95
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.98,
                        "controlled_entry_percent": 0.59,
                        "controlled_entry_with_chance_percent": 0.21
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.43,
                        "retrievals_per_60": 2.63,
                        "successful_retrieval_percent": 0.58,
                        "exits_per_60": 0.1,
                        "botched_retrievals_per_60": -1.95
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "tom wilson": {
        "name": "Tom\u00a0Wilson",
        "team": "ARI",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 137.6,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.74,
                        "shot_assists_per_60": 0.57,
                        "total_shot_contributions_per_60": 1.31,
                        "chances_per_60": 0.72,
                        "chance_assists_per_60": 0.66
                },
                "passing": {
                        "high_danger_assists_per_60": 0.65
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.79,
                        "rush_offense_per_60": 0.38,
                        "shots_off_hd_passes_per_60": 0.53
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.19,
                        "controlled_entry_percent": 0.32,
                        "controlled_entry_with_chance_percent": 0.17
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.67,
                        "retrievals_per_60": 1.96,
                        "successful_retrieval_percent": 0.83,
                        "exits_per_60": 0.11,
                        "botched_retrievals_per_60": -2.7
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "taylor raddysh": {
        "name": "Taylor\u00a0Raddysh",
        "team": "BOS",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 185.8,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.21,
                        "shot_assists_per_60": 0.45,
                        "total_shot_contributions_per_60": 1.66,
                        "chances_per_60": 1.1,
                        "chance_assists_per_60": 0.52
                },
                "passing": {
                        "high_danger_assists_per_60": 0.41
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.15,
                        "rush_offense_per_60": 0.89,
                        "shots_off_hd_passes_per_60": 0.95
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.94,
                        "controlled_entry_percent": 0.45,
                        "controlled_entry_with_chance_percent": 0.18
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.68,
                        "retrievals_per_60": 1.77,
                        "successful_retrieval_percent": 0.66,
                        "exits_per_60": 0.31,
                        "botched_retrievals_per_60": -2.69
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "rasmus sandin": {
        "name": "Rasmus\u00a0Sandin",
        "team": "BUF",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 175.0,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.14,
                        "shot_assists_per_60": 0.43,
                        "total_shot_contributions_per_60": 0.57,
                        "chances_per_60": 0.16,
                        "chance_assists_per_60": 0.6
                },
                "passing": {
                        "high_danger_assists_per_60": 0.51
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.11,
                        "rush_offense_per_60": 0.1,
                        "shots_off_hd_passes_per_60": 0.12
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.69,
                        "controlled_entry_percent": 0.47,
                        "controlled_entry_with_chance_percent": 0.28
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 5.13,
                        "retrievals_per_60": 4.41,
                        "successful_retrieval_percent": 0.58,
                        "exits_per_60": 0.24,
                        "botched_retrievals_per_60": -1.66
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "pierre_luc dubois": {
        "name": "Pierre-Luc\u00a0Dubois",
        "team": "CGY",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 116.8,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.911,
                        "goals_against_average": 2.45,
                        "wins": 22,
                        "shutouts": 2
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "nic dowd": {
        "name": "Nic\u00a0Dowd",
        "team": "CAR",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 132.0,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.45,
                        "shot_assists_per_60": 0.63,
                        "total_shot_contributions_per_60": 2.08,
                        "chances_per_60": 1.16,
                        "chance_assists_per_60": 0.61
                },
                "passing": {
                        "high_danger_assists_per_60": 0.6
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.16,
                        "rush_offense_per_60": 0.66,
                        "shots_off_hd_passes_per_60": 1.51
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.95,
                        "controlled_entry_percent": 0.62,
                        "controlled_entry_with_chance_percent": 0.2
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.16,
                        "retrievals_per_60": 2.05,
                        "successful_retrieval_percent": 0.74,
                        "exits_per_60": 0.26,
                        "botched_retrievals_per_60": -3.89
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "matt roy": {
        "name": "Matt\u00a0Roy",
        "team": "CHI",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 181.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.57,
                        "shot_assists_per_60": 1.13,
                        "total_shot_contributions_per_60": 1.7,
                        "chances_per_60": 0.41,
                        "chance_assists_per_60": 1.37
                },
                "passing": {
                        "high_danger_assists_per_60": 1.29
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.47,
                        "rush_offense_per_60": 0.41,
                        "shots_off_hd_passes_per_60": 0.53
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.69,
                        "controlled_entry_percent": 0.6,
                        "controlled_entry_with_chance_percent": 0.16
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.24,
                        "retrievals_per_60": 2.51,
                        "successful_retrieval_percent": 0.76,
                        "exits_per_60": 0.4,
                        "botched_retrievals_per_60": -2.73
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "martin fehervary": {
        "name": "Martin\u00a0Fehervary",
        "team": "COL",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 186.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.13,
                        "shot_assists_per_60": 0.52,
                        "total_shot_contributions_per_60": 1.65,
                        "chances_per_60": 1.02,
                        "chance_assists_per_60": 0.43
                },
                "passing": {
                        "high_danger_assists_per_60": 0.56
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.43,
                        "rush_offense_per_60": 0.68,
                        "shots_off_hd_passes_per_60": 0.98
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.3,
                        "controlled_entry_percent": 0.57,
                        "controlled_entry_with_chance_percent": 0.25
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.41,
                        "retrievals_per_60": 2.91,
                        "successful_retrieval_percent": 0.61,
                        "exits_per_60": 0.38,
                        "botched_retrievals_per_60": -3.27
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "lars eller": {
        "name": "Lars\u00a0Eller",
        "team": "CBJ",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 185.6,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.26,
                        "shot_assists_per_60": 0.38,
                        "total_shot_contributions_per_60": 0.64,
                        "chances_per_60": 0.3,
                        "chance_assists_per_60": 0.42
                },
                "passing": {
                        "high_danger_assists_per_60": 0.31
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.31,
                        "rush_offense_per_60": 0.17,
                        "shots_off_hd_passes_per_60": 0.2
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.65,
                        "controlled_entry_percent": 0.6,
                        "controlled_entry_with_chance_percent": 0.31
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.13,
                        "retrievals_per_60": 2.64,
                        "successful_retrieval_percent": 0.65,
                        "exits_per_60": 0.31,
                        "botched_retrievals_per_60": -2.86
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "john carlson": {
        "name": "John\u00a0Carlson",
        "team": "DAL",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 119.9,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.914,
                        "goals_against_average": 2.78,
                        "wins": 41,
                        "shutouts": 8
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jakob chychrun": {
        "name": "Jakob\u00a0Chychrun",
        "team": "DET",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 158.3,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.73,
                        "shot_assists_per_60": 0.91,
                        "total_shot_contributions_per_60": 2.64,
                        "chances_per_60": 1.39,
                        "chance_assists_per_60": 0.84
                },
                "passing": {
                        "high_danger_assists_per_60": 0.86
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 2.15,
                        "rush_offense_per_60": 0.98,
                        "shots_off_hd_passes_per_60": 1.66
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.64,
                        "controlled_entry_percent": 0.62,
                        "controlled_entry_with_chance_percent": 0.2
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.04,
                        "retrievals_per_60": 2.48,
                        "successful_retrieval_percent": 0.56,
                        "exits_per_60": 0.3,
                        "botched_retrievals_per_60": -2.33
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "dylan strome": {
        "name": "Dylan\u00a0Strome",
        "team": "EDM",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 155.2,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.35,
                        "shot_assists_per_60": 0.57,
                        "total_shot_contributions_per_60": 1.92,
                        "chances_per_60": 1.54,
                        "chance_assists_per_60": 0.76
                },
                "passing": {
                        "high_danger_assists_per_60": 0.64
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.81,
                        "rush_offense_per_60": 0.52,
                        "shots_off_hd_passes_per_60": 1.39
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.52,
                        "controlled_entry_percent": 0.44,
                        "controlled_entry_with_chance_percent": 0.21
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.82,
                        "retrievals_per_60": 2.63,
                        "successful_retrieval_percent": 0.8,
                        "exits_per_60": 0.24,
                        "botched_retrievals_per_60": -2.37
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "connor mcmichael": {
        "name": "Connor\u00a0McMichael",
        "team": "FLA",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 173.6,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.62,
                        "shot_assists_per_60": 0.47,
                        "total_shot_contributions_per_60": 2.09,
                        "chances_per_60": 2.03,
                        "chance_assists_per_60": 0.57
                },
                "passing": {
                        "high_danger_assists_per_60": 0.5
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 2.06,
                        "rush_offense_per_60": 0.52,
                        "shots_off_hd_passes_per_60": 1.74
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.91,
                        "controlled_entry_percent": 0.55,
                        "controlled_entry_with_chance_percent": 0.31
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.91,
                        "retrievals_per_60": 1.76,
                        "successful_retrieval_percent": 0.83,
                        "exits_per_60": 0.26,
                        "botched_retrievals_per_60": -3.91
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "brandon duhaime": {
        "name": "Brandon\u00a0Duhaime",
        "team": "LAK",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 107.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.69,
                        "shot_assists_per_60": 0.62,
                        "total_shot_contributions_per_60": 1.31,
                        "chances_per_60": 0.7,
                        "chance_assists_per_60": 0.62
                },
                "passing": {
                        "high_danger_assists_per_60": 0.51
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.84,
                        "rush_offense_per_60": 0.51,
                        "shots_off_hd_passes_per_60": 0.65
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.36,
                        "controlled_entry_percent": 0.62,
                        "controlled_entry_with_chance_percent": 0.26
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.93,
                        "retrievals_per_60": 3.31,
                        "successful_retrieval_percent": 0.72,
                        "exits_per_60": 0.39,
                        "botched_retrievals_per_60": -2.66
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "andrew mangiapane": {
        "name": "Andrew\u00a0Mangiapane",
        "team": "MIN",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 189.7,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.926,
                        "goals_against_average": 2.18,
                        "wins": 41,
                        "shutouts": 3
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "aliaksei protas": {
        "name": "Aliaksei\u00a0Protas",
        "team": "MTL",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 163.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.46,
                        "shot_assists_per_60": 0.68,
                        "total_shot_contributions_per_60": 2.14,
                        "chances_per_60": 1.59,
                        "chance_assists_per_60": 0.65
                },
                "passing": {
                        "high_danger_assists_per_60": 0.58
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.54,
                        "rush_offense_per_60": 1.05,
                        "shots_off_hd_passes_per_60": 1.38
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.01,
                        "controlled_entry_percent": 0.4,
                        "controlled_entry_with_chance_percent": 0.17
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.17,
                        "retrievals_per_60": 2.45,
                        "successful_retrieval_percent": 0.63,
                        "exits_per_60": 0.16,
                        "botched_retrievals_per_60": -1.76
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "alex ovechkin": {
        "name": "Alex\u00a0Ovechkin",
        "team": "NSH",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 162.3,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.7,
                        "shot_assists_per_60": 1.19,
                        "total_shot_contributions_per_60": 1.89,
                        "chances_per_60": 0.6,
                        "chance_assists_per_60": 1.41
                },
                "passing": {
                        "high_danger_assists_per_60": 1.23
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.64,
                        "rush_offense_per_60": 0.37,
                        "shots_off_hd_passes_per_60": 0.52
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.44,
                        "controlled_entry_percent": 0.34,
                        "controlled_entry_with_chance_percent": 0.3
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.32,
                        "retrievals_per_60": 1.51,
                        "successful_retrieval_percent": 0.7,
                        "exits_per_60": 0.14,
                        "botched_retrievals_per_60": -1.93
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "vladislav namestnikov": {
        "name": "Vladislav\u00a0Namestnikov",
        "team": "NJD",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 128.6,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.24,
                        "shot_assists_per_60": 1.14,
                        "total_shot_contributions_per_60": 2.38,
                        "chances_per_60": 1.56,
                        "chance_assists_per_60": 1.23
                },
                "passing": {
                        "high_danger_assists_per_60": 1.04
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.09,
                        "rush_offense_per_60": 0.44,
                        "shots_off_hd_passes_per_60": 1.25
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.76,
                        "controlled_entry_percent": 0.44,
                        "controlled_entry_with_chance_percent": 0.33
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.95,
                        "retrievals_per_60": 2.1,
                        "successful_retrieval_percent": 0.79,
                        "exits_per_60": 0.23,
                        "botched_retrievals_per_60": -3.41
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "rasmus kupari": {
        "name": "Rasmus\u00a0Kupari",
        "team": "NYI",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 198.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.18,
                        "shot_assists_per_60": 0.32,
                        "total_shot_contributions_per_60": 0.5,
                        "chances_per_60": 0.19,
                        "chance_assists_per_60": 0.31
                },
                "passing": {
                        "high_danger_assists_per_60": 0.36
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.21,
                        "rush_offense_per_60": 0.06,
                        "shots_off_hd_passes_per_60": 0.15
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.41,
                        "controlled_entry_percent": 0.57,
                        "controlled_entry_with_chance_percent": 0.22
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 4.78,
                        "retrievals_per_60": 4.25,
                        "successful_retrieval_percent": 0.67,
                        "exits_per_60": 0.1,
                        "botched_retrievals_per_60": -1.78
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "nino niederreiter": {
        "name": "Nino\u00a0Niederreiter",
        "team": "NYR",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 165.4,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.928,
                        "goals_against_average": 3.2,
                        "wins": 45,
                        "shutouts": 3
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "nikolaj ehlers": {
        "name": "Nikolaj\u00a0Ehlers",
        "team": "OTT",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 180.2,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.51,
                        "shot_assists_per_60": 0.77,
                        "total_shot_contributions_per_60": 2.28,
                        "chances_per_60": 1.37,
                        "chance_assists_per_60": 0.72
                },
                "passing": {
                        "high_danger_assists_per_60": 0.78
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.75,
                        "rush_offense_per_60": 1.15,
                        "shots_off_hd_passes_per_60": 1.22
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.1,
                        "controlled_entry_percent": 0.43,
                        "controlled_entry_with_chance_percent": 0.16
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.33,
                        "retrievals_per_60": 2.2,
                        "successful_retrieval_percent": 0.58,
                        "exits_per_60": 0.21,
                        "botched_retrievals_per_60": -1.96
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "neal pionk": {
        "name": "Neal\u00a0Pionk",
        "team": "PHI",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 108.2,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.73,
                        "shot_assists_per_60": 0.54,
                        "total_shot_contributions_per_60": 2.27,
                        "chances_per_60": 1.48,
                        "chance_assists_per_60": 0.44
                },
                "passing": {
                        "high_danger_assists_per_60": 0.52
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.58,
                        "rush_offense_per_60": 1.35,
                        "shots_off_hd_passes_per_60": 1.55
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.92,
                        "controlled_entry_percent": 0.36,
                        "controlled_entry_with_chance_percent": 0.16
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.52,
                        "retrievals_per_60": 2.38,
                        "successful_retrieval_percent": 0.56,
                        "exits_per_60": 0.24,
                        "botched_retrievals_per_60": -3.65
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "morgan barron": {
        "name": "Morgan\u00a0Barron",
        "team": "PIT",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 187.3,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.29,
                        "shot_assists_per_60": 1.05,
                        "total_shot_contributions_per_60": 2.34,
                        "chances_per_60": 1.01,
                        "chance_assists_per_60": 1.45
                },
                "passing": {
                        "high_danger_assists_per_60": 1.08
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.41,
                        "rush_offense_per_60": 0.53,
                        "shots_off_hd_passes_per_60": 0.99
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.63,
                        "controlled_entry_percent": 0.55,
                        "controlled_entry_with_chance_percent": 0.35
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.76,
                        "retrievals_per_60": 1.63,
                        "successful_retrieval_percent": 0.67,
                        "exits_per_60": 0.2,
                        "botched_retrievals_per_60": -1.79
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "mason appleton": {
        "name": "Mason\u00a0Appleton",
        "team": "SJS",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 169.0,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.44,
                        "shot_assists_per_60": 0.59,
                        "total_shot_contributions_per_60": 1.03,
                        "chances_per_60": 0.35,
                        "chance_assists_per_60": 0.59
                },
                "passing": {
                        "high_danger_assists_per_60": 0.56
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.39,
                        "rush_offense_per_60": 0.22,
                        "shots_off_hd_passes_per_60": 0.41
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.37,
                        "controlled_entry_percent": 0.46,
                        "controlled_entry_with_chance_percent": 0.17
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.14,
                        "retrievals_per_60": 3.9,
                        "successful_retrieval_percent": 0.65,
                        "exits_per_60": 0.1,
                        "botched_retrievals_per_60": -3.68
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "mark scheifele": {
        "name": "Mark\u00a0Scheifele",
        "team": "SEA",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 194.3,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.918,
                        "goals_against_average": 2.31,
                        "wins": 11,
                        "shutouts": 5
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "logan stanley": {
        "name": "Logan\u00a0Stanley",
        "team": "STL",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 165.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.51,
                        "shot_assists_per_60": 1.17,
                        "total_shot_contributions_per_60": 2.68,
                        "chances_per_60": 1.63,
                        "chance_assists_per_60": 1.52
                },
                "passing": {
                        "high_danger_assists_per_60": 1.13
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.53,
                        "rush_offense_per_60": 0.56,
                        "shots_off_hd_passes_per_60": 1.26
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.23,
                        "controlled_entry_percent": 0.55,
                        "controlled_entry_with_chance_percent": 0.34
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.69,
                        "retrievals_per_60": 2.03,
                        "successful_retrieval_percent": 0.62,
                        "exits_per_60": 0.16,
                        "botched_retrievals_per_60": -3.96
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "kyle connor": {
        "name": "Kyle\u00a0Connor",
        "team": "TBL",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 107.7,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.56,
                        "shot_assists_per_60": 0.98,
                        "total_shot_contributions_per_60": 2.54,
                        "chances_per_60": 1.45,
                        "chance_assists_per_60": 1.22
                },
                "passing": {
                        "high_danger_assists_per_60": 1.01
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.89,
                        "rush_offense_per_60": 0.86,
                        "shots_off_hd_passes_per_60": 1.13
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.08,
                        "controlled_entry_percent": 0.27,
                        "controlled_entry_with_chance_percent": 0.3
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.36,
                        "retrievals_per_60": 2.87,
                        "successful_retrieval_percent": 0.67,
                        "exits_per_60": 0.3,
                        "botched_retrievals_per_60": -1.64
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "josh morrissey": {
        "name": "Josh\u00a0Morrissey",
        "team": "TOR",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 173.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.14,
                        "shot_assists_per_60": 0.4,
                        "total_shot_contributions_per_60": 1.54,
                        "chances_per_60": 1.2,
                        "chance_assists_per_60": 0.56
                },
                "passing": {
                        "high_danger_assists_per_60": 0.44
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.93,
                        "rush_offense_per_60": 0.67,
                        "shots_off_hd_passes_per_60": 1.08
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.06,
                        "controlled_entry_percent": 0.57,
                        "controlled_entry_with_chance_percent": 0.25
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.67,
                        "retrievals_per_60": 1.9,
                        "successful_retrieval_percent": 0.78,
                        "exits_per_60": 0.17,
                        "botched_retrievals_per_60": -1.98
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "haydn fleury": {
        "name": "Haydn\u00a0Fleury",
        "team": "VAN",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 104.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.63,
                        "shot_assists_per_60": 0.84,
                        "total_shot_contributions_per_60": 1.47,
                        "chances_per_60": 0.71,
                        "chance_assists_per_60": 0.89
                },
                "passing": {
                        "high_danger_assists_per_60": 0.82
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.62,
                        "rush_offense_per_60": 0.35,
                        "shots_off_hd_passes_per_60": 0.63
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.31,
                        "controlled_entry_percent": 0.36,
                        "controlled_entry_with_chance_percent": 0.19
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.27,
                        "retrievals_per_60": 3.83,
                        "successful_retrieval_percent": 0.61,
                        "exits_per_60": 0.23,
                        "botched_retrievals_per_60": -2.79
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "gabriel vilardi": {
        "name": "Gabriel\u00a0Vilardi",
        "team": "VGK",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 115.3,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.923,
                        "goals_against_average": 2.23,
                        "wins": 17,
                        "shutouts": 6
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "dylan samberg": {
        "name": "Dylan\u00a0Samberg",
        "team": "WSH",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 152.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.78,
                        "shot_assists_per_60": 0.53,
                        "total_shot_contributions_per_60": 1.31,
                        "chances_per_60": 0.64,
                        "chance_assists_per_60": 0.63
                },
                "passing": {
                        "high_danger_assists_per_60": 0.54
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.98,
                        "rush_offense_per_60": 0.58,
                        "shots_off_hd_passes_per_60": 0.78
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.7,
                        "controlled_entry_percent": 0.55,
                        "controlled_entry_with_chance_percent": 0.21
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.42,
                        "retrievals_per_60": 2.7,
                        "successful_retrieval_percent": 0.71,
                        "exits_per_60": 0.1,
                        "botched_retrievals_per_60": -3.26
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "dylan demelo": {
        "name": "Dylan\u00a0DeMelo",
        "team": "WPG",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 111.2,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.86,
                        "shot_assists_per_60": 0.97,
                        "total_shot_contributions_per_60": 1.83,
                        "chances_per_60": 0.88,
                        "chance_assists_per_60": 0.83
                },
                "passing": {
                        "high_danger_assists_per_60": 0.85
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.12,
                        "rush_offense_per_60": 0.37,
                        "shots_off_hd_passes_per_60": 0.8
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.29,
                        "controlled_entry_percent": 0.52,
                        "controlled_entry_with_chance_percent": 0.32
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.05,
                        "retrievals_per_60": 2.54,
                        "successful_retrieval_percent": 0.75,
                        "exits_per_60": 0.19,
                        "botched_retrievals_per_60": -2.66
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "colin miller": {
        "name": "Colin\u00a0Miller",
        "team": "ANA",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 155.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.88,
                        "shot_assists_per_60": 1.16,
                        "total_shot_contributions_per_60": 2.04,
                        "chances_per_60": 0.86,
                        "chance_assists_per_60": 1.56
                },
                "passing": {
                        "high_danger_assists_per_60": 1.18
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.72,
                        "rush_offense_per_60": 0.29,
                        "shots_off_hd_passes_per_60": 0.84
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.39,
                        "controlled_entry_percent": 0.3,
                        "controlled_entry_with_chance_percent": 0.23
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.83,
                        "retrievals_per_60": 1.81,
                        "successful_retrieval_percent": 0.79,
                        "exits_per_60": 0.32,
                        "botched_retrievals_per_60": -2.12
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "cole perfetti": {
        "name": "Cole\u00a0Perfetti",
        "team": "ARI",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 185.2,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.54,
                        "shot_assists_per_60": 0.46,
                        "total_shot_contributions_per_60": 1.0,
                        "chances_per_60": 0.56,
                        "chance_assists_per_60": 0.41
                },
                "passing": {
                        "high_danger_assists_per_60": 0.45
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.59,
                        "rush_offense_per_60": 0.4,
                        "shots_off_hd_passes_per_60": 0.59
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.67,
                        "controlled_entry_percent": 0.54,
                        "controlled_entry_with_chance_percent": 0.22
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.68,
                        "retrievals_per_60": 3.8,
                        "successful_retrieval_percent": 0.57,
                        "exits_per_60": 0.23,
                        "botched_retrievals_per_60": -2.19
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "alex iafallo": {
        "name": "Alex\u00a0Iafallo",
        "team": "BOS",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 126.3,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.909,
                        "goals_against_average": 2.05,
                        "wins": 32,
                        "shutouts": 3
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "adam lowry": {
        "name": "Adam\u00a0Lowry",
        "team": "BUF",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 163.6,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.13,
                        "shot_assists_per_60": 0.6,
                        "total_shot_contributions_per_60": 1.73,
                        "chances_per_60": 0.94,
                        "chance_assists_per_60": 0.54
                },
                "passing": {
                        "high_danger_assists_per_60": 0.64
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.14,
                        "rush_offense_per_60": 0.45,
                        "shots_off_hd_passes_per_60": 1.2
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.74,
                        "controlled_entry_percent": 0.27,
                        "controlled_entry_with_chance_percent": 0.25
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.59,
                        "retrievals_per_60": 1.7,
                        "successful_retrieval_percent": 0.64,
                        "exits_per_60": 0.21,
                        "botched_retrievals_per_60": -2.36
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "zach whitecloud": {
        "name": "Zach\u00a0Whitecloud",
        "team": "CGY",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 145.0,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.78,
                        "shot_assists_per_60": 0.46,
                        "total_shot_contributions_per_60": 2.24,
                        "chances_per_60": 1.6,
                        "chance_assists_per_60": 0.43
                },
                "passing": {
                        "high_danger_assists_per_60": 0.49
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.57,
                        "rush_offense_per_60": 0.65,
                        "shots_off_hd_passes_per_60": 1.51
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.65,
                        "controlled_entry_percent": 0.52,
                        "controlled_entry_with_chance_percent": 0.29
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.29,
                        "retrievals_per_60": 1.51,
                        "successful_retrieval_percent": 0.7,
                        "exits_per_60": 0.31,
                        "botched_retrievals_per_60": -3.81
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "william karlsson": {
        "name": "William\u00a0Karlsson",
        "team": "CAR",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 137.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.37,
                        "shot_assists_per_60": 0.75,
                        "total_shot_contributions_per_60": 2.12,
                        "chances_per_60": 1.46,
                        "chance_assists_per_60": 0.75
                },
                "passing": {
                        "high_danger_assists_per_60": 0.82
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.24,
                        "rush_offense_per_60": 0.42,
                        "shots_off_hd_passes_per_60": 1.42
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.13,
                        "controlled_entry_percent": 0.35,
                        "controlled_entry_with_chance_percent": 0.22
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.87,
                        "retrievals_per_60": 1.99,
                        "successful_retrieval_percent": 0.57,
                        "exits_per_60": 0.32,
                        "botched_retrievals_per_60": -3.86
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "victor olofsson": {
        "name": "Victor\u00a0Olofsson",
        "team": "CHI",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 123.1,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.58,
                        "shot_assists_per_60": 0.56,
                        "total_shot_contributions_per_60": 1.14,
                        "chances_per_60": 0.6,
                        "chance_assists_per_60": 0.64
                },
                "passing": {
                        "high_danger_assists_per_60": 0.54
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.59,
                        "rush_offense_per_60": 0.31,
                        "shots_off_hd_passes_per_60": 0.52
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.57,
                        "controlled_entry_percent": 0.26,
                        "controlled_entry_with_chance_percent": 0.3
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.3,
                        "retrievals_per_60": 3.03,
                        "successful_retrieval_percent": 0.72,
                        "exits_per_60": 0.22,
                        "botched_retrievals_per_60": -2.06
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "tomas hertl": {
        "name": "Tomas\u00a0Hertl",
        "team": "COL",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 121.7,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.906,
                        "goals_against_average": 2.73,
                        "wins": 36,
                        "shutouts": 7
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "tanner pearson": {
        "name": "Tanner\u00a0Pearson",
        "team": "CBJ",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 128.8,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.81,
                        "shot_assists_per_60": 1.16,
                        "total_shot_contributions_per_60": 1.97,
                        "chances_per_60": 0.74,
                        "chance_assists_per_60": 1.07
                },
                "passing": {
                        "high_danger_assists_per_60": 1.01
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.9,
                        "rush_offense_per_60": 0.47,
                        "shots_off_hd_passes_per_60": 0.82
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.82,
                        "controlled_entry_percent": 0.49,
                        "controlled_entry_with_chance_percent": 0.25
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.78,
                        "retrievals_per_60": 2.57,
                        "successful_retrieval_percent": 0.66,
                        "exits_per_60": 0.32,
                        "botched_retrievals_per_60": -1.79
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "shea theodore": {
        "name": "Shea\u00a0Theodore",
        "team": "DAL",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 150.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.03,
                        "shot_assists_per_60": 0.57,
                        "total_shot_contributions_per_60": 1.6,
                        "chances_per_60": 0.97,
                        "chance_assists_per_60": 0.59
                },
                "passing": {
                        "high_danger_assists_per_60": 0.51
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.95,
                        "rush_offense_per_60": 0.74,
                        "shots_off_hd_passes_per_60": 0.8
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.07,
                        "controlled_entry_percent": 0.57,
                        "controlled_entry_with_chance_percent": 0.27
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.95,
                        "retrievals_per_60": 2.77,
                        "successful_retrieval_percent": 0.65,
                        "exits_per_60": 0.27,
                        "botched_retrievals_per_60": -2.19
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "pavel dorofeyev": {
        "name": "Pavel\u00a0Dorofeyev",
        "team": "DET",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 199.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.54,
                        "shot_assists_per_60": 0.55,
                        "total_shot_contributions_per_60": 1.09,
                        "chances_per_60": 0.41,
                        "chance_assists_per_60": 0.76
                },
                "passing": {
                        "high_danger_assists_per_60": 0.48
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.52,
                        "rush_offense_per_60": 0.3,
                        "shots_off_hd_passes_per_60": 0.55
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.12,
                        "controlled_entry_percent": 0.64,
                        "controlled_entry_with_chance_percent": 0.16
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.82,
                        "retrievals_per_60": 2.83,
                        "successful_retrieval_percent": 0.73,
                        "exits_per_60": 0.16,
                        "botched_retrievals_per_60": -3.15
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "noah hanifin": {
        "name": "Noah\u00a0Hanifin",
        "team": "EDM",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 151.2,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.35,
                        "shot_assists_per_60": 0.43,
                        "total_shot_contributions_per_60": 0.78,
                        "chances_per_60": 0.32,
                        "chance_assists_per_60": 0.41
                },
                "passing": {
                        "high_danger_assists_per_60": 0.37
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.3,
                        "rush_offense_per_60": 0.18,
                        "shots_off_hd_passes_per_60": 0.36
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.44,
                        "controlled_entry_percent": 0.54,
                        "controlled_entry_with_chance_percent": 0.22
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.83,
                        "retrievals_per_60": 3.4,
                        "successful_retrieval_percent": 0.65,
                        "exits_per_60": 0.36,
                        "botched_retrievals_per_60": -2.98
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "nicolas roy": {
        "name": "Nicolas\u00a0Roy",
        "team": "FLA",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 166.7,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.925,
                        "goals_against_average": 2.19,
                        "wins": 22,
                        "shutouts": 2
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "nicolas hague": {
        "name": "Nicolas\u00a0Hague",
        "team": "LAK",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 121.6,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.23,
                        "shot_assists_per_60": 1.01,
                        "total_shot_contributions_per_60": 2.24,
                        "chances_per_60": 0.87,
                        "chance_assists_per_60": 0.94
                },
                "passing": {
                        "high_danger_assists_per_60": 0.88
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.49,
                        "rush_offense_per_60": 0.95,
                        "shots_off_hd_passes_per_60": 1.13
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.95,
                        "controlled_entry_percent": 0.52,
                        "controlled_entry_with_chance_percent": 0.35
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.03,
                        "retrievals_per_60": 1.93,
                        "successful_retrieval_percent": 0.77,
                        "exits_per_60": 0.35,
                        "botched_retrievals_per_60": -1.94
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "mark stone": {
        "name": "Mark\u00a0Stone",
        "team": "MIN",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 169.6,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.79,
                        "shot_assists_per_60": 0.86,
                        "total_shot_contributions_per_60": 1.65,
                        "chances_per_60": 0.93,
                        "chance_assists_per_60": 1.01
                },
                "passing": {
                        "high_danger_assists_per_60": 0.8
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.91,
                        "rush_offense_per_60": 0.26,
                        "shots_off_hd_passes_per_60": 0.71
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.78,
                        "controlled_entry_percent": 0.63,
                        "controlled_entry_with_chance_percent": 0.22
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.95,
                        "retrievals_per_60": 1.98,
                        "successful_retrieval_percent": 0.72,
                        "exits_per_60": 0.32,
                        "botched_retrievals_per_60": -1.66
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "keegan kolesar": {
        "name": "Keegan\u00a0Kolesar",
        "team": "MTL",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 169.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.33,
                        "shot_assists_per_60": 0.64,
                        "total_shot_contributions_per_60": 1.97,
                        "chances_per_60": 1.15,
                        "chance_assists_per_60": 0.58
                },
                "passing": {
                        "high_danger_assists_per_60": 0.64
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.58,
                        "rush_offense_per_60": 0.95,
                        "shots_off_hd_passes_per_60": 1.29
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.93,
                        "controlled_entry_percent": 0.56,
                        "controlled_entry_with_chance_percent": 0.33
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.47,
                        "retrievals_per_60": 1.52,
                        "successful_retrieval_percent": 0.72,
                        "exits_per_60": 0.15,
                        "botched_retrievals_per_60": -3.08
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "kaedan korczak": {
        "name": "Kaedan\u00a0Korczak",
        "team": "NSH",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 112.1,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.79,
                        "shot_assists_per_60": 0.49,
                        "total_shot_contributions_per_60": 1.28,
                        "chances_per_60": 0.58,
                        "chance_assists_per_60": 0.47
                },
                "passing": {
                        "high_danger_assists_per_60": 0.44
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.84,
                        "rush_offense_per_60": 0.46,
                        "shots_off_hd_passes_per_60": 0.59
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.48,
                        "controlled_entry_percent": 0.63,
                        "controlled_entry_with_chance_percent": 0.35
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.09,
                        "retrievals_per_60": 2.56,
                        "successful_retrieval_percent": 0.66,
                        "exits_per_60": 0.1,
                        "botched_retrievals_per_60": -2.17
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jack eichel": {
        "name": "Jack\u00a0Eichel",
        "team": "NJD",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 170.2,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.915,
                        "goals_against_average": 3.44,
                        "wins": 12,
                        "shutouts": 3
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "ivan barbashev": {
        "name": "Ivan\u00a0Barbashev",
        "team": "NYI",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 178.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.85,
                        "shot_assists_per_60": 0.89,
                        "total_shot_contributions_per_60": 1.74,
                        "chances_per_60": 1.01,
                        "chance_assists_per_60": 0.9
                },
                "passing": {
                        "high_danger_assists_per_60": 0.91
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.8,
                        "rush_offense_per_60": 0.45,
                        "shots_off_hd_passes_per_60": 0.84
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.08,
                        "controlled_entry_percent": 0.29,
                        "controlled_entry_with_chance_percent": 0.2
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.72,
                        "retrievals_per_60": 2.78,
                        "successful_retrieval_percent": 0.78,
                        "exits_per_60": 0.19,
                        "botched_retrievals_per_60": -3.63
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "cole schwindt": {
        "name": "Cole\u00a0Schwindt",
        "team": "NYR",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 128.7,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.42,
                        "shot_assists_per_60": 0.54,
                        "total_shot_contributions_per_60": 1.96,
                        "chances_per_60": 1.82,
                        "chance_assists_per_60": 0.48
                },
                "passing": {
                        "high_danger_assists_per_60": 0.6
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.96,
                        "rush_offense_per_60": 0.97,
                        "shots_off_hd_passes_per_60": 1.31
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.44,
                        "controlled_entry_percent": 0.34,
                        "controlled_entry_with_chance_percent": 0.15
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.26,
                        "retrievals_per_60": 2.69,
                        "successful_retrieval_percent": 0.67,
                        "exits_per_60": 0.13,
                        "botched_retrievals_per_60": -2.88
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "brett howden": {
        "name": "Brett\u00a0Howden",
        "team": "OTT",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 179.2,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.69,
                        "shot_assists_per_60": 0.75,
                        "total_shot_contributions_per_60": 2.44,
                        "chances_per_60": 1.53,
                        "chance_assists_per_60": 0.74
                },
                "passing": {
                        "high_danger_assists_per_60": 0.69
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.46,
                        "rush_offense_per_60": 1.1,
                        "shots_off_hd_passes_per_60": 1.64
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.95,
                        "controlled_entry_percent": 0.34,
                        "controlled_entry_with_chance_percent": 0.32
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.66,
                        "retrievals_per_60": 2.45,
                        "successful_retrieval_percent": 0.85,
                        "exits_per_60": 0.12,
                        "botched_retrievals_per_60": -1.86
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "brayden mcnabb": {
        "name": "Brayden\u00a0McNabb",
        "team": "PHI",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 164.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.63,
                        "shot_assists_per_60": 0.62,
                        "total_shot_contributions_per_60": 1.25,
                        "chances_per_60": 0.79,
                        "chance_assists_per_60": 0.57
                },
                "passing": {
                        "high_danger_assists_per_60": 0.55
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.74,
                        "rush_offense_per_60": 0.43,
                        "shots_off_hd_passes_per_60": 0.58
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.8,
                        "controlled_entry_percent": 0.49,
                        "controlled_entry_with_chance_percent": 0.34
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 4.68,
                        "retrievals_per_60": 4.32,
                        "successful_retrieval_percent": 0.8,
                        "exits_per_60": 0.11,
                        "botched_retrievals_per_60": -3.38
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "alexander holtz": {
        "name": "Alexander\u00a0Holtz",
        "team": "PIT",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 168.4,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.921,
                        "goals_against_average": 2.46,
                        "wins": 38,
                        "shutouts": 3
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "alex pietrangelo": {
        "name": "Alex\u00a0Pietrangelo",
        "team": "SJS",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 118.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.51,
                        "shot_assists_per_60": 0.45,
                        "total_shot_contributions_per_60": 1.96,
                        "chances_per_60": 1.77,
                        "chance_assists_per_60": 0.58
                },
                "passing": {
                        "high_danger_assists_per_60": 0.47
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.41,
                        "rush_offense_per_60": 0.7,
                        "shots_off_hd_passes_per_60": 1.33
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.94,
                        "controlled_entry_percent": 0.31,
                        "controlled_entry_with_chance_percent": 0.17
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.69,
                        "retrievals_per_60": 2.4,
                        "successful_retrieval_percent": 0.62,
                        "exits_per_60": 0.13,
                        "botched_retrievals_per_60": -3.86
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "vincent desharnais": {
        "name": "Vincent\u00a0Desharnais",
        "team": "SEA",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 167.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.58,
                        "shot_assists_per_60": 1.1,
                        "total_shot_contributions_per_60": 1.68,
                        "chances_per_60": 0.46,
                        "chance_assists_per_60": 1.29
                },
                "passing": {
                        "high_danger_assists_per_60": 0.98
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.72,
                        "rush_offense_per_60": 0.4,
                        "shots_off_hd_passes_per_60": 0.47
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.85,
                        "controlled_entry_percent": 0.48,
                        "controlled_entry_with_chance_percent": 0.19
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.36,
                        "retrievals_per_60": 1.7,
                        "successful_retrieval_percent": 0.84,
                        "exits_per_60": 0.4,
                        "botched_retrievals_per_60": -3.92
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "tyler myers": {
        "name": "Tyler\u00a0Myers",
        "team": "STL",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 138.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.7,
                        "shot_assists_per_60": 0.49,
                        "total_shot_contributions_per_60": 2.19,
                        "chances_per_60": 2.01,
                        "chance_assists_per_60": 0.58
                },
                "passing": {
                        "high_danger_assists_per_60": 0.44
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.72,
                        "rush_offense_per_60": 0.88,
                        "shots_off_hd_passes_per_60": 1.22
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.53,
                        "controlled_entry_percent": 0.37,
                        "controlled_entry_with_chance_percent": 0.26
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.49,
                        "retrievals_per_60": 2.93,
                        "successful_retrieval_percent": 0.71,
                        "exits_per_60": 0.16,
                        "botched_retrievals_per_60": -3.08
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "teddy blueger": {
        "name": "Teddy\u00a0Blueger",
        "team": "TBL",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 175.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.63,
                        "shot_assists_per_60": 0.71,
                        "total_shot_contributions_per_60": 1.34,
                        "chances_per_60": 0.77,
                        "chance_assists_per_60": 0.75
                },
                "passing": {
                        "high_danger_assists_per_60": 0.64
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.57,
                        "rush_offense_per_60": 0.49,
                        "shots_off_hd_passes_per_60": 0.5
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.54,
                        "controlled_entry_percent": 0.36,
                        "controlled_entry_with_chance_percent": 0.29
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.67,
                        "retrievals_per_60": 2.97,
                        "successful_retrieval_percent": 0.62,
                        "exits_per_60": 0.13,
                        "botched_retrievals_per_60": -3.3
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "quinn hughes": {
        "name": "Quinn\u00a0Hughes",
        "team": "TOR",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 102.2,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.929,
                        "goals_against_average": 2.74,
                        "wins": 38,
                        "shutouts": 0
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "pius suter": {
        "name": "Pius\u00a0Suter",
        "team": "VAN",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 122.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.88,
                        "shot_assists_per_60": 0.99,
                        "total_shot_contributions_per_60": 1.87,
                        "chances_per_60": 0.68,
                        "chance_assists_per_60": 1.08
                },
                "passing": {
                        "high_danger_assists_per_60": 1.17
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.18,
                        "rush_offense_per_60": 0.28,
                        "shots_off_hd_passes_per_60": 0.82
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.84,
                        "controlled_entry_percent": 0.51,
                        "controlled_entry_with_chance_percent": 0.26
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.6,
                        "retrievals_per_60": 2.68,
                        "successful_retrieval_percent": 0.67,
                        "exits_per_60": 0.31,
                        "botched_retrievals_per_60": -2.09
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "other_elias pettersson": {
        "name": "Other Elias\u00a0Pettersson",
        "team": "VGK",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 128.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.61,
                        "shot_assists_per_60": 0.91,
                        "total_shot_contributions_per_60": 1.52,
                        "chances_per_60": 0.44,
                        "chance_assists_per_60": 1.05
                },
                "passing": {
                        "high_danger_assists_per_60": 0.88
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.74,
                        "rush_offense_per_60": 0.28,
                        "shots_off_hd_passes_per_60": 0.58
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.35,
                        "controlled_entry_percent": 0.38,
                        "controlled_entry_with_chance_percent": 0.19
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.42,
                        "retrievals_per_60": 2.75,
                        "successful_retrieval_percent": 0.68,
                        "exits_per_60": 0.3,
                        "botched_retrievals_per_60": -1.61
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "noah juulsen": {
        "name": "Noah\u00a0Juulsen",
        "team": "WSH",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 160.2,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.83,
                        "shot_assists_per_60": 0.9,
                        "total_shot_contributions_per_60": 1.73,
                        "chances_per_60": 0.91,
                        "chance_assists_per_60": 1.04
                },
                "passing": {
                        "high_danger_assists_per_60": 0.75
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.95,
                        "rush_offense_per_60": 0.65,
                        "shots_off_hd_passes_per_60": 0.82
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.84,
                        "controlled_entry_percent": 0.63,
                        "controlled_entry_with_chance_percent": 0.17
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.83,
                        "retrievals_per_60": 2.85,
                        "successful_retrieval_percent": 0.72,
                        "exits_per_60": 0.24,
                        "botched_retrievals_per_60": -2.75
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "nils hoglander": {
        "name": "Nils\u00a0Hoglander",
        "team": "WPG",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 159.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.59,
                        "shot_assists_per_60": 0.66,
                        "total_shot_contributions_per_60": 1.25,
                        "chances_per_60": 0.57,
                        "chance_assists_per_60": 0.69
                },
                "passing": {
                        "high_danger_assists_per_60": 0.71
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.77,
                        "rush_offense_per_60": 0.29,
                        "shots_off_hd_passes_per_60": 0.42
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.34,
                        "controlled_entry_percent": 0.63,
                        "controlled_entry_with_chance_percent": 0.18
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.85,
                        "retrievals_per_60": 2.98,
                        "successful_retrieval_percent": 0.77,
                        "exits_per_60": 0.34,
                        "botched_retrievals_per_60": -3.04
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "max sasson": {
        "name": "Max\u00a0Sasson",
        "team": "ANA",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 100.9,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.903,
                        "goals_against_average": 2.51,
                        "wins": 43,
                        "shutouts": 2
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "marcus pettersson": {
        "name": "Marcus\u00a0Pettersson",
        "team": "ARI",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 164.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.69,
                        "shot_assists_per_60": 1.11,
                        "total_shot_contributions_per_60": 2.8,
                        "chances_per_60": 1.84,
                        "chance_assists_per_60": 1.13
                },
                "passing": {
                        "high_danger_assists_per_60": 1.31
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.88,
                        "rush_offense_per_60": 1.34,
                        "shots_off_hd_passes_per_60": 1.46
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.38,
                        "controlled_entry_percent": 0.6,
                        "controlled_entry_with_chance_percent": 0.34
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.07,
                        "retrievals_per_60": 2.95,
                        "successful_retrieval_percent": 0.64,
                        "exits_per_60": 0.1,
                        "botched_retrievals_per_60": -3.58
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "linus karlsson": {
        "name": "Linus\u00a0Karlsson",
        "team": "BOS",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 170.6,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.5,
                        "shot_assists_per_60": 1.18,
                        "total_shot_contributions_per_60": 1.68,
                        "chances_per_60": 0.56,
                        "chance_assists_per_60": 1.56
                },
                "passing": {
                        "high_danger_assists_per_60": 1.05
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.67,
                        "rush_offense_per_60": 0.3,
                        "shots_off_hd_passes_per_60": 0.51
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.96,
                        "controlled_entry_percent": 0.45,
                        "controlled_entry_with_chance_percent": 0.31
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.13,
                        "retrievals_per_60": 1.79,
                        "successful_retrieval_percent": 0.63,
                        "exits_per_60": 0.12,
                        "botched_retrievals_per_60": -1.62
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "kiefer sherwood": {
        "name": "Kiefer\u00a0Sherwood",
        "team": "BUF",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 110.1,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.7,
                        "shot_assists_per_60": 0.93,
                        "total_shot_contributions_per_60": 2.63,
                        "chances_per_60": 1.6,
                        "chance_assists_per_60": 1.29
                },
                "passing": {
                        "high_danger_assists_per_60": 1.01
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.41,
                        "rush_offense_per_60": 1.12,
                        "shots_off_hd_passes_per_60": 1.81
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.56,
                        "controlled_entry_percent": 0.55,
                        "controlled_entry_with_chance_percent": 0.25
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.73,
                        "retrievals_per_60": 1.82,
                        "successful_retrieval_percent": 0.77,
                        "exits_per_60": 0.16,
                        "botched_retrievals_per_60": -3.03
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jonathan lekkerimaki": {
        "name": "Jonathan\u00a0Lekkerimaki",
        "team": "CGY",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 161.2,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.13,
                        "shot_assists_per_60": 0.35,
                        "total_shot_contributions_per_60": 0.48,
                        "chances_per_60": 0.14,
                        "chance_assists_per_60": 0.34
                },
                "passing": {
                        "high_danger_assists_per_60": 0.29
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.18,
                        "rush_offense_per_60": 0.04,
                        "shots_off_hd_passes_per_60": 0.09
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.55,
                        "controlled_entry_percent": 0.29,
                        "controlled_entry_with_chance_percent": 0.17
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 4.09,
                        "retrievals_per_60": 4.41,
                        "successful_retrieval_percent": 0.6,
                        "exits_per_60": 0.25,
                        "botched_retrievals_per_60": -3.47
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jake debrusk": {
        "name": "Jake\u00a0DeBrusk",
        "team": "CAR",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 138.1,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.914,
                        "goals_against_average": 2.94,
                        "wins": 13,
                        "shutouts": 0
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jt miller": {
        "name": "J.T.\u00a0Miller",
        "team": "CHI",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 160.1,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.36,
                        "shot_assists_per_60": 1.04,
                        "total_shot_contributions_per_60": 2.4,
                        "chances_per_60": 1.62,
                        "chance_assists_per_60": 1.27
                },
                "passing": {
                        "high_danger_assists_per_60": 1.05
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.9,
                        "rush_offense_per_60": 0.48,
                        "shots_off_hd_passes_per_60": 1.17
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.21,
                        "controlled_entry_percent": 0.45,
                        "controlled_entry_with_chance_percent": 0.15
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.55,
                        "retrievals_per_60": 1.79,
                        "successful_retrieval_percent": 0.61,
                        "exits_per_60": 0.17,
                        "botched_retrievals_per_60": -3.28
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "filip hronek": {
        "name": "Filip\u00a0Hronek",
        "team": "COL",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 183.2,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.56,
                        "shot_assists_per_60": 1.16,
                        "total_shot_contributions_per_60": 1.72,
                        "chances_per_60": 0.62,
                        "chance_assists_per_60": 1.21
                },
                "passing": {
                        "high_danger_assists_per_60": 1.17
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.46,
                        "rush_offense_per_60": 0.31,
                        "shots_off_hd_passes_per_60": 0.48
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.84,
                        "controlled_entry_percent": 0.6,
                        "controlled_entry_with_chance_percent": 0.32
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.95,
                        "retrievals_per_60": 2.24,
                        "successful_retrieval_percent": 0.8,
                        "exits_per_60": 0.17,
                        "botched_retrievals_per_60": -3.57
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "erik brannstrom": {
        "name": "Erik\u00a0Brannstrom",
        "team": "CBJ",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 181.8,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.64,
                        "shot_assists_per_60": 0.89,
                        "total_shot_contributions_per_60": 2.53,
                        "chances_per_60": 1.38,
                        "chance_assists_per_60": 1.14
                },
                "passing": {
                        "high_danger_assists_per_60": 0.72
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.44,
                        "rush_offense_per_60": 1.21,
                        "shots_off_hd_passes_per_60": 1.72
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.13,
                        "controlled_entry_percent": 0.49,
                        "controlled_entry_with_chance_percent": 0.18
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.31,
                        "retrievals_per_60": 2.98,
                        "successful_retrieval_percent": 0.55,
                        "exits_per_60": 0.3,
                        "botched_retrievals_per_60": -2.04
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "elias pettersson": {
        "name": "Elias\u00a0Pettersson",
        "team": "DAL",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 128.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.24,
                        "shot_assists_per_60": 0.22,
                        "total_shot_contributions_per_60": 0.46,
                        "chances_per_60": 0.24,
                        "chance_assists_per_60": 0.29
                },
                "passing": {
                        "high_danger_assists_per_60": 0.25
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.28,
                        "rush_offense_per_60": 0.11,
                        "shots_off_hd_passes_per_60": 0.2
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.52,
                        "controlled_entry_percent": 0.54,
                        "controlled_entry_with_chance_percent": 0.32
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.9,
                        "retrievals_per_60": 3.82,
                        "successful_retrieval_percent": 0.72,
                        "exits_per_60": 0.36,
                        "botched_retrievals_per_60": -3.41
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "derek forbort": {
        "name": "Derek\u00a0Forbort",
        "team": "DET",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 110.8,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.923,
                        "goals_against_average": 2.63,
                        "wins": 21,
                        "shutouts": 7
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "danton heinen": {
        "name": "Danton\u00a0Heinen",
        "team": "EDM",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 122.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.74,
                        "shot_assists_per_60": 0.41,
                        "total_shot_contributions_per_60": 2.15,
                        "chances_per_60": 2.18,
                        "chance_assists_per_60": 0.42
                },
                "passing": {
                        "high_danger_assists_per_60": 0.49
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.47,
                        "rush_offense_per_60": 1.25,
                        "shots_off_hd_passes_per_60": 1.7
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.03,
                        "controlled_entry_percent": 0.61,
                        "controlled_entry_with_chance_percent": 0.32
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.58,
                        "retrievals_per_60": 2.97,
                        "successful_retrieval_percent": 0.61,
                        "exits_per_60": 0.31,
                        "botched_retrievals_per_60": -2.47
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "dakota joshua": {
        "name": "Dakota\u00a0Joshua",
        "team": "FLA",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 167.8,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.65,
                        "shot_assists_per_60": 1.17,
                        "total_shot_contributions_per_60": 1.82,
                        "chances_per_60": 0.5,
                        "chance_assists_per_60": 1.54
                },
                "passing": {
                        "high_danger_assists_per_60": 1.38
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.71,
                        "rush_offense_per_60": 0.45,
                        "shots_off_hd_passes_per_60": 0.56
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.38,
                        "controlled_entry_percent": 0.44,
                        "controlled_entry_with_chance_percent": 0.28
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.86,
                        "retrievals_per_60": 2.55,
                        "successful_retrieval_percent": 0.8,
                        "exits_per_60": 0.11,
                        "botched_retrievals_per_60": -3.49
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "conor garland": {
        "name": "Conor\u00a0Garland",
        "team": "LAK",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 121.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.63,
                        "shot_assists_per_60": 0.98,
                        "total_shot_contributions_per_60": 1.61,
                        "chances_per_60": 0.64,
                        "chance_assists_per_60": 0.87
                },
                "passing": {
                        "high_danger_assists_per_60": 0.83
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.71,
                        "rush_offense_per_60": 0.45,
                        "shots_off_hd_passes_per_60": 0.66
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.91,
                        "controlled_entry_percent": 0.45,
                        "controlled_entry_with_chance_percent": 0.27
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.47,
                        "retrievals_per_60": 1.59,
                        "successful_retrieval_percent": 0.74,
                        "exits_per_60": 0.34,
                        "botched_retrievals_per_60": -3.82
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "carson soucy": {
        "name": "Carson\u00a0Soucy",
        "team": "MIN",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 155.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.33,
                        "shot_assists_per_60": 0.25,
                        "total_shot_contributions_per_60": 0.58,
                        "chances_per_60": 0.27,
                        "chance_assists_per_60": 0.24
                },
                "passing": {
                        "high_danger_assists_per_60": 0.24
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.35,
                        "rush_offense_per_60": 0.26,
                        "shots_off_hd_passes_per_60": 0.36
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.51,
                        "controlled_entry_percent": 0.61,
                        "controlled_entry_with_chance_percent": 0.29
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 4.22,
                        "retrievals_per_60": 4.47,
                        "successful_retrieval_percent": 0.6,
                        "exits_per_60": 0.25,
                        "botched_retrievals_per_60": -2.97
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "brock boeser": {
        "name": "Brock\u00a0Boeser",
        "team": "MTL",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 120.8,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.915,
                        "goals_against_average": 2.71,
                        "wins": 29,
                        "shutouts": 6
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "arshdeep bains": {
        "name": "Arshdeep\u00a0Bains",
        "team": "NSH",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 132.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.53,
                        "shot_assists_per_60": 0.49,
                        "total_shot_contributions_per_60": 2.02,
                        "chances_per_60": 1.88,
                        "chance_assists_per_60": 0.58
                },
                "passing": {
                        "high_danger_assists_per_60": 0.47
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.43,
                        "rush_offense_per_60": 0.77,
                        "shots_off_hd_passes_per_60": 1.42
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.78,
                        "controlled_entry_percent": 0.65,
                        "controlled_entry_with_chance_percent": 0.2
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.27,
                        "retrievals_per_60": 2.07,
                        "successful_retrieval_percent": 0.75,
                        "exits_per_60": 0.27,
                        "botched_retrievals_per_60": -2.78
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "aatu raty": {
        "name": "Aatu\u00a0Raty",
        "team": "NJD",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 109.8,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.73,
                        "shot_assists_per_60": 1.13,
                        "total_shot_contributions_per_60": 2.86,
                        "chances_per_60": 2.01,
                        "chance_assists_per_60": 1.23
                },
                "passing": {
                        "high_danger_assists_per_60": 1.15
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 2.13,
                        "rush_offense_per_60": 0.92,
                        "shots_off_hd_passes_per_60": 1.4
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.65,
                        "controlled_entry_percent": 0.63,
                        "controlled_entry_with_chance_percent": 0.23
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.42,
                        "retrievals_per_60": 1.71,
                        "successful_retrieval_percent": 0.55,
                        "exits_per_60": 0.29,
                        "botched_retrievals_per_60": -3.68
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "olli määttä": {
        "name": "Olli\u00a0M\u00e4\u00e4tt\u00e4",
        "team": "NYI",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 152.8,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.71,
                        "shot_assists_per_60": 0.82,
                        "total_shot_contributions_per_60": 1.53,
                        "chances_per_60": 0.52,
                        "chance_assists_per_60": 0.8
                },
                "passing": {
                        "high_danger_assists_per_60": 0.81
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.91,
                        "rush_offense_per_60": 0.52,
                        "shots_off_hd_passes_per_60": 0.55
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.49,
                        "controlled_entry_percent": 0.46,
                        "controlled_entry_with_chance_percent": 0.16
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.05,
                        "retrievals_per_60": 2.01,
                        "successful_retrieval_percent": 0.66,
                        "exits_per_60": 0.27,
                        "botched_retrievals_per_60": -2.6
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "nick schmaltz": {
        "name": "Nick\u00a0Schmaltz",
        "team": "NYR",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 140.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.14,
                        "shot_assists_per_60": 0.55,
                        "total_shot_contributions_per_60": 0.69,
                        "chances_per_60": 0.12,
                        "chance_assists_per_60": 0.58
                },
                "passing": {
                        "high_danger_assists_per_60": 0.55
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.17,
                        "rush_offense_per_60": 0.07,
                        "shots_off_hd_passes_per_60": 0.12
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.32,
                        "controlled_entry_percent": 0.33,
                        "controlled_entry_with_chance_percent": 0.33
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 4.16,
                        "retrievals_per_60": 4.25,
                        "successful_retrieval_percent": 0.76,
                        "exits_per_60": 0.18,
                        "botched_retrievals_per_60": -1.71
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "nick bjugstad": {
        "name": "Nick\u00a0Bjugstad",
        "team": "OTT",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 174.0,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.907,
                        "goals_against_average": 2.47,
                        "wins": 14,
                        "shutouts": 5
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "mikhail sergachev": {
        "name": "Mikhail\u00a0Sergachev",
        "team": "PHI",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 175.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.66,
                        "shot_assists_per_60": 0.87,
                        "total_shot_contributions_per_60": 2.53,
                        "chances_per_60": 1.65,
                        "chance_assists_per_60": 1.08
                },
                "passing": {
                        "high_danger_assists_per_60": 0.8
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.74,
                        "rush_offense_per_60": 0.95,
                        "shots_off_hd_passes_per_60": 1.68
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.0,
                        "controlled_entry_percent": 0.46,
                        "controlled_entry_with_chance_percent": 0.3
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.77,
                        "retrievals_per_60": 2.43,
                        "successful_retrieval_percent": 0.58,
                        "exits_per_60": 0.2,
                        "botched_retrievals_per_60": -3.75
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "michael kesselring": {
        "name": "Michael\u00a0Kesselring",
        "team": "PIT",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 160.1,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.77,
                        "shot_assists_per_60": 1.07,
                        "total_shot_contributions_per_60": 2.84,
                        "chances_per_60": 2.04,
                        "chance_assists_per_60": 0.95
                },
                "passing": {
                        "high_danger_assists_per_60": 1.02
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 2.35,
                        "rush_offense_per_60": 0.68,
                        "shots_off_hd_passes_per_60": 1.84
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.16,
                        "controlled_entry_percent": 0.35,
                        "controlled_entry_with_chance_percent": 0.21
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.14,
                        "retrievals_per_60": 1.89,
                        "successful_retrieval_percent": 0.85,
                        "exits_per_60": 0.2,
                        "botched_retrievals_per_60": -1.55
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "michael carcone": {
        "name": "Michael\u00a0Carcone",
        "team": "SJS",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 167.1,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.89,
                        "shot_assists_per_60": 0.7,
                        "total_shot_contributions_per_60": 1.59,
                        "chances_per_60": 1.1,
                        "chance_assists_per_60": 0.57
                },
                "passing": {
                        "high_danger_assists_per_60": 0.81
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.06,
                        "rush_offense_per_60": 0.3,
                        "shots_off_hd_passes_per_60": 0.72
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.39,
                        "controlled_entry_percent": 0.6,
                        "controlled_entry_with_chance_percent": 0.32
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.25,
                        "retrievals_per_60": 2.41,
                        "successful_retrieval_percent": 0.7,
                        "exits_per_60": 0.27,
                        "botched_retrievals_per_60": -2.34
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "matias maccelli": {
        "name": "Matias\u00a0Maccelli",
        "team": "SEA",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 111.6,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.6,
                        "shot_assists_per_60": 0.81,
                        "total_shot_contributions_per_60": 1.41,
                        "chances_per_60": 0.46,
                        "chance_assists_per_60": 0.79
                },
                "passing": {
                        "high_danger_assists_per_60": 0.82
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.79,
                        "rush_offense_per_60": 0.31,
                        "shots_off_hd_passes_per_60": 0.48
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.55,
                        "controlled_entry_percent": 0.64,
                        "controlled_entry_with_chance_percent": 0.31
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.48,
                        "retrievals_per_60": 2.99,
                        "successful_retrieval_percent": 0.81,
                        "exits_per_60": 0.21,
                        "botched_retrievals_per_60": -2.01
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "logan cooley": {
        "name": "Logan\u00a0Cooley",
        "team": "STL",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 134.5,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.927,
                        "goals_against_average": 3.32,
                        "wins": 19,
                        "shutouts": 5
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "lawson crouse": {
        "name": "Lawson\u00a0Crouse",
        "team": "TBL",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 156.7,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.1,
                        "shot_assists_per_60": 0.98,
                        "total_shot_contributions_per_60": 2.08,
                        "chances_per_60": 1.27,
                        "chance_assists_per_60": 1.3
                },
                "passing": {
                        "high_danger_assists_per_60": 0.92
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.3,
                        "rush_offense_per_60": 0.56,
                        "shots_off_hd_passes_per_60": 0.93
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.57,
                        "controlled_entry_percent": 0.35,
                        "controlled_entry_with_chance_percent": 0.2
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.24,
                        "retrievals_per_60": 2.5,
                        "successful_retrieval_percent": 0.61,
                        "exits_per_60": 0.29,
                        "botched_retrievals_per_60": -3.77
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "kevin stenlund": {
        "name": "Kevin\u00a0Stenlund",
        "team": "TOR",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 124.0,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.65,
                        "shot_assists_per_60": 1.07,
                        "total_shot_contributions_per_60": 1.72,
                        "chances_per_60": 0.48,
                        "chance_assists_per_60": 1.28
                },
                "passing": {
                        "high_danger_assists_per_60": 0.96
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.72,
                        "rush_offense_per_60": 0.39,
                        "shots_off_hd_passes_per_60": 0.6
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.31,
                        "controlled_entry_percent": 0.32,
                        "controlled_entry_with_chance_percent": 0.28
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.49,
                        "retrievals_per_60": 1.58,
                        "successful_retrieval_percent": 0.79,
                        "exits_per_60": 0.38,
                        "botched_retrievals_per_60": -1.91
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "juuso valimaki": {
        "name": "Juuso\u00a0Valimaki",
        "team": "VAN",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 174.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.79,
                        "shot_assists_per_60": 0.8,
                        "total_shot_contributions_per_60": 1.59,
                        "chances_per_60": 0.63,
                        "chance_assists_per_60": 1.02
                },
                "passing": {
                        "high_danger_assists_per_60": 0.9
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.76,
                        "rush_offense_per_60": 0.63,
                        "shots_off_hd_passes_per_60": 0.78
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.63,
                        "controlled_entry_percent": 0.57,
                        "controlled_entry_with_chance_percent": 0.33
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.62,
                        "retrievals_per_60": 2.39,
                        "successful_retrieval_percent": 0.63,
                        "exits_per_60": 0.29,
                        "botched_retrievals_per_60": -1.67
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "john marino": {
        "name": "John\u00a0Marino",
        "team": "VGK",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 114.8,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.59,
                        "shot_assists_per_60": 0.34,
                        "total_shot_contributions_per_60": 0.93,
                        "chances_per_60": 0.64,
                        "chance_assists_per_60": 0.31
                },
                "passing": {
                        "high_danger_assists_per_60": 0.29
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.56,
                        "rush_offense_per_60": 0.43,
                        "shots_off_hd_passes_per_60": 0.64
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.79,
                        "controlled_entry_percent": 0.35,
                        "controlled_entry_with_chance_percent": 0.3
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 5.31,
                        "retrievals_per_60": 4.45,
                        "successful_retrieval_percent": 0.77,
                        "exits_per_60": 0.27,
                        "botched_retrievals_per_60": -2.1
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jack mcbain": {
        "name": "Jack\u00a0McBain",
        "team": "WSH",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 110.7,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.929,
                        "goals_against_average": 2.52,
                        "wins": 31,
                        "shutouts": 3
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "ian cole": {
        "name": "Ian\u00a0Cole",
        "team": "WPG",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 130.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.12,
                        "shot_assists_per_60": 0.7,
                        "total_shot_contributions_per_60": 1.82,
                        "chances_per_60": 1.26,
                        "chance_assists_per_60": 0.78
                },
                "passing": {
                        "high_danger_assists_per_60": 0.78
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.1,
                        "rush_offense_per_60": 0.75,
                        "shots_off_hd_passes_per_60": 1.19
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.69,
                        "controlled_entry_percent": 0.59,
                        "controlled_entry_with_chance_percent": 0.2
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.12,
                        "retrievals_per_60": 2.34,
                        "successful_retrieval_percent": 0.64,
                        "exits_per_60": 0.25,
                        "botched_retrievals_per_60": -2.47
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "dylan guenther": {
        "name": "Dylan\u00a0Guenther",
        "team": "ANA",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 190.3,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.4,
                        "shot_assists_per_60": 1.07,
                        "total_shot_contributions_per_60": 2.47,
                        "chances_per_60": 1.45,
                        "chance_assists_per_60": 1.18
                },
                "passing": {
                        "high_danger_assists_per_60": 0.91
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.96,
                        "rush_offense_per_60": 0.44,
                        "shots_off_hd_passes_per_60": 1.26
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.1,
                        "controlled_entry_percent": 0.58,
                        "controlled_entry_with_chance_percent": 0.3
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.45,
                        "retrievals_per_60": 2.62,
                        "successful_retrieval_percent": 0.61,
                        "exits_per_60": 0.2,
                        "botched_retrievals_per_60": -2.21
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "clayton keller": {
        "name": "Clayton\u00a0Keller",
        "team": "ARI",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 140.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.22,
                        "shot_assists_per_60": 0.47,
                        "total_shot_contributions_per_60": 1.69,
                        "chances_per_60": 1.18,
                        "chance_assists_per_60": 0.57
                },
                "passing": {
                        "high_danger_assists_per_60": 0.52
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.26,
                        "rush_offense_per_60": 0.51,
                        "shots_off_hd_passes_per_60": 0.87
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.07,
                        "controlled_entry_percent": 0.31,
                        "controlled_entry_with_chance_percent": 0.32
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.8,
                        "retrievals_per_60": 2.44,
                        "successful_retrieval_percent": 0.79,
                        "exits_per_60": 0.39,
                        "botched_retrievals_per_60": -3.25
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "barrett hayton": {
        "name": "Barrett\u00a0Hayton",
        "team": "BOS",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 175.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.75,
                        "shot_assists_per_60": 0.7,
                        "total_shot_contributions_per_60": 1.45,
                        "chances_per_60": 0.7,
                        "chance_assists_per_60": 0.87
                },
                "passing": {
                        "high_danger_assists_per_60": 0.77
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.71,
                        "rush_offense_per_60": 0.33,
                        "shots_off_hd_passes_per_60": 0.69
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.4,
                        "controlled_entry_percent": 0.64,
                        "controlled_entry_with_chance_percent": 0.18
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.34,
                        "retrievals_per_60": 3.57,
                        "successful_retrieval_percent": 0.84,
                        "exits_per_60": 0.37,
                        "botched_retrievals_per_60": -2.26
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "alexander kerfoot": {
        "name": "Alexander\u00a0Kerfoot",
        "team": "BUF",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 144.4,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.911,
                        "goals_against_average": 2.14,
                        "wins": 41,
                        "shutouts": 0
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "william nylander": {
        "name": "William\u00a0Nylander",
        "team": "CGY",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 124.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.69,
                        "shot_assists_per_60": 0.83,
                        "total_shot_contributions_per_60": 2.52,
                        "chances_per_60": 1.38,
                        "chance_assists_per_60": 0.88
                },
                "passing": {
                        "high_danger_assists_per_60": 0.9
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.67,
                        "rush_offense_per_60": 0.56,
                        "shots_off_hd_passes_per_60": 1.72
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.6,
                        "controlled_entry_percent": 0.61,
                        "controlled_entry_with_chance_percent": 0.2
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.28,
                        "retrievals_per_60": 1.92,
                        "successful_retrieval_percent": 0.67,
                        "exits_per_60": 0.34,
                        "botched_retrievals_per_60": -3.14
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "steven lorentz": {
        "name": "Steven\u00a0Lorentz",
        "team": "CAR",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 190.2,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.74,
                        "shot_assists_per_60": 0.91,
                        "total_shot_contributions_per_60": 1.65,
                        "chances_per_60": 0.58,
                        "chance_assists_per_60": 1.2
                },
                "passing": {
                        "high_danger_assists_per_60": 0.94
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.83,
                        "rush_offense_per_60": 0.33,
                        "shots_off_hd_passes_per_60": 0.57
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.66,
                        "controlled_entry_percent": 0.55,
                        "controlled_entry_with_chance_percent": 0.23
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.24,
                        "retrievals_per_60": 1.98,
                        "successful_retrieval_percent": 0.57,
                        "exits_per_60": 0.27,
                        "botched_retrievals_per_60": -2.7
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "simon benoit": {
        "name": "Simon\u00a0Benoit",
        "team": "CHI",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 136.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.75,
                        "shot_assists_per_60": 1.12,
                        "total_shot_contributions_per_60": 1.87,
                        "chances_per_60": 0.96,
                        "chance_assists_per_60": 1.3
                },
                "passing": {
                        "high_danger_assists_per_60": 1.05
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.68,
                        "rush_offense_per_60": 0.46,
                        "shots_off_hd_passes_per_60": 0.53
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.77,
                        "controlled_entry_percent": 0.35,
                        "controlled_entry_with_chance_percent": 0.34
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.75,
                        "retrievals_per_60": 1.52,
                        "successful_retrieval_percent": 0.81,
                        "exits_per_60": 0.22,
                        "botched_retrievals_per_60": -1.53
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "pontus holmberg": {
        "name": "Pontus\u00a0Holmberg",
        "team": "COL",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 153.2,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.18,
                        "shot_assists_per_60": 0.45,
                        "total_shot_contributions_per_60": 0.63,
                        "chances_per_60": 0.16,
                        "chance_assists_per_60": 0.48
                },
                "passing": {
                        "high_danger_assists_per_60": 0.52
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.24,
                        "rush_offense_per_60": 0.06,
                        "shots_off_hd_passes_per_60": 0.13
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.31,
                        "controlled_entry_percent": 0.48,
                        "controlled_entry_with_chance_percent": 0.34
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 4.46,
                        "retrievals_per_60": 3.72,
                        "successful_retrieval_percent": 0.73,
                        "exits_per_60": 0.36,
                        "botched_retrievals_per_60": -3.11
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "philippe myers": {
        "name": "Philippe\u00a0Myers",
        "team": "CBJ",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 176.8,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.91,
                        "goals_against_average": 3.25,
                        "wins": 33,
                        "shutouts": 3
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "oliver ekman_larsson": {
        "name": "Oliver\u00a0Ekman-Larsson",
        "team": "DAL",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 191.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.51,
                        "shot_assists_per_60": 1.04,
                        "total_shot_contributions_per_60": 2.55,
                        "chances_per_60": 1.66,
                        "chance_assists_per_60": 1.02
                },
                "passing": {
                        "high_danger_assists_per_60": 1.05
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.4,
                        "rush_offense_per_60": 1.07,
                        "shots_off_hd_passes_per_60": 1.49
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.62,
                        "controlled_entry_percent": 0.4,
                        "controlled_entry_with_chance_percent": 0.25
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.95,
                        "retrievals_per_60": 1.94,
                        "successful_retrieval_percent": 0.76,
                        "exits_per_60": 0.2,
                        "botched_retrievals_per_60": -2.64
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "nicholas robertson": {
        "name": "Nicholas\u00a0Robertson",
        "team": "DET",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 191.1,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.13,
                        "shot_assists_per_60": 0.64,
                        "total_shot_contributions_per_60": 1.77,
                        "chances_per_60": 1.22,
                        "chance_assists_per_60": 0.62
                },
                "passing": {
                        "high_danger_assists_per_60": 0.58
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.95,
                        "rush_offense_per_60": 0.77,
                        "shots_off_hd_passes_per_60": 1.03
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.26,
                        "controlled_entry_percent": 0.33,
                        "controlled_entry_with_chance_percent": 0.17
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.27,
                        "retrievals_per_60": 2.45,
                        "successful_retrieval_percent": 0.81,
                        "exits_per_60": 0.21,
                        "botched_retrievals_per_60": -2.01
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "morgan rielly": {
        "name": "Morgan\u00a0Rielly",
        "team": "EDM",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 106.2,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.53,
                        "shot_assists_per_60": 0.5,
                        "total_shot_contributions_per_60": 1.03,
                        "chances_per_60": 0.45,
                        "chance_assists_per_60": 0.44
                },
                "passing": {
                        "high_danger_assists_per_60": 0.59
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.51,
                        "rush_offense_per_60": 0.23,
                        "shots_off_hd_passes_per_60": 0.4
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.21,
                        "controlled_entry_percent": 0.3,
                        "controlled_entry_with_chance_percent": 0.32
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.29,
                        "retrievals_per_60": 2.86,
                        "successful_retrieval_percent": 0.66,
                        "exits_per_60": 0.18,
                        "botched_retrievals_per_60": -2.92
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "mitch marner": {
        "name": "Mitch\u00a0Marner",
        "team": "FLA",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 152.1,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.75,
                        "shot_assists_per_60": 0.78,
                        "total_shot_contributions_per_60": 1.53,
                        "chances_per_60": 0.72,
                        "chance_assists_per_60": 0.91
                },
                "passing": {
                        "high_danger_assists_per_60": 0.78
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.86,
                        "rush_offense_per_60": 0.49,
                        "shots_off_hd_passes_per_60": 0.56
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.56,
                        "controlled_entry_percent": 0.28,
                        "controlled_entry_with_chance_percent": 0.24
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.22,
                        "retrievals_per_60": 2.59,
                        "successful_retrieval_percent": 0.84,
                        "exits_per_60": 0.22,
                        "botched_retrievals_per_60": -2.59
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "max pacioretty": {
        "name": "Max\u00a0Pacioretty",
        "team": "LAK",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 127.4,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.926,
                        "goals_against_average": 2.17,
                        "wins": 14,
                        "shutouts": 4
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "max domi": {
        "name": "Max\u00a0Domi",
        "team": "MIN",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 121.0,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.14,
                        "shot_assists_per_60": 1.16,
                        "total_shot_contributions_per_60": 2.3,
                        "chances_per_60": 1.13,
                        "chance_assists_per_60": 0.98
                },
                "passing": {
                        "high_danger_assists_per_60": 1.18
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.01,
                        "rush_offense_per_60": 0.58,
                        "shots_off_hd_passes_per_60": 1.11
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.47,
                        "controlled_entry_percent": 0.45,
                        "controlled_entry_with_chance_percent": 0.3
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.92,
                        "retrievals_per_60": 2.83,
                        "successful_retrieval_percent": 0.83,
                        "exits_per_60": 0.32,
                        "botched_retrievals_per_60": -3.14
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "matthew knies": {
        "name": "Matthew\u00a0Knies",
        "team": "MTL",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 191.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.89,
                        "shot_assists_per_60": 0.51,
                        "total_shot_contributions_per_60": 1.4,
                        "chances_per_60": 0.71,
                        "chance_assists_per_60": 0.65
                },
                "passing": {
                        "high_danger_assists_per_60": 0.44
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.2,
                        "rush_offense_per_60": 0.61,
                        "shots_off_hd_passes_per_60": 0.67
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.16,
                        "controlled_entry_percent": 0.44,
                        "controlled_entry_with_chance_percent": 0.22
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.14,
                        "retrievals_per_60": 2.24,
                        "successful_retrieval_percent": 0.69,
                        "exits_per_60": 0.35,
                        "botched_retrievals_per_60": -3.06
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "john tavares": {
        "name": "John\u00a0Tavares",
        "team": "NSH",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 100.3,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.12,
                        "shot_assists_per_60": 0.78,
                        "total_shot_contributions_per_60": 1.9,
                        "chances_per_60": 0.83,
                        "chance_assists_per_60": 0.98
                },
                "passing": {
                        "high_danger_assists_per_60": 0.65
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.02,
                        "rush_offense_per_60": 0.61,
                        "shots_off_hd_passes_per_60": 1.02
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.18,
                        "controlled_entry_percent": 0.45,
                        "controlled_entry_with_chance_percent": 0.17
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.03,
                        "retrievals_per_60": 1.85,
                        "successful_retrieval_percent": 0.57,
                        "exits_per_60": 0.23,
                        "botched_retrievals_per_60": -2.58
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jake mccabe": {
        "name": "Jake\u00a0McCabe",
        "team": "NJD",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 192.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.71,
                        "shot_assists_per_60": 0.62,
                        "total_shot_contributions_per_60": 1.33,
                        "chances_per_60": 0.54,
                        "chance_assists_per_60": 0.79
                },
                "passing": {
                        "high_danger_assists_per_60": 0.69
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.83,
                        "rush_offense_per_60": 0.5,
                        "shots_off_hd_passes_per_60": 0.7
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.34,
                        "controlled_entry_percent": 0.34,
                        "controlled_entry_with_chance_percent": 0.26
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.93,
                        "retrievals_per_60": 3.55,
                        "successful_retrieval_percent": 0.55,
                        "exits_per_60": 0.12,
                        "botched_retrievals_per_60": -1.51
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "david kampf": {
        "name": "David\u00a0Kampf",
        "team": "NYI",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 118.5,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.919,
                        "goals_against_average": 2.78,
                        "wins": 13,
                        "shutouts": 4
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "conor timmins": {
        "name": "Conor\u00a0Timmins",
        "team": "NYR",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 138.6,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.78,
                        "shot_assists_per_60": 0.71,
                        "total_shot_contributions_per_60": 1.49,
                        "chances_per_60": 0.68,
                        "chance_assists_per_60": 0.61
                },
                "passing": {
                        "high_danger_assists_per_60": 0.81
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.07,
                        "rush_offense_per_60": 0.26,
                        "shots_off_hd_passes_per_60": 0.76
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.53,
                        "controlled_entry_percent": 0.31,
                        "controlled_entry_with_chance_percent": 0.33
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.54,
                        "retrievals_per_60": 2.31,
                        "successful_retrieval_percent": 0.69,
                        "exits_per_60": 0.15,
                        "botched_retrievals_per_60": -2.31
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "chris tanev": {
        "name": "Chris\u00a0Tanev",
        "team": "OTT",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 174.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.75,
                        "shot_assists_per_60": 0.68,
                        "total_shot_contributions_per_60": 1.43,
                        "chances_per_60": 0.56,
                        "chance_assists_per_60": 0.93
                },
                "passing": {
                        "high_danger_assists_per_60": 0.54
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.02,
                        "rush_offense_per_60": 0.46,
                        "shots_off_hd_passes_per_60": 0.77
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.96,
                        "controlled_entry_percent": 0.29,
                        "controlled_entry_with_chance_percent": 0.17
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.47,
                        "retrievals_per_60": 1.69,
                        "successful_retrieval_percent": 0.68,
                        "exits_per_60": 0.12,
                        "botched_retrievals_per_60": -3.31
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "bobby mcmann": {
        "name": "Bobby\u00a0McMann",
        "team": "PHI",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 121.0,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.41,
                        "shot_assists_per_60": 0.85,
                        "total_shot_contributions_per_60": 2.26,
                        "chances_per_60": 1.43,
                        "chance_assists_per_60": 0.9
                },
                "passing": {
                        "high_danger_assists_per_60": 0.95
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.54,
                        "rush_offense_per_60": 1.06,
                        "shots_off_hd_passes_per_60": 1.06
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.87,
                        "controlled_entry_percent": 0.57,
                        "controlled_entry_with_chance_percent": 0.29
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.3,
                        "retrievals_per_60": 2.76,
                        "successful_retrieval_percent": 0.78,
                        "exits_per_60": 0.15,
                        "botched_retrievals_per_60": -3.68
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "auston matthews": {
        "name": "Auston\u00a0Matthews",
        "team": "PIT",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 146.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.59,
                        "shot_assists_per_60": 0.84,
                        "total_shot_contributions_per_60": 1.43,
                        "chances_per_60": 0.47,
                        "chance_assists_per_60": 1.06
                },
                "passing": {
                        "high_danger_assists_per_60": 0.68
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.67,
                        "rush_offense_per_60": 0.47,
                        "shots_off_hd_passes_per_60": 0.54
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.65,
                        "controlled_entry_percent": 0.52,
                        "controlled_entry_with_chance_percent": 0.19
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.97,
                        "retrievals_per_60": 3.33,
                        "successful_retrieval_percent": 0.67,
                        "exits_per_60": 0.31,
                        "botched_retrievals_per_60": -2.68
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "zemgus girgensons": {
        "name": "Zemgus\u00a0Girgensons",
        "team": "SJS",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 196.5,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.911,
                        "goals_against_average": 3.37,
                        "wins": 41,
                        "shutouts": 6
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "yanni gourde": {
        "name": "Yanni\u00a0Gourde",
        "team": "SEA",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 189.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.55,
                        "shot_assists_per_60": 0.69,
                        "total_shot_contributions_per_60": 2.24,
                        "chances_per_60": 1.17,
                        "chance_assists_per_60": 0.84
                },
                "passing": {
                        "high_danger_assists_per_60": 0.7
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.62,
                        "rush_offense_per_60": 0.97,
                        "shots_off_hd_passes_per_60": 1.13
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.44,
                        "controlled_entry_percent": 0.28,
                        "controlled_entry_with_chance_percent": 0.2
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.57,
                        "retrievals_per_60": 2.58,
                        "successful_retrieval_percent": 0.75,
                        "exits_per_60": 0.25,
                        "botched_retrievals_per_60": -3.7
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "victor hedman": {
        "name": "Victor\u00a0Hedman",
        "team": "STL",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 151.2,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.88,
                        "shot_assists_per_60": 1.11,
                        "total_shot_contributions_per_60": 1.99,
                        "chances_per_60": 0.92,
                        "chance_assists_per_60": 1.22
                },
                "passing": {
                        "high_danger_assists_per_60": 1.23
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.18,
                        "rush_offense_per_60": 0.27,
                        "shots_off_hd_passes_per_60": 0.88
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.35,
                        "controlled_entry_percent": 0.31,
                        "controlled_entry_with_chance_percent": 0.33
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.89,
                        "retrievals_per_60": 1.8,
                        "successful_retrieval_percent": 0.74,
                        "exits_per_60": 0.2,
                        "botched_retrievals_per_60": -1.95
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "ryan mcdonagh": {
        "name": "Ryan\u00a0McDonagh",
        "team": "TBL",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 191.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.54,
                        "shot_assists_per_60": 0.78,
                        "total_shot_contributions_per_60": 2.32,
                        "chances_per_60": 1.74,
                        "chance_assists_per_60": 0.66
                },
                "passing": {
                        "high_danger_assists_per_60": 0.87
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.44,
                        "rush_offense_per_60": 1.15,
                        "shots_off_hd_passes_per_60": 1.16
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.16,
                        "controlled_entry_percent": 0.49,
                        "controlled_entry_with_chance_percent": 0.22
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.1,
                        "retrievals_per_60": 2.81,
                        "successful_retrieval_percent": 0.8,
                        "exits_per_60": 0.35,
                        "botched_retrievals_per_60": -2.88
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "oliver bjorkstrand": {
        "name": "Oliver\u00a0Bjorkstrand",
        "team": "TOR",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 142.2,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.67,
                        "shot_assists_per_60": 0.48,
                        "total_shot_contributions_per_60": 1.15,
                        "chances_per_60": 0.73,
                        "chance_assists_per_60": 0.59
                },
                "passing": {
                        "high_danger_assists_per_60": 0.5
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.89,
                        "rush_offense_per_60": 0.43,
                        "shots_off_hd_passes_per_60": 0.61
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.63,
                        "controlled_entry_percent": 0.34,
                        "controlled_entry_with_chance_percent": 0.17
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.56,
                        "retrievals_per_60": 4.42,
                        "successful_retrieval_percent": 0.58,
                        "exits_per_60": 0.33,
                        "botched_retrievals_per_60": -3.11
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "nikita kucherov": {
        "name": "Nikita\u00a0Kucherov",
        "team": "VAN",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 178.3,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.912,
                        "goals_against_average": 2.81,
                        "wins": 16,
                        "shutouts": 6
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "nick perbix": {
        "name": "Nick\u00a0Perbix",
        "team": "VGK",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 147.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.94,
                        "shot_assists_per_60": 1.11,
                        "total_shot_contributions_per_60": 2.05,
                        "chances_per_60": 1.18,
                        "chance_assists_per_60": 1.43
                },
                "passing": {
                        "high_danger_assists_per_60": 1.17
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.07,
                        "rush_offense_per_60": 0.37,
                        "shots_off_hd_passes_per_60": 0.98
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.56,
                        "controlled_entry_percent": 0.37,
                        "controlled_entry_with_chance_percent": 0.35
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.33,
                        "retrievals_per_60": 1.55,
                        "successful_retrieval_percent": 0.78,
                        "exits_per_60": 0.15,
                        "botched_retrievals_per_60": -2.62
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "nick paul": {
        "name": "Nick\u00a0Paul",
        "team": "WSH",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 182.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.53,
                        "shot_assists_per_60": 0.67,
                        "total_shot_contributions_per_60": 2.2,
                        "chances_per_60": 1.66,
                        "chance_assists_per_60": 0.69
                },
                "passing": {
                        "high_danger_assists_per_60": 0.56
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 2.11,
                        "rush_offense_per_60": 0.92,
                        "shots_off_hd_passes_per_60": 1.2
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.42,
                        "controlled_entry_percent": 0.65,
                        "controlled_entry_with_chance_percent": 0.18
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.23,
                        "retrievals_per_60": 1.92,
                        "successful_retrieval_percent": 0.68,
                        "exits_per_60": 0.28,
                        "botched_retrievals_per_60": -2.91
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "mitchell chaffee": {
        "name": "Mitchell\u00a0Chaffee",
        "team": "WPG",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 162.0,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.28,
                        "shot_assists_per_60": 0.64,
                        "total_shot_contributions_per_60": 1.92,
                        "chances_per_60": 1.17,
                        "chance_assists_per_60": 0.82
                },
                "passing": {
                        "high_danger_assists_per_60": 0.56
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.24,
                        "rush_offense_per_60": 0.66,
                        "shots_off_hd_passes_per_60": 1.1
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.83,
                        "controlled_entry_percent": 0.58,
                        "controlled_entry_with_chance_percent": 0.25
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.2,
                        "retrievals_per_60": 2.91,
                        "successful_retrieval_percent": 0.68,
                        "exits_per_60": 0.33,
                        "botched_retrievals_per_60": -3.39
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "michael eyssimont": {
        "name": "Michael\u00a0Eyssimont",
        "team": "ANA",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 194.1,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.18,
                        "shot_assists_per_60": 0.83,
                        "total_shot_contributions_per_60": 1.01,
                        "chances_per_60": 0.14,
                        "chance_assists_per_60": 0.97
                },
                "passing": {
                        "high_danger_assists_per_60": 0.72
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.19,
                        "rush_offense_per_60": 0.09,
                        "shots_off_hd_passes_per_60": 0.2
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.55,
                        "controlled_entry_percent": 0.32,
                        "controlled_entry_with_chance_percent": 0.22
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 4.38,
                        "retrievals_per_60": 3.7,
                        "successful_retrieval_percent": 0.61,
                        "exits_per_60": 0.14,
                        "botched_retrievals_per_60": -3.48
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "luke glendening": {
        "name": "Luke\u00a0Glendening",
        "team": "ARI",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 162.2,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.922,
                        "goals_against_average": 3.14,
                        "wins": 21,
                        "shutouts": 8
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jake guentzel": {
        "name": "Jake\u00a0Guentzel",
        "team": "BOS",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 113.7,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.8,
                        "shot_assists_per_60": 0.85,
                        "total_shot_contributions_per_60": 1.65,
                        "chances_per_60": 0.98,
                        "chance_assists_per_60": 1.16
                },
                "passing": {
                        "high_danger_assists_per_60": 0.79
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.09,
                        "rush_offense_per_60": 0.61,
                        "shots_off_hd_passes_per_60": 0.72
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.4,
                        "controlled_entry_percent": 0.59,
                        "controlled_entry_with_chance_percent": 0.21
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.85,
                        "retrievals_per_60": 2.59,
                        "successful_retrieval_percent": 0.71,
                        "exits_per_60": 0.4,
                        "botched_retrievals_per_60": -3.95
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jj moser": {
        "name": "J.J.\u00a0Moser",
        "team": "BUF",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 195.2,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.61,
                        "shot_assists_per_60": 1.02,
                        "total_shot_contributions_per_60": 1.63,
                        "chances_per_60": 0.76,
                        "chance_assists_per_60": 0.82
                },
                "passing": {
                        "high_danger_assists_per_60": 1.1
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.64,
                        "rush_offense_per_60": 0.37,
                        "shots_off_hd_passes_per_60": 0.51
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.05,
                        "controlled_entry_percent": 0.53,
                        "controlled_entry_with_chance_percent": 0.31
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.34,
                        "retrievals_per_60": 2.72,
                        "successful_retrieval_percent": 0.67,
                        "exits_per_60": 0.19,
                        "botched_retrievals_per_60": -1.88
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "gage goncalves": {
        "name": "Gage\u00a0Goncalves",
        "team": "CGY",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 138.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.11,
                        "shot_assists_per_60": 0.57,
                        "total_shot_contributions_per_60": 1.68,
                        "chances_per_60": 0.93,
                        "chance_assists_per_60": 0.62
                },
                "passing": {
                        "high_danger_assists_per_60": 0.53
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.42,
                        "rush_offense_per_60": 0.49,
                        "shots_off_hd_passes_per_60": 0.86
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.43,
                        "controlled_entry_percent": 0.33,
                        "controlled_entry_with_chance_percent": 0.34
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.88,
                        "retrievals_per_60": 1.72,
                        "successful_retrieval_percent": 0.6,
                        "exits_per_60": 0.16,
                        "botched_retrievals_per_60": -1.95
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "erik cernak": {
        "name": "Erik\u00a0Cernak",
        "team": "CAR",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 115.6,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.16,
                        "shot_assists_per_60": 0.47,
                        "total_shot_contributions_per_60": 0.63,
                        "chances_per_60": 0.2,
                        "chance_assists_per_60": 0.65
                },
                "passing": {
                        "high_danger_assists_per_60": 0.46
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.14,
                        "rush_offense_per_60": 0.05,
                        "shots_off_hd_passes_per_60": 0.13
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.73,
                        "controlled_entry_percent": 0.41,
                        "controlled_entry_with_chance_percent": 0.22
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 4.23,
                        "retrievals_per_60": 3.85,
                        "successful_retrieval_percent": 0.8,
                        "exits_per_60": 0.22,
                        "botched_retrievals_per_60": -2.04
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "emil lilleberg": {
        "name": "Emil\u00a0Lilleberg",
        "team": "CHI",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 163.0,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.907,
                        "goals_against_average": 2.42,
                        "wins": 35,
                        "shutouts": 6
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "darren raddysh": {
        "name": "Darren\u00a0Raddysh",
        "team": "COL",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 171.0,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.28,
                        "shot_assists_per_60": 0.59,
                        "total_shot_contributions_per_60": 1.87,
                        "chances_per_60": 1.63,
                        "chance_assists_per_60": 0.69
                },
                "passing": {
                        "high_danger_assists_per_60": 0.69
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.15,
                        "rush_offense_per_60": 0.53,
                        "shots_off_hd_passes_per_60": 1.23
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.15,
                        "controlled_entry_percent": 0.3,
                        "controlled_entry_with_chance_percent": 0.32
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.57,
                        "retrievals_per_60": 2.57,
                        "successful_retrieval_percent": 0.83,
                        "exits_per_60": 0.13,
                        "botched_retrievals_per_60": -2.17
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "conor geekie": {
        "name": "Conor\u00a0Geekie",
        "team": "CBJ",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 140.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.72,
                        "shot_assists_per_60": 0.74,
                        "total_shot_contributions_per_60": 2.46,
                        "chances_per_60": 1.98,
                        "chance_assists_per_60": 0.66
                },
                "passing": {
                        "high_danger_assists_per_60": 0.78
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.81,
                        "rush_offense_per_60": 1.22,
                        "shots_off_hd_passes_per_60": 1.25
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.82,
                        "controlled_entry_percent": 0.48,
                        "controlled_entry_with_chance_percent": 0.31
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.73,
                        "retrievals_per_60": 2.94,
                        "successful_retrieval_percent": 0.6,
                        "exits_per_60": 0.33,
                        "botched_retrievals_per_60": -3.96
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "cam atkinson": {
        "name": "Cam\u00a0Atkinson",
        "team": "DAL",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 117.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.83,
                        "shot_assists_per_60": 1.14,
                        "total_shot_contributions_per_60": 1.97,
                        "chances_per_60": 1.02,
                        "chance_assists_per_60": 0.94
                },
                "passing": {
                        "high_danger_assists_per_60": 1.26
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.7,
                        "rush_offense_per_60": 0.27,
                        "shots_off_hd_passes_per_60": 0.61
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.95,
                        "controlled_entry_percent": 0.28,
                        "controlled_entry_with_chance_percent": 0.24
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.69,
                        "retrievals_per_60": 1.62,
                        "successful_retrieval_percent": 0.57,
                        "exits_per_60": 0.35,
                        "botched_retrievals_per_60": -1.61
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "brayden point": {
        "name": "Brayden\u00a0Point",
        "team": "DET",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 183.8,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.72,
                        "shot_assists_per_60": 0.35,
                        "total_shot_contributions_per_60": 1.07,
                        "chances_per_60": 0.84,
                        "chance_assists_per_60": 0.33
                },
                "passing": {
                        "high_danger_assists_per_60": 0.41
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.69,
                        "rush_offense_per_60": 0.29,
                        "shots_off_hd_passes_per_60": 0.58
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.49,
                        "controlled_entry_percent": 0.3,
                        "controlled_entry_with_chance_percent": 0.33
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.29,
                        "retrievals_per_60": 2.93,
                        "successful_retrieval_percent": 0.67,
                        "exits_per_60": 0.16,
                        "botched_retrievals_per_60": -3.06
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "brandon hagel": {
        "name": "Brandon\u00a0Hagel",
        "team": "EDM",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 181.5,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.919,
                        "goals_against_average": 3.3,
                        "wins": 38,
                        "shutouts": 1
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "anthony cirelli": {
        "name": "Anthony\u00a0Cirelli",
        "team": "FLA",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 147.8,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.27,
                        "shot_assists_per_60": 0.6,
                        "total_shot_contributions_per_60": 1.87,
                        "chances_per_60": 1.52,
                        "chance_assists_per_60": 0.65
                },
                "passing": {
                        "high_danger_assists_per_60": 0.69
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.07,
                        "rush_offense_per_60": 0.54,
                        "shots_off_hd_passes_per_60": 0.92
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.72,
                        "controlled_entry_percent": 0.48,
                        "controlled_entry_with_chance_percent": 0.2
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.57,
                        "retrievals_per_60": 2.76,
                        "successful_retrieval_percent": 0.69,
                        "exits_per_60": 0.31,
                        "botched_retrievals_per_60": -3.78
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "zack bolduc": {
        "name": "Zack\u00a0Bolduc",
        "team": "LAK",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 193.8,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.11,
                        "shot_assists_per_60": 0.46,
                        "total_shot_contributions_per_60": 1.57,
                        "chances_per_60": 1.08,
                        "chance_assists_per_60": 0.62
                },
                "passing": {
                        "high_danger_assists_per_60": 0.44
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.45,
                        "rush_offense_per_60": 0.66,
                        "shots_off_hd_passes_per_60": 1.14
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.39,
                        "controlled_entry_percent": 0.64,
                        "controlled_entry_with_chance_percent": 0.24
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.45,
                        "retrievals_per_60": 2.24,
                        "successful_retrieval_percent": 0.61,
                        "exits_per_60": 0.38,
                        "botched_retrievals_per_60": -3.85
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "tyler tucker": {
        "name": "Tyler\u00a0Tucker",
        "team": "MIN",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 104.2,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.86,
                        "shot_assists_per_60": 0.43,
                        "total_shot_contributions_per_60": 1.29,
                        "chances_per_60": 0.91,
                        "chance_assists_per_60": 0.4
                },
                "passing": {
                        "high_danger_assists_per_60": 0.37
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.07,
                        "rush_offense_per_60": 0.37,
                        "shots_off_hd_passes_per_60": 0.92
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.82,
                        "controlled_entry_percent": 0.52,
                        "controlled_entry_with_chance_percent": 0.32
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.37,
                        "retrievals_per_60": 2.9,
                        "successful_retrieval_percent": 0.62,
                        "exits_per_60": 0.14,
                        "botched_retrievals_per_60": -1.93
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "scott perunovich": {
        "name": "Scott\u00a0Perunovich",
        "team": "MTL",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 138.0,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.69,
                        "shot_assists_per_60": 0.75,
                        "total_shot_contributions_per_60": 1.44,
                        "chances_per_60": 0.77,
                        "chance_assists_per_60": 0.64
                },
                "passing": {
                        "high_danger_assists_per_60": 0.69
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.83,
                        "rush_offense_per_60": 0.44,
                        "shots_off_hd_passes_per_60": 0.6
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.52,
                        "controlled_entry_percent": 0.43,
                        "controlled_entry_with_chance_percent": 0.27
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.81,
                        "retrievals_per_60": 4.2,
                        "successful_retrieval_percent": 0.63,
                        "exits_per_60": 0.36,
                        "botched_retrievals_per_60": -2.6
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "ryan suter": {
        "name": "Ryan\u00a0Suter",
        "team": "NSH",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 154.6,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.917,
                        "goals_against_average": 2.08,
                        "wins": 34,
                        "shutouts": 8
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "robert thomas": {
        "name": "Robert\u00a0Thomas",
        "team": "NJD",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 162.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.51,
                        "shot_assists_per_60": 0.92,
                        "total_shot_contributions_per_60": 2.43,
                        "chances_per_60": 1.35,
                        "chance_assists_per_60": 1.04
                },
                "passing": {
                        "high_danger_assists_per_60": 0.78
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.38,
                        "rush_offense_per_60": 1.17,
                        "shots_off_hd_passes_per_60": 1.22
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.02,
                        "controlled_entry_percent": 0.5,
                        "controlled_entry_with_chance_percent": 0.33
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.56,
                        "retrievals_per_60": 1.62,
                        "successful_retrieval_percent": 0.76,
                        "exits_per_60": 0.18,
                        "botched_retrievals_per_60": -1.85
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "radek faksa": {
        "name": "Radek\u00a0Faksa",
        "team": "NYI",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 194.2,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.67,
                        "shot_assists_per_60": 0.59,
                        "total_shot_contributions_per_60": 2.26,
                        "chances_per_60": 2.11,
                        "chance_assists_per_60": 0.78
                },
                "passing": {
                        "high_danger_assists_per_60": 0.67
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.82,
                        "rush_offense_per_60": 0.8,
                        "shots_off_hd_passes_per_60": 1.76
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.66,
                        "controlled_entry_percent": 0.45,
                        "controlled_entry_with_chance_percent": 0.29
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.08,
                        "retrievals_per_60": 2.56,
                        "successful_retrieval_percent": 0.6,
                        "exits_per_60": 0.35,
                        "botched_retrievals_per_60": -2.82
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "pierre_olivier joseph": {
        "name": "Pierre-Olivier\u00a0Joseph",
        "team": "NYR",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 177.3,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.08,
                        "shot_assists_per_60": 0.59,
                        "total_shot_contributions_per_60": 1.67,
                        "chances_per_60": 1.26,
                        "chance_assists_per_60": 0.55
                },
                "passing": {
                        "high_danger_assists_per_60": 0.6
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.32,
                        "rush_offense_per_60": 0.62,
                        "shots_off_hd_passes_per_60": 0.77
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.76,
                        "controlled_entry_percent": 0.55,
                        "controlled_entry_with_chance_percent": 0.22
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.25,
                        "retrievals_per_60": 2.67,
                        "successful_retrieval_percent": 0.83,
                        "exits_per_60": 0.15,
                        "botched_retrievals_per_60": -2.27
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "philip broberg": {
        "name": "Philip\u00a0Broberg",
        "team": "OTT",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 154.6,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.52,
                        "shot_assists_per_60": 0.9,
                        "total_shot_contributions_per_60": 1.42,
                        "chances_per_60": 0.42,
                        "chance_assists_per_60": 1.2
                },
                "passing": {
                        "high_danger_assists_per_60": 0.92
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.57,
                        "rush_offense_per_60": 0.38,
                        "shots_off_hd_passes_per_60": 0.42
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.61,
                        "controlled_entry_percent": 0.59,
                        "controlled_entry_with_chance_percent": 0.17
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.32,
                        "retrievals_per_60": 3.51,
                        "successful_retrieval_percent": 0.63,
                        "exits_per_60": 0.36,
                        "botched_retrievals_per_60": -3.6
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "pavel buchnevich": {
        "name": "Pavel\u00a0Buchnevich",
        "team": "PHI",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 189.6,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.914,
                        "goals_against_average": 2.8,
                        "wins": 24,
                        "shutouts": 8
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "oskar sundqvist": {
        "name": "Oskar\u00a0Sundqvist",
        "team": "PIT",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 190.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.74,
                        "shot_assists_per_60": 0.54,
                        "total_shot_contributions_per_60": 2.28,
                        "chances_per_60": 1.43,
                        "chance_assists_per_60": 0.63
                },
                "passing": {
                        "high_danger_assists_per_60": 0.45
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 2.16,
                        "rush_offense_per_60": 0.89,
                        "shots_off_hd_passes_per_60": 1.38
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.23,
                        "controlled_entry_percent": 0.51,
                        "controlled_entry_with_chance_percent": 0.31
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.23,
                        "retrievals_per_60": 1.51,
                        "successful_retrieval_percent": 0.66,
                        "exits_per_60": 0.27,
                        "botched_retrievals_per_60": -2.38
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "nick leddy": {
        "name": "Nick\u00a0Leddy",
        "team": "SJS",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 155.3,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.02,
                        "shot_assists_per_60": 0.4,
                        "total_shot_contributions_per_60": 1.42,
                        "chances_per_60": 0.88,
                        "chance_assists_per_60": 0.55
                },
                "passing": {
                        "high_danger_assists_per_60": 0.39
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.98,
                        "rush_offense_per_60": 0.5,
                        "shots_off_hd_passes_per_60": 1.01
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.83,
                        "controlled_entry_percent": 0.42,
                        "controlled_entry_with_chance_percent": 0.26
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.87,
                        "retrievals_per_60": 2.84,
                        "successful_retrieval_percent": 0.85,
                        "exits_per_60": 0.28,
                        "botched_retrievals_per_60": -1.78
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "nathan walker": {
        "name": "Nathan\u00a0Walker",
        "team": "SEA",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 183.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.76,
                        "shot_assists_per_60": 1.1,
                        "total_shot_contributions_per_60": 2.86,
                        "chances_per_60": 1.75,
                        "chance_assists_per_60": 1.19
                },
                "passing": {
                        "high_danger_assists_per_60": 1.08
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.99,
                        "rush_offense_per_60": 0.7,
                        "shots_off_hd_passes_per_60": 1.72
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.26,
                        "controlled_entry_percent": 0.29,
                        "controlled_entry_with_chance_percent": 0.26
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.11,
                        "retrievals_per_60": 2.99,
                        "successful_retrieval_percent": 0.7,
                        "exits_per_60": 0.19,
                        "botched_retrievals_per_60": -1.52
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "matthew kessel": {
        "name": "Matthew\u00a0Kessel",
        "team": "STL",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 171.6,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.24,
                        "shot_assists_per_60": 0.73,
                        "total_shot_contributions_per_60": 0.97,
                        "chances_per_60": 0.2,
                        "chance_assists_per_60": 0.66
                },
                "passing": {
                        "high_danger_assists_per_60": 0.8
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.2,
                        "rush_offense_per_60": 0.15,
                        "shots_off_hd_passes_per_60": 0.26
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.75,
                        "controlled_entry_percent": 0.28,
                        "controlled_entry_with_chance_percent": 0.3
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.21,
                        "retrievals_per_60": 3.18,
                        "successful_retrieval_percent": 0.55,
                        "exits_per_60": 0.31,
                        "botched_retrievals_per_60": -2.72
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "mathieu joseph": {
        "name": "Mathieu\u00a0Joseph",
        "team": "TBL",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 146.2,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.911,
                        "goals_against_average": 3.28,
                        "wins": 41,
                        "shutouts": 4
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "justin faulk": {
        "name": "Justin\u00a0Faulk",
        "team": "TOR",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 110.1,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.86,
                        "shot_assists_per_60": 0.54,
                        "total_shot_contributions_per_60": 1.4,
                        "chances_per_60": 0.66,
                        "chance_assists_per_60": 0.64
                },
                "passing": {
                        "high_danger_assists_per_60": 0.6
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.87,
                        "rush_offense_per_60": 0.64,
                        "shots_off_hd_passes_per_60": 0.84
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.11,
                        "controlled_entry_percent": 0.26,
                        "controlled_entry_with_chance_percent": 0.34
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.15,
                        "retrievals_per_60": 1.85,
                        "successful_retrieval_percent": 0.82,
                        "exits_per_60": 0.26,
                        "botched_retrievals_per_60": -3.5
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jordan kyrou": {
        "name": "Jordan\u00a0Kyrou",
        "team": "VAN",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 171.0,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.48,
                        "shot_assists_per_60": 1.08,
                        "total_shot_contributions_per_60": 2.56,
                        "chances_per_60": 1.1,
                        "chance_assists_per_60": 0.92
                },
                "passing": {
                        "high_danger_assists_per_60": 1.16
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.4,
                        "rush_offense_per_60": 0.82,
                        "shots_off_hd_passes_per_60": 1.07
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.87,
                        "controlled_entry_percent": 0.38,
                        "controlled_entry_with_chance_percent": 0.31
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.69,
                        "retrievals_per_60": 2.71,
                        "successful_retrieval_percent": 0.6,
                        "exits_per_60": 0.11,
                        "botched_retrievals_per_60": -2.69
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jake neighbours": {
        "name": "Jake\u00a0Neighbours",
        "team": "VGK",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 149.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.55,
                        "shot_assists_per_60": 1.06,
                        "total_shot_contributions_per_60": 1.61,
                        "chances_per_60": 0.56,
                        "chance_assists_per_60": 1.27
                },
                "passing": {
                        "high_danger_assists_per_60": 1.26
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.45,
                        "rush_offense_per_60": 0.25,
                        "shots_off_hd_passes_per_60": 0.4
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.12,
                        "controlled_entry_percent": 0.33,
                        "controlled_entry_with_chance_percent": 0.34
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.57,
                        "retrievals_per_60": 1.74,
                        "successful_retrieval_percent": 0.8,
                        "exits_per_60": 0.32,
                        "botched_retrievals_per_60": -3.2
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "dylan holloway": {
        "name": "Dylan\u00a0Holloway",
        "team": "WSH",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 154.8,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.1,
                        "shot_assists_per_60": 0.47,
                        "total_shot_contributions_per_60": 0.57,
                        "chances_per_60": 0.1,
                        "chance_assists_per_60": 0.52
                },
                "passing": {
                        "high_danger_assists_per_60": 0.53
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.12,
                        "rush_offense_per_60": 0.07,
                        "shots_off_hd_passes_per_60": 0.1
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.48,
                        "controlled_entry_percent": 0.64,
                        "controlled_entry_with_chance_percent": 0.2
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.21,
                        "retrievals_per_60": 3.48,
                        "successful_retrieval_percent": 0.73,
                        "exits_per_60": 0.19,
                        "botched_retrievals_per_60": -3.94
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "colton parayko": {
        "name": "Colton\u00a0Parayko",
        "team": "WPG",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 185.1,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.924,
                        "goals_against_average": 2.26,
                        "wins": 23,
                        "shutouts": 3
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "cam fowler": {
        "name": "Cam\u00a0Fowler",
        "team": "ANA",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 191.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.18,
                        "shot_assists_per_60": 0.71,
                        "total_shot_contributions_per_60": 1.89,
                        "chances_per_60": 1.28,
                        "chance_assists_per_60": 0.85
                },
                "passing": {
                        "high_danger_assists_per_60": 0.85
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.96,
                        "rush_offense_per_60": 0.4,
                        "shots_off_hd_passes_per_60": 0.87
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.9,
                        "controlled_entry_percent": 0.29,
                        "controlled_entry_with_chance_percent": 0.27
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.84,
                        "retrievals_per_60": 2.83,
                        "successful_retrieval_percent": 0.79,
                        "exits_per_60": 0.18,
                        "botched_retrievals_per_60": -3.16
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "brayden schenn": {
        "name": "Brayden\u00a0Schenn",
        "team": "ARI",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 109.3,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.81,
                        "shot_assists_per_60": 0.8,
                        "total_shot_contributions_per_60": 1.61,
                        "chances_per_60": 0.91,
                        "chance_assists_per_60": 0.7
                },
                "passing": {
                        "high_danger_assists_per_60": 0.93
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.02,
                        "rush_offense_per_60": 0.54,
                        "shots_off_hd_passes_per_60": 0.74
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.11,
                        "controlled_entry_percent": 0.57,
                        "controlled_entry_with_chance_percent": 0.31
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.01,
                        "retrievals_per_60": 2.96,
                        "successful_retrieval_percent": 0.56,
                        "exits_per_60": 0.37,
                        "botched_retrievals_per_60": -3.13
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "brandon saad": {
        "name": "Brandon\u00a0Saad",
        "team": "BOS",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 174.3,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.73,
                        "shot_assists_per_60": 0.6,
                        "total_shot_contributions_per_60": 2.33,
                        "chances_per_60": 1.82,
                        "chance_assists_per_60": 0.51
                },
                "passing": {
                        "high_danger_assists_per_60": 0.61
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.6,
                        "rush_offense_per_60": 0.89,
                        "shots_off_hd_passes_per_60": 1.34
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.11,
                        "controlled_entry_percent": 0.59,
                        "controlled_entry_with_chance_percent": 0.33
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.63,
                        "retrievals_per_60": 3.0,
                        "successful_retrieval_percent": 0.7,
                        "exits_per_60": 0.23,
                        "botched_retrievals_per_60": -3.99
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "alexey toropchenko": {
        "name": "Alexey\u00a0Toropchenko",
        "team": "BUF",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 105.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.78,
                        "shot_assists_per_60": 0.51,
                        "total_shot_contributions_per_60": 1.29,
                        "chances_per_60": 0.61,
                        "chance_assists_per_60": 0.57
                },
                "passing": {
                        "high_danger_assists_per_60": 0.56
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.73,
                        "rush_offense_per_60": 0.52,
                        "shots_off_hd_passes_per_60": 0.63
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.38,
                        "controlled_entry_percent": 0.58,
                        "controlled_entry_with_chance_percent": 0.23
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.16,
                        "retrievals_per_60": 2.56,
                        "successful_retrieval_percent": 0.75,
                        "exits_per_60": 0.25,
                        "botched_retrievals_per_60": -2.73
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "alexandre texier": {
        "name": "Alexandre\u00a0Texier",
        "team": "CGY",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 130.0,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.915,
                        "goals_against_average": 2.94,
                        "wins": 40,
                        "shutouts": 4
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "will borgen": {
        "name": "Will\u00a0Borgen",
        "team": "CAR",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 150.8,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.13,
                        "shot_assists_per_60": 0.98,
                        "total_shot_contributions_per_60": 2.11,
                        "chances_per_60": 0.96,
                        "chance_assists_per_60": 0.81
                },
                "passing": {
                        "high_danger_assists_per_60": 0.83
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.32,
                        "rush_offense_per_60": 0.72,
                        "shots_off_hd_passes_per_60": 1.11
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.86,
                        "controlled_entry_percent": 0.27,
                        "controlled_entry_with_chance_percent": 0.34
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.34,
                        "retrievals_per_60": 1.57,
                        "successful_retrieval_percent": 0.66,
                        "exits_per_60": 0.39,
                        "botched_retrievals_per_60": -3.21
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "vince dunn": {
        "name": "Vince\u00a0Dunn",
        "team": "CHI",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 115.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.05,
                        "shot_assists_per_60": 0.68,
                        "total_shot_contributions_per_60": 1.73,
                        "chances_per_60": 1.09,
                        "chance_assists_per_60": 0.66
                },
                "passing": {
                        "high_danger_assists_per_60": 0.63
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.2,
                        "rush_offense_per_60": 0.43,
                        "shots_off_hd_passes_per_60": 1.15
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.95,
                        "controlled_entry_percent": 0.36,
                        "controlled_entry_with_chance_percent": 0.17
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.56,
                        "retrievals_per_60": 2.77,
                        "successful_retrieval_percent": 0.72,
                        "exits_per_60": 0.22,
                        "botched_retrievals_per_60": -2.65
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "tye kartye": {
        "name": "Tye\u00a0Kartye",
        "team": "COL",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 192.8,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.49,
                        "shot_assists_per_60": 0.53,
                        "total_shot_contributions_per_60": 2.02,
                        "chances_per_60": 1.1,
                        "chance_assists_per_60": 0.72
                },
                "passing": {
                        "high_danger_assists_per_60": 0.54
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.84,
                        "rush_offense_per_60": 0.93,
                        "shots_off_hd_passes_per_60": 1.08
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.04,
                        "controlled_entry_percent": 0.37,
                        "controlled_entry_with_chance_percent": 0.21
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.52,
                        "retrievals_per_60": 2.31,
                        "successful_retrieval_percent": 0.85,
                        "exits_per_60": 0.33,
                        "botched_retrievals_per_60": -3.67
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "shane wright": {
        "name": "Shane\u00a0Wright",
        "team": "CBJ",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 177.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.35,
                        "shot_assists_per_60": 0.35,
                        "total_shot_contributions_per_60": 0.7,
                        "chances_per_60": 0.42,
                        "chance_assists_per_60": 0.29
                },
                "passing": {
                        "high_danger_assists_per_60": 0.32
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.39,
                        "rush_offense_per_60": 0.17,
                        "shots_off_hd_passes_per_60": 0.31
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.7,
                        "controlled_entry_percent": 0.31,
                        "controlled_entry_with_chance_percent": 0.16
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 4.21,
                        "retrievals_per_60": 4.16,
                        "successful_retrieval_percent": 0.59,
                        "exits_per_60": 0.27,
                        "botched_retrievals_per_60": -3.32
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "ryker evans": {
        "name": "Ryker\u00a0Evans",
        "team": "DAL",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 151.7,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.902,
                        "goals_against_average": 3.28,
                        "wins": 45,
                        "shutouts": 4
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "matty beniers": {
        "name": "Matty\u00a0Beniers",
        "team": "DET",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 158.1,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.0,
                        "shot_assists_per_60": 0.75,
                        "total_shot_contributions_per_60": 1.75,
                        "chances_per_60": 0.81,
                        "chance_assists_per_60": 0.85
                },
                "passing": {
                        "high_danger_assists_per_60": 0.79
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.93,
                        "rush_offense_per_60": 0.37,
                        "shots_off_hd_passes_per_60": 0.98
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.91,
                        "controlled_entry_percent": 0.56,
                        "controlled_entry_with_chance_percent": 0.32
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.17,
                        "retrievals_per_60": 2.27,
                        "successful_retrieval_percent": 0.62,
                        "exits_per_60": 0.19,
                        "botched_retrievals_per_60": -1.73
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "kaapo kakko": {
        "name": "Kaapo\u00a0Kakko",
        "team": "EDM",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 137.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.41,
                        "shot_assists_per_60": 0.91,
                        "total_shot_contributions_per_60": 2.32,
                        "chances_per_60": 1.39,
                        "chance_assists_per_60": 1.19
                },
                "passing": {
                        "high_danger_assists_per_60": 0.97
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.55,
                        "rush_offense_per_60": 0.76,
                        "shots_off_hd_passes_per_60": 1.43
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.82,
                        "controlled_entry_percent": 0.44,
                        "controlled_entry_with_chance_percent": 0.29
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.72,
                        "retrievals_per_60": 1.65,
                        "successful_retrieval_percent": 0.82,
                        "exits_per_60": 0.25,
                        "botched_retrievals_per_60": -1.55
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "joshua mahura": {
        "name": "Joshua\u00a0Mahura",
        "team": "FLA",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 195.3,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.69,
                        "shot_assists_per_60": 0.97,
                        "total_shot_contributions_per_60": 1.66,
                        "chances_per_60": 0.6,
                        "chance_assists_per_60": 1.12
                },
                "passing": {
                        "high_danger_assists_per_60": 0.86
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.79,
                        "rush_offense_per_60": 0.36,
                        "shots_off_hd_passes_per_60": 0.58
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.5,
                        "controlled_entry_percent": 0.41,
                        "controlled_entry_with_chance_percent": 0.2
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.69,
                        "retrievals_per_60": 1.62,
                        "successful_retrieval_percent": 0.6,
                        "exits_per_60": 0.18,
                        "botched_retrievals_per_60": -1.65
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jordan eberle": {
        "name": "Jordan\u00a0Eberle",
        "team": "LAK",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 103.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.29,
                        "shot_assists_per_60": 0.83,
                        "total_shot_contributions_per_60": 1.12,
                        "chances_per_60": 0.2,
                        "chance_assists_per_60": 0.98
                },
                "passing": {
                        "high_danger_assists_per_60": 0.82
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.26,
                        "rush_offense_per_60": 0.13,
                        "shots_off_hd_passes_per_60": 0.31
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.59,
                        "controlled_entry_percent": 0.48,
                        "controlled_entry_with_chance_percent": 0.26
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.3,
                        "retrievals_per_60": 3.24,
                        "successful_retrieval_percent": 0.78,
                        "exits_per_60": 0.12,
                        "botched_retrievals_per_60": -3.6
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jared mccann": {
        "name": "Jared\u00a0McCann",
        "team": "MIN",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 127.2,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.925,
                        "goals_against_average": 2.58,
                        "wins": 41,
                        "shutouts": 5
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jamie oleksiak": {
        "name": "Jamie\u00a0Oleksiak",
        "team": "MTL",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 168.3,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.54,
                        "shot_assists_per_60": 1.14,
                        "total_shot_contributions_per_60": 1.68,
                        "chances_per_60": 0.5,
                        "chance_assists_per_60": 0.92
                },
                "passing": {
                        "high_danger_assists_per_60": 1.27
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.52,
                        "rush_offense_per_60": 0.34,
                        "shots_off_hd_passes_per_60": 0.58
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.86,
                        "controlled_entry_percent": 0.65,
                        "controlled_entry_with_chance_percent": 0.19
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.96,
                        "retrievals_per_60": 2.38,
                        "successful_retrieval_percent": 0.64,
                        "exits_per_60": 0.13,
                        "botched_retrievals_per_60": -1.69
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jaden schwartz": {
        "name": "Jaden\u00a0Schwartz",
        "team": "NSH",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 187.6,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.56,
                        "shot_assists_per_60": 0.44,
                        "total_shot_contributions_per_60": 1.0,
                        "chances_per_60": 0.44,
                        "chance_assists_per_60": 0.44
                },
                "passing": {
                        "high_danger_assists_per_60": 0.43
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.7,
                        "rush_offense_per_60": 0.22,
                        "shots_off_hd_passes_per_60": 0.4
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.91,
                        "controlled_entry_percent": 0.42,
                        "controlled_entry_with_chance_percent": 0.24
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.37,
                        "retrievals_per_60": 1.99,
                        "successful_retrieval_percent": 0.63,
                        "exits_per_60": 0.37,
                        "botched_retrievals_per_60": -2.77
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "eeli tolvanen": {
        "name": "Eeli\u00a0Tolvanen",
        "team": "NJD",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 161.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.54,
                        "shot_assists_per_60": 0.48,
                        "total_shot_contributions_per_60": 2.02,
                        "chances_per_60": 1.85,
                        "chance_assists_per_60": 0.41
                },
                "passing": {
                        "high_danger_assists_per_60": 0.56
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.34,
                        "rush_offense_per_60": 1.14,
                        "shots_off_hd_passes_per_60": 1.23
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.39,
                        "controlled_entry_percent": 0.44,
                        "controlled_entry_with_chance_percent": 0.18
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.38,
                        "retrievals_per_60": 2.88,
                        "successful_retrieval_percent": 0.77,
                        "exits_per_60": 0.21,
                        "botched_retrievals_per_60": -1.94
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "chandler stephenson": {
        "name": "Chandler\u00a0Stephenson",
        "team": "NYI",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 169.2,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.52,
                        "shot_assists_per_60": 0.66,
                        "total_shot_contributions_per_60": 1.18,
                        "chances_per_60": 0.59,
                        "chance_assists_per_60": 0.54
                },
                "passing": {
                        "high_danger_assists_per_60": 0.74
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.68,
                        "rush_offense_per_60": 0.3,
                        "shots_off_hd_passes_per_60": 0.46
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.62,
                        "controlled_entry_percent": 0.42,
                        "controlled_entry_with_chance_percent": 0.19
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.13,
                        "retrievals_per_60": 2.62,
                        "successful_retrieval_percent": 0.68,
                        "exits_per_60": 0.15,
                        "botched_retrievals_per_60": -3.1
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "brandon tanev": {
        "name": "Brandon\u00a0Tanev",
        "team": "NYR",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 184.3,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.925,
                        "goals_against_average": 3.27,
                        "wins": 21,
                        "shutouts": 4
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "brandon montour": {
        "name": "Brandon\u00a0Montour",
        "team": "OTT",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 173.0,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.14,
                        "shot_assists_per_60": 1.01,
                        "total_shot_contributions_per_60": 2.15,
                        "chances_per_60": 1.03,
                        "chance_assists_per_60": 1.36
                },
                "passing": {
                        "high_danger_assists_per_60": 0.95
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.03,
                        "rush_offense_per_60": 0.5,
                        "shots_off_hd_passes_per_60": 1.05
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.93,
                        "controlled_entry_percent": 0.54,
                        "controlled_entry_with_chance_percent": 0.34
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.93,
                        "retrievals_per_60": 2.11,
                        "successful_retrieval_percent": 0.62,
                        "exits_per_60": 0.13,
                        "botched_retrievals_per_60": -1.86
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "andre burakovsky": {
        "name": "Andre\u00a0Burakovsky",
        "team": "PHI",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 172.8,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.23,
                        "shot_assists_per_60": 0.53,
                        "total_shot_contributions_per_60": 1.76,
                        "chances_per_60": 1.21,
                        "chance_assists_per_60": 0.43
                },
                "passing": {
                        "high_danger_assists_per_60": 0.49
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.2,
                        "rush_offense_per_60": 0.67,
                        "shots_off_hd_passes_per_60": 0.99
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.4,
                        "controlled_entry_percent": 0.29,
                        "controlled_entry_with_chance_percent": 0.28
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.73,
                        "retrievals_per_60": 1.54,
                        "successful_retrieval_percent": 0.71,
                        "exits_per_60": 0.29,
                        "botched_retrievals_per_60": -2.65
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "adam larsson": {
        "name": "Adam\u00a0Larsson",
        "team": "PIT",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 104.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.01,
                        "shot_assists_per_60": 1.13,
                        "total_shot_contributions_per_60": 2.14,
                        "chances_per_60": 0.97,
                        "chance_assists_per_60": 0.98
                },
                "passing": {
                        "high_danger_assists_per_60": 1.17
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.28,
                        "rush_offense_per_60": 0.41,
                        "shots_off_hd_passes_per_60": 1.11
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.05,
                        "controlled_entry_percent": 0.26,
                        "controlled_entry_with_chance_percent": 0.31
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.65,
                        "retrievals_per_60": 1.64,
                        "successful_retrieval_percent": 0.59,
                        "exits_per_60": 0.23,
                        "botched_retrievals_per_60": -3.13
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "william eklund": {
        "name": "William\u00a0Eklund",
        "team": "SJS",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 180.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.11,
                        "shot_assists_per_60": 0.69,
                        "total_shot_contributions_per_60": 0.8,
                        "chances_per_60": 0.14,
                        "chance_assists_per_60": 0.77
                },
                "passing": {
                        "high_danger_assists_per_60": 0.63
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.11,
                        "rush_offense_per_60": 0.03,
                        "shots_off_hd_passes_per_60": 0.1
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.37,
                        "controlled_entry_percent": 0.35,
                        "controlled_entry_with_chance_percent": 0.19
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.14,
                        "retrievals_per_60": 3.62,
                        "successful_retrieval_percent": 0.59,
                        "exits_per_60": 0.21,
                        "botched_retrievals_per_60": -1.88
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "will smith": {
        "name": "Will\u00a0Smith",
        "team": "SEA",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 129.1,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.917,
                        "goals_against_average": 3.49,
                        "wins": 19,
                        "shutouts": 2
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "tyler toffoli": {
        "name": "Tyler\u00a0Toffoli",
        "team": "STL",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 183.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.53,
                        "shot_assists_per_60": 1.11,
                        "total_shot_contributions_per_60": 2.64,
                        "chances_per_60": 1.93,
                        "chance_assists_per_60": 0.97
                },
                "passing": {
                        "high_danger_assists_per_60": 0.92
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.56,
                        "rush_offense_per_60": 0.96,
                        "shots_off_hd_passes_per_60": 1.32
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.15,
                        "controlled_entry_percent": 0.56,
                        "controlled_entry_with_chance_percent": 0.27
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.69,
                        "retrievals_per_60": 2.95,
                        "successful_retrieval_percent": 0.56,
                        "exits_per_60": 0.23,
                        "botched_retrievals_per_60": -2.43
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "ty dellandrea": {
        "name": "Ty\u00a0Dellandrea",
        "team": "TBL",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 110.0,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.74,
                        "shot_assists_per_60": 0.65,
                        "total_shot_contributions_per_60": 2.39,
                        "chances_per_60": 1.76,
                        "chance_assists_per_60": 0.87
                },
                "passing": {
                        "high_danger_assists_per_60": 0.72
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 2.16,
                        "rush_offense_per_60": 0.85,
                        "shots_off_hd_passes_per_60": 1.52
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.62,
                        "controlled_entry_percent": 0.29,
                        "controlled_entry_with_chance_percent": 0.16
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.63,
                        "retrievals_per_60": 2.89,
                        "successful_retrieval_percent": 0.74,
                        "exits_per_60": 0.26,
                        "botched_retrievals_per_60": -2.68
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "timothy liljegren": {
        "name": "Timothy\u00a0Liljegren",
        "team": "TOR",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 168.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.62,
                        "shot_assists_per_60": 1.02,
                        "total_shot_contributions_per_60": 1.64,
                        "chances_per_60": 0.46,
                        "chance_assists_per_60": 1.1
                },
                "passing": {
                        "high_danger_assists_per_60": 1.12
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.54,
                        "rush_offense_per_60": 0.33,
                        "shots_off_hd_passes_per_60": 0.44
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.37,
                        "controlled_entry_percent": 0.51,
                        "controlled_entry_with_chance_percent": 0.33
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.38,
                        "retrievals_per_60": 2.14,
                        "successful_retrieval_percent": 0.61,
                        "exits_per_60": 0.16,
                        "botched_retrievals_per_60": -3.25
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "shakir mukhamadullin": {
        "name": "Shakir\u00a0Mukhamadullin",
        "team": "VAN",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 156.2,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.77,
                        "shot_assists_per_60": 0.4,
                        "total_shot_contributions_per_60": 1.17,
                        "chances_per_60": 0.9,
                        "chance_assists_per_60": 0.47
                },
                "passing": {
                        "high_danger_assists_per_60": 0.42
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.77,
                        "rush_offense_per_60": 0.37,
                        "shots_off_hd_passes_per_60": 0.75
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.8,
                        "controlled_entry_percent": 0.56,
                        "controlled_entry_with_chance_percent": 0.19
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 4.53,
                        "retrievals_per_60": 4.0,
                        "successful_retrieval_percent": 0.64,
                        "exits_per_60": 0.21,
                        "botched_retrievals_per_60": -1.91
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "nico sturm": {
        "name": "Nico\u00a0Sturm",
        "team": "VGK",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 113.7,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.925,
                        "goals_against_average": 2.84,
                        "wins": 12,
                        "shutouts": 8
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "mikael granlund": {
        "name": "Mikael\u00a0Granlund",
        "team": "WSH",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 190.7,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.33,
                        "shot_assists_per_60": 0.98,
                        "total_shot_contributions_per_60": 2.31,
                        "chances_per_60": 1.43,
                        "chance_assists_per_60": 1.36
                },
                "passing": {
                        "high_danger_assists_per_60": 1.13
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.72,
                        "rush_offense_per_60": 0.92,
                        "shots_off_hd_passes_per_60": 1.44
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.04,
                        "controlled_entry_percent": 0.31,
                        "controlled_entry_with_chance_percent": 0.15
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.33,
                        "retrievals_per_60": 1.62,
                        "successful_retrieval_percent": 0.81,
                        "exits_per_60": 0.29,
                        "botched_retrievals_per_60": -2.36
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "mario ferraro": {
        "name": "Mario\u00a0Ferraro",
        "team": "WPG",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 116.2,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.37,
                        "shot_assists_per_60": 0.79,
                        "total_shot_contributions_per_60": 2.16,
                        "chances_per_60": 1.62,
                        "chance_assists_per_60": 0.79
                },
                "passing": {
                        "high_danger_assists_per_60": 0.76
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.13,
                        "rush_offense_per_60": 0.43,
                        "shots_off_hd_passes_per_60": 1.14
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.42,
                        "controlled_entry_percent": 0.26,
                        "controlled_entry_with_chance_percent": 0.27
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.97,
                        "retrievals_per_60": 1.77,
                        "successful_retrieval_percent": 0.85,
                        "exits_per_60": 0.34,
                        "botched_retrievals_per_60": -2.89
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "macklin celebrini": {
        "name": "Macklin\u00a0Celebrini",
        "team": "ANA",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 118.2,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.6,
                        "shot_assists_per_60": 0.95,
                        "total_shot_contributions_per_60": 1.55,
                        "chances_per_60": 0.63,
                        "chance_assists_per_60": 1.06
                },
                "passing": {
                        "high_danger_assists_per_60": 1.06
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.68,
                        "rush_offense_per_60": 0.41,
                        "shots_off_hd_passes_per_60": 0.64
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.04,
                        "controlled_entry_percent": 0.47,
                        "controlled_entry_with_chance_percent": 0.18
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.91,
                        "retrievals_per_60": 2.73,
                        "successful_retrieval_percent": 0.72,
                        "exits_per_60": 0.17,
                        "botched_retrievals_per_60": -2.48
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "luke kunin": {
        "name": "Luke\u00a0Kunin",
        "team": "ARI",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 145.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.1,
                        "shot_assists_per_60": 0.82,
                        "total_shot_contributions_per_60": 0.92,
                        "chances_per_60": 0.09,
                        "chance_assists_per_60": 0.97
                },
                "passing": {
                        "high_danger_assists_per_60": 0.93
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.08,
                        "rush_offense_per_60": 0.06,
                        "shots_off_hd_passes_per_60": 0.08
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.76,
                        "controlled_entry_percent": 0.62,
                        "controlled_entry_with_chance_percent": 0.17
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.09,
                        "retrievals_per_60": 3.28,
                        "successful_retrieval_percent": 0.7,
                        "exits_per_60": 0.37,
                        "botched_retrievals_per_60": -1.93
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jan rutta": {
        "name": "Jan\u00a0Rutta",
        "team": "BOS",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 180.7,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.902,
                        "goals_against_average": 2.86,
                        "wins": 26,
                        "shutouts": 7
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jake walman": {
        "name": "Jake\u00a0Walman",
        "team": "BUF",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 116.7,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.85,
                        "shot_assists_per_60": 0.71,
                        "total_shot_contributions_per_60": 1.56,
                        "chances_per_60": 0.73,
                        "chance_assists_per_60": 0.61
                },
                "passing": {
                        "high_danger_assists_per_60": 0.72
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.74,
                        "rush_offense_per_60": 0.5,
                        "shots_off_hd_passes_per_60": 0.71
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.05,
                        "controlled_entry_percent": 0.29,
                        "controlled_entry_with_chance_percent": 0.32
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.41,
                        "retrievals_per_60": 2.9,
                        "successful_retrieval_percent": 0.7,
                        "exits_per_60": 0.31,
                        "botched_retrievals_per_60": -1.91
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jack thompson": {
        "name": "Jack\u00a0Thompson",
        "team": "CGY",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 164.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.78,
                        "shot_assists_per_60": 0.75,
                        "total_shot_contributions_per_60": 2.53,
                        "chances_per_60": 1.99,
                        "chance_assists_per_60": 0.8
                },
                "passing": {
                        "high_danger_assists_per_60": 0.77
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 2.23,
                        "rush_offense_per_60": 1.08,
                        "shots_off_hd_passes_per_60": 1.68
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.25,
                        "controlled_entry_percent": 0.38,
                        "controlled_entry_with_chance_percent": 0.32
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.83,
                        "retrievals_per_60": 1.54,
                        "successful_retrieval_percent": 0.79,
                        "exits_per_60": 0.26,
                        "botched_retrievals_per_60": -2.82
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "henry thrun": {
        "name": "Henry\u00a0Thrun",
        "team": "CAR",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 194.7,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.58,
                        "shot_assists_per_60": 1.06,
                        "total_shot_contributions_per_60": 2.64,
                        "chances_per_60": 1.24,
                        "chance_assists_per_60": 0.91
                },
                "passing": {
                        "high_danger_assists_per_60": 1.0
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 2.01,
                        "rush_offense_per_60": 0.95,
                        "shots_off_hd_passes_per_60": 1.5
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.85,
                        "controlled_entry_percent": 0.44,
                        "controlled_entry_with_chance_percent": 0.29
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.19,
                        "retrievals_per_60": 2.19,
                        "successful_retrieval_percent": 0.66,
                        "exits_per_60": 0.27,
                        "botched_retrievals_per_60": -2.07
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "fabian zetterlund": {
        "name": "Fabian\u00a0Zetterlund",
        "team": "CHI",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 169.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.8,
                        "shot_assists_per_60": 0.58,
                        "total_shot_contributions_per_60": 1.38,
                        "chances_per_60": 0.92,
                        "chance_assists_per_60": 0.67
                },
                "passing": {
                        "high_danger_assists_per_60": 0.51
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.9,
                        "rush_offense_per_60": 0.56,
                        "shots_off_hd_passes_per_60": 0.61
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.73,
                        "controlled_entry_percent": 0.57,
                        "controlled_entry_with_chance_percent": 0.28
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.74,
                        "retrievals_per_60": 2.54,
                        "successful_retrieval_percent": 0.77,
                        "exits_per_60": 0.21,
                        "botched_retrievals_per_60": -3.63
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "collin graf": {
        "name": "Collin\u00a0Graf",
        "team": "COL",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 152.4,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.91,
                        "goals_against_average": 2.6,
                        "wins": 30,
                        "shutouts": 3
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "cody ceci": {
        "name": "Cody\u00a0Ceci",
        "team": "CBJ",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 111.1,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.0,
                        "shot_assists_per_60": 0.42,
                        "total_shot_contributions_per_60": 1.42,
                        "chances_per_60": 0.94,
                        "chance_assists_per_60": 0.54
                },
                "passing": {
                        "high_danger_assists_per_60": 0.49
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.3,
                        "rush_offense_per_60": 0.48,
                        "shots_off_hd_passes_per_60": 0.9
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.26,
                        "controlled_entry_percent": 0.31,
                        "controlled_entry_with_chance_percent": 0.2
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.82,
                        "retrievals_per_60": 2.27,
                        "successful_retrieval_percent": 0.62,
                        "exits_per_60": 0.29,
                        "botched_retrievals_per_60": -1.95
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "carl grundstrom": {
        "name": "Carl\u00a0Grundstrom",
        "team": "DAL",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 182.7,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.31,
                        "shot_assists_per_60": 1.04,
                        "total_shot_contributions_per_60": 2.35,
                        "chances_per_60": 1.45,
                        "chance_assists_per_60": 1.16
                },
                "passing": {
                        "high_danger_assists_per_60": 1.07
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.7,
                        "rush_offense_per_60": 0.92,
                        "shots_off_hd_passes_per_60": 1.19
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.85,
                        "controlled_entry_percent": 0.43,
                        "controlled_entry_with_chance_percent": 0.23
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.89,
                        "retrievals_per_60": 2.26,
                        "successful_retrieval_percent": 0.69,
                        "exits_per_60": 0.27,
                        "botched_retrievals_per_60": -1.81
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "barclay goodrow": {
        "name": "Barclay\u00a0Goodrow",
        "team": "DET",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 125.8,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.5,
                        "shot_assists_per_60": 1.16,
                        "total_shot_contributions_per_60": 1.66,
                        "chances_per_60": 0.55,
                        "chance_assists_per_60": 1.48
                },
                "passing": {
                        "high_danger_assists_per_60": 1.12
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.51,
                        "rush_offense_per_60": 0.17,
                        "shots_off_hd_passes_per_60": 0.39
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.94,
                        "controlled_entry_percent": 0.39,
                        "controlled_entry_with_chance_percent": 0.17
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.97,
                        "retrievals_per_60": 2.18,
                        "successful_retrieval_percent": 0.6,
                        "exits_per_60": 0.24,
                        "botched_retrievals_per_60": -1.88
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "alexander wennberg": {
        "name": "Alexander\u00a0Wennberg",
        "team": "EDM",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 169.7,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.63,
                        "shot_assists_per_60": 0.21,
                        "total_shot_contributions_per_60": 0.84,
                        "chances_per_60": 0.74,
                        "chance_assists_per_60": 0.21
                },
                "passing": {
                        "high_danger_assists_per_60": 0.18
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.66,
                        "rush_offense_per_60": 0.32,
                        "shots_off_hd_passes_per_60": 0.61
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.32,
                        "controlled_entry_percent": 0.57,
                        "controlled_entry_with_chance_percent": 0.27
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.31,
                        "retrievals_per_60": 3.91,
                        "successful_retrieval_percent": 0.8,
                        "exits_per_60": 0.33,
                        "botched_retrievals_per_60": -3.41
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "sidney crosby": {
        "name": "Sidney\u00a0Crosby",
        "team": "FLA",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 137.6,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.921,
                        "goals_against_average": 2.24,
                        "wins": 39,
                        "shutouts": 1
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "ryan shea": {
        "name": "Ryan\u00a0Shea",
        "team": "LAK",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 174.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.62,
                        "shot_assists_per_60": 0.9,
                        "total_shot_contributions_per_60": 1.52,
                        "chances_per_60": 0.5,
                        "chance_assists_per_60": 0.79
                },
                "passing": {
                        "high_danger_assists_per_60": 0.76
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.84,
                        "rush_offense_per_60": 0.48,
                        "shots_off_hd_passes_per_60": 0.58
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.66,
                        "controlled_entry_percent": 0.6,
                        "controlled_entry_with_chance_percent": 0.23
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.15,
                        "retrievals_per_60": 1.85,
                        "successful_retrieval_percent": 0.77,
                        "exits_per_60": 0.21,
                        "botched_retrievals_per_60": -3.7
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "ryan graves": {
        "name": "Ryan\u00a0Graves",
        "team": "MIN",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 131.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.14,
                        "shot_assists_per_60": 0.61,
                        "total_shot_contributions_per_60": 1.75,
                        "chances_per_60": 0.92,
                        "chance_assists_per_60": 0.53
                },
                "passing": {
                        "high_danger_assists_per_60": 0.6
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.96,
                        "rush_offense_per_60": 0.87,
                        "shots_off_hd_passes_per_60": 1.08
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.27,
                        "controlled_entry_percent": 0.38,
                        "controlled_entry_with_chance_percent": 0.28
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.67,
                        "retrievals_per_60": 2.63,
                        "successful_retrieval_percent": 0.61,
                        "exits_per_60": 0.31,
                        "botched_retrievals_per_60": -3.31
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "rickard rakell": {
        "name": "Rickard\u00a0Rakell",
        "team": "MTL",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 162.6,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.04,
                        "shot_assists_per_60": 0.77,
                        "total_shot_contributions_per_60": 1.81,
                        "chances_per_60": 0.97,
                        "chance_assists_per_60": 0.74
                },
                "passing": {
                        "high_danger_assists_per_60": 0.7
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.03,
                        "rush_offense_per_60": 0.33,
                        "shots_off_hd_passes_per_60": 1.14
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.44,
                        "controlled_entry_percent": 0.25,
                        "controlled_entry_with_chance_percent": 0.21
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.7,
                        "retrievals_per_60": 1.68,
                        "successful_retrieval_percent": 0.75,
                        "exits_per_60": 0.13,
                        "botched_retrievals_per_60": -2.57
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "philip tomasino": {
        "name": "Philip\u00a0Tomasino",
        "team": "NSH",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 172.8,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.28,
                        "shot_assists_per_60": 0.54,
                        "total_shot_contributions_per_60": 0.82,
                        "chances_per_60": 0.31,
                        "chance_assists_per_60": 0.57
                },
                "passing": {
                        "high_danger_assists_per_60": 0.54
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.29,
                        "rush_offense_per_60": 0.21,
                        "shots_off_hd_passes_per_60": 0.28
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.58,
                        "controlled_entry_percent": 0.63,
                        "controlled_entry_with_chance_percent": 0.31
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.9,
                        "retrievals_per_60": 3.83,
                        "successful_retrieval_percent": 0.57,
                        "exits_per_60": 0.39,
                        "botched_retrievals_per_60": -3.17
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "po joseph": {
        "name": "P.O\u00a0Joseph",
        "team": "NJD",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 180.9,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.917,
                        "goals_against_average": 2.79,
                        "wins": 24,
                        "shutouts": 4
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "owen pickering": {
        "name": "Owen\u00a0Pickering",
        "team": "NYI",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 142.6,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.95,
                        "shot_assists_per_60": 0.54,
                        "total_shot_contributions_per_60": 1.49,
                        "chances_per_60": 1.21,
                        "chance_assists_per_60": 0.58
                },
                "passing": {
                        "high_danger_assists_per_60": 0.56
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.11,
                        "rush_offense_per_60": 0.42,
                        "shots_off_hd_passes_per_60": 0.79
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.98,
                        "controlled_entry_percent": 0.34,
                        "controlled_entry_with_chance_percent": 0.28
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.13,
                        "retrievals_per_60": 2.42,
                        "successful_retrieval_percent": 0.72,
                        "exits_per_60": 0.29,
                        "botched_retrievals_per_60": -3.57
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "noel acciari": {
        "name": "Noel\u00a0Acciari",
        "team": "NYR",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 148.8,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.93,
                        "shot_assists_per_60": 0.87,
                        "total_shot_contributions_per_60": 1.8,
                        "chances_per_60": 1.18,
                        "chance_assists_per_60": 1.06
                },
                "passing": {
                        "high_danger_assists_per_60": 0.74
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.75,
                        "rush_offense_per_60": 0.29,
                        "shots_off_hd_passes_per_60": 0.66
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.95,
                        "controlled_entry_percent": 0.62,
                        "controlled_entry_with_chance_percent": 0.34
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.92,
                        "retrievals_per_60": 2.01,
                        "successful_retrieval_percent": 0.6,
                        "exits_per_60": 0.12,
                        "botched_retrievals_per_60": -1.92
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "michael bunting": {
        "name": "Michael\u00a0Bunting",
        "team": "OTT",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 123.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.29,
                        "shot_assists_per_60": 0.55,
                        "total_shot_contributions_per_60": 1.84,
                        "chances_per_60": 1.01,
                        "chance_assists_per_60": 0.61
                },
                "passing": {
                        "high_danger_assists_per_60": 0.58
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.04,
                        "rush_offense_per_60": 0.56,
                        "shots_off_hd_passes_per_60": 1.23
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.27,
                        "controlled_entry_percent": 0.32,
                        "controlled_entry_with_chance_percent": 0.23
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.68,
                        "retrievals_per_60": 1.66,
                        "successful_retrieval_percent": 0.65,
                        "exits_per_60": 0.17,
                        "botched_retrievals_per_60": -1.81
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "matt grzelcyk": {
        "name": "Matt\u00a0Grzelcyk",
        "team": "PHI",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 135.6,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.72,
                        "shot_assists_per_60": 0.76,
                        "total_shot_contributions_per_60": 1.48,
                        "chances_per_60": 0.53,
                        "chance_assists_per_60": 0.61
                },
                "passing": {
                        "high_danger_assists_per_60": 0.85
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.62,
                        "rush_offense_per_60": 0.41,
                        "shots_off_hd_passes_per_60": 0.5
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.79,
                        "controlled_entry_percent": 0.4,
                        "controlled_entry_with_chance_percent": 0.3
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.68,
                        "retrievals_per_60": 3.92,
                        "successful_retrieval_percent": 0.55,
                        "exits_per_60": 0.1,
                        "botched_retrievals_per_60": -2.13
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "kris letang": {
        "name": "Kris\u00a0Letang",
        "team": "PIT",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 153.1,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.904,
                        "goals_against_average": 2.26,
                        "wins": 26,
                        "shutouts": 0
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "kevin hayes": {
        "name": "Kevin\u00a0Hayes",
        "team": "SJS",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 145.1,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.17,
                        "shot_assists_per_60": 0.44,
                        "total_shot_contributions_per_60": 1.61,
                        "chances_per_60": 1.34,
                        "chance_assists_per_60": 0.53
                },
                "passing": {
                        "high_danger_assists_per_60": 0.48
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.38,
                        "rush_offense_per_60": 0.44,
                        "shots_off_hd_passes_per_60": 0.96
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.73,
                        "controlled_entry_percent": 0.53,
                        "controlled_entry_with_chance_percent": 0.17
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.42,
                        "retrievals_per_60": 1.61,
                        "successful_retrieval_percent": 0.55,
                        "exits_per_60": 0.4,
                        "botched_retrievals_per_60": -3.7
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "evgeni malkin": {
        "name": "Evgeni\u00a0Malkin",
        "team": "SEA",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 170.2,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.91,
                        "shot_assists_per_60": 0.51,
                        "total_shot_contributions_per_60": 1.42,
                        "chances_per_60": 0.86,
                        "chance_assists_per_60": 0.48
                },
                "passing": {
                        "high_danger_assists_per_60": 0.54
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.22,
                        "rush_offense_per_60": 0.29,
                        "shots_off_hd_passes_per_60": 0.84
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.71,
                        "controlled_entry_percent": 0.29,
                        "controlled_entry_with_chance_percent": 0.28
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.78,
                        "retrievals_per_60": 2.21,
                        "successful_retrieval_percent": 0.7,
                        "exits_per_60": 0.1,
                        "botched_retrievals_per_60": -2.29
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "erik karlsson": {
        "name": "Erik\u00a0Karlsson",
        "team": "STL",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 171.8,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.23,
                        "shot_assists_per_60": 0.5,
                        "total_shot_contributions_per_60": 1.73,
                        "chances_per_60": 1.19,
                        "chance_assists_per_60": 0.62
                },
                "passing": {
                        "high_danger_assists_per_60": 0.51
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.07,
                        "rush_offense_per_60": 0.46,
                        "shots_off_hd_passes_per_60": 1.09
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.82,
                        "controlled_entry_percent": 0.28,
                        "controlled_entry_with_chance_percent": 0.31
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.54,
                        "retrievals_per_60": 1.61,
                        "successful_retrieval_percent": 0.83,
                        "exits_per_60": 0.2,
                        "botched_retrievals_per_60": -1.65
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "drew o'connor": {
        "name": "Drew\u00a0O'Connor",
        "team": "TBL",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 123.1,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.33,
                        "shot_assists_per_60": 0.41,
                        "total_shot_contributions_per_60": 0.74,
                        "chances_per_60": 0.35,
                        "chance_assists_per_60": 0.54
                },
                "passing": {
                        "high_danger_assists_per_60": 0.33
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.29,
                        "rush_offense_per_60": 0.14,
                        "shots_off_hd_passes_per_60": 0.27
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.43,
                        "controlled_entry_percent": 0.47,
                        "controlled_entry_with_chance_percent": 0.16
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.93,
                        "retrievals_per_60": 4.05,
                        "successful_retrieval_percent": 0.59,
                        "exits_per_60": 0.25,
                        "botched_retrievals_per_60": -3.24
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "cody glass": {
        "name": "Cody\u00a0Glass",
        "team": "TOR",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 166.3,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.929,
                        "goals_against_average": 2.87,
                        "wins": 36,
                        "shutouts": 6
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "bryan rust": {
        "name": "Bryan\u00a0Rust",
        "team": "VAN",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 192.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.06,
                        "shot_assists_per_60": 0.68,
                        "total_shot_contributions_per_60": 1.74,
                        "chances_per_60": 0.94,
                        "chance_assists_per_60": 0.93
                },
                "passing": {
                        "high_danger_assists_per_60": 0.78
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.87,
                        "rush_offense_per_60": 0.75,
                        "shots_off_hd_passes_per_60": 0.79
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.2,
                        "controlled_entry_percent": 0.49,
                        "controlled_entry_with_chance_percent": 0.31
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.74,
                        "retrievals_per_60": 2.14,
                        "successful_retrieval_percent": 0.68,
                        "exits_per_60": 0.2,
                        "botched_retrievals_per_60": -1.66
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "blake lizotte": {
        "name": "Blake\u00a0Lizotte",
        "team": "VGK",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 150.2,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.68,
                        "shot_assists_per_60": 0.52,
                        "total_shot_contributions_per_60": 2.2,
                        "chances_per_60": 1.36,
                        "chance_assists_per_60": 0.59
                },
                "passing": {
                        "high_danger_assists_per_60": 0.58
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 2.21,
                        "rush_offense_per_60": 1.07,
                        "shots_off_hd_passes_per_60": 1.64
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.61,
                        "controlled_entry_percent": 0.35,
                        "controlled_entry_with_chance_percent": 0.34
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.21,
                        "retrievals_per_60": 2.09,
                        "successful_retrieval_percent": 0.65,
                        "exits_per_60": 0.24,
                        "botched_retrievals_per_60": -3.17
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "anthony beauvillier": {
        "name": "Anthony\u00a0Beauvillier",
        "team": "WSH",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 197.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.23,
                        "shot_assists_per_60": 0.87,
                        "total_shot_contributions_per_60": 2.1,
                        "chances_per_60": 1.17,
                        "chance_assists_per_60": 0.84
                },
                "passing": {
                        "high_danger_assists_per_60": 0.7
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.03,
                        "rush_offense_per_60": 0.68,
                        "shots_off_hd_passes_per_60": 0.86
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.26,
                        "controlled_entry_percent": 0.46,
                        "controlled_entry_with_chance_percent": 0.29
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.81,
                        "retrievals_per_60": 1.81,
                        "successful_retrieval_percent": 0.74,
                        "exits_per_60": 0.35,
                        "botched_retrievals_per_60": -3.73
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "tyson foerster": {
        "name": "Tyson\u00a0Foerster",
        "team": "WPG",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 136.3,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.54,
                        "shot_assists_per_60": 0.6,
                        "total_shot_contributions_per_60": 1.14,
                        "chances_per_60": 0.59,
                        "chance_assists_per_60": 0.57
                },
                "passing": {
                        "high_danger_assists_per_60": 0.54
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.62,
                        "rush_offense_per_60": 0.29,
                        "shots_off_hd_passes_per_60": 0.42
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.7,
                        "controlled_entry_percent": 0.63,
                        "controlled_entry_with_chance_percent": 0.32
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.58,
                        "retrievals_per_60": 2.8,
                        "successful_retrieval_percent": 0.67,
                        "exits_per_60": 0.1,
                        "botched_retrievals_per_60": -1.86
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "travis sanheim": {
        "name": "Travis\u00a0Sanheim",
        "team": "ANA",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 183.2,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.913,
                        "goals_against_average": 3.03,
                        "wins": 43,
                        "shutouts": 2
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "travis konecny": {
        "name": "Travis\u00a0Konecny",
        "team": "ARI",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 175.8,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.82,
                        "shot_assists_per_60": 1.15,
                        "total_shot_contributions_per_60": 1.97,
                        "chances_per_60": 0.63,
                        "chance_assists_per_60": 1.3
                },
                "passing": {
                        "high_danger_assists_per_60": 1.05
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.92,
                        "rush_offense_per_60": 0.58,
                        "shots_off_hd_passes_per_60": 0.58
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.76,
                        "controlled_entry_percent": 0.62,
                        "controlled_entry_with_chance_percent": 0.31
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.19,
                        "retrievals_per_60": 2.89,
                        "successful_retrieval_percent": 0.67,
                        "exits_per_60": 0.31,
                        "botched_retrievals_per_60": -1.76
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "sean couturier": {
        "name": "Sean\u00a0Couturier",
        "team": "BOS",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 189.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.7,
                        "shot_assists_per_60": 0.57,
                        "total_shot_contributions_per_60": 2.27,
                        "chances_per_60": 1.57,
                        "chance_assists_per_60": 0.73
                },
                "passing": {
                        "high_danger_assists_per_60": 0.66
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 2.27,
                        "rush_offense_per_60": 0.97,
                        "shots_off_hd_passes_per_60": 1.81
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.34,
                        "controlled_entry_percent": 0.38,
                        "controlled_entry_with_chance_percent": 0.29
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.52,
                        "retrievals_per_60": 2.32,
                        "successful_retrieval_percent": 0.59,
                        "exits_per_60": 0.27,
                        "botched_retrievals_per_60": -2.27
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "scott laughton": {
        "name": "Scott\u00a0Laughton",
        "team": "BUF",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 150.2,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.27,
                        "shot_assists_per_60": 0.93,
                        "total_shot_contributions_per_60": 2.2,
                        "chances_per_60": 1.05,
                        "chance_assists_per_60": 1.16
                },
                "passing": {
                        "high_danger_assists_per_60": 0.76
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.68,
                        "rush_offense_per_60": 0.95,
                        "shots_off_hd_passes_per_60": 1.05
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.13,
                        "controlled_entry_percent": 0.59,
                        "controlled_entry_with_chance_percent": 0.22
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.01,
                        "retrievals_per_60": 2.21,
                        "successful_retrieval_percent": 0.8,
                        "exits_per_60": 0.29,
                        "botched_retrievals_per_60": -3.15
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "ryan poehling": {
        "name": "Ryan\u00a0Poehling",
        "team": "CGY",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 167.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.58,
                        "shot_assists_per_60": 0.79,
                        "total_shot_contributions_per_60": 1.37,
                        "chances_per_60": 0.67,
                        "chance_assists_per_60": 1.01
                },
                "passing": {
                        "high_danger_assists_per_60": 0.67
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.56,
                        "rush_offense_per_60": 0.36,
                        "shots_off_hd_passes_per_60": 0.6
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.66,
                        "controlled_entry_percent": 0.25,
                        "controlled_entry_with_chance_percent": 0.15
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.69,
                        "retrievals_per_60": 3.78,
                        "successful_retrieval_percent": 0.66,
                        "exits_per_60": 0.11,
                        "botched_retrievals_per_60": -3.58
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "rasmus ristolainen": {
        "name": "Rasmus\u00a0Ristolainen",
        "team": "CAR",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 114.3,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.925,
                        "goals_against_average": 3.11,
                        "wins": 11,
                        "shutouts": 0
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "owen tippett": {
        "name": "Owen\u00a0Tippett",
        "team": "CHI",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 195.0,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.86,
                        "shot_assists_per_60": 1.16,
                        "total_shot_contributions_per_60": 2.02,
                        "chances_per_60": 1.05,
                        "chance_assists_per_60": 1.26
                },
                "passing": {
                        "high_danger_assists_per_60": 1.3
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.94,
                        "rush_offense_per_60": 0.28,
                        "shots_off_hd_passes_per_60": 0.82
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.7,
                        "controlled_entry_percent": 0.52,
                        "controlled_entry_with_chance_percent": 0.22
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.74,
                        "retrievals_per_60": 1.7,
                        "successful_retrieval_percent": 0.64,
                        "exits_per_60": 0.34,
                        "botched_retrievals_per_60": -2.17
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "noah cates": {
        "name": "Noah\u00a0Cates",
        "team": "COL",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 131.8,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.46,
                        "shot_assists_per_60": 0.73,
                        "total_shot_contributions_per_60": 2.19,
                        "chances_per_60": 1.55,
                        "chance_assists_per_60": 0.87
                },
                "passing": {
                        "high_danger_assists_per_60": 0.72
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.89,
                        "rush_offense_per_60": 0.46,
                        "shots_off_hd_passes_per_60": 1.6
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.9,
                        "controlled_entry_percent": 0.31,
                        "controlled_entry_with_chance_percent": 0.3
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.99,
                        "retrievals_per_60": 2.04,
                        "successful_retrieval_percent": 0.79,
                        "exits_per_60": 0.18,
                        "botched_retrievals_per_60": -3.73
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "nick seeler": {
        "name": "Nick\u00a0Seeler",
        "team": "CBJ",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 125.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.78,
                        "shot_assists_per_60": 0.45,
                        "total_shot_contributions_per_60": 2.23,
                        "chances_per_60": 1.65,
                        "chance_assists_per_60": 0.63
                },
                "passing": {
                        "high_danger_assists_per_60": 0.44
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.72,
                        "rush_offense_per_60": 1.42,
                        "shots_off_hd_passes_per_60": 1.28
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.68,
                        "controlled_entry_percent": 0.56,
                        "controlled_entry_with_chance_percent": 0.27
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.16,
                        "retrievals_per_60": 2.29,
                        "successful_retrieval_percent": 0.7,
                        "exits_per_60": 0.39,
                        "botched_retrievals_per_60": -3.82
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "morgan frost": {
        "name": "Morgan\u00a0Frost",
        "team": "DAL",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 151.2,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.68,
                        "shot_assists_per_60": 0.6,
                        "total_shot_contributions_per_60": 1.28,
                        "chances_per_60": 0.57,
                        "chance_assists_per_60": 0.55
                },
                "passing": {
                        "high_danger_assists_per_60": 0.65
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.64,
                        "rush_offense_per_60": 0.41,
                        "shots_off_hd_passes_per_60": 0.71
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.62,
                        "controlled_entry_percent": 0.32,
                        "controlled_entry_with_chance_percent": 0.31
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 4.08,
                        "retrievals_per_60": 3.96,
                        "successful_retrieval_percent": 0.71,
                        "exits_per_60": 0.37,
                        "botched_retrievals_per_60": -3.19
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "matvei michkov": {
        "name": "Matvei\u00a0Michkov",
        "team": "DET",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 186.3,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.91,
                        "goals_against_average": 3.14,
                        "wins": 13,
                        "shutouts": 0
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "joel farabee": {
        "name": "Joel\u00a0Farabee",
        "team": "EDM",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 172.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.77,
                        "shot_assists_per_60": 0.41,
                        "total_shot_contributions_per_60": 2.18,
                        "chances_per_60": 1.9,
                        "chance_assists_per_60": 0.47
                },
                "passing": {
                        "high_danger_assists_per_60": 0.49
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.56,
                        "rush_offense_per_60": 0.57,
                        "shots_off_hd_passes_per_60": 1.65
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.84,
                        "controlled_entry_percent": 0.42,
                        "controlled_entry_with_chance_percent": 0.26
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.19,
                        "retrievals_per_60": 2.95,
                        "successful_retrieval_percent": 0.73,
                        "exits_per_60": 0.17,
                        "botched_retrievals_per_60": -2.91
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jamie drysdale": {
        "name": "Jamie\u00a0Drysdale",
        "team": "FLA",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 142.2,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.68,
                        "shot_assists_per_60": 0.52,
                        "total_shot_contributions_per_60": 1.2,
                        "chances_per_60": 0.73,
                        "chance_assists_per_60": 0.61
                },
                "passing": {
                        "high_danger_assists_per_60": 0.51
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.67,
                        "rush_offense_per_60": 0.42,
                        "shots_off_hd_passes_per_60": 0.66
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.31,
                        "controlled_entry_percent": 0.48,
                        "controlled_entry_with_chance_percent": 0.23
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.43,
                        "retrievals_per_60": 2.67,
                        "successful_retrieval_percent": 0.82,
                        "exits_per_60": 0.21,
                        "botched_retrievals_per_60": -2.99
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "garnet hathaway": {
        "name": "Garnet\u00a0Hathaway",
        "team": "LAK",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 190.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.85,
                        "shot_assists_per_60": 0.83,
                        "total_shot_contributions_per_60": 1.68,
                        "chances_per_60": 0.75,
                        "chance_assists_per_60": 0.86
                },
                "passing": {
                        "high_danger_assists_per_60": 0.78
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.0,
                        "rush_offense_per_60": 0.31,
                        "shots_off_hd_passes_per_60": 0.9
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.23,
                        "controlled_entry_percent": 0.54,
                        "controlled_entry_with_chance_percent": 0.28
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.05,
                        "retrievals_per_60": 1.79,
                        "successful_retrieval_percent": 0.81,
                        "exits_per_60": 0.2,
                        "botched_retrievals_per_60": -1.75
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "emil andrae": {
        "name": "Emil\u00a0Andrae",
        "team": "MIN",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 182.3,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.3,
                        "shot_assists_per_60": 0.79,
                        "total_shot_contributions_per_60": 1.09,
                        "chances_per_60": 0.22,
                        "chance_assists_per_60": 0.94
                },
                "passing": {
                        "high_danger_assists_per_60": 0.79
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.36,
                        "rush_offense_per_60": 0.2,
                        "shots_off_hd_passes_per_60": 0.27
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.68,
                        "controlled_entry_percent": 0.4,
                        "controlled_entry_with_chance_percent": 0.18
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.98,
                        "retrievals_per_60": 4.12,
                        "successful_retrieval_percent": 0.62,
                        "exits_per_60": 0.22,
                        "botched_retrievals_per_60": -3.13
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "egor zamula": {
        "name": "Egor\u00a0Zamula",
        "team": "MTL",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 198.6,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.901,
                        "goals_against_average": 2.56,
                        "wins": 36,
                        "shutouts": 4
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "cam york": {
        "name": "Cam\u00a0York",
        "team": "NSH",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 112.0,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.64,
                        "shot_assists_per_60": 1.08,
                        "total_shot_contributions_per_60": 2.72,
                        "chances_per_60": 1.55,
                        "chance_assists_per_60": 1.06
                },
                "passing": {
                        "high_danger_assists_per_60": 1.13
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.74,
                        "rush_offense_per_60": 0.8,
                        "shots_off_hd_passes_per_60": 1.5
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.68,
                        "controlled_entry_percent": 0.57,
                        "controlled_entry_with_chance_percent": 0.19
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.06,
                        "retrievals_per_60": 2.86,
                        "successful_retrieval_percent": 0.7,
                        "exits_per_60": 0.34,
                        "botched_retrievals_per_60": -3.62
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "bobby brink": {
        "name": "Bobby\u00a0Brink",
        "team": "NJD",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 126.6,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.68,
                        "shot_assists_per_60": 0.48,
                        "total_shot_contributions_per_60": 2.16,
                        "chances_per_60": 1.5,
                        "chance_assists_per_60": 0.66
                },
                "passing": {
                        "high_danger_assists_per_60": 0.51
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.56,
                        "rush_offense_per_60": 0.91,
                        "shots_off_hd_passes_per_60": 1.79
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.24,
                        "controlled_entry_percent": 0.58,
                        "controlled_entry_with_chance_percent": 0.16
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.83,
                        "retrievals_per_60": 2.59,
                        "successful_retrieval_percent": 0.8,
                        "exits_per_60": 0.31,
                        "botched_retrievals_per_60": -1.52
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "tyler kleven": {
        "name": "Tyler\u00a0Kleven",
        "team": "NYI",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 119.6,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.07,
                        "shot_assists_per_60": 0.99,
                        "total_shot_contributions_per_60": 2.06,
                        "chances_per_60": 0.76,
                        "chance_assists_per_60": 0.97
                },
                "passing": {
                        "high_danger_assists_per_60": 0.91
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.9,
                        "rush_offense_per_60": 0.78,
                        "shots_off_hd_passes_per_60": 0.9
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.15,
                        "controlled_entry_percent": 0.64,
                        "controlled_entry_with_chance_percent": 0.25
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.7,
                        "retrievals_per_60": 2.94,
                        "successful_retrieval_percent": 0.6,
                        "exits_per_60": 0.13,
                        "botched_retrievals_per_60": -2.52
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "travis hamonic": {
        "name": "Travis\u00a0Hamonic",
        "team": "NYR",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 123.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.49,
                        "shot_assists_per_60": 0.44,
                        "total_shot_contributions_per_60": 0.93,
                        "chances_per_60": 0.57,
                        "chance_assists_per_60": 0.54
                },
                "passing": {
                        "high_danger_assists_per_60": 0.43
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.65,
                        "rush_offense_per_60": 0.34,
                        "shots_off_hd_passes_per_60": 0.5
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.46,
                        "controlled_entry_percent": 0.31,
                        "controlled_entry_with_chance_percent": 0.3
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 4.01,
                        "retrievals_per_60": 3.73,
                        "successful_retrieval_percent": 0.8,
                        "exits_per_60": 0.28,
                        "botched_retrievals_per_60": -2.03
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "tim stützle": {
        "name": "Tim\u00a0St\u00fctzle",
        "team": "OTT",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 144.7,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.927,
                        "goals_against_average": 2.11,
                        "wins": 12,
                        "shutouts": 7
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "thomas chabot": {
        "name": "Thomas\u00a0Chabot",
        "team": "PHI",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 161.1,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.71,
                        "shot_assists_per_60": 1.16,
                        "total_shot_contributions_per_60": 1.87,
                        "chances_per_60": 0.5,
                        "chance_assists_per_60": 1.02
                },
                "passing": {
                        "high_danger_assists_per_60": 1.27
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.83,
                        "rush_offense_per_60": 0.32,
                        "shots_off_hd_passes_per_60": 0.69
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.6,
                        "controlled_entry_percent": 0.65,
                        "controlled_entry_with_chance_percent": 0.17
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.47,
                        "retrievals_per_60": 2.64,
                        "successful_retrieval_percent": 0.7,
                        "exits_per_60": 0.25,
                        "botched_retrievals_per_60": -2.77
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "shane pinto": {
        "name": "Shane\u00a0Pinto",
        "team": "PIT",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 101.7,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.3,
                        "shot_assists_per_60": 0.76,
                        "total_shot_contributions_per_60": 2.06,
                        "chances_per_60": 1.32,
                        "chance_assists_per_60": 0.78
                },
                "passing": {
                        "high_danger_assists_per_60": 0.78
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.19,
                        "rush_offense_per_60": 0.95,
                        "shots_off_hd_passes_per_60": 1.15
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.25,
                        "controlled_entry_percent": 0.58,
                        "controlled_entry_with_chance_percent": 0.23
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.64,
                        "retrievals_per_60": 2.01,
                        "successful_retrieval_percent": 0.83,
                        "exits_per_60": 0.31,
                        "botched_retrievals_per_60": -3.12
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "ridly greig": {
        "name": "Ridly\u00a0Greig",
        "team": "SJS",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 133.7,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.01,
                        "shot_assists_per_60": 0.85,
                        "total_shot_contributions_per_60": 1.86,
                        "chances_per_60": 1.1,
                        "chance_assists_per_60": 0.86
                },
                "passing": {
                        "high_danger_assists_per_60": 0.9
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.88,
                        "rush_offense_per_60": 0.77,
                        "shots_off_hd_passes_per_60": 1.03
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.14,
                        "controlled_entry_percent": 0.54,
                        "controlled_entry_with_chance_percent": 0.2
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.45,
                        "retrievals_per_60": 1.61,
                        "successful_retrieval_percent": 0.62,
                        "exits_per_60": 0.37,
                        "botched_retrievals_per_60": -3.19
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "noah gregor": {
        "name": "Noah\u00a0Gregor",
        "team": "SEA",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 105.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.22,
                        "shot_assists_per_60": 0.7,
                        "total_shot_contributions_per_60": 0.92,
                        "chances_per_60": 0.2,
                        "chance_assists_per_60": 0.98
                },
                "passing": {
                        "high_danger_assists_per_60": 0.61
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.23,
                        "rush_offense_per_60": 0.11,
                        "shots_off_hd_passes_per_60": 0.19
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.7,
                        "controlled_entry_percent": 0.62,
                        "controlled_entry_with_chance_percent": 0.26
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.43,
                        "retrievals_per_60": 3.58,
                        "successful_retrieval_percent": 0.59,
                        "exits_per_60": 0.11,
                        "botched_retrievals_per_60": -3.73
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "nick jensen": {
        "name": "Nick\u00a0Jensen",
        "team": "STL",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 108.3,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.927,
                        "goals_against_average": 2.02,
                        "wins": 35,
                        "shutouts": 8
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "nick cousins": {
        "name": "Nick\u00a0Cousins",
        "team": "TBL",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 139.0,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.98,
                        "shot_assists_per_60": 0.76,
                        "total_shot_contributions_per_60": 1.74,
                        "chances_per_60": 0.7,
                        "chance_assists_per_60": 0.7
                },
                "passing": {
                        "high_danger_assists_per_60": 0.64
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.93,
                        "rush_offense_per_60": 0.72,
                        "shots_off_hd_passes_per_60": 0.77
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.29,
                        "controlled_entry_percent": 0.28,
                        "controlled_entry_with_chance_percent": 0.33
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.92,
                        "retrievals_per_60": 1.86,
                        "successful_retrieval_percent": 0.69,
                        "exits_per_60": 0.38,
                        "botched_retrievals_per_60": -1.7
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "michael amadio": {
        "name": "Michael\u00a0Amadio",
        "team": "TOR",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 172.2,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.24,
                        "shot_assists_per_60": 0.72,
                        "total_shot_contributions_per_60": 1.96,
                        "chances_per_60": 1.6,
                        "chance_assists_per_60": 0.75
                },
                "passing": {
                        "high_danger_assists_per_60": 0.67
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.06,
                        "rush_offense_per_60": 0.67,
                        "shots_off_hd_passes_per_60": 1.06
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.82,
                        "controlled_entry_percent": 0.62,
                        "controlled_entry_with_chance_percent": 0.25
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.79,
                        "retrievals_per_60": 1.76,
                        "successful_retrieval_percent": 0.71,
                        "exits_per_60": 0.38,
                        "botched_retrievals_per_60": -3.65
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "josh norris": {
        "name": "Josh\u00a0Norris",
        "team": "VAN",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 179.7,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.56,
                        "shot_assists_per_60": 0.53,
                        "total_shot_contributions_per_60": 2.09,
                        "chances_per_60": 1.26,
                        "chance_assists_per_60": 0.62
                },
                "passing": {
                        "high_danger_assists_per_60": 0.5
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.49,
                        "rush_offense_per_60": 1.22,
                        "shots_off_hd_passes_per_60": 1.51
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.43,
                        "controlled_entry_percent": 0.32,
                        "controlled_entry_with_chance_percent": 0.28
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.43,
                        "retrievals_per_60": 2.12,
                        "successful_retrieval_percent": 0.74,
                        "exits_per_60": 0.1,
                        "botched_retrievals_per_60": -1.61
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jake sanderson": {
        "name": "Jake\u00a0Sanderson",
        "team": "VGK",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 115.6,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.3,
                        "shot_assists_per_60": 0.52,
                        "total_shot_contributions_per_60": 0.82,
                        "chances_per_60": 0.23,
                        "chance_assists_per_60": 0.66
                },
                "passing": {
                        "high_danger_assists_per_60": 0.44
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.37,
                        "rush_offense_per_60": 0.1,
                        "shots_off_hd_passes_per_60": 0.32
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.74,
                        "controlled_entry_percent": 0.56,
                        "controlled_entry_with_chance_percent": 0.33
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.86,
                        "retrievals_per_60": 4.11,
                        "successful_retrieval_percent": 0.77,
                        "exits_per_60": 0.35,
                        "botched_retrievals_per_60": -2.56
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jacob bernard_docker": {
        "name": "Jacob\u00a0Bernard-Docker",
        "team": "WSH",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 151.5,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.928,
                        "goals_against_average": 2.52,
                        "wins": 22,
                        "shutouts": 7
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "drake batherson": {
        "name": "Drake\u00a0Batherson",
        "team": "WPG",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 192.7,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.85,
                        "shot_assists_per_60": 0.91,
                        "total_shot_contributions_per_60": 1.76,
                        "chances_per_60": 0.67,
                        "chance_assists_per_60": 0.8
                },
                "passing": {
                        "high_danger_assists_per_60": 1.05
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.74,
                        "rush_offense_per_60": 0.56,
                        "shots_off_hd_passes_per_60": 0.81
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.63,
                        "controlled_entry_percent": 0.57,
                        "controlled_entry_with_chance_percent": 0.22
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.61,
                        "retrievals_per_60": 2.54,
                        "successful_retrieval_percent": 0.61,
                        "exits_per_60": 0.37,
                        "botched_retrievals_per_60": -2.99
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "claude giroux": {
        "name": "Claude\u00a0Giroux",
        "team": "ANA",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 194.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.55,
                        "shot_assists_per_60": 0.42,
                        "total_shot_contributions_per_60": 1.97,
                        "chances_per_60": 1.93,
                        "chance_assists_per_60": 0.42
                },
                "passing": {
                        "high_danger_assists_per_60": 0.41
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.27,
                        "rush_offense_per_60": 1.14,
                        "shots_off_hd_passes_per_60": 1.46
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.25,
                        "controlled_entry_percent": 0.55,
                        "controlled_entry_with_chance_percent": 0.16
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.3,
                        "retrievals_per_60": 2.04,
                        "successful_retrieval_percent": 0.81,
                        "exits_per_60": 0.14,
                        "botched_retrievals_per_60": -3.88
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "brady tkachuk": {
        "name": "Brady\u00a0Tkachuk",
        "team": "ARI",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 127.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.09,
                        "shot_assists_per_60": 0.42,
                        "total_shot_contributions_per_60": 1.51,
                        "chances_per_60": 1.31,
                        "chance_assists_per_60": 0.35
                },
                "passing": {
                        "high_danger_assists_per_60": 0.42
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.24,
                        "rush_offense_per_60": 0.61,
                        "shots_off_hd_passes_per_60": 1.2
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.83,
                        "controlled_entry_percent": 0.6,
                        "controlled_entry_with_chance_percent": 0.33
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.31,
                        "retrievals_per_60": 1.61,
                        "successful_retrieval_percent": 0.55,
                        "exits_per_60": 0.39,
                        "botched_retrievals_per_60": -1.71
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "artem zub": {
        "name": "Artem\u00a0Zub",
        "team": "BOS",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 114.6,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.41,
                        "shot_assists_per_60": 0.3,
                        "total_shot_contributions_per_60": 0.71,
                        "chances_per_60": 0.5,
                        "chance_assists_per_60": 0.3
                },
                "passing": {
                        "high_danger_assists_per_60": 0.3
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.34,
                        "rush_offense_per_60": 0.24,
                        "shots_off_hd_passes_per_60": 0.43
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.67,
                        "controlled_entry_percent": 0.32,
                        "controlled_entry_with_chance_percent": 0.25
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 4.02,
                        "retrievals_per_60": 3.37,
                        "successful_retrieval_percent": 0.71,
                        "exits_per_60": 0.2,
                        "botched_retrievals_per_60": -1.78
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "adam gaudette": {
        "name": "Adam\u00a0Gaudette",
        "team": "BUF",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 159.7,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.906,
                        "goals_against_average": 2.13,
                        "wins": 28,
                        "shutouts": 0
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "zac jones": {
        "name": "Zac\u00a0Jones",
        "team": "CGY",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 135.1,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.34,
                        "shot_assists_per_60": 0.91,
                        "total_shot_contributions_per_60": 2.25,
                        "chances_per_60": 1.44,
                        "chance_assists_per_60": 1.03
                },
                "passing": {
                        "high_danger_assists_per_60": 0.78
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.32,
                        "rush_offense_per_60": 0.49,
                        "shots_off_hd_passes_per_60": 1.24
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.45,
                        "controlled_entry_percent": 0.48,
                        "controlled_entry_with_chance_percent": 0.26
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.89,
                        "retrievals_per_60": 2.67,
                        "successful_retrieval_percent": 0.57,
                        "exits_per_60": 0.15,
                        "botched_retrievals_per_60": -3.49
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "will cuylle": {
        "name": "Will\u00a0Cuylle",
        "team": "CAR",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 196.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.72,
                        "shot_assists_per_60": 0.52,
                        "total_shot_contributions_per_60": 2.24,
                        "chances_per_60": 2.18,
                        "chance_assists_per_60": 0.64
                },
                "passing": {
                        "high_danger_assists_per_60": 0.58
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.72,
                        "rush_offense_per_60": 1.11,
                        "shots_off_hd_passes_per_60": 1.34
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.07,
                        "controlled_entry_percent": 0.35,
                        "controlled_entry_with_chance_percent": 0.21
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.74,
                        "retrievals_per_60": 2.04,
                        "successful_retrieval_percent": 0.56,
                        "exits_per_60": 0.28,
                        "botched_retrievals_per_60": -3.75
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "vincent trocheck": {
        "name": "Vincent\u00a0Trocheck",
        "team": "CHI",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 153.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.49,
                        "shot_assists_per_60": 0.41,
                        "total_shot_contributions_per_60": 1.9,
                        "chances_per_60": 1.57,
                        "chance_assists_per_60": 0.35
                },
                "passing": {
                        "high_danger_assists_per_60": 0.34
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.66,
                        "rush_offense_per_60": 0.81,
                        "shots_off_hd_passes_per_60": 1.53
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.97,
                        "controlled_entry_percent": 0.35,
                        "controlled_entry_with_chance_percent": 0.31
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.08,
                        "retrievals_per_60": 2.38,
                        "successful_retrieval_percent": 0.75,
                        "exits_per_60": 0.14,
                        "botched_retrievals_per_60": -1.82
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "urho vaakanainen": {
        "name": "Urho\u00a0Vaakanainen",
        "team": "COL",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 106.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.46,
                        "shot_assists_per_60": 0.4,
                        "total_shot_contributions_per_60": 0.86,
                        "chances_per_60": 0.48,
                        "chance_assists_per_60": 0.32
                },
                "passing": {
                        "high_danger_assists_per_60": 0.44
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.55,
                        "rush_offense_per_60": 0.14,
                        "shots_off_hd_passes_per_60": 0.48
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.33,
                        "controlled_entry_percent": 0.54,
                        "controlled_entry_with_chance_percent": 0.2
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 5.24,
                        "retrievals_per_60": 4.44,
                        "successful_retrieval_percent": 0.6,
                        "exits_per_60": 0.29,
                        "botched_retrievals_per_60": -3.59
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "sam carrick": {
        "name": "Sam\u00a0Carrick",
        "team": "CBJ",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 121.2,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.911,
                        "goals_against_average": 3.29,
                        "wins": 22,
                        "shutouts": 5
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "ryan lindgren": {
        "name": "Ryan\u00a0Lindgren",
        "team": "DAL",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 174.1,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.67,
                        "shot_assists_per_60": 0.89,
                        "total_shot_contributions_per_60": 1.56,
                        "chances_per_60": 0.75,
                        "chance_assists_per_60": 1.07
                },
                "passing": {
                        "high_danger_assists_per_60": 0.83
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.85,
                        "rush_offense_per_60": 0.51,
                        "shots_off_hd_passes_per_60": 0.56
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.32,
                        "controlled_entry_percent": 0.39,
                        "controlled_entry_with_chance_percent": 0.22
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.85,
                        "retrievals_per_60": 2.73,
                        "successful_retrieval_percent": 0.81,
                        "exits_per_60": 0.27,
                        "botched_retrievals_per_60": -1.62
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "reilly smith": {
        "name": "Reilly\u00a0Smith",
        "team": "DET",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 102.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.43,
                        "shot_assists_per_60": 0.92,
                        "total_shot_contributions_per_60": 2.35,
                        "chances_per_60": 1.05,
                        "chance_assists_per_60": 1.12
                },
                "passing": {
                        "high_danger_assists_per_60": 0.86
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.27,
                        "rush_offense_per_60": 0.53,
                        "shots_off_hd_passes_per_60": 1.32
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.54,
                        "controlled_entry_percent": 0.54,
                        "controlled_entry_with_chance_percent": 0.22
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.81,
                        "retrievals_per_60": 1.68,
                        "successful_retrieval_percent": 0.76,
                        "exits_per_60": 0.25,
                        "botched_retrievals_per_60": -3.03
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "mika zibanejad": {
        "name": "Mika\u00a0Zibanejad",
        "team": "EDM",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 161.8,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.53,
                        "shot_assists_per_60": 0.83,
                        "total_shot_contributions_per_60": 2.36,
                        "chances_per_60": 1.11,
                        "chance_assists_per_60": 0.68
                },
                "passing": {
                        "high_danger_assists_per_60": 0.94
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.77,
                        "rush_offense_per_60": 0.58,
                        "shots_off_hd_passes_per_60": 1.4
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.17,
                        "controlled_entry_percent": 0.41,
                        "controlled_entry_with_chance_percent": 0.15
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.8,
                        "retrievals_per_60": 1.55,
                        "successful_retrieval_percent": 0.65,
                        "exits_per_60": 0.38,
                        "botched_retrievals_per_60": -3.45
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "k'andre miller": {
        "name": "K'Andre\u00a0Miller",
        "team": "FLA",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 105.8,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.69,
                        "shot_assists_per_60": 0.7,
                        "total_shot_contributions_per_60": 1.39,
                        "chances_per_60": 0.85,
                        "chance_assists_per_60": 0.79
                },
                "passing": {
                        "high_danger_assists_per_60": 0.66
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.56,
                        "rush_offense_per_60": 0.28,
                        "shots_off_hd_passes_per_60": 0.53
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.32,
                        "controlled_entry_percent": 0.62,
                        "controlled_entry_with_chance_percent": 0.24
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.28,
                        "retrievals_per_60": 3.44,
                        "successful_retrieval_percent": 0.79,
                        "exits_per_60": 0.21,
                        "botched_retrievals_per_60": -2.79
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "filip chytil": {
        "name": "Filip\u00a0Chytil",
        "team": "LAK",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 130.6,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.904,
                        "goals_against_average": 2.84,
                        "wins": 32,
                        "shutouts": 3
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "chris kreider": {
        "name": "Chris\u00a0Kreider",
        "team": "MIN",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 107.1,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.14,
                        "shot_assists_per_60": 0.99,
                        "total_shot_contributions_per_60": 2.13,
                        "chances_per_60": 0.98,
                        "chance_assists_per_60": 0.9
                },
                "passing": {
                        "high_danger_assists_per_60": 1.13
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.2,
                        "rush_offense_per_60": 0.4,
                        "shots_off_hd_passes_per_60": 1.08
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.08,
                        "controlled_entry_percent": 0.42,
                        "controlled_entry_with_chance_percent": 0.16
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.29,
                        "retrievals_per_60": 2.84,
                        "successful_retrieval_percent": 0.72,
                        "exits_per_60": 0.39,
                        "botched_retrievals_per_60": -2.77
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "braden schneider": {
        "name": "Braden\u00a0Schneider",
        "team": "MTL",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 170.0,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.39,
                        "shot_assists_per_60": 0.81,
                        "total_shot_contributions_per_60": 2.2,
                        "chances_per_60": 1.19,
                        "chance_assists_per_60": 1.01
                },
                "passing": {
                        "high_danger_assists_per_60": 0.81
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.51,
                        "rush_offense_per_60": 0.91,
                        "shots_off_hd_passes_per_60": 1.3
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.73,
                        "controlled_entry_percent": 0.36,
                        "controlled_entry_with_chance_percent": 0.35
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.79,
                        "retrievals_per_60": 2.11,
                        "successful_retrieval_percent": 0.82,
                        "exits_per_60": 0.36,
                        "botched_retrievals_per_60": -2.19
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "artemi panarin": {
        "name": "Artemi\u00a0Panarin",
        "team": "NSH",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 150.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.69,
                        "shot_assists_per_60": 0.51,
                        "total_shot_contributions_per_60": 2.2,
                        "chances_per_60": 2.02,
                        "chance_assists_per_60": 0.64
                },
                "passing": {
                        "high_danger_assists_per_60": 0.5
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.45,
                        "rush_offense_per_60": 0.8,
                        "shots_off_hd_passes_per_60": 1.26
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.06,
                        "controlled_entry_percent": 0.45,
                        "controlled_entry_with_chance_percent": 0.27
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.72,
                        "retrievals_per_60": 2.76,
                        "successful_retrieval_percent": 0.68,
                        "exits_per_60": 0.33,
                        "botched_retrievals_per_60": -3.94
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "alexis lafrenière": {
        "name": "Alexis\u00a0Lafreni\u00e8re",
        "team": "NJD",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 126.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.6,
                        "shot_assists_per_60": 0.73,
                        "total_shot_contributions_per_60": 1.33,
                        "chances_per_60": 0.46,
                        "chance_assists_per_60": 0.6
                },
                "passing": {
                        "high_danger_assists_per_60": 0.64
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.74,
                        "rush_offense_per_60": 0.36,
                        "shots_off_hd_passes_per_60": 0.43
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.68,
                        "controlled_entry_percent": 0.4,
                        "controlled_entry_with_chance_percent": 0.21
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.57,
                        "retrievals_per_60": 2.95,
                        "successful_retrieval_percent": 0.73,
                        "exits_per_60": 0.25,
                        "botched_retrievals_per_60": -2.29
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "adam fox": {
        "name": "Adam\u00a0Fox",
        "team": "NYI",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 186.5,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.926,
                        "goals_against_average": 2.5,
                        "wins": 13,
                        "shutouts": 2
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "adam edstrom": {
        "name": "Adam\u00a0Edstrom",
        "team": "NYR",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 120.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.29,
                        "shot_assists_per_60": 0.73,
                        "total_shot_contributions_per_60": 2.02,
                        "chances_per_60": 1.58,
                        "chance_assists_per_60": 0.77
                },
                "passing": {
                        "high_danger_assists_per_60": 0.78
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.79,
                        "rush_offense_per_60": 0.63,
                        "shots_off_hd_passes_per_60": 1.33
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.81,
                        "controlled_entry_percent": 0.47,
                        "controlled_entry_with_chance_percent": 0.29
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.39,
                        "retrievals_per_60": 2.05,
                        "successful_retrieval_percent": 0.83,
                        "exits_per_60": 0.13,
                        "botched_retrievals_per_60": -3.4
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "tony deangelo": {
        "name": "Tony\u00a0DeAngelo",
        "team": "OTT",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 102.7,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.73,
                        "shot_assists_per_60": 1.06,
                        "total_shot_contributions_per_60": 1.79,
                        "chances_per_60": 0.62,
                        "chance_assists_per_60": 1.28
                },
                "passing": {
                        "high_danger_assists_per_60": 1.27
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.65,
                        "rush_offense_per_60": 0.56,
                        "shots_off_hd_passes_per_60": 0.55
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.62,
                        "controlled_entry_percent": 0.37,
                        "controlled_entry_with_chance_percent": 0.33
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.39,
                        "retrievals_per_60": 2.48,
                        "successful_retrieval_percent": 0.78,
                        "exits_per_60": 0.16,
                        "botched_retrievals_per_60": -3.02
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "simon holmstrom": {
        "name": "Simon\u00a0Holmstrom",
        "team": "PHI",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 162.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.22,
                        "shot_assists_per_60": 0.96,
                        "total_shot_contributions_per_60": 2.18,
                        "chances_per_60": 1.32,
                        "chance_assists_per_60": 0.78
                },
                "passing": {
                        "high_danger_assists_per_60": 1.04
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.69,
                        "rush_offense_per_60": 0.41,
                        "shots_off_hd_passes_per_60": 1.25
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.4,
                        "controlled_entry_percent": 0.52,
                        "controlled_entry_with_chance_percent": 0.26
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.81,
                        "retrievals_per_60": 2.81,
                        "successful_retrieval_percent": 0.66,
                        "exits_per_60": 0.2,
                        "botched_retrievals_per_60": -2.89
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "scott mayfield": {
        "name": "Scott\u00a0Mayfield",
        "team": "PIT",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 106.3,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.69,
                        "shot_assists_per_60": 0.41,
                        "total_shot_contributions_per_60": 1.1,
                        "chances_per_60": 0.78,
                        "chance_assists_per_60": 0.44
                },
                "passing": {
                        "high_danger_assists_per_60": 0.36
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.73,
                        "rush_offense_per_60": 0.25,
                        "shots_off_hd_passes_per_60": 0.61
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.5,
                        "controlled_entry_percent": 0.25,
                        "controlled_entry_with_chance_percent": 0.16
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.37,
                        "retrievals_per_60": 3.51,
                        "successful_retrieval_percent": 0.73,
                        "exits_per_60": 0.36,
                        "botched_retrievals_per_60": -2.16
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "ryan pulock": {
        "name": "Ryan\u00a0Pulock",
        "team": "SJS",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 127.2,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.909,
                        "goals_against_average": 2.15,
                        "wins": 29,
                        "shutouts": 4
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "pierre engvall": {
        "name": "Pierre\u00a0Engvall",
        "team": "SEA",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 176.7,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.73,
                        "shot_assists_per_60": 0.58,
                        "total_shot_contributions_per_60": 1.31,
                        "chances_per_60": 0.56,
                        "chance_assists_per_60": 0.58
                },
                "passing": {
                        "high_danger_assists_per_60": 0.67
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.67,
                        "rush_offense_per_60": 0.33,
                        "shots_off_hd_passes_per_60": 0.59
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.25,
                        "controlled_entry_percent": 0.35,
                        "controlled_entry_with_chance_percent": 0.31
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.07,
                        "retrievals_per_60": 2.16,
                        "successful_retrieval_percent": 0.58,
                        "exits_per_60": 0.15,
                        "botched_retrievals_per_60": -3.71
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "noah dobson": {
        "name": "Noah\u00a0Dobson",
        "team": "STL",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 143.7,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.62,
                        "shot_assists_per_60": 1.09,
                        "total_shot_contributions_per_60": 2.71,
                        "chances_per_60": 1.89,
                        "chance_assists_per_60": 1.37
                },
                "passing": {
                        "high_danger_assists_per_60": 1.11
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.76,
                        "rush_offense_per_60": 1.05,
                        "shots_off_hd_passes_per_60": 1.38
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.33,
                        "controlled_entry_percent": 0.46,
                        "controlled_entry_with_chance_percent": 0.22
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.92,
                        "retrievals_per_60": 2.94,
                        "successful_retrieval_percent": 0.65,
                        "exits_per_60": 0.33,
                        "botched_retrievals_per_60": -2.53
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "maxim tsyplakov": {
        "name": "Maxim\u00a0Tsyplakov",
        "team": "TBL",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 129.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.22,
                        "shot_assists_per_60": 0.6,
                        "total_shot_contributions_per_60": 1.82,
                        "chances_per_60": 0.87,
                        "chance_assists_per_60": 0.73
                },
                "passing": {
                        "high_danger_assists_per_60": 0.62
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.62,
                        "rush_offense_per_60": 0.89,
                        "shots_off_hd_passes_per_60": 1.2
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.87,
                        "controlled_entry_percent": 0.48,
                        "controlled_entry_with_chance_percent": 0.23
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.09,
                        "retrievals_per_60": 2.06,
                        "successful_retrieval_percent": 0.57,
                        "exits_per_60": 0.36,
                        "botched_retrievals_per_60": -2.58
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "kyle palmieri": {
        "name": "Kyle\u00a0Palmieri",
        "team": "TOR",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 189.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.29,
                        "shot_assists_per_60": 0.32,
                        "total_shot_contributions_per_60": 0.61,
                        "chances_per_60": 0.37,
                        "chance_assists_per_60": 0.38
                },
                "passing": {
                        "high_danger_assists_per_60": 0.34
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.29,
                        "rush_offense_per_60": 0.17,
                        "shots_off_hd_passes_per_60": 0.3
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.54,
                        "controlled_entry_percent": 0.38,
                        "controlled_entry_with_chance_percent": 0.17
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.61,
                        "retrievals_per_60": 2.62,
                        "successful_retrieval_percent": 0.77,
                        "exits_per_60": 0.2,
                        "botched_retrievals_per_60": -2.87
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "kyle maclean": {
        "name": "Kyle\u00a0MacLean",
        "team": "VAN",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 147.8,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.906,
                        "goals_against_average": 2.13,
                        "wins": 29,
                        "shutouts": 1
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jean_gabriel pageau": {
        "name": "Jean-Gabriel\u00a0Pageau",
        "team": "VGK",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 115.3,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.32,
                        "shot_assists_per_60": 0.62,
                        "total_shot_contributions_per_60": 1.94,
                        "chances_per_60": 1.42,
                        "chance_assists_per_60": 0.62
                },
                "passing": {
                        "high_danger_assists_per_60": 0.51
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.39,
                        "rush_offense_per_60": 0.89,
                        "shots_off_hd_passes_per_60": 1.29
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.01,
                        "controlled_entry_percent": 0.33,
                        "controlled_entry_with_chance_percent": 0.24
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.79,
                        "retrievals_per_60": 1.76,
                        "successful_retrieval_percent": 0.68,
                        "exits_per_60": 0.21,
                        "botched_retrievals_per_60": -3.67
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "hudson fasching": {
        "name": "Hudson\u00a0Fasching",
        "team": "WSH",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 128.0,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.01,
                        "shot_assists_per_60": 0.87,
                        "total_shot_contributions_per_60": 1.88,
                        "chances_per_60": 0.92,
                        "chance_assists_per_60": 0.8
                },
                "passing": {
                        "high_danger_assists_per_60": 0.95
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.98,
                        "rush_offense_per_60": 0.57,
                        "shots_off_hd_passes_per_60": 0.88
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.76,
                        "controlled_entry_percent": 0.27,
                        "controlled_entry_with_chance_percent": 0.24
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.13,
                        "retrievals_per_60": 2.52,
                        "successful_retrieval_percent": 0.64,
                        "exits_per_60": 0.29,
                        "botched_retrievals_per_60": -2.02
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "dennis cholowski": {
        "name": "Dennis\u00a0Cholowski",
        "team": "WPG",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 160.8,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.53,
                        "shot_assists_per_60": 0.62,
                        "total_shot_contributions_per_60": 2.15,
                        "chances_per_60": 1.75,
                        "chance_assists_per_60": 0.77
                },
                "passing": {
                        "high_danger_assists_per_60": 0.56
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.99,
                        "rush_offense_per_60": 0.57,
                        "shots_off_hd_passes_per_60": 1.63
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.82,
                        "controlled_entry_percent": 0.62,
                        "controlled_entry_with_chance_percent": 0.25
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.8,
                        "retrievals_per_60": 1.83,
                        "successful_retrieval_percent": 0.76,
                        "exits_per_60": 0.38,
                        "botched_retrievals_per_60": -1.77
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "casey cizikas": {
        "name": "Casey\u00a0Cizikas",
        "team": "ANA",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 134.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.19,
                        "shot_assists_per_60": 0.78,
                        "total_shot_contributions_per_60": 0.97,
                        "chances_per_60": 0.15,
                        "chance_assists_per_60": 0.84
                },
                "passing": {
                        "high_danger_assists_per_60": 0.86
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.21,
                        "rush_offense_per_60": 0.08,
                        "shots_off_hd_passes_per_60": 0.2
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.42,
                        "controlled_entry_percent": 0.65,
                        "controlled_entry_with_chance_percent": 0.28
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.07,
                        "retrievals_per_60": 3.08,
                        "successful_retrieval_percent": 0.63,
                        "exits_per_60": 0.17,
                        "botched_retrievals_per_60": -1.57
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "brock nelson": {
        "name": "Brock\u00a0Nelson",
        "team": "ARI",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 121.7,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.913,
                        "goals_against_average": 3.37,
                        "wins": 18,
                        "shutouts": 3
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "bo horvat": {
        "name": "Bo\u00a0Horvat",
        "team": "BOS",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 103.7,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.65,
                        "shot_assists_per_60": 0.95,
                        "total_shot_contributions_per_60": 2.6,
                        "chances_per_60": 1.63,
                        "chance_assists_per_60": 1.3
                },
                "passing": {
                        "high_danger_assists_per_60": 0.8
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.5,
                        "rush_offense_per_60": 0.53,
                        "shots_off_hd_passes_per_60": 1.21
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.93,
                        "controlled_entry_percent": 0.38,
                        "controlled_entry_with_chance_percent": 0.33
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.63,
                        "retrievals_per_60": 2.7,
                        "successful_retrieval_percent": 0.56,
                        "exits_per_60": 0.2,
                        "botched_retrievals_per_60": -3.63
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "anthony duclair": {
        "name": "Anthony\u00a0Duclair",
        "team": "BUF",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 157.3,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.66,
                        "shot_assists_per_60": 1.0,
                        "total_shot_contributions_per_60": 1.66,
                        "chances_per_60": 0.66,
                        "chance_assists_per_60": 1.38
                },
                "passing": {
                        "high_danger_assists_per_60": 1.09
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.74,
                        "rush_offense_per_60": 0.39,
                        "shots_off_hd_passes_per_60": 0.65
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.94,
                        "controlled_entry_percent": 0.48,
                        "controlled_entry_with_chance_percent": 0.15
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.3,
                        "retrievals_per_60": 2.2,
                        "successful_retrieval_percent": 0.66,
                        "exits_per_60": 0.2,
                        "botched_retrievals_per_60": -1.88
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "anders lee": {
        "name": "Anders\u00a0Lee",
        "team": "CGY",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 191.7,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.19,
                        "shot_assists_per_60": 0.93,
                        "total_shot_contributions_per_60": 2.12,
                        "chances_per_60": 1.19,
                        "chance_assists_per_60": 0.8
                },
                "passing": {
                        "high_danger_assists_per_60": 1.02
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.15,
                        "rush_offense_per_60": 0.67,
                        "shots_off_hd_passes_per_60": 1.12
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.8,
                        "controlled_entry_percent": 0.57,
                        "controlled_entry_with_chance_percent": 0.25
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.08,
                        "retrievals_per_60": 2.03,
                        "successful_retrieval_percent": 0.65,
                        "exits_per_60": 0.36,
                        "botched_retrievals_per_60": -3.75
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "alexander romanov": {
        "name": "Alexander\u00a0Romanov",
        "team": "CAR",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 184.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.36,
                        "shot_assists_per_60": 0.37,
                        "total_shot_contributions_per_60": 0.73,
                        "chances_per_60": 0.45,
                        "chance_assists_per_60": 0.47
                },
                "passing": {
                        "high_danger_assists_per_60": 0.34
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.35,
                        "rush_offense_per_60": 0.21,
                        "shots_off_hd_passes_per_60": 0.29
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.36,
                        "controlled_entry_percent": 0.62,
                        "controlled_entry_with_chance_percent": 0.31
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.7,
                        "retrievals_per_60": 2.96,
                        "successful_retrieval_percent": 0.85,
                        "exits_per_60": 0.18,
                        "botched_retrievals_per_60": -2.82
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "adam pelech": {
        "name": "Adam\u00a0Pelech",
        "team": "CHI",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 175.0,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.903,
                        "goals_against_average": 2.88,
                        "wins": 24,
                        "shutouts": 4
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "zachary l'heureux": {
        "name": "Zachary\u00a0L'Heureux",
        "team": "COL",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 116.7,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.79,
                        "shot_assists_per_60": 0.8,
                        "total_shot_contributions_per_60": 2.59,
                        "chances_per_60": 2.06,
                        "chance_assists_per_60": 1.09
                },
                "passing": {
                        "high_danger_assists_per_60": 0.9
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 2.0,
                        "rush_offense_per_60": 1.31,
                        "shots_off_hd_passes_per_60": 1.75
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.68,
                        "controlled_entry_percent": 0.43,
                        "controlled_entry_with_chance_percent": 0.19
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.46,
                        "retrievals_per_60": 2.36,
                        "successful_retrieval_percent": 0.69,
                        "exits_per_60": 0.26,
                        "botched_retrievals_per_60": -3.05
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "tommy novak": {
        "name": "Tommy\u00a0Novak",
        "team": "CBJ",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 132.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.46,
                        "shot_assists_per_60": 0.55,
                        "total_shot_contributions_per_60": 2.01,
                        "chances_per_60": 1.74,
                        "chance_assists_per_60": 0.46
                },
                "passing": {
                        "high_danger_assists_per_60": 0.63
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.47,
                        "rush_offense_per_60": 1.06,
                        "shots_off_hd_passes_per_60": 1.06
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.04,
                        "controlled_entry_percent": 0.48,
                        "controlled_entry_with_chance_percent": 0.19
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.68,
                        "retrievals_per_60": 2.98,
                        "successful_retrieval_percent": 0.69,
                        "exits_per_60": 0.21,
                        "botched_retrievals_per_60": -2.0
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "steven stamkos": {
        "name": "Steven\u00a0Stamkos",
        "team": "DAL",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 163.1,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.67,
                        "shot_assists_per_60": 1.08,
                        "total_shot_contributions_per_60": 1.75,
                        "chances_per_60": 0.78,
                        "chance_assists_per_60": 1.14
                },
                "passing": {
                        "high_danger_assists_per_60": 1.24
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.91,
                        "rush_offense_per_60": 0.2,
                        "shots_off_hd_passes_per_60": 0.66
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.01,
                        "controlled_entry_percent": 0.56,
                        "controlled_entry_with_chance_percent": 0.19
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.55,
                        "retrievals_per_60": 2.64,
                        "successful_retrieval_percent": 0.59,
                        "exits_per_60": 0.3,
                        "botched_retrievals_per_60": -2.79
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "spencer stastney": {
        "name": "Spencer\u00a0Stastney",
        "team": "DET",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 106.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.69,
                        "shot_assists_per_60": 0.89,
                        "total_shot_contributions_per_60": 1.58,
                        "chances_per_60": 0.63,
                        "chance_assists_per_60": 0.95
                },
                "passing": {
                        "high_danger_assists_per_60": 0.87
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.65,
                        "rush_offense_per_60": 0.54,
                        "shots_off_hd_passes_per_60": 0.7
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.47,
                        "controlled_entry_percent": 0.41,
                        "controlled_entry_with_chance_percent": 0.32
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.55,
                        "retrievals_per_60": 3.11,
                        "successful_retrieval_percent": 0.69,
                        "exits_per_60": 0.23,
                        "botched_retrievals_per_60": -3.6
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "ryan o'reilly": {
        "name": "Ryan\u00a0O'Reilly",
        "team": "EDM",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 154.0,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.912,
                        "goals_against_average": 3.38,
                        "wins": 30,
                        "shutouts": 8
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "roman josi": {
        "name": "Roman\u00a0Josi",
        "team": "FLA",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 102.8,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.79,
                        "shot_assists_per_60": 0.92,
                        "total_shot_contributions_per_60": 2.71,
                        "chances_per_60": 1.98,
                        "chance_assists_per_60": 0.8
                },
                "passing": {
                        "high_danger_assists_per_60": 1.1
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.72,
                        "rush_offense_per_60": 1.12,
                        "shots_off_hd_passes_per_60": 1.37
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.3,
                        "controlled_entry_percent": 0.45,
                        "controlled_entry_with_chance_percent": 0.2
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.22,
                        "retrievals_per_60": 2.42,
                        "successful_retrieval_percent": 0.78,
                        "exits_per_60": 0.38,
                        "botched_retrievals_per_60": -3.16
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "nick blankenburg": {
        "name": "Nick\u00a0Blankenburg",
        "team": "LAK",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 102.3,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.59,
                        "shot_assists_per_60": 0.47,
                        "total_shot_contributions_per_60": 1.06,
                        "chances_per_60": 0.71,
                        "chance_assists_per_60": 0.62
                },
                "passing": {
                        "high_danger_assists_per_60": 0.47
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.49,
                        "rush_offense_per_60": 0.45,
                        "shots_off_hd_passes_per_60": 0.58
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.68,
                        "controlled_entry_percent": 0.28,
                        "controlled_entry_with_chance_percent": 0.24
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.9,
                        "retrievals_per_60": 2.81,
                        "successful_retrieval_percent": 0.63,
                        "exits_per_60": 0.24,
                        "botched_retrievals_per_60": -2.77
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "michael mccarron": {
        "name": "Michael\u00a0McCarron",
        "team": "MIN",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 169.3,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.4,
                        "shot_assists_per_60": 0.91,
                        "total_shot_contributions_per_60": 2.31,
                        "chances_per_60": 1.66,
                        "chance_assists_per_60": 1.05
                },
                "passing": {
                        "high_danger_assists_per_60": 0.75
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.79,
                        "rush_offense_per_60": 0.87,
                        "shots_off_hd_passes_per_60": 1.22
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.04,
                        "controlled_entry_percent": 0.37,
                        "controlled_entry_with_chance_percent": 0.19
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.31,
                        "retrievals_per_60": 2.18,
                        "successful_retrieval_percent": 0.57,
                        "exits_per_60": 0.36,
                        "botched_retrievals_per_60": -1.71
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "mark jankowski": {
        "name": "Mark\u00a0Jankowski",
        "team": "MTL",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 132.7,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.62,
                        "shot_assists_per_60": 0.49,
                        "total_shot_contributions_per_60": 1.11,
                        "chances_per_60": 0.65,
                        "chance_assists_per_60": 0.46
                },
                "passing": {
                        "high_danger_assists_per_60": 0.42
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.66,
                        "rush_offense_per_60": 0.49,
                        "shots_off_hd_passes_per_60": 0.58
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.51,
                        "controlled_entry_percent": 0.64,
                        "controlled_entry_with_chance_percent": 0.16
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 5.02,
                        "retrievals_per_60": 4.48,
                        "successful_retrieval_percent": 0.62,
                        "exits_per_60": 0.13,
                        "botched_retrievals_per_60": -2.46
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "marc del_gaizo": {
        "name": "Marc\u00a0Del Gaizo",
        "team": "NSH",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 130.8,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.906,
                        "goals_against_average": 2.07,
                        "wins": 14,
                        "shutouts": 3
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "luke schenn": {
        "name": "Luke\u00a0Schenn",
        "team": "NJD",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 182.0,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.23,
                        "shot_assists_per_60": 0.81,
                        "total_shot_contributions_per_60": 2.04,
                        "chances_per_60": 1.34,
                        "chance_assists_per_60": 1.06
                },
                "passing": {
                        "high_danger_assists_per_60": 0.86
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.68,
                        "rush_offense_per_60": 0.59,
                        "shots_off_hd_passes_per_60": 1.27
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.04,
                        "controlled_entry_percent": 0.28,
                        "controlled_entry_with_chance_percent": 0.33
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.34,
                        "retrievals_per_60": 2.32,
                        "successful_retrieval_percent": 0.85,
                        "exits_per_60": 0.14,
                        "botched_retrievals_per_60": -3.77
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "luke evangelista": {
        "name": "Luke\u00a0Evangelista",
        "team": "NYI",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 156.6,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.21,
                        "shot_assists_per_60": 0.43,
                        "total_shot_contributions_per_60": 1.64,
                        "chances_per_60": 1.42,
                        "chance_assists_per_60": 0.57
                },
                "passing": {
                        "high_danger_assists_per_60": 0.49
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.62,
                        "rush_offense_per_60": 0.88,
                        "shots_off_hd_passes_per_60": 0.87
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.77,
                        "controlled_entry_percent": 0.39,
                        "controlled_entry_with_chance_percent": 0.25
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.73,
                        "retrievals_per_60": 1.72,
                        "successful_retrieval_percent": 0.62,
                        "exits_per_60": 0.13,
                        "botched_retrievals_per_60": -2.4
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "justin barron": {
        "name": "Justin\u00a0Barron",
        "team": "NYR",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 112.8,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.44,
                        "shot_assists_per_60": 1.07,
                        "total_shot_contributions_per_60": 2.51,
                        "chances_per_60": 1.46,
                        "chance_assists_per_60": 1.45
                },
                "passing": {
                        "high_danger_assists_per_60": 1.02
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.86,
                        "rush_offense_per_60": 0.8,
                        "shots_off_hd_passes_per_60": 1.1
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.76,
                        "controlled_entry_percent": 0.64,
                        "controlled_entry_with_chance_percent": 0.26
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.77,
                        "retrievals_per_60": 1.57,
                        "successful_retrieval_percent": 0.55,
                        "exits_per_60": 0.39,
                        "botched_retrievals_per_60": -3.45
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jonathan marchessault": {
        "name": "Jonathan\u00a0Marchessault",
        "team": "OTT",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 173.6,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.38,
                        "shot_assists_per_60": 0.73,
                        "total_shot_contributions_per_60": 1.11,
                        "chances_per_60": 0.37,
                        "chance_assists_per_60": 0.98
                },
                "passing": {
                        "high_danger_assists_per_60": 0.83
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.49,
                        "rush_offense_per_60": 0.24,
                        "shots_off_hd_passes_per_60": 0.4
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.64,
                        "controlled_entry_percent": 0.46,
                        "controlled_entry_with_chance_percent": 0.27
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.97,
                        "retrievals_per_60": 3.42,
                        "successful_retrieval_percent": 0.72,
                        "exits_per_60": 0.11,
                        "botched_retrievals_per_60": -1.99
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jeremy lauzon": {
        "name": "Jeremy\u00a0Lauzon",
        "team": "PHI",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 145.2,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.902,
                        "goals_against_average": 2.42,
                        "wins": 44,
                        "shutouts": 3
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "gustav nyquist": {
        "name": "Gustav\u00a0Nyquist",
        "team": "PIT",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 174.0,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.23,
                        "shot_assists_per_60": 1.04,
                        "total_shot_contributions_per_60": 2.27,
                        "chances_per_60": 1.54,
                        "chance_assists_per_60": 1.33
                },
                "passing": {
                        "high_danger_assists_per_60": 1.23
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.38,
                        "rush_offense_per_60": 0.81,
                        "shots_off_hd_passes_per_60": 1.34
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.32,
                        "controlled_entry_percent": 0.43,
                        "controlled_entry_with_chance_percent": 0.23
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.82,
                        "retrievals_per_60": 1.97,
                        "successful_retrieval_percent": 0.65,
                        "exits_per_60": 0.14,
                        "botched_retrievals_per_60": -2.91
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "filip forsberg": {
        "name": "Filip\u00a0Forsberg",
        "team": "SJS",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 131.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.66,
                        "shot_assists_per_60": 0.41,
                        "total_shot_contributions_per_60": 1.07,
                        "chances_per_60": 0.74,
                        "chance_assists_per_60": 0.47
                },
                "passing": {
                        "high_danger_assists_per_60": 0.43
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.92,
                        "rush_offense_per_60": 0.46,
                        "shots_off_hd_passes_per_60": 0.63
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.7,
                        "controlled_entry_percent": 0.34,
                        "controlled_entry_with_chance_percent": 0.15
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.01,
                        "retrievals_per_60": 1.84,
                        "successful_retrieval_percent": 0.81,
                        "exits_per_60": 0.27,
                        "botched_retrievals_per_60": -2.49
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "fedor svechkov": {
        "name": "Fedor\u00a0Svechkov",
        "team": "SEA",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 159.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.86,
                        "shot_assists_per_60": 1.05,
                        "total_shot_contributions_per_60": 1.91,
                        "chances_per_60": 0.8,
                        "chance_assists_per_60": 1.44
                },
                "passing": {
                        "high_danger_assists_per_60": 0.87
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.06,
                        "rush_offense_per_60": 0.49,
                        "shots_off_hd_passes_per_60": 0.65
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.96,
                        "controlled_entry_percent": 0.52,
                        "controlled_entry_with_chance_percent": 0.28
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.74,
                        "retrievals_per_60": 2.54,
                        "successful_retrieval_percent": 0.64,
                        "exits_per_60": 0.28,
                        "botched_retrievals_per_60": -3.9
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "colton sissons": {
        "name": "Colton\u00a0Sissons",
        "team": "STL",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 185.8,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.26,
                        "shot_assists_per_60": 0.65,
                        "total_shot_contributions_per_60": 0.91,
                        "chances_per_60": 0.25,
                        "chance_assists_per_60": 0.79
                },
                "passing": {
                        "high_danger_assists_per_60": 0.67
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.36,
                        "rush_offense_per_60": 0.14,
                        "shots_off_hd_passes_per_60": 0.2
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.43,
                        "controlled_entry_percent": 0.58,
                        "controlled_entry_with_chance_percent": 0.32
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.14,
                        "retrievals_per_60": 3.24,
                        "successful_retrieval_percent": 0.68,
                        "exits_per_60": 0.1,
                        "botched_retrievals_per_60": -2.59
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "cole smith": {
        "name": "Cole\u00a0Smith",
        "team": "TBL",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 157.4,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.92,
                        "goals_against_average": 2.59,
                        "wins": 30,
                        "shutouts": 8
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "brady skjei": {
        "name": "Brady\u00a0Skjei",
        "team": "TOR",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 151.3,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.1,
                        "shot_assists_per_60": 0.91,
                        "total_shot_contributions_per_60": 2.01,
                        "chances_per_60": 1.4,
                        "chance_assists_per_60": 1.19
                },
                "passing": {
                        "high_danger_assists_per_60": 1.09
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.52,
                        "rush_offense_per_60": 0.7,
                        "shots_off_hd_passes_per_60": 1.12
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.09,
                        "controlled_entry_percent": 0.56,
                        "controlled_entry_with_chance_percent": 0.16
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.42,
                        "retrievals_per_60": 2.1,
                        "successful_retrieval_percent": 0.55,
                        "exits_per_60": 0.13,
                        "botched_retrievals_per_60": -1.55
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "alexandre carrier": {
        "name": "Alexandre\u00a0Carrier",
        "team": "VAN",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 136.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.54,
                        "shot_assists_per_60": 0.87,
                        "total_shot_contributions_per_60": 2.41,
                        "chances_per_60": 1.66,
                        "chance_assists_per_60": 0.71
                },
                "passing": {
                        "high_danger_assists_per_60": 0.8
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.48,
                        "rush_offense_per_60": 0.95,
                        "shots_off_hd_passes_per_60": 1.39
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.46,
                        "controlled_entry_percent": 0.43,
                        "controlled_entry_with_chance_percent": 0.3
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.29,
                        "retrievals_per_60": 1.57,
                        "successful_retrieval_percent": 0.7,
                        "exits_per_60": 0.15,
                        "botched_retrievals_per_60": -1.89
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "tomas tatar": {
        "name": "Tomas\u00a0Tatar",
        "team": "VGK",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 174.3,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.3,
                        "shot_assists_per_60": 0.71,
                        "total_shot_contributions_per_60": 2.01,
                        "chances_per_60": 1.03,
                        "chance_assists_per_60": 0.7
                },
                "passing": {
                        "high_danger_assists_per_60": 0.57
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.5,
                        "rush_offense_per_60": 0.77,
                        "shots_off_hd_passes_per_60": 1.35
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.38,
                        "controlled_entry_percent": 0.28,
                        "controlled_entry_with_chance_percent": 0.16
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.9,
                        "retrievals_per_60": 1.77,
                        "successful_retrieval_percent": 0.76,
                        "exits_per_60": 0.32,
                        "botched_retrievals_per_60": -2.82
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "timo meier": {
        "name": "Timo\u00a0Meier",
        "team": "WSH",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 102.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.44,
                        "shot_assists_per_60": 0.52,
                        "total_shot_contributions_per_60": 0.96,
                        "chances_per_60": 0.37,
                        "chance_assists_per_60": 0.42
                },
                "passing": {
                        "high_danger_assists_per_60": 0.53
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.4,
                        "rush_offense_per_60": 0.35,
                        "shots_off_hd_passes_per_60": 0.4
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.78,
                        "controlled_entry_percent": 0.46,
                        "controlled_entry_with_chance_percent": 0.31
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 4.01,
                        "retrievals_per_60": 3.86,
                        "successful_retrieval_percent": 0.81,
                        "exits_per_60": 0.34,
                        "botched_retrievals_per_60": -2.42
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "stefan noesen": {
        "name": "Stefan\u00a0Noesen",
        "team": "WPG",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 122.4,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.905,
                        "goals_against_average": 2.45,
                        "wins": 35,
                        "shutouts": 6
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "paul cotter": {
        "name": "Paul\u00a0Cotter",
        "team": "ANA",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 176.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.72,
                        "shot_assists_per_60": 1.13,
                        "total_shot_contributions_per_60": 1.85,
                        "chances_per_60": 0.82,
                        "chance_assists_per_60": 1.29
                },
                "passing": {
                        "high_danger_assists_per_60": 0.95
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.83,
                        "rush_offense_per_60": 0.35,
                        "shots_off_hd_passes_per_60": 0.53
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.54,
                        "controlled_entry_percent": 0.59,
                        "controlled_entry_with_chance_percent": 0.21
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.85,
                        "retrievals_per_60": 1.63,
                        "successful_retrieval_percent": 0.84,
                        "exits_per_60": 0.16,
                        "botched_retrievals_per_60": -2.9
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "ondrej palat": {
        "name": "Ondrej\u00a0Palat",
        "team": "ARI",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 142.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.26,
                        "shot_assists_per_60": 1.03,
                        "total_shot_contributions_per_60": 2.29,
                        "chances_per_60": 1.14,
                        "chance_assists_per_60": 0.99
                },
                "passing": {
                        "high_danger_assists_per_60": 0.92
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.58,
                        "rush_offense_per_60": 0.97,
                        "shots_off_hd_passes_per_60": 1.12
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.69,
                        "controlled_entry_percent": 0.26,
                        "controlled_entry_with_chance_percent": 0.25
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.22,
                        "retrievals_per_60": 1.52,
                        "successful_retrieval_percent": 0.69,
                        "exits_per_60": 0.11,
                        "botched_retrievals_per_60": -2.49
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "nico hischier": {
        "name": "Nico\u00a0Hischier",
        "team": "BOS",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 164.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.53,
                        "shot_assists_per_60": 0.69,
                        "total_shot_contributions_per_60": 1.22,
                        "chances_per_60": 0.63,
                        "chance_assists_per_60": 0.94
                },
                "passing": {
                        "high_danger_assists_per_60": 0.65
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.56,
                        "rush_offense_per_60": 0.42,
                        "shots_off_hd_passes_per_60": 0.41
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.16,
                        "controlled_entry_percent": 0.4,
                        "controlled_entry_with_chance_percent": 0.28
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.69,
                        "retrievals_per_60": 1.78,
                        "successful_retrieval_percent": 0.59,
                        "exits_per_60": 0.36,
                        "botched_retrievals_per_60": -2.35
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "nathan bastian": {
        "name": "Nathan\u00a0Bastian",
        "team": "BUF",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 138.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.79,
                        "shot_assists_per_60": 0.22,
                        "total_shot_contributions_per_60": 1.01,
                        "chances_per_60": 0.8,
                        "chance_assists_per_60": 0.27
                },
                "passing": {
                        "high_danger_assists_per_60": 0.26
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.75,
                        "rush_offense_per_60": 0.34,
                        "shots_off_hd_passes_per_60": 0.66
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.41,
                        "controlled_entry_percent": 0.65,
                        "controlled_entry_with_chance_percent": 0.19
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.62,
                        "retrievals_per_60": 4.32,
                        "successful_retrieval_percent": 0.56,
                        "exits_per_60": 0.3,
                        "botched_retrievals_per_60": -3.72
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "mike hardman": {
        "name": "Mike\u00a0Hardman",
        "team": "CGY",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 190.0,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.914,
                        "goals_against_average": 2.21,
                        "wins": 10,
                        "shutouts": 7
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "luke hughes": {
        "name": "Luke\u00a0Hughes",
        "team": "CAR",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 152.7,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.32,
                        "shot_assists_per_60": 0.41,
                        "total_shot_contributions_per_60": 1.73,
                        "chances_per_60": 1.43,
                        "chance_assists_per_60": 0.41
                },
                "passing": {
                        "high_danger_assists_per_60": 0.43
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.06,
                        "rush_offense_per_60": 0.9,
                        "shots_off_hd_passes_per_60": 1.17
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.25,
                        "controlled_entry_percent": 0.52,
                        "controlled_entry_with_chance_percent": 0.22
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.09,
                        "retrievals_per_60": 2.3,
                        "successful_retrieval_percent": 0.74,
                        "exits_per_60": 0.29,
                        "botched_retrievals_per_60": -3.42
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "justin dowling": {
        "name": "Justin\u00a0Dowling",
        "team": "CHI",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 150.6,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.63,
                        "shot_assists_per_60": 0.98,
                        "total_shot_contributions_per_60": 1.61,
                        "chances_per_60": 0.74,
                        "chance_assists_per_60": 1.13
                },
                "passing": {
                        "high_danger_assists_per_60": 1.17
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.69,
                        "rush_offense_per_60": 0.26,
                        "shots_off_hd_passes_per_60": 0.65
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.8,
                        "controlled_entry_percent": 0.51,
                        "controlled_entry_with_chance_percent": 0.16
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.66,
                        "retrievals_per_60": 2.58,
                        "successful_retrieval_percent": 0.66,
                        "exits_per_60": 0.3,
                        "botched_retrievals_per_60": -2.2
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jonas siegenthaler": {
        "name": "Jonas\u00a0Siegenthaler",
        "team": "COL",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 182.8,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.29,
                        "shot_assists_per_60": 0.98,
                        "total_shot_contributions_per_60": 2.27,
                        "chances_per_60": 1.52,
                        "chance_assists_per_60": 1.29
                },
                "passing": {
                        "high_danger_assists_per_60": 1.01
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.05,
                        "rush_offense_per_60": 0.99,
                        "shots_off_hd_passes_per_60": 1.29
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.26,
                        "controlled_entry_percent": 0.39,
                        "controlled_entry_with_chance_percent": 0.32
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.67,
                        "retrievals_per_60": 2.6,
                        "successful_retrieval_percent": 0.85,
                        "exits_per_60": 0.16,
                        "botched_retrievals_per_60": -2.77
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "johnathan kovacevic": {
        "name": "Johnathan\u00a0Kovacevic",
        "team": "CBJ",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 169.7,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.39,
                        "shot_assists_per_60": 0.73,
                        "total_shot_contributions_per_60": 1.12,
                        "chances_per_60": 0.38,
                        "chance_assists_per_60": 0.69
                },
                "passing": {
                        "high_danger_assists_per_60": 0.73
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.43,
                        "rush_offense_per_60": 0.28,
                        "shots_off_hd_passes_per_60": 0.36
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.44,
                        "controlled_entry_percent": 0.38,
                        "controlled_entry_with_chance_percent": 0.2
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.51,
                        "retrievals_per_60": 3.07,
                        "successful_retrieval_percent": 0.64,
                        "exits_per_60": 0.27,
                        "botched_retrievals_per_60": -3.37
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jesper bratt": {
        "name": "Jesper\u00a0Bratt",
        "team": "DAL",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 112.2,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.913,
                        "goals_against_average": 3.47,
                        "wins": 23,
                        "shutouts": 2
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jack hughes": {
        "name": "Jack\u00a0Hughes",
        "team": "DET",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 115.0,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.96,
                        "shot_assists_per_60": 0.75,
                        "total_shot_contributions_per_60": 1.71,
                        "chances_per_60": 1.0,
                        "chance_assists_per_60": 0.94
                },
                "passing": {
                        "high_danger_assists_per_60": 0.74
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.01,
                        "rush_offense_per_60": 0.49,
                        "shots_off_hd_passes_per_60": 0.75
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.8,
                        "controlled_entry_percent": 0.51,
                        "controlled_entry_with_chance_percent": 0.21
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.21,
                        "retrievals_per_60": 2.87,
                        "successful_retrieval_percent": 0.63,
                        "exits_per_60": 0.15,
                        "botched_retrievals_per_60": -3.97
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "erik haula": {
        "name": "Erik\u00a0Haula",
        "team": "EDM",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 195.3,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.05,
                        "shot_assists_per_60": 0.82,
                        "total_shot_contributions_per_60": 1.87,
                        "chances_per_60": 1.01,
                        "chance_assists_per_60": 0.66
                },
                "passing": {
                        "high_danger_assists_per_60": 0.84
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.21,
                        "rush_offense_per_60": 0.61,
                        "shots_off_hd_passes_per_60": 1.06
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.58,
                        "controlled_entry_percent": 0.41,
                        "controlled_entry_with_chance_percent": 0.29
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.53,
                        "retrievals_per_60": 1.89,
                        "successful_retrieval_percent": 0.72,
                        "exits_per_60": 0.31,
                        "botched_retrievals_per_60": -2.06
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "dougie hamilton": {
        "name": "Dougie\u00a0Hamilton",
        "team": "FLA",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 117.3,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.29,
                        "shot_assists_per_60": 0.68,
                        "total_shot_contributions_per_60": 1.97,
                        "chances_per_60": 0.92,
                        "chance_assists_per_60": 0.82
                },
                "passing": {
                        "high_danger_assists_per_60": 0.57
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.7,
                        "rush_offense_per_60": 0.62,
                        "shots_off_hd_passes_per_60": 1.34
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.27,
                        "controlled_entry_percent": 0.41,
                        "controlled_entry_with_chance_percent": 0.33
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.77,
                        "retrievals_per_60": 1.89,
                        "successful_retrieval_percent": 0.65,
                        "exits_per_60": 0.26,
                        "botched_retrievals_per_60": -1.7
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "dawson mercer": {
        "name": "Dawson\u00a0Mercer",
        "team": "LAK",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 143.2,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.67,
                        "shot_assists_per_60": 0.71,
                        "total_shot_contributions_per_60": 1.38,
                        "chances_per_60": 0.58,
                        "chance_assists_per_60": 0.62
                },
                "passing": {
                        "high_danger_assists_per_60": 0.8
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.69,
                        "rush_offense_per_60": 0.33,
                        "shots_off_hd_passes_per_60": 0.63
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.64,
                        "controlled_entry_percent": 0.27,
                        "controlled_entry_with_chance_percent": 0.17
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.52,
                        "retrievals_per_60": 2.96,
                        "successful_retrieval_percent": 0.64,
                        "exits_per_60": 0.16,
                        "botched_retrievals_per_60": -1.7
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "curtis lazar": {
        "name": "Curtis\u00a0Lazar",
        "team": "MIN",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 161.5,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.921,
                        "goals_against_average": 2.03,
                        "wins": 38,
                        "shutouts": 5
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "brett pesce": {
        "name": "Brett\u00a0Pesce",
        "team": "MTL",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 187.3,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.54,
                        "shot_assists_per_60": 0.76,
                        "total_shot_contributions_per_60": 2.3,
                        "chances_per_60": 1.1,
                        "chance_assists_per_60": 0.79
                },
                "passing": {
                        "high_danger_assists_per_60": 0.63
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 2.13,
                        "rush_offense_per_60": 0.67,
                        "shots_off_hd_passes_per_60": 1.14
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.15,
                        "controlled_entry_percent": 0.41,
                        "controlled_entry_with_chance_percent": 0.15
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.53,
                        "retrievals_per_60": 2.43,
                        "successful_retrieval_percent": 0.83,
                        "exits_per_60": 0.38,
                        "botched_retrievals_per_60": -1.76
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "brenden dillon": {
        "name": "Brenden\u00a0Dillon",
        "team": "NSH",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 130.7,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.32,
                        "shot_assists_per_60": 0.53,
                        "total_shot_contributions_per_60": 1.85,
                        "chances_per_60": 1.35,
                        "chance_assists_per_60": 0.71
                },
                "passing": {
                        "high_danger_assists_per_60": 0.6
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.82,
                        "rush_offense_per_60": 0.87,
                        "shots_off_hd_passes_per_60": 1.28
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.63,
                        "controlled_entry_percent": 0.61,
                        "controlled_entry_with_chance_percent": 0.28
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.05,
                        "retrievals_per_60": 1.99,
                        "successful_retrieval_percent": 0.61,
                        "exits_per_60": 0.19,
                        "botched_retrievals_per_60": -3.01
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "patrik laine": {
        "name": "Patrik\u00a0Laine",
        "team": "NJD",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 118.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.62,
                        "shot_assists_per_60": 0.86,
                        "total_shot_contributions_per_60": 1.48,
                        "chances_per_60": 0.54,
                        "chance_assists_per_60": 1.12
                },
                "passing": {
                        "high_danger_assists_per_60": 0.73
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.56,
                        "rush_offense_per_60": 0.27,
                        "shots_off_hd_passes_per_60": 0.57
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.9,
                        "controlled_entry_percent": 0.37,
                        "controlled_entry_with_chance_percent": 0.2
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.81,
                        "retrievals_per_60": 1.94,
                        "successful_retrieval_percent": 0.7,
                        "exits_per_60": 0.16,
                        "botched_retrievals_per_60": -2.32
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "nick suzuki": {
        "name": "Nick\u00a0Suzuki",
        "team": "NYI",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 179.8,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.38,
                        "shot_assists_per_60": 0.82,
                        "total_shot_contributions_per_60": 1.2,
                        "chances_per_60": 0.27,
                        "chance_assists_per_60": 0.83
                },
                "passing": {
                        "high_danger_assists_per_60": 0.79
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.31,
                        "rush_offense_per_60": 0.2,
                        "shots_off_hd_passes_per_60": 0.38
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.36,
                        "controlled_entry_percent": 0.51,
                        "controlled_entry_with_chance_percent": 0.18
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 4.77,
                        "retrievals_per_60": 4.06,
                        "successful_retrieval_percent": 0.82,
                        "exits_per_60": 0.18,
                        "botched_retrievals_per_60": -2.14
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "mike matheson": {
        "name": "Mike\u00a0Matheson",
        "team": "NYR",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 181.3,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.904,
                        "goals_against_average": 2.89,
                        "wins": 42,
                        "shutouts": 3
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "lane hutson": {
        "name": "Lane\u00a0Hutson",
        "team": "OTT",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 195.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.68,
                        "shot_assists_per_60": 0.48,
                        "total_shot_contributions_per_60": 2.16,
                        "chances_per_60": 1.57,
                        "chance_assists_per_60": 0.59
                },
                "passing": {
                        "high_danger_assists_per_60": 0.51
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 2.21,
                        "rush_offense_per_60": 0.57,
                        "shots_off_hd_passes_per_60": 1.23
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.33,
                        "controlled_entry_percent": 0.45,
                        "controlled_entry_with_chance_percent": 0.16
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.59,
                        "retrievals_per_60": 2.19,
                        "successful_retrieval_percent": 0.84,
                        "exits_per_60": 0.2,
                        "botched_retrievals_per_60": -3.88
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "kirby dach": {
        "name": "Kirby\u00a0Dach",
        "team": "PHI",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 127.6,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.8,
                        "shot_assists_per_60": 0.43,
                        "total_shot_contributions_per_60": 1.23,
                        "chances_per_60": 0.85,
                        "chance_assists_per_60": 0.51
                },
                "passing": {
                        "high_danger_assists_per_60": 0.51
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.72,
                        "rush_offense_per_60": 0.56,
                        "shots_off_hd_passes_per_60": 0.6
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.26,
                        "controlled_entry_percent": 0.49,
                        "controlled_entry_with_chance_percent": 0.31
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.89,
                        "retrievals_per_60": 2.55,
                        "successful_retrieval_percent": 0.78,
                        "exits_per_60": 0.34,
                        "botched_retrievals_per_60": -2.57
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "kaiden guhle": {
        "name": "Kaiden\u00a0Guhle",
        "team": "PIT",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 128.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.8,
                        "shot_assists_per_60": 0.76,
                        "total_shot_contributions_per_60": 1.56,
                        "chances_per_60": 0.76,
                        "chance_assists_per_60": 0.71
                },
                "passing": {
                        "high_danger_assists_per_60": 0.7
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.11,
                        "rush_offense_per_60": 0.3,
                        "shots_off_hd_passes_per_60": 0.62
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.15,
                        "controlled_entry_percent": 0.28,
                        "controlled_entry_with_chance_percent": 0.3
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.09,
                        "retrievals_per_60": 2.57,
                        "successful_retrieval_percent": 0.7,
                        "exits_per_60": 0.14,
                        "botched_retrievals_per_60": -2.0
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "juraj slafkovský": {
        "name": "Juraj\u00a0Slafkovsk\u00fd",
        "team": "SJS",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 158.8,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.22,
                        "shot_assists_per_60": 0.66,
                        "total_shot_contributions_per_60": 0.88,
                        "chances_per_60": 0.21,
                        "chance_assists_per_60": 0.87
                },
                "passing": {
                        "high_danger_assists_per_60": 0.54
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.19,
                        "rush_offense_per_60": 0.07,
                        "shots_off_hd_passes_per_60": 0.23
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.38,
                        "controlled_entry_percent": 0.27,
                        "controlled_entry_with_chance_percent": 0.33
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 4.05,
                        "retrievals_per_60": 3.7,
                        "successful_retrieval_percent": 0.77,
                        "exits_per_60": 0.22,
                        "botched_retrievals_per_60": -2.66
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "josh anderson": {
        "name": "Josh\u00a0Anderson",
        "team": "SEA",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 102.3,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.929,
                        "goals_against_average": 2.92,
                        "wins": 44,
                        "shutouts": 7
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "joel armia": {
        "name": "Joel\u00a0Armia",
        "team": "STL",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 141.2,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.47,
                        "shot_assists_per_60": 0.51,
                        "total_shot_contributions_per_60": 1.98,
                        "chances_per_60": 1.26,
                        "chance_assists_per_60": 0.43
                },
                "passing": {
                        "high_danger_assists_per_60": 0.48
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.86,
                        "rush_offense_per_60": 0.53,
                        "shots_off_hd_passes_per_60": 1.58
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.25,
                        "controlled_entry_percent": 0.43,
                        "controlled_entry_with_chance_percent": 0.31
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.93,
                        "retrievals_per_60": 2.49,
                        "successful_retrieval_percent": 0.73,
                        "exits_per_60": 0.26,
                        "botched_retrievals_per_60": -3.24
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jayden struble": {
        "name": "Jayden\u00a0Struble",
        "team": "TBL",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 188.3,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.71,
                        "shot_assists_per_60": 0.59,
                        "total_shot_contributions_per_60": 1.3,
                        "chances_per_60": 0.7,
                        "chance_assists_per_60": 0.58
                },
                "passing": {
                        "high_danger_assists_per_60": 0.57
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.77,
                        "rush_offense_per_60": 0.3,
                        "shots_off_hd_passes_per_60": 0.7
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.6,
                        "controlled_entry_percent": 0.43,
                        "controlled_entry_with_chance_percent": 0.28
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.72,
                        "retrievals_per_60": 2.83,
                        "successful_retrieval_percent": 0.69,
                        "exits_per_60": 0.2,
                        "botched_retrievals_per_60": -3.63
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jake evans": {
        "name": "Jake\u00a0Evans",
        "team": "TOR",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 175.0,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.63,
                        "shot_assists_per_60": 1.18,
                        "total_shot_contributions_per_60": 1.81,
                        "chances_per_60": 0.46,
                        "chance_assists_per_60": 0.98
                },
                "passing": {
                        "high_danger_assists_per_60": 1.17
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.53,
                        "rush_offense_per_60": 0.45,
                        "shots_off_hd_passes_per_60": 0.68
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.95,
                        "controlled_entry_percent": 0.32,
                        "controlled_entry_with_chance_percent": 0.24
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.14,
                        "retrievals_per_60": 2.4,
                        "successful_retrieval_percent": 0.69,
                        "exits_per_60": 0.16,
                        "botched_retrievals_per_60": -1.9
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "emil heineman": {
        "name": "Emil\u00a0Heineman",
        "team": "VAN",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 156.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.56,
                        "shot_assists_per_60": 0.44,
                        "total_shot_contributions_per_60": 1.0,
                        "chances_per_60": 0.48,
                        "chance_assists_per_60": 0.38
                },
                "passing": {
                        "high_danger_assists_per_60": 0.5
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.45,
                        "rush_offense_per_60": 0.18,
                        "shots_off_hd_passes_per_60": 0.51
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.57,
                        "controlled_entry_percent": 0.54,
                        "controlled_entry_with_chance_percent": 0.27
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.61,
                        "retrievals_per_60": 3.1,
                        "successful_retrieval_percent": 0.75,
                        "exits_per_60": 0.34,
                        "botched_retrievals_per_60": -1.54
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "david savard": {
        "name": "David\u00a0Savard",
        "team": "VGK",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 124.0,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.914,
                        "goals_against_average": 2.9,
                        "wins": 38,
                        "shutouts": 2
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "cole caufield": {
        "name": "Cole\u00a0Caufield",
        "team": "WSH",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 199.7,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.8,
                        "shot_assists_per_60": 0.43,
                        "total_shot_contributions_per_60": 1.23,
                        "chances_per_60": 1.0,
                        "chance_assists_per_60": 0.51
                },
                "passing": {
                        "high_danger_assists_per_60": 0.38
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.01,
                        "rush_offense_per_60": 0.37,
                        "shots_off_hd_passes_per_60": 0.71
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.18,
                        "controlled_entry_percent": 0.33,
                        "controlled_entry_with_chance_percent": 0.2
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.46,
                        "retrievals_per_60": 2.08,
                        "successful_retrieval_percent": 0.6,
                        "exits_per_60": 0.36,
                        "botched_retrievals_per_60": -2.55
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "christian dvorak": {
        "name": "Christian\u00a0Dvorak",
        "team": "WPG",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 165.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.55,
                        "shot_assists_per_60": 0.66,
                        "total_shot_contributions_per_60": 1.21,
                        "chances_per_60": 0.42,
                        "chance_assists_per_60": 0.76
                },
                "passing": {
                        "high_danger_assists_per_60": 0.61
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.69,
                        "rush_offense_per_60": 0.22,
                        "shots_off_hd_passes_per_60": 0.45
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.98,
                        "controlled_entry_percent": 0.44,
                        "controlled_entry_with_chance_percent": 0.25
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.47,
                        "retrievals_per_60": 2.38,
                        "successful_retrieval_percent": 0.75,
                        "exits_per_60": 0.32,
                        "botched_retrievals_per_60": -3.45
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "brendan gallagher": {
        "name": "Brendan\u00a0Gallagher",
        "team": "ANA",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 191.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.08,
                        "shot_assists_per_60": 1.19,
                        "total_shot_contributions_per_60": 2.27,
                        "chances_per_60": 1.35,
                        "chance_assists_per_60": 1.34
                },
                "passing": {
                        "high_danger_assists_per_60": 1.08
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.37,
                        "rush_offense_per_60": 0.58,
                        "shots_off_hd_passes_per_60": 0.81
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.66,
                        "controlled_entry_percent": 0.48,
                        "controlled_entry_with_chance_percent": 0.28
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.79,
                        "retrievals_per_60": 2.76,
                        "successful_retrieval_percent": 0.75,
                        "exits_per_60": 0.12,
                        "botched_retrievals_per_60": -3.78
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "arber xhekaj": {
        "name": "Arber\u00a0Xhekaj",
        "team": "ARI",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 170.7,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.7,
                        "shot_assists_per_60": 0.48,
                        "total_shot_contributions_per_60": 1.18,
                        "chances_per_60": 0.9,
                        "chance_assists_per_60": 0.4
                },
                "passing": {
                        "high_danger_assists_per_60": 0.5
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.73,
                        "rush_offense_per_60": 0.53,
                        "shots_off_hd_passes_per_60": 0.58
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.65,
                        "controlled_entry_percent": 0.63,
                        "controlled_entry_with_chance_percent": 0.31
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.61,
                        "retrievals_per_60": 3.96,
                        "successful_retrieval_percent": 0.68,
                        "exits_per_60": 0.18,
                        "botched_retrievals_per_60": -2.22
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "alex newhook": {
        "name": "Alex\u00a0Newhook",
        "team": "BOS",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 142.9,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.924,
                        "goals_against_average": 2.66,
                        "wins": 41,
                        "shutouts": 7
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "zach bogosian": {
        "name": "Zach\u00a0Bogosian",
        "team": "BUF",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 168.3,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.32,
                        "shot_assists_per_60": 0.74,
                        "total_shot_contributions_per_60": 2.06,
                        "chances_per_60": 1.46,
                        "chance_assists_per_60": 0.79
                },
                "passing": {
                        "high_danger_assists_per_60": 0.62
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.73,
                        "rush_offense_per_60": 0.42,
                        "shots_off_hd_passes_per_60": 0.93
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.81,
                        "controlled_entry_percent": 0.52,
                        "controlled_entry_with_chance_percent": 0.35
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.66,
                        "retrievals_per_60": 2.62,
                        "successful_retrieval_percent": 0.66,
                        "exits_per_60": 0.17,
                        "botched_retrievals_per_60": -2.2
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "yakov trenin": {
        "name": "Yakov\u00a0Trenin",
        "team": "CGY",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 192.1,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.58,
                        "shot_assists_per_60": 0.41,
                        "total_shot_contributions_per_60": 1.99,
                        "chances_per_60": 1.48,
                        "chance_assists_per_60": 0.46
                },
                "passing": {
                        "high_danger_assists_per_60": 0.35
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.76,
                        "rush_offense_per_60": 0.6,
                        "shots_off_hd_passes_per_60": 1.44
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.22,
                        "controlled_entry_percent": 0.63,
                        "controlled_entry_with_chance_percent": 0.15
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.01,
                        "retrievals_per_60": 2.28,
                        "successful_retrieval_percent": 0.69,
                        "exits_per_60": 0.28,
                        "botched_retrievals_per_60": -1.63
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "ryan hartman": {
        "name": "Ryan\u00a0Hartman",
        "team": "CAR",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 191.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.13,
                        "shot_assists_per_60": 1.17,
                        "total_shot_contributions_per_60": 2.3,
                        "chances_per_60": 1.43,
                        "chance_assists_per_60": 1.02
                },
                "passing": {
                        "high_danger_assists_per_60": 0.94
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.36,
                        "rush_offense_per_60": 0.51,
                        "shots_off_hd_passes_per_60": 1.2
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.33,
                        "controlled_entry_percent": 0.26,
                        "controlled_entry_with_chance_percent": 0.21
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.69,
                        "retrievals_per_60": 1.79,
                        "successful_retrieval_percent": 0.58,
                        "exits_per_60": 0.38,
                        "botched_retrievals_per_60": -1.69
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "matt boldy": {
        "name": "Matt\u00a0Boldy",
        "team": "CHI",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 119.3,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.76,
                        "shot_assists_per_60": 0.86,
                        "total_shot_contributions_per_60": 1.62,
                        "chances_per_60": 0.85,
                        "chance_assists_per_60": 0.97
                },
                "passing": {
                        "high_danger_assists_per_60": 0.73
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.8,
                        "rush_offense_per_60": 0.52,
                        "shots_off_hd_passes_per_60": 0.74
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.66,
                        "controlled_entry_percent": 0.4,
                        "controlled_entry_with_chance_percent": 0.21
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 4.53,
                        "retrievals_per_60": 4.29,
                        "successful_retrieval_percent": 0.81,
                        "exits_per_60": 0.31,
                        "botched_retrievals_per_60": -3.49
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "mats zuccarello": {
        "name": "Mats\u00a0Zuccarello",
        "team": "COL",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 186.7,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.925,
                        "goals_against_average": 2.58,
                        "wins": 45,
                        "shutouts": 8
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "marcus johansson": {
        "name": "Marcus\u00a0Johansson",
        "team": "CBJ",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 135.0,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.11,
                        "shot_assists_per_60": 0.76,
                        "total_shot_contributions_per_60": 1.87,
                        "chances_per_60": 1.39,
                        "chance_assists_per_60": 0.78
                },
                "passing": {
                        "high_danger_assists_per_60": 0.62
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.35,
                        "rush_offense_per_60": 0.87,
                        "shots_off_hd_passes_per_60": 0.96
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.75,
                        "controlled_entry_percent": 0.51,
                        "controlled_entry_with_chance_percent": 0.31
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.2,
                        "retrievals_per_60": 2.97,
                        "successful_retrieval_percent": 0.75,
                        "exits_per_60": 0.18,
                        "botched_retrievals_per_60": -2.53
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "marcus foligno": {
        "name": "Marcus\u00a0Foligno",
        "team": "DAL",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 157.6,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.7,
                        "shot_assists_per_60": 0.77,
                        "total_shot_contributions_per_60": 2.47,
                        "chances_per_60": 2.0,
                        "chance_assists_per_60": 1.03
                },
                "passing": {
                        "high_danger_assists_per_60": 0.78
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.96,
                        "rush_offense_per_60": 1.1,
                        "shots_off_hd_passes_per_60": 1.51
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.12,
                        "controlled_entry_percent": 0.31,
                        "controlled_entry_with_chance_percent": 0.3
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.31,
                        "retrievals_per_60": 2.88,
                        "successful_retrieval_percent": 0.83,
                        "exits_per_60": 0.31,
                        "botched_retrievals_per_60": -2.48
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "marco rossi": {
        "name": "Marco\u00a0Rossi",
        "team": "DET",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 197.8,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.55,
                        "shot_assists_per_60": 0.83,
                        "total_shot_contributions_per_60": 2.38,
                        "chances_per_60": 1.73,
                        "chance_assists_per_60": 1.05
                },
                "passing": {
                        "high_danger_assists_per_60": 0.75
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.54,
                        "rush_offense_per_60": 0.96,
                        "shots_off_hd_passes_per_60": 1.31
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.1,
                        "controlled_entry_percent": 0.49,
                        "controlled_entry_with_chance_percent": 0.35
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.36,
                        "retrievals_per_60": 2.48,
                        "successful_retrieval_percent": 0.65,
                        "exits_per_60": 0.29,
                        "botched_retrievals_per_60": -3.51
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "marat khusnutdinov": {
        "name": "Marat\u00a0Khusnutdinov",
        "team": "EDM",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 146.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.16,
                        "shot_assists_per_60": 0.29,
                        "total_shot_contributions_per_60": 0.45,
                        "chances_per_60": 0.17,
                        "chance_assists_per_60": 0.41
                },
                "passing": {
                        "high_danger_assists_per_60": 0.32
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.14,
                        "rush_offense_per_60": 0.11,
                        "shots_off_hd_passes_per_60": 0.13
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.32,
                        "controlled_entry_percent": 0.26,
                        "controlled_entry_with_chance_percent": 0.31
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 4.14,
                        "retrievals_per_60": 4.43,
                        "successful_retrieval_percent": 0.7,
                        "exits_per_60": 0.36,
                        "botched_retrievals_per_60": -3.74
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "kirill kaprizov": {
        "name": "Kirill\u00a0Kaprizov",
        "team": "FLA",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 112.2,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.909,
                        "goals_against_average": 3.31,
                        "wins": 43,
                        "shutouts": 0
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jonas brodin": {
        "name": "Jonas\u00a0Brodin",
        "team": "LAK",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 182.3,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.39,
                        "shot_assists_per_60": 0.79,
                        "total_shot_contributions_per_60": 2.18,
                        "chances_per_60": 1.61,
                        "chance_assists_per_60": 0.67
                },
                "passing": {
                        "high_danger_assists_per_60": 0.88
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.61,
                        "rush_offense_per_60": 0.69,
                        "shots_off_hd_passes_per_60": 1.41
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.31,
                        "controlled_entry_percent": 0.63,
                        "controlled_entry_with_chance_percent": 0.28
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.84,
                        "retrievals_per_60": 2.58,
                        "successful_retrieval_percent": 0.79,
                        "exits_per_60": 0.24,
                        "botched_retrievals_per_60": -1.75
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jon merrill": {
        "name": "Jon\u00a0Merrill",
        "team": "MIN",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 152.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.17,
                        "shot_assists_per_60": 0.52,
                        "total_shot_contributions_per_60": 1.69,
                        "chances_per_60": 1.17,
                        "chance_assists_per_60": 0.64
                },
                "passing": {
                        "high_danger_assists_per_60": 0.47
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.0,
                        "rush_offense_per_60": 0.8,
                        "shots_off_hd_passes_per_60": 0.95
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.92,
                        "controlled_entry_percent": 0.32,
                        "controlled_entry_with_chance_percent": 0.26
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.32,
                        "retrievals_per_60": 2.4,
                        "successful_retrieval_percent": 0.76,
                        "exits_per_60": 0.18,
                        "botched_retrievals_per_60": -3.46
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "joel eriksson_ek": {
        "name": "Joel\u00a0Eriksson Ek",
        "team": "MTL",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 176.6,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.54,
                        "shot_assists_per_60": 0.53,
                        "total_shot_contributions_per_60": 2.07,
                        "chances_per_60": 1.15,
                        "chance_assists_per_60": 0.63
                },
                "passing": {
                        "high_danger_assists_per_60": 0.61
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.69,
                        "rush_offense_per_60": 0.64,
                        "shots_off_hd_passes_per_60": 1.2
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.79,
                        "controlled_entry_percent": 0.29,
                        "controlled_entry_with_chance_percent": 0.22
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.92,
                        "retrievals_per_60": 2.48,
                        "successful_retrieval_percent": 0.81,
                        "exits_per_60": 0.36,
                        "botched_retrievals_per_60": -2.56
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jared spurgeon": {
        "name": "Jared\u00a0Spurgeon",
        "team": "NSH",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 112.0,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.36,
                        "shot_assists_per_60": 0.6,
                        "total_shot_contributions_per_60": 0.96,
                        "chances_per_60": 0.46,
                        "chance_assists_per_60": 0.68
                },
                "passing": {
                        "high_danger_assists_per_60": 0.48
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.42,
                        "rush_offense_per_60": 0.24,
                        "shots_off_hd_passes_per_60": 0.35
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.63,
                        "controlled_entry_percent": 0.39,
                        "controlled_entry_with_chance_percent": 0.33
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.19,
                        "retrievals_per_60": 3.33,
                        "successful_retrieval_percent": 0.8,
                        "exits_per_60": 0.14,
                        "botched_retrievals_per_60": -3.37
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jake middleton": {
        "name": "Jake\u00a0Middleton",
        "team": "NJD",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 104.5,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.915,
                        "goals_against_average": 2.72,
                        "wins": 34,
                        "shutouts": 6
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "frederick gaudreau": {
        "name": "Frederick\u00a0Gaudreau",
        "team": "NYI",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 172.1,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.53,
                        "shot_assists_per_60": 0.99,
                        "total_shot_contributions_per_60": 2.52,
                        "chances_per_60": 1.49,
                        "chance_assists_per_60": 1.2
                },
                "passing": {
                        "high_danger_assists_per_60": 1.09
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.41,
                        "rush_offense_per_60": 0.8,
                        "shots_off_hd_passes_per_60": 1.31
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.08,
                        "controlled_entry_percent": 0.42,
                        "controlled_entry_with_chance_percent": 0.35
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.94,
                        "retrievals_per_60": 2.57,
                        "successful_retrieval_percent": 0.6,
                        "exits_per_60": 0.28,
                        "botched_retrievals_per_60": -2.3
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "declan chisholm": {
        "name": "Declan\u00a0Chisholm",
        "team": "NYR",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 185.1,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.59,
                        "shot_assists_per_60": 1.16,
                        "total_shot_contributions_per_60": 2.75,
                        "chances_per_60": 1.55,
                        "chance_assists_per_60": 1.14
                },
                "passing": {
                        "high_danger_assists_per_60": 0.96
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 2.16,
                        "rush_offense_per_60": 0.75,
                        "shots_off_hd_passes_per_60": 1.28
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.42,
                        "controlled_entry_percent": 0.3,
                        "controlled_entry_with_chance_percent": 0.17
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.83,
                        "retrievals_per_60": 2.08,
                        "successful_retrieval_percent": 0.76,
                        "exits_per_60": 0.37,
                        "botched_retrievals_per_60": -1.99
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "brock faber": {
        "name": "Brock\u00a0Faber",
        "team": "OTT",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 104.6,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.64,
                        "shot_assists_per_60": 0.65,
                        "total_shot_contributions_per_60": 2.29,
                        "chances_per_60": 1.82,
                        "chance_assists_per_60": 0.77
                },
                "passing": {
                        "high_danger_assists_per_60": 0.64
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 2.09,
                        "rush_offense_per_60": 1.23,
                        "shots_off_hd_passes_per_60": 1.77
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.59,
                        "controlled_entry_percent": 0.37,
                        "controlled_entry_with_chance_percent": 0.23
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.24,
                        "retrievals_per_60": 1.9,
                        "successful_retrieval_percent": 0.58,
                        "exits_per_60": 0.22,
                        "botched_retrievals_per_60": -1.88
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "warren foegele": {
        "name": "Warren\u00a0Foegele",
        "team": "PHI",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 103.8,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.2,
                        "shot_assists_per_60": 0.31,
                        "total_shot_contributions_per_60": 0.51,
                        "chances_per_60": 0.21,
                        "chance_assists_per_60": 0.42
                },
                "passing": {
                        "high_danger_assists_per_60": 0.37
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.19,
                        "rush_offense_per_60": 0.06,
                        "shots_off_hd_passes_per_60": 0.14
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.76,
                        "controlled_entry_percent": 0.5,
                        "controlled_entry_with_chance_percent": 0.25
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.0,
                        "retrievals_per_60": 3.68,
                        "successful_retrieval_percent": 0.67,
                        "exits_per_60": 0.13,
                        "botched_retrievals_per_60": -3.38
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "vladislav gavrikov": {
        "name": "Vladislav\u00a0Gavrikov",
        "team": "PIT",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 178.5,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.927,
                        "goals_against_average": 2.6,
                        "wins": 28,
                        "shutouts": 8
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "trevor moore": {
        "name": "Trevor\u00a0Moore",
        "team": "SJS",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 121.3,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.8,
                        "shot_assists_per_60": 0.94,
                        "total_shot_contributions_per_60": 1.74,
                        "chances_per_60": 0.97,
                        "chance_assists_per_60": 1.0
                },
                "passing": {
                        "high_danger_assists_per_60": 0.77
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.83,
                        "rush_offense_per_60": 0.63,
                        "shots_off_hd_passes_per_60": 0.64
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.36,
                        "controlled_entry_percent": 0.29,
                        "controlled_entry_with_chance_percent": 0.34
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.77,
                        "retrievals_per_60": 1.63,
                        "successful_retrieval_percent": 0.81,
                        "exits_per_60": 0.22,
                        "botched_retrievals_per_60": -3.1
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "trevor lewis": {
        "name": "Trevor\u00a0Lewis",
        "team": "SEA",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 119.6,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.77,
                        "shot_assists_per_60": 0.69,
                        "total_shot_contributions_per_60": 1.46,
                        "chances_per_60": 0.72,
                        "chance_assists_per_60": 0.61
                },
                "passing": {
                        "high_danger_assists_per_60": 0.62
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.75,
                        "rush_offense_per_60": 0.29,
                        "shots_off_hd_passes_per_60": 0.55
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.67,
                        "controlled_entry_percent": 0.48,
                        "controlled_entry_with_chance_percent": 0.25
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.18,
                        "retrievals_per_60": 2.07,
                        "successful_retrieval_percent": 0.59,
                        "exits_per_60": 0.3,
                        "botched_retrievals_per_60": -3.33
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "tanner jeannot": {
        "name": "Tanner\u00a0Jeannot",
        "team": "STL",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 113.8,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.78,
                        "shot_assists_per_60": 0.5,
                        "total_shot_contributions_per_60": 1.28,
                        "chances_per_60": 0.89,
                        "chance_assists_per_60": 0.55
                },
                "passing": {
                        "high_danger_assists_per_60": 0.55
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.97,
                        "rush_offense_per_60": 0.32,
                        "shots_off_hd_passes_per_60": 0.58
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.5,
                        "controlled_entry_percent": 0.54,
                        "controlled_entry_with_chance_percent": 0.29
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.78,
                        "retrievals_per_60": 2.37,
                        "successful_retrieval_percent": 0.7,
                        "exits_per_60": 0.39,
                        "botched_retrievals_per_60": -2.36
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "quinton byfield": {
        "name": "Quinton\u00a0Byfield",
        "team": "TBL",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 144.6,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.67,
                        "shot_assists_per_60": 0.4,
                        "total_shot_contributions_per_60": 1.07,
                        "chances_per_60": 0.84,
                        "chance_assists_per_60": 0.39
                },
                "passing": {
                        "high_danger_assists_per_60": 0.35
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.84,
                        "rush_offense_per_60": 0.34,
                        "shots_off_hd_passes_per_60": 0.58
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.62,
                        "controlled_entry_percent": 0.62,
                        "controlled_entry_with_chance_percent": 0.24
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.37,
                        "retrievals_per_60": 3.71,
                        "successful_retrieval_percent": 0.72,
                        "exits_per_60": 0.28,
                        "botched_retrievals_per_60": -3.8
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "phillip danault": {
        "name": "Phillip\u00a0Danault",
        "team": "TOR",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 121.5,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.914,
                        "goals_against_average": 2.37,
                        "wins": 45,
                        "shutouts": 0
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "mikey anderson": {
        "name": "Mikey\u00a0Anderson",
        "team": "VAN",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 102.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.15,
                        "shot_assists_per_60": 0.75,
                        "total_shot_contributions_per_60": 1.9,
                        "chances_per_60": 1.45,
                        "chance_assists_per_60": 0.71
                },
                "passing": {
                        "high_danger_assists_per_60": 0.73
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.53,
                        "rush_offense_per_60": 0.49,
                        "shots_off_hd_passes_per_60": 0.87
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.19,
                        "controlled_entry_percent": 0.45,
                        "controlled_entry_with_chance_percent": 0.23
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.31,
                        "retrievals_per_60": 2.48,
                        "successful_retrieval_percent": 0.63,
                        "exits_per_60": 0.37,
                        "botched_retrievals_per_60": -3.77
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "kevin fiala": {
        "name": "Kevin\u00a0Fiala",
        "team": "VGK",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 101.3,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.75,
                        "shot_assists_per_60": 0.53,
                        "total_shot_contributions_per_60": 1.28,
                        "chances_per_60": 0.63,
                        "chance_assists_per_60": 0.56
                },
                "passing": {
                        "high_danger_assists_per_60": 0.56
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.72,
                        "rush_offense_per_60": 0.48,
                        "shots_off_hd_passes_per_60": 0.79
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.54,
                        "controlled_entry_percent": 0.61,
                        "controlled_entry_with_chance_percent": 0.2
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.97,
                        "retrievals_per_60": 2.64,
                        "successful_retrieval_percent": 0.84,
                        "exits_per_60": 0.21,
                        "botched_retrievals_per_60": -1.59
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jordan spence": {
        "name": "Jordan\u00a0Spence",
        "team": "WSH",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 137.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.54,
                        "shot_assists_per_60": 1.08,
                        "total_shot_contributions_per_60": 2.62,
                        "chances_per_60": 1.95,
                        "chance_assists_per_60": 0.9
                },
                "passing": {
                        "high_danger_assists_per_60": 1.1
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 2.03,
                        "rush_offense_per_60": 1.23,
                        "shots_off_hd_passes_per_60": 1.65
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.2,
                        "controlled_entry_percent": 0.62,
                        "controlled_entry_with_chance_percent": 0.18
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.64,
                        "retrievals_per_60": 1.75,
                        "successful_retrieval_percent": 0.81,
                        "exits_per_60": 0.3,
                        "botched_retrievals_per_60": -3.12
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "joel edmundson": {
        "name": "Joel\u00a0Edmundson",
        "team": "WPG",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 137.1,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.5,
                        "shot_assists_per_60": 0.58,
                        "total_shot_contributions_per_60": 1.08,
                        "chances_per_60": 0.35,
                        "chance_assists_per_60": 0.71
                },
                "passing": {
                        "high_danger_assists_per_60": 0.65
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.52,
                        "rush_offense_per_60": 0.31,
                        "shots_off_hd_passes_per_60": 0.55
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.79,
                        "controlled_entry_percent": 0.47,
                        "controlled_entry_with_chance_percent": 0.18
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.13,
                        "retrievals_per_60": 3.02,
                        "successful_retrieval_percent": 0.6,
                        "exits_per_60": 0.3,
                        "botched_retrievals_per_60": -1.96
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jacob moverare": {
        "name": "Jacob\u00a0Moverare",
        "team": "ANA",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 190.6,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.91,
                        "goals_against_average": 3.12,
                        "wins": 44,
                        "shutouts": 8
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "drew doughty": {
        "name": "Drew\u00a0Doughty",
        "team": "ARI",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 105.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.79,
                        "shot_assists_per_60": 0.67,
                        "total_shot_contributions_per_60": 1.46,
                        "chances_per_60": 0.74,
                        "chance_assists_per_60": 0.67
                },
                "passing": {
                        "high_danger_assists_per_60": 0.74
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.71,
                        "rush_offense_per_60": 0.28,
                        "shots_off_hd_passes_per_60": 0.8
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.48,
                        "controlled_entry_percent": 0.43,
                        "controlled_entry_with_chance_percent": 0.27
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.45,
                        "retrievals_per_60": 1.65,
                        "successful_retrieval_percent": 0.56,
                        "exits_per_60": 0.13,
                        "botched_retrievals_per_60": -2.61
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "brandt clarke": {
        "name": "Brandt\u00a0Clarke",
        "team": "BOS",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 191.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.44,
                        "shot_assists_per_60": 1.11,
                        "total_shot_contributions_per_60": 2.55,
                        "chances_per_60": 1.82,
                        "chance_assists_per_60": 1.44
                },
                "passing": {
                        "high_danger_assists_per_60": 1.25
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.95,
                        "rush_offense_per_60": 1.07,
                        "shots_off_hd_passes_per_60": 1.04
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.93,
                        "controlled_entry_percent": 0.46,
                        "controlled_entry_with_chance_percent": 0.25
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.44,
                        "retrievals_per_60": 1.71,
                        "successful_retrieval_percent": 0.81,
                        "exits_per_60": 0.18,
                        "botched_retrievals_per_60": -1.81
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "anze kopitar": {
        "name": "Anze\u00a0Kopitar",
        "team": "BUF",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 156.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.42,
                        "shot_assists_per_60": 0.82,
                        "total_shot_contributions_per_60": 2.24,
                        "chances_per_60": 1.56,
                        "chance_assists_per_60": 1.13
                },
                "passing": {
                        "high_danger_assists_per_60": 0.87
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.57,
                        "rush_offense_per_60": 0.9,
                        "shots_off_hd_passes_per_60": 1.04
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.85,
                        "controlled_entry_percent": 0.35,
                        "controlled_entry_with_chance_percent": 0.33
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.47,
                        "retrievals_per_60": 1.61,
                        "successful_retrieval_percent": 0.85,
                        "exits_per_60": 0.17,
                        "botched_retrievals_per_60": -2.9
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "alex turcotte": {
        "name": "Alex\u00a0Turcotte",
        "team": "CGY",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 191.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.49,
                        "shot_assists_per_60": 0.51,
                        "total_shot_contributions_per_60": 1.0,
                        "chances_per_60": 0.41,
                        "chance_assists_per_60": 0.43
                },
                "passing": {
                        "high_danger_assists_per_60": 0.44
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.41,
                        "rush_offense_per_60": 0.26,
                        "shots_off_hd_passes_per_60": 0.36
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.56,
                        "controlled_entry_percent": 0.28,
                        "controlled_entry_with_chance_percent": 0.18
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 4.42,
                        "retrievals_per_60": 3.85,
                        "successful_retrieval_percent": 0.81,
                        "exits_per_60": 0.34,
                        "botched_retrievals_per_60": -1.8
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "alex laferriere": {
        "name": "Alex\u00a0Laferriere",
        "team": "CAR",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 181.7,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.902,
                        "goals_against_average": 2.97,
                        "wins": 22,
                        "shutouts": 0
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "adrian kempe": {
        "name": "Adrian\u00a0Kempe",
        "team": "CHI",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 160.7,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.53,
                        "shot_assists_per_60": 0.57,
                        "total_shot_contributions_per_60": 1.1,
                        "chances_per_60": 0.49,
                        "chance_assists_per_60": 0.49
                },
                "passing": {
                        "high_danger_assists_per_60": 0.65
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.5,
                        "rush_offense_per_60": 0.3,
                        "shots_off_hd_passes_per_60": 0.58
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.43,
                        "controlled_entry_percent": 0.65,
                        "controlled_entry_with_chance_percent": 0.31
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.83,
                        "retrievals_per_60": 1.99,
                        "successful_retrieval_percent": 0.63,
                        "exits_per_60": 0.1,
                        "botched_retrievals_per_60": -3.22
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "uvis balinskis": {
        "name": "Uvis\u00a0Balinskis",
        "team": "COL",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 160.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.82,
                        "shot_assists_per_60": 0.77,
                        "total_shot_contributions_per_60": 1.59,
                        "chances_per_60": 1.04,
                        "chance_assists_per_60": 0.97
                },
                "passing": {
                        "high_danger_assists_per_60": 0.65
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.79,
                        "rush_offense_per_60": 0.4,
                        "shots_off_hd_passes_per_60": 0.86
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.04,
                        "controlled_entry_percent": 0.6,
                        "controlled_entry_with_chance_percent": 0.31
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.37,
                        "retrievals_per_60": 2.55,
                        "successful_retrieval_percent": 0.83,
                        "exits_per_60": 0.35,
                        "botched_retrievals_per_60": -2.07
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "tomas nosek": {
        "name": "Tomas\u00a0Nosek",
        "team": "CBJ",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 152.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.87,
                        "shot_assists_per_60": 0.43,
                        "total_shot_contributions_per_60": 1.3,
                        "chances_per_60": 1.08,
                        "chance_assists_per_60": 0.55
                },
                "passing": {
                        "high_danger_assists_per_60": 0.36
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.13,
                        "rush_offense_per_60": 0.55,
                        "shots_off_hd_passes_per_60": 0.67
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.76,
                        "controlled_entry_percent": 0.5,
                        "controlled_entry_with_chance_percent": 0.31
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.72,
                        "retrievals_per_60": 2.27,
                        "successful_retrieval_percent": 0.76,
                        "exits_per_60": 0.35,
                        "botched_retrievals_per_60": -1.92
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "sam reinhart": {
        "name": "Sam\u00a0Reinhart",
        "team": "DAL",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 121.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.79,
                        "shot_assists_per_60": 0.63,
                        "total_shot_contributions_per_60": 1.42,
                        "chances_per_60": 0.67,
                        "chance_assists_per_60": 0.59
                },
                "passing": {
                        "high_danger_assists_per_60": 0.56
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.74,
                        "rush_offense_per_60": 0.45,
                        "shots_off_hd_passes_per_60": 0.76
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.5,
                        "controlled_entry_percent": 0.27,
                        "controlled_entry_with_chance_percent": 0.18
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.39,
                        "retrievals_per_60": 2.97,
                        "successful_retrieval_percent": 0.82,
                        "exits_per_60": 0.21,
                        "botched_retrievals_per_60": -3.35
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "sam bennett": {
        "name": "Sam\u00a0Bennett",
        "team": "DET",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 189.5,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.919,
                        "goals_against_average": 3.45,
                        "wins": 40,
                        "shutouts": 3
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "niko mikkola": {
        "name": "Niko\u00a0Mikkola",
        "team": "EDM",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 184.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.53,
                        "shot_assists_per_60": 0.82,
                        "total_shot_contributions_per_60": 1.35,
                        "chances_per_60": 0.42,
                        "chance_assists_per_60": 0.95
                },
                "passing": {
                        "high_danger_assists_per_60": 0.76
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.61,
                        "rush_offense_per_60": 0.18,
                        "shots_off_hd_passes_per_60": 0.43
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.88,
                        "controlled_entry_percent": 0.29,
                        "controlled_entry_with_chance_percent": 0.31
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.53,
                        "retrievals_per_60": 2.31,
                        "successful_retrieval_percent": 0.55,
                        "exits_per_60": 0.14,
                        "botched_retrievals_per_60": -1.83
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "nate schmidt": {
        "name": "Nate\u00a0Schmidt",
        "team": "FLA",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 175.0,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.92,
                        "shot_assists_per_60": 0.44,
                        "total_shot_contributions_per_60": 1.36,
                        "chances_per_60": 0.88,
                        "chance_assists_per_60": 0.49
                },
                "passing": {
                        "high_danger_assists_per_60": 0.42
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.86,
                        "rush_offense_per_60": 0.58,
                        "shots_off_hd_passes_per_60": 0.88
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.22,
                        "controlled_entry_percent": 0.33,
                        "controlled_entry_with_chance_percent": 0.33
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.9,
                        "retrievals_per_60": 1.73,
                        "successful_retrieval_percent": 0.74,
                        "exits_per_60": 0.24,
                        "botched_retrievals_per_60": -3.22
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "matthew tkachuk": {
        "name": "Matthew\u00a0Tkachuk",
        "team": "LAK",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 169.3,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.7,
                        "shot_assists_per_60": 0.43,
                        "total_shot_contributions_per_60": 2.13,
                        "chances_per_60": 1.8,
                        "chance_assists_per_60": 0.53
                },
                "passing": {
                        "high_danger_assists_per_60": 0.48
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.74,
                        "rush_offense_per_60": 0.92,
                        "shots_off_hd_passes_per_60": 1.32
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.76,
                        "controlled_entry_percent": 0.56,
                        "controlled_entry_with_chance_percent": 0.16
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.48,
                        "retrievals_per_60": 2.45,
                        "successful_retrieval_percent": 0.67,
                        "exits_per_60": 0.23,
                        "botched_retrievals_per_60": -2.51
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "mackie samoskevich": {
        "name": "Mackie\u00a0Samoskevich",
        "team": "MIN",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 148.2,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.59,
                        "shot_assists_per_60": 0.82,
                        "total_shot_contributions_per_60": 1.41,
                        "chances_per_60": 0.59,
                        "chance_assists_per_60": 1.11
                },
                "passing": {
                        "high_danger_assists_per_60": 0.9
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.77,
                        "rush_offense_per_60": 0.41,
                        "shots_off_hd_passes_per_60": 0.53
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.65,
                        "controlled_entry_percent": 0.28,
                        "controlled_entry_with_chance_percent": 0.32
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.91,
                        "retrievals_per_60": 3.89,
                        "successful_retrieval_percent": 0.69,
                        "exits_per_60": 0.4,
                        "botched_retrievals_per_60": -2.73
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jesper boqvist": {
        "name": "Jesper\u00a0Boqvist",
        "team": "MTL",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 169.2,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.922,
                        "goals_against_average": 2.03,
                        "wins": 31,
                        "shutouts": 6
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "gustav forsling": {
        "name": "Gustav\u00a0Forsling",
        "team": "NSH",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 156.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.13,
                        "shot_assists_per_60": 1.05,
                        "total_shot_contributions_per_60": 2.18,
                        "chances_per_60": 0.99,
                        "chance_assists_per_60": 1.35
                },
                "passing": {
                        "high_danger_assists_per_60": 1.01
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.49,
                        "rush_offense_per_60": 0.8,
                        "shots_off_hd_passes_per_60": 0.96
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.49,
                        "controlled_entry_percent": 0.34,
                        "controlled_entry_with_chance_percent": 0.18
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.57,
                        "retrievals_per_60": 1.83,
                        "successful_retrieval_percent": 0.68,
                        "exits_per_60": 0.14,
                        "botched_retrievals_per_60": -2.97
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "evan rodrigues": {
        "name": "Evan\u00a0Rodrigues",
        "team": "NJD",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 101.3,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.53,
                        "shot_assists_per_60": 1.0,
                        "total_shot_contributions_per_60": 1.53,
                        "chances_per_60": 0.52,
                        "chance_assists_per_60": 1.39
                },
                "passing": {
                        "high_danger_assists_per_60": 0.94
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.7,
                        "rush_offense_per_60": 0.19,
                        "shots_off_hd_passes_per_60": 0.41
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.69,
                        "controlled_entry_percent": 0.56,
                        "controlled_entry_with_chance_percent": 0.2
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.58,
                        "retrievals_per_60": 2.8,
                        "successful_retrieval_percent": 0.67,
                        "exits_per_60": 0.2,
                        "botched_retrievals_per_60": -1.63
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "eetu luostarinen": {
        "name": "Eetu\u00a0Luostarinen",
        "team": "NYI",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 183.8,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.76,
                        "shot_assists_per_60": 0.69,
                        "total_shot_contributions_per_60": 2.45,
                        "chances_per_60": 1.71,
                        "chance_assists_per_60": 0.61
                },
                "passing": {
                        "high_danger_assists_per_60": 0.56
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.68,
                        "rush_offense_per_60": 1.28,
                        "shots_off_hd_passes_per_60": 1.6
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.74,
                        "controlled_entry_percent": 0.45,
                        "controlled_entry_with_chance_percent": 0.19
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.14,
                        "retrievals_per_60": 2.09,
                        "successful_retrieval_percent": 0.64,
                        "exits_per_60": 0.37,
                        "botched_retrievals_per_60": -1.88
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "dmitry kulikov": {
        "name": "Dmitry\u00a0Kulikov",
        "team": "NYR",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 100.1,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.3,
                        "shot_assists_per_60": 0.25,
                        "total_shot_contributions_per_60": 0.55,
                        "chances_per_60": 0.34,
                        "chance_assists_per_60": 0.3
                },
                "passing": {
                        "high_danger_assists_per_60": 0.23
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.41,
                        "rush_offense_per_60": 0.22,
                        "shots_off_hd_passes_per_60": 0.22
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.65,
                        "controlled_entry_percent": 0.64,
                        "controlled_entry_with_chance_percent": 0.18
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.77,
                        "retrievals_per_60": 4.06,
                        "successful_retrieval_percent": 0.56,
                        "exits_per_60": 0.38,
                        "botched_retrievals_per_60": -3.07
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "carter verhaeghe": {
        "name": "Carter\u00a0Verhaeghe",
        "team": "OTT",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 161.4,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.91,
                        "goals_against_average": 2.81,
                        "wins": 33,
                        "shutouts": 3
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "anton lundell": {
        "name": "Anton\u00a0Lundell",
        "team": "PHI",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 112.6,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.55,
                        "shot_assists_per_60": 0.9,
                        "total_shot_contributions_per_60": 1.45,
                        "chances_per_60": 0.57,
                        "chance_assists_per_60": 0.75
                },
                "passing": {
                        "high_danger_assists_per_60": 0.91
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.63,
                        "rush_offense_per_60": 0.3,
                        "shots_off_hd_passes_per_60": 0.48
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.38,
                        "controlled_entry_percent": 0.49,
                        "controlled_entry_with_chance_percent": 0.16
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.82,
                        "retrievals_per_60": 1.99,
                        "successful_retrieval_percent": 0.78,
                        "exits_per_60": 0.28,
                        "botched_retrievals_per_60": -3.84
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "aleksander barkov": {
        "name": "Aleksander\u00a0Barkov",
        "team": "PIT",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 168.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.34,
                        "shot_assists_per_60": 0.55,
                        "total_shot_contributions_per_60": 1.89,
                        "chances_per_60": 1.67,
                        "chance_assists_per_60": 0.51
                },
                "passing": {
                        "high_danger_assists_per_60": 0.52
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.38,
                        "rush_offense_per_60": 0.65,
                        "shots_off_hd_passes_per_60": 1.27
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.19,
                        "controlled_entry_percent": 0.33,
                        "controlled_entry_with_chance_percent": 0.25
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.06,
                        "retrievals_per_60": 2.86,
                        "successful_retrieval_percent": 0.66,
                        "exits_per_60": 0.29,
                        "botched_retrievals_per_60": -2.23
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "aaron ekblad": {
        "name": "Aaron\u00a0Ekblad",
        "team": "SJS",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 134.8,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.32,
                        "shot_assists_per_60": 0.89,
                        "total_shot_contributions_per_60": 2.21,
                        "chances_per_60": 0.97,
                        "chance_assists_per_60": 1.06
                },
                "passing": {
                        "high_danger_assists_per_60": 0.94
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.21,
                        "rush_offense_per_60": 0.71,
                        "shots_off_hd_passes_per_60": 1.43
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.23,
                        "controlled_entry_percent": 0.39,
                        "controlled_entry_with_chance_percent": 0.21
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.23,
                        "retrievals_per_60": 2.27,
                        "successful_retrieval_percent": 0.82,
                        "exits_per_60": 0.12,
                        "botched_retrievals_per_60": -3.18
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "aj greer": {
        "name": "A.J.\u00a0Greer",
        "team": "SEA",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 196.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.54,
                        "shot_assists_per_60": 0.79,
                        "total_shot_contributions_per_60": 1.33,
                        "chances_per_60": 0.66,
                        "chance_assists_per_60": 0.96
                },
                "passing": {
                        "high_danger_assists_per_60": 0.75
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.63,
                        "rush_offense_per_60": 0.41,
                        "shots_off_hd_passes_per_60": 0.44
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.67,
                        "controlled_entry_percent": 0.41,
                        "controlled_entry_with_chance_percent": 0.34
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.66,
                        "retrievals_per_60": 3.18,
                        "successful_retrieval_percent": 0.66,
                        "exits_per_60": 0.18,
                        "botched_retrievals_per_60": -3.83
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "zach hyman": {
        "name": "Zach\u00a0Hyman",
        "team": "STL",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 145.7,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.918,
                        "goals_against_average": 2.75,
                        "wins": 19,
                        "shutouts": 5
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "vasily podkolzin": {
        "name": "Vasily\u00a0Podkolzin",
        "team": "TBL",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 196.6,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.09,
                        "shot_assists_per_60": 1.18,
                        "total_shot_contributions_per_60": 2.27,
                        "chances_per_60": 1.31,
                        "chance_assists_per_60": 1.12
                },
                "passing": {
                        "high_danger_assists_per_60": 1.0
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.45,
                        "rush_offense_per_60": 0.86,
                        "shots_off_hd_passes_per_60": 0.93
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.39,
                        "controlled_entry_percent": 0.34,
                        "controlled_entry_with_chance_percent": 0.15
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.09,
                        "retrievals_per_60": 2.12,
                        "successful_retrieval_percent": 0.58,
                        "exits_per_60": 0.3,
                        "botched_retrievals_per_60": -2.1
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "ty emberson": {
        "name": "Ty\u00a0Emberson",
        "team": "TOR",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 121.7,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.95,
                        "shot_assists_per_60": 0.63,
                        "total_shot_contributions_per_60": 1.58,
                        "chances_per_60": 1.04,
                        "chance_assists_per_60": 0.6
                },
                "passing": {
                        "high_danger_assists_per_60": 0.59
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.23,
                        "rush_offense_per_60": 0.48,
                        "shots_off_hd_passes_per_60": 0.74
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.38,
                        "controlled_entry_percent": 0.59,
                        "controlled_entry_with_chance_percent": 0.32
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.8,
                        "retrievals_per_60": 2.47,
                        "successful_retrieval_percent": 0.7,
                        "exits_per_60": 0.26,
                        "botched_retrievals_per_60": -2.53
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "troy stecher": {
        "name": "Troy\u00a0Stecher",
        "team": "VAN",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 112.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.4,
                        "shot_assists_per_60": 0.4,
                        "total_shot_contributions_per_60": 1.8,
                        "chances_per_60": 1.43,
                        "chance_assists_per_60": 0.49
                },
                "passing": {
                        "high_danger_assists_per_60": 0.43
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.94,
                        "rush_offense_per_60": 0.62,
                        "shots_off_hd_passes_per_60": 1.2
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.05,
                        "controlled_entry_percent": 0.42,
                        "controlled_entry_with_chance_percent": 0.28
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.41,
                        "retrievals_per_60": 2.89,
                        "successful_retrieval_percent": 0.59,
                        "exits_per_60": 0.34,
                        "botched_retrievals_per_60": -1.84
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "ryan nugent_hopkins": {
        "name": "Ryan\u00a0Nugent-Hopkins",
        "team": "VGK",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 184.7,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.25,
                        "shot_assists_per_60": 0.69,
                        "total_shot_contributions_per_60": 0.94,
                        "chances_per_60": 0.25,
                        "chance_assists_per_60": 0.84
                },
                "passing": {
                        "high_danger_assists_per_60": 0.78
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.34,
                        "rush_offense_per_60": 0.11,
                        "shots_off_hd_passes_per_60": 0.2
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.64,
                        "controlled_entry_percent": 0.55,
                        "controlled_entry_with_chance_percent": 0.23
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.95,
                        "retrievals_per_60": 3.44,
                        "successful_retrieval_percent": 0.63,
                        "exits_per_60": 0.16,
                        "botched_retrievals_per_60": -3.56
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "mattias janmark": {
        "name": "Mattias\u00a0Janmark",
        "team": "WSH",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 115.5,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.913,
                        "goals_against_average": 3.11,
                        "wins": 41,
                        "shutouts": 0
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "mattias ekholm": {
        "name": "Mattias\u00a0Ekholm",
        "team": "WPG",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 146.6,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.71,
                        "shot_assists_per_60": 0.67,
                        "total_shot_contributions_per_60": 1.38,
                        "chances_per_60": 0.83,
                        "chance_assists_per_60": 0.84
                },
                "passing": {
                        "high_danger_assists_per_60": 0.62
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.73,
                        "rush_offense_per_60": 0.51,
                        "shots_off_hd_passes_per_60": 0.56
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.23,
                        "controlled_entry_percent": 0.48,
                        "controlled_entry_with_chance_percent": 0.26
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.78,
                        "retrievals_per_60": 2.02,
                        "successful_retrieval_percent": 0.72,
                        "exits_per_60": 0.38,
                        "botched_retrievals_per_60": -2.11
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "leon draisaitl": {
        "name": "Leon\u00a0Draisaitl",
        "team": "ANA",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 199.6,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.87,
                        "shot_assists_per_60": 0.45,
                        "total_shot_contributions_per_60": 1.32,
                        "chances_per_60": 0.64,
                        "chance_assists_per_60": 0.6
                },
                "passing": {
                        "high_danger_assists_per_60": 0.46
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.98,
                        "rush_offense_per_60": 0.67,
                        "shots_off_hd_passes_per_60": 0.72
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.75,
                        "controlled_entry_percent": 0.38,
                        "controlled_entry_with_chance_percent": 0.17
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.18,
                        "retrievals_per_60": 2.24,
                        "successful_retrieval_percent": 0.84,
                        "exits_per_60": 0.36,
                        "botched_retrievals_per_60": -2.59
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "kasperi kapanen": {
        "name": "Kasperi\u00a0Kapanen",
        "team": "ARI",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 190.0,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.7,
                        "shot_assists_per_60": 0.78,
                        "total_shot_contributions_per_60": 1.48,
                        "chances_per_60": 0.55,
                        "chance_assists_per_60": 0.93
                },
                "passing": {
                        "high_danger_assists_per_60": 0.75
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.92,
                        "rush_offense_per_60": 0.41,
                        "shots_off_hd_passes_per_60": 0.76
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.7,
                        "controlled_entry_percent": 0.25,
                        "controlled_entry_with_chance_percent": 0.16
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.91,
                        "retrievals_per_60": 1.76,
                        "successful_retrieval_percent": 0.82,
                        "exits_per_60": 0.23,
                        "botched_retrievals_per_60": -2.72
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jeff skinner": {
        "name": "Jeff\u00a0Skinner",
        "team": "BOS",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 190.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.14,
                        "shot_assists_per_60": 0.62,
                        "total_shot_contributions_per_60": 0.76,
                        "chances_per_60": 0.15,
                        "chance_assists_per_60": 0.73
                },
                "passing": {
                        "high_danger_assists_per_60": 0.72
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.15,
                        "rush_offense_per_60": 0.09,
                        "shots_off_hd_passes_per_60": 0.15
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.58,
                        "controlled_entry_percent": 0.33,
                        "controlled_entry_with_chance_percent": 0.16
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 4.13,
                        "retrievals_per_60": 4.14,
                        "successful_retrieval_percent": 0.72,
                        "exits_per_60": 0.28,
                        "botched_retrievals_per_60": -2.41
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "evan bouchard": {
        "name": "Evan\u00a0Bouchard",
        "team": "BUF",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 189.6,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.918,
                        "goals_against_average": 3.21,
                        "wins": 33,
                        "shutouts": 6
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "derek ryan": {
        "name": "Derek\u00a0Ryan",
        "team": "CGY",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 112.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.04,
                        "shot_assists_per_60": 0.47,
                        "total_shot_contributions_per_60": 1.51,
                        "chances_per_60": 0.93,
                        "chance_assists_per_60": 0.59
                },
                "passing": {
                        "high_danger_assists_per_60": 0.49
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.98,
                        "rush_offense_per_60": 0.67,
                        "shots_off_hd_passes_per_60": 0.87
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.28,
                        "controlled_entry_percent": 0.34,
                        "controlled_entry_with_chance_percent": 0.31
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.25,
                        "retrievals_per_60": 2.21,
                        "successful_retrieval_percent": 0.64,
                        "exits_per_60": 0.3,
                        "botched_retrievals_per_60": -3.6
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "darnell nurse": {
        "name": "Darnell\u00a0Nurse",
        "team": "CAR",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 177.6,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.2,
                        "shot_assists_per_60": 0.97,
                        "total_shot_contributions_per_60": 2.17,
                        "chances_per_60": 0.87,
                        "chance_assists_per_60": 1.22
                },
                "passing": {
                        "high_danger_assists_per_60": 0.99
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.57,
                        "rush_offense_per_60": 0.81,
                        "shots_off_hd_passes_per_60": 0.89
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.55,
                        "controlled_entry_percent": 0.45,
                        "controlled_entry_with_chance_percent": 0.16
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.65,
                        "retrievals_per_60": 1.58,
                        "successful_retrieval_percent": 0.75,
                        "exits_per_60": 0.14,
                        "botched_retrievals_per_60": -2.68
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "corey perry": {
        "name": "Corey\u00a0Perry",
        "team": "CHI",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 128.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.72,
                        "shot_assists_per_60": 1.15,
                        "total_shot_contributions_per_60": 1.87,
                        "chances_per_60": 0.91,
                        "chance_assists_per_60": 1.47
                },
                "passing": {
                        "high_danger_assists_per_60": 1.12
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.72,
                        "rush_offense_per_60": 0.23,
                        "shots_off_hd_passes_per_60": 0.68
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.11,
                        "controlled_entry_percent": 0.6,
                        "controlled_entry_with_chance_percent": 0.15
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.92,
                        "retrievals_per_60": 2.18,
                        "successful_retrieval_percent": 0.65,
                        "exits_per_60": 0.29,
                        "botched_retrievals_per_60": -3.95
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "connor mcdavid": {
        "name": "Connor\u00a0McDavid",
        "team": "COL",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 186.3,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.16,
                        "shot_assists_per_60": 0.49,
                        "total_shot_contributions_per_60": 0.65,
                        "chances_per_60": 0.2,
                        "chance_assists_per_60": 0.46
                },
                "passing": {
                        "high_danger_assists_per_60": 0.59
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.21,
                        "rush_offense_per_60": 0.12,
                        "shots_off_hd_passes_per_60": 0.11
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.51,
                        "controlled_entry_percent": 0.26,
                        "controlled_entry_with_chance_percent": 0.24
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.21,
                        "retrievals_per_60": 2.9,
                        "successful_retrieval_percent": 0.84,
                        "exits_per_60": 0.33,
                        "botched_retrievals_per_60": -2.77
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "connor brown": {
        "name": "Connor\u00a0Brown",
        "team": "CBJ",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 144.2,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.925,
                        "goals_against_average": 3.11,
                        "wins": 29,
                        "shutouts": 4
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "brett kulak": {
        "name": "Brett\u00a0Kulak",
        "team": "DAL",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 103.8,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.79,
                        "shot_assists_per_60": 0.5,
                        "total_shot_contributions_per_60": 2.29,
                        "chances_per_60": 1.73,
                        "chance_assists_per_60": 0.57
                },
                "passing": {
                        "high_danger_assists_per_60": 0.44
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 2.42,
                        "rush_offense_per_60": 0.62,
                        "shots_off_hd_passes_per_60": 1.76
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.08,
                        "controlled_entry_percent": 0.5,
                        "controlled_entry_with_chance_percent": 0.2
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.34,
                        "retrievals_per_60": 2.45,
                        "successful_retrieval_percent": 0.66,
                        "exits_per_60": 0.14,
                        "botched_retrievals_per_60": -1.93
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "adam henrique": {
        "name": "Adam\u00a0Henrique",
        "team": "DET",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 161.3,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.39,
                        "shot_assists_per_60": 0.86,
                        "total_shot_contributions_per_60": 2.25,
                        "chances_per_60": 1.19,
                        "chance_assists_per_60": 0.82
                },
                "passing": {
                        "high_danger_assists_per_60": 0.87
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.17,
                        "rush_offense_per_60": 0.8,
                        "shots_off_hd_passes_per_60": 1.01
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.74,
                        "controlled_entry_percent": 0.3,
                        "controlled_entry_with_chance_percent": 0.3
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.64,
                        "retrievals_per_60": 1.68,
                        "successful_retrieval_percent": 0.8,
                        "exits_per_60": 0.21,
                        "botched_retrievals_per_60": -2.37
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "vladimir tarasenko": {
        "name": "Vladimir\u00a0Tarasenko",
        "team": "EDM",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 150.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.97,
                        "shot_assists_per_60": 1.03,
                        "total_shot_contributions_per_60": 2.0,
                        "chances_per_60": 1.12,
                        "chance_assists_per_60": 1.38
                },
                "passing": {
                        "high_danger_assists_per_60": 1.16
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.01,
                        "rush_offense_per_60": 0.56,
                        "shots_off_hd_passes_per_60": 0.93
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.62,
                        "controlled_entry_percent": 0.37,
                        "controlled_entry_with_chance_percent": 0.19
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.12,
                        "retrievals_per_60": 2.22,
                        "successful_retrieval_percent": 0.56,
                        "exits_per_60": 0.28,
                        "botched_retrievals_per_60": -2.25
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "tyler motte": {
        "name": "Tyler\u00a0Motte",
        "team": "FLA",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 125.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.41,
                        "shot_assists_per_60": 0.26,
                        "total_shot_contributions_per_60": 0.67,
                        "chances_per_60": 0.44,
                        "chance_assists_per_60": 0.24
                },
                "passing": {
                        "high_danger_assists_per_60": 0.29
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.43,
                        "rush_offense_per_60": 0.32,
                        "shots_off_hd_passes_per_60": 0.44
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.59,
                        "controlled_entry_percent": 0.42,
                        "controlled_entry_with_chance_percent": 0.32
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.8,
                        "retrievals_per_60": 3.97,
                        "successful_retrieval_percent": 0.79,
                        "exits_per_60": 0.32,
                        "botched_retrievals_per_60": -2.75
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "simon edvinsson": {
        "name": "Simon\u00a0Edvinsson",
        "team": "LAK",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 197.3,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.928,
                        "goals_against_average": 3.4,
                        "wins": 39,
                        "shutouts": 4
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "patrick kane": {
        "name": "Patrick\u00a0Kane",
        "team": "MIN",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 188.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.68,
                        "shot_assists_per_60": 1.03,
                        "total_shot_contributions_per_60": 1.71,
                        "chances_per_60": 0.77,
                        "chance_assists_per_60": 0.94
                },
                "passing": {
                        "high_danger_assists_per_60": 0.9
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.84,
                        "rush_offense_per_60": 0.53,
                        "shots_off_hd_passes_per_60": 0.53
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.46,
                        "controlled_entry_percent": 0.59,
                        "controlled_entry_with_chance_percent": 0.32
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.18,
                        "retrievals_per_60": 2.63,
                        "successful_retrieval_percent": 0.75,
                        "exits_per_60": 0.39,
                        "botched_retrievals_per_60": -2.56
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "moritz seider": {
        "name": "Moritz\u00a0Seider",
        "team": "MTL",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 169.2,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.21,
                        "shot_assists_per_60": 0.56,
                        "total_shot_contributions_per_60": 1.77,
                        "chances_per_60": 1.2,
                        "chance_assists_per_60": 0.64
                },
                "passing": {
                        "high_danger_assists_per_60": 0.63
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.19,
                        "rush_offense_per_60": 0.45,
                        "shots_off_hd_passes_per_60": 1.04
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.37,
                        "controlled_entry_percent": 0.58,
                        "controlled_entry_with_chance_percent": 0.26
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.17,
                        "retrievals_per_60": 2.14,
                        "successful_retrieval_percent": 0.59,
                        "exits_per_60": 0.36,
                        "botched_retrievals_per_60": -1.62
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "michael rasmussen": {
        "name": "Michael\u00a0Rasmussen",
        "team": "NSH",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 115.1,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.7,
                        "shot_assists_per_60": 1.15,
                        "total_shot_contributions_per_60": 1.85,
                        "chances_per_60": 0.55,
                        "chance_assists_per_60": 1.47
                },
                "passing": {
                        "high_danger_assists_per_60": 1.1
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.58,
                        "rush_offense_per_60": 0.31,
                        "shots_off_hd_passes_per_60": 0.7
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.91,
                        "controlled_entry_percent": 0.36,
                        "controlled_entry_with_chance_percent": 0.33
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.44,
                        "retrievals_per_60": 2.96,
                        "successful_retrieval_percent": 0.81,
                        "exits_per_60": 0.15,
                        "botched_retrievals_per_60": -2.6
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "marco kasper": {
        "name": "Marco\u00a0Kasper",
        "team": "NJD",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 133.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.49,
                        "shot_assists_per_60": 0.78,
                        "total_shot_contributions_per_60": 1.27,
                        "chances_per_60": 0.61,
                        "chance_assists_per_60": 0.75
                },
                "passing": {
                        "high_danger_assists_per_60": 0.72
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.61,
                        "rush_offense_per_60": 0.21,
                        "shots_off_hd_passes_per_60": 0.49
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.43,
                        "controlled_entry_percent": 0.51,
                        "controlled_entry_with_chance_percent": 0.18
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 4.13,
                        "retrievals_per_60": 3.98,
                        "successful_retrieval_percent": 0.78,
                        "exits_per_60": 0.39,
                        "botched_retrievals_per_60": -1.5
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "lucas raymond": {
        "name": "Lucas\u00a0Raymond",
        "team": "NYI",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 138.5,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.907,
                        "goals_against_average": 2.53,
                        "wins": 20,
                        "shutouts": 1
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "justin holl": {
        "name": "Justin\u00a0Holl",
        "team": "NYR",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 133.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.0,
                        "shot_assists_per_60": 0.55,
                        "total_shot_contributions_per_60": 1.55,
                        "chances_per_60": 1.25,
                        "chance_assists_per_60": 0.75
                },
                "passing": {
                        "high_danger_assists_per_60": 0.56
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.36,
                        "rush_offense_per_60": 0.68,
                        "shots_off_hd_passes_per_60": 0.92
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.23,
                        "controlled_entry_percent": 0.32,
                        "controlled_entry_with_chance_percent": 0.16
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.85,
                        "retrievals_per_60": 2.29,
                        "successful_retrieval_percent": 0.72,
                        "exits_per_60": 0.29,
                        "botched_retrievals_per_60": -1.84
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jonatan berggren": {
        "name": "Jonatan\u00a0Berggren",
        "team": "OTT",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 117.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.08,
                        "shot_assists_per_60": 0.48,
                        "total_shot_contributions_per_60": 1.56,
                        "chances_per_60": 1.0,
                        "chance_assists_per_60": 0.65
                },
                "passing": {
                        "high_danger_assists_per_60": 0.46
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.25,
                        "rush_offense_per_60": 0.66,
                        "shots_off_hd_passes_per_60": 0.78
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.45,
                        "controlled_entry_percent": 0.61,
                        "controlled_entry_with_chance_percent": 0.24
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.51,
                        "retrievals_per_60": 2.52,
                        "successful_retrieval_percent": 0.8,
                        "exits_per_60": 0.2,
                        "botched_retrievals_per_60": -1.6
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "joe veleno": {
        "name": "Joe\u00a0Veleno",
        "team": "PHI",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 185.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.71,
                        "shot_assists_per_60": 1.06,
                        "total_shot_contributions_per_60": 2.77,
                        "chances_per_60": 1.62,
                        "chance_assists_per_60": 1.21
                },
                "passing": {
                        "high_danger_assists_per_60": 1.03
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.94,
                        "rush_offense_per_60": 1.08,
                        "shots_off_hd_passes_per_60": 1.32
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.28,
                        "controlled_entry_percent": 0.37,
                        "controlled_entry_with_chance_percent": 0.33
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.05,
                        "retrievals_per_60": 2.62,
                        "successful_retrieval_percent": 0.72,
                        "exits_per_60": 0.4,
                        "botched_retrievals_per_60": -3.72
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jeff petry": {
        "name": "Jeff\u00a0Petry",
        "team": "PIT",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 150.0,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.35,
                        "shot_assists_per_60": 0.74,
                        "total_shot_contributions_per_60": 1.09,
                        "chances_per_60": 0.28,
                        "chance_assists_per_60": 0.97
                },
                "passing": {
                        "high_danger_assists_per_60": 0.61
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.41,
                        "rush_offense_per_60": 0.26,
                        "shots_off_hd_passes_per_60": 0.29
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.38,
                        "controlled_entry_percent": 0.42,
                        "controlled_entry_with_chance_percent": 0.23
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.94,
                        "retrievals_per_60": 2.84,
                        "successful_retrieval_percent": 0.64,
                        "exits_per_60": 0.17,
                        "botched_retrievals_per_60": -1.8
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jt compher": {
        "name": "J.T.\u00a0Compher",
        "team": "SJS",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 167.8,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.915,
                        "goals_against_average": 2.76,
                        "wins": 37,
                        "shutouts": 2
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "erik gustafsson": {
        "name": "Erik\u00a0Gustafsson",
        "team": "SEA",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 105.2,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.63,
                        "shot_assists_per_60": 0.52,
                        "total_shot_contributions_per_60": 2.15,
                        "chances_per_60": 1.89,
                        "chance_assists_per_60": 0.57
                },
                "passing": {
                        "high_danger_assists_per_60": 0.42
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 2.25,
                        "rush_offense_per_60": 0.54,
                        "shots_off_hd_passes_per_60": 1.28
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.77,
                        "controlled_entry_percent": 0.63,
                        "controlled_entry_with_chance_percent": 0.19
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.16,
                        "retrievals_per_60": 2.34,
                        "successful_retrieval_percent": 0.67,
                        "exits_per_60": 0.2,
                        "botched_retrievals_per_60": -1.86
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "dylan larkin": {
        "name": "Dylan\u00a0Larkin",
        "team": "STL",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 166.2,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.96,
                        "shot_assists_per_60": 0.58,
                        "total_shot_contributions_per_60": 1.54,
                        "chances_per_60": 0.82,
                        "chance_assists_per_60": 0.48
                },
                "passing": {
                        "high_danger_assists_per_60": 0.57
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.32,
                        "rush_offense_per_60": 0.53,
                        "shots_off_hd_passes_per_60": 0.94
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.55,
                        "controlled_entry_percent": 0.29,
                        "controlled_entry_with_chance_percent": 0.18
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.1,
                        "retrievals_per_60": 2.53,
                        "successful_retrieval_percent": 0.72,
                        "exits_per_60": 0.35,
                        "botched_retrievals_per_60": -1.7
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "christian fischer": {
        "name": "Christian\u00a0Fischer",
        "team": "TBL",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 125.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.83,
                        "shot_assists_per_60": 0.69,
                        "total_shot_contributions_per_60": 1.52,
                        "chances_per_60": 0.95,
                        "chance_assists_per_60": 0.62
                },
                "passing": {
                        "high_danger_assists_per_60": 0.68
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.13,
                        "rush_offense_per_60": 0.43,
                        "shots_off_hd_passes_per_60": 0.77
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.12,
                        "controlled_entry_percent": 0.28,
                        "controlled_entry_with_chance_percent": 0.23
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.86,
                        "retrievals_per_60": 1.79,
                        "successful_retrieval_percent": 0.66,
                        "exits_per_60": 0.2,
                        "botched_retrievals_per_60": -1.63
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "ben chiarot": {
        "name": "Ben\u00a0Chiarot",
        "team": "TOR",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 167.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.45,
                        "shot_assists_per_60": 0.45,
                        "total_shot_contributions_per_60": 0.9,
                        "chances_per_60": 0.32,
                        "chance_assists_per_60": 0.62
                },
                "passing": {
                        "high_danger_assists_per_60": 0.53
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.54,
                        "rush_offense_per_60": 0.35,
                        "shots_off_hd_passes_per_60": 0.46
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.4,
                        "controlled_entry_percent": 0.44,
                        "controlled_entry_with_chance_percent": 0.25
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.59,
                        "retrievals_per_60": 3.14,
                        "successful_retrieval_percent": 0.59,
                        "exits_per_60": 0.37,
                        "botched_retrievals_per_60": -2.3
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "andrew copp": {
        "name": "Andrew\u00a0Copp",
        "team": "VAN",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 125.8,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.928,
                        "goals_against_average": 3.47,
                        "wins": 18,
                        "shutouts": 7
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "alex debrincat": {
        "name": "Alex\u00a0DeBrincat",
        "team": "VGK",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 186.0,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.21,
                        "shot_assists_per_60": 0.63,
                        "total_shot_contributions_per_60": 1.84,
                        "chances_per_60": 1.48,
                        "chance_assists_per_60": 0.86
                },
                "passing": {
                        "high_danger_assists_per_60": 0.61
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.23,
                        "rush_offense_per_60": 0.81,
                        "shots_off_hd_passes_per_60": 1.12
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.21,
                        "controlled_entry_percent": 0.65,
                        "controlled_entry_with_chance_percent": 0.28
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.27,
                        "retrievals_per_60": 2.22,
                        "successful_retrieval_percent": 0.62,
                        "exits_per_60": 0.2,
                        "botched_retrievals_per_60": -2.28
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "albert johansson": {
        "name": "Albert\u00a0Johansson",
        "team": "WSH",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 155.6,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.4,
                        "shot_assists_per_60": 0.73,
                        "total_shot_contributions_per_60": 2.13,
                        "chances_per_60": 1.68,
                        "chance_assists_per_60": 0.74
                },
                "passing": {
                        "high_danger_assists_per_60": 0.64
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.44,
                        "rush_offense_per_60": 0.7,
                        "shots_off_hd_passes_per_60": 1.32
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.03,
                        "controlled_entry_percent": 0.58,
                        "controlled_entry_with_chance_percent": 0.3
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.1,
                        "retrievals_per_60": 2.69,
                        "successful_retrieval_percent": 0.69,
                        "exits_per_60": 0.4,
                        "botched_retrievals_per_60": -2.87
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "wyatt johnston": {
        "name": "Wyatt\u00a0Johnston",
        "team": "WPG",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 105.1,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.39,
                        "shot_assists_per_60": 0.72,
                        "total_shot_contributions_per_60": 2.11,
                        "chances_per_60": 1.32,
                        "chance_assists_per_60": 0.88
                },
                "passing": {
                        "high_danger_assists_per_60": 0.6
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.94,
                        "rush_offense_per_60": 0.86,
                        "shots_off_hd_passes_per_60": 1.27
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.78,
                        "controlled_entry_percent": 0.41,
                        "controlled_entry_with_chance_percent": 0.23
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.87,
                        "retrievals_per_60": 2.98,
                        "successful_retrieval_percent": 0.74,
                        "exits_per_60": 0.22,
                        "botched_retrievals_per_60": -2.44
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "tyler seguin": {
        "name": "Tyler\u00a0Seguin",
        "team": "ANA",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 168.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.75,
                        "shot_assists_per_60": 0.75,
                        "total_shot_contributions_per_60": 1.5,
                        "chances_per_60": 0.76,
                        "chance_assists_per_60": 1.01
                },
                "passing": {
                        "high_danger_assists_per_60": 0.67
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.66,
                        "rush_offense_per_60": 0.46,
                        "shots_off_hd_passes_per_60": 0.71
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.7,
                        "controlled_entry_percent": 0.36,
                        "controlled_entry_with_chance_percent": 0.22
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.06,
                        "retrievals_per_60": 3.79,
                        "successful_retrieval_percent": 0.59,
                        "exits_per_60": 0.26,
                        "botched_retrievals_per_60": -3.38
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "thomas harley": {
        "name": "Thomas\u00a0Harley",
        "team": "ARI",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 158.8,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.902,
                        "goals_against_average": 2.05,
                        "wins": 24,
                        "shutouts": 3
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "sam steel": {
        "name": "Sam\u00a0Steel",
        "team": "BOS",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 186.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.02,
                        "shot_assists_per_60": 0.6,
                        "total_shot_contributions_per_60": 1.62,
                        "chances_per_60": 0.76,
                        "chance_assists_per_60": 0.81
                },
                "passing": {
                        "high_danger_assists_per_60": 0.49
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.35,
                        "rush_offense_per_60": 0.57,
                        "shots_off_hd_passes_per_60": 0.98
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.09,
                        "controlled_entry_percent": 0.42,
                        "controlled_entry_with_chance_percent": 0.2
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.06,
                        "retrievals_per_60": 2.92,
                        "successful_retrieval_percent": 0.61,
                        "exits_per_60": 0.12,
                        "botched_retrievals_per_60": -3.0
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "roope hintz": {
        "name": "Roope\u00a0Hintz",
        "team": "BUF",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 132.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.21,
                        "shot_assists_per_60": 0.89,
                        "total_shot_contributions_per_60": 2.1,
                        "chances_per_60": 0.89,
                        "chance_assists_per_60": 0.79
                },
                "passing": {
                        "high_danger_assists_per_60": 1.01
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.1,
                        "rush_offense_per_60": 0.37,
                        "shots_off_hd_passes_per_60": 0.95
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.7,
                        "controlled_entry_percent": 0.5,
                        "controlled_entry_with_chance_percent": 0.2
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.94,
                        "retrievals_per_60": 2.92,
                        "successful_retrieval_percent": 0.56,
                        "exits_per_60": 0.25,
                        "botched_retrievals_per_60": -2.46
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "oskar bäck": {
        "name": "Oskar\u00a0B\u00e4ck",
        "team": "CGY",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 147.0,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.33,
                        "shot_assists_per_60": 0.65,
                        "total_shot_contributions_per_60": 1.98,
                        "chances_per_60": 1.54,
                        "chance_assists_per_60": 0.82
                },
                "passing": {
                        "high_danger_assists_per_60": 0.71
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.1,
                        "rush_offense_per_60": 0.89,
                        "shots_off_hd_passes_per_60": 1.0
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.44,
                        "controlled_entry_percent": 0.62,
                        "controlled_entry_with_chance_percent": 0.34
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.07,
                        "retrievals_per_60": 1.97,
                        "successful_retrieval_percent": 0.55,
                        "exits_per_60": 0.22,
                        "botched_retrievals_per_60": -2.06
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "nils lundkvist": {
        "name": "Nils\u00a0Lundkvist",
        "team": "CAR",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 195.7,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.51,
                        "shot_assists_per_60": 0.49,
                        "total_shot_contributions_per_60": 1.0,
                        "chances_per_60": 0.57,
                        "chance_assists_per_60": 0.45
                },
                "passing": {
                        "high_danger_assists_per_60": 0.41
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.55,
                        "rush_offense_per_60": 0.38,
                        "shots_off_hd_passes_per_60": 0.4
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.65,
                        "controlled_entry_percent": 0.55,
                        "controlled_entry_with_chance_percent": 0.29
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.44,
                        "retrievals_per_60": 4.19,
                        "successful_retrieval_percent": 0.7,
                        "exits_per_60": 0.21,
                        "botched_retrievals_per_60": -3.39
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "miro heiskanen": {
        "name": "Miro\u00a0Heiskanen",
        "team": "CHI",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 149.7,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.905,
                        "goals_against_average": 3.2,
                        "wins": 28,
                        "shutouts": 7
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "mikko rantanen": {
        "name": "Mikko\u00a0Rantanen",
        "team": "COL",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 126.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.64,
                        "shot_assists_per_60": 0.66,
                        "total_shot_contributions_per_60": 1.3,
                        "chances_per_60": 0.49,
                        "chance_assists_per_60": 0.63
                },
                "passing": {
                        "high_danger_assists_per_60": 0.73
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.72,
                        "rush_offense_per_60": 0.36,
                        "shots_off_hd_passes_per_60": 0.64
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.23,
                        "controlled_entry_percent": 0.46,
                        "controlled_entry_with_chance_percent": 0.29
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.1,
                        "retrievals_per_60": 2.77,
                        "successful_retrieval_percent": 0.61,
                        "exits_per_60": 0.19,
                        "botched_retrievals_per_60": -3.55
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "mavrik bourque": {
        "name": "Mavrik\u00a0Bourque",
        "team": "CBJ",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 101.6,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.06,
                        "shot_assists_per_60": 1.07,
                        "total_shot_contributions_per_60": 2.13,
                        "chances_per_60": 0.76,
                        "chance_assists_per_60": 1.16
                },
                "passing": {
                        "high_danger_assists_per_60": 0.94
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.13,
                        "rush_offense_per_60": 0.57,
                        "shots_off_hd_passes_per_60": 1.01
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.31,
                        "controlled_entry_percent": 0.28,
                        "controlled_entry_with_chance_percent": 0.29
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.89,
                        "retrievals_per_60": 1.91,
                        "successful_retrieval_percent": 0.75,
                        "exits_per_60": 0.28,
                        "botched_retrievals_per_60": -3.52
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "matt duchene": {
        "name": "Matt\u00a0Duchene",
        "team": "DAL",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 163.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.85,
                        "shot_assists_per_60": 0.94,
                        "total_shot_contributions_per_60": 1.79,
                        "chances_per_60": 0.78,
                        "chance_assists_per_60": 0.82
                },
                "passing": {
                        "high_danger_assists_per_60": 1.04
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.79,
                        "rush_offense_per_60": 0.61,
                        "shots_off_hd_passes_per_60": 0.9
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.43,
                        "controlled_entry_percent": 0.53,
                        "controlled_entry_with_chance_percent": 0.33
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.26,
                        "retrievals_per_60": 1.53,
                        "successful_retrieval_percent": 0.7,
                        "exits_per_60": 0.17,
                        "botched_retrievals_per_60": -3.99
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "mathew dumba": {
        "name": "Mathew\u00a0Dumba",
        "team": "DET",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 113.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.2,
                        "shot_assists_per_60": 0.88,
                        "total_shot_contributions_per_60": 1.08,
                        "chances_per_60": 0.14,
                        "chance_assists_per_60": 1.14
                },
                "passing": {
                        "high_danger_assists_per_60": 0.95
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.27,
                        "rush_offense_per_60": 0.15,
                        "shots_off_hd_passes_per_60": 0.15
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.32,
                        "controlled_entry_percent": 0.59,
                        "controlled_entry_with_chance_percent": 0.32
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.68,
                        "retrievals_per_60": 3.64,
                        "successful_retrieval_percent": 0.59,
                        "exits_per_60": 0.17,
                        "botched_retrievals_per_60": -3.79
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "mason marchment": {
        "name": "Mason\u00a0Marchment",
        "team": "EDM",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 125.2,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.927,
                        "goals_against_average": 3.1,
                        "wins": 24,
                        "shutouts": 2
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "logan stankoven": {
        "name": "Logan\u00a0Stankoven",
        "team": "FLA",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 168.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.44,
                        "shot_assists_per_60": 1.0,
                        "total_shot_contributions_per_60": 2.44,
                        "chances_per_60": 1.4,
                        "chance_assists_per_60": 1.08
                },
                "passing": {
                        "high_danger_assists_per_60": 1.04
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.6,
                        "rush_offense_per_60": 0.74,
                        "shots_off_hd_passes_per_60": 1.43
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.32,
                        "controlled_entry_percent": 0.39,
                        "controlled_entry_with_chance_percent": 0.3
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.21,
                        "retrievals_per_60": 1.95,
                        "successful_retrieval_percent": 0.77,
                        "exits_per_60": 0.22,
                        "botched_retrievals_per_60": -1.57
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "lian bichsel": {
        "name": "Lian\u00a0Bichsel",
        "team": "LAK",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 166.0,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.58,
                        "shot_assists_per_60": 0.75,
                        "total_shot_contributions_per_60": 2.33,
                        "chances_per_60": 1.47,
                        "chance_assists_per_60": 0.84
                },
                "passing": {
                        "high_danger_assists_per_60": 0.61
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.88,
                        "rush_offense_per_60": 1.01,
                        "shots_off_hd_passes_per_60": 1.14
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.27,
                        "controlled_entry_percent": 0.6,
                        "controlled_entry_with_chance_percent": 0.17
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.66,
                        "retrievals_per_60": 2.0,
                        "successful_retrieval_percent": 0.61,
                        "exits_per_60": 0.24,
                        "botched_retrievals_per_60": -2.37
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jason robertson": {
        "name": "Jason\u00a0Robertson",
        "team": "MIN",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 124.8,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.69,
                        "shot_assists_per_60": 0.71,
                        "total_shot_contributions_per_60": 1.4,
                        "chances_per_60": 0.62,
                        "chance_assists_per_60": 0.59
                },
                "passing": {
                        "high_danger_assists_per_60": 0.58
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.58,
                        "rush_offense_per_60": 0.39,
                        "shots_off_hd_passes_per_60": 0.62
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.94,
                        "controlled_entry_percent": 0.35,
                        "controlled_entry_with_chance_percent": 0.26
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.98,
                        "retrievals_per_60": 2.07,
                        "successful_retrieval_percent": 0.72,
                        "exits_per_60": 0.13,
                        "botched_retrievals_per_60": -1.52
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jamie benn": {
        "name": "Jamie\u00a0Benn",
        "team": "MTL",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 181.8,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.26,
                        "shot_assists_per_60": 0.73,
                        "total_shot_contributions_per_60": 0.99,
                        "chances_per_60": 0.2,
                        "chance_assists_per_60": 0.67
                },
                "passing": {
                        "high_danger_assists_per_60": 0.71
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.24,
                        "rush_offense_per_60": 0.13,
                        "shots_off_hd_passes_per_60": 0.2
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.41,
                        "controlled_entry_percent": 0.63,
                        "controlled_entry_with_chance_percent": 0.16
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 4.37,
                        "retrievals_per_60": 3.93,
                        "successful_retrieval_percent": 0.72,
                        "exits_per_60": 0.27,
                        "botched_retrievals_per_60": -2.53
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "ilya lyubushkin": {
        "name": "Ilya\u00a0Lyubushkin",
        "team": "NSH",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 103.3,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.911,
                        "goals_against_average": 2.29,
                        "wins": 13,
                        "shutouts": 8
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "evgenii dadonov": {
        "name": "Evgenii\u00a0Dadonov",
        "team": "NJD",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 121.6,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.77,
                        "shot_assists_per_60": 0.93,
                        "total_shot_contributions_per_60": 1.7,
                        "chances_per_60": 0.59,
                        "chance_assists_per_60": 1.01
                },
                "passing": {
                        "high_danger_assists_per_60": 0.91
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.96,
                        "rush_offense_per_60": 0.38,
                        "shots_off_hd_passes_per_60": 0.55
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.79,
                        "controlled_entry_percent": 0.6,
                        "controlled_entry_with_chance_percent": 0.31
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.4,
                        "retrievals_per_60": 2.28,
                        "successful_retrieval_percent": 0.82,
                        "exits_per_60": 0.13,
                        "botched_retrievals_per_60": -2.86
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "esa lindell": {
        "name": "Esa\u00a0Lindell",
        "team": "NYI",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 156.1,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.8,
                        "shot_assists_per_60": 0.64,
                        "total_shot_contributions_per_60": 1.44,
                        "chances_per_60": 0.73,
                        "chance_assists_per_60": 0.67
                },
                "passing": {
                        "high_danger_assists_per_60": 0.61
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.08,
                        "rush_offense_per_60": 0.64,
                        "shots_off_hd_passes_per_60": 0.78
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.39,
                        "controlled_entry_percent": 0.26,
                        "controlled_entry_with_chance_percent": 0.32
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.29,
                        "retrievals_per_60": 1.95,
                        "successful_retrieval_percent": 0.77,
                        "exits_per_60": 0.29,
                        "botched_retrievals_per_60": -1.51
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "colin blackwell": {
        "name": "Colin\u00a0Blackwell",
        "team": "NYR",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 103.3,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.06,
                        "shot_assists_per_60": 0.84,
                        "total_shot_contributions_per_60": 1.9,
                        "chances_per_60": 0.75,
                        "chance_assists_per_60": 0.71
                },
                "passing": {
                        "high_danger_assists_per_60": 0.81
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.19,
                        "rush_offense_per_60": 0.54,
                        "shots_off_hd_passes_per_60": 0.97
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.93,
                        "controlled_entry_percent": 0.53,
                        "controlled_entry_with_chance_percent": 0.18
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.11,
                        "retrievals_per_60": 1.8,
                        "successful_retrieval_percent": 0.68,
                        "exits_per_60": 0.17,
                        "botched_retrievals_per_60": -2.05
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "valeri nichushkin": {
        "name": "Valeri\u00a0Nichushkin",
        "team": "OTT",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 198.6,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.79,
                        "shot_assists_per_60": 0.46,
                        "total_shot_contributions_per_60": 1.25,
                        "chances_per_60": 0.58,
                        "chance_assists_per_60": 0.54
                },
                "passing": {
                        "high_danger_assists_per_60": 0.54
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.89,
                        "rush_offense_per_60": 0.55,
                        "shots_off_hd_passes_per_60": 0.74
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.44,
                        "controlled_entry_percent": 0.35,
                        "controlled_entry_with_chance_percent": 0.24
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.33,
                        "retrievals_per_60": 2.82,
                        "successful_retrieval_percent": 0.66,
                        "exits_per_60": 0.12,
                        "botched_retrievals_per_60": -1.95
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "samuel girard": {
        "name": "Samuel\u00a0Girard",
        "team": "PHI",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 139.5,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.928,
                        "goals_against_average": 3.12,
                        "wins": 42,
                        "shutouts": 6
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "sam malinski": {
        "name": "Sam\u00a0Malinski",
        "team": "PIT",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 141.3,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.18,
                        "shot_assists_per_60": 0.5,
                        "total_shot_contributions_per_60": 1.68,
                        "chances_per_60": 1.41,
                        "chance_assists_per_60": 0.6
                },
                "passing": {
                        "high_danger_assists_per_60": 0.43
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.21,
                        "rush_offense_per_60": 0.49,
                        "shots_off_hd_passes_per_60": 1.15
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.86,
                        "controlled_entry_percent": 0.58,
                        "controlled_entry_with_chance_percent": 0.16
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.9,
                        "retrievals_per_60": 1.94,
                        "successful_retrieval_percent": 0.75,
                        "exits_per_60": 0.19,
                        "botched_retrievals_per_60": -1.57
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "ross colton": {
        "name": "Ross\u00a0Colton",
        "team": "SJS",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 160.2,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.82,
                        "shot_assists_per_60": 0.54,
                        "total_shot_contributions_per_60": 1.36,
                        "chances_per_60": 0.84,
                        "chance_assists_per_60": 0.67
                },
                "passing": {
                        "high_danger_assists_per_60": 0.47
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.68,
                        "rush_offense_per_60": 0.52,
                        "shots_off_hd_passes_per_60": 0.65
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.54,
                        "controlled_entry_percent": 0.46,
                        "controlled_entry_with_chance_percent": 0.34
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.75,
                        "retrievals_per_60": 2.07,
                        "successful_retrieval_percent": 0.68,
                        "exits_per_60": 0.35,
                        "botched_retrievals_per_60": -3.12
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "parker kelly": {
        "name": "Parker\u00a0Kelly",
        "team": "SEA",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 147.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.57,
                        "shot_assists_per_60": 0.91,
                        "total_shot_contributions_per_60": 1.48,
                        "chances_per_60": 0.51,
                        "chance_assists_per_60": 1.05
                },
                "passing": {
                        "high_danger_assists_per_60": 0.76
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.75,
                        "rush_offense_per_60": 0.22,
                        "shots_off_hd_passes_per_60": 0.49
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.72,
                        "controlled_entry_percent": 0.47,
                        "controlled_entry_with_chance_percent": 0.34
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.29,
                        "retrievals_per_60": 2.02,
                        "successful_retrieval_percent": 0.63,
                        "exits_per_60": 0.38,
                        "botched_retrievals_per_60": -3.52
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "nathan mackinnon": {
        "name": "Nathan\u00a0MacKinnon",
        "team": "STL",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 104.8,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.62,
                        "shot_assists_per_60": 0.54,
                        "total_shot_contributions_per_60": 1.16,
                        "chances_per_60": 0.53,
                        "chance_assists_per_60": 0.51
                },
                "passing": {
                        "high_danger_assists_per_60": 0.45
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.64,
                        "rush_offense_per_60": 0.45,
                        "shots_off_hd_passes_per_60": 0.52
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.55,
                        "controlled_entry_percent": 0.49,
                        "controlled_entry_with_chance_percent": 0.24
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.45,
                        "retrievals_per_60": 2.95,
                        "successful_retrieval_percent": 0.71,
                        "exits_per_60": 0.23,
                        "botched_retrievals_per_60": -2.34
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "martin necas": {
        "name": "Martin\u00a0Necas",
        "team": "TBL",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 140.4,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.901,
                        "goals_against_average": 3.1,
                        "wins": 27,
                        "shutouts": 4
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "logan o'connor": {
        "name": "Logan\u00a0O'Connor",
        "team": "TOR",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 186.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.11,
                        "shot_assists_per_60": 0.65,
                        "total_shot_contributions_per_60": 1.76,
                        "chances_per_60": 1.33,
                        "chance_assists_per_60": 0.73
                },
                "passing": {
                        "high_danger_assists_per_60": 0.72
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.19,
                        "rush_offense_per_60": 0.55,
                        "shots_off_hd_passes_per_60": 1.14
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.56,
                        "controlled_entry_percent": 0.33,
                        "controlled_entry_with_chance_percent": 0.2
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.57,
                        "retrievals_per_60": 2.92,
                        "successful_retrieval_percent": 0.77,
                        "exits_per_60": 0.27,
                        "botched_retrievals_per_60": -1.71
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "keaton middleton": {
        "name": "Keaton\u00a0Middleton",
        "team": "VAN",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 126.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.74,
                        "shot_assists_per_60": 0.54,
                        "total_shot_contributions_per_60": 2.28,
                        "chances_per_60": 2.24,
                        "chance_assists_per_60": 0.64
                },
                "passing": {
                        "high_danger_assists_per_60": 0.54
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.89,
                        "rush_offense_per_60": 1.02,
                        "shots_off_hd_passes_per_60": 1.83
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.75,
                        "controlled_entry_percent": 0.43,
                        "controlled_entry_with_chance_percent": 0.33
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.62,
                        "retrievals_per_60": 1.97,
                        "successful_retrieval_percent": 0.58,
                        "exits_per_60": 0.37,
                        "botched_retrievals_per_60": -2.28
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "josh manson": {
        "name": "Josh\u00a0Manson",
        "team": "VGK",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 124.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.11,
                        "shot_assists_per_60": 1.09,
                        "total_shot_contributions_per_60": 2.2,
                        "chances_per_60": 1.03,
                        "chance_assists_per_60": 1.2
                },
                "passing": {
                        "high_danger_assists_per_60": 1.01
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.43,
                        "rush_offense_per_60": 0.5,
                        "shots_off_hd_passes_per_60": 0.79
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.02,
                        "controlled_entry_percent": 0.6,
                        "controlled_entry_with_chance_percent": 0.17
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.78,
                        "retrievals_per_60": 1.97,
                        "successful_retrieval_percent": 0.82,
                        "exits_per_60": 0.3,
                        "botched_retrievals_per_60": -2.21
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jonathan drouin": {
        "name": "Jonathan\u00a0Drouin",
        "team": "WSH",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 175.8,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.48,
                        "shot_assists_per_60": 0.65,
                        "total_shot_contributions_per_60": 1.13,
                        "chances_per_60": 0.53,
                        "chance_assists_per_60": 0.61
                },
                "passing": {
                        "high_danger_assists_per_60": 0.71
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.6,
                        "rush_offense_per_60": 0.21,
                        "shots_off_hd_passes_per_60": 0.48
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.74,
                        "controlled_entry_percent": 0.47,
                        "controlled_entry_with_chance_percent": 0.28
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.47,
                        "retrievals_per_60": 4.14,
                        "successful_retrieval_percent": 0.82,
                        "exits_per_60": 0.15,
                        "botched_retrievals_per_60": -3.18
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "joel kiviranta": {
        "name": "Joel\u00a0Kiviranta",
        "team": "WPG",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 199.5,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.923,
                        "goals_against_average": 2.14,
                        "wins": 19,
                        "shutouts": 4
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jack drury": {
        "name": "Jack\u00a0Drury",
        "team": "ANA",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 119.2,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.99,
                        "shot_assists_per_60": 0.44,
                        "total_shot_contributions_per_60": 1.43,
                        "chances_per_60": 0.8,
                        "chance_assists_per_60": 0.5
                },
                "passing": {
                        "high_danger_assists_per_60": 0.49
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.93,
                        "rush_offense_per_60": 0.77,
                        "shots_off_hd_passes_per_60": 1.0
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.37,
                        "controlled_entry_percent": 0.45,
                        "controlled_entry_with_chance_percent": 0.15
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.19,
                        "retrievals_per_60": 2.04,
                        "successful_retrieval_percent": 0.76,
                        "exits_per_60": 0.34,
                        "botched_retrievals_per_60": -1.95
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "ivan ivan": {
        "name": "Ivan\u00a0Ivan",
        "team": "ARI",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 138.8,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.98,
                        "shot_assists_per_60": 0.75,
                        "total_shot_contributions_per_60": 1.73,
                        "chances_per_60": 1.04,
                        "chance_assists_per_60": 0.61
                },
                "passing": {
                        "high_danger_assists_per_60": 0.6
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.09,
                        "rush_offense_per_60": 0.69,
                        "shots_off_hd_passes_per_60": 0.92
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.58,
                        "controlled_entry_percent": 0.39,
                        "controlled_entry_with_chance_percent": 0.21
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.7,
                        "retrievals_per_60": 2.96,
                        "successful_retrieval_percent": 0.63,
                        "exits_per_60": 0.19,
                        "botched_retrievals_per_60": -1.75
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "devon toews": {
        "name": "Devon\u00a0Toews",
        "team": "BOS",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 199.1,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.82,
                        "shot_assists_per_60": 0.79,
                        "total_shot_contributions_per_60": 1.61,
                        "chances_per_60": 0.66,
                        "chance_assists_per_60": 0.92
                },
                "passing": {
                        "high_danger_assists_per_60": 0.78
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.11,
                        "rush_offense_per_60": 0.37,
                        "shots_off_hd_passes_per_60": 0.74
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.03,
                        "controlled_entry_percent": 0.6,
                        "controlled_entry_with_chance_percent": 0.34
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.55,
                        "retrievals_per_60": 2.38,
                        "successful_retrieval_percent": 0.66,
                        "exits_per_60": 0.23,
                        "botched_retrievals_per_60": -2.06
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "casey mittelstadt": {
        "name": "Casey\u00a0Mittelstadt",
        "team": "BUF",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 134.7,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.33,
                        "shot_assists_per_60": 0.77,
                        "total_shot_contributions_per_60": 1.1,
                        "chances_per_60": 0.28,
                        "chance_assists_per_60": 0.88
                },
                "passing": {
                        "high_danger_assists_per_60": 0.78
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.44,
                        "rush_offense_per_60": 0.13,
                        "shots_off_hd_passes_per_60": 0.34
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.7,
                        "controlled_entry_percent": 0.4,
                        "controlled_entry_with_chance_percent": 0.21
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.52,
                        "retrievals_per_60": 3.88,
                        "successful_retrieval_percent": 0.56,
                        "exits_per_60": 0.37,
                        "botched_retrievals_per_60": -1.6
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "calvin de_haan": {
        "name": "Calvin\u00a0de Haan",
        "team": "CGY",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 104.9,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.915,
                        "goals_against_average": 2.97,
                        "wins": 26,
                        "shutouts": 3
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "cale makar": {
        "name": "Cale\u00a0Makar",
        "team": "CAR",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 183.3,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.83,
                        "shot_assists_per_60": 1.16,
                        "total_shot_contributions_per_60": 1.99,
                        "chances_per_60": 0.93,
                        "chance_assists_per_60": 1.49
                },
                "passing": {
                        "high_danger_assists_per_60": 1.28
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.91,
                        "rush_offense_per_60": 0.65,
                        "shots_off_hd_passes_per_60": 0.83
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.85,
                        "controlled_entry_percent": 0.63,
                        "controlled_entry_with_chance_percent": 0.28
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.94,
                        "retrievals_per_60": 2.83,
                        "successful_retrieval_percent": 0.71,
                        "exits_per_60": 0.15,
                        "botched_retrievals_per_60": -1.99
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "artturi lehkonen": {
        "name": "Artturi\u00a0Lehkonen",
        "team": "CHI",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 197.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.52,
                        "shot_assists_per_60": 0.67,
                        "total_shot_contributions_per_60": 1.19,
                        "chances_per_60": 0.37,
                        "chance_assists_per_60": 0.82
                },
                "passing": {
                        "high_danger_assists_per_60": 0.7
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.67,
                        "rush_offense_per_60": 0.24,
                        "shots_off_hd_passes_per_60": 0.53
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.32,
                        "controlled_entry_percent": 0.49,
                        "controlled_entry_with_chance_percent": 0.34
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.9,
                        "retrievals_per_60": 2.6,
                        "successful_retrieval_percent": 0.75,
                        "exits_per_60": 0.35,
                        "botched_retrievals_per_60": -3.91
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "wyatt kaiser": {
        "name": "Wyatt\u00a0Kaiser",
        "team": "COL",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 122.2,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.92,
                        "shot_assists_per_60": 1.11,
                        "total_shot_contributions_per_60": 2.03,
                        "chances_per_60": 0.66,
                        "chance_assists_per_60": 1.32
                },
                "passing": {
                        "high_danger_assists_per_60": 1.3
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.82,
                        "rush_offense_per_60": 0.39,
                        "shots_off_hd_passes_per_60": 0.68
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.1,
                        "controlled_entry_percent": 0.55,
                        "controlled_entry_with_chance_percent": 0.22
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.99,
                        "retrievals_per_60": 1.99,
                        "successful_retrieval_percent": 0.58,
                        "exits_per_60": 0.24,
                        "botched_retrievals_per_60": -2.68
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "tyler bertuzzi": {
        "name": "Tyler\u00a0Bertuzzi",
        "team": "CBJ",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 191.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.8,
                        "shot_assists_per_60": 0.53,
                        "total_shot_contributions_per_60": 1.33,
                        "chances_per_60": 0.97,
                        "chance_assists_per_60": 0.49
                },
                "passing": {
                        "high_danger_assists_per_60": 0.45
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.88,
                        "rush_offense_per_60": 0.64,
                        "shots_off_hd_passes_per_60": 0.6
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.65,
                        "controlled_entry_percent": 0.5,
                        "controlled_entry_with_chance_percent": 0.32
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.69,
                        "retrievals_per_60": 3.41,
                        "successful_retrieval_percent": 0.77,
                        "exits_per_60": 0.33,
                        "botched_retrievals_per_60": -2.54
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "tj brodie": {
        "name": "TJ\u00a0Brodie",
        "team": "DAL",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 131.0,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.917,
                        "goals_against_average": 2.46,
                        "wins": 40,
                        "shutouts": 3
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "teuvo teravainen": {
        "name": "Teuvo\u00a0Teravainen",
        "team": "DET",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 128.6,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.61,
                        "shot_assists_per_60": 1.19,
                        "total_shot_contributions_per_60": 2.8,
                        "chances_per_60": 1.89,
                        "chance_assists_per_60": 0.99
                },
                "passing": {
                        "high_danger_assists_per_60": 1.42
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 2.02,
                        "rush_offense_per_60": 0.89,
                        "shots_off_hd_passes_per_60": 1.54
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.1,
                        "controlled_entry_percent": 0.45,
                        "controlled_entry_with_chance_percent": 0.24
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.75,
                        "retrievals_per_60": 1.76,
                        "successful_retrieval_percent": 0.71,
                        "exits_per_60": 0.39,
                        "botched_retrievals_per_60": -3.74
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "taylor hall": {
        "name": "Taylor\u00a0Hall",
        "team": "EDM",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 110.3,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.14,
                        "shot_assists_per_60": 0.62,
                        "total_shot_contributions_per_60": 1.76,
                        "chances_per_60": 1.06,
                        "chance_assists_per_60": 0.77
                },
                "passing": {
                        "high_danger_assists_per_60": 0.52
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.43,
                        "rush_offense_per_60": 0.35,
                        "shots_off_hd_passes_per_60": 0.9
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.95,
                        "controlled_entry_percent": 0.48,
                        "controlled_entry_with_chance_percent": 0.17
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.79,
                        "retrievals_per_60": 1.75,
                        "successful_retrieval_percent": 0.62,
                        "exits_per_60": 0.11,
                        "botched_retrievals_per_60": -2.03
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "seth jones": {
        "name": "Seth\u00a0Jones",
        "team": "FLA",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 179.2,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.21,
                        "shot_assists_per_60": 0.65,
                        "total_shot_contributions_per_60": 1.86,
                        "chances_per_60": 1.3,
                        "chance_assists_per_60": 0.52
                },
                "passing": {
                        "high_danger_assists_per_60": 0.74
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.02,
                        "rush_offense_per_60": 0.64,
                        "shots_off_hd_passes_per_60": 0.99
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.36,
                        "controlled_entry_percent": 0.26,
                        "controlled_entry_with_chance_percent": 0.31
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.71,
                        "retrievals_per_60": 2.53,
                        "successful_retrieval_percent": 0.82,
                        "exits_per_60": 0.11,
                        "botched_retrievals_per_60": -2.31
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "ryan donato": {
        "name": "Ryan\u00a0Donato",
        "team": "LAK",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 146.2,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.3,
                        "shot_assists_per_60": 0.63,
                        "total_shot_contributions_per_60": 0.93,
                        "chances_per_60": 0.29,
                        "chance_assists_per_60": 0.87
                },
                "passing": {
                        "high_danger_assists_per_60": 0.7
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.39,
                        "rush_offense_per_60": 0.14,
                        "shots_off_hd_passes_per_60": 0.24
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.34,
                        "controlled_entry_percent": 0.55,
                        "controlled_entry_with_chance_percent": 0.2
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.2,
                        "retrievals_per_60": 2.82,
                        "successful_retrieval_percent": 0.84,
                        "exits_per_60": 0.11,
                        "botched_retrievals_per_60": -2.96
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "philipp kurashev": {
        "name": "Philipp\u00a0Kurashev",
        "team": "MIN",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 154.9,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.904,
                        "goals_against_average": 3.23,
                        "wins": 14,
                        "shutouts": 5
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "patrick maroon": {
        "name": "Patrick\u00a0Maroon",
        "team": "MTL",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 178.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.04,
                        "shot_assists_per_60": 1.15,
                        "total_shot_contributions_per_60": 2.19,
                        "chances_per_60": 1.07,
                        "chance_assists_per_60": 1.15
                },
                "passing": {
                        "high_danger_assists_per_60": 1.27
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.07,
                        "rush_offense_per_60": 0.39,
                        "shots_off_hd_passes_per_60": 0.82
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.84,
                        "controlled_entry_percent": 0.51,
                        "controlled_entry_with_chance_percent": 0.3
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.58,
                        "retrievals_per_60": 1.82,
                        "successful_retrieval_percent": 0.8,
                        "exits_per_60": 0.24,
                        "botched_retrievals_per_60": -1.9
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "nolan allan": {
        "name": "Nolan\u00a0Allan",
        "team": "NSH",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 199.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.75,
                        "shot_assists_per_60": 0.8,
                        "total_shot_contributions_per_60": 2.55,
                        "chances_per_60": 1.29,
                        "chance_assists_per_60": 1.07
                },
                "passing": {
                        "high_danger_assists_per_60": 0.71
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 2.42,
                        "rush_offense_per_60": 1.06,
                        "shots_off_hd_passes_per_60": 1.35
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.47,
                        "controlled_entry_percent": 0.56,
                        "controlled_entry_with_chance_percent": 0.2
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.92,
                        "retrievals_per_60": 2.72,
                        "successful_retrieval_percent": 0.81,
                        "exits_per_60": 0.38,
                        "botched_retrievals_per_60": -2.07
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "nick foligno": {
        "name": "Nick\u00a0Foligno",
        "team": "NJD",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 133.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.01,
                        "shot_assists_per_60": 0.91,
                        "total_shot_contributions_per_60": 1.92,
                        "chances_per_60": 0.75,
                        "chance_assists_per_60": 1.0
                },
                "passing": {
                        "high_danger_assists_per_60": 0.76
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.03,
                        "rush_offense_per_60": 0.31,
                        "shots_off_hd_passes_per_60": 0.82
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.96,
                        "controlled_entry_percent": 0.49,
                        "controlled_entry_with_chance_percent": 0.31
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.42,
                        "retrievals_per_60": 2.12,
                        "successful_retrieval_percent": 0.73,
                        "exits_per_60": 0.37,
                        "botched_retrievals_per_60": -1.96
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "lukas reichel": {
        "name": "Lukas\u00a0Reichel",
        "team": "NYI",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 105.0,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.68,
                        "shot_assists_per_60": 0.3,
                        "total_shot_contributions_per_60": 0.98,
                        "chances_per_60": 0.61,
                        "chance_assists_per_60": 0.34
                },
                "passing": {
                        "high_danger_assists_per_60": 0.26
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.71,
                        "rush_offense_per_60": 0.47,
                        "shots_off_hd_passes_per_60": 0.53
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.77,
                        "controlled_entry_percent": 0.28,
                        "controlled_entry_with_chance_percent": 0.18
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.69,
                        "retrievals_per_60": 4.18,
                        "successful_retrieval_percent": 0.73,
                        "exits_per_60": 0.34,
                        "botched_retrievals_per_60": -2.44
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "kevin korchinski": {
        "name": "Kevin\u00a0Korchinski",
        "team": "NYR",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 158.5,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.912,
                        "goals_against_average": 2.35,
                        "wins": 45,
                        "shutouts": 5
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "joey anderson": {
        "name": "Joey\u00a0Anderson",
        "team": "OTT",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 123.6,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.33,
                        "shot_assists_per_60": 0.8,
                        "total_shot_contributions_per_60": 2.13,
                        "chances_per_60": 1.22,
                        "chance_assists_per_60": 0.75
                },
                "passing": {
                        "high_danger_assists_per_60": 0.65
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.3,
                        "rush_offense_per_60": 0.55,
                        "shots_off_hd_passes_per_60": 1.41
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.92,
                        "controlled_entry_percent": 0.57,
                        "controlled_entry_with_chance_percent": 0.31
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.84,
                        "retrievals_per_60": 1.95,
                        "successful_retrieval_percent": 0.6,
                        "exits_per_60": 0.14,
                        "botched_retrievals_per_60": -2.43
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jason dickinson": {
        "name": "Jason\u00a0Dickinson",
        "team": "PHI",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 102.2,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.76,
                        "shot_assists_per_60": 0.41,
                        "total_shot_contributions_per_60": 1.17,
                        "chances_per_60": 0.82,
                        "chance_assists_per_60": 0.34
                },
                "passing": {
                        "high_danger_assists_per_60": 0.41
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.73,
                        "rush_offense_per_60": 0.28,
                        "shots_off_hd_passes_per_60": 0.58
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.3,
                        "controlled_entry_percent": 0.26,
                        "controlled_entry_with_chance_percent": 0.34
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.07,
                        "retrievals_per_60": 2.81,
                        "successful_retrieval_percent": 0.66,
                        "exits_per_60": 0.3,
                        "botched_retrievals_per_60": -2.83
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "ilya mikheyev": {
        "name": "Ilya\u00a0Mikheyev",
        "team": "PIT",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 146.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.52,
                        "shot_assists_per_60": 0.64,
                        "total_shot_contributions_per_60": 1.16,
                        "chances_per_60": 0.48,
                        "chance_assists_per_60": 0.86
                },
                "passing": {
                        "high_danger_assists_per_60": 0.64
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.56,
                        "rush_offense_per_60": 0.27,
                        "shots_off_hd_passes_per_60": 0.5
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.2,
                        "controlled_entry_percent": 0.26,
                        "controlled_entry_with_chance_percent": 0.2
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.91,
                        "retrievals_per_60": 2.73,
                        "successful_retrieval_percent": 0.7,
                        "exits_per_60": 0.24,
                        "botched_retrievals_per_60": -2.01
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "craig smith": {
        "name": "Craig\u00a0Smith",
        "team": "SJS",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 111.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.58,
                        "shot_assists_per_60": 0.5,
                        "total_shot_contributions_per_60": 1.08,
                        "chances_per_60": 0.48,
                        "chance_assists_per_60": 0.68
                },
                "passing": {
                        "high_danger_assists_per_60": 0.52
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.71,
                        "rush_offense_per_60": 0.23,
                        "shots_off_hd_passes_per_60": 0.63
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.76,
                        "controlled_entry_percent": 0.52,
                        "controlled_entry_with_chance_percent": 0.23
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.94,
                        "retrievals_per_60": 3.29,
                        "successful_retrieval_percent": 0.58,
                        "exits_per_60": 0.29,
                        "botched_retrievals_per_60": -3.69
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "connor murphy": {
        "name": "Connor\u00a0Murphy",
        "team": "SEA",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 100.8,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.912,
                        "goals_against_average": 2.17,
                        "wins": 21,
                        "shutouts": 5
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "connor bedard": {
        "name": "Connor\u00a0Bedard",
        "team": "STL",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 110.7,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.72,
                        "shot_assists_per_60": 0.46,
                        "total_shot_contributions_per_60": 2.18,
                        "chances_per_60": 2.09,
                        "chance_assists_per_60": 0.37
                },
                "passing": {
                        "high_danger_assists_per_60": 0.52
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.91,
                        "rush_offense_per_60": 1.13,
                        "shots_off_hd_passes_per_60": 1.62
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.45,
                        "controlled_entry_percent": 0.27,
                        "controlled_entry_with_chance_percent": 0.22
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.13,
                        "retrievals_per_60": 2.67,
                        "successful_retrieval_percent": 0.77,
                        "exits_per_60": 0.25,
                        "botched_retrievals_per_60": -2.08
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "alex vlasic": {
        "name": "Alex\u00a0Vlasic",
        "team": "TBL",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 104.1,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.51,
                        "shot_assists_per_60": 1.06,
                        "total_shot_contributions_per_60": 2.57,
                        "chances_per_60": 1.19,
                        "chance_assists_per_60": 1.09
                },
                "passing": {
                        "high_danger_assists_per_60": 1.24
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.64,
                        "rush_offense_per_60": 0.5,
                        "shots_off_hd_passes_per_60": 1.64
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.41,
                        "controlled_entry_percent": 0.57,
                        "controlled_entry_with_chance_percent": 0.24
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.62,
                        "retrievals_per_60": 2.79,
                        "successful_retrieval_percent": 0.62,
                        "exits_per_60": 0.39,
                        "botched_retrievals_per_60": -2.64
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "alec martinez": {
        "name": "Alec\u00a0Martinez",
        "team": "TOR",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 112.6,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.79,
                        "shot_assists_per_60": 1.07,
                        "total_shot_contributions_per_60": 1.86,
                        "chances_per_60": 0.68,
                        "chance_assists_per_60": 0.94
                },
                "passing": {
                        "high_danger_assists_per_60": 1.12
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.79,
                        "rush_offense_per_60": 0.37,
                        "shots_off_hd_passes_per_60": 0.71
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.52,
                        "controlled_entry_percent": 0.49,
                        "controlled_entry_with_chance_percent": 0.31
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.81,
                        "retrievals_per_60": 2.05,
                        "successful_retrieval_percent": 0.73,
                        "exits_per_60": 0.24,
                        "botched_retrievals_per_60": -3.43
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "yegor sharangovich": {
        "name": "Yegor\u00a0Sharangovich",
        "team": "VAN",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 113.1,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.73,
                        "shot_assists_per_60": 0.67,
                        "total_shot_contributions_per_60": 1.4,
                        "chances_per_60": 0.58,
                        "chance_assists_per_60": 0.93
                },
                "passing": {
                        "high_danger_assists_per_60": 0.64
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.69,
                        "rush_offense_per_60": 0.5,
                        "shots_off_hd_passes_per_60": 0.74
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.66,
                        "controlled_entry_percent": 0.29,
                        "controlled_entry_with_chance_percent": 0.19
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.55,
                        "retrievals_per_60": 3.18,
                        "successful_retrieval_percent": 0.73,
                        "exits_per_60": 0.17,
                        "botched_retrievals_per_60": -3.62
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "ryan lomberg": {
        "name": "Ryan\u00a0Lomberg",
        "team": "VGK",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 196.5,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.912,
                        "goals_against_average": 2.65,
                        "wins": 32,
                        "shutouts": 1
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "rasmus andersson": {
        "name": "Rasmus\u00a0Andersson",
        "team": "WSH",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 128.7,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.3,
                        "shot_assists_per_60": 0.82,
                        "total_shot_contributions_per_60": 2.12,
                        "chances_per_60": 0.96,
                        "chance_assists_per_60": 0.69
                },
                "passing": {
                        "high_danger_assists_per_60": 0.75
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.29,
                        "rush_offense_per_60": 1.0,
                        "shots_off_hd_passes_per_60": 1.31
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.63,
                        "controlled_entry_percent": 0.59,
                        "controlled_entry_with_chance_percent": 0.23
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.67,
                        "retrievals_per_60": 1.85,
                        "successful_retrieval_percent": 0.81,
                        "exits_per_60": 0.39,
                        "botched_retrievals_per_60": -1.91
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "nazem kadri": {
        "name": "Nazem\u00a0Kadri",
        "team": "WPG",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 185.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.18,
                        "shot_assists_per_60": 1.04,
                        "total_shot_contributions_per_60": 2.22,
                        "chances_per_60": 0.89,
                        "chance_assists_per_60": 0.96
                },
                "passing": {
                        "high_danger_assists_per_60": 0.88
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.3,
                        "rush_offense_per_60": 0.85,
                        "shots_off_hd_passes_per_60": 0.84
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.47,
                        "controlled_entry_percent": 0.56,
                        "controlled_entry_with_chance_percent": 0.22
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.84,
                        "retrievals_per_60": 1.76,
                        "successful_retrieval_percent": 0.83,
                        "exits_per_60": 0.36,
                        "botched_retrievals_per_60": -3.58
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "mikael backlund": {
        "name": "Mikael\u00a0Backlund",
        "team": "ANA",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 153.0,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.75,
                        "shot_assists_per_60": 1.0,
                        "total_shot_contributions_per_60": 1.75,
                        "chances_per_60": 0.82,
                        "chance_assists_per_60": 1.22
                },
                "passing": {
                        "high_danger_assists_per_60": 0.86
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.92,
                        "rush_offense_per_60": 0.47,
                        "shots_off_hd_passes_per_60": 0.53
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.17,
                        "controlled_entry_percent": 0.51,
                        "controlled_entry_with_chance_percent": 0.17
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.96,
                        "retrievals_per_60": 2.51,
                        "successful_retrieval_percent": 0.66,
                        "exits_per_60": 0.39,
                        "botched_retrievals_per_60": -2.59
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "matt coronato": {
        "name": "Matt\u00a0Coronato",
        "team": "ARI",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 129.1,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.66,
                        "shot_assists_per_60": 0.53,
                        "total_shot_contributions_per_60": 1.19,
                        "chances_per_60": 0.55,
                        "chance_assists_per_60": 0.66
                },
                "passing": {
                        "high_danger_assists_per_60": 0.51
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.88,
                        "rush_offense_per_60": 0.28,
                        "shots_off_hd_passes_per_60": 0.72
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.49,
                        "controlled_entry_percent": 0.45,
                        "controlled_entry_with_chance_percent": 0.29
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 4.1,
                        "retrievals_per_60": 3.78,
                        "successful_retrieval_percent": 0.81,
                        "exits_per_60": 0.1,
                        "botched_retrievals_per_60": -1.7
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "martin pospisil": {
        "name": "Martin\u00a0Pospisil",
        "team": "BOS",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 111.8,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.927,
                        "goals_against_average": 2.44,
                        "wins": 33,
                        "shutouts": 5
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "mackenzie weegar": {
        "name": "MacKenzie\u00a0Weegar",
        "team": "BUF",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 166.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.71,
                        "shot_assists_per_60": 1.09,
                        "total_shot_contributions_per_60": 1.8,
                        "chances_per_60": 0.76,
                        "chance_assists_per_60": 1.06
                },
                "passing": {
                        "high_danger_assists_per_60": 1.08
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.58,
                        "rush_offense_per_60": 0.24,
                        "shots_off_hd_passes_per_60": 0.61
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.23,
                        "controlled_entry_percent": 0.54,
                        "controlled_entry_with_chance_percent": 0.29
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.43,
                        "retrievals_per_60": 2.37,
                        "successful_retrieval_percent": 0.82,
                        "exits_per_60": 0.22,
                        "botched_retrievals_per_60": -2.77
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "kevin rooney": {
        "name": "Kevin\u00a0Rooney",
        "team": "CGY",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 183.3,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.54,
                        "shot_assists_per_60": 0.6,
                        "total_shot_contributions_per_60": 1.14,
                        "chances_per_60": 0.61,
                        "chance_assists_per_60": 0.75
                },
                "passing": {
                        "high_danger_assists_per_60": 0.7
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.7,
                        "rush_offense_per_60": 0.28,
                        "shots_off_hd_passes_per_60": 0.55
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.88,
                        "controlled_entry_percent": 0.29,
                        "controlled_entry_with_chance_percent": 0.32
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.69,
                        "retrievals_per_60": 1.61,
                        "successful_retrieval_percent": 0.68,
                        "exits_per_60": 0.13,
                        "botched_retrievals_per_60": -3.61
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "kevin bahl": {
        "name": "Kevin\u00a0Bahl",
        "team": "CAR",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 102.1,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.13,
                        "shot_assists_per_60": 1.02,
                        "total_shot_contributions_per_60": 2.15,
                        "chances_per_60": 1.28,
                        "chance_assists_per_60": 1.16
                },
                "passing": {
                        "high_danger_assists_per_60": 1.07
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.97,
                        "rush_offense_per_60": 0.51,
                        "shots_off_hd_passes_per_60": 1.1
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.21,
                        "controlled_entry_percent": 0.33,
                        "controlled_entry_with_chance_percent": 0.26
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.68,
                        "retrievals_per_60": 1.86,
                        "successful_retrieval_percent": 0.71,
                        "exits_per_60": 0.17,
                        "botched_retrievals_per_60": -3.51
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jonathan huberdeau": {
        "name": "Jonathan\u00a0Huberdeau",
        "team": "CHI",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 148.8,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.13,
                        "shot_assists_per_60": 0.64,
                        "total_shot_contributions_per_60": 0.77,
                        "chances_per_60": 0.14,
                        "chance_assists_per_60": 0.67
                },
                "passing": {
                        "high_danger_assists_per_60": 0.6
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.15,
                        "rush_offense_per_60": 0.06,
                        "shots_off_hd_passes_per_60": 0.11
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.46,
                        "controlled_entry_percent": 0.37,
                        "controlled_entry_with_chance_percent": 0.16
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 4.21,
                        "retrievals_per_60": 3.92,
                        "successful_retrieval_percent": 0.79,
                        "exits_per_60": 0.12,
                        "botched_retrievals_per_60": -3.7
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "joel hanley": {
        "name": "Joel\u00a0Hanley",
        "team": "COL",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 122.5,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.916,
                        "goals_against_average": 2.79,
                        "wins": 26,
                        "shutouts": 8
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jake bean": {
        "name": "Jake\u00a0Bean",
        "team": "CBJ",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 159.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.23,
                        "shot_assists_per_60": 0.81,
                        "total_shot_contributions_per_60": 2.04,
                        "chances_per_60": 1.16,
                        "chance_assists_per_60": 0.78
                },
                "passing": {
                        "high_danger_assists_per_60": 0.97
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.19,
                        "rush_offense_per_60": 0.42,
                        "shots_off_hd_passes_per_60": 0.87
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.76,
                        "controlled_entry_percent": 0.63,
                        "controlled_entry_with_chance_percent": 0.25
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.56,
                        "retrievals_per_60": 1.52,
                        "successful_retrieval_percent": 0.56,
                        "exits_per_60": 0.35,
                        "botched_retrievals_per_60": -2.69
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "daniil miromanov": {
        "name": "Daniil\u00a0Miromanov",
        "team": "DAL",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 102.1,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.96,
                        "shot_assists_per_60": 0.52,
                        "total_shot_contributions_per_60": 1.48,
                        "chances_per_60": 0.95,
                        "chance_assists_per_60": 0.51
                },
                "passing": {
                        "high_danger_assists_per_60": 0.42
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.86,
                        "rush_offense_per_60": 0.38,
                        "shots_off_hd_passes_per_60": 0.74
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.39,
                        "controlled_entry_percent": 0.6,
                        "controlled_entry_with_chance_percent": 0.33
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.22,
                        "retrievals_per_60": 2.16,
                        "successful_retrieval_percent": 0.57,
                        "exits_per_60": 0.38,
                        "botched_retrievals_per_60": -1.69
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "connor zary": {
        "name": "Connor\u00a0Zary",
        "team": "DET",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 117.7,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.26,
                        "shot_assists_per_60": 0.64,
                        "total_shot_contributions_per_60": 1.9,
                        "chances_per_60": 1.15,
                        "chance_assists_per_60": 0.6
                },
                "passing": {
                        "high_danger_assists_per_60": 0.54
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.74,
                        "rush_offense_per_60": 0.61,
                        "shots_off_hd_passes_per_60": 0.97
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.18,
                        "controlled_entry_percent": 0.31,
                        "controlled_entry_with_chance_percent": 0.3
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.74,
                        "retrievals_per_60": 1.85,
                        "successful_retrieval_percent": 0.56,
                        "exits_per_60": 0.17,
                        "botched_retrievals_per_60": -2.55
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "brayden pachal": {
        "name": "Brayden\u00a0Pachal",
        "team": "EDM",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 133.0,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.67,
                        "shot_assists_per_60": 0.83,
                        "total_shot_contributions_per_60": 1.5,
                        "chances_per_60": 0.57,
                        "chance_assists_per_60": 0.97
                },
                "passing": {
                        "high_danger_assists_per_60": 0.96
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.59,
                        "rush_offense_per_60": 0.29,
                        "shots_off_hd_passes_per_60": 0.73
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.45,
                        "controlled_entry_percent": 0.35,
                        "controlled_entry_with_chance_percent": 0.25
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.79,
                        "retrievals_per_60": 3.48,
                        "successful_retrieval_percent": 0.7,
                        "exits_per_60": 0.24,
                        "botched_retrievals_per_60": -2.45
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "blake coleman": {
        "name": "Blake\u00a0Coleman",
        "team": "FLA",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 194.9,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.919,
                        "goals_against_average": 3.2,
                        "wins": 40,
                        "shutouts": 3
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "zach werenski": {
        "name": "Zach\u00a0Werenski",
        "team": "LAK",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 130.0,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.1,
                        "shot_assists_per_60": 0.9,
                        "total_shot_contributions_per_60": 2.0,
                        "chances_per_60": 0.92,
                        "chance_assists_per_60": 0.84
                },
                "passing": {
                        "high_danger_assists_per_60": 0.79
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.26,
                        "rush_offense_per_60": 0.44,
                        "shots_off_hd_passes_per_60": 1.14
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.46,
                        "controlled_entry_percent": 0.45,
                        "controlled_entry_with_chance_percent": 0.24
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.76,
                        "retrievals_per_60": 1.69,
                        "successful_retrieval_percent": 0.8,
                        "exits_per_60": 0.26,
                        "botched_retrievals_per_60": -3.49
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "zach aston_reese": {
        "name": "Zach\u00a0Aston-Reese",
        "team": "MIN",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 152.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.06,
                        "shot_assists_per_60": 0.62,
                        "total_shot_contributions_per_60": 1.68,
                        "chances_per_60": 1.36,
                        "chance_assists_per_60": 0.63
                },
                "passing": {
                        "high_danger_assists_per_60": 0.7
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.94,
                        "rush_offense_per_60": 0.57,
                        "shots_off_hd_passes_per_60": 0.92
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.7,
                        "controlled_entry_percent": 0.51,
                        "controlled_entry_with_chance_percent": 0.22
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.4,
                        "retrievals_per_60": 2.9,
                        "successful_retrieval_percent": 0.73,
                        "exits_per_60": 0.34,
                        "botched_retrievals_per_60": -2.89
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "sean monahan": {
        "name": "Sean\u00a0Monahan",
        "team": "MTL",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 175.1,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.85,
                        "shot_assists_per_60": 0.63,
                        "total_shot_contributions_per_60": 1.48,
                        "chances_per_60": 0.64,
                        "chance_assists_per_60": 0.64
                },
                "passing": {
                        "high_danger_assists_per_60": 0.55
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.76,
                        "rush_offense_per_60": 0.46,
                        "shots_off_hd_passes_per_60": 0.69
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.07,
                        "controlled_entry_percent": 0.3,
                        "controlled_entry_with_chance_percent": 0.33
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.49,
                        "retrievals_per_60": 2.98,
                        "successful_retrieval_percent": 0.66,
                        "exits_per_60": 0.33,
                        "botched_retrievals_per_60": -2.92
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "sean kuraly": {
        "name": "Sean\u00a0Kuraly",
        "team": "NSH",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 139.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.33,
                        "shot_assists_per_60": 0.84,
                        "total_shot_contributions_per_60": 1.17,
                        "chances_per_60": 0.24,
                        "chance_assists_per_60": 0.98
                },
                "passing": {
                        "high_danger_assists_per_60": 0.91
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.45,
                        "rush_offense_per_60": 0.15,
                        "shots_off_hd_passes_per_60": 0.27
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.61,
                        "controlled_entry_percent": 0.31,
                        "controlled_entry_with_chance_percent": 0.2
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.34,
                        "retrievals_per_60": 3.14,
                        "successful_retrieval_percent": 0.57,
                        "exits_per_60": 0.39,
                        "botched_retrievals_per_60": -3.02
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "mathieu olivier": {
        "name": "Mathieu\u00a0Olivier",
        "team": "NJD",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 151.7,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.91,
                        "goals_against_average": 3.38,
                        "wins": 31,
                        "shutouts": 4
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "kirill marchenko": {
        "name": "Kirill\u00a0Marchenko",
        "team": "NYI",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 185.7,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.86,
                        "shot_assists_per_60": 0.58,
                        "total_shot_contributions_per_60": 1.44,
                        "chances_per_60": 0.87,
                        "chance_assists_per_60": 0.48
                },
                "passing": {
                        "high_danger_assists_per_60": 0.62
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.77,
                        "rush_offense_per_60": 0.41,
                        "shots_off_hd_passes_per_60": 0.82
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.87,
                        "controlled_entry_percent": 0.46,
                        "controlled_entry_with_chance_percent": 0.18
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.58,
                        "retrievals_per_60": 2.94,
                        "successful_retrieval_percent": 0.75,
                        "exits_per_60": 0.31,
                        "botched_retrievals_per_60": -1.76
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "kent johnson": {
        "name": "Kent\u00a0Johnson",
        "team": "NYR",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 153.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.59,
                        "shot_assists_per_60": 1.02,
                        "total_shot_contributions_per_60": 1.61,
                        "chances_per_60": 0.45,
                        "chance_assists_per_60": 0.93
                },
                "passing": {
                        "high_danger_assists_per_60": 1.22
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.81,
                        "rush_offense_per_60": 0.19,
                        "shots_off_hd_passes_per_60": 0.53
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.65,
                        "controlled_entry_percent": 0.42,
                        "controlled_entry_with_chance_percent": 0.25
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.12,
                        "retrievals_per_60": 2.29,
                        "successful_retrieval_percent": 0.78,
                        "exits_per_60": 0.38,
                        "botched_retrievals_per_60": -3.13
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "james van_riemsdyk": {
        "name": "James\u00a0van Riemsdyk",
        "team": "OTT",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 121.7,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.65,
                        "shot_assists_per_60": 1.01,
                        "total_shot_contributions_per_60": 1.66,
                        "chances_per_60": 0.66,
                        "chance_assists_per_60": 1.12
                },
                "passing": {
                        "high_danger_assists_per_60": 1.05
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.57,
                        "rush_offense_per_60": 0.37,
                        "shots_off_hd_passes_per_60": 0.52
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.95,
                        "controlled_entry_percent": 0.38,
                        "controlled_entry_with_chance_percent": 0.25
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.28,
                        "retrievals_per_60": 1.95,
                        "successful_retrieval_percent": 0.73,
                        "exits_per_60": 0.13,
                        "botched_retrievals_per_60": -2.12
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jake christiansen": {
        "name": "Jake\u00a0Christiansen",
        "team": "PHI",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 103.6,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.14,
                        "shot_assists_per_60": 0.36,
                        "total_shot_contributions_per_60": 0.5,
                        "chances_per_60": 0.1,
                        "chance_assists_per_60": 0.35
                },
                "passing": {
                        "high_danger_assists_per_60": 0.41
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.13,
                        "rush_offense_per_60": 0.08,
                        "shots_off_hd_passes_per_60": 0.14
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.75,
                        "controlled_entry_percent": 0.28,
                        "controlled_entry_with_chance_percent": 0.16
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.81,
                        "retrievals_per_60": 3.17,
                        "successful_retrieval_percent": 0.58,
                        "exits_per_60": 0.12,
                        "botched_retrievals_per_60": -3.05
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "ivan provorov": {
        "name": "Ivan\u00a0Provorov",
        "team": "PIT",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 125.4,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.926,
                        "goals_against_average": 3.06,
                        "wins": 33,
                        "shutouts": 5
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "dmitri voronkov": {
        "name": "Dmitri\u00a0Voronkov",
        "team": "SJS",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 181.3,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.87,
                        "shot_assists_per_60": 0.51,
                        "total_shot_contributions_per_60": 1.38,
                        "chances_per_60": 0.9,
                        "chance_assists_per_60": 0.57
                },
                "passing": {
                        "high_danger_assists_per_60": 0.47
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.84,
                        "rush_offense_per_60": 0.59,
                        "shots_off_hd_passes_per_60": 0.66
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.8,
                        "controlled_entry_percent": 0.54,
                        "controlled_entry_with_chance_percent": 0.32
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.2,
                        "retrievals_per_60": 1.94,
                        "successful_retrieval_percent": 0.71,
                        "exits_per_60": 0.2,
                        "botched_retrievals_per_60": -2.94
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "dante fabbro": {
        "name": "Dante\u00a0Fabbro",
        "team": "SEA",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 109.8,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.05,
                        "shot_assists_per_60": 1.0,
                        "total_shot_contributions_per_60": 2.05,
                        "chances_per_60": 1.35,
                        "chance_assists_per_60": 1.18
                },
                "passing": {
                        "high_danger_assists_per_60": 0.88
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.18,
                        "rush_offense_per_60": 0.35,
                        "shots_off_hd_passes_per_60": 0.89
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.8,
                        "controlled_entry_percent": 0.37,
                        "controlled_entry_with_chance_percent": 0.2
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.57,
                        "retrievals_per_60": 2.78,
                        "successful_retrieval_percent": 0.65,
                        "exits_per_60": 0.11,
                        "botched_retrievals_per_60": -3.84
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "damon severson": {
        "name": "Damon\u00a0Severson",
        "team": "STL",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 141.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.79,
                        "shot_assists_per_60": 0.54,
                        "total_shot_contributions_per_60": 2.33,
                        "chances_per_60": 1.37,
                        "chance_assists_per_60": 0.48
                },
                "passing": {
                        "high_danger_assists_per_60": 0.45
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.7,
                        "rush_offense_per_60": 0.8,
                        "shots_off_hd_passes_per_60": 1.36
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.65,
                        "controlled_entry_percent": 0.42,
                        "controlled_entry_with_chance_percent": 0.22
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.36,
                        "retrievals_per_60": 1.52,
                        "successful_retrieval_percent": 0.66,
                        "exits_per_60": 0.32,
                        "botched_retrievals_per_60": -2.58
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "cole sillinger": {
        "name": "Cole\u00a0Sillinger",
        "team": "TBL",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 134.2,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.21,
                        "shot_assists_per_60": 0.54,
                        "total_shot_contributions_per_60": 0.75,
                        "chances_per_60": 0.19,
                        "chance_assists_per_60": 0.48
                },
                "passing": {
                        "high_danger_assists_per_60": 0.48
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.26,
                        "rush_offense_per_60": 0.1,
                        "shots_off_hd_passes_per_60": 0.17
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.74,
                        "controlled_entry_percent": 0.37,
                        "controlled_entry_with_chance_percent": 0.22
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 4.25,
                        "retrievals_per_60": 4.3,
                        "successful_retrieval_percent": 0.55,
                        "exits_per_60": 0.13,
                        "botched_retrievals_per_60": -1.67
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "adam fantilli": {
        "name": "Adam\u00a0Fantilli",
        "team": "TOR",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 191.1,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.915,
                        "goals_against_average": 2.61,
                        "wins": 18,
                        "shutouts": 6
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "william carrier": {
        "name": "William\u00a0Carrier",
        "team": "VAN",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 192.0,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.03,
                        "shot_assists_per_60": 0.85,
                        "total_shot_contributions_per_60": 1.88,
                        "chances_per_60": 1.05,
                        "chance_assists_per_60": 1.13
                },
                "passing": {
                        "high_danger_assists_per_60": 0.83
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.12,
                        "rush_offense_per_60": 0.62,
                        "shots_off_hd_passes_per_60": 0.96
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.43,
                        "controlled_entry_percent": 0.52,
                        "controlled_entry_with_chance_percent": 0.15
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.62,
                        "retrievals_per_60": 1.63,
                        "successful_retrieval_percent": 0.56,
                        "exits_per_60": 0.26,
                        "botched_retrievals_per_60": -2.95
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "tyson jost": {
        "name": "Tyson\u00a0Jost",
        "team": "VGK",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 107.8,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.02,
                        "shot_assists_per_60": 0.73,
                        "total_shot_contributions_per_60": 1.75,
                        "chances_per_60": 1.23,
                        "chance_assists_per_60": 0.72
                },
                "passing": {
                        "high_danger_assists_per_60": 0.79
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.9,
                        "rush_offense_per_60": 0.67,
                        "shots_off_hd_passes_per_60": 1.1
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.6,
                        "controlled_entry_percent": 0.63,
                        "controlled_entry_with_chance_percent": 0.27
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.01,
                        "retrievals_per_60": 2.77,
                        "successful_retrieval_percent": 0.73,
                        "exits_per_60": 0.33,
                        "botched_retrievals_per_60": -3.85
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "shayne gostisbehere": {
        "name": "Shayne\u00a0Gostisbehere",
        "team": "WSH",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 182.2,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.63,
                        "shot_assists_per_60": 0.72,
                        "total_shot_contributions_per_60": 2.35,
                        "chances_per_60": 1.54,
                        "chance_assists_per_60": 0.94
                },
                "passing": {
                        "high_danger_assists_per_60": 0.59
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.58,
                        "rush_offense_per_60": 1.24,
                        "shots_off_hd_passes_per_60": 1.56
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.3,
                        "controlled_entry_percent": 0.32,
                        "controlled_entry_with_chance_percent": 0.27
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.95,
                        "retrievals_per_60": 2.41,
                        "successful_retrieval_percent": 0.83,
                        "exits_per_60": 0.34,
                        "botched_retrievals_per_60": -2.39
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "seth jarvis": {
        "name": "Seth\u00a0Jarvis",
        "team": "WPG",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 139.1,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.17,
                        "shot_assists_per_60": 0.7,
                        "total_shot_contributions_per_60": 0.87,
                        "chances_per_60": 0.19,
                        "chance_assists_per_60": 0.67
                },
                "passing": {
                        "high_danger_assists_per_60": 0.77
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.17,
                        "rush_offense_per_60": 0.12,
                        "shots_off_hd_passes_per_60": 0.18
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.74,
                        "controlled_entry_percent": 0.36,
                        "controlled_entry_with_chance_percent": 0.25
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.55,
                        "retrievals_per_60": 3.17,
                        "successful_retrieval_percent": 0.64,
                        "exits_per_60": 0.35,
                        "botched_retrievals_per_60": -3.07
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "sebastian aho": {
        "name": "Sebastian\u00a0Aho",
        "team": "ANA",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 178.7,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.905,
                        "goals_against_average": 2.07,
                        "wins": 18,
                        "shutouts": 2
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "sean walker": {
        "name": "Sean\u00a0Walker",
        "team": "ARI",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 120.7,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.71,
                        "shot_assists_per_60": 1.15,
                        "total_shot_contributions_per_60": 1.86,
                        "chances_per_60": 0.69,
                        "chance_assists_per_60": 1.55
                },
                "passing": {
                        "high_danger_assists_per_60": 1.16
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.9,
                        "rush_offense_per_60": 0.56,
                        "shots_off_hd_passes_per_60": 0.72
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.38,
                        "controlled_entry_percent": 0.59,
                        "controlled_entry_with_chance_percent": 0.27
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.64,
                        "retrievals_per_60": 2.58,
                        "successful_retrieval_percent": 0.67,
                        "exits_per_60": 0.31,
                        "botched_retrievals_per_60": -3.2
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jordan staal": {
        "name": "Jordan\u00a0Staal",
        "team": "BOS",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 183.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.95,
                        "shot_assists_per_60": 0.89,
                        "total_shot_contributions_per_60": 1.84,
                        "chances_per_60": 0.83,
                        "chance_assists_per_60": 0.83
                },
                "passing": {
                        "high_danger_assists_per_60": 0.94
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.28,
                        "rush_offense_per_60": 0.56,
                        "shots_off_hd_passes_per_60": 0.94
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.16,
                        "controlled_entry_percent": 0.28,
                        "controlled_entry_with_chance_percent": 0.28
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.38,
                        "retrievals_per_60": 2.55,
                        "successful_retrieval_percent": 0.78,
                        "exits_per_60": 0.18,
                        "botched_retrievals_per_60": -2.15
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jordan martinook": {
        "name": "Jordan\u00a0Martinook",
        "team": "BUF",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 131.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.65,
                        "shot_assists_per_60": 0.46,
                        "total_shot_contributions_per_60": 1.11,
                        "chances_per_60": 0.63,
                        "chance_assists_per_60": 0.46
                },
                "passing": {
                        "high_danger_assists_per_60": 0.38
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.74,
                        "rush_offense_per_60": 0.3,
                        "shots_off_hd_passes_per_60": 0.48
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.87,
                        "controlled_entry_percent": 0.58,
                        "controlled_entry_with_chance_percent": 0.34
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.03,
                        "retrievals_per_60": 2.85,
                        "successful_retrieval_percent": 0.65,
                        "exits_per_60": 0.37,
                        "botched_retrievals_per_60": -2.06
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jesperi kotkaniemi": {
        "name": "Jesperi\u00a0Kotkaniemi",
        "team": "CGY",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 113.0,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.15,
                        "shot_assists_per_60": 0.41,
                        "total_shot_contributions_per_60": 0.56,
                        "chances_per_60": 0.19,
                        "chance_assists_per_60": 0.49
                },
                "passing": {
                        "high_danger_assists_per_60": 0.37
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.13,
                        "rush_offense_per_60": 0.07,
                        "shots_off_hd_passes_per_60": 0.16
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.46,
                        "controlled_entry_percent": 0.34,
                        "controlled_entry_with_chance_percent": 0.32
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.65,
                        "retrievals_per_60": 3.53,
                        "successful_retrieval_percent": 0.75,
                        "exits_per_60": 0.38,
                        "botched_retrievals_per_60": -2.68
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jalen chatfield": {
        "name": "Jalen\u00a0Chatfield",
        "team": "CAR",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 166.1,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.904,
                        "goals_against_average": 3.06,
                        "wins": 13,
                        "shutouts": 0
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jackson blake": {
        "name": "Jackson\u00a0Blake",
        "team": "CHI",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 176.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.1,
                        "shot_assists_per_60": 0.86,
                        "total_shot_contributions_per_60": 1.96,
                        "chances_per_60": 1.41,
                        "chance_assists_per_60": 0.85
                },
                "passing": {
                        "high_danger_assists_per_60": 0.99
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.15,
                        "rush_offense_per_60": 0.54,
                        "shots_off_hd_passes_per_60": 0.9
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.06,
                        "controlled_entry_percent": 0.53,
                        "controlled_entry_with_chance_percent": 0.22
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.88,
                        "retrievals_per_60": 1.75,
                        "successful_retrieval_percent": 0.78,
                        "exits_per_60": 0.19,
                        "botched_retrievals_per_60": -2.8
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jack roslovic": {
        "name": "Jack\u00a0Roslovic",
        "team": "COL",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 149.8,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.12,
                        "shot_assists_per_60": 0.56,
                        "total_shot_contributions_per_60": 1.68,
                        "chances_per_60": 1.08,
                        "chance_assists_per_60": 0.58
                },
                "passing": {
                        "high_danger_assists_per_60": 0.52
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.15,
                        "rush_offense_per_60": 0.74,
                        "shots_off_hd_passes_per_60": 0.98
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.79,
                        "controlled_entry_percent": 0.48,
                        "controlled_entry_with_chance_percent": 0.33
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.7,
                        "retrievals_per_60": 1.77,
                        "successful_retrieval_percent": 0.64,
                        "exits_per_60": 0.33,
                        "botched_retrievals_per_60": -2.05
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jaccob slavin": {
        "name": "Jaccob\u00a0Slavin",
        "team": "CBJ",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 110.6,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.17,
                        "shot_assists_per_60": 0.62,
                        "total_shot_contributions_per_60": 1.79,
                        "chances_per_60": 1.49,
                        "chance_assists_per_60": 0.61
                },
                "passing": {
                        "high_danger_assists_per_60": 0.7
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.94,
                        "rush_offense_per_60": 0.5,
                        "shots_off_hd_passes_per_60": 0.89
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.38,
                        "controlled_entry_percent": 0.36,
                        "controlled_entry_with_chance_percent": 0.27
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.77,
                        "retrievals_per_60": 2.82,
                        "successful_retrieval_percent": 0.62,
                        "exits_per_60": 0.36,
                        "botched_retrievals_per_60": -1.82
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "eric robinson": {
        "name": "Eric\u00a0Robinson",
        "team": "DAL",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 129.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.63,
                        "shot_assists_per_60": 0.43,
                        "total_shot_contributions_per_60": 1.06,
                        "chances_per_60": 0.61,
                        "chance_assists_per_60": 0.35
                },
                "passing": {
                        "high_danger_assists_per_60": 0.46
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.61,
                        "rush_offense_per_60": 0.32,
                        "shots_off_hd_passes_per_60": 0.64
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.6,
                        "controlled_entry_percent": 0.57,
                        "controlled_entry_with_chance_percent": 0.31
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.52,
                        "retrievals_per_60": 4.17,
                        "successful_retrieval_percent": 0.76,
                        "exits_per_60": 0.36,
                        "botched_retrievals_per_60": -3.85
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "dmitry orlov": {
        "name": "Dmitry\u00a0Orlov",
        "team": "DET",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 136.8,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.902,
                        "goals_against_average": 2.51,
                        "wins": 10,
                        "shutouts": 4
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "brent burns": {
        "name": "Brent\u00a0Burns",
        "team": "EDM",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 172.6,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.15,
                        "shot_assists_per_60": 0.97,
                        "total_shot_contributions_per_60": 2.12,
                        "chances_per_60": 1.13,
                        "chance_assists_per_60": 1.1
                },
                "passing": {
                        "high_danger_assists_per_60": 1.14
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.21,
                        "rush_offense_per_60": 0.86,
                        "shots_off_hd_passes_per_60": 1.02
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.85,
                        "controlled_entry_percent": 0.65,
                        "controlled_entry_with_chance_percent": 0.2
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.31,
                        "retrievals_per_60": 2.41,
                        "successful_retrieval_percent": 0.77,
                        "exits_per_60": 0.2,
                        "botched_retrievals_per_60": -2.72
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "andrei svechnikov": {
        "name": "Andrei\u00a0Svechnikov",
        "team": "FLA",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 124.8,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.14,
                        "shot_assists_per_60": 0.41,
                        "total_shot_contributions_per_60": 1.55,
                        "chances_per_60": 1.33,
                        "chance_assists_per_60": 0.49
                },
                "passing": {
                        "high_danger_assists_per_60": 0.38
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.17,
                        "rush_offense_per_60": 0.86,
                        "shots_off_hd_passes_per_60": 0.92
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.02,
                        "controlled_entry_percent": 0.41,
                        "controlled_entry_with_chance_percent": 0.15
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.24,
                        "retrievals_per_60": 2.48,
                        "successful_retrieval_percent": 0.65,
                        "exits_per_60": 0.31,
                        "botched_retrievals_per_60": -2.34
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "zach benson": {
        "name": "Zach\u00a0Benson",
        "team": "LAK",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 172.6,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.91,
                        "shot_assists_per_60": 1.13,
                        "total_shot_contributions_per_60": 2.04,
                        "chances_per_60": 0.68,
                        "chance_assists_per_60": 1.27
                },
                "passing": {
                        "high_danger_assists_per_60": 1.02
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.88,
                        "rush_offense_per_60": 0.29,
                        "shots_off_hd_passes_per_60": 0.83
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.09,
                        "controlled_entry_percent": 0.6,
                        "controlled_entry_with_chance_percent": 0.32
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.89,
                        "retrievals_per_60": 2.17,
                        "successful_retrieval_percent": 0.58,
                        "exits_per_60": 0.37,
                        "botched_retrievals_per_60": -1.57
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "tage thompson": {
        "name": "Tage\u00a0Thompson",
        "team": "MIN",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 173.7,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.26,
                        "shot_assists_per_60": 0.59,
                        "total_shot_contributions_per_60": 0.85,
                        "chances_per_60": 0.28,
                        "chance_assists_per_60": 0.78
                },
                "passing": {
                        "high_danger_assists_per_60": 0.51
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.33,
                        "rush_offense_per_60": 0.17,
                        "shots_off_hd_passes_per_60": 0.28
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.46,
                        "controlled_entry_percent": 0.46,
                        "controlled_entry_with_chance_percent": 0.28
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.26,
                        "retrievals_per_60": 3.85,
                        "successful_retrieval_percent": 0.64,
                        "exits_per_60": 0.23,
                        "botched_retrievals_per_60": -1.88
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "sam lafferty": {
        "name": "Sam\u00a0Lafferty",
        "team": "MTL",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 131.0,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.922,
                        "goals_against_average": 3.42,
                        "wins": 14,
                        "shutouts": 6
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "ryan mcleod": {
        "name": "Ryan\u00a0McLeod",
        "team": "NSH",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 167.2,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.57,
                        "shot_assists_per_60": 0.59,
                        "total_shot_contributions_per_60": 2.16,
                        "chances_per_60": 1.55,
                        "chance_assists_per_60": 0.59
                },
                "passing": {
                        "high_danger_assists_per_60": 0.5
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.57,
                        "rush_offense_per_60": 0.97,
                        "shots_off_hd_passes_per_60": 1.69
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.62,
                        "controlled_entry_percent": 0.36,
                        "controlled_entry_with_chance_percent": 0.29
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.87,
                        "retrievals_per_60": 1.74,
                        "successful_retrieval_percent": 0.68,
                        "exits_per_60": 0.31,
                        "botched_retrievals_per_60": -1.6
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "rasmus dahlin": {
        "name": "Rasmus\u00a0Dahlin",
        "team": "NJD",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 137.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.6,
                        "shot_assists_per_60": 0.71,
                        "total_shot_contributions_per_60": 1.31,
                        "chances_per_60": 0.64,
                        "chance_assists_per_60": 0.61
                },
                "passing": {
                        "high_danger_assists_per_60": 0.61
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.59,
                        "rush_offense_per_60": 0.25,
                        "shots_off_hd_passes_per_60": 0.43
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.61,
                        "controlled_entry_percent": 0.45,
                        "controlled_entry_with_chance_percent": 0.16
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.77,
                        "retrievals_per_60": 1.62,
                        "successful_retrieval_percent": 0.78,
                        "exits_per_60": 0.37,
                        "botched_retrievals_per_60": -2.35
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "peyton krebs": {
        "name": "Peyton\u00a0Krebs",
        "team": "NYI",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 192.1,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.37,
                        "shot_assists_per_60": 0.5,
                        "total_shot_contributions_per_60": 1.87,
                        "chances_per_60": 1.24,
                        "chance_assists_per_60": 0.67
                },
                "passing": {
                        "high_danger_assists_per_60": 0.56
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.11,
                        "rush_offense_per_60": 0.5,
                        "shots_off_hd_passes_per_60": 1.19
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.41,
                        "controlled_entry_percent": 0.61,
                        "controlled_entry_with_chance_percent": 0.22
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.57,
                        "retrievals_per_60": 2.72,
                        "successful_retrieval_percent": 0.79,
                        "exits_per_60": 0.31,
                        "botched_retrievals_per_60": -2.81
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "owen power": {
        "name": "Owen\u00a0Power",
        "team": "NYR",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 138.3,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.21,
                        "shot_assists_per_60": 0.86,
                        "total_shot_contributions_per_60": 1.07,
                        "chances_per_60": 0.17,
                        "chance_assists_per_60": 0.85
                },
                "passing": {
                        "high_danger_assists_per_60": 0.89
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.25,
                        "rush_offense_per_60": 0.08,
                        "shots_off_hd_passes_per_60": 0.2
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.8,
                        "controlled_entry_percent": 0.3,
                        "controlled_entry_with_chance_percent": 0.2
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 4.58,
                        "retrievals_per_60": 3.83,
                        "successful_retrieval_percent": 0.67,
                        "exits_per_60": 0.16,
                        "botched_retrievals_per_60": -2.33
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "mattias samuelsson": {
        "name": "Mattias\u00a0Samuelsson",
        "team": "OTT",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 183.2,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.916,
                        "goals_against_average": 2.4,
                        "wins": 27,
                        "shutouts": 6
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jordan greenway": {
        "name": "Jordan\u00a0Greenway",
        "team": "PHI",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 157.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.77,
                        "shot_assists_per_60": 0.82,
                        "total_shot_contributions_per_60": 1.59,
                        "chances_per_60": 0.75,
                        "chance_assists_per_60": 0.82
                },
                "passing": {
                        "high_danger_assists_per_60": 0.77
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.83,
                        "rush_offense_per_60": 0.26,
                        "shots_off_hd_passes_per_60": 0.7
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.89,
                        "controlled_entry_percent": 0.34,
                        "controlled_entry_with_chance_percent": 0.32
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.37,
                        "retrievals_per_60": 2.82,
                        "successful_retrieval_percent": 0.6,
                        "exits_per_60": 0.4,
                        "botched_retrievals_per_60": -2.78
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jj peterka": {
        "name": "JJ\u00a0Peterka",
        "team": "PIT",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 155.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.45,
                        "shot_assists_per_60": 0.47,
                        "total_shot_contributions_per_60": 1.92,
                        "chances_per_60": 1.06,
                        "chance_assists_per_60": 0.58
                },
                "passing": {
                        "high_danger_assists_per_60": 0.55
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 2.01,
                        "rush_offense_per_60": 0.83,
                        "shots_off_hd_passes_per_60": 1.06
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.65,
                        "controlled_entry_percent": 0.33,
                        "controlled_entry_with_chance_percent": 0.33
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.42,
                        "retrievals_per_60": 2.76,
                        "successful_retrieval_percent": 0.83,
                        "exits_per_60": 0.18,
                        "botched_retrievals_per_60": -3.49
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jiri kulich": {
        "name": "Jiri\u00a0Kulich",
        "team": "SJS",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 145.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.29,
                        "shot_assists_per_60": 0.68,
                        "total_shot_contributions_per_60": 1.97,
                        "chances_per_60": 1.68,
                        "chance_assists_per_60": 0.93
                },
                "passing": {
                        "high_danger_assists_per_60": 0.76
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.55,
                        "rush_offense_per_60": 0.49,
                        "shots_off_hd_passes_per_60": 0.94
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.29,
                        "controlled_entry_percent": 0.53,
                        "controlled_entry_with_chance_percent": 0.19
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.95,
                        "retrievals_per_60": 1.68,
                        "successful_retrieval_percent": 0.83,
                        "exits_per_60": 0.13,
                        "botched_retrievals_per_60": -2.63
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jason zucker": {
        "name": "Jason\u00a0Zucker",
        "team": "SEA",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 137.2,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.49,
                        "shot_assists_per_60": 0.23,
                        "total_shot_contributions_per_60": 0.72,
                        "chances_per_60": 0.6,
                        "chance_assists_per_60": 0.29
                },
                "passing": {
                        "high_danger_assists_per_60": 0.27
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.66,
                        "rush_offense_per_60": 0.35,
                        "shots_off_hd_passes_per_60": 0.53
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.45,
                        "controlled_entry_percent": 0.37,
                        "controlled_entry_with_chance_percent": 0.17
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.76,
                        "retrievals_per_60": 3.54,
                        "successful_retrieval_percent": 0.61,
                        "exits_per_60": 0.16,
                        "botched_retrievals_per_60": -3.37
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jacob bryson": {
        "name": "Jacob\u00a0Bryson",
        "team": "STL",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 137.3,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.916,
                        "goals_against_average": 2.66,
                        "wins": 20,
                        "shutouts": 4
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jack quinn": {
        "name": "Jack\u00a0Quinn",
        "team": "TBL",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 158.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.54,
                        "shot_assists_per_60": 0.59,
                        "total_shot_contributions_per_60": 1.13,
                        "chances_per_60": 0.65,
                        "chance_assists_per_60": 0.68
                },
                "passing": {
                        "high_danger_assists_per_60": 0.69
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.65,
                        "rush_offense_per_60": 0.2,
                        "shots_off_hd_passes_per_60": 0.46
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.25,
                        "controlled_entry_percent": 0.49,
                        "controlled_entry_with_chance_percent": 0.32
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.98,
                        "retrievals_per_60": 2.69,
                        "successful_retrieval_percent": 0.56,
                        "exits_per_60": 0.21,
                        "botched_retrievals_per_60": -3.28
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "henri jokiharju": {
        "name": "Henri\u00a0Jokiharju",
        "team": "TOR",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 177.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.16,
                        "shot_assists_per_60": 0.68,
                        "total_shot_contributions_per_60": 1.84,
                        "chances_per_60": 1.17,
                        "chance_assists_per_60": 0.78
                },
                "passing": {
                        "high_danger_assists_per_60": 0.78
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.14,
                        "rush_offense_per_60": 0.56,
                        "shots_off_hd_passes_per_60": 1.15
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.23,
                        "controlled_entry_percent": 0.58,
                        "controlled_entry_with_chance_percent": 0.27
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.07,
                        "retrievals_per_60": 2.07,
                        "successful_retrieval_percent": 0.77,
                        "exits_per_60": 0.35,
                        "botched_retrievals_per_60": -2.27
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "dylan cozens": {
        "name": "Dylan\u00a0Cozens",
        "team": "VAN",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 189.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.53,
                        "shot_assists_per_60": 0.59,
                        "total_shot_contributions_per_60": 2.12,
                        "chances_per_60": 1.91,
                        "chance_assists_per_60": 0.62
                },
                "passing": {
                        "high_danger_assists_per_60": 0.55
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.85,
                        "rush_offense_per_60": 0.67,
                        "shots_off_hd_passes_per_60": 1.53
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.3,
                        "controlled_entry_percent": 0.46,
                        "controlled_entry_with_chance_percent": 0.21
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.68,
                        "retrievals_per_60": 1.9,
                        "successful_retrieval_percent": 0.73,
                        "exits_per_60": 0.14,
                        "botched_retrievals_per_60": -2.25
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "connor clifton": {
        "name": "Connor\u00a0Clifton",
        "team": "VGK",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 118.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.51,
                        "shot_assists_per_60": 0.63,
                        "total_shot_contributions_per_60": 1.14,
                        "chances_per_60": 0.42,
                        "chance_assists_per_60": 0.54
                },
                "passing": {
                        "high_danger_assists_per_60": 0.75
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.58,
                        "rush_offense_per_60": 0.28,
                        "shots_off_hd_passes_per_60": 0.53
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.34,
                        "controlled_entry_percent": 0.55,
                        "controlled_entry_with_chance_percent": 0.18
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.36,
                        "retrievals_per_60": 4.14,
                        "successful_retrieval_percent": 0.57,
                        "exits_per_60": 0.36,
                        "botched_retrievals_per_60": -2.19
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "bowen byram": {
        "name": "Bowen\u00a0Byram",
        "team": "WSH",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 143.9,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.924,
                        "goals_against_average": 3.33,
                        "wins": 29,
                        "shutouts": 6
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "beck malenstyn": {
        "name": "Beck\u00a0Malenstyn",
        "team": "WPG",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 160.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.46,
                        "shot_assists_per_60": 0.65,
                        "total_shot_contributions_per_60": 2.11,
                        "chances_per_60": 1.73,
                        "chance_assists_per_60": 0.9
                },
                "passing": {
                        "high_danger_assists_per_60": 0.72
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.87,
                        "rush_offense_per_60": 0.46,
                        "shots_off_hd_passes_per_60": 1.52
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.66,
                        "controlled_entry_percent": 0.27,
                        "controlled_entry_with_chance_percent": 0.19
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.47,
                        "retrievals_per_60": 1.56,
                        "successful_retrieval_percent": 0.66,
                        "exits_per_60": 0.36,
                        "botched_retrievals_per_60": -3.71
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "alex tuch": {
        "name": "Alex\u00a0Tuch",
        "team": "ANA",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 109.1,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.13,
                        "shot_assists_per_60": 0.64,
                        "total_shot_contributions_per_60": 1.77,
                        "chances_per_60": 1.46,
                        "chance_assists_per_60": 0.84
                },
                "passing": {
                        "high_danger_assists_per_60": 0.6
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.32,
                        "rush_offense_per_60": 0.38,
                        "shots_off_hd_passes_per_60": 1.05
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.46,
                        "controlled_entry_percent": 0.32,
                        "controlled_entry_with_chance_percent": 0.25
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.13,
                        "retrievals_per_60": 2.3,
                        "successful_retrieval_percent": 0.71,
                        "exits_per_60": 0.36,
                        "botched_retrievals_per_60": -1.71
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "trent frederic": {
        "name": "Trent\u00a0Frederic",
        "team": "ARI",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 132.3,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.54,
                        "shot_assists_per_60": 0.58,
                        "total_shot_contributions_per_60": 2.12,
                        "chances_per_60": 1.62,
                        "chance_assists_per_60": 0.54
                },
                "passing": {
                        "high_danger_assists_per_60": 0.57
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.65,
                        "rush_offense_per_60": 0.97,
                        "shots_off_hd_passes_per_60": 1.32
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.18,
                        "controlled_entry_percent": 0.39,
                        "controlled_entry_with_chance_percent": 0.2
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.86,
                        "retrievals_per_60": 2.6,
                        "successful_retrieval_percent": 0.61,
                        "exits_per_60": 0.26,
                        "botched_retrievals_per_60": -2.59
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "pavel zacha": {
        "name": "Pavel\u00a0Zacha",
        "team": "BOS",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 107.8,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.16,
                        "shot_assists_per_60": 0.72,
                        "total_shot_contributions_per_60": 0.88,
                        "chances_per_60": 0.19,
                        "chance_assists_per_60": 0.62
                },
                "passing": {
                        "high_danger_assists_per_60": 0.86
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.18,
                        "rush_offense_per_60": 0.1,
                        "shots_off_hd_passes_per_60": 0.14
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.8,
                        "controlled_entry_percent": 0.36,
                        "controlled_entry_with_chance_percent": 0.28
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.79,
                        "retrievals_per_60": 3.27,
                        "successful_retrieval_percent": 0.73,
                        "exits_per_60": 0.35,
                        "botched_retrievals_per_60": -2.31
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "nikita zadorov": {
        "name": "Nikita\u00a0Zadorov",
        "team": "BUF",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 154.5,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.929,
                        "goals_against_average": 2.32,
                        "wins": 23,
                        "shutouts": 3
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "morgan geekie": {
        "name": "Morgan\u00a0Geekie",
        "team": "CGY",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 101.7,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.56,
                        "shot_assists_per_60": 0.99,
                        "total_shot_contributions_per_60": 1.55,
                        "chances_per_60": 0.72,
                        "chance_assists_per_60": 0.83
                },
                "passing": {
                        "high_danger_assists_per_60": 0.91
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.67,
                        "rush_offense_per_60": 0.37,
                        "shots_off_hd_passes_per_60": 0.48
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.5,
                        "controlled_entry_percent": 0.34,
                        "controlled_entry_with_chance_percent": 0.15
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.06,
                        "retrievals_per_60": 2.31,
                        "successful_retrieval_percent": 0.61,
                        "exits_per_60": 0.33,
                        "botched_retrievals_per_60": -1.52
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "mason lohrei": {
        "name": "Mason\u00a0Lohrei",
        "team": "CAR",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 127.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.3,
                        "shot_assists_per_60": 0.94,
                        "total_shot_contributions_per_60": 2.24,
                        "chances_per_60": 1.34,
                        "chance_assists_per_60": 0.95
                },
                "passing": {
                        "high_danger_assists_per_60": 0.78
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.75,
                        "rush_offense_per_60": 0.61,
                        "shots_off_hd_passes_per_60": 1.43
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.91,
                        "controlled_entry_percent": 0.5,
                        "controlled_entry_with_chance_percent": 0.2
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.67,
                        "retrievals_per_60": 2.55,
                        "successful_retrieval_percent": 0.72,
                        "exits_per_60": 0.17,
                        "botched_retrievals_per_60": -1.61
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "mark kastelic": {
        "name": "Mark\u00a0Kastelic",
        "team": "CHI",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 130.1,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.01,
                        "shot_assists_per_60": 0.48,
                        "total_shot_contributions_per_60": 1.49,
                        "chances_per_60": 1.01,
                        "chance_assists_per_60": 0.6
                },
                "passing": {
                        "high_danger_assists_per_60": 0.57
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.99,
                        "rush_offense_per_60": 0.43,
                        "shots_off_hd_passes_per_60": 0.82
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.17,
                        "controlled_entry_percent": 0.54,
                        "controlled_entry_with_chance_percent": 0.26
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.57,
                        "retrievals_per_60": 2.5,
                        "successful_retrieval_percent": 0.79,
                        "exits_per_60": 0.37,
                        "botched_retrievals_per_60": -2.52
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "justin brazeau": {
        "name": "Justin\u00a0Brazeau",
        "team": "COL",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 149.2,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.16,
                        "shot_assists_per_60": 0.67,
                        "total_shot_contributions_per_60": 0.83,
                        "chances_per_60": 0.21,
                        "chance_assists_per_60": 0.73
                },
                "passing": {
                        "high_danger_assists_per_60": 0.77
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.18,
                        "rush_offense_per_60": 0.05,
                        "shots_off_hd_passes_per_60": 0.13
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.55,
                        "controlled_entry_percent": 0.52,
                        "controlled_entry_with_chance_percent": 0.35
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.85,
                        "retrievals_per_60": 3.53,
                        "successful_retrieval_percent": 0.65,
                        "exits_per_60": 0.29,
                        "botched_retrievals_per_60": -2.34
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jordan oesterle": {
        "name": "Jordan\u00a0Oesterle",
        "team": "CBJ",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 174.6,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.902,
                        "goals_against_average": 2.68,
                        "wins": 36,
                        "shutouts": 3
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "john beecher": {
        "name": "John\u00a0Beecher",
        "team": "DAL",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 144.7,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.79,
                        "shot_assists_per_60": 1.14,
                        "total_shot_contributions_per_60": 1.93,
                        "chances_per_60": 0.88,
                        "chance_assists_per_60": 1.44
                },
                "passing": {
                        "high_danger_assists_per_60": 0.96
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.66,
                        "rush_offense_per_60": 0.41,
                        "shots_off_hd_passes_per_60": 0.63
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.3,
                        "controlled_entry_percent": 0.26,
                        "controlled_entry_with_chance_percent": 0.18
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.6,
                        "retrievals_per_60": 2.71,
                        "successful_retrieval_percent": 0.65,
                        "exits_per_60": 0.16,
                        "botched_retrievals_per_60": -3.31
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "elias lindholm": {
        "name": "Elias\u00a0Lindholm",
        "team": "DET",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 118.3,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.71,
                        "shot_assists_per_60": 0.97,
                        "total_shot_contributions_per_60": 1.68,
                        "chances_per_60": 0.53,
                        "chance_assists_per_60": 0.8
                },
                "passing": {
                        "high_danger_assists_per_60": 1.01
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.88,
                        "rush_offense_per_60": 0.32,
                        "shots_off_hd_passes_per_60": 0.74
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.12,
                        "controlled_entry_percent": 0.47,
                        "controlled_entry_with_chance_percent": 0.17
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.75,
                        "retrievals_per_60": 2.96,
                        "successful_retrieval_percent": 0.79,
                        "exits_per_60": 0.23,
                        "botched_retrievals_per_60": -1.97
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "david pastrnak": {
        "name": "David\u00a0Pastrnak",
        "team": "EDM",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 126.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.66,
                        "shot_assists_per_60": 0.64,
                        "total_shot_contributions_per_60": 1.3,
                        "chances_per_60": 0.63,
                        "chance_assists_per_60": 0.63
                },
                "passing": {
                        "high_danger_assists_per_60": 0.69
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.76,
                        "rush_offense_per_60": 0.46,
                        "shots_off_hd_passes_per_60": 0.7
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.4,
                        "controlled_entry_percent": 0.65,
                        "controlled_entry_with_chance_percent": 0.33
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.07,
                        "retrievals_per_60": 2.02,
                        "successful_retrieval_percent": 0.73,
                        "exits_per_60": 0.2,
                        "botched_retrievals_per_60": -1.98
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "cole koepke": {
        "name": "Cole\u00a0Koepke",
        "team": "FLA",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 127.5,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.67,
                        "shot_assists_per_60": 0.85,
                        "total_shot_contributions_per_60": 1.52,
                        "chances_per_60": 0.8,
                        "chance_assists_per_60": 1.18
                },
                "passing": {
                        "high_danger_assists_per_60": 0.72
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.68,
                        "rush_offense_per_60": 0.31,
                        "shots_off_hd_passes_per_60": 0.58
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.45,
                        "controlled_entry_percent": 0.26,
                        "controlled_entry_with_chance_percent": 0.19
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.54,
                        "retrievals_per_60": 4.2,
                        "successful_retrieval_percent": 0.69,
                        "exits_per_60": 0.25,
                        "botched_retrievals_per_60": -3.15
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "charlie mcavoy": {
        "name": "Charlie\u00a0McAvoy",
        "team": "LAK",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 193.2,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.909,
                        "goals_against_average": 2.82,
                        "wins": 40,
                        "shutouts": 0
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "charlie coyle": {
        "name": "Charlie\u00a0Coyle",
        "team": "MIN",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 187.8,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.31,
                        "shot_assists_per_60": 0.87,
                        "total_shot_contributions_per_60": 2.18,
                        "chances_per_60": 1.13,
                        "chance_assists_per_60": 0.87
                },
                "passing": {
                        "high_danger_assists_per_60": 0.86
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.33,
                        "rush_offense_per_60": 0.89,
                        "shots_off_hd_passes_per_60": 1.19
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.59,
                        "controlled_entry_percent": 0.3,
                        "controlled_entry_with_chance_percent": 0.25
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.06,
                        "retrievals_per_60": 2.36,
                        "successful_retrieval_percent": 0.61,
                        "exits_per_60": 0.12,
                        "botched_retrievals_per_60": -1.97
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "brandon carlo": {
        "name": "Brandon\u00a0Carlo",
        "team": "MTL",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 157.1,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.09,
                        "shot_assists_per_60": 1.0,
                        "total_shot_contributions_per_60": 2.09,
                        "chances_per_60": 0.94,
                        "chance_assists_per_60": 1.35
                },
                "passing": {
                        "high_danger_assists_per_60": 0.87
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.22,
                        "rush_offense_per_60": 0.65,
                        "shots_off_hd_passes_per_60": 0.92
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.2,
                        "controlled_entry_percent": 0.41,
                        "controlled_entry_with_chance_percent": 0.26
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.38,
                        "retrievals_per_60": 1.64,
                        "successful_retrieval_percent": 0.8,
                        "exits_per_60": 0.34,
                        "botched_retrievals_per_60": -3.32
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "brad marchand": {
        "name": "Brad\u00a0Marchand",
        "team": "NSH",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 162.8,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.27,
                        "shot_assists_per_60": 0.72,
                        "total_shot_contributions_per_60": 1.99,
                        "chances_per_60": 1.54,
                        "chance_assists_per_60": 0.67
                },
                "passing": {
                        "high_danger_assists_per_60": 0.77
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.22,
                        "rush_offense_per_60": 0.73,
                        "shots_off_hd_passes_per_60": 1.36
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.31,
                        "controlled_entry_percent": 0.61,
                        "controlled_entry_with_chance_percent": 0.17
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.42,
                        "retrievals_per_60": 2.32,
                        "successful_retrieval_percent": 0.83,
                        "exits_per_60": 0.31,
                        "botched_retrievals_per_60": -2.48
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "andrew peeke": {
        "name": "Andrew\u00a0Peeke",
        "team": "NJD",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 128.0,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.71,
                        "shot_assists_per_60": 0.72,
                        "total_shot_contributions_per_60": 1.43,
                        "chances_per_60": 0.54,
                        "chance_assists_per_60": 0.64
                },
                "passing": {
                        "high_danger_assists_per_60": 0.68
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.69,
                        "rush_offense_per_60": 0.27,
                        "shots_off_hd_passes_per_60": 0.55
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.32,
                        "controlled_entry_percent": 0.42,
                        "controlled_entry_with_chance_percent": 0.32
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.92,
                        "retrievals_per_60": 2.9,
                        "successful_retrieval_percent": 0.57,
                        "exits_per_60": 0.37,
                        "botched_retrievals_per_60": -2.15
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "troy terry": {
        "name": "Troy\u00a0Terry",
        "team": "NYI",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 155.9,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.915,
                        "goals_against_average": 3.46,
                        "wins": 42,
                        "shutouts": 0
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "trevor zegras": {
        "name": "Trevor\u00a0Zegras",
        "team": "NYR",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 140.3,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.78,
                        "shot_assists_per_60": 0.92,
                        "total_shot_contributions_per_60": 1.7,
                        "chances_per_60": 0.86,
                        "chance_assists_per_60": 0.91
                },
                "passing": {
                        "high_danger_assists_per_60": 1.04
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.77,
                        "rush_offense_per_60": 0.56,
                        "shots_off_hd_passes_per_60": 0.7
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.88,
                        "controlled_entry_percent": 0.27,
                        "controlled_entry_with_chance_percent": 0.32
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.7,
                        "retrievals_per_60": 2.89,
                        "successful_retrieval_percent": 0.77,
                        "exits_per_60": 0.12,
                        "botched_retrievals_per_60": -3.48
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "ryan strome": {
        "name": "Ryan\u00a0Strome",
        "team": "OTT",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 157.8,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.45,
                        "shot_assists_per_60": 0.48,
                        "total_shot_contributions_per_60": 1.93,
                        "chances_per_60": 1.24,
                        "chance_assists_per_60": 0.51
                },
                "passing": {
                        "high_danger_assists_per_60": 0.45
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.31,
                        "rush_offense_per_60": 1.08,
                        "shots_off_hd_passes_per_60": 1.12
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.51,
                        "controlled_entry_percent": 0.64,
                        "controlled_entry_with_chance_percent": 0.24
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.67,
                        "retrievals_per_60": 1.78,
                        "successful_retrieval_percent": 0.76,
                        "exits_per_60": 0.36,
                        "botched_retrievals_per_60": -2.76
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "robby fabbri": {
        "name": "Robby\u00a0Fabbri",
        "team": "PHI",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 126.9,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.12,
                        "shot_assists_per_60": 0.95,
                        "total_shot_contributions_per_60": 2.07,
                        "chances_per_60": 0.97,
                        "chance_assists_per_60": 1.1
                },
                "passing": {
                        "high_danger_assists_per_60": 1.05
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.46,
                        "rush_offense_per_60": 0.83,
                        "shots_off_hd_passes_per_60": 1.03
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.02,
                        "controlled_entry_percent": 0.32,
                        "controlled_entry_with_chance_percent": 0.35
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.57,
                        "retrievals_per_60": 2.76,
                        "successful_retrieval_percent": 0.78,
                        "exits_per_60": 0.26,
                        "botched_retrievals_per_60": -2.48
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "radko gudas": {
        "name": "Radko\u00a0Gudas",
        "team": "PIT",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 191.0,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.11,
                        "shot_assists_per_60": 0.61,
                        "total_shot_contributions_per_60": 0.72,
                        "chances_per_60": 0.08,
                        "chance_assists_per_60": 0.71
                },
                "passing": {
                        "high_danger_assists_per_60": 0.66
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.15,
                        "rush_offense_per_60": 0.03,
                        "shots_off_hd_passes_per_60": 0.12
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.67,
                        "controlled_entry_percent": 0.46,
                        "controlled_entry_with_chance_percent": 0.19
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.67,
                        "retrievals_per_60": 3.04,
                        "successful_retrieval_percent": 0.79,
                        "exits_per_60": 0.38,
                        "botched_retrievals_per_60": -3.29
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "pavel mintyukov": {
        "name": "Pavel\u00a0Mintyukov",
        "team": "SJS",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 192.0,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.906,
                        "goals_against_average": 2.05,
                        "wins": 30,
                        "shutouts": 6
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "olen zellweger": {
        "name": "Olen\u00a0Zellweger",
        "team": "SEA",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 104.1,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.06,
                        "shot_assists_per_60": 0.44,
                        "total_shot_contributions_per_60": 1.5,
                        "chances_per_60": 1.02,
                        "chance_assists_per_60": 0.36
                },
                "passing": {
                        "high_danger_assists_per_60": 0.5
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.96,
                        "rush_offense_per_60": 0.7,
                        "shots_off_hd_passes_per_60": 1.05
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.87,
                        "controlled_entry_percent": 0.58,
                        "controlled_entry_with_chance_percent": 0.18
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.53,
                        "retrievals_per_60": 1.56,
                        "successful_retrieval_percent": 0.78,
                        "exits_per_60": 0.38,
                        "botched_retrievals_per_60": -2.37
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "mason mctavish": {
        "name": "Mason\u00a0McTavish",
        "team": "STL",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 135.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.51,
                        "shot_assists_per_60": 0.62,
                        "total_shot_contributions_per_60": 1.13,
                        "chances_per_60": 0.5,
                        "chance_assists_per_60": 0.83
                },
                "passing": {
                        "high_danger_assists_per_60": 0.73
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.71,
                        "rush_offense_per_60": 0.31,
                        "shots_off_hd_passes_per_60": 0.39
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.3,
                        "controlled_entry_percent": 0.52,
                        "controlled_entry_with_chance_percent": 0.25
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.85,
                        "retrievals_per_60": 2.1,
                        "successful_retrieval_percent": 0.8,
                        "exits_per_60": 0.22,
                        "botched_retrievals_per_60": -3.35
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "leo carlsson": {
        "name": "Leo\u00a0Carlsson",
        "team": "TBL",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 134.2,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.62,
                        "shot_assists_per_60": 0.85,
                        "total_shot_contributions_per_60": 2.47,
                        "chances_per_60": 1.46,
                        "chance_assists_per_60": 1.14
                },
                "passing": {
                        "high_danger_assists_per_60": 0.85
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 2.09,
                        "rush_offense_per_60": 1.1,
                        "shots_off_hd_passes_per_60": 1.7
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.69,
                        "controlled_entry_percent": 0.4,
                        "controlled_entry_with_chance_percent": 0.25
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.9,
                        "retrievals_per_60": 1.96,
                        "successful_retrieval_percent": 0.6,
                        "exits_per_60": 0.3,
                        "botched_retrievals_per_60": -2.85
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jansen harkins": {
        "name": "Jansen\u00a0Harkins",
        "team": "TOR",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 124.2,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.18,
                        "shot_assists_per_60": 0.89,
                        "total_shot_contributions_per_60": 1.07,
                        "chances_per_60": 0.15,
                        "chance_assists_per_60": 1.2
                },
                "passing": {
                        "high_danger_assists_per_60": 0.82
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.21,
                        "rush_offense_per_60": 0.07,
                        "shots_off_hd_passes_per_60": 0.19
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.55,
                        "controlled_entry_percent": 0.32,
                        "controlled_entry_with_chance_percent": 0.15
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.91,
                        "retrievals_per_60": 3.42,
                        "successful_retrieval_percent": 0.6,
                        "exits_per_60": 0.15,
                        "botched_retrievals_per_60": -2.79
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jacob trouba": {
        "name": "Jacob\u00a0Trouba",
        "team": "VAN",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 130.3,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.929,
                        "goals_against_average": 2.14,
                        "wins": 41,
                        "shutouts": 2
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "jackson lacombe": {
        "name": "Jackson\u00a0LaCombe",
        "team": "VGK",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 151.7,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.98,
                        "shot_assists_per_60": 0.68,
                        "total_shot_contributions_per_60": 1.66,
                        "chances_per_60": 0.77,
                        "chance_assists_per_60": 0.63
                },
                "passing": {
                        "high_danger_assists_per_60": 0.6
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.8,
                        "rush_offense_per_60": 0.39,
                        "shots_off_hd_passes_per_60": 0.71
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.15,
                        "controlled_entry_percent": 0.43,
                        "controlled_entry_with_chance_percent": 0.25
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.12,
                        "retrievals_per_60": 1.93,
                        "successful_retrieval_percent": 0.83,
                        "exits_per_60": 0.1,
                        "botched_retrievals_per_60": -2.81
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "isac lundestrom": {
        "name": "Isac\u00a0Lundestrom",
        "team": "WSH",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 175.1,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.24,
                        "shot_assists_per_60": 0.73,
                        "total_shot_contributions_per_60": 1.97,
                        "chances_per_60": 1.11,
                        "chance_assists_per_60": 0.71
                },
                "passing": {
                        "high_danger_assists_per_60": 0.7
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.18,
                        "rush_offense_per_60": 0.94,
                        "shots_off_hd_passes_per_60": 1.08
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.66,
                        "controlled_entry_percent": 0.42,
                        "controlled_entry_with_chance_percent": 0.2
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.07,
                        "retrievals_per_60": 2.23,
                        "successful_retrieval_percent": 0.74,
                        "exits_per_60": 0.27,
                        "botched_retrievals_per_60": -3.71
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "frank vatrano": {
        "name": "Frank\u00a0Vatrano",
        "team": "WPG",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 113.0,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.68,
                        "shot_assists_per_60": 1.08,
                        "total_shot_contributions_per_60": 1.76,
                        "chances_per_60": 0.84,
                        "chance_assists_per_60": 1.36
                },
                "passing": {
                        "high_danger_assists_per_60": 1.2
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.67,
                        "rush_offense_per_60": 0.33,
                        "shots_off_hd_passes_per_60": 0.57
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.36,
                        "controlled_entry_percent": 0.57,
                        "controlled_entry_with_chance_percent": 0.21
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.99,
                        "retrievals_per_60": 1.82,
                        "successful_retrieval_percent": 0.71,
                        "exits_per_60": 0.16,
                        "botched_retrievals_per_60": -2.58
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "drew helleson": {
        "name": "Drew\u00a0Helleson",
        "team": "ANA",
        "position": "D",
        "year": "2024-25",
        "5v5_toi": 181.8,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.41,
                        "shot_assists_per_60": 0.4,
                        "total_shot_contributions_per_60": 0.81,
                        "chances_per_60": 0.32,
                        "chance_assists_per_60": 0.36
                },
                "passing": {
                        "high_danger_assists_per_60": 0.47
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 0.45,
                        "rush_offense_per_60": 0.14,
                        "shots_off_hd_passes_per_60": 0.32
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.43,
                        "controlled_entry_percent": 0.29,
                        "controlled_entry_with_chance_percent": 0.25
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 3.66,
                        "retrievals_per_60": 3.57,
                        "successful_retrieval_percent": 0.77,
                        "exits_per_60": 0.14,
                        "botched_retrievals_per_60": -3.86
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "cutter gauthier": {
        "name": "Cutter\u00a0Gauthier",
        "team": "ARI",
        "position": "G",
        "year": "2024-25",
        "5v5_toi": 194.5,
        "stats": {
                "goalie_stats": {
                        "save_percentage": 0.908,
                        "goals_against_average": 2.51,
                        "wins": 30,
                        "shutouts": 1
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "brian dumoulin": {
        "name": "Brian\u00a0Dumoulin",
        "team": "BOS",
        "position": "C",
        "year": "2024-25",
        "5v5_toi": 170.7,
        "stats": {
                "general_offense": {
                        "shots_per_60": 0.85,
                        "shot_assists_per_60": 0.92,
                        "total_shot_contributions_per_60": 1.77,
                        "chances_per_60": 1.04,
                        "chance_assists_per_60": 1.21
                },
                "passing": {
                        "high_danger_assists_per_60": 0.93
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.08,
                        "rush_offense_per_60": 0.54,
                        "shots_off_hd_passes_per_60": 0.71
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.24,
                        "controlled_entry_percent": 0.57,
                        "controlled_entry_with_chance_percent": 0.19
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.15,
                        "retrievals_per_60": 2.42,
                        "successful_retrieval_percent": 0.78,
                        "exits_per_60": 0.16,
                        "botched_retrievals_per_60": -3.29
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "brett leason": {
        "name": "Brett\u00a0Leason",
        "team": "BUF",
        "position": "LW",
        "year": "2024-25",
        "5v5_toi": 177.4,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.34,
                        "shot_assists_per_60": 0.53,
                        "total_shot_contributions_per_60": 1.87,
                        "chances_per_60": 1.62,
                        "chance_assists_per_60": 0.7
                },
                "passing": {
                        "high_danger_assists_per_60": 0.63
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.49,
                        "rush_offense_per_60": 0.52,
                        "shots_off_hd_passes_per_60": 0.99
                },
                "zone_entries": {
                        "zone_entries_per_60": 1.33,
                        "controlled_entry_percent": 0.36,
                        "controlled_entry_with_chance_percent": 0.19
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 1.78,
                        "retrievals_per_60": 1.54,
                        "successful_retrieval_percent": 0.78,
                        "exits_per_60": 0.13,
                        "botched_retrievals_per_60": -3.31
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
    "alex killorn": {
        "name": "Alex\u00a0Killorn",
        "team": "CGY",
        "position": "RW",
        "year": "2024-25",
        "5v5_toi": 103.8,
        "stats": {
                "general_offense": {
                        "shots_per_60": 1.42,
                        "shot_assists_per_60": 0.78,
                        "total_shot_contributions_per_60": 2.2,
                        "chances_per_60": 1.62,
                        "chance_assists_per_60": 0.88
                },
                "passing": {
                        "high_danger_assists_per_60": 0.84
                },
                "offense_types": {
                        "cycle_forecheck_offense_per_60": 1.38,
                        "rush_offense_per_60": 0.79,
                        "shots_off_hd_passes_per_60": 1.21
                },
                "zone_entries": {
                        "zone_entries_per_60": 0.84,
                        "controlled_entry_percent": 0.4,
                        "controlled_entry_with_chance_percent": 0.2
                },
                "dz_retrievals_exits": {
                        "dz_puck_touches_per_60": 2.01,
                        "retrievals_per_60": 2.37,
                        "successful_retrieval_percent": 0.77,
                        "exits_per_60": 0.34,
                        "botched_retrievals_per_60": -3.66
                }
        },
        "source": "All Three Zones Project - REAL PLAYER LIST",
        "last_updated": "2024-25 Season"
},
}

def get_all_three_zones_player(player_name):
    """Get player data from All Three Zones database"""
    player_key = player_name.lower().replace(" ", "_").replace(".", "").replace("-", "_")
    return REAL_ALL_THREE_ZONES_PLAYERS.get(player_key)

def get_all_players():
    """Get all All Three Zones players"""
    return list(REAL_ALL_THREE_ZONES_PLAYERS.values())

def search_players(query):
    """Search players by name"""
    query = query.lower()
    results = []
    for player in REAL_ALL_THREE_ZONES_PLAYERS.values():
        if query in player["name"].lower():
            results.append(player)
    return results
