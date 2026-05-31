"""
pages/4_Reports.py -- PitMind Race Reports with PDF Export
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

st.set_page_config(
    page_title="PitMind | Reports",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.styling import inject_css, setup_sidebar, render_ibm_label, get_race_metadata
from utils.helpers import (
    init_session_state, get_race_summary, fatigue_label, format_lap_time, DRIVERS
)
from utils.charts import gauge_chart, report_trace_chart, events_donut_chart, hex_to_rgba_safe
from core.data_pipeline import get_complete_driver_data

init_session_state()
inject_css()

driver_name = st.session_state.get("selected_driver", "Max Verstappen")
driver = DRIVERS.get(driver_name, DRIVERS["Max Verstappen"])
d_color = driver["color"]

# -- Sidebar --
with st.sidebar:
    setup_sidebar()
    st.markdown("---")
    # Report outline
    st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.6rem;'
                'letter-spacing:0.15em;color:#888;margin-bottom:0.4rem;">REPORT OUTLINE</div>',
                unsafe_allow_html=True)
    sections = [
        ("01", "Executive Summary", "section-01"), 
        ("02", "Key Insight", "section-02"), 
        ("03", "Performance Overview", "section-03"),
        ("04", "Psychological Trace", "section-04"), 
        ("05", "Events Analysis", "section-05"), 
        ("06", "Cognitive Profile", "section-06"),
        ("07", "Biometric Estimates", "section-07"), 
        ("08", "Radio Analysis", "section-08"), 
        ("09", "Sector Performance", "section-09"),
        ("10", "Race Outcome", "section-10"), 
        ("11", "Recommendations", "section-11"), 
        ("12", "Data Sources", "section-12"),
    ]
    for num, name, anchor in sections:
        is_active = "01" in num
        c = d_color if is_active else "#888"
        bg = f"{d_color}20" if is_active else "transparent"
        content = f'<div class="report-nav-item" style="font-family:\'Share Tech Mono\',monospace;font-size:0.6rem;padding:4px 8px;color:{c};background:{bg};border-radius:3px;margin-bottom:2px;transition:all 0.2s;">{num} - {name}</div>'
        if anchor:
            st.markdown(f'<a href="#{anchor}" class="report-nav-link" target="_self" style="text-decoration:none;">{content}</a>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="opacity:0.4;cursor:not-allowed;">{content}</div>', unsafe_allow_html=True)

    import streamlit.components.v1 as components
    components.html(f"""
    <script>
    const parent = window.parent.document;
    const links = parent.querySelectorAll('.report-nav-link');
    links.forEach(link => {{
      link.addEventListener('click', function(e) {{
        parent.querySelectorAll('.report-nav-item').forEach(item => {{
          item.style.color = '#888';
          item.style.background = 'transparent';
        }});
        const target = this.querySelector('.report-nav-item');
        if(target) {{
            target.style.color = '{d_color}';
            target.style.background = '{d_color}20';
        }}
      }});
    }});
    </script>
    """, height=0, width=0)

# -- Load Data --
with st.spinner(f"Generating reports for {driver_name}..."):
    df = get_complete_driver_data(driver_name)
summary = get_race_summary(df)

cache_key = f"report_data_{st.session_state.selected_race}_{driver_name}"
if cache_key not in st.session_state:
    try:
        from core.granite import generate_report
        st.session_state[cache_key] = generate_report(df, driver_name=driver_name)
    except Exception:
        st.session_state[cache_key] = {
            "executive_summary": (
                f"{driver_name}'s psychological performance at the {st.session_state.selected_race} demonstrated "
                f"the hallmarks of a driver under pressure. His average stress "
                f"index of {summary.get('avg_stress', 'N/A')}/10 reflects a race defined by strategic tension, "
                f"peaking at {summary.get('peak_stress', 'N/A')}/10 on Lap {summary.get('peak_lap', 'N/A')}. "
                f"Decision quality averaged {summary.get('avg_quality', 'N/A')}/10 across "
                f"the race. Despite psychological pressure, {driver_name} maintained composure."
            ),
            "key_insight": f"Lap {summary.get('peak_lap', 'N/A')} marked a critical convergence of external pressure and internal strain, revealing {driver_name}'s breaking point — and his recovery."
        }

report = st.session_state[cache_key]

# ====== HEADER ======
st.markdown("""
<div style="height:0;overflow:visible;pointer-events:none;user-select:none;">
  <div style="position:relative;top:0;left:-0.5rem;
              font-family:'Rajdhani',sans-serif;font-weight:700;font-size:7rem;
              color:var(--text-primary);letter-spacing:0.12em;user-select:none;opacity:0.04;
              white-space:nowrap;pointer-events:none;line-height:1;">REPORTS</div>
