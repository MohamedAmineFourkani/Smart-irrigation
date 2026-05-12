"""
config.py
Centralised configuration for the Smart Irrigation System.
All tunable thresholds live here -- edit once, apply everywhere.
"""

# ── Moisture zone thresholds (%) ──────────────────────────────────────────────
ZONE_RED    = 15.0   # < 15 %  → irrigation possible
ZONE_ORANGE = 20.0   # 15-20 % → warning zone
ZONE_GREEN  = 50.0   # 20-50 % → optimal

# ── Safety thresholds (%) ─────────────────────────────────────────────────────
EMERGENCY_THRESHOLD = 5.0    # < 5%   → immediate pump ON (bypass all layers)
WET_THRESHOLD       = 20.0   # > 20%  → safety veto, pump OFF (root rot prevention)

# ── Sensor validation ranges ──────────────────────────────────────────────────
SENSOR_RANGES = {
    "temp_SOIL":    {"min": -10.0, "max": 60.0,  "default": None},
    "water_SOIL":   {"min":   0.0, "max": 100.0, "default": None},
    "conduct_SOIL": {"min":   0.0, "max": 2000.0,"default": None},
    "BatV":         {"min":   0.0, "max": 5.0,   "default": None},
}

# ── TTN API retry ─────────────────────────────────────────────────────────────
TTN_RETRIES = 3
TTN_TIMEOUT = 15   # seconds per request
TTN_BACKOFF = 5    # seconds between retries

# ── Irrigation planner ────────────────────────────────────────────────────────
PLANNER_CYCLE_DURATION_MIN = 10    # minutes per irrigation cycle
PLANNER_COOLDOWN_MIN       = 300   # 5 hours between cycles
PLANNER_MAX_DAILY_MIN      = 60    # max total irrigation per day

# ── Manual control ────────────────────────────────────────────────────────────
MANUAL_PUMP_TIMEOUT_MIN = 30    # auto turn off pump after N minutes

# ── Live loop ─────────────────────────────────────────────────────────────────
LOOP_INTERVAL    = 20 * 60        # 20 minutes (seconds)
FORECAST_REFRESH = 24 * 60 * 60   # refresh forecast every 24 hours
