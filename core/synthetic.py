"""
core/synthetic.py
PitMind — Synthetic biometric generation from real race variables.

DISCLOSURE: Heart rate, eye tracking, and reaction time are modeled estimates
derived from real performance telemetry using established sports psychology
stress indicators. They are NOT directly measured biometric data.
"""

import numpy as np
import pandas as pd


# ─────────────────────────────────────────────
# Constants (sports psychology baselines)
# ─────────────────────────────────────────────

BASE_HEART_RATE = 145          # BPM at steady-state racing
MAX_HEART_RATE = 195           # Physiological cap for elite athletes
BASE_REACTION_MS = 250         # Baseline reaction time (ms)
STRESS_REACTION_SCALE = 68     # ms degradation per stress unit above 5


# ─────────────────────────────────────────────
# Individual metric calculators
# ─────────────────────────────────────────────

def calculate_heart_rate(lap_data: dict) -> int:
    """
    Estimate heart rate from race stress variables.
    Each factor adds BPM based on documented sports psychology correlations.
    """
    hr = BASE_HEART_RATE

    # Safety car shock: sudden deceleration + restart anticipation
    hr += lap_data.get("safety_car", 0) * 20

    # Tyre cliff: losing grip creates acute stress
    tyre_age = lap_data.get("tyre_age", 10)
    tyre_cliff = 1.0 if tyre_age > 25 else (tyre_age / 25.0)
    hr += tyre_cliff * 12

    # Negative radio sentiment: external pressure signals
    radio_sent = abs(lap_data.get("radio_sentiment", 0.0))
    hr += radio_sent * 10

    # Gap pressure: being within 1s of another car
    gap = lap_data.get("gap_to_p2", 20.0)
    gap_pressure = max(0.0, (3.0 - gap) / 3.0)  # max effect within 3s
    hr += gap_pressure * 15

    # Laps remaining pressure: end-of-race intensity
    total_laps = 58
    laps_done = lap_data.get("lap", 30)
    laps_remaining = total_laps - laps_done
    remaining_pressure = max(0.0, 1.0 - (laps_remaining / total_laps))
    hr += remaining_pressure * 8

    # Yellow flag: heightened alertness
    hr += lap_data.get("yellow_flag", 0) * 8

    # Stress index amplifier
    stress = lap_data.get("stress_index", 5.0)
    hr += (stress - 5.0) * 4.0

    return min(int(hr), MAX_HEART_RATE)


def calculate_mental_state(stress_index: float) -> str:
    """Classify psychological state from stress index."""
    if stress_index > 8.5:
        return "CRITICAL ANXIETY"
    elif stress_index > 7.0:
        return "ELEVATED STRESS"
    elif stress_index > 5.5:
        return "MODERATE PRESSURE"
    elif stress_index > 3.5:
        return "FOCUSED"
    else:
        return "OPTIMAL FOCUS"


def calculate_eye_tracking(stress_index: float) -> str:
    """Estimate eye tracking behavior from stress level."""
    if stress_index > 7.5:
        return "ERRATIC"
    elif stress_index > 5.0:
        return "MODERATE"
    else:
        return "FOCUSED"


def calculate_reaction_delta(stress_index: float) -> int:
    """
    Estimate reaction time delta vs baseline (negative = slower).
    Under high stress, cognitive overload slows fine motor response.
    """
    delta = -int((stress_index - 5.0) * STRESS_REACTION_SCALE)
    return max(-500, min(100, delta))  # cap at -500ms to +100ms


def calculate_situational_awareness(
    stress_index: float,
    mental_fatigue: float,
    position: int,
    gap_to_p2: float
) -> float:
    """
    Estimate situational awareness (0-10).
    Decreases with fatigue and high stress; improves with lead margin.
    """
    base = 10.0
    # High stress reduces awareness
    base -= (stress_index - 5.0) * 0.4
    # Fatigue degrades awareness
    base -= (mental_fatigue - 5.0) * 0.3
    # Being in the lead with gap helps confidence
    if position == 1 and gap_to_p2 > 5.0:
        base += 0.5
    return round(max(1.0, min(10.0, base)), 1)


# ─────────────────────────────────────────────
# Main generator
# ─────────────────────────────────────────────

