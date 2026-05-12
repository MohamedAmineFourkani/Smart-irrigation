"""Tests for sensor validation logic."""

import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))

from data_fetcher import validate_sensor_reading, is_sensor_healthy


def test_valid_reading():
    reading = {"temp_SOIL": 25.0, "water_SOIL": 30.0, "conduct_SOIL": 150, "BatV": 3.3}
    result = validate_sensor_reading(reading)
    assert result["valid"] is True
    assert len(result["errors"]) == 0
    assert is_sensor_healthy(reading) is True


def test_missing_key():
    reading = {"water_SOIL": 30.0, "conduct_SOIL": 150}
    result = validate_sensor_reading(reading)
    assert result["valid"] is False
    errors = " ".join(result["errors"])
    assert "temp_SOIL" in errors


def test_out_of_range_moisture():
    reading = {"temp_SOIL": 25.0, "water_SOIL": 120.0, "conduct_SOIL": 150, "BatV": 3.3}
    result = validate_sensor_reading(reading)
    assert result["valid"] is False
    errors = " ".join(result["errors"])
    assert "out of range" in errors
    assert result["sanitized"]["water_SOIL"] is None


def test_negative_moisture():
    reading = {"temp_SOIL": 25.0, "water_SOIL": -5.0, "conduct_SOIL": 150, "BatV": 3.3}
    result = validate_sensor_reading(reading)
    assert result["valid"] is False


def test_extreme_temp():
    reading = {"temp_SOIL": 100.0, "water_SOIL": 30.0, "conduct_SOIL": 150, "BatV": 3.3}
    result = validate_sensor_reading(reading)
    assert result["valid"] is False
    assert result["sanitized"]["temp_SOIL"] is None


def test_non_numeric_value():
    reading = {"temp_SOIL": "abc", "water_SOIL": 30.0, "conduct_SOIL": 150, "BatV": 3.3}
    result = validate_sensor_reading(reading)
    assert result["valid"] is False


def test_is_sensor_healthy_missing_critical():
    reading = {"temp_SOIL": 25.0, "water_SOIL": None, "conduct_SOIL": 150}
    assert is_sensor_healthy(reading) is False


def test_is_sensor_healthy_partial_check():
    reading = {"water_SOIL": 30.0}
    result = is_sensor_healthy(reading, check_keys=["water_SOIL"])
    assert result is True


def test_empty_reading():
    result = validate_sensor_reading({})
    assert result["valid"] is False
    assert len(result["errors"]) == 4  # all 4 keys missing


if __name__ == "__main__":
    test_valid_reading()
    test_missing_key()
    test_out_of_range_moisture()
    test_negative_moisture()
    test_extreme_temp()
    test_non_numeric_value()
    test_is_sensor_healthy_missing_critical()
    test_is_sensor_healthy_partial_check()
    test_empty_reading()
    print("ALL VALIDATION TESTS PASSED")
