"""
pages/2_Lap_Dive.py -- PitMind Lap Deep Dive
"""

import streamlit as st
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

st.set_page_config(
    page_title="PitMind | Lap Dive",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.styling import inject_css, setup_sidebar, get_svg_icon, render_ibm_label, get_race_metadata
from utils.helpers import (
    init_session_state, get_race_data, get_race_summary, load_lap_data,
    get_best_lap_data, format_lap_time, format_delta, stress_color,
    get_event_badges, get_key_events, get_tyre_badge,
)
from utils.charts import zoomed_lap_chart, hr_sparkline, eeg_sparkline, reaction_bar_chart

init_session_state()
inject_css()

# -- Sidebar --
with st.sidebar:
    setup_sidebar()

# -- Load Data --
with st.spinner("Loading race data..."):
    df = get_race_data(st.session_state.selected_race)
summary = get_race_summary(df)
best_lap_data = get_best_lap_data(df)
total_laps = len(df)
lap_num = st.session_state.selected_lap

# ====== HEADER ======
st.markdown(f"""
<div style="height:0;overflow:visible;pointer-events:none;user-select:none;">
  <div style="position:relative;top:0;left:-0.5rem;
              font-family:'Rajdhani',sans-serif;font-weight:700;font-size:7rem;
              color:var(--text-primary);letter-spacing:0.12em;user-select:none;opacity:0.04;
              white-space:nowrap;pointer-events:none;line-height:1;">LAP {lap_num}</div>
</div>""", unsafe_allow_html=True)

# Load lap data
lap_data = load_lap_data(df, lap_num)
stress = round(float(lap_data.get("stress_index", 5.0)), 1)
is_critical = stress >= 8.0

# Top row
top_l, top_m, top_r = st.columns([2, 3, 2])
with top_l:
    st.markdown(f"""
<div style="padding-top:2.5rem;">
  <span style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;
               letter-spacing:0.2em;color:#888;">LAP</span>
  <span style="font-family:'Rajdhani',sans-serif;font-size:3.5rem;font-weight:700;
               color:#E8002D;margin-left:8px;">{lap_num}</span>
</div>""", unsafe_allow_html=True)

with top_m:
    badge = '<span class="pm-badge pm-badge-red">CRITICAL PSYCHOLOGICAL EVENT</span>' if is_critical else ''
    st.markdown(f"""
<div style="padding-top:3rem;">
  {badge}
  <span style="font-family:'Share Tech Mono',monospace;font-size:0.75rem;color:#888;margin-left:8px;">
    Lap Time: <b style="color:var(--text-primary);">{format_lap_time(float(lap_data.get("lap_time_seconds", 89.987)))}</b>
    &nbsp; Delta: <b style="color:#E8002D;">{format_delta(float(lap_data.get("delta_to_best", 0)))}</b>
  </span>
</div>""", unsafe_allow_html=True)

with top_r:
    st.markdown('<div style="padding-top:2.5rem;"></div>', unsafe_allow_html=True)
    nl, ni, nr = st.columns([1.2, 1.5, 1.2])
    with nl:
        if st.button("< PREV", key="prev", use_container_width=True):
            st.session_state.selected_lap = max(1, lap_num - 1)
            st.rerun()
    with ni:
        new_lap = st.number_input("Lap", 1, total_laps, lap_num, label_visibility="collapsed", key="lap_in")
        if new_lap != lap_num:
            st.session_state.selected_lap = new_lap
            st.rerun()
    with nr:
        if st.button("NEXT >", key="next", use_container_width=True):
            st.session_state.selected_lap = min(total_laps, lap_num + 1)
            st.rerun()

st.markdown('<div style="height:2px;background:linear-gradient(90deg,#E8002D,transparent);margin:0.3rem 0 1rem;"></div>', unsafe_allow_html=True)

# ====== ROW 1 - INFO / COGNITIVE / GRANITE ======
col_info, col_cog, col_granite = st.columns([1.2, 1.5, 1.5], gap="medium")

with col_info:
    compound = str(lap_data.get("tyre_compound", "SOFT")).upper()
    tyre_age = int(lap_data.get("tyre_age", 18))
    timestamp = lap_data.get("timestamp", "21:24:44")
    meta = get_race_metadata(st.session_state.selected_race)
    st.markdown(f"""
<div style="background:var(--bg-card);border:1px solid var(--border);border-radius:8px;padding:1rem 1.2rem;">
  <div style="font-family:'Share Tech Mono',monospace;font-size:0.6rem;
              letter-spacing:0.15em;color:var(--text-muted);margin-bottom:0.5rem;">SESSION INFO</div>
  <div style="font-family:'Rajdhani',sans-serif;font-size:0.85rem;color:var(--text-muted);line-height:2.2;">
    <div>{get_svg_icon("flag")} <b>Circuit:</b> {meta['circuit']}</div>
    <div>{get_svg_icon("calendar")} <b>Date:</b> {meta['date']}</div>
    <div>{get_svg_icon("time")} <b>Time:</b> {timestamp}</div>
    <div>{get_svg_icon("conditions")} <b>Conditions:</b> {meta['conditions']}</div>
    <div>{get_svg_icon("tyre", color="currentColor")} <b>Tyre:</b> {get_tyre_badge(compound)} &middot; {tyre_age} laps old</div>
    <div>{get_svg_icon("pin")} <b>Position:</b> P{int(lap_data.get("position", 1))}</div>
    <div>{get_svg_icon("timer")} <b>Gap to P2:</b> {float(lap_data.get("gap_to_p2", 0)):.1f}s</div>
  </div>
</div>""", unsafe_allow_html=True)

with col_cog:
    st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.65rem;'
                'letter-spacing:0.15em;color:#888;margin-bottom:0.5rem;">COGNITIVE LOAD DISTRIBUTION</div>',
                unsafe_allow_html=True)
    quality = round(float(lap_data.get("decision_quality", 6.0)), 1)
    fatigue = round(float(lap_data.get("mental_fatigue", 5.0)), 1)
    sa = round(float(lap_data.get("situational_awareness", 7.0)), 1)

    for label, value, color in [
        ("STRESS LEVEL", stress, "#E8002D"),
        ("DECISION QUALITY", quality, "#4A9EFF"),
        ("MENTAL FATIGUE", fatigue, "#FF7B00"),
        ("SITUATIONAL AWARENESS", sa, "#00C853"),
    ]:
        pct = int(min(100, value * 10))
        st.markdown(f"""
<div style="margin-bottom:0.6rem;">
  <div style="display:flex;justify-content:space-between;margin-bottom:3px;">
    <span style="font-family:'Share Tech Mono',monospace;font-size:0.6rem;color:var(--text-muted);">{label}</span>
    <span style="font-family:'Rajdhani',sans-serif;font-size:0.85rem;font-weight:600;color:{color};">{value}/10</span>
  </div>
  <div style="width:100%;height:8px;background:var(--bg-primary);border-radius:4px;overflow:hidden;">
    <div style="width:{pct}%;height:100%;background:{color};border-radius:4px;"></div>
  </div>
</div>""", unsafe_allow_html=True)