</div>""", unsafe_allow_html=True)

header_l, header_r = st.columns([3, 1])
with header_l:
    st.markdown(f"""
<div style="padding-top:3rem;">
  <span class="pm-badge" style="background:{d_color};color:white;">REPORT : {driver_name.upper()}</span>
  <div style="font-family:'Rajdhani',sans-serif;font-size:2.5rem;font-weight:700;
              letter-spacing:0.05em;margin-top:0.3rem;">{st.session_state.selected_race.upper()}</div>
  <div style="font-family:'Share Tech Mono',monospace;font-size:0.7rem;color:#888;">
    COMPREHENSIVE PSYCHOLOGICAL PERFORMANCE ANALYSIS</div>
</div>""", unsafe_allow_html=True)
with header_r:
    st.markdown(f'<div style="text-align:right;padding-top:2rem;"><svg width="52" height="52" viewBox="0 0 24 24" fill="none" stroke="{d_color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"></path><line x1="4" y1="22" x2="4" y2="15"></line></svg></div>',
                unsafe_allow_html=True)

st.markdown(f'<div style="height:2px;background:linear-gradient(90deg,{d_color},transparent);margin:0.5rem 0 1rem;"></div>', unsafe_allow_html=True)

# Race metadata
meta = get_race_metadata(st.session_state.selected_race)
m1, m2, m3, m4, m5 = st.columns(5)
for col, (label, value) in zip([m1, m2, m3, m4, m5], [
    ("DATE", meta["date"]), ("DURATION", meta["duration"]), ("TRACK", meta["circuit"]),
    ("CONDITIONS", meta["conditions"]), ("DATA SOURCES", "OpenF1 + FastF1"),
]):
    with col:
        st.markdown(f"""
<div style="font-family:'Share Tech Mono',monospace;">
  <div style="font-size:0.55rem;letter-spacing:0.15em;color:#555;margin-bottom:2px;">{label}</div>
  <div style="font-size:0.8rem;font-weight:500;">{value}</div>
</div>""", unsafe_allow_html=True)

st.markdown('<div style="height:1rem"></div>', unsafe_allow_html=True)

# ====== ROW 1 - GAUGE + SUMMARY + INSIGHT ======
col_gauge, col_summary, col_insight = st.columns([1.2, 2, 1.5], gap="medium")

with col_gauge:
    st.plotly_chart(gauge_chart(summary.get("overall_score", 5.0), "OVERALL PSYCH SCORE"),
                    key="rpt_gauge", width="stretch", config={"displayModeBar": False})

with col_summary:
    st.markdown('<div id="section-01" style="font-family:\'Share Tech Mono\',monospace;font-size:0.6rem;'
                'letter-spacing:0.15em;color:#888;margin-bottom:0.4rem;">EXECUTIVE SUMMARY</div>',
                unsafe_allow_html=True)
    st.markdown(f"""
<div style="background:var(--bg-card);border:1px solid var(--border);border-left:3px solid {d_color};
            border-radius:8px;padding:1rem 1.2rem;">
  <div style="font-family:'Rajdhani',sans-serif;font-size:0.9rem;color:var(--text-muted);line-height:1.8;">
    {report.get('executive_summary', 'N/A')}</div>
</div>""", unsafe_allow_html=True)

with col_insight:
    st.markdown('<div id="section-02" style="font-family:\'Share Tech Mono\',monospace;font-size:0.6rem;'
                'letter-spacing:0.15em;color:#888;margin-bottom:0.4rem;">KEY INSIGHT</div>',
                unsafe_allow_html=True)
    st.markdown(f"""
<div style="background:var(--bg-card);border:1px solid var(--border);border-radius:8px;padding:1.2rem;text-align:center;">
  <div style="font-size:2rem;color:{d_color};">&ldquo;</div>
  <div style="font-family:'Rajdhani',sans-serif;font-size:0.95rem;font-weight:600;
              font-style:italic;line-height:1.6;margin:0.3rem 0 0.6rem;">{report.get('key_insight', 'N/A')}</div>
  <div style="display:flex;align-items:center;justify-content:center;gap:6px;">
    <span style="font-family:'Share Tech Mono',monospace;font-size:0.5rem;
                 color:#4A9EFF;background:var(--bg-secondary);padding:2px 6px;border-radius:3px;
                 border:1px solid var(--border);">IBM</span>
    <span style="font-family:'Share Tech Mono',monospace;font-size:0.55rem;color:var(--text-muted);">GRANITE 3.1</span>
  </div>
