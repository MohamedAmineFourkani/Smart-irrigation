"""
planner.py
Irrigation planner with cooldown, daily budget, and protection mechanisms.
"""

from datetime import datetime, timedelta, date
from typing import Optional

from data_fetcher import get_moisture_zone, ZONE_RED, ZONE_ORANGE
from config import (
    PLANNER_CYCLE_DURATION_MIN,
    PLANNER_COOLDOWN_MIN,
    PLANNER_MAX_DAILY_MIN,
)


class IrrigationPlanner:
    def __init__(
        self,
        cycle_duration_min: int = PLANNER_CYCLE_DURATION_MIN,
        cooldown_min: int = PLANNER_COOLDOWN_MIN,
        max_daily_minutes: int = PLANNER_MAX_DAILY_MIN,
    ):
        self.cycle_duration = timedelta(minutes=cycle_duration_min)
        self.cooldown       = timedelta(minutes=cooldown_min)
        self.max_daily      = timedelta(minutes=max_daily_minutes)

        self._last_run: Optional[datetime] = None
        self._daily_date: Optional[date]   = None
        self._daily_total: timedelta       = timedelta(0)

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
          zone (dict), ai_agrees (bool), cooldown_remaining (str),
          daily_used (str), daily_budget (str)
        """
        now  = now or datetime.utcnow()
        zone = get_moisture_zone(water_soil)
        ai_agrees = bool(ai_prediction == 1)

        # ── Reset daily budget at midnight ────────────────────────────────────
        today = now.date()
        if self._daily_date != today:
            self._daily_date  = today
            self._daily_total = timedelta(0)

        # ── Hard override: too wet ────────────────────────────────────────────
        if not zone["pump_allowed"]:
            return self._response(
                irrigate=False,
                reason=f"Zone {zone['zone']}: pump locked OFF (moisture {water_soil:.1f}%)",
                zone=zone,
                ai_agrees=ai_agrees,
                now=now,
            )

        # ── Cooldown check ────────────────────────────────────────────────────
        if self._last_run and (now - self._last_run) < self.cooldown:
            remaining = self.cooldown - (now - self._last_run)
            return self._response(
                irrigate=False,
                reason=(
                    f"Cooldown active — next eligible in {_fmt(remaining)} "
                    f"(cooldown: {_fmt(self.cooldown)})"
                ),
                zone=zone,
                ai_agrees=ai_agrees,
                now=now,
            )

        # ── Daily budget check (including this cycle) ─────────────────────────
        projected_total = self._daily_total + self.cycle_duration
        if projected_total > self.max_daily:
            return self._response(
                irrigate=False,
                reason=(
                    f"Daily budget would be exceeded ({_fmt(self._daily_total)} + "
                    f"{_fmt(self.cycle_duration)} > {_fmt(self.max_daily)})"
                ),
                zone=zone,
                ai_agrees=ai_agrees,
                now=now,
            )

        # ── Hybrid decision: sensor RED + AI agrees ───────────────────────────
        if water_soil < ZONE_RED and ai_agrees:
            self._last_run   = now
            self._daily_total += self.cycle_duration
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
        cooldown_remaining = ""
        if self._last_run and (now - self._last_run) < self.cooldown:
            remaining = self.cooldown - (now - self._last_run)
            cooldown_remaining = _fmt(remaining)

        return {
            "irrigate"          : irrigate,
            "reason"            : reason,
            "zone"              : zone,
            "ai_agrees"         : ai_agrees,
            "pump_end"          : now + self.cycle_duration if irrigate else None,
            "next_check"        : now + self.cooldown,
            "cooldown_remaining": cooldown_remaining,
            "daily_used"        : _fmt(self._daily_total),
            "daily_budget"      : _fmt(self.max_daily),
            "timestamp"         : now.isoformat(),
        }


def _fmt(td: timedelta) -> str:
    total = int(td.total_seconds())
    h, r  = divmod(total, 3600)
    m, s  = divmod(r, 60)
    if h:
        return f"{h}h {m:02d}m"
    return f"{m}m {s:02d}s"
