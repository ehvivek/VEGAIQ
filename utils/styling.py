"""
utils/styling.py
PitMind — Complete CSS injection for dark/light theme.
Imported by every page via inject_css().
"""

import streamlit as st

DARK_CSS = """
:root {
    --bg-primary:    #0A0A0A;
    --bg-secondary:  #141414;
    --bg-card:       #1A1A1A;
    --bg-hover:      #222222;
    --text-primary:  #FFFFFF;
    --text-muted:    #888888;
    --text-dim:      #555555;
    --accent-red:    #E8002D;
    --accent-orange: #FF7B00;
    --accent-blue:   #4A9EFF;
    --accent-green:  #00C853;
    --accent-gold:   #FFD700;
    --border:        #2A2A2A;
    --border-hover:  #404040;
    --filter-icon:   brightness(0) invert(1);
}
"""

LIGHT_CSS = """
:root {
    --bg-primary:    #F5F5F5;
    --bg-secondary:  #FFFFFF;
    --bg-card:       #FAFAFA;
    --bg-hover:      #F0F0F0;
    --text-primary:  #0A0A0A;
    --text-muted:    #555555;
    --text-dim:      #999999;
    --accent-red:    #E8002D;
    --accent-orange: #FF7B00;
    --accent-blue:   #2979FF;
    --accent-green:  #00A843;
    --accent-gold:   #F5A623;
    --border:        #E0E0E0;
    --border-hover:  #CCCCCC;
    --filter-icon:   brightness(0);
}
"""

BASE_CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Share+Tech+Mono&family=Inter:wght@300;400;500;600&display=swap');

/* == Reset & Base == */
html, body, [class*="css"] {
    font-family: 'Rajdhani', 'Inter', sans-serif !important;
}

/* == HIDE default Streamlit chrome == */
footer { visibility: hidden !important; }
header { background: transparent !important; visibility: visible !important; }
.stDeployButton { display: none !important; }
header [data-testid="stStatusWidget"], 
header [data-testid="stStatusWidget"] p,
header [data-testid="stStatusWidget"] span,
header [data-testid="stToolbar"] button {
    color: var(--text-primary) !important;
}
header [data-testid="stStatusWidget"] img,
header [data-testid="stStatusWidget"] svg,
header [data-testid="stToolbar"] svg {
    filter: var(--filter-icon) !important;
}

/* Ensure sidebar expand control is always visible */
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"],
.stSidebarCollapsedControl,
button[aria-label="Expand sidebar"] {
    visibility: visible !important;
    display: flex !important;
    opacity: 1 !important;
    z-index: 999999 !important;
    color: var(--text-primary) !important;
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 4px !important;
    padding: 0.2rem !important;
    margin: 0.5rem !important;
}
[data-testid="collapsedControl"] svg,
[data-testid="stSidebarCollapsedControl"] svg,
.stSidebarCollapsedControl svg,
button[aria-label="Expand sidebar"] svg {
    fill: var(--text-primary) !important;
}

/* == HIDE Streamlit auto-generated page navigation == */
[data-testid="stSidebarNav"] { display: none !important; }
nav[data-testid="stSidebarNav"] { display: none !important; }