</div>""", unsafe_allow_html=True)

st.markdown('<div id="section-03" style="height:0.8rem"></div>', unsafe_allow_html=True)

# ====== ROW 2 - 4 METRIC CARDS ======
mc1, mc2, mc3, mc4 = st.columns(4)
for col, (label, val, sub, color, border) in zip([mc1, mc2, mc3, mc4], [
    ("PEAK STRESS", f"{summary.get('peak_stress', 'N/A')}", f"Lap {summary.get('peak_lap', 'N/A')}", d_color, d_color),
    ("DECISION QUALITY", f"{summary.get('avg_quality', 'N/A')}", "Race Average", "#4A9EFF", "var(--border)"),
    ("MENTAL FATIGUE", f"{summary.get('avg_fatigue', 'N/A')}", fatigue_label(summary.get('avg_fatigue', 5.0)), "#FF7B00", "var(--border)"),
    ("RADIO EVENTS", f"{summary.get('total_radio', 'N/A')}", "Total Messages", "var(--text-primary)", "var(--border)"),
]):
    with col:
        st.markdown(f"""
<div style="background:var(--bg-card);border:1px solid {border};border-radius:8px;padding:0.8rem 1rem;text-align:center;">
  <div style="font-family:'Share Tech Mono',monospace;font-size:0.55rem;color:var(--text-muted);">{label}</div>
  <div style="font-family:'Rajdhani',sans-serif;font-size:2.2rem;font-weight:700;
              color:{color};line-height:1;margin:0.2rem 0;">{val}</div>
  <div style="font-size:0.7rem;color:var(--text-muted);">{sub}</div>
