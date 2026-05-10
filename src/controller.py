"""
controller.py
─────────────────────────────────────────────────────────────────────────────
3-Layer Hybrid Decision Engine:
  Layer 1 — Strategic  : 7-day forecast (forecaster.py)
  Layer 2 — Real-Time  : TTN soil sensor thresholds
  Layer 3 — AI Model   : DT/RF/XGBoost confirmation
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Literal, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
from data_fetcher import get_moisture_zone, ZONE_RED, ZONE_ORANGE, ZONE_GREEN
from predictor import predict, predict_proba, ModelType
from planner import IrrigationPlanner
from forecaster import fetch_forecast, get_today_plan, print_forecast

PUMP_STATE = {"on": False}

# ── Thresholds ────────────────────────────────────────────────────────────────
EMERGENCY_THRESHOLD = 5.0    # < 5%  → emergency override, bypass all layers
WET_THRESHOLD       = 20.0   # > 20% → safety veto, pump OFF (root rot)

ModelChoice = Literal["decision_tree", "random_forest", "xgboost_model"]


class IrrigationController:
    """
    3-Layer Hybrid Irrigation Controller.

    Layer 1 — Strategic  : Weekly forecast cluster (Full / Half / None)
    Layer 2 — Real-Time  : Soil moisture safety veto
    Layer 3 — AI Model   : ML confirmation (DT / RF / XGBoost)
    """

    def __init__(
        self,
        model_type: ModelChoice = "random_forest",
        verbose: bool = True,
    ):
        self.model_type    = model_type
        self.verbose       = verbose
        self.planner       = IrrigationPlanner()
        self.audit_log     : list[dict] = []

        # ── Fetch strategic forecast once at startup ──────────────────────────
        print("\n  📡  Fetching 7-day strategic forecast...")
        self.forecast_df   = fetch_forecast()
        self.today_plan    = get_today_plan(self.forecast_df)
        if self.verbose:
            print_forecast(self.forecast_df)

    # ── Public API ────────────────────────────────────────────────────────────
    def switch_model(self, model_type: ModelChoice):
        """Hot-swap the active AI model at runtime."""
        self.model_type = model_type
        if self.verbose:
            print(f"  [Controller] Active model → [{model_type}]")

    def refresh_forecast(self):
        """Re-fetch the 7-day forecast (call once per day)."""
        print("\n  🔄  Refreshing strategic forecast...")
        self.forecast_df = fetch_forecast()
        self.today_plan  = get_today_plan(self.forecast_df)
        if self.verbose:
            print_forecast(self.forecast_df)

    def tick(
        self,
        sensor_reading: dict,
        now: Optional[datetime] = None,
        manual_override: Optional[bool] = None,
    ) -> dict:
        """
        Process one sensor reading through all 3 layers.

        Parameters
        ----------
        sensor_reading  : dict with keys temp_SOIL, water_SOIL, conduct_SOIL
        now             : Simulated or real timestamp
        manual_override : True = force ON, False = force OFF, None = auto
        """
        now        = now or datetime.utcnow()
        water_soil = sensor_reading["water_SOIL"]
        zone       = get_moisture_zone(water_soil)

        # ── Layer 3: AI inference ─────────────────────────────────────────────
        ai_pred  = int(predict(sensor_reading, model_type=self.model_type)[0])
        ai_proba = float(
            predict_proba(sensor_reading, model_type=self.model_type)[0][1]
        )

        # ── Layer 1: Strategic plan for today ─────────────────────────────────
        strategic_power    = self.today_plan["power"]     # FULL / HALF / NONE
        strategic_label    = self.today_plan["label"]     # DRY / MILD / WET
        strategic_cluster  = self.today_plan["cluster"]   # 0 / 1 / 2

        # ── Decision logic ────────────────────────────────────────────────────
        pump_on         = False
        decision_source = "AUTO"
        reason          = ""

        # ── Emergency override (< 5%) — bypasses all layers ──────────────────
        if water_soil < EMERGENCY_THRESHOLD:
            pump_on         = True
            decision_source = "EMERGENCY"
            reason          = (
                f"⚠️  EMERGENCY: moisture at {water_soil:.1f}% "
                f"(< {EMERGENCY_THRESHOLD}%) — bypassing all layers!"
            )

        # ── Manual override ───────────────────────────────────────────────────
        elif manual_override is True and water_soil < WET_THRESHOLD:
            pump_on         = True
            decision_source = "MANUAL_ON"
            reason          = "Manual override ON"

        elif manual_override is False:
            pump_on         = False
            decision_source = "MANUAL_OFF"
            reason          = "Manual override OFF"

        # ── Layer 2: Safety veto (> 20%) ─────────────────────────────────────
        elif water_soil > WET_THRESHOLD:
            pump_on         = False
            decision_source = "SAFETY_VETO"
            reason          = (
                f"🛑  Safety veto: soil too wet ({water_soil:.1f}% > "
                f"{WET_THRESHOLD}%) — preventing root rot"
            )

        # ── Layer 1: Strategic skip (forecast = WET/NONE) ─────────────────────
        elif strategic_power == "NONE":
            pump_on         = False
            decision_source = "STRATEGIC_SKIP"
            reason          = (
                f"📅  Strategic skip: forecast is {strategic_label} "
                f"— no irrigation planned today"
            )

        # ── All 3 layers must agree ───────────────────────────────────────────
        elif water_soil < ZONE_RED and ai_pred == 1:
            # Check strategic layer approves
            if strategic_power in ("FULL", "HALF"):
                pump_on         = True
                decision_source = "CONSENSUS"
                reason          = (
                    f"✅  Consensus: soil at {water_soil:.1f}% + "
                    f"AI agrees + forecast is {strategic_label} "
                    f"({strategic_power} irrigation)"
                )
            else:
                pump_on         = False
                decision_source = "STRATEGIC_SKIP"
                reason          = (
                    f"📅  Strategic skip: soil thirsty but "
                    f"forecast says {strategic_label}"
                )

        # ── Soil thirsty but AI disagrees ────────────────────────────────────
        elif water_soil < ZONE_RED and ai_pred == 0:
            pump_on         = False
            decision_source = "AI_VETO"
            reason          = (
                f"🤖  AI veto: soil at {water_soil:.1f}% but model "
                f"predicts no irrigation needed (P={ai_proba:.3f})"
            )

        # ── Orange zone — monitoring ──────────────────────────────────────────
        elif water_soil < ZONE_ORANGE:
            pump_on         = False
            decision_source = "MONITORING"
            reason          = (
                f"🟠  Monitoring: soil at {water_soil:.1f}% "
                f"— approaching threshold"
            )

        # ── Optimal zone ──────────────────────────────────────────────────────
        else:
            pump_on         = False
            decision_source = "OPTIMAL"
            reason          = (
                f"🟢  Optimal: soil at {water_soil:.1f}% "
                f"— no action needed"
            )

        PUMP_STATE["on"] = pump_on

        record = {
            "timestamp"        : now.isoformat(),
            "model"            : self.model_type,
            "temp_SOIL"        : sensor_reading.get("temp_SOIL"),
            "water_SOIL"       : water_soil,
            "conduct_SOIL"     : sensor_reading.get("conduct_SOIL"),
            "zone"             : zone["zone"],
            "zone_colour"      : zone["colour"],
            # Layer 1
            "strategic_cluster": strategic_cluster,
            "strategic_label"  : strategic_label,
            "strategic_power"  : strategic_power,
            # Layer 3
            "ai_prediction"    : ai_pred,
            "ai_probability"   : round(ai_proba, 4),
            # Final
            "pump_on"          : pump_on,
            "decision_source"  : decision_source,
            "reason"           : reason,
        }

        self.audit_log.append(record)

        if self.verbose:
            self._print_status(record)

        return record

    def export_log(self) -> "pd.DataFrame":
        import pandas as pd
        return pd.DataFrame(self.audit_log)

    # ── Pretty printer ────────────────────────────────────────────────────────
    def _print_status(self, r: dict):
        pump_icon = "💧 ON " if r["pump_on"] else "🔴 OFF"
        print(
            f"\n┌─ {r['timestamp']}  [{r['model']}] ─────────────────────────\n"
            f"│  Moisture   : {r['water_SOIL']:5.1f}%  "
            f"{r['zone_colour']} {r['zone']}\n"
            f"│  Temp       : {r['temp_SOIL']:5.2f}°C   "
            f"Conductivity: {r['conduct_SOIL']} µS/cm\n"
            f"│  Layer 1    : {r['strategic_label']} "
            f"(Cluster {r['strategic_cluster']}) → "
            f"{r['strategic_power']} irrigation\n"
            f"│  Layer 3    : AI {'YES' if r['ai_prediction'] else 'NO ':3s}  "
            f"(P={r['ai_probability']:.3f})\n"
            f"│  Decision   : {r['reason']}\n"
            f"│  Source     : {r['decision_source']}\n"
            f"└─ PUMP: {pump_icon} ──────────────────────────────────────────"
        )