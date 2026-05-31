"""
utils/charts.py
PitMind — All Plotly chart functions for the Streamlit UI.
Every chart uses a transparent dark background to match the PitMind theme.
"""

import json
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ── Theme constants ──
BG = "rgba(0,0,0,0)"
PAPER_BG = "rgba(0,0,0,0)"
RED = "#E8002D"
ORANGE = "#FF7B00"
BLUE = "#4A9EFF"
GREEN = "#00C853"
GREY = "#888888"
WHITE = "#FFFFFF"
DARK_GRID = "#2A2A2A"
FONT_FAMILY = "Rajdhani, Share Tech Mono, sans-serif"

def hex_to_rgba_safe(color: str, alpha: float) -> str:
    """Safely convert hex or rgb string to rgba string for Plotly."""
    if "rgb" in color:
        return color.replace(")", f",{alpha})").replace("rgb", "rgba")
    elif color.startswith("#"):
        hex_c = color.lstrip('#')
        if len(hex_c) == 6:
            return f"rgba({int(hex_c[:2], 16)},{int(hex_c[2:4], 16)},{int(hex_c[4:6], 16)},{alpha})"
        elif len(hex_c) == 3:
            return f"rgba({int(hex_c[0]*2, 16)},{int(hex_c[1]*2, 16)},{int(hex_c[2]*2, 16)},{alpha})"
    return color



def is_dark() -> bool:
    """Read theme state from Streamlit session state."""
    import streamlit as st
    return st.session_state.get("dark_mode", True)


def _base_layout(**kwargs) -> dict:
    """Return common theme-aware layout settings."""
    dark = is_dark()
    text_color = WHITE if dark else "#0A0A0A"
    grid_color = DARK_GRID if dark else "#E0E0E0"
    muted_color = GREY if dark else "#555555"

    return dict(
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=BG,
        font=dict(family=FONT_FAMILY, color=text_color, size=12),
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(
            bgcolor="rgba(20,20,20,0.8)" if dark else "rgba(255,255,255,0.8)",
            bordercolor=grid_color,
            borderwidth=1,
            font=dict(color=text_color),
        ),
        xaxis=dict(
            gridcolor=grid_color, gridwidth=1,
            linecolor=grid_color, tickcolor=grid_color,
            tickfont=dict(color=muted_color),
            title=dict(font=dict(color=text_color)),
        ),
        yaxis=dict(
            gridcolor=grid_color, gridwidth=1,
            linecolor=grid_color, tickcolor=grid_color,
            tickfont=dict(color=muted_color),
            title=dict(font=dict(color=text_color)),
        ),
        **kwargs,
    )


# ─────────────────────────────────────────────
# 1. Psychological Trace Chart (full race)
# ─────────────────────────────────────────────

def psychological_trace_chart(df: pd.DataFrame, selected_lap: int = 47, color: str = RED) -> go.Figure:
    """Dual-axis: Stress Index (color) + Lap Time (grey dashed) across all laps."""
    laps = df["lap"].tolist()
    stress = df["stress_index"].tolist()
    lap_times = df["lap_time_seconds"].tolist()

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Stress trace
    fig.add_trace(
        go.Scatter(
            x=laps, y=stress,
            name="Stress Index",
            line=dict(color=color, width=2.5),
            fill="tozeroy",
            fillcolor=hex_to_rgba_safe(color, 0.08),
            hovertemplate="Lap %{x}<br>Stress: %{y:.1f}/10<extra></extra>",
        ),
        secondary_y=False,
    )

    # Lap time trace
    fig.add_trace(
        go.Scatter(
            x=laps, y=lap_times,
            name="Lap Time (s)",
            line=dict(color=GREY, width=1.5, dash="dash"),
            hovertemplate="Lap %{x}<br>Lap Time: %{y:.3f}s<extra></extra>",
        ),
        secondary_y=True,
    )

    # Selected lap vertical line
    fig.add_vline(
        x=selected_lap, line_dash="dot",
        line_color=color, line_width=1.5, opacity=0.7,
    )

    # Critical lap annotation
    if selected_lap in laps:
        idx = laps.index(selected_lap)
        peak_stress = stress[idx]
        fig.add_annotation(
            x=selected_lap, y=peak_stress,
            text=f"◆ CRITICAL — LAP {selected_lap}",
            showarrow=True, arrowhead=2,
            arrowcolor=color, arrowwidth=1.5,
            font=dict(color=color, size=11, family=FONT_FAMILY),
            bgcolor=hex_to_rgba_safe(color, 0.15),
            bordercolor=color, borderwidth=1,
            ax=40, ay=-35,
        )

    dark = is_dark()
    text_color = WHITE if dark else "#0A0A0A"
    grid_color = DARK_GRID if dark else "#E0E0E0"
    muted_color = GREY if dark else "#555555"

    layout = _base_layout(
        title=dict(
            text="PSYCHOLOGICAL TRACE — ABU DHABI GP 2024",
            font=dict(size=13, color=text_color),
            x=0.01,
        ),
        hovermode="x unified",
        height=320,
    )

    layout["yaxis"]["title"] = dict(text="Stress Index", font=dict(color=RED, size=11))
    layout["yaxis"]["range"] = [0, 11]
    fig.update_layout(**layout)
    fig.update_yaxes(
        title_text="Lap Time (s)",
        title_font=dict(color=muted_color, size=11),
        gridcolor=grid_color,
        tickfont=dict(color=muted_color),
        secondary_y=True,
    )
    return fig


