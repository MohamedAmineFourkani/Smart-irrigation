"""Insert sample data for dashboard testing."""

import random
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC))

from database import init, save

MOROCCO_TZ = timezone(timedelta(hours=1))
now = datetime.now(MOROCCO_TZ)

init()
for i in range(20):
    t = now - timedelta(hours=i * 2)
    save({
        "timestamp"          : t.isoformat(),
        "temp_SOIL"          : round(random.uniform(12, 35), 2),
        "water_SOIL"         : round(random.uniform(5, 45), 2),
        "conduct_SOIL"       : random.randint(100, 400),
        "zone"               : "RED" if i < 5 else "ORANGE" if i < 10 else "GREEN",
        "ai_prediction"      : 1 if i < 3 else 0,
        "ai_probability"     : round(random.uniform(0.7, 0.99), 4),
        "strategic_cluster"  : 0 if i < 5 else 1 if i < 10 else 2 if i < 15 else 3,
        "strategic_label"    : ["VERY_DRY","DRY","MILD","WET","VERY_WET"][i // 4],
        "strategic_power"    : ["FULL","FULL","HALF","LOW","NONE"][i // 4],
        "pump_on"            : 1 if i < 3 else 0,
        "decision_source"    : "CONSENSUS" if i < 3 else "MONITORING",
        "reason"             : "Seed data for dashboard",
        "cooldown_remaining" : "" if i >= 3 else "4h 20m",
        "daily_used"         : f"{i * 10}m / 1h 00m",
        "model"              : "random_forest",
    })

print(f"Inserted 20 test records")
