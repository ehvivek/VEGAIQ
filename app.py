"""
app.py -- PitMind Home Page
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

st.set_page_config(
    page_title="PitMind | Performance Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from utils.styling import inject_css, get_circuit_svg, get_race_metadata, render_ibm_label, sidebar_nav, render_logo
from utils.helpers import init_session_state

init_session_state()
inject_css()

# -- Sidebar --
with st.sidebar:
    render_logo(width="140px", center=True)
    st.markdown("---")
    sidebar_nav()
    st.markdown("---")

    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = True

    new_light = st.toggle(
        "LIGHT THEME",
        value=not st.session_state.dark_mode,
        key="theme_toggle_home",
    )

    if new_light == st.session_state.dark_mode:
        st.session_state.dark_mode = not new_light
        st.rerun()

# ====== HERO SECTION ======

# Watermark — purely decorative, zero pointer events so it never blocks clicks
st.markdown("""
<div style="height:0;overflow:visible;pointer-events:none;user-select:none;">
  <div style="position:relative;top:0;left:-1rem;
              font-family:'Rajdhani',sans-serif;font-weight:700;font-size:8rem;
              color:var(--text-primary);letter-spacing:0.12em;user-select:none;
              opacity:0.04;white-space:nowrap;pointer-events:none;
              line-height:1;">VERSTAPPEN</div>
</div>""", unsafe_allow_html=True)

# Top bar
col_logo, col_spacer, col_right = st.columns([3, 3, 2])
with col_logo:
    render_logo(width="340px", center=False)

with col_right:
    st.markdown("""
<div style="text-align:right;padding-top:1rem;">
  <span style="background:#E8002D;color:white;font-family:'Share Tech Mono',monospace;
               font-size:0.6rem;letter-spacing:0.1em;padding:3px 8px;border-radius:3px;">
    VERSION: 2024
  </span>
</div>""", unsafe_allow_html=True)

st.markdown('<div style="height:2px;background:linear-gradient(90deg,#E8002D,transparent);margin:0.8rem 0;"></div>', unsafe_allow_html=True)

# ====== MAIN HERO ======
left_col, right_col = st.columns([3, 2], gap="large")

with left_col:
    st.markdown("""
<div style="border-left:3px solid #E8002D;padding-left:1rem;margin-bottom:1.5rem;">
  <div style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;
              letter-spacing:0.2em;color:#888;margin-bottom:0.3rem;">TAGLINE</div>
  <div style="font-family:'Rajdhani',sans-serif;font-size:1.6rem;font-weight:700;
              line-height:1.2;">UNDERSTAND THE MIND.<br>BEYOND THE DATA.</div>
</div>""", unsafe_allow_html=True)

    driver_col, info_col = st.columns([1, 3])
    with driver_col:
        st.markdown("""
<div style="font-family:'Rajdhani',sans-serif;font-size:5.5rem;font-weight:700;
            color:#E8002D;line-height:1;text-align:center;">1</div>
<div style="width:72px;height:72px;border-radius:50%;background:var(--bg-secondary);
            border:3px solid #E8002D;margin:0.4rem auto;display:flex;
            align-items:center;justify-content:center;font-size:2rem;overflow:hidden;">
    <img src="https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/M/MAXVER01_Max_Verstappen/maxver01.png" style="width:100%;height:100%;object-fit:cover;object-position:top;background:#1A1A1A;">
</div>""",
            unsafe_allow_html=True)

    with info_col:
        st.markdown("""
<div style="padding-top:0.5rem;">
  <div style="font-family:'Rajdhani',sans-serif;font-size:1.8rem;font-weight:700;
              letter-spacing:0.05em;">MAX VERSTAPPEN</div>
  <div style="font-family:'Share Tech Mono',monospace;font-size:0.7rem;color:#888;
              letter-spacing:0.1em;margin-bottom:0.6rem;">RED BULL RACING &middot; 4x WORLD CHAMPION</div>
  <div style="font-family:'Rajdhani',sans-serif;font-size:0.95rem;color:#888;
              line-height:1.6;max-width:380px;">
    After 4 world championships, what goes on inside his mind during a race?
    PitMind reveals the psychological story lap by lap -- stress patterns,
    decision quality, and mental fatigue that no camera shows.
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    if st.button("ANALYZE DRIVER  ->", key="cta_main"):
        st.switch_page("pages/1_Dashboard.py")