# ─────────────────────────────────────────────
# 2. Zoomed Lap Chart (±7 laps window)
# ─────────────────────────────────────────────

def zoomed_lap_chart(df: pd.DataFrame, center_lap: int = 47) -> go.Figure:
    """Dual-axis zoomed to ±7 laps around selected lap."""
    lap_min = max(1, center_lap - 7)
    lap_max = min(58, center_lap + 7)
    subset = df[(df["lap"] >= lap_min) & (df["lap"] <= lap_max)]

    laps = subset["lap"].tolist()
    stress = subset["stress_index"].tolist()
    lap_times = subset["lap_time_seconds"].tolist()
    quality = subset["decision_quality"].tolist()

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(x=laps, y=stress, name="Stress Index",
                   line=dict(color=RED, width=3),
                   fill="tozeroy", fillcolor="rgba(232,0,45,0.1)",
                   hovertemplate="Lap %{x}<br>Stress: %{y:.1f}/10<extra></extra>"),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=laps, y=quality, name="Decision Quality",
                   line=dict(color=BLUE, width=2, dash="dot"),
                   hovertemplate="Lap %{x}<br>Quality: %{y:.1f}/10<extra></extra>"),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=laps, y=lap_times, name="Lap Time (s)",
                   line=dict(color=GREY, width=1.5, dash="dash"),
                   hovertemplate="Lap %{x}<br>%{y:.3f}s<extra></extra>"),
        secondary_y=True,
    )

    if center_lap in laps:
        idx = laps.index(center_lap)
        fig.add_annotation(
            x=center_lap, y=stress[idx],
            text=f"LAP {center_lap}",
            showarrow=True, arrowhead=2, arrowcolor=RED,
            font=dict(color=RED, size=11), ax=30, ay=-30,
            bgcolor="rgba(232,0,45,0.15)", bordercolor=RED, borderwidth=1,
        )

    dark = is_dark()
    grid_color = DARK_GRID if dark else "#E0E0E0"
    muted_color = GREY if dark else "#555555"
    text_color = WHITE if dark else "#0A0A0A"

    layout = _base_layout(height=280, title=dict(
        text=f"STRESS & LAP TIME — LAPS {lap_min}–{lap_max}",
        font=dict(size=12, color=text_color), x=0.01,
    ), hovermode="x unified")
    fig.update_layout(**layout)
    fig.update_yaxes(
        title_text="Lap Time (s)", title_font=dict(color=muted_color, size=10),
        gridcolor=grid_color, tickfont=dict(color=muted_color), secondary_y=True,
    )
    return fig


# ─────────────────────────────────────────────
# 3. Gauge Chart (Overall Psychological Score)
# ─────────────────────────────────────────────

def gauge_chart(score: float, title: str = "OVERALL PSYCH SCORE") -> go.Figure:
    """Circular gauge chart for overall psychological performance score."""
    dark = is_dark()
    text_color = WHITE if dark else "#0A0A0A"
    grid_color = DARK_GRID if dark else "#E0E0E0"
    muted_color = GREY if dark else "#555555"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={"x": [0, 1], "y": [0, 1]},
        number={
            "font": {"size": 42, "color": text_color, "family": FONT_FAMILY},
            "suffix": "/10",
        },
        gauge={
            "axis": {
                "range": [0, 10],
                "tickwidth": 1,
                "tickcolor": muted_color,
                "tickfont": {"color": muted_color, "size": 10},
            },
            "bar": {"color": RED, "thickness": 0.25},
            "bgcolor": "#1A1A1A" if dark else "#FAFAFA",
            "borderwidth": 2,
            "bordercolor": grid_color,
            "steps": [
                {"range": [0, 3], "color": "#1A1A1A" if dark else "#FAFAFA"},
                {"range": [3, 6], "color": "#1F1F1F" if dark else "#F0F0F0"},
                {"range": [6, 8], "color": "#242424" if dark else "#EAEAEA"},
                {"range": [8, 10], "color": "#2A1A1A" if dark else "#FFEAEA"},
            ],
            "threshold": {
                "line": {"color": RED, "width": 3},
                "thickness": 0.8,
                "value": score,
            },
        },
    ))
    fig.update_layout(
        paper_bgcolor=PAPER_BG,
        font=dict(family=FONT_FAMILY, color=text_color),
        margin=dict(l=20, r=20, t=50, b=20),
        height=260,
        title=dict(text=title, font=dict(size=12, color=muted_color), x=0.5),
        annotations=[dict(
            text="High Performance",
            x=0.5, y=0.08, xref="paper", yref="paper",
            font=dict(size=12, color=muted_color, family=FONT_FAMILY),
            showarrow=False,
        )],
    )
    return fig