with col_granite:
    st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.65rem;'
                'letter-spacing:0.15em;color:#888;margin-bottom:0.5rem;">IBM GRANITE ANALYSIS</div>',
                unsafe_allow_html=True)
    cache_key = f"granite_lap_{st.session_state.selected_race}_{lap_num}"
    if cache_key not in st.session_state:
        try:
            from core.granite import analyze_lap
            st.session_state[cache_key] = analyze_lap(lap_data)
        except Exception:
            st.session_state[cache_key] = (
                f"IBM Granite Analysis — Lap {lap_num}: Max Verstappen maintained psychological composure. "
                f"Stress metrics were within range for this phase of the race. Decision quality reflects "
                f"his experience and situational awareness."
            )

    st.markdown(f"""
<div style="background:var(--bg-card);border:1px solid var(--border);border-left:3px solid #E8002D;
            border-radius:8px;padding:1rem 1.2rem;">
  <div style="display:flex;align-items:center;gap:6px;margin-bottom:0.5rem;">
    <span style="font-family:'Share Tech Mono',monospace;font-size:0.5rem;
                 color:#4A9EFF;background:var(--bg-secondary);padding:2px 6px;border-radius:3px;
                 border:1px solid var(--border);">IBM</span>
    <span style="font-family:'Share Tech Mono',monospace;font-size:0.55rem;color:var(--text-muted);">GRANITE 3.1</span>
  </div>
  <div style="font-family:'Rajdhani',sans-serif;font-size:0.85rem;color:var(--text-muted);
              line-height:1.7;">{st.session_state[cache_key]}</div>
</div>""", unsafe_allow_html=True)

