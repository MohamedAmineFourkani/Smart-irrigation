import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "irrigation.db"
conn = sqlite3.connect(DB_PATH)
conn.execute("DELETE FROM irrigation_log WHERE decision_source IN ('TEST', 'TEST_COOLDOWN')")
conn.commit()
print("Deleted test records:", conn.total_changes)
conn.close()
