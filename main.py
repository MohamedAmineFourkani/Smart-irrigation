"""
main.py
─────────────────────────────────────────────────────────────────────────────
Smart Irrigation System — Entry Point

Usage
-----
    python main.py                          # train + live loop with random_forest
    python main.py --model decision_tree    # use decision tree
    python main.py --model xgboost_model    # use xgboost
    python main.py --skip-train             # skip training (use saved .pkl files)
"""

import argparse
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

MOROCCO_TZ = timezone(timedelta(hours=1))

# ── Make src/ importable ──────────────────────────────────────────────────────
SRC_DIR = Path(__file__).resolve().parent / "src"
sys.path.insert(0, str(SRC_DIR))

from config import LOOP_INTERVAL, FORECAST_REFRESH
from data_fetcher import load_data, fetch_live_data
from trainer import train_and_evaluate
from controller import IrrigationController
from forecaster import fetch_forecast, print_forecast
from cluster_trainer import train as train_clusters
import database as db

VALID_MODELS     = ("decision_tree", "random_forest", "xgboost_model")


# ─────────────────────────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description="Smart Irrigation System")
    p.add_argument(
        "--model",
        choices=VALID_MODELS,
        default="random_forest",
        help="AI model to use (default: random_forest)",
    )
    p.add_argument(
        "--skip-train",
        action="store_true",
        help="Skip model training and use existing .pkl files",
    )
    p.add_argument(
        "--train-clusters",
        action="store_true",
        help="Train NASA cluster models from data.csv and exit",
    )
    return p.parse_args()


# ─────────────────────────────────────────────────────────────────────────────
def run_live_loop(model_type: str):
    """
    Main live loop:
      - Fetches TTN soil sensor every 20 minutes      (Layer 2 + 3)
      - Refreshes 7-day forecast every 24 hours       (Layer 1)
      - Runs 3-layer decision engine on every tick
      - Saves every decision to SQLite database
    """

    print("\n" + "=" * 66)
    print(f"  🌱  Smart Irrigation System — LIVE MODE")
    print(f"  Active model    : [{model_type}]")
    print(f"  Sensor interval : every 20 minutes")
    print(f"  Forecast refresh: every 24 hours")
    print(f"  Database        : data/irrigation.db")
    print(f"  Press Ctrl+C to stop")
    print("=" * 66)

    # ── Initialise controller (fetches forecast at startup) ───────────────────
    controller         = IrrigationController(model_type=model_type, verbose=True)
    tick               = 0
    last_forecast_time = time.time()

    while True:
        tick += 1
        now = time.time()

        # ── Refresh forecast every 24 hours ───────────────────────────────────
        if now - last_forecast_time >= FORECAST_REFRESH:
            controller.refresh_forecast()
            last_forecast_time = now

        print(f"\n  🔄  Tick #{tick} — fetching live soil data from TTN...")

        try:
            # ── Fetch live soil reading ───────────────────────────────────────
            reading = fetch_live_data()

            # ── Check connection status ───────────────────────────────────────
            sensor_connected = reading.get("_valid", False)
            sensor_errors    = reading.get("_validation_errors", [])

            if not sensor_connected:
                error_msg = "; ".join(sensor_errors) or "Unknown fetch error"
                print(f"  ⚠️  Sensor/API issue: {error_msg}")
                db.save({
                    "timestamp": datetime.now(MOROCCO_TZ).isoformat(),
                    "decision_source": "SENSOR_OFFLINE",
                    "reason"         : f"Sensor offline: {error_msg}",
                    "pump_on"        : False,
                    "water_SOIL"     : None,
                    "temp_SOIL"      : None,
                    "conduct_SOIL"   : None,
                    "zone"           : "OFFLINE",
                    "ai_prediction"  : 0,
                    "ai_probability" : 0.0,
                    "strategic_cluster": controller.today_plan["cluster"],
                    "strategic_label"  : controller.today_plan["label"],
                    "strategic_power"  : controller.today_plan["power"],
                })
                print(f"  ⏳  Retrying in 20 minutes...")
                time.sleep(LOOP_INTERVAL)
                continue

            print(
                f"  📡  Sensor → "
                f"temp: {reading['temp_SOIL']}°C  "
                f"moisture: {reading['water_SOIL']}%  "
                f"conductivity: {reading['conduct_SOIL']} µS/cm"
            )

            # ── Run 3-layer decision ──────────────────────────────────────────
            record = controller.tick(reading, now=datetime.now(MOROCCO_TZ))

            # ── Save to database ──────────────────────────────────────────────
            db.save(record)
            print(f"  💾  Record saved to database.")

        except Exception as e:
            print(f"  ❌  Error: {e}")
            print(f"  ⏳  Retrying in 20 minutes...")

            # ── Log the error to DB ───────────────────────────────────────────
            db.save({
                "timestamp": datetime.now(MOROCCO_TZ).isoformat(),
                "decision_source": "ERROR",
                "reason"         : str(e),
                "pump_on"        : False,
            })

        # ── Summary stats every 5 ticks ───────────────────────────────────────
        if tick % 5 == 0:
            _print_summary()

        print(f"\n  ⏳  Next reading in 20 minutes — waiting...")
        time.sleep(LOOP_INTERVAL)


# ─────────────────────────────────────────────────────────────────────────────
def _print_summary():
    """Print a rolling summary every 5 ticks from the database."""
    df = db.fetch(limit=50)
    if df.empty:
        return

    print("\n" + "=" * 66)
    print(f"  📊  Rolling Summary (last {len(df)} ticks)")
    print("=" * 66)
    print(f"  Pump activated    : {df['pump_on'].sum()} times")
    print(f"  Avg moisture      : {df['water_SOIL'].mean():.2f}%")
    print(f"  Min moisture      : {df['water_SOIL'].min():.2f}%")
    print(f"  Decision breakdown:")
    for source, cnt in df["decision_source"].value_counts().items():
        print(f"    {source:20s}: {cnt} ticks")
    print("=" * 66)


# ─────────────────────────────────────────────────────────────────────────────
def main():
    args = parse_args()

    # ── Step 0: Train cluster models if requested ─────────────────────────────
    if args.train_clusters:
        print("\n  🌍  Training NASA cluster models from data.csv...")
        train_clusters()
        print("\n  ✅  Cluster training complete. Run 'python main.py --skip-train' to start live loop.")
        return

    # ── Step 1: Initialise database ───────────────────────────────────────────
    print("\n  🗄️   Initialising database...")
    db.init()

    # ── Step 2: Train soil models on CSV (unless skipped) ─────────────────────
    if not args.skip_train:
        print("\n  📊  Training soil models on Soil_Moisture.csv...")
        print("  (irrigation_rf_model.pkl and scaler.pkl are pre-trained)\n")
        train_and_evaluate(verbose=True)
    else:
        print("\n  [--skip-train] Skipping training — using saved .pkl files.")

    # ── Step 3: Start 3-layer live loop ───────────────────────────────────────
    run_live_loop(args.model)


if __name__ == "__main__":
    main()