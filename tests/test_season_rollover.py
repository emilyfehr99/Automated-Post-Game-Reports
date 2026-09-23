import datetime
from pathlib import Path
from utils.season_utils import (
    current_season_string,
    current_season_file_tag,
    get_team_stats_path,
    get_schedule_path,
)
from utils.playoff_context import is_playoff_game


def test_season_string_rollover():
    # Test October (regular season start)
    dt_oct = datetime.datetime(2027, 10, 15)
    assert current_season_string(dt_oct) == "20272028"
    assert current_season_file_tag(dt_oct) == "2027_2028"

    # Test February (mid season)
    dt_feb = datetime.datetime(2028, 2, 20)
    assert current_season_string(dt_feb) == "20272028"
    assert current_season_file_tag(dt_feb) == "2027_2028"

    # Test June (playoffs/finals)
    dt_jun = datetime.datetime(2028, 6, 10)
    assert current_season_string(dt_jun) == "20272028"
    assert current_season_file_tag(dt_jun) == "2027_2028"

    # Test July (season rollover)
    dt_jul = datetime.datetime(2028, 7, 1)
    assert current_season_string(dt_jul) == "20282029"
    assert current_season_file_tag(dt_jul) == "2028_2029"


def test_paths_resolved_dynamically():
    stats_p = get_team_stats_path()
    assert isinstance(stats_p, Path)
    assert stats_p.name.startswith("season_") and stats_p.name.endswith("_team_stats.json")

    sched_p = get_schedule_path()
    assert isinstance(sched_p, Path)
    assert sched_p.name.startswith("season_") and sched_p.name.endswith("_schedule.json")


def test_universal_playoff_game_detection():
    # Regular season format: YYYY02XXXX
    assert not is_playoff_game(2026020123)
    assert not is_playoff_game("2027020500")

    # Playoff format: YYYY03XXXX
    assert is_playoff_game(2026030111)
    assert is_playoff_game("2027030121")
    assert is_playoff_game(2028030214)