/* == Main app container == */
.stApp {
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

/* == Sidebar == */
section[data-testid="stSidebar"] {
    background-color: var(--bg-secondary) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] * {
    color: var(--text-primary) !important;
}
section[data-testid="stSidebar"] > div:first-child {
    padding-top: 1rem !important;
}

/* == Main content padding == */
.main .block-container {
    padding: 1.5rem 2rem 2rem !important;
    max-width: 1400px !important;
}

/* == Metric cards == */
[data-testid="metric-container"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    padding: 1rem 1.2rem !important;
}
[data-testid="stMetricLabel"] {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.12em !important;
    color: var(--text-muted) !important;
    text-transform: uppercase !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
}

/* == Buttons == */
.stButton > button {
    background: transparent !important;
    border: 1px solid var(--accent-red) !important;
    color: var(--accent-red) !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.1em !important;
    border-radius: 4px !important;
    transition: all 0.2s ease !important;
    text-transform: uppercase !important;
    cursor: pointer !important;
}
.stButton > button:hover {
    background: var(--accent-red) !important;
    color: #FFFFFF !important;
    box-shadow: 0 0 16px rgba(232, 0, 45, 0.4) !important;
}

/* == Select boxes == */
[data-testid="stSelectbox"] > div > div {
    background: var(--bg-card) !important;
    border-color: var(--border) !important;
    border-radius: 6px !important;
    color: var(--text-primary) !important;
}
[data-testid="stSelectbox"] * {
    color: var(--text-primary) !important;
}

/* == Number input == */
[data-testid="stNumberInput"] input {
    background: var(--bg-card) !important;
    border-color: var(--border) !important;
    color: var(--text-primary) !important;
    font-family: 'Share Tech Mono', monospace !important;
}
[data-testid="stNumberInput"] button {
    background: var(--bg-card) !important;
    color: var(--text-primary) !important;
}

/* == Toggle == */
[data-testid="stToggle"] label {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.1em !important;
    color: var(--text-muted) !important;
}

/* == Checkbox == */
[data-testid="stCheckbox"] label,
[data-testid="stCheckbox"] p,
[data-testid="stCheckbox"] span {
    color: var(--text-primary) !important;
}

/* == Chat messages == */
[data-testid="stChatMessage"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    margin: 0.3rem 0 !important;
}
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] div {
    color: var(--text-primary) !important;
}
[data-testid="stChatInput"] textarea {
    color: var(--text-primary) !important;
    background-color: var(--bg-card) !important;
}

/* == Dataframes == */
[data-testid="stDataFrame"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}

/* == Expander == */
[data-testid="stExpander"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}

/* == Scrollbar == */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--border-hover); }

/* == PitMind Custom Components == */

.pm-watermark {
    font-family: 'Rajdhani', sans-serif;
    font-weight: 700;
    font-size: 7rem;
    color: var(--text-primary);
    letter-spacing: 0.15em;
    text-transform: uppercase;
    user-select: none;
    pointer-events: none;
    line-height: 1;
    opacity: 0.04;
}

