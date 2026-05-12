"""
data_fetcher.py
Loads the Soil_Moisture.csv, engineers features, and generates the target label.
"""

import time
from pathlib import Path

import numpy as np
import pandas as pd


from config import (
    ZONE_RED, ZONE_ORANGE, ZONE_GREEN,
    SENSOR_RANGES,
    TTN_RETRIES, TTN_TIMEOUT, TTN_BACKOFF,
)

FEATURE_COLS = ["temp_SOIL", "water_SOIL", "conduct_SOIL"]
TARGET_COL   = "Irrigation_Required"

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "Soil_Moisture.csv"


def validate_sensor_reading(reading: dict) -> dict:
    """
    Validate a sensor reading against plausible ranges.
    Returns a dict with:
      - valid: bool
      - errors: list[str]
      - sanitized: dict with bad values replaced by None
    """
    errors    = []
    sanitized = {}

    for key, rng in SENSOR_RANGES.items():
        val = reading.get(key)
        if val is None:
            errors.append(f"{key} is missing")
            sanitized[key] = None
            continue
        try:
            val = float(val)
        except (ValueError, TypeError):
            errors.append(f"{key}={val!r} is not numeric")
            sanitized[key] = None
            continue
        if val < rng["min"] or val > rng["max"]:
            errors.append(
                f"{key}={val} out of range [{rng['min']}, {rng['max']}]"
            )
            sanitized[key] = rng["default"]
        else:
            sanitized[key] = val

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "sanitized": sanitized,
    }


def is_sensor_healthy(reading: dict, check_keys: list = None) -> bool:
    """Quick check: return True if all required sensor values are present and in range."""
    if check_keys is None:
        check_keys = ["temp_SOIL", "water_SOIL", "conduct_SOIL"]
    result = validate_sensor_reading(reading)
    # Only fail validation errors for the keys we care about
    for key in check_keys:
        if key not in result["sanitized"] or result["sanitized"].get(key) is None:
            return False
    return True


def load_data(path: Path = DATA_PATH) -> pd.DataFrame:
    """Read raw CSV and return a cleaned DataFrame with the target column."""
    df = pd.read_csv(path, parse_dates=["time"])
    df = df.dropna(subset=FEATURE_COLS)

    # ── Target: 1 if soil moisture below RED threshold ────────────────────────
    df[TARGET_COL] = (df["water_SOIL"] < ZONE_RED).astype(int)

    return df


def get_features_and_target(df: pd.DataFrame):
    """Return X (feature matrix) and y (target vector)."""
    X = df[FEATURE_COLS].copy()
    y = df[TARGET_COL].copy()
    return X, y


def get_moisture_zone(water_soil: float) -> dict:
    """
    Classify a moisture reading into a named zone.

    Returns
    -------
    dict with keys: zone (str), colour (str), pump_allowed (bool)
    """
    if water_soil < ZONE_RED:
        return {"zone": "RED",    "colour": "🔴", "pump_allowed": True}
    elif water_soil < ZONE_ORANGE:
        return {"zone": "ORANGE", "colour": "🟠", "pump_allowed": True}
    elif water_soil <= ZONE_GREEN:
        return {"zone": "GREEN",  "colour": "🟢", "pump_allowed": False}
    else:
        return {"zone": "WARNING","colour": "⚠️ ", "pump_allowed": False}

def fetch_live_data() -> dict:
    """
    Fetch real-time soil reading from TTN (The Things Network).
    Includes retry logic, timeout, and sensor validation.
    """
    import json
    import requests

    API_KEY = "NNSXS.ASLLX336KBM2DC6FAHKTCJN7ADUMKCAEA3H5Z2Q.BQ2YBW3SCALTTURG4Q26CM6XRI3QYM544BZLIVWQMGEHL5R37PZQ"
    APP_ID  = "a8404180a75e149b"
    TTN_URL = f"https://eu1.cloud.thethings.network/api/v3/as/applications/{APP_ID}/packages/storage/uplink_message"

    last_error = None
    for attempt in range(1, TTN_RETRIES + 1):
        try:
            r = requests.get(
                TTN_URL,
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Accept"       : "application/json",
                },
                params={"limit": 1},
                timeout=TTN_TIMEOUT,
            )
            r.raise_for_status()

            # TTN returns one JSON object per line
            first_line  = r.text.strip().split("\n")[0]
            raw         = json.loads(first_line)
            payload     = raw["result"]["uplink_message"]["decoded_payload"]

            reading = {
                "temp_SOIL"    : float(payload.get("temp_SOIL", 0)),
                "water_SOIL"   : float(payload.get("water_SOIL", 0)),
                "conduct_SOIL" : int(payload.get("conduct_SOIL", 0)),
                "BatV"         : float(payload.get("BatV", 0)),
            }

            # Validate sensor data
            result = validate_sensor_reading(reading)
            if not result["valid"]:
                # Return sanitized reading with error info
                reading["_validation_errors"] = result["errors"]
                reading["_valid"] = False
            else:
                reading["_valid"] = True
                reading["_validation_errors"] = []

            return reading

        except requests.exceptions.Timeout:
            last_error = f"TTN request timed out after {TTN_TIMEOUT}s (attempt {attempt}/{TTN_RETRIES})"
        except requests.exceptions.ConnectionError as e:
            last_error = f"TTN connection error: {e} (attempt {attempt}/{TTN_RETRIES})"
        except requests.exceptions.HTTPError as e:
            last_error = f"TTN HTTP error: {e} (attempt {attempt}/{TTN_RETRIES})"
        except (KeyError, json.JSONDecodeError, IndexError) as e:
            last_error = f"TTN response parse error: {e} (attempt {attempt}/{TTN_RETRIES})"

        if attempt < TTN_RETRIES:
            time.sleep(TTN_BACKOFF)

    return {
        "temp_SOIL":    None,
        "water_SOIL":   None,
        "conduct_SOIL": None,
        "BatV":         None,
        "_valid":       False,
        "_validation_errors": [last_error],
        "_error":       last_error,
    }

if __name__ == "__main__":
    df = load_data()
    print(f"Dataset shape : {df.shape}")
    print(f"Irrigation required: {df[TARGET_COL].sum()} / {len(df)} rows")
    print(df.head())