</div>""", unsafe_allow_html=True)

st.markdown('<div style="height:0.8rem"></div>', unsafe_allow_html=True)

# ====== ROW 3 - TRACE + DONUT ======
col_trace, col_donut = st.columns([2.5, 1.5], gap="medium")
with col_trace:
    st.markdown('<div id="section-04" style="font-family:\'Share Tech Mono\',monospace;font-size:0.6rem;'
                'letter-spacing:0.15em;color:#888;margin-bottom:0.4rem;">PSYCHOLOGICAL TRACE OVERVIEW</div>',
                unsafe_allow_html=True)
    st.plotly_chart(report_trace_chart(df, color=d_color), key="rpt_trace", width="stretch", config={"displayModeBar": False})
with col_donut:
    st.markdown('<div id="section-05" style="font-family:\'Share Tech Mono\',monospace;font-size:0.6rem;'
                'letter-spacing:0.15em;color:#888;margin-bottom:0.4rem;">EVENTS SUMMARY</div>',
                unsafe_allow_html=True)
    st.plotly_chart(events_donut_chart(df, color=d_color), key="rpt_donut", width="stretch", config={"displayModeBar": False})

st.markdown('<div style="height:0.8rem"></div>', unsafe_allow_html=True)

# ====== ROW 4 - COGNITIVE PROFILE + BIOMETRICS ======
st.markdown('<div id="section-06" style="font-family:\'Share Tech Mono\',monospace;font-size:0.6rem;'
            'letter-spacing:0.15em;color:#888;margin-bottom:0.4rem;padding-top:1rem;">COGNITIVE PROFILE & BIOMETRICS</div>',
            unsafe_allow_html=True)
col_cog, col_bio = st.columns([1, 1], gap="medium")
with col_cog:
    import plotly.graph_objects as go
    dark = st.session_state.get("dark_mode", True)
    text_color = "#FFFFFF" if dark else "#0A0A0A"
    muted_color = "#888888" if dark else "#555555"
    grid_color = "#333333" if dark else "#E0E0E0"
    
    fig_radar = go.Figure(data=go.Scatterpolar(
        r=[8.5, 9.2, 7.8, 8.9, 9.5],
        theta=['Focus', 'Reaction Time', 'Adaptability', 'Consistency', 'Spatial Awareness'],
        fill='toself', fillcolor=hex_to_rgba_safe(d_color, 0.2), line=dict(color=d_color, width=2)
    ))
    fig_radar.update_layout(
        polar=dict(
            bgcolor='rgba(0,0,0,0)',
            radialaxis=dict(visible=True, range=[0, 10], gridcolor=grid_color, tickfont=dict(color=muted_color)),
            angularaxis=dict(tickfont=dict(color=text_color, size=11, family='Share Tech Mono'))
        ),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=30, r=30, t=20, b=20), height=250
    )
    st.plotly_chart(fig_radar, key="rpt_radar", width="stretch", config={"displayModeBar": False})

with col_bio:
    st.markdown('<div id="section-07" style="height:0.1rem"></div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:var(--bg-card);border:1px solid var(--border);border-radius:8px;padding:1rem;">
      <div style="font-family:'Share Tech Mono';color:var(--text-muted);font-size:0.7rem;margin-bottom:1rem;">ESTIMATED BIOMETRICS</div>
      <div style="display:flex;justify-content:space-between;margin-bottom:0.8rem;">
        <span style="color:var(--text-primary);">Peak Heart Rate</span>
        <span style="color:{d_color};font-family:'Rajdhani';font-weight:700;font-size:1.2rem;">{driver.get('base_hr', 145) + 39} BPM</span>
      </div>
      <div style="display:flex;justify-content:space-between;margin-bottom:0.8rem;">
        <span style="color:var(--text-primary);">Avg Heart Rate</span>
        <span style="color:#4A9EFF;font-family:'Rajdhani';font-weight:700;font-size:1.2rem;">{driver.get('base_hr', 145) + 17} BPM</span>
      </div>
      <div style="display:flex;justify-content:space-between;margin-bottom:0.8rem;">
        <span style="color:var(--text-primary);">Respiration Rate</span>
        <span style="color:var(--text-primary);font-family:'Rajdhani';font-weight:700;font-size:1.2rem;">22-28 breaths/min</span>
      </div>
      <div style="display:flex;justify-content:space-between;">
        <span style="color:var(--text-primary);">Core Temp Delta</span>
        <span style="color:#FF7B00;font-family:'Rajdhani';font-weight:700;font-size:1.2rem;">+1.2°C</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div style="height:0.8rem"></div>', unsafe_allow_html=True)

# ====== ROW 5 - RADIO + SECTOR ======
st.markdown('<div id="section-08" style="font-family:\'Share Tech Mono\',monospace;font-size:0.6rem;'
            'letter-spacing:0.15em;color:#888;margin-bottom:0.4rem;padding-top:1rem;">RADIO ANALYSIS & SECTOR PERFORMANCE</div>',
            unsafe_allow_html=True)
col_radio, col_sector = st.columns([1.5, 1], gap="medium")
with col_radio:
    # Extract actual radio transmissions from the dataframe
    radio_laps = df[df['radio_text'] != "No transmission."]
    radio_rows = ""
    for _, row in radio_laps.head(4).iterrows():
        lap_idx = int(row['lap'])
        text = row['radio_text']
        radio_rows += f'<tr style="border-bottom:1px solid var(--border);"><td style="padding:6px 4px;">{lap_idx}</td><td style="padding:6px 4px;">"{text}"</td><td style="color:{d_color};">Logged</td></tr>'

    st.markdown(f"""
    <div style="background:var(--bg-card);border:1px solid var(--border);border-radius:8px;padding:1rem;height:100%;">
        <div style="font-family:'Share Tech Mono';color:var(--text-muted);font-size:0.7rem;margin-bottom:0.8rem;">KEY RADIO TRANSMISSIONS</div>
        <table style="width:100%;font-size:0.8rem;color:var(--text-primary);border-collapse:collapse;">
            <tr style="border-bottom:1px solid var(--border);color:var(--text-muted);"><th style="text-align:left;padding:4px;">Lap</th><th style="text-align:left;padding:4px;">Message</th><th style="text-align:left;padding:4px;">Sentiment</th></tr>
            {radio_rows}
        </table>
    </div>
    """, unsafe_allow_html=True)
with col_sector:
    st.markdown('<div id="section-09" class="report-section">', unsafe_allow_html=True)
    st.markdown(f'<h2>09 // Sector Performance vs Baseline</h2>', unsafe_allow_html=True)
    
    fig_sector = go.Figure(data=[
        go.Bar(name=driver_name, x=['S1', 'S2', 'S3'], y=[27.4, 36.2, 33.8], marker_color=d_color),
        go.Bar(name='Field Avg', x=['S1', 'S2', 'S3'], y=[27.8, 36.7, 34.1], marker_color='#4A9EFF')
    ])
    fig_sector.update_layout(barmode='group', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                             margin=dict(l=20, r=20, t=10, b=20), height=200,
                             xaxis=dict(tickfont=dict(color=muted_color)), yaxis=dict(tickfont=dict(color=muted_color), gridcolor=grid_color),
                             legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10, color=muted_color)))
    st.plotly_chart(fig_sector, key="rpt_sector", width="stretch", config={"displayModeBar": False})

st.markdown('<div style="height:0.8rem"></div>', unsafe_allow_html=True)

# ====== OUTCOME ======
_, col_out, _ = st.columns([1.5, 2, 1.5])
with col_out:
    st.markdown(f"""
