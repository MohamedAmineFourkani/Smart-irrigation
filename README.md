# Smart Irrigation System

AI-driven hybrid control platform for automated irrigation using soil sensors, weather forecasts, and machine learning.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Smart Irrigation System                    │
├─────────────────────────────────────────────────────────────┤
│  Layer 1  │  Strategic  │  7-day weather forecast (Open-Meteo) │
│           │             │  → classified into DRY/MILD/WET      │
├───────────┼─────────────┼─────────────────────────────────────┤
│  Layer 2  │  Real-Time  │  TTN soil sensor thresholds          │
│           │             │  → emergency + safety veto           │
├───────────┼─────────────┼─────────────────────────────────────┤
│  Layer 3  │  AI Model   │  ML: decision_tree / random_forest  │
│           │             │  / xgboost confirmation              │
├───────────┼─────────────┼─────────────────────────────────────┤
│  Safety   │  Planner    │  Cooldown + daily water budget        │
├───────────┼─────────────┼─────────────────────────────────────┤
│  UI       │  Dashboard  │  Streamlit (charts, controls, logs)  │
└───────────┴─────────────┴─────────────────────────────────────┘
```

## Decision Priority

1. **Emergency** — moisture < 5% → pump ON (bypass all layers)
2. **Manual Override** — user force ON/OFF (auto-off after 30 min)
3. **Safety Veto** — moisture > 20% → pump OFF (root rot prevention)
4. **Strategic Skip** — forecast = WET/NONE → no irrigation planned
5. **Planner Veto** — cooldown active or daily budget exhausted
6. **Consensus** — all 3 layers agree → pump ON
7. **AI Veto** — soil dry but AI disagrees
8. **Monitoring** — orange zone (15-20%)
9. **Optimal** — no action needed

## Setup

```bash
# 1. Clone or cd into the project
cd smart_irrigation_project

# 2. Create and activate virtual environment (Python 3.10+)
python -m venv venv
venv\Scripts\Activate.ps1    # Windows
# source venv/bin/activate   # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt
```

## Usage

### Run the live system
```bash
python main.py                              # train + live loop
python main.py --model decision_tree        # use decision tree
python main.py --model xgboost_model        # use XGBoost
python main.py --skip-train                 # skip retraining
```

### Launch the dashboard
```bash
streamlit run dashboard/app.py
```

### Run individual modules
```bash
python src/trainer.py        # train models + view comparison
python src/forecaster.py     # fetch 7-day forecast
python src/predictor.py      # test predictions
python src/database.py       # init DB + view records
python test_ttn.py           # test TTN API connection
```

## Configuration

All tunable thresholds are in `src/config.py`:

| Parameter | Default | Description |
|---|---|---|
| `ZONE_RED` | 15% | Below this → irrigation possible |
| `ZONE_ORANGE` | 20% | Warning zone threshold |
| `ZONE_GREEN` | 50% | Optimal upper bound |
| `EMERGENCY_THRESHOLD` | 5% | Bypass all layers |
| `WET_THRESHOLD` | 20% | Safety veto (root rot) |
| `PLANNER_COOLDOWN_MIN` | 300 (5h) | Min between irrigation cycles |
| `PLANNER_MAX_DAILY_MIN` | 60 | Max irrigation per day |
| `MANUAL_PUMP_TIMEOUT_MIN` | 30 | Auto-off for manual override |
| `LOOP_INTERVAL` | 20 min | Sensor reading interval |
| `FORECAST_REFRESH` | 24h | Forecast refresh interval |

## Project Structure

```
smart_irrigation_project/
├── main.py              # Entry point
├── config.py            # All tunable parameters
├── src/
│   ├── controller.py    # 3-layer hybrid decision engine
│   ├── data_fetcher.py  # CSV loader + TTN API fetcher + validation
│   ├── database.py      # SQLite abstraction
│   ├── forecaster.py    # 7-day weather forecast + clustering
│   ├── planner.py       # Cooldown + daily budget + irrigation planning
│   ├── predictor.py     # Cached model inference
│   └── trainer.py       # Train DT/RF/XGBoost models
├── dashboard/
│   └── app.py           # Streamlit dashboard
├── models/              # Pre-trained .pkl files
├── data/                # Soil_Moisture.csv + irrigation.db
└── tests/               # Unit tests

```

## Data Storage

All irrigation decisions are stored in `data/irrigation.db` (SQLite):

- Timestamp, sensor readings, moisture zone
- Layer 1: strategic cluster/label/power
- Layer 3: AI prediction + probability
- Planner: cooldown remaining, daily water usage
- Final decision: pump state, source, reason

## Alerts

The dashboard shows alerts for:
- Low moisture (emergency <5%, warning <15%)
- High moisture (safety veto)
- Sensor/API offline
- Invalid sensor data
- Planner veto (cooldown/budget)
- Manual override active + remaining time
- Battery low
- Pump activation

Alerts are rate-limited (120s cooldown) to prevent spam.