# ─────────────────────────────────────────────
# 4. Events Donut Chart
# ─────────────────────────────────────────────

def events_donut_chart(df: pd.DataFrame, color: str = BLUE) -> go.Figure:
    """Donut chart showing race event breakdown."""
    sc_count = 0
    yf_count = 0
    radio_count = 0
    other_count = 0

    for _, row in df.iterrows():
        events_raw = row.get("race_events", "[]")
        if isinstance(events_raw, str):
            try:
                events = json.loads(events_raw)
            except Exception:
                events = []
        else:
            events = events_raw if isinstance(events_raw, list) else []

        for e in events:
            if "SAFETY" in str(e):
                sc_count += 1
            elif "YELLOW" in str(e):
                yf_count += 1
            else:
                other_count += 1

        radio = row.get("radio_text", "")
        if radio and radio not in ["No transmission.", ""]:
            radio_count += 1

    labels = ["Safety Car", "Yellow Flag", "Radio Events", "Other"]
    values = [max(sc_count, 3), max(yf_count, 5), max(radio_count, 14), max(other_count, 2)]
    dark = is_dark()
    text_color = WHITE if dark else "#0A0A0A"
    grid_color = DARK_GRID if dark else "#E0E0E0"
    muted_color = GREY if dark else "#555555"

    labels = ["Safety Car", "Yellow Flag", "Radio Events", "Other"]
    values = [max(sc_count, 3), max(yf_count, 5), max(radio_count, 14), max(other_count, 2)]
    colors = [RED, "#FFD700", color, GREY]
    total = sum(values)

    fig = go.Figure(go.Pie(
        labels=labels, values=values,
        hole=0.6,
        marker=dict(colors=colors, line=dict(color="#0A0A0A" if dark else "#FFFFFF", width=2)),
        textfont=dict(size=11, color=text_color, family=FONT_FAMILY),
        hovertemplate="%{label}: %{value}<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor=PAPER_BG,
        font=dict(family=FONT_FAMILY, color=text_color),
        margin=dict(l=10, r=10, t=40, b=10),
        height=280,
        showlegend=True,
        legend=dict(bgcolor="rgba(20,20,20,0.8)" if dark else "rgba(255,255,255,0.8)", bordercolor=grid_color, borderwidth=1, font=dict(color=text_color)),
        title=dict(text="EVENTS BREAKDOWN", font=dict(size=12, color=text_color), x=0.01),
        annotations=[dict(
            text=f"<b>{total}</b><br><span style='font-size:10px;color:{muted_color}'>TOTAL</span>",
            x=0.5, y=0.5, xref="paper", yref="paper",
            font=dict(size=18, color=text_color, family=FONT_FAMILY),
            showarrow=False,
        )],
    )
    return fig


# ─────────────────────────────────────────────
# 5. Multi-line Report Trace (Stress + Quality + Fatigue)
# ─────────────────────────────────────────────

def report_trace_chart(df: pd.DataFrame, color: str = RED) -> go.Figure:
    """3-line Plotly chart for Reports page: Stress + Quality + Fatigue."""
    laps = df["lap"].tolist()
    stress = df["stress_index"].tolist()
    quality = df["decision_quality"].tolist()
    fatigue = df["mental_fatigue"].tolist()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=laps, y=stress, name="Stress Index",
        line=dict(color=color, width=2.5),
        hovertemplate="Lap %{x} — Stress: %{y:.1f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=laps, y=quality, name="Decision Quality",
        line=dict(color=BLUE, width=2),
        hovertemplate="Lap %{x} — Quality: %{y:.1f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=laps, y=fatigue, name="Mental Fatigue",
        line=dict(color=ORANGE, width=2),
        hovertemplate="Lap %{x} — Fatigue: %{y:.1f}<extra></extra>",
    ))

    # Critical lap 47 annotation
    if 47 in laps:
        idx = laps.index(47)
        fig.add_vline(x=47, line_dash="dot", line_color=color, line_width=1.5, opacity=0.7)
        fig.add_annotation(
            x=47, y=stress[idx],
            text="CRITICAL LAP 47",
            showarrow=True, arrowhead=2, arrowcolor=color,
            font=dict(color=color, size=10), ax=35, ay=-30,
            bgcolor=hex_to_rgba_safe(color, 0.15), bordercolor=color, borderwidth=1,
        )

    dark = is_dark()
    text_color = WHITE if dark else "#0A0A0A"
    muted_color = GREY if dark else "#555555"

    layout = _base_layout(
        height=300,
        hovermode="x unified",
        title=dict(text="PSYCHOLOGICAL TRACE OVERVIEW", font=dict(size=12, color=text_color), x=0.01),
    )
    layout["yaxis"]["range"] = [0, 11]
    layout["yaxis"]["title"] = dict(text="Score (0-10)", font=dict(color=muted_color, size=10))
    fig.update_layout(**layout)
    return fig