with right_col:
    # Race selector
    st.markdown("""
<div style="background:var(--bg-card);border:1px solid var(--border);border-radius:8px;
            padding:1rem 1.2rem;margin-bottom:0.8rem;">
  <div style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;
              letter-spacing:0.15em;color:var(--text-muted);margin-bottom:0.6rem;">SELECT RACE</div>""",
        unsafe_allow_html=True)
    
    def on_race_change():
        new_race = st.session_state.race_sel
        st.session_state.selected_race = new_race
        
        # Reset selected lap to peak stress lap of newly selected race
        meta = get_race_metadata(new_race)
        st.session_state.selected_lap = meta["peak_stress_lap"]
        
        # Clear cached report/db analysis to force regeneration
        st.session_state.pop("granite_db", None)
        st.session_state.pop("report_data", None)

    r_options = ["Abu Dhabi GP 2024", "Monaco GP 2024", "Bahrain GP 2024"]
    default_idx = r_options.index(st.session_state.selected_race) if st.session_state.selected_race in r_options else 0
    st.selectbox("Race", r_options, index=default_idx,
                 label_visibility="collapsed", key="race_sel", on_change=on_race_change)
    st.selectbox("Session", ["Race", "Qualifying", "Sprint"],
                 label_visibility="collapsed", key="sess_sel")
    st.markdown("</div>", unsafe_allow_html=True)

    # Track SVG
    meta = get_race_metadata(st.session_state.selected_race)
    svg = get_circuit_svg(st.session_state.selected_race)
    st.markdown(f"""
<div style="background:var(--bg-card);border:1px solid var(--border);border-radius:8px;
            padding:0.8rem 1rem;">
  <div style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;
              letter-spacing:0.15em;color:var(--text-muted);margin-bottom:0.4rem;">
    {meta['flag_entity']} {meta['circuit']}</div>
  {svg}
</div>""", unsafe_allow_html=True)

st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)

# ====== RACE STATISTICS ======
st.markdown("""
<div style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;
            letter-spacing:0.2em;color:#888;margin-bottom:0.6rem;">RACE STATISTICS</div>""",
    unsafe_allow_html=True)

# Load summary data
from utils.helpers import get_race_data, get_race_summary
df = get_race_data(st.session_state.selected_race)
summary = get_race_summary(df)

sc1, sc2, sc3, sc4 = st.columns(4)
cards_data = [
    ("NUMBER OF LAPS", str(summary["total_laps"]), st.session_state.selected_race, "var(--text-primary)", "var(--border)"),
    ("PEAK STRESS LAP", f"LAP {summary['peak_lap']}", f"Highest stress: {summary['peak_stress']}/10", "#E8002D", "#E8002D"),
    ("CRITICAL EVENTS", meta["critical_events"], meta["critical_events_desc"], "#FF7B00", "var(--border)"),
    ("RADIO TRANSMISSIONS", str(summary["total_radio"]), "Total messages", "#4A9EFF", "var(--border)"),
]
for col, (label, value, sub, color, border) in zip([sc1, sc2, sc3, sc4], cards_data):
    with col:
        st.markdown(f"""
<div style="background:var(--bg-card);border:1px solid {border};border-radius:8px;
            padding:1rem 1.2rem;text-align:center;">
  <div style="font-family:'Share Tech Mono',monospace;font-size:0.6rem;
              letter-spacing:0.15em;color:var(--text-muted);margin-bottom:0.3rem;">{label}</div>
  <div style="font-family:'Rajdhani',sans-serif;font-size:2.5rem;font-weight:700;
              color:{color};line-height:1;">{value}</div>
  <div style="font-family:'Rajdhani',sans-serif;font-size:0.8rem;color:var(--text-dim);
              margin-top:0.2rem;">{sub}</div>
</div>""", unsafe_allow_html=True)

# ====== FOOTER ======
st.markdown('<div style="height:2px;background:linear-gradient(90deg,#E8002D,transparent);margin:1.5rem 0 0.5rem;"></div>', unsafe_allow_html=True)
foot_l, foot_r = st.columns([3, 1])
with foot_l:
    render_ibm_label("IBM GRANITE 3.1 &middot; IBM BOB &middot; LANGFLOW &middot; OpenF1 + FastF1")
with foot_r:
    st.markdown("""
<div style="text-align:right;display:flex;align-items:center;justify-content:flex-end;gap:6px;">
  <span style="width:8px;height:8px;background:#00C853;border-radius:50%;
               display:inline-block;animation:pulse 2s infinite;"></span>
  <span style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;color:#00C853;">SYSTEM READY</span>
</div>""", unsafe_allow_html=True)
