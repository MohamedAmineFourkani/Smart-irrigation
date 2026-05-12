"""
forecaster.py
─────────────────────────────────────────────────────────────────────────────
Strategic Layer — 7-day weather forecast + irrigation plan.
Uses Open-Meteo API + irrigation_rf_model.pkl + scaler.pkl
"""

import sys
from datetime import datetime
from pathlib import Path

import joblib
import requests
import pandas as pd

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"

# ── Cluster definitions ───────────────────────────────────────────────────────
CLUSTER_PLAN = {
    0: {"label": "DRY",  "emoji": "☀️ ", "frequency": 3, "power": "FULL"},
    1: {"label": "MILD", "emoji": "🌤️ ", "frequency": 2, "power": "HALF"},
    2: {"label": "WET",  "emoji": "🌧️ ", "frequency": 0, "power": "NONE"},
}

# ── Location (Morocco) ────────────────────────────────────────────────────────
LAT = 31.877705
LON = -8.314369


def fetch_forecast() -> pd.DataFrame:
    """Fetch 7-day forecast from Open-Meteo and return classified DataFrame."""

    # ── 1. Fetch from Open-Meteo ──────────────────────────────────────────────
    r = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude"               : LAT,
            "longitude"              : LON,
            "daily"                  : [
                "temperature_2m_max",
                "temperature_2m_min",
                "relative_humidity_2m_max",
                "wind_speed_10m_max",
                "precipitation_sum",
                "shortwave_radiation_sum",
                "surface_pressure_mean",
            ],
            "wind_speed_unit"        : "ms",
            "timezone"               : "Africa/Casablanca",
            "forecast_days"          : 7,
        },
    )
    r.raise_for_status()
    json_data = r.json()

    if "daily" not in json_data:
        raise ValueError("Open-Meteo returned no daily data.")

    # ── 2. Build DataFrame ────────────────────────────────────────────────────
    df = pd.DataFrame(json_data["daily"])
    df["surface_pressure_mean"] = df["surface_pressure_mean"] * 0.1  # hPa → kPa
    dates = pd.to_datetime(df["time"])

    X = df[[
        "temperature_2m_max",
        "relative_humidity_2m_max",
        "wind_speed_10m_max",
        "precipitation_sum",
        "shortwave_radiation_sum",
        "surface_pressure_mean",
    ]].copy()
    X.columns = ["temp", "humidity", "wind", "rain", "solar_rad", "pressure"]

    # ── 3. Scale + classify ───────────────────────────────────────────────────
    scaler   = joblib.load(MODELS_DIR / "scaler.pkl")
    rf_model = joblib.load(MODELS_DIR / "irrigation_rf_model.pkl")

    X_scaled     = scaler.transform(X)
    predictions  = rf_model.predict(X_scaled)

    # ── 4. Compute enhanced metrics ───────────────────────────────────────────
    LOW_HUMIDITY_THRESHOLD = 30  # percent
    humidity_max = df.get("relative_humidity_2m_max", pd.Series([None]*len(dates)))
    humidity_min = df.get("relative_humidity_2m_min", pd.Series([None]*len(dates)))
    temp_min     = df.get("temperature_2m_min",       pd.Series([None]*len(dates)))

    low_humidity_events = (humidity_max < LOW_HUMIDITY_THRESHOLD).astype(int).values

    # ── 5. Build results DataFrame ────────────────────────────────────────────
    results = pd.DataFrame({
        "date"                : dates,
        "cluster"             : predictions,
        "label"               : [CLUSTER_PLAN[c]["label"]     for c in predictions],
        "emoji"               : [CLUSTER_PLAN[c]["emoji"]     for c in predictions],
        "frequency"           : [CLUSTER_PLAN[c]["frequency"] for c in predictions],
        "power"               : [CLUSTER_PLAN[c]["power"]     for c in predictions],
        "temp_max"            : X["temp"].values,
        "temp_min"            : temp_min.values,
        "humidity_max"        : humidity_max.values,
        "humidity_min"        : humidity_min.values,
        "humidity_avg"        : X["humidity"].values,
        "low_humidity_event"  : low_humidity_events,
        "rain"                : X["rain"].values,
    })

    # ── Override to 0 irrigation if all 7 days are humid enough ───────────────
    if low_humidity_events.sum() == 0:
        results["frequency"] = 0
        results["power"]     = "NONE"
        results["label"]     = "WET"

    return results


def get_today_plan(forecast_df: pd.DataFrame) -> dict:
    """Extract today's strategic plan from the forecast DataFrame."""
    today = pd.Timestamp(datetime.utcnow().date())
    row   = forecast_df[forecast_df["date"] == today]

    if row.empty:
        # Default to first day if today not found
        row = forecast_df.iloc[[0]]

    r = row.iloc[0]
    return {
        "date"              : r["date"],
        "cluster"           : int(r["cluster"]),
        "label"             : r["label"],
        "emoji"             : r["emoji"],
        "frequency"         : int(r["frequency"]),
        "power"             : r["power"],
        "temp_max"          : float(r.get("temp_max", r.get("temp", 0))),
        "temp_min"          : float(r.get("temp_min", 0)),
        "humidity_max"      : float(r.get("humidity_max", r.get("humidity_avg", 0))),
        "humidity_min"      : float(r.get("humidity_min", 0)),
        "humidity_avg"      : float(r.get("humidity_avg", r.get("humidity", 0))),
        "low_humidity_event": bool(r.get("low_humidity_event", False)),
    }


def print_forecast(forecast_df: pd.DataFrame):
    """Pretty-print the 7-day forecast plan."""
    print("\n" + "=" * 72)
    print("  📅  7-Day Strategic Irrigation Forecast")
    print("=" * 72)
    for _, row in forecast_df.iterrows():
        low_flag = " !LOW" if row.get("low_humidity_event") else ""
        print(
            f"  {row['date'].strftime('%a %d %b')}  {row['emoji']}  "
            f"{row['label']:4s}  →  "
            f"{'x'+str(row['frequency'])+'/week':8s}  "
            f"Power: {row['power']:4s}  "
            f"| Temp: {row.get('temp_max', row.get('temp', 0)):.1f}°C  "
            f"Hum: {row.get('humidity_max', row.get('humidity_avg', 0)):.0f}%{low_flag}  "
            f"Rain: {row['rain']:.1f}mm"
        )
    print("=" * 72)


if __name__ == "__main__":
    df = fetch_forecast()
    print_forecast(df)
    print("\nToday's plan:", get_today_plan(df))