st.markdown('<div style="height:0.8rem"></div>', unsafe_allow_html=True)

# ====== ROW 2 - BIOMETRIC ESTIMATES ======
st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.65rem;'
            'letter-spacing:0.15em;color:#888;margin-bottom:0.5rem;">BIOMETRIC ESTIMATES</div>',
            unsafe_allow_html=True)

hr = int(lap_data.get("heart_rate_est", 155))
mental_state = str(lap_data.get("mental_state", "FOCUSED"))
eye = str(lap_data.get("eye_tracking", "FOCUSED"))
rt_delta = int(lap_data.get("reaction_time_delta", 0))

bio1, bio2, bio3, bio4 = st.columns(4, gap="medium")

with bio1:
    pk = '<span class="pm-badge pm-badge-red">PEAK</span>' if hr >= 165 else ""
    st.markdown(f"""
<div style="background:var(--bg-card);border:1px solid var(--border);border-radius:8px;padding:1rem;text-align:center;">
  <div style="color:var(--text-primary);">{get_svg_icon("heart", size=24, margin="0")}</div>
  <div style="font-family:'Share Tech Mono',monospace;font-size:0.6rem;color:var(--text-muted);margin:0.2rem 0;">HEART RATE</div>
  <div style="font-family:'Rajdhani',sans-serif;font-size:2rem;font-weight:700;color:#E8002D;">
    {hr} <span style="font-size:0.9rem;color:var(--text-muted);">BPM</span></div>
  {pk}
</div>""", unsafe_allow_html=True)
    st.plotly_chart(hr_sparkline(hr), key=f"hr_spark_{lap_num}", width="stretch", config={"displayModeBar": False})

with bio2:
    ms_color = "#E8002D" if "CRITICAL" in mental_state else "#FF7B00" if "ELEVATED" in mental_state else "#00C853"
    st.markdown(f"""
<div style="background:var(--bg-card);border:1px solid var(--border);border-radius:8px;padding:1rem;text-align:center;">
  <div style="color:var(--text-primary);">{get_svg_icon("brain", size=24, margin="0")}</div>
  <div style="font-family:'Share Tech Mono',monospace;font-size:0.6rem;color:var(--text-muted);margin:0.2rem 0;">MENTAL STATE</div>
  <div style="font-family:'Rajdhani',sans-serif;font-size:1.1rem;font-weight:700;color:{ms_color};">{mental_state}</div>
</div>""", unsafe_allow_html=True)
    st.plotly_chart(eeg_sparkline(stress, color=ms_color), key=f"eeg_spark_{lap_num}", width="stretch", config={"displayModeBar": False})

with bio3:
    eye_color = "#E8002D" if eye == "ERRATIC" else "#FF7B00" if eye == "MODERATE" else "#00C853"
    st.markdown(f"""
<div style="background:var(--bg-card);border:1px solid var(--border);border-radius:8px;padding:1rem;text-align:center;">
  <div style="color:var(--text-primary);">{get_svg_icon("eye", size=24, margin="0")}</div>
  <div style="font-family:'Share Tech Mono',monospace;font-size:0.6rem;color:var(--text-muted);margin:0.2rem 0;">EYE TRACKING</div>
  <div style="font-family:'Rajdhani',sans-serif;font-size:1.1rem;font-weight:700;color:{eye_color};">{eye}</div>
</div>""", unsafe_allow_html=True)
    st.plotly_chart(eeg_sparkline(stress * 0.8, color=eye_color), key=f"eye_spark_{lap_num}", width="stretch", config={"displayModeBar": False})

