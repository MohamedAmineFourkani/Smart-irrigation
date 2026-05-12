"""
database.py
─────────────────────────────────────────────────────────────────────────────
SQLite abstraction layer — 3 functions only:
    init()        → create DB + table if not exists
    save(record)  → insert one tick result
    fetch()       → return full history as DataFrame
"""

import sqlite3
from pathlib import Path
from datetime import datetime
import pandas as pd

# ── DB location ───────────────────────────────────────────────────────────────
DB_PATH = Path(__file__).resolve().parent.parent / "data" / "irrigation.db"


# ─────────────────────────────────────────────────────────────────────────────
def init():
    """Create the database and table if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS irrigation_log (
            id                 INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp          TEXT,
            temp_SOIL          REAL,
            water_SOIL         REAL,
            conduct_SOIL       INTEGER,
            BatV               REAL,
            zone               TEXT,
            ai_prediction      INTEGER,
            ai_probability     REAL,
            strategic_cluster  INTEGER,
            strategic_label    TEXT,
            strategic_power    TEXT,
            pump_on            INTEGER,
            decision_source    TEXT,
            reason             TEXT,
            model              TEXT,
            cooldown_remaining TEXT,
            daily_used         TEXT,
            manual_remaining   TEXT
        )
    """)
    conn.commit()

    # ── Migrate: add missing columns (safe if already exist) ───────────────────
    new_columns = [
        "model TEXT",
        "cooldown_remaining TEXT",
        "daily_used TEXT",
        "manual_remaining TEXT",
    ]
    existing = [row[1] for row in cursor.execute("PRAGMA table_info(irrigation_log)")]
    for col_def in new_columns:
        col_name = col_def.split()[0]
        if col_name not in existing:
            cursor.execute(f"ALTER TABLE irrigation_log ADD COLUMN {col_def}")

    conn.commit()
    conn.close()
    print(f"  ✅  Database ready → {DB_PATH}")


# ─────────────────────────────────────────────────────────────────────────────
def save(record: dict):
    """Insert one tick record into the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO irrigation_log (
            timestamp, temp_SOIL, water_SOIL, conduct_SOIL, BatV,
            zone, ai_prediction, ai_probability,
            strategic_cluster, strategic_label, strategic_power,
            pump_on, decision_source, reason,
            model, cooldown_remaining, daily_used, manual_remaining
        ) VALUES (
            :timestamp, :temp_SOIL, :water_SOIL, :conduct_SOIL, :BatV,
            :zone, :ai_prediction, :ai_probability,
            :strategic_cluster, :strategic_label, :strategic_power,
            :pump_on, :decision_source, :reason,
            :model, :cooldown_remaining, :daily_used, :manual_remaining
        )
    """, {
        "timestamp"        : record.get("timestamp",
                                datetime.utcnow().isoformat()),
        "temp_SOIL"        : record.get("temp_SOIL"),
        "water_SOIL"       : record.get("water_SOIL"),
        "conduct_SOIL"     : record.get("conduct_SOIL"),
        "BatV"             : record.get("BatV"),
        "zone"             : record.get("zone"),
        "ai_prediction"    : int(record.get("ai_prediction", 0)),
        "ai_probability"   : record.get("ai_probability"),
        "strategic_cluster": record.get("strategic_cluster"),
        "strategic_label"  : record.get("strategic_label"),
        "strategic_power"  : record.get("strategic_power"),
        "pump_on"          : int(record.get("pump_on", 0)),
        "decision_source"  : record.get("decision_source"),
        "reason"           : record.get("reason"),
        "model"            : record.get("model"),
        "cooldown_remaining": record.get("cooldown_remaining"),
        "daily_used"       : record.get("daily_used"),
        "manual_remaining" : record.get("manual_remaining"),
    })
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────────────────────────────────────
def fetch(limit: int = None) -> pd.DataFrame:
    """
    Return irrigation history as a DataFrame.

    Parameters
    ----------
    limit : int, optional — return only the last N rows
    """
    conn = sqlite3.connect(DB_PATH)

    query = "SELECT * FROM irrigation_log ORDER BY timestamp DESC"
    if limit:
        query += f" LIMIT {limit}"

    df = pd.read_sql_query(query, conn)
    conn.close()

    # ── Convert types ─────────────────────────────────────────────────────────
    df["timestamp"] = pd.to_datetime(df["timestamp"], format='ISO8601')
    df["pump_on"]   = df["pump_on"].astype(bool)

    return df


# ─────────────────────────────────────────────────────────────────────────────
def fetch_latest() -> dict:
    """Return the single most recent record as a dict."""
    df = fetch(limit=1)
    if df.empty:
        return {}
    return df.iloc[0].to_dict()


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    init()
    print("Latest record:", fetch_latest())
    print(f"Total records: {len(fetch())}")