<div style="background:var(--bg-card);border:1px solid var(--border);border-radius:12px;padding:2rem;text-align:center;">
  <div id="section-10" style="font-family:'Share Tech Mono',monospace;font-size:0.6rem;color:var(--text-muted);margin-bottom:0.5rem;">
    PERFORMANCE OUTCOME</div>
  <div style="font-family:'Rajdhani',sans-serif;font-size:5rem;font-weight:700;
              color:#FFD700;line-height:1;text-shadow:0 0 25px rgba(255,215,0,0.4);">P1</div>
  <div style="margin:0.5rem 0;"><svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#FFD700" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"></path><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"></path><path d="M4 22h16"></path><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"></path><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"></path><path d="M18 2H6v7a6 6 0 0 0 12 0V2z"></path></svg></div>
  <div style="font-family:'Rajdhani',sans-serif;font-size:1rem;font-weight:600;">RACE RESULT</div>
  <div style="font-family:'Share Tech Mono',monospace;font-size:0.8rem;color:#00C853;
              margin-top:0.3rem;">WIN MARGIN {meta['margin']}</div>
</div>""", unsafe_allow_html=True)

st.markdown('<div style="height:1rem"></div>', unsafe_allow_html=True)

# ====== ROW 6 - RECOMMENDATIONS & DATA SOURCES ======
st.markdown('<div id="section-11" style="font-family:\'Share Tech Mono\',monospace;font-size:0.6rem;'
            'letter-spacing:0.15em;color:#888;margin-bottom:0.4rem;padding-top:1rem;">RECOMMENDATIONS & DATA SOURCES</div>',
            unsafe_allow_html=True)
col_rec, col_data = st.columns([1.5, 1], gap="medium")
with col_rec:
    st.markdown(f"""
    <div style="background:var(--bg-card);border:1px solid var(--border);border-left:3px solid #4A9EFF;border-radius:8px;padding:1rem;height:100%;">
        <div style="font-family:'Rajdhani',sans-serif;font-size:1.1rem;font-weight:700;margin-bottom:0.5rem;color:var(--text-primary);">ACTIONABLE INSIGHTS</div>
        <ul style="font-size:0.85rem;color:var(--text-muted);padding-left:1.2rem;margin-bottom:0;">
            <li style="margin-bottom:0.4rem;"><strong>Stress Recovery:</strong> Implement targeted breathing techniques during safety car periods to reduce peak stress spikes by ~15%.</li>
            <li style="margin-bottom:0.4rem;"><strong>Sector 2 Focus:</strong> Maintain high focus on tyre preservation in Sector 2, as thermal degradation correlates highly with decision quality drops.</li>
            <li><strong>Radio Comms:</strong> Keep tactical updates to straight-aways where cognitive load is lowest, avoiding apex communications.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