def generate_biometrics(lap_data: dict) -> dict:
    """
    Generate all synthetic biometric estimates for a single lap.

    Args:
        lap_data: dict containing stress_index, mental_fatigue, tyre_age,
                  radio_sentiment, gap_to_p2, safety_car, yellow_flag, position, lap

    Returns:
        dict with heart_rate_est, mental_state, eye_tracking,
              reaction_time_delta, situational_awareness
    """
    stress = lap_data.get("stress_index", 5.0)
    fatigue = lap_data.get("mental_fatigue", 5.0)
    quality = lap_data.get("decision_quality", 6.0)

    # Extract event flags
    import json
    events_raw = lap_data.get("race_events", "[]")
    if isinstance(events_raw, str):
        try:
            events = json.loads(events_raw)
        except Exception:
            events = []
    else:
        events = events_raw if isinstance(events_raw, list) else []

    lap_data_enriched = {
        **lap_data,
        "safety_car": 1 if "SAFETY_CAR" in events else 0,
        "yellow_flag": 1 if "YELLOW_FLAG" in events else 0,
    }

    hr = calculate_heart_rate(lap_data_enriched)
    mental_state = calculate_mental_state(stress)
    eye_tracking = calculate_eye_tracking(stress)
    reaction_delta = calculate_reaction_delta(stress)
    sa = calculate_situational_awareness(
        stress, fatigue,
        int(lap_data.get("position", 1)),
        float(lap_data.get("gap_to_p2", 10.0))
    )

    return {
        "heart_rate_est": hr,
        "mental_state": mental_state,
        "eye_tracking": eye_tracking,
        "reaction_time_delta": reaction_delta,
        "situational_awareness": round(sa, 1),
    }


def enrich_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Apply biometric generation to all rows of the race dataframe."""
    df = df.copy()

    bio_cols = ["heart_rate_est", "mental_state", "eye_tracking",
                "reaction_time_delta", "situational_awareness"]

    results = []
    for _, row in df.iterrows():
        bio = generate_biometrics(row.to_dict())
        results.append(bio)

    bio_df = pd.DataFrame(results)
    for col in bio_cols:
        df[col] = bio_df[col].values

    return df


# ─────────────────────────────────────────────
# Waveform data generators for sparkline charts
# ─────────────────────────────────────────────

def generate_hr_waveform(heart_rate: int, n_points: int = 50) -> list:
    """Generate realistic heart rate waveform data for chart."""
    np.random.seed(heart_rate)
    base = heart_rate
    wave = []
    for i in range(n_points):
        # QRS complex simulation
        if i % 8 == 4:
            wave.append(base + 15)   # R peak
        elif i % 8 == 3 or i % 8 == 5:
            wave.append(base - 5)    # Q/S valley
        else:
            wave.append(base + np.random.uniform(-3, 3))
    return wave


def generate_eeg_waveform(stress_index: float, n_points: int = 50) -> list:
    """Generate synthetic EEG-style mental state waveform."""
    np.random.seed(int(stress_index * 10))
    amplitude = stress_index * 2
    freq = stress_index / 5.0
    t = np.linspace(0, 4 * np.pi * freq, n_points)
    wave = amplitude * np.sin(t) + np.random.uniform(-0.5, 0.5, n_points)
    return wave.tolist()


def generate_eye_waveform(eye_tracking: str, n_points: int = 50) -> list:
    """Generate eye movement pattern waveform."""
    np.random.seed(42)
    if eye_tracking == "ERRATIC":
        return list(np.random.uniform(-8, 8, n_points))
    elif eye_tracking == "MODERATE":
        return list(np.random.uniform(-4, 4, n_points))
    else:
        return list(np.sin(np.linspace(0, 4 * np.pi, n_points)) * 2)


if __name__ == "__main__":
    # Test biometric generation
    test_lap = {
        "lap": 47,
        "stress_index": 9.1,
        "mental_fatigue": 7.4,
        "decision_quality": 5.2,
        "tyre_age": 18,
        "tyre_compound": "SOFT",
        "radio_sentiment": -0.82,
        "gap_to_p2": 0.0,
        "position": 1,
        "race_events": '["SAFETY_CAR", "YELLOW_FLAG"]',
    }
    bio = generate_biometrics(test_lap)
    print("Lap 47 Biometrics:")
    for k, v in bio.items():
        print(f"  {k}: {v}")
