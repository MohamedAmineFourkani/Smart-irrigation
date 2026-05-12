"""Tests for IrrigationPlanner."""

import sys
from pathlib import Path
from datetime import datetime, timedelta

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))

from planner import IrrigationPlanner


def test_planner_irrigates_in_red_zone():
    pl = IrrigationPlanner(cycle_duration_min=10, cooldown_min=300, max_daily_minutes=60)
    now = datetime(2026, 5, 12, 8, 0, 0)
    result = pl.recommend(water_soil=10.0, ai_prediction=1, now=now)
    assert result["irrigate"] is True
    assert result["daily_used"] != "0m 00s"


def test_planner_blocks_in_green_zone():
    pl = IrrigationPlanner()
    result = pl.recommend(water_soil=30.0, ai_prediction=1)
    assert result["irrigate"] is False


def test_planner_cooldown():
    pl = IrrigationPlanner(cycle_duration_min=10, cooldown_min=300, max_daily_minutes=60)
    now = datetime(2026, 5, 12, 8, 0, 0)
    pl.recommend(water_soil=10.0, ai_prediction=1, now=now)
    result = pl.recommend(water_soil=10.0, ai_prediction=1, now=now + timedelta(minutes=5))
    assert result["irrigate"] is False  # cooldown active


def test_planner_cooldown_expires():
    pl = IrrigationPlanner(cycle_duration_min=10, cooldown_min=60, max_daily_minutes=60)
    now = datetime(2026, 5, 12, 8, 0, 0)
    pl.recommend(water_soil=10.0, ai_prediction=1, now=now)
    result = pl.recommend(water_soil=10.0, ai_prediction=1, now=now + timedelta(minutes=90))
    assert result["irrigate"] is True  # cooldown expired


def test_planner_daily_budget():
    pl = IrrigationPlanner(cycle_duration_min=10, cooldown_min=0, max_daily_minutes=15)
    now = datetime(2026, 5, 12, 8, 0, 0)
    r1 = pl.recommend(water_soil=10.0, ai_prediction=1, now=now)
    assert r1["irrigate"] is True
    r2 = pl.recommend(water_soil=10.0, ai_prediction=1, now=now + timedelta(minutes=5))
    assert r2["irrigate"] is False  # would exceed 15 min budget


def test_planner_budget_resets_daily():
    pl = IrrigationPlanner(cycle_duration_min=10, cooldown_min=0, max_daily_minutes=15)
    now = datetime(2026, 5, 12, 8, 0, 0)
    pl.recommend(water_soil=10.0, ai_prediction=1, now=now)
    next_day = datetime(2026, 5, 13, 8, 0, 0)
    r2 = pl.recommend(water_soil=10.0, ai_prediction=1, now=next_day)
    assert r2["irrigate"] is True  # budget reset


def test_planner_ai_disagrees():
    pl = IrrigationPlanner()
    result = pl.recommend(water_soil=10.0, ai_prediction=0)
    assert result["irrigate"] is False
    assert result["ai_agrees"] is False


def test_planner_orange_zone():
    pl = IrrigationPlanner()
    result = pl.recommend(water_soil=18.0, ai_prediction=1)
    assert result["irrigate"] is False


def test_planner_response_keys():
    pl = IrrigationPlanner()
    result = pl.recommend(water_soil=10.0, ai_prediction=1)
    for key in ("irrigate", "reason", "cooldown_remaining", "daily_used", "daily_budget"):
        assert key in result, f"Missing key: {key}"


if __name__ == "__main__":
    test_planner_irrigates_in_red_zone()
    test_planner_blocks_in_green_zone()
    test_planner_cooldown()
    test_planner_cooldown_expires()
    test_planner_daily_budget()
    test_planner_budget_resets_daily()
    test_planner_ai_disagrees()
    test_planner_orange_zone()
    test_planner_response_keys()
    print("ALL PLANNER TESTS PASSED")