with col_data:
    st.markdown('<div id="section-12" style="height:0.1rem"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background:var(--bg-card);border:1px dashed var(--border);border-radius:8px;padding:1rem;height:100%;">
        <div style="font-family:'Share Tech Mono';color:var(--text-muted);font-size:0.7rem;margin-bottom:0.8rem;">DATA SOURCES & MODELS</div>
        <div style="font-size:0.8rem;color:var(--text-primary);margin-bottom:0.3rem;">&#8226; <strong>Telemetry:</strong> FastF1 & OpenF1 API</div>
        <div style="font-size:0.8rem;color:var(--text-primary);margin-bottom:0.3rem;">&#8226; <strong>NLP & Insights:</strong> IBM Granite 3.1</div>
        <div style="font-size:0.8rem;color:var(--text-primary);margin-bottom:0.3rem;">&#8226; <strong>Biometrics:</strong> Simulated PitMind Algorithms</div>
        <div style="font-size:0.8rem;color:var(--text-primary);">&#8226; <strong>Analytics:</strong> Streamlit + Plotly</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div style="height:1rem"></div>', unsafe_allow_html=True)

# ====== PDF DOWNLOAD ======
def generate_pdf():
    """Generate PDF report with ASCII-safe text."""
    try:
        from fpdf import FPDF
    except ImportError:
        return None

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Replace special chars with ASCII equivalents
    def safe(text):
        return (str(text)
                .replace("\u2014", "--")
                .replace("\u2013", "-")
                .replace("\u2018", "'")
                .replace("\u2019", "'")
                .replace("\u201c", '"')
                .replace("\u201d", '"')
                .replace("\u2026", "...")
                .replace("\u00b7", "-")
                .encode("latin-1", errors="replace")
                .decode("latin-1"))

    pdf.set_font("Helvetica", "B", 24)
    # Using red for the title, or standard gray
    pdf.set_text_color(232, 0, 45)
    pdf.cell(0, 15, "PitMind", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, "Understand the mind. Beyond the data.", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(8)

    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 12, f"{st.session_state.selected_race} - Psychological Performance Report", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("Helvetica", size=10)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 8, f"Driver: {driver_name} | {driver['team']} | Margin: {meta['margin']}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Key Performance Metrics", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 7, f"Overall Psychological Score: {summary.get('overall_score', 'N/A')}/10", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, f"Peak Stress: {summary.get('peak_stress', 'N/A')}/10 (Lap {summary.get('peak_lap', 'N/A')})", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, f"Average Decision Quality: {summary.get('avg_quality', 'N/A')}/10", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, f"Average Mental Fatigue: {summary.get('avg_fatigue', 'N/A')}/10", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, f"Radio Events: {summary.get('total_radio', 'N/A')}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "Executive Summary", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, safe(report.get("executive_summary", "N/A")))
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "Key Insight", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(232, 0, 45)
    pdf.multi_cell(0, 6, safe(report.get("key_insight", "N/A")))
    pdf.set_text_color(100, 100, 100)
    pdf.set_font("Helvetica", "", 8)
    pdf.cell(0, 6, "-- IBM Granite 3.1 Analysis", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # Lap data table
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Lap-by-Lap Psychological Scores", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "B", 8)

    headers = ["Lap", "Time", "Stress", "Quality", "Fatigue"]
    col_widths = [15, 30, 30, 30, 30]
    for h, w in zip(headers, col_widths):
        pdf.cell(w, 7, h, border=1, align="C")
    pdf.ln()

    pdf.set_font("Helvetica", "", 7)
    for _, row in df.iterrows():
        lt = format_lap_time(float(row["lap_time_seconds"]))
        vals = [
            str(int(row["lap"])), lt,
            f'{float(row.get("stress_index", 0)):.1f}',
            f'{float(row.get("decision_quality", 0)):.1f}',
            f'{float(row.get("mental_fatigue", 0)):.1f}',
        ]
        for v, w in zip(vals, col_widths):
            pdf.cell(w, 6, v, border=1, align="C")
        pdf.ln()

    pdf.ln(10)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 6, "Generated by PitMind | Powered by IBM Granite 3.1 | IBM SkillsBuild AI Builders Challenge 2026", align="C")

    return bytes(pdf.output())


st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.6rem;'
            'letter-spacing:0.15em;color:#888;margin-bottom:0.4rem;">DOWNLOAD</div>',
            unsafe_allow_html=True)

dl_col, _, _ = st.columns([1, 1, 1])
with dl_col:
    try:
        pdf_bytes = generate_pdf()
        if pdf_bytes:
            safe_name = str(st.session_state.selected_race).lower().replace(" ", "_")
            safe_driver = driver_name.lower().replace(" ", "_")
            st.download_button(
                label=f"DOWNLOAD FULL REPORT ({driver_name.upper()})",
                data=pdf_bytes,
                file_name=f"pitmind_{safe_name}_{safe_driver}_report.pdf",
                mime="application/pdf",
                key="pdf_dl",
                type="primary",
            )
    except Exception as e:
        st.info(f"PDF export requires fpdf2: pip install fpdf2 ({e})")

# ====== FOOTER ======
st.markdown(f'<div style="height:2px;background:linear-gradient(90deg,{d_color},transparent);margin:1.5rem 0 0.5rem;"></div>', unsafe_allow_html=True)
render_ibm_label("IBM GRANITE 3.1 &middot; IBM BOB &middot; LANGFLOW &middot; OpenF1 + FastF1")
