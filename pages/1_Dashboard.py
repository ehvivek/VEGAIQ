"""
pages/1_Dashboard.py -- PitMind Race Dashboard
"""

import streamlit as st
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

st.set_page_config(
    page_title="PitMind | Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.styling import inject_css, setup_sidebar, render_ibm_label, get_race_metadata
from utils.helpers import (
    init_session_state, get_race_summary,
    stress_color, quality_label, fatigue_label, format_lap_time, get_event_badges,
    DRIVERS
)
from utils.charts import psychological_trace_chart
from core.data_pipeline import get_complete_driver_data, fetch_driver_radio
from core.models import get_peak_stress_lap

init_session_state()
inject_css()

# -- Sidebar --
with st.sidebar:
    setup_sidebar()

driver_name = st.session_state.get("selected_driver", "Max Verstappen")
driver = DRIVERS.get(driver_name, DRIVERS["Max Verstappen"])

# -- Load Data --
with st.spinner(f"Loading {driver_name} race data..."):
    df = get_complete_driver_data(driver_name)

# Ensure selected_lap defaults to this driver's peak
if "selected_lap" not in st.session_state or st.session_state.selected_lap not in df['lap'].values:
    st.session_state.selected_lap = get_peak_stress_lap(driver_name)

summary = get_race_summary(df)
peak_stress_lap = get_peak_stress_lap(driver_name)
peak_stress_val = df['stress_index'].max() if 'stress_index' in df.columns and not df.empty else 0.0
avg_decision = df['decision_quality'].mean() if 'decision_quality' in df.columns and not df.empty else 0.0
peak_fatigue = df['mental_fatigue'].max() if 'mental_fatigue' in df.columns and not df.empty else 0.0
radio_count = len(fetch_driver_radio(driver['code']))

# ====== HEADER ======
st.markdown("""
<div style="height:0;overflow:visible;pointer-events:none;user-select:none;">
  <div style="position:relative;top:0;left:-0.5rem;
              font-family:'Rajdhani',sans-serif;font-weight:700;font-size:7rem;
              color:var(--text-primary);letter-spacing:0.12em;user-select:none;opacity:0.04;
              white-space:nowrap;pointer-events:none;line-height:1;">DASHBOARD</div>
</div>""", unsafe_allow_html=True)

head_l, head_r = st.columns([3, 2])
with head_l:
    sess_text = str(st.session_state.get("selected_session", "RACE")).upper()
    st.markdown(f'<div style="padding-top:2.5rem;font-family:\'Share Tech Mono\',monospace;'
                f'font-size:0.65rem;letter-spacing:0.15em;color:#888;">{sess_text} OVERVIEW : {driver_name.upper()}</div>',
                unsafe_allow_html=True)
with head_r:
    meta = get_race_metadata(st.session_state.selected_race)
    st.markdown(f"""
<div style="text-align:right;padding-top:2.5rem;font-family:'Share Tech Mono',monospace;
            font-size:0.7rem;color:#888;">
  {meta['flag_entity']} {st.session_state.selected_race.upper()} &nbsp;
  <span style="color:{driver['color']};">&#9679;</span> {sess_text} &middot; {len(df)} LAPS
</div>""", unsafe_allow_html=True)

st.markdown(f'<div style="height:2px;background:linear-gradient(90deg,{driver["color"]},transparent);'
            'margin:0.3rem 0 1rem;"></div>', unsafe_allow_html=True)

# --- RAW STAT CALCULATION AND VERIFICATION ---
from core.data_pipeline import fetch_driver_laps, fetch_race_control

# 1. Number of Laps
raw_laps_df = fetch_driver_laps(driver['code'])
num_laps = len(raw_laps_df)
print(f"\\n--- VERIFIED METRIC: {driver_name} ---")
print(f"Number of Laps: {num_laps}")

# 2. Peak Stress Lap
# Using model output as explicitly allowed
peak_stress_lap_verified = peak_stress_lap
print(f"Peak Stress Lap: {peak_stress_lap_verified}")

# 3. Critical Events
rc_events = fetch_race_control()
critical_events_raw = []
for event in rc_events:
    cat = event.get('category', '').upper()
    msg = event.get('message', '').upper()
    if (any(x in cat for x in ['SAFETY CAR', 'VIRTUAL SAFETY CAR', 'RED FLAG', 'YELLOW FLAG']) or 
       any(x in msg for x in ['SAFETY CAR', 'VIRTUAL SAFETY CAR', 'RED FLAG', 'YELLOW FLAG'])):
        critical_events_raw.append(event)
critical_events_count = len(critical_events_raw)
print(f"Critical Events Count: {critical_events_count}")
print("--- RAW CRITICAL EVENTS ---")
for e in critical_events_raw:
    print(f"  Lap: {e.get('lap_number')} | Category: {e.get('category')} | Message: {e.get('message')}")

# 4. Radio Transmissions
radio_events = fetch_driver_radio(driver['code'])
radio_count = len(radio_events)
print(f"Radio Transmissions Count: {radio_count}")
print("--- RAW RADIO EVENTS ---")
for r in radio_events:
    print(f"  Date: {r.get('date')} | URL: {r.get('recording_url')}\\n")

# ====== ROW 1 - 4 METRIC CARDS ======
c1, c2, c3, c4 = st.columns(4)
metrics_data = [
    ("NUMBER OF LAPS", f"{num_laps}", "COMPLETED LAPS", "var(--text-primary)", "var(--border)"),
    ("PEAK STRESS LAP", f"LAP {peak_stress_lap_verified}", f"{peak_stress_val:.1f}/10 SCORE", driver["color"], driver["color"]),
    ("CRITICAL EVENTS", f"{critical_events_count}", "SAFETY/FLAGS", "#FF7B00", "var(--border)"),
    ("RADIO TRANSMISSIONS", f"{radio_count}", "AUDIO ENTRIES", "var(--text-primary)", "var(--border)"),
]
for col, (label, val, sub, color, border) in zip([c1, c2, c3, c4], metrics_data):
    with col:
        st.markdown(f"""
<div style="background:var(--bg-card);border:1px solid {border};border-radius:8px;padding:1rem 1.2rem;">
  <div style="font-family:'Share Tech Mono',monospace;font-size:0.6rem;
              letter-spacing:0.15em;color:var(--text-muted);">{label}</div>
  <div style="font-family:'Rajdhani',sans-serif;font-size:2.5rem;font-weight:700;
              color:{color};line-height:1;">{val}</div>
  <div style="font-family:'Rajdhani',sans-serif;font-size:0.8rem;color:var(--text-muted);">{sub}</div>
</div>""", unsafe_allow_html=True)

st.markdown('<div style="height:1rem"></div>', unsafe_allow_html=True)

# ====== ROW 2 - TABLE + CHART ======
col_table, col_chart = st.columns([2, 3], gap="medium")

with col_table:
    st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.65rem;'
                'letter-spacing:0.15em;color:#888;margin-bottom:0.5rem;">RACE TIMELINE</div>',
                unsafe_allow_html=True)

    show_all = st.checkbox("Show all laps", value=False, key="show_all")
    display_df = df.copy() if show_all else df[(df["lap"] >= max(1, peak_stress_lap - 5)) & (df["lap"] <= peak_stress_lap + 10)].copy()

    table_rows = []
    for _, row in display_df.iterrows():
        lap = int(row["lap"])
        stress = round(float(row["stress_index"]), 1)
        scolor = stress_color(stress)
        is_crit = lap == peak_stress_lap
        events = get_event_badges(row.get("race_events", "[]"))
        lt = format_lap_time(float(row["lap_time_seconds"]))
        hl = f"border-left:3px solid {driver['color']};background:rgba(232,0,45,0.06);" if is_crit else "border-left:3px solid transparent;"
        pct = min(100, int(stress * 10))
        fw = "700" if is_crit else "400"
        tc = driver["color"] if is_crit else "var(--text-primary)"

        table_rows.append(f"""<tr style="{hl}">
  <td style="padding:6px 10px;font-weight:{fw};color:{tc};">{lap}</td>
  <td style="padding:6px 10px;font-family:'Share Tech Mono',monospace;font-size:0.8rem;">{lt}</td>
  <td style="padding:6px 10px;font-size:0.75rem;">{events}</td>
  <td style="padding:6px 10px;">
    <div style="display:flex;align-items:center;gap:6px;">
      <div style="width:60px;height:6px;background:var(--bg-primary);border-radius:3px;overflow:hidden;">
        <div style="width:{pct}%;height:100%;background:{scolor};border-radius:3px;"></div>
      </div>
      <span style="font-size:0.75rem;color:{scolor};font-weight:600;">{stress}</span>
    </div>
  </td>
</tr>""")

    st.markdown(f"""
<div style="background:var(--bg-card);border:1px solid var(--border);border-radius:8px;
            overflow:hidden;max-height:400px;overflow-y:auto;">
  <table style="width:100%;border-collapse:collapse;font-family:'Rajdhani',sans-serif;font-size:0.85rem;">
    <thead><tr style="background:var(--bg-secondary);border-bottom:1px solid var(--border);">
      <th style="padding:8px 10px;text-align:left;font-family:'Share Tech Mono',monospace;
                 font-size:0.65rem;letter-spacing:0.1em;color:var(--text-muted);">LAP</th>
      <th style="padding:8px 10px;text-align:left;font-family:'Share Tech Mono',monospace;
                 font-size:0.65rem;color:var(--text-muted);">TIME</th>
      <th style="padding:8px 10px;text-align:left;font-family:'Share Tech Mono',monospace;
                 font-size:0.65rem;color:var(--text-muted);">EVENT</th>
      <th style="padding:8px 10px;text-align:left;font-family:'Share Tech Mono',monospace;
                 font-size:0.65rem;color:var(--text-muted);">STRESS</th>
    </tr></thead>
    <tbody>{''.join(table_rows)}</tbody>
  </table>
</div>""", unsafe_allow_html=True)