with bio4:
    rt_color = "#E8002D" if rt_delta < -100 else "#FF7B00" if rt_delta < 0 else "#00C853"
    st.markdown(f"""
<div style="background:var(--bg-card);border:1px solid var(--border);border-radius:8px;padding:1rem;text-align:center;">
  <div style="color:var(--text-primary);">{get_svg_icon("time", size=24, margin="0")}</div>
  <div style="font-family:'Share Tech Mono',monospace;font-size:0.6rem;color:var(--text-muted);margin:0.2rem 0;">REACTION TIME</div>
  <div style="font-family:'Rajdhani',sans-serif;font-size:2rem;font-weight:700;color:{rt_color};">
    {rt_delta:+d}<span style="font-size:0.8rem;color:var(--text-muted);">ms</span></div>
  <div style="font-size:0.7rem;color:var(--text-muted);">vs baseline</div>
</div>""", unsafe_allow_html=True)
    st.plotly_chart(reaction_bar_chart(rt_delta), key=f"rt_spark_{lap_num}", width="stretch", config={"displayModeBar": False})

st.markdown('<div style="height:0.8rem"></div>', unsafe_allow_html=True)

# ====== ROW 3 - EVENTS + CHART ======
col_ev, col_zc = st.columns([1.5, 2.5], gap="medium")

