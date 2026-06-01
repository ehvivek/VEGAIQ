"""
utils/helpers.py
PitMind — Shared utility functions across all pages.
"""

import json
import pandas as pd
import numpy as np
import streamlit as st
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


# ─────────────────────────────────────────────
# Formatting helpers
# ─────────────────────────────────────────────

def format_lap_time(seconds: float) -> str:
    """Convert seconds to F1 lap time string: 1:29.987"""
    if pd.isna(seconds) or seconds <= 0:
        return "–:–––.–––"
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes}:{secs:06.3f}"


def format_delta(delta: float) -> str:
    """Format lap time delta with sign: +1.487s or -0.312s"""
    if pd.isna(delta):
        return "±0.000s"
    sign = "+" if delta >= 0 else ""
    return f"{sign}{delta:.3f}s"


def stress_color(stress: float) -> str:
    """Return hex color for stress value."""
    if stress >= 8.0:
        return "#E8002D"
    elif stress >= 6.5:
        return "#FF7B00"
    elif stress >= 5.0:
        return "#FFD700"
    else:
        return "#00C853"


def stress_label(stress: float) -> str:
    """Return text label for stress level."""
    if stress >= 8.5:
        return "CRITICAL"
    elif stress >= 7.0:
        return "Very High"
    elif stress >= 5.5:
        return "High"
    elif stress >= 4.0:
        return "Moderate"
    else:
        return "Low"


def quality_label(quality: float) -> str:
    if quality >= 8.0:
        return "Excellent"
    elif quality >= 6.5:
        return "Good"
    elif quality >= 5.0:
        return "Moderate"
    else:
        return "Poor"


def fatigue_label(fatigue: float) -> str:
    if fatigue >= 8.0:
        return "Severe"
    elif fatigue >= 6.5:
        return "High"
    elif fatigue >= 5.0:
        return "Moderate"
    else:
        return "Low"


def get_event_badges(events_raw) -> str:
    """Convert events list to emoji badge string."""
    if isinstance(events_raw, str):
        try:
            events = json.loads(events_raw)
        except Exception:
            events = []
    else:
        events = events_raw if isinstance(events_raw, list) else []

    badges = []
    for e_str in events:
        e_str = str(e_str).upper()
        if "SC" in e_str and "VSC" not in e_str:
            badges.append("SC")
        elif "YF" in e_str or "YELLOW" in e_str:
            badges.append("YF")
        elif "VSC" in e_str:
            badges.append("VSC")
        elif "DRS" in e_str:
            badges.append("DRS")
        elif e_str:
            badges.append(f"{e_str[:8]}")
    return " ".join(badges) if badges else "—"


def get_tyre_badge(compound: str) -> str:
    """Return tyre compound badge."""
    c = str(compound).upper()
    badges = {
        "SOFT": "SOFT",
        "MEDIUM": "MEDIUM",
        "HARD": "HARD",
        "INTER": "INTER",
        "WET": "WET",
    }
    return badges.get(c, c)


# ─────────────────────────────────────────────
# Data accessors
# ─────────────────────────────────────────────

def load_lap_data(df: pd.DataFrame, lap_number: int) -> dict:
    """Extract full unified schema dict for a specific lap."""
    rows = df[df["lap"] == lap_number]
    if rows.empty:
        # Return default lap 47 data
        return {
            "lap": lap_number,
            "driver": "VER",
            "lap_time_seconds": 89.987,
            "lap_time_formatted": "1:29.987",
            "delta_to_best": 1.487,
            "tyre_compound": "SOFT",
            "tyre_age": 18,
            "position": 1,
            "gap_to_p2": 0.0,
            "race_events": '["SAFETY_CAR", "YELLOW_FLAG"]',
            "radio_text": "These tyres are completely gone, I cannot hold Norris.",
            "radio_sentiment": -0.82,
            "heart_rate_est": 167,
            "eye_tracking": "ERRATIC",
            "reaction_time_delta": -340,
            "mental_state": "CRITICAL ANXIETY",
            "stress_index": 9.1,
            "decision_quality": 5.2,
            "mental_fatigue": 7.4,
            "situational_awareness": 6.8,
            "sector1": 23.456,
            "sector2": 42.107,
            "sector3": 24.424,
            "granite_analysis": "",
            "timestamp": "21:24:44",
        }
    return rows.iloc[0].to_dict()


def get_best_lap_data(df: pd.DataFrame) -> dict:
    """Get the lap with the fastest lap time."""
    if df.empty:
        return {}
    best_idx = df["lap_time_seconds"].idxmin()
    return df.loc[best_idx].to_dict()


