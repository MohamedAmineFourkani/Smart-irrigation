"""
planner.py
Simple irrigation planner: recommends irrigation windows based on
moisture zone, AI prediction, and a minimum rest interval between cycles.
"""

from datetime import datetime, timedelta
from typing import Optional

from data_fetcher import get_moisture_zone, ZONE_RED, ZONE_ORANGE


# ── Default planning parameters ───────────────────────────────────────────────
DEFAULT_DURATION_MIN  = 10   # minutes to run the pump per cycle
DEFAULT_REST_MIN      = 60   # minimum minutes between two pump cycles


class IrrigationPlanner:
    def __init__(
        self,
        cycle_duration_min: int = DEFAULT_DURATION_MIN,
        rest_min: int = DEFAULT_REST_MIN,
    ):
        self.cycle_duration = timedelta(minutes=cycle_duration_min)
        self.rest_interval  = timedelta(minutes=rest_min)
        self._last_run: Optional[datetime] = None

    # ── Public API ────────────────────────────────────────────────────────────
    def recommend(
        self,
        water_soil: float,
        ai_prediction: int,
        now: Optional[datetime] = None,
    ) -> dict:
        """
        Decide whether to irrigate now.

        Returns
        -------
        dict with keys:
          irrigate (bool), reason (str), next_check (datetime),
          zone (dict), ai_agrees (bool)
        """
        now  = now or datetime.utcnow()
        zone = get_moisture_zone(water_soil)
        ai_agrees = bool(ai_prediction == 1)

        # ── Hard override: too wet ────────────────────────────────────────────
        if not zone["pump_allowed"]:
            return self._response(
                irrigate=False,
                reason=f"Zone {zone['zone']}: pump locked OFF (moisture {water_soil:.1f}%)",
                zone=zone,
                ai_agrees=ai_agrees,
                now=now,
            )

        # ── Rest interval not yet elapsed ────────────────────────────────────
        if self._last_run and (now - self._last_run) < self.rest_interval:
            remaining = self.rest_interval - (now - self._last_run)
            return self._response(
                irrigate=False,
                reason=f"Rest interval active — next eligible in {_fmt(remaining)}",
                zone=zone,
                ai_agrees=ai_agrees,
                now=now,
            )

        # ── Hybrid decision: sensor RED + AI agrees ───────────────────────────
        if water_soil < ZONE_RED and ai_agrees:
            self._last_run = now
            return self._response(
                irrigate=True,
                reason=(
                    f"RED zone ({water_soil:.1f}%) AND AI predicts irrigation required "
                    f"→ pump ON for {int(self.cycle_duration.total_seconds()//60)} min"
                ),
                zone=zone,
                ai_agrees=ai_agrees,
                now=now,
            )

        # ── ORANGE zone: recommend but do not force ───────────────────────────
        if water_soil < ZONE_ORANGE:
            msg = f"ORANGE zone ({water_soil:.1f}%) — monitoring recommended"
            if not ai_agrees:
                msg += "; AI does not predict need yet"
            return self._response(
                irrigate=False,
                reason=msg,
                zone=zone,
                ai_agrees=ai_agrees,
                now=now,
            )

        # ── RED zone but AI disagrees ─────────────────────────────────────────
        if water_soil < ZONE_RED and not ai_agrees:
            return self._response(
                irrigate=False,
                reason=(
                    f"RED zone ({water_soil:.1f}%) but AI predicts no irrigation needed "
                    "— standing by"
                ),
                zone=zone,
                ai_agrees=ai_agrees,
                now=now,
            )

        return self._response(
            irrigate=False,
            reason=f"Optimal zone ({water_soil:.1f}%) — no action required",
            zone=zone,
            ai_agrees=ai_agrees,
            now=now,
        )

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _response(
        self,
        irrigate: bool,
        reason: str,
        zone: dict,
        ai_agrees: bool,
        now: datetime,
    ) -> dict:
        return {
            "irrigate"   : irrigate,
            "reason"     : reason,
            "zone"       : zone,
            "ai_agrees"  : ai_agrees,
            "pump_end"   : now + self.cycle_duration if irrigate else None,
            "next_check" : now + self.rest_interval,
            "timestamp"  : now.isoformat(),
        }


def _fmt(td: timedelta) -> str:
    total = int(td.total_seconds())
    m, s  = divmod(total, 60)
    return f"{m}m {s:02d}s"