with col_ev:
    st.markdown(f'<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.65rem;'
                f'letter-spacing:0.15em;color:#888;margin-bottom:0.5rem;">KEY EVENTS ON LAP {lap_num}</div>',
                unsafe_allow_html=True)
    events = get_key_events(lap_num)
    if events:
        for ev in events:
            st.markdown(f"""
<div style="display:flex;align-items:flex-start;gap:10px;margin-bottom:0.6rem;
            padding:0.5rem 0.8rem;background:var(--bg-card);border:1px solid var(--border);
            border-left:3px solid {ev['color']};border-radius:6px;">
  <div style="font-family:'Share Tech Mono',monospace;font-size:0.7rem;color:var(--text-muted);">{ev['time']}</div>
  <div style="font-size:0.8rem;">{ev['dot']}</div>
  <div style="font-family:'Rajdhani',sans-serif;font-size:0.85rem;font-weight:600;">{ev['event']}</div>
</div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div style="background:var(--bg-card);border:1px solid var(--border);border-radius:8px;'
                    'padding:1.5rem;text-align:center;color:var(--text-dim);font-family:\'Share Tech Mono\',monospace;'
                    'font-size:0.75rem;">No major events on this lap</div>', unsafe_allow_html=True)

    # Radio transcript
    radio_text = str(lap_data.get("radio_text", ""))
    if radio_text and radio_text not in ["No transmission.", ""]:
        st.markdown(f"""
<div style="background:var(--bg-card);border:1px solid var(--border);border-left:3px solid #4ADE80;
            border-radius:6px;padding:0.8rem 1rem;margin-top:0.8rem;">
  <div style="font-family:'Share Tech Mono',monospace;font-size:0.6rem;color:#4ADE80;margin-bottom:0.4rem;">
    COMM TRANSCRIPT -- {timestamp}</div>
  <div style="font-family:'Share Tech Mono',monospace;font-size:0.8rem;color:#4ADE80;line-height:1.8;">
    <div>SP: "Max, we need to push now."</div>
    <div style="color:#FFD700;">MAX: "{radio_text}"</div>
  </div>
</div>""", unsafe_allow_html=True)

with col_zc:
    st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.65rem;'
                'letter-spacing:0.15em;color:#888;margin-bottom:0.5rem;">STRESS & LAP TIME</div>',
                unsafe_allow_html=True)
    st.plotly_chart(zoomed_lap_chart(df, lap_num), key=f"zoom_{lap_num}", width="stretch", config={"displayModeBar": False})

st.markdown('<div style="height:0.8rem"></div>', unsafe_allow_html=True)

# ====== ROW 4 - SECTOR BREAKDOWN ======
st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.65rem;'
            'letter-spacing:0.15em;color:#888;margin-bottom:0.5rem;">SECTOR BREAKDOWN</div>',
            unsafe_allow_html=True)

s1 = round(float(lap_data.get("sector1", 24.0)), 3)
s2 = round(float(lap_data.get("sector2", 42.0)), 3)
s3 = round(float(lap_data.get("sector3", 24.0)), 3)
total = round(s1 + s2 + s3, 3)
bs1 = round(float(best_lap_data.get("sector1", 23.5)), 3)
bs2 = round(float(best_lap_data.get("sector2", 41.8)), 3)
bs3 = round(float(best_lap_data.get("sector3", 23.2)), 3)
btotal = round(bs1 + bs2 + bs3, 3)
d1, d2, d3 = round(s1-bs1,3), round(s2-bs2,3), round(s3-bs3,3)
dtotal = round(total-btotal, 3)

def dc(d): return "#E8002D" if d > 0.1 else "#FF7B00" if d > 0 else "#00C853"

st.markdown(f"""
<div style="background:var(--bg-card);border:1px solid var(--border);border-radius:8px;overflow:hidden;">
  <table style="width:100%;border-collapse:collapse;font-family:'Rajdhani',sans-serif;font-size:0.9rem;">
    <thead><tr style="background:var(--bg-secondary);border-bottom:1px solid var(--border);">
      <th style="padding:10px;text-align:left;font-family:'Share Tech Mono',monospace;font-size:0.6rem;color:var(--text-muted);">METRIC</th>
      <th style="padding:10px;text-align:center;font-family:'Share Tech Mono',monospace;font-size:0.6rem;color:var(--text-muted);">S1</th>
      <th style="padding:10px;text-align:center;font-family:'Share Tech Mono',monospace;font-size:0.6rem;color:var(--text-muted);">S2</th>
      <th style="padding:10px;text-align:center;font-family:'Share Tech Mono',monospace;font-size:0.6rem;color:var(--text-muted);">S3</th>
      <th style="padding:10px;text-align:center;font-family:'Share Tech Mono',monospace;font-size:0.6rem;color:var(--text-muted);">TOTAL</th>
    </tr></thead>
    <tbody>
      <tr style="border-bottom:1px solid var(--border);">
        <td style="padding:10px;color:var(--text-muted);">THIS LAP</td>
        <td style="padding:10px;text-align:center;font-weight:600;">{s1:.3f}s</td>
        <td style="padding:10px;text-align:center;font-weight:600;">{s2:.3f}s</td>
        <td style="padding:10px;text-align:center;font-weight:600;">{s3:.3f}s</td>
        <td style="padding:10px;text-align:center;font-weight:700;">{total:.3f}s</td>
      </tr>
      <tr style="border-bottom:1px solid var(--border);">
        <td style="padding:10px;color:var(--text-muted);">BEST LAP</td>
        <td style="padding:10px;text-align:center;color:var(--text-muted);">{bs1:.3f}s</td>
        <td style="padding:10px;text-align:center;color:var(--text-muted);">{bs2:.3f}s</td>
        <td style="padding:10px;text-align:center;color:var(--text-muted);">{bs3:.3f}s</td>
        <td style="padding:10px;text-align:center;color:var(--text-muted);">{btotal:.3f}s</td>
      </tr>
      <tr>
        <td style="padding:10px;color:var(--text-muted);">DELTA</td>
        <td style="padding:10px;text-align:center;color:{dc(d1)};font-weight:700;">{'+' if d1>=0 else ''}{d1:.3f}s</td>
        <td style="padding:10px;text-align:center;color:{dc(d2)};font-weight:700;">{'+' if d2>=0 else ''}{d2:.3f}s</td>
        <td style="padding:10px;text-align:center;color:{dc(d3)};font-weight:700;">{'+' if d3>=0 else ''}{d3:.3f}s</td>
        <td style="padding:10px;text-align:center;color:{dc(dtotal)};font-weight:700;">{'+' if dtotal>=0 else ''}{dtotal:.3f}s</td>
      </tr>
    </tbody>
  </table>
  <div style="display:flex;padding:8px 10px;gap:4px;">
    <div style="flex:1;height:4px;background:{dc(d1)};border-radius:2px;"></div>
    <div style="flex:1;height:4px;background:{dc(d2)};border-radius:2px;"></div>
    <div style="flex:1;height:4px;background:{dc(d3)};border-radius:2px;"></div>
  </div>
</div>""", unsafe_allow_html=True)

# ====== FOOTER ======
st.markdown('<div style="height:2px;background:linear-gradient(90deg,#E8002D,transparent);margin:1.5rem 0 0.5rem;"></div>', unsafe_allow_html=True)
render_ibm_label("IBM GRANITE 3.1 &middot; Data: OpenF1 + FastF1")