def get_race_summary(df: pd.DataFrame) -> dict:
    """Compute overall race statistics from full dataframe."""
    if df.empty:
        return {
            "avg_stress": 5.8, "peak_stress": 9.1, "peak_lap": 47,
            "avg_quality": 6.4, "avg_fatigue": 5.8, "total_radio": 14,
            "overall_score": 7.6, "total_laps": 58,
        }
    return {
        "avg_stress": round(float(df["stress_index"].mean()), 1),
        "peak_stress": round(float(df["stress_index"].max()), 1),
        "peak_lap": int(df.loc[df["stress_index"].idxmax(), "lap"]),
        "avg_quality": round(float(df["decision_quality"].mean()), 1),
        "avg_fatigue": round(float(df["mental_fatigue"].mean()), 1),
        "total_radio": int((df["radio_text"] != "No transmission.").sum()),
        "overall_score": round(float((
            df["decision_quality"].mean() * 0.4 +
            (10 - df["stress_index"].mean()) * 0.3 +
            (10 - df["mental_fatigue"].mean()) * 0.3
        )), 1),
        "total_laps": len(df),
    }


# ─────────────────────────────────────────────
# Session state initializer
# ─────────────────────────────────────────────

def init_session_state():
    """Initialize all Streamlit session state variables."""
    defaults = {
        "dark_mode": True,
        "selected_lap": 47,
        "selected_race": "Abu Dhabi GP 2024",
        "selected_session": "Race",
        "race_df": None,
        "pipeline_run": False,
        "messages": [],
        "voice_output": False,
        "granite_cache": {},
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value



# ─────────────────────────────────────────────
# Data loading with caching
# ─────────────────────────────────────────────

@st.cache_data(show_spinner=False, ttl=3600)
def get_race_data(race_name: str = "Abu Dhabi GP 2024") -> pd.DataFrame:
    """Load and fully process race data (cached for 1 hour)."""
    from core.data_pipeline import load_race_data, _generate_fallback_data
    from core.models import predict_all_laps, train_models
    from core.synthetic import enrich_dataframe

    try:
        df = load_race_data(race_name)
    except Exception:
        df = _generate_fallback_data(race_name)

    if df.empty:
        df = _generate_fallback_data(race_name)

    # Train models if not done yet
    try:
        train_models()
        df = predict_all_laps(df)
    except Exception as e:
        st.warning(f"ML models not available: {e}")
        # Assign realistic fallback scores
        np.random.seed(42)
        n = len(df)
        name = str(race_name).lower()
        peak = 67 if "monaco" in name else 1 if "bahrain" in name else 47
        total = 78 if "monaco" in name else 57 if "bahrain" in name else 58
        stress_base = np.array([5.0 + 3.0 * np.exp(-((i - peak)**2) / 30) for i in df["lap"]])
        df["stress_index"] = np.clip(stress_base + np.random.normal(0, 0.3, n), 0, 10).round(1)
        df["decision_quality"] = np.clip(7.5 - stress_base * 0.4 + np.random.normal(0, 0.3, n), 0, 10).round(1)
        df["mental_fatigue"] = np.clip(3.0 + df["lap"] / total * 5.0 + np.random.normal(0, 0.2, n), 0, 10).round(1)

    try:
        df = enrich_dataframe(df)
    except Exception as e:
        st.warning(f"Biometrics not computed: {e}")

    return df


# ─────────────────────────────────────────────
# Key events data for Lap 47
# ─────────────────────────────────────────────

KEY_EVENTS_LAP47 = [
    {"time": "21:24:12", "color": "#E8002D", "dot": "🔴", "event": "SAFETY CAR DEPLOYED"},
    {"time": "21:24:28", "color": "#FFD700", "dot": "🟡", "event": "YELLOW FLAG — TURN 14"},
    {"time": "21:24:44", "color": "#888888", "dot": "⚫", "event": "RADIO MESSAGE RECEIVED"},
    {"time": "21:25:02", "color": "#E8002D", "dot": "🔴", "event": "RESTART SEQUENCE BEGINS"},
]

KEY_EVENTS_BY_LAP = {
    44: [{"time": "21:18:30", "color": "#FFD700", "dot": "🟡", "event": "YELLOW FLAG — TURN 9"}],
    45: [{"time": "21:19:55", "color": "#E8002D", "dot": "🔴", "event": "SAFETY CAR DEPLOYED"}],
    46: [{"time": "21:21:40", "color": "#E8002D", "dot": "🔴", "event": "SAFETY CAR — LAP 2"}],
    47: KEY_EVENTS_LAP47,
    48: [{"time": "21:26:15", "color": "#E8002D", "dot": "🔴", "event": "SAFETY CAR IN"}],
    49: [{"time": "21:28:00", "color": "#00C853", "dot": "🟢", "event": "DRS ENABLED"}],
    50: [{"time": "21:29:50", "color": "#888888", "dot": "⚫", "event": "BOX BOX — PIT STOP"}],
}


def get_key_events(lap_number: int) -> list:
    """Get key events for a given lap."""
    return KEY_EVENTS_BY_LAP.get(lap_number, [])
