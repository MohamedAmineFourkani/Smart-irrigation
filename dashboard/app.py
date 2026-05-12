"""
dashboard/app.py
─────────────────────────────────────────────────────────────────────────────
Smart Irrigation Control Platform — Streamlit Dashboard

Run with:
    streamlit run dashboard/app.py
"""

import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# ── Morocco timezone GMT+1 ────────────────────────────────────────────────────
MOROCCO_TZ = timezone(timedelta(hours=1))

# ── Make src/ importable ──────────────────────────────────────────────────────
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))

import database as db
from forecaster import fetch_forecast, CLUSTER_PLAN

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Smart Irrigation",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# STYLING
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

    :root {
        --green      : #00c896;
        --green-dim  : #00c89622;
        --orange     : #f59e0b;
        --red        : #ef4444;
        --blue       : #3b82f6;
        --bg         : #0a0f0d;
        --card       : #111a15;
        --border     : #1e2e24;
        --text       : #e2efe8;
        --text-dim   : #6b8f77;
    }

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
        background-color: var(--bg);
        color: var(--text);
    }

    .stApp { background-color: var(--bg); }

    /* ── Header ── */
    .header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1.5rem 0 1rem 0;
        border-bottom: 1px solid var(--border);
        margin-bottom: 1.5rem;
    }
    .header-title {
        font-family: 'Space Mono', monospace;
        font-size: 1.4rem;
        font-weight: 700;
        color: var(--green);
        letter-spacing: -0.5px;
    }
    .header-sub {
        font-size: 0.78rem;
        color: var(--text-dim);
        margin-top: 2px;
    }
    .live-badge {
        background: var(--green-dim);
        border: 1px solid var(--green);
        color: var(--green);
        font-family: 'Space Mono', monospace;
        font-size: 0.7rem;
        padding: 4px 10px;
        border-radius: 20px;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50%       { opacity: 0.4; }
    }

    /* ── Metric cards ── */
    .metric-card {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.2rem 1.4rem;
        height: 100%;
    }
    .metric-label {
        font-size: 0.72rem;
        color: var(--text-dim);
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 6px;
    }
    .metric-value {
        font-family: 'Space Mono', monospace;
        font-size: 2rem;
        font-weight: 700;
        line-height: 1;
    }
    .metric-sub {
        font-size: 0.75rem;
        color: var(--text-dim);
        margin-top: 4px;
    }
    .green  { color: var(--green);  }
    .orange { color: var(--orange); }
    .red    { color: var(--red);    }
    .blue   { color: var(--blue);   }
    .dim    { color: var(--text-dim); }

    /* ── Section titles ── */
    .section-title {
        font-family: 'Space Mono', monospace;
        font-size: 0.78rem;
        color: var(--text-dim);
        text-transform: uppercase;
        letter-spacing: 2px;
        margin: 1.8rem 0 0.8rem 0;
        padding-bottom: 6px;
        border-bottom: 1px solid var(--border);
    }

    /* ── Decision card ── */
    .decision-card {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.2rem 1.4rem;
    }
    .layer-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid var(--border);
        font-size: 0.85rem;
    }
    .layer-row:last-child { border-bottom: none; }
    .layer-name { color: var(--text-dim); font-size: 0.75rem; }
    .badge {
        font-family: 'Space Mono', monospace;
        font-size: 0.72rem;
        padding: 3px 10px;
        border-radius: 20px;
    }
    .badge-green  { background: var(--green-dim);  color: var(--green);  border: 1px solid var(--green); }
    .badge-red    { background: #ef444422;          color: var(--red);    border: 1px solid var(--red); }
    .badge-orange { background: #f59e0b22;          color: var(--orange); border: 1px solid var(--orange); }
    .badge-blue   { background: #3b82f622;          color: var(--blue);   border: 1px solid var(--blue); }
    .badge-dim    { background: #ffffff11;          color: var(--text-dim); border: 1px solid var(--border); }

    /* ── Pump status ── */
    .pump-on  { color: var(--green);  font-family: 'Space Mono', monospace; font-size: 1.3rem; }
    .pump-off { color: var(--red);    font-family: 'Space Mono', monospace; font-size: 1.3rem; }

    /* ── Alert box ── */
    .alert {
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 8px;
        font-size: 0.82rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .alert-red    { background: #ef444415; border: 1px solid #ef444440; color: #fca5a5; }
    .alert-orange { background: #f59e0b15; border: 1px solid #f59e0b40; color: #fcd34d; }
    .alert-green  { background: #00c89615; border: 1px solid #00c89640; color: #6ee7b7; }
    .alert-blue   { background: #3b82f615; border: 1px solid #3b82f640; color: #93c5fd; }

    /* ── Forecast row ── */
    .forecast-row {
        display: flex;
        gap: 8px;
        margin-top: 8px;
    }
    .forecast-day {
        flex: 1;
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 10px 8px;
        text-align: center;
        font-size: 0.75rem;
    }
    .forecast-day-name {
        color: var(--text-dim);
        font-size: 0.68rem;
        margin-bottom: 4px;
    }
    .forecast-emoji { font-size: 1.3rem; }
    .forecast-label {
        font-family: 'Space Mono', monospace;
        font-size: 0.65rem;
        margin-top: 4px;
    }
    .forecast-freq {
        color: var(--text-dim);
        font-size: 0.65rem;
        margin-top: 2px;
    }

    /* ── Control buttons ── */
    .stButton > button {
        border-radius: 8px;
        font-family: 'Space Mono', monospace;
        font-size: 0.8rem;
        font-weight: 700;
        padding: 0.6rem 1.2rem;
        border: none;
        width: 100%;
        cursor: pointer;
        transition: opacity 0.2s;
    }
    .stButton > button:hover { opacity: 0.85; }

    /* Hide streamlit default elements */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 1rem; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def moisture_colour(val):
    if val is None:  return "dim"
    if val < 5:      return "red"
    if val < 15:     return "red"
    if val < 20:     return "orange"
    if val <= 50:    return "green"
    return "orange"

def badge_for_zone(zone):
    mapping = {
        "RED"    : "badge-red",
        "ORANGE" : "badge-orange",
        "GREEN"  : "badge-green",
        "WARNING": "badge-orange",
    }
    return mapping.get(zone, "badge-dim")

def badge_for_power(power):
    mapping = {
        "FULL" : "badge-red",
        "HALF" : "badge-orange",
        "NONE" : "badge-green",
    }
    return mapping.get(power, "badge-dim")

ALERT_COOLDOWN_SEC = 120  # don't repeat the same alert type within 2 minutes

def generate_alerts(latest, df):
    alerts = []
    now_ts = datetime.now(MOROCCO_TZ)

    # ── Initialise alert cooldown tracker ─────────────────────────────────────
    if "_alert_last" not in st.session_state:
        st.session_state["_alert_last"] = {}

    def should_alert(key: str) -> bool:
        last = st.session_state["_alert_last"].get(key)
        if last and (now_ts - last).total_seconds() < ALERT_COOLDOWN_SEC:
            return False
        st.session_state["_alert_last"][key] = now_ts
        return True

    if latest:
        w = latest.get("water_SOIL")
        ts = latest.get("timestamp")

        # ── Sensor connection status ──────────────────────────────────────────
        if ts is not None:
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=MOROCCO_TZ)
            age_min = (now_ts - ts).total_seconds() / 60
            if age_min > 60 and should_alert("sensor_offline"):
                alerts.append(("red",    "📡", f"Sensor offline for {age_min:.0f} minutes!"))
            elif age_min > 30 and should_alert("sensor_stale"):
                alerts.append(("orange", "📡", f"Sensor stale — last reading {age_min:.0f} min ago"))

        if w is not None:
            if w < 5 and should_alert("emergency_low"):
                alerts.append(("red",    "🚨", f"EMERGENCY: Moisture critically low at {w:.1f}%!"))
            elif w < 15 and should_alert("below_threshold"):
                alerts.append(("red",    "⚠️", f"Moisture below threshold: {w:.1f}% — irrigation may be needed"))
            elif w < 20 and should_alert("approaching"):
                alerts.append(("orange", "🟠", f"Moisture approaching threshold: {w:.1f}%"))
        if latest.get("pump_on") and should_alert("pump_on"):
            alerts.append(("green",  "💧", f"Pump activated — {latest.get('decision_source', '')}"))
        if latest.get("decision_source") == "ERROR" and should_alert("api_error"):
            alerts.append(("blue",   "❌", f"API Error: {latest.get('reason', 'Unknown error')}"))
        if latest.get("decision_source") == "SENSOR_OFFLINE" and should_alert("sensor_down"):
            alerts.append(("red",   "📡", f"Sensor offline: {latest.get('reason', 'No data')}"))
        if latest.get("decision_source") == "INVALID_DATA" and should_alert("bad_data"):
            alerts.append(("red",   "⚠️", f"Invalid sensor data: {latest.get('reason', '')}"))
        if latest.get("decision_source") == "PLANNER_VETO" and should_alert("planner_veto"):
            alerts.append(("blue",  "🛡️", f"Planner vetoed: {latest.get('reason', '')}"))
        bat = latest.get("BatV")
        if bat and bat < 3.0 and should_alert("battery_low"):
            alerts.append(("orange", "🔋", f"Battery low: {bat:.2f}V"))
    if not alerts:
        if should_alert("nominal"):
            alerts.append(("green", "✅", "All systems nominal"))
    return alerts


# ─────────────────────────────────────────────────────────────────────────────
# MAIN DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
def main():

    # ── Init DB ───────────────────────────────────────────────────────────────
    db.init()

    # ── Load data ─────────────────────────────────────────────────────────────
    df       = db.fetch()
    latest   = db.fetch_latest()
    has_data = not df.empty

    # ── Header ───────────────────────────────────────────────────────────────
    st.markdown("""
        <div class="header">
            <div>
                <div class="header-title">🌱 SMART IRRIGATION</div>
                <div class="header-sub">AI-Driven Hybrid Control Platform</div>
            </div>
            <div class="live-badge">● LIVE</div>
        </div>
    """, unsafe_allow_html=True)

    # ── SECTION 1: Live Metrics ───────────────────────────────────────────────
    st.markdown('<div class="section-title">Live Sensor Data</div>',
                unsafe_allow_html=True)

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    water  = latest.get("water_SOIL")   if has_data else None
    temp   = latest.get("temp_SOIL")    if has_data else None
    cond   = latest.get("conduct_SOIL") if has_data else None
    batv   = latest.get("BatV")         if has_data else None
    zone   = latest.get("zone", "—")    if has_data else "—"
    ts     = latest.get("timestamp")    if has_data else None

    w_col  = moisture_colour(water)

    # ── Connection status ─────────────────────────────────────────────────────
    now_ts = datetime.now(MOROCCO_TZ)
    if ts is not None:
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=MOROCCO_TZ)
        age_min = (now_ts - ts).total_seconds() / 60
        if age_min < 30:
            conn_status = "🟢 Connected"
            conn_colour = "green"
        elif age_min < 60:
            conn_status = "🟠 Stale"
            conn_colour = "orange"
        else:
            conn_status = "🔴 Offline"
            conn_colour = "red"
    else:
        conn_status = "⚫ No data"
        conn_colour = "dim"

    with c1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">💧 Soil Moisture</div>
                <div class="metric-value {w_col}">
                    {f"{water:.1f}%" if water is not None else "—"}
                </div>
                <div class="metric-sub">Zone: {zone}</div>
            </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">🌡️ Soil Temp</div>
                <div class="metric-value green">
                    {f"{temp:.1f}°C" if temp is not None else "—"}
                </div>
                <div class="metric-sub">DS18B20 probe</div>
            </div>""", unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">⚡ Conductivity</div>
                <div class="metric-value blue">
                    {f"{cond} µS" if cond is not None else "—"}
                </div>
                <div class="metric-sub">Soil salinity</div>
            </div>""", unsafe_allow_html=True)

    with c4:
        bat_col = "red" if batv and batv < 3.0 else "green"
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">🔋 Battery</div>
                <div class="metric-value {bat_col}">
                    {f"{batv:.2f}V" if batv is not None else "—"}
                </div>
                <div class="metric-sub">Sensor node</div>
            </div>""", unsafe_allow_html=True)

    with c5:
        pump_on  = latest.get("pump_on", False) if has_data else False
        pump_cls = "pump-on" if pump_on else "pump-off"
        pump_txt = "💧 ON" if pump_on else "🔴 OFF"
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">⚙️ Pump Status</div>
                <div class="{pump_cls}">{pump_txt}</div>
                <div class="metric-sub">
                    {latest.get('decision_source', '—') if has_data else '—'}
                </div>
            </div>""", unsafe_allow_html=True)

    with c6:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">📡 Connection</div>
                <div class="metric-value {conn_colour}">{conn_status}</div>
                <div class="metric-sub">
                    {ts.strftime('%H:%M:%S') if ts else '—'}
                </div>
            </div>""", unsafe_allow_html=True)

    # ── SECTION 1b: Protection Status ──────────────────────────────────────────
    st.markdown('<div class="section-title">Protection Status</div>',
                unsafe_allow_html=True)

    cd_remin  = latest.get("cooldown_remaining", "") if has_data else ""
    daily_use = latest.get("daily_used", "—") if has_data else "—"

    cooldown_txt = cd_remin if cd_remin else "Ready"
    cooldown_cls = "orange" if cd_remin else "green"

    # ── Parse daily_used to check if budget is nearly full ─────────────────
    budget_cls = "green"
    if daily_use != "—":
        try:
            used_str = daily_use.split("/")[0].strip()
            if used_str:
                parts = used_str.split()
                if "h" in used_str:
                    used_min = int(parts[0]) * 60 + int(parts[1])
                else:
                    used_min = int(parts[0])
                if used_min >= 50:
                    budget_cls = "red"
                elif used_min >= 40:
                    budget_cls = "orange"
        except (ValueError, IndexError):
            pass

    sa1, sa2 = st.columns(2)

    with sa1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">⏱️ Cooldown Timer</div>
                <div class="metric-value {cooldown_cls}">{cooldown_txt}</div>
                <div class="metric-sub">Wait time before next irrigation cycle</div>
            </div>""", unsafe_allow_html=True)

    with sa2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">📊 Daily Water Limit</div>
                <div class="metric-value {budget_cls}">{daily_use}</div>
                <div class="metric-sub">Irrigation used today / Maximum allowed</div>
            </div>""", unsafe_allow_html=True)

    # ── SECTION 2: AI Decision + Forecast ────────────────────────────────────
    st.markdown('<div class="section-title">AI Decision Engine</div>',
                unsafe_allow_html=True)

    col_dec, col_fore = st.columns([1, 2])

    with col_dec:
        ai_pred   = latest.get("ai_prediction")   if has_data else 0
        ai_prob   = latest.get("ai_probability")  if has_data else 0
        strat_lbl = latest.get("strategic_label", "—") if has_data else "—"
        strat_pwr = latest.get("strategic_power", "—") if has_data else "—"
        reason    = latest.get("reason", "No data yet") if has_data else "No data yet"
        src       = latest.get("decision_source", "—") if has_data else "—"

        ai_badge  = "badge-red"  if ai_pred else "badge-green"
        ai_txt    = "IRRIGATE"   if ai_pred else "NO ACTION"
        pwr_badge = badge_for_power(strat_pwr)
        z_badge   = badge_for_zone(zone)

        def _pct(v):
            if v is None: return "—"
            try: return f"{float(v):.0%}"
            except: return "—"
        def _s(v, d="—"):
            return v if v is not None and v != "None" else d

        st.markdown(f"""
            <div class="decision-card">
                <div class="layer-row">
                    <span class="layer-name">LAYER 1 — Strategic</span>
                    <span class="badge {pwr_badge}">{_s(strat_lbl)} · {_s(strat_pwr)}</span>
                </div>
                <div class="layer-row">
                    <span class="layer-name">LAYER 2 — Sensor</span>
                    <span class="badge {z_badge}">{_s(zone)}</span>
                </div>
                <div class="layer-row">
                    <span class="layer-name">LAYER 3 — AI Model</span>
                    <span class="badge {ai_badge}">{ai_txt} ({_pct(ai_prob)})</span>
                </div>
                <div class="layer-row">
                    <span class="layer-name">FINAL DECISION</span>
                    <span class="badge {'badge-red' if pump_on else 'badge-dim'}">{src}</span>
                </div>
                <div style="margin-top:10px; font-size:0.78rem; color:#6b8f77;">
                    {reason}
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col_fore:
        try:
            forecast_df = fetch_forecast()
            days_html   = ""
            for _, row in forecast_df.iterrows():
                lbl_color = {
                    "DRY" : "#ef4444",
                    "MILD": "#f59e0b",
                    "WET" : "#3b82f6",
                }.get(row["label"], "#6b8f77")
                days_html += f"""
                    <div class="forecast-day">
                        <div class="forecast-day-name">{row['date'].strftime('%a')}</div>
                        <div class="forecast-emoji">{row['emoji']}</div>
                        <div class="forecast-label" style="color:{lbl_color}">
                            {row['label']}
                        </div>
                        <div class="forecast-freq">x{row['frequency']}/wk</div>
                        <div class="forecast-freq">{row['rain']:.0f}mm</div>
                    </div>"""
            st.markdown(f"""
                <div style="background:var(--card); border:1px solid var(--border);
                            border-radius:12px; padding:1rem;">
                    <div style="font-size:0.72rem; color:var(--text-dim);
                                text-transform:uppercase; letter-spacing:1px;
                                margin-bottom:6px;">📅 7-Day Strategic Forecast</div>
                    <div class="forecast-row">{days_html}</div>
                </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.markdown(
                f'<div class="alert alert-blue">❌ Forecast unavailable: {e}</div>',
                unsafe_allow_html=True,
            )

    # ── SECTION 3: Manual Control ─────────────────────────────────────────────
    st.markdown('<div class="section-title">Manual Control</div>',
                unsafe_allow_html=True)

    # ── Show manual remaining time ────────────────────────────────────────────
    manual_remaining = latest.get("manual_remaining", "") if has_data else ""
    if manual_remaining:
        st.markdown(
            f'<div class="alert alert-orange">⏱️ Manual override active '
            f'— auto-off in {manual_remaining}</div>',
            unsafe_allow_html=True,
        )

    mc1, mc2, mc3, mc4 = st.columns(4)

    with mc1:
        MANUAL_TIMEOUT_MIN = 30
        if st.button(f"💧 Force Pump ON ({MANUAL_TIMEOUT_MIN}min)", key="force_on"):
            db.save({
                "timestamp"        : datetime.now(MOROCCO_TZ).isoformat(),
                "decision_source"  : "MANUAL_ON",
                "reason"           : f"Manual override — pump ON (auto-off {MANUAL_TIMEOUT_MIN}min)",
                "pump_on"          : True,
                "water_SOIL"       : water,
                "temp_SOIL"        : temp,
                "conduct_SOIL"     : cond,
                "BatV"             : batv,
                "zone"             : zone,
                "ai_prediction"    : 0,
                "ai_probability"   : 0,
                "strategic_cluster": 0,
                "strategic_label"  : strat_lbl,
                "strategic_power"  : strat_pwr,
            })
            st.success(f"✅ Pump forced ON — auto-off in {MANUAL_TIMEOUT_MIN} min")

    with mc2:
        if st.button("🔴 Force Pump OFF", key="force_off"):
            db.save({
                "timestamp"        : datetime.now(MOROCCO_TZ).isoformat(),
                "decision_source"  : "MANUAL_OFF",
                "reason"           : "Manual override — user forced pump OFF",
                "pump_on"          : False,
                "water_SOIL"       : water,
                "temp_SOIL"        : temp,
                "conduct_SOIL"     : cond,
                "BatV"             : batv,
                "zone"             : zone,
                "ai_prediction"    : 0,
                "ai_probability"   : 0,
                "strategic_cluster": 0,
                "strategic_label"  : strat_lbl,
                "strategic_power"  : strat_pwr,
            })
            st.success("✅ Pump forced OFF — logged to database")

    with mc3:
        if st.button("🔄 Refresh Data", key="refresh"):
            st.rerun()

    with mc4:
        if st.button("📊 Export Log (CSV)", key="export"):
            if has_data:
                csv = df.to_csv(index=False)
                st.download_button(
                    "⬇️ Download",
                    csv,
                    "irrigation_log.csv",
                    "text/csv",
                )
            else:
                st.warning("No data to export yet.")

    # ── SECTION 4: Alerts ─────────────────────────────────────────────────────
    st.markdown('<div class="section-title">Alerts</div>',
                unsafe_allow_html=True)

    alerts = generate_alerts(latest if has_data else {}, df)
    for colour, icon, msg in alerts:
        st.markdown(
            f'<div class="alert alert-{colour}">{icon} {msg}</div>',
            unsafe_allow_html=True,
        )

    # ── SECTION 5: Historical Charts ──────────────────────────────────────────
    st.markdown('<div class="section-title">Historical Data</div>',
                unsafe_allow_html=True)

    if not has_data:
        st.markdown("""
            <div class="alert alert-blue">
                📭 No historical data yet — run main.py to start collecting.
            </div>""", unsafe_allow_html=True)
    else:
        df_plot = df.sort_values("timestamp")

        ch1, ch2 = st.columns(2)

        # ── Chart 1: Moisture over time ───────────────────────────────────────
        with ch1:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_plot["timestamp"],
                y=df_plot["water_SOIL"],
                mode="lines+markers",
                name="Moisture",
                line=dict(color="#00c896", width=2),
                marker=dict(size=4),
                fill="tozeroy",
                fillcolor="rgba(0,200,150,0.08)",
            ))
            fig.add_hline(
                y=15, line_dash="dash", line_color="#ef4444", opacity=0.6,
                annotation_text="RED threshold (15%)",
            )
            fig.add_hline(
                y=20, line_dash="dash", line_color="#f59e0b", opacity=0.6,
                annotation_text="ORANGE threshold (20%)",
            )
            fig.update_layout(
                title="Soil Moisture Over Time",
                paper_bgcolor="#111a15",
                plot_bgcolor="#111a15",
                font=dict(color="#6b8f77", size=11),
                xaxis=dict(gridcolor="#1e2e24", title=""),
                yaxis=dict(gridcolor="#1e2e24", title="Moisture (%)"),
                margin=dict(l=40, r=20, t=40, b=20),
                height=280,
            )
            st.plotly_chart(fig, use_container_width=True)

        # ── Chart 2: Pump activations ─────────────────────────────────────────
        with ch2:
            pump_counts        = df_plot.copy()
            pump_counts["date"] = pd.to_datetime(
                pump_counts["timestamp"]).dt.date
            daily = pump_counts.groupby("date")["pump_on"].sum().reset_index()

            fig2 = go.Figure(go.Bar(
                x=daily["date"],
                y=daily["pump_on"],
                marker_color="#3b82f6",
                opacity=0.8,
            ))
            fig2.update_layout(
                title="Pump Activations per Day",
                paper_bgcolor="#111a15",
                plot_bgcolor="#111a15",
                font=dict(color="#6b8f77", size=11),
                xaxis=dict(gridcolor="#1e2e24", title=""),
                yaxis=dict(gridcolor="#1e2e24", title="Activations"),
                margin=dict(l=40, r=20, t=40, b=20),
                height=280,
            )
            st.plotly_chart(fig2, use_container_width=True)

        ch3, ch4 = st.columns(2)

        # ── Chart 3: Temperature trend ────────────────────────────────────────
        with ch3:
            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(
                x=df_plot["timestamp"],
                y=df_plot["temp_SOIL"],
                mode="lines",
                name="Temp",
                line=dict(color="#f59e0b", width=2),
            ))
            fig3.update_layout(
                title="Soil Temperature Trend",
                paper_bgcolor="#111a15",
                plot_bgcolor="#111a15",
                font=dict(color="#6b8f77", size=11),
                xaxis=dict(gridcolor="#1e2e24", title=""),
                yaxis=dict(gridcolor="#1e2e24", title="°C"),
                margin=dict(l=40, r=20, t=40, b=20),
                height=280,
            )
            st.plotly_chart(fig3, use_container_width=True)

        # ── Chart 4: Decision source breakdown ────────────────────────────────
        with ch4:
            dec_counts         = df["decision_source"].value_counts().reset_index()
            dec_counts.columns = ["source", "count"]
            fig4 = px.pie(
                dec_counts,
                names="source",
                values="count",
                color_discrete_sequence=[
                    "#00c896", "#3b82f6", "#f59e0b",
                    "#ef4444", "#8b5cf6", "#6b8f77",
                ],
            )
            fig4.update_layout(
                title="Decision Source Breakdown",
                paper_bgcolor="#111a15",
                plot_bgcolor="#111a15",
                font=dict(color="#6b8f77", size=11),
                margin=dict(l=20, r=20, t=40, b=20),
                height=280,
                legend=dict(font=dict(color="#6b8f77")),
            )
            st.plotly_chart(fig4, use_container_width=True)

        # ── Audit log table ───────────────────────────────────────────────────
        st.markdown('<div class="section-title">Audit Log</div>',
                    unsafe_allow_html=True)
        display_cols = [
            "timestamp", "water_SOIL", "temp_SOIL",
            "zone", "strategic_label", "ai_prediction",
            "pump_on", "decision_source", "reason",
        ]
        available = [c for c in display_cols if c in df.columns]
        st.dataframe(
            df[available].head(50),
            use_container_width=True,
            height=300,
        )

    # ── Footer ────────────────────────────────────────────────────────────────
    last_update = (
        ts.strftime("%Y-%m-%d %H:%M:%S GMT+1")
        if ts else "No data yet"
    )
    st.markdown(f"""
        <div style="text-align:center; color:#2d4a38;
                    font-size:0.72rem; margin-top:2rem; padding-top:1rem;
                    border-top:1px solid #1e2e24;">
            Smart Irrigation Platform · Last sensor reading: {last_update}
        </div>
    """, unsafe_allow_html=True)

    # ── Auto-refresh every 60 seconds ─────────────────────────────────────────
    st.markdown("""
        <script>
            setTimeout(() => window.location.reload(), 60000);
        </script>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()