# ─────────────────────────────────────────────
# 6. Biometric Sparklines
# ─────────────────────────────────────────────

def hr_sparkline(heart_rate: int) -> go.Figure:
    """Mini heart rate waveform chart."""
    from core.synthetic import generate_hr_waveform
    wave = generate_hr_waveform(heart_rate)
    x = list(range(len(wave)))

    fig = go.Figure(go.Scatter(
        x=x, y=wave, mode="lines",
        line=dict(color=RED, width=1.5),
        fill="tozeroy", fillcolor="rgba(232,0,45,0.1)",
    ))
    fig.update_layout(
        paper_bgcolor=PAPER_BG, plot_bgcolor=BG,
        height=60, margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        showlegend=False,
    )
    return fig


def eeg_sparkline(stress_index: float, color: str = BLUE) -> go.Figure:
    """Mini EEG-style waveform for mental state."""
    from core.synthetic import generate_eeg_waveform
    wave = generate_eeg_waveform(stress_index)
    x = list(range(len(wave)))

    fig = go.Figure(go.Scatter(x=x, y=wave, mode="lines",
                               line=dict(color=color, width=1.5)))
    fig.update_layout(
        paper_bgcolor=PAPER_BG, plot_bgcolor=BG,
        height=60, margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        showlegend=False,
    )
    return fig


def reaction_bar_chart(delta_ms: int) -> go.Figure:
    """Mini horizontal bar showing reaction time delta."""
    color = RED if delta_ms < 0 else GREEN
    fig = go.Figure()
    # Background track
    fig.add_trace(go.Bar(
        x=[500], y=["RT"],
        orientation="h",
        marker_color="rgba(100, 100, 100, 0.1)",
        width=0.15,
        hoverinfo="none"
    ))
    # Actual delta bar
    fig.add_trace(go.Bar(
        x=[abs(delta_ms)], y=["RT"],
        orientation="h",
        marker_color=color,
        width=0.15
    ))
    fig.update_layout(
        paper_bgcolor=PAPER_BG, plot_bgcolor=BG,
        height=60, margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False, range=[0, 500]),
        yaxis=dict(visible=False),
        showlegend=False,
        barmode="overlay"
    )
    return fig


# ─────────────────────────────────────────────
# 7. Sector Performance Bars
# ─────────────────────────────────────────────

def sector_performance_chart(lap_data: dict, best_lap_data: dict) -> go.Figure:
    """Horizontal bar chart showing sector performance vs best lap."""
    sectors = ["Sector 1", "Sector 2", "Sector 3"]
    this_lap = [
        lap_data.get("sector1", 24.0),
        lap_data.get("sector2", 42.0),
        lap_data.get("sector3", 24.0),
    ]
    best = [
        best_lap_data.get("sector1", 23.5),
        best_lap_data.get("sector2", 41.8),
        best_lap_data.get("sector3", 23.2),
    ]
    deltas = [round(t - b, 3) for t, b in zip(this_lap, best)]
    colors = [RED if d > 0.2 else (ORANGE if d > 0 else GREEN) for d in deltas]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="This Lap", x=this_lap, y=sectors,
        orientation="h", marker_color=colors,
        hovertemplate="%{y}: %{x:.3f}s<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        name="Best Lap", x=best, y=sectors,
        orientation="h", marker_color=GREY, opacity=0.4,
        hovertemplate="%{y} Best: %{x:.3f}s<extra></extra>",
    ))
    dark = is_dark()
    text_color = WHITE if dark else "#0A0A0A"
    layout = _base_layout(
        barmode="overlay", height=200,
        title=dict(text="SECTOR PERFORMANCE", font=dict(size=11, color=text_color), x=0.01),
    )
    fig.update_layout(**layout)
    return fig