.pm-badge {
    display: inline-block;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 2px 8px;
    border-radius: 3px;
    border: 1px solid currentColor;
}
.pm-badge-red { color: #E8002D; border-color: #E8002D; background: rgba(232,0,45,0.1); }
.pm-badge-green { color: #00C853; border-color: #00C853; background: rgba(0,200,83,0.1); }
.pm-badge-orange { color: #FF7B00; border-color: #FF7B00; background: rgba(255,123,0,0.1); }

/* Pulsing dot animation */
@keyframes pulse {
    0%   { opacity: 1; transform: scale(1); box-shadow: 0 0 0 0 rgba(232,0,45,0.6); }
    50%  { opacity: 0.7; transform: scale(1.1); box-shadow: 0 0 0 6px rgba(232,0,45,0); }
    100% { opacity: 1; transform: scale(1); box-shadow: 0 0 0 0 rgba(232,0,45,0); }
}

.pm-terminal {
    background: #0D1117;
    border: 1px solid #2A2A2A;
    border-left: 3px solid #4ADE80;
    border-radius: 6px;
    padding: 1rem 1.2rem;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.8rem;
    color: #4ADE80;
    line-height: 1.8;
}

/* Page link styling */
.stPageLink > a {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.08em !important;
}
"""

YAS_MARINA_SVG = """
<svg width="100%" height="180" viewBox="0 0 400 180" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="glow">
      <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
      <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <path d="M 60 90 L 80 40 L 140 30 L 200 35 L 250 30 L 310 40 L 340 70
           L 340 100 L 320 120 L 300 130 L 280 135 L 260 130 L 240 120
           L 220 115 L 200 120 L 180 130 L 160 140 L 140 145 L 120 140
           L 100 130 L 80 120 L 60 115 Z"
        fill="none" stroke="#2A2A2A" stroke-width="14" stroke-linejoin="round"/>
  <path d="M 60 90 L 80 40 L 140 30 L 200 35 L 250 30 L 310 40 L 340 70
           L 340 100 L 320 120 L 300 130 L 280 135 L 260 130 L 240 120
           L 220 115 L 200 120 L 180 130 L 160 140 L 140 145 L 120 140
           L 100 130 L 80 120 L 60 115 Z"
        fill="none" stroke="#E8002D" stroke-width="2.5" stroke-linejoin="round"
        filter="url(#glow)"/>
  <circle cx="60" cy="90" r="6" fill="#E8002D" filter="url(#glow)"/>
  <text x="30" y="88" fill="#888888" font-size="9" font-family="monospace">S/F</text>
  <text x="155" y="22" fill="#444" font-size="7" font-family="monospace">T1</text>
  <text x="320" y="60" fill="#444" font-size="7" font-family="monospace">T8</text>
  <text x="310" y="140" fill="#444" font-size="7" font-family="monospace">T14</text>
  <text x="100" y="155" fill="#444" font-size="7" font-family="monospace">T19</text>
  <text x="165" y="90" fill="#333" font-size="11" font-weight="600" text-anchor="middle">YAS MARINA</text>
</svg>
"""

MONACO_SVG = """
<svg width="100%" height="180" viewBox="0 0 400 180" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="glow">
      <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
      <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <path d="M 60 140 L 40 100 L 70 80 L 100 85 L 140 60 L 180 50 L 230 65 L 250 85
           L 220 95 L 200 90 L 180 105 L 190 120 L 230 115 L 270 125 L 320 120 L 350 140
           L 300 150 L 240 145 L 160 150 L 100 145 Z"
        fill="none" stroke="#2A2A2A" stroke-width="14" stroke-linejoin="round"/>
  <path d="M 60 140 L 40 100 L 70 80 L 100 85 L 140 60 L 180 50 L 230 65 L 250 85
           L 220 95 L 200 90 L 180 105 L 190 120 L 230 115 L 270 125 L 320 120 L 350 140
           L 300 150 L 240 145 L 160 150 L 100 145 Z"
        fill="none" stroke="#E8002D" stroke-width="2.5" stroke-linejoin="round"
        filter="url(#glow)"/>
  <circle cx="60" cy="140" r="6" fill="#E8002D" filter="url(#glow)"/>
  <text x="35" y="145" fill="#888888" font-size="9" font-family="monospace">S/F</text>
  <text x="180" y="42" fill="#444" font-size="7" font-family="monospace">CASINO</text>
  <text x="320" y="110" fill="#444" font-size="7" font-family="monospace">TUNNEL</text>
  <text x="300" y="165" fill="#444" font-size="7" font-family="monospace">TABAC</text>
  <text x="210" y="100" fill="#333" font-size="11" font-weight="600" text-anchor="middle">CIRCUIT DE MONACO</text>
</svg>
"""

BAHRAIN_SVG = """
<svg width="100%" height="180" viewBox="0 0 400 180" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="glow">
      <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
      <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <path d="M 80 150 L 80 40 L 140 30 L 180 60 L 140 80 L 200 100 L 250 80 L 280 110
           L 240 130 L 220 120 L 180 145 L 140 135 L 110 150 Z"
        fill="none" stroke="#2A2A2A" stroke-width="14" stroke-linejoin="round"/>
  <path d="M 80 150 L 80 40 L 140 30 L 180 60 L 140 80 L 200 100 L 250 80 L 280 110
           L 240 130 L 220 120 L 180 145 L 140 135 L 110 150 Z"
        fill="none" stroke="#E8002D" stroke-width="2.5" stroke-linejoin="round"
        filter="url(#glow)"/>
  <circle cx="80" cy="150" r="6" fill="#E8002D" filter="url(#glow)"/>
  <text x="55" y="155" fill="#888888" font-size="9" font-family="monospace">S/F</text>
  <text x="80" y="25" fill="#444" font-size="7" font-family="monospace">T1</text>
  <text x="210" y="65" fill="#444" font-size="7" font-family="monospace">T4</text>
  <text x="290" y="110" fill="#444" font-size="7" font-family="monospace">T10</text>
  <text x="180" y="90" fill="#333" font-size="11" font-weight="600" text-anchor="middle">SAKHIR CIRCUIT</text>
</svg>
"""


def get_circuit_svg(race_name: str) -> str:
    """Return circuit SVG based on selected race name."""
    name = str(race_name).lower()
    if "monaco" in name:
        return MONACO_SVG
    elif "bahrain" in name:
        return BAHRAIN_SVG
    else:
        return YAS_MARINA_SVG


def get_svg_icon(name: str, size=14, color="currentColor", margin="4px") -> str:
    if name == "ibm":
        w = int(size * 2.68)
        return f'<svg width="{w}" height="{size}" viewBox="0 0 1075 401.15" fill="{color}" style="vertical-align:middle;margin-right:{margin};display:inline-block;"><g><rect y="373.17" width="194.43" height="27.932"/><rect y="319.83" width="194.43" height="27.932"/><rect x="55.468" y="266.54" width="83.399" height="27.932"/><rect x="55.468" y="213.25" width="83.399" height="27.932"/><rect x="55.468" y="159.96" width="83.399" height="27.932"/><rect x="55.468" y="106.58" width="83.399" height="27.932"/><rect y="53.288" width="194.43" height="27.932"/><rect width="194.43" height="27.932"/><path d="m222.17 400.85 207.11 0.297c27.734 0 52.793-10.697 71.513-27.932h-278.62z"/><path d="m222.17 347.76h299.03c5.051-8.617 8.815-18.027 11.094-27.932h-310.12z"/><rect x="277.73" y="266.54" width="83.3" height="27.932"/><path d="m444.43 266.54v27.932h90.927c0-9.608-1.288-19.017-3.764-27.932z"/><path d="m497.92 213.25h-220.19v27.932h243.46c-6.34-10.698-14.165-20.107-23.277-27.932z"/><path d="m277.73 159.96v27.932h220.19c9.311-7.825 17.135-17.235 23.277-27.932z"/><rect x="277.73" y="106.58" width="83.3" height="27.932"/><path d="m444.43 134.51h87.163c2.476-8.914 3.764-18.324 3.764-27.932h-90.927z"/><path d="m521.2 53.288h-299.03v27.932h310.12c-2.575-9.905-6.339-19.314-11.093-27.932z"/><path d="m429.28 0h-207.11v27.932h278.53c-18.621-17.235-43.878-27.932-71.414-27.932z"/><polygon points="555.57 81.22 742.67 81.22 733.06 53.288 555.57 53.288"/><polygon points="555.57 27.932 724.25 27.932 714.64 0 555.57 0"/><polygon points="861.03 401.17 861.03 373.24 1e3 373.24 1e3 401.17"/><polygon points="861.03 347.76 861.03 319.83 1e3 319.83 1e3 347.76"/><polygon points="777.73 182.54 769.91 159.96 694.43 159.96 611.03 159.96 611.03 187.89 694.43 187.89 694.43 162.24 703.25 187.89 852.22 187.89 861.03 162.24 861.03 187.89 944.43 187.89 944.43 159.96 861.03 159.96 785.56 159.96"/><polygon points="944.43 106.58 803.98 106.58 794.37 134.51 944.43 134.51"/><polygon points="1e3 27.932 1e3 0 840.93 0 831.32 27.932"/><polygon points="768.13 373.22 777.73 400.85 787.34 373.22"/><polygon points="749.5 319.83 759.31 347.76 796.16 347.76 806.06 319.83"/><polygon points="730.78 266.54 740.59 294.47 814.88 294.47 824.68 266.54"/><polygon points="721.97 241.18 833.6 241.18 843.11 213.25 712.36 213.25"/><polygon points="611.03 134.51 761.09 134.51 751.49 106.58 611.03 106.58"/><polygon points="1e3 53.288 822.4 53.288 812.9 81.22 1e3 81.22"/><rect x="555.57" y="373.22" width="138.97" height="27.932"/><rect x="555.57" y="319.83" width="138.97" height="27.932"/><rect x="611.03" y="266.54" width="83.399" height="27.932"/><rect x="611.03" y="213.25" width="83.399" height="27.932"/><rect x="861.03" y="213.25" width="83.399" height="27.932"/><rect x="861.03" y="266.54" width="83.399" height="27.932"/></g></svg>'
    
    paths = {
        "flag": '<path d="M14.4 6L14 4H5v17h2v-7h5.6l.4 2h7V6z"/>',
        "calendar": '<path d="M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19a2 2 0 0 0 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11z"/>',
        "time": '<path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z"/><path d="M12.5 7H11v6l5.25 3.15.75-1.23-4.5-2.67z"/>',
        "timer": '<path d="M15 1H9v2h6V1zm-4 13h2V8h-2v6zm8.03-6.61l1.42-1.42c-.43-.51-.9-.99-1.41-1.41l-1.42 1.42A8.962 8.962 0 0 0 12 4c-4.97 0-9 4.03-9 9s4.03 9 9 9 9-4.03 9-9c0-2.12-.74-4.07-1.97-5.61zM12 20c-3.87 0-7-3.13-7-7s3.13-7 7-7 7 3.13 7 7-3.13 7-7 7z"/>',
        "conditions": '<path d="M15 13V5c0-1.66-1.34-3-3-3S9 3.34 9 5v8c-1.21.91-2 2.37-2 4 0 2.76 2.24 5 5 5s5-2.24 5-5c0-1.63-.79-3.09-2-4zm-4-8c0-.55.45-1 1-1s1 .45 1 1v4H11V5z"/>',
        "car": '<path d="M18.92 6.01C18.72 5.42 18.16 5 17.5 5h-11c-.66 0-1.21.42-1.42 1.01L3 12v8c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h12v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-8l-2.08-5.99zM6.5 16c-.83 0-1.5-.67-1.5-1.5S5.67 13 6.5 13s1.5.67 1.5 1.5S7.33 16 6.5 16zm11 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zM5 11l1.5-4.5h11L19 11H5z"/>',
        "tyre": f'<circle cx="12" cy="12" r="8" stroke="{color}" stroke-width="2" fill="none"/><circle cx="12" cy="12" r="3" fill="{color}"/>',
        "pin": '<path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5a2.5 2.5 0 0 1 0-5 2.5 2.5 0 0 1 0 5z"/>',
        "brain": '<path d="M13 3c-4.97 0-9 4.03-9 9H1l3.89 3.89.07.14L9 12H6c0-3.87 3.13-7 7-7s7 3.13 7 7-3.13 7-7 7c-1.93 0-3.68-.79-4.94-2.06l-1.42 1.42C8.27 19.99 10.51 21 13 21c4.97 0 9-4.03 9-9s-4.03-9-9-9zm-1 5v5l4.28 2.54.72-1.21-3.5-2.08V8H12z"/>',
        "eye": '<path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/>',
        "heart": '<path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>',
        "headset": '<path d="M12 1c-4.97 0-9 4.03-9 9v7c0 1.66 1.34 3 3 3h3v-8H5v-2c0-3.87 3.13-7 7-7s7 3.13 7 7v2h-4v8h3c1.66 0 3-1.34 3-3v-7c0-4.97-4.03-9-9-9z"/>',
        "trending": '<path d="M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z"/>',
        "uae": '<rect width="24" height="16" y="4" fill="#E8002D"/><path d="M8 4h16v5.33H8z" fill="#00732F"/><path d="M8 14.67h16V20H8z" fill="#000"/><path d="M8 9.33h16v5.34H8z" fill="#FFF"/><path d="M0 4h8v16H0z" fill="#E8002D"/>',
        "monaco": '<rect width="24" height="16" y="4" fill="#E8002D"/><path d="M0 12h24v8H0z" fill="#FFF"/>',
        "bahrain": '<rect width="24" height="16" y="4" fill="#E8002D"/><path d="M0 4h8l4 8-4 8H0z" fill="#FFF"/>',
    }
    p = paths.get(name, paths["car"])
    fill_attr = "" if name in ["uae", "monaco", "bahrain", "tyre"] else f'fill="{color}"'
    return f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" {fill_attr} style="vertical-align:middle;margin-right:{margin};display:inline-block;">{p}</svg>'

RACE_METADATA = {
    "Abu Dhabi GP 2024": {
        "flag": "uae",
        "flag_entity": get_svg_icon("uae", size=18, margin="2px"),
        "circuit": "YAS MARINA CIRCUIT",
        "laps": 58,
        "date": "08 Dec 2024",
        "duration": "1:32:15",
        "conditions": "27C Dry",
        "margin": "+38.457s",
        "peak_stress_lap": 47,
        "critical_events": "3",
        "critical_events_desc": "SC + Yellow + Restart",
        "radio_count": "14",
    },
    "Monaco GP 2024": {
        "flag_entity": get_svg_icon("monaco", size=18, margin="2px"),
        "circuit": "CIRCUIT DE MONACO",
        "laps": 78,
        "date": "26 May 2024",
        "duration": "1:45:08",
        "conditions": "21C Dry",
        "margin": "+4.125s",
        "peak_stress_lap": 67,
        "critical_events": "2",
        "critical_events_desc": "Tight Street Track Constraints",
        "radio_count": "18",
    },
    "Bahrain GP 2024": {
        "flag_entity": get_svg_icon("bahrain", size=18, margin="2px"),
        "circuit": "SAKHIR CIRCUIT",
        "laps": 57,
        "date": "02 Mar 2024",
        "duration": "1:31:44",
        "conditions": "19C Cool",
        "margin": "+22.457s",
        "peak_stress_lap": 1,
        "critical_events": "4",
        "critical_events_desc": "High Temp + Start Chaos",
        "radio_count": "11",
    }
}


def get_race_metadata(race_name: str) -> dict:
    """Return dictionary of race-specific metadata."""
    return RACE_METADATA.get(race_name, RACE_METADATA["Abu Dhabi GP 2024"])



def inject_css():
    """Inject full PitMind CSS based on the selected theme."""
    theme_css = DARK_CSS if st.session_state.get("dark_mode", True) else LIGHT_CSS
    st.markdown(f"<style>{theme_css}{BASE_CSS}</style>", unsafe_allow_html=True)


def render_ibm_label(text="IBM GRANITE 3.1"):
    st.markdown(
        f'<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.6rem;'
        f'letter-spacing:0.15em;color:#555;text-transform:uppercase;">'
        f'&#9632; {text} &middot; Powered by watsonx.ai</div>',
        unsafe_allow_html=True,
    )



def render_badge(text, variant="red"):
    st.markdown(
        f'<span class="pm-badge pm-badge-{variant}">{text}</span>',
        unsafe_allow_html=True,
    )


def render_logo(width="180px", center=False):
    import os
    import base64
    import streamlit as st
    align = "text-align:center;" if center else ""
    margin = "margin:0 auto;" if center else ""
    justify = "center" if center else "flex-start"
    origin = "center center" if center else "left center"
    
    # Remove excessive negative margin that hides the logo on the landing page
    shift_left = ""
    
    is_dark = st.session_state.get("dark_mode", True)
    
    # In dark mode, invert the colors (white->black, black->white, red->red)
    # In light mode, use mix-blend-mode: multiply to make the white background transparent
    image_css = "filter: invert(1) hue-rotate(180deg) brightness(1.2);" if is_dark else "mix-blend-mode: multiply;"
    
    if os.path.exists("VEGAIQlogo.png"):
        with open("VEGAIQlogo.png", "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
        # Smart adaptive filter based on current theme
        st.markdown(f"""
        <div style="display:flex; align-items:center; justify-content:{justify}; height:50px; margin-bottom:1rem; pointer-events:none; user-select:none;">
          <img src="data:image/png;base64,{data}" style="width:auto; max-height:40px; {margin} {shift_left} {image_css} pointer-events:none; margin-right: 15px;">
          <div style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:1.8rem;letter-spacing:0.05em;line-height:1; transform: translateY(-1px);">VEGAIQ</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="{align} padding:0.5rem 0; margin-bottom:1rem; {margin}">
          <div style="display:flex;align-items:center;gap:10px;justify-content:{'center' if center else 'flex-start'};">
              <div style="width:36px;height:36px;background:#E8002D;border-radius:6px;
                          display:flex;align-items:center;justify-content:center;
                          font-family:'Rajdhani',sans-serif;font-weight:700;color:white;font-size:1.1rem;">V</div>
              <div style="text-align:left;">
                <div style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:1.8rem;
                            letter-spacing:0.05em;line-height:1;">VEGAIQ</div>
              </div>
          </div>
        </div>""", unsafe_allow_html=True)


def sidebar_driver_card():
    """Render the driver info card in the sidebar."""
    selected_race = st.session_state.get("selected_race", "Abu Dhabi GP 2024")
    meta = get_race_metadata(selected_race)
    st.markdown(f"""
<div style="text-align:center;padding:0 0 0.5rem;">
  <div style="font-family:'Rajdhani',sans-serif;font-size:3.5rem;font-weight:700;
              color:#E8002D;line-height:1;">1</div>
  <div style="width:64px;height:64px;border-radius:50%;background:var(--bg-secondary);
              border:2px solid #E8002D;margin:0.4rem auto;display:flex;
              align-items:center;justify-content:center;overflow:hidden;">
      <img src="https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/M/MAXVER01_Max_Verstappen/maxver01.png" style="width:100%;height:100%;object-fit:cover;object-position:top;background:#1A1A1A;">
  </div>
  <div style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:1rem;
              letter-spacing:0.05em;color:var(--text-primary);">MAX VERSTAPPEN</div>
  <div style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;
              color:var(--text-muted);letter-spacing:0.1em;margin-top:2px;">RED BULL RACING</div>
</div>
<div style="background:var(--bg-card);border:1px solid var(--border);border-radius:6px;
            padding:0.6rem 0.8rem;margin:0.5rem 0;font-family:'Share Tech Mono',monospace;
            font-size:0.7rem;color:var(--text-muted);">
  <div style="margin-bottom:3px;">{meta['flag_entity']} {selected_race.upper()}</div>
  <div><span style="color:#E8002D;">&#9679;</span> RACE &middot; {meta['laps']} LAPS</div>
</div>""", unsafe_allow_html=True)


def sidebar_nav():
    """Render the sidebar navigation links."""
    st.markdown("""
<div style="font-family:'Share Tech Mono',monospace;font-size:0.6rem;
            letter-spacing:0.15em;color:#888;margin:0.3rem 0;text-transform:uppercase;">
    Navigation</div>""", unsafe_allow_html=True)
    st.page_link("app.py", label="HOME", icon=":material/home:")
    st.page_link("pages/1_Dashboard.py", label="Dashboard", icon=":material/dashboard:")
    st.page_link("pages/2_Lap_Dive.py", label="Lap Dive", icon=":material/search:")
    st.page_link("pages/3_AI_Chat.py", label="AI Chat", icon=":material/smart_toy:")
    st.page_link("pages/4_Reports.py", label="Reports", icon=":material/analytics:")


def sidebar_live_status():
    """Render the live telemetry status."""
    st.markdown("""
<div style="display:flex;align-items:center;gap:6px;padding:0.4rem 0;
            border-top:1px solid var(--border);margin-top:0.5rem;">
  <span style="width:8px;height:8px;background:#E8002D;border-radius:50%;
               display:inline-block;animation:pulse 2s infinite;"></span>
  <span style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;
               letter-spacing:0.1em;color:#888;">LIVE TELEMETRY</span>
  <span style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;
               color:#00C853;margin-left:auto;">CONNECTED</span>
</div>""", unsafe_allow_html=True)


def setup_sidebar():
    """Complete sidebar setup used by all inner pages."""
    render_logo(width="260px", center=True)
    sidebar_driver_card()
    sidebar_nav()
    st.markdown("---")

    # Initialise dark_mode in session state if not already set
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = True

    # Render the toggle — value reflects the CURRENT light/dark state
    # We store dark_mode=True for dark, so light_theme toggle = not dark_mode
    new_light = st.toggle(
        "LIGHT THEME",
        value=not st.session_state.dark_mode,
        key="theme_toggle",
    )

    # Only rerun when the user actually flips the toggle
    if new_light == st.session_state.dark_mode:
        # dark_mode was True but toggle now wants light (new_light=True), or vice-versa
        st.session_state.dark_mode = not new_light
        st.rerun()

    st.markdown("---")
    sidebar_live_status()