with col_chart:
    st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.65rem;'
                'letter-spacing:0.15em;color:#888;margin-bottom:0.5rem;">PSYCHOLOGICAL TRACE</div>',
                unsafe_allow_html=True)
    fig = psychological_trace_chart(df, peak_stress_lap, color=driver['color'])
    st.plotly_chart(fig, key="db_trace_chart", width="stretch", config={"displayModeBar": False})

st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)

# ====== ROW 3 - IBM GRANITE ANALYSIS ======
st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.65rem;'
            'letter-spacing:0.15em;color:#888;margin-bottom:0.5rem;">IBM GRANITE ANALYSIS</div>',
            unsafe_allow_html=True)

cache_key = f"granite_db_{st.session_state.selected_race}_{driver_name}"
if cache_key not in st.session_state:
    try:
        from core.granite import analyze_lap_for_driver
        st.session_state[cache_key] = analyze_lap_for_driver(driver_name, peak_stress_lap)
    except Exception as e:
        st.session_state[cache_key] = f"IBM Granite Analysis failed: {e}"

st.markdown(f"""
<div style="background:var(--bg-card);border:1px solid var(--border);border-left:3px solid {driver['color']};
            border-radius:8px;padding:1.2rem 1.5rem;">
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:0.6rem;">
    <div style="width:24px;height:24px;background:var(--bg-secondary);border:1px solid var(--border);
                border-radius:4px;display:flex;align-items:center;justify-content:center;
                font-size:0.6rem;font-family:'Share Tech Mono',monospace;color:#4A9EFF;">IBM</div>
    <span style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;
                 letter-spacing:0.12em;color:var(--text-muted);">GRANITE ANALYSIS &middot; LAP {peak_stress_lap}</span>
  </div>
  <div style="font-family:'Rajdhani',sans-serif;font-size:0.95rem;color:var(--text-muted);
              line-height:1.7;">{st.session_state[cache_key]}</div>
</div>""", unsafe_allow_html=True)

# ====== FOOTER ======
st.markdown(f'<div style="height:2px;background:linear-gradient(90deg,{driver["color"]},transparent);'
            'margin:1.5rem 0 0.5rem;"></div>', unsafe_allow_html=True)
render_ibm_label("IBM GRANITE 3.1 &middot; Data: OpenF1 + FastF1")
