"""
data_fetcher.py
Loads the Soil_Moisture.csv, engineers features, and generates the target label.
"""

import pandas as pd
import numpy as np
from pathlib import Path


# ── Moisture zone thresholds ──────────────────────────────────────────────────
ZONE_RED    = 15.0   # < 15 %  → irrigation possible
ZONE_ORANGE = 20.0   # 15–20 % → warning / recommended
ZONE_GREEN  = 50.0   # 20–50 % → optimal
# > 50 %  → force pump OFF

FEATURE_COLS = ["temp_SOIL", "water_SOIL", "conduct_SOIL"]
TARGET_COL   = "Irrigation_Required"

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "Soil_Moisture.csv"


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
    """Fetch real-time soil reading from TTN (The Things Network)."""
    import requests
    import json

    API_KEY = "NNSXS.ASLLX336KBM2DC6FAHKTCJN7ADUMKCAEA3H5Z2Q.BQ2YBW3SCALTTURG4Q26CM6XRI3QYM544BZLIVWQMGEHL5R37PZQ"
    APP_ID  = "a8404180a75e149b"
    TTN_URL = f"https://eu1.cloud.thethings.network/api/v3/as/applications/{APP_ID}/packages/storage/uplink_message"

    r = requests.get(
        TTN_URL,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Accept"       : "application/json",
        },
        params={"limit": 1}   # latest message only
    )

    r.raise_for_status()

    # TTN returns one JSON object per line
    first_line  = r.text.strip().split("\n")[0]
    raw         = json.loads(first_line)
    payload     = raw["result"]["uplink_message"]["decoded_payload"]

    return {
        "temp_SOIL"    : float(payload["temp_SOIL"]),
        "water_SOIL"   : float(payload["water_SOIL"]),
        "conduct_SOIL" : int(payload["conduct_SOIL"]),
    }

if __name__ == "__main__":
    df = load_data()
    print(f"Dataset shape : {df.shape}")
    print(f"Irrigation required: {df[TARGET_COL].sum()} / {len(df)} rows")
    print(df.head())
