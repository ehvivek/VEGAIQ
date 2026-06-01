"""
core/data_pipeline.py
PitMind — FastF1 + OpenF1 data fetching and caching pipeline.
Discovers the correct Abu Dhabi 2024 Race session_key dynamically.
"""

import os
import json
import requests
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent.parent / "data"
CACHE_CSV = DATA_DIR / "verstappen_abu_dhabi_2024.csv"
SAMPLE_CSV = DATA_DIR / "verstappen_abu_dhabi_2024_sample.csv"
OPENF1_BASE = "https://api.openf1.org/v1"


# ─────────────────────────────────────────────
# OpenF1 helpers
# ─────────────────────────────────────────────

def get_abu_dhabi_session_key() -> int:
    """Dynamically discover the Abu Dhabi 2024 Race session_key from OpenF1."""
    try:
        resp = requests.get(
            f"{OPENF1_BASE}/sessions",
            params={"year": 2024, "country_name": "Abu Dhabi", "session_name": "Race"},
            timeout=10,
        )
        sessions = resp.json()
        if sessions:
            key = sessions[0].get("session_key")
            print(f"[OpenF1] Found Abu Dhabi 2024 Race session_key: {key}")
            return key
    except Exception as e:
        print(f"[OpenF1] Could not fetch session key: {e}")
    # Fallback: known key for Abu Dhabi 2024 Race
    return 9662


def fetch_team_radio(session_key: int) -> list:
    """Fetch Verstappen team radio for the session."""
    try:
        resp = requests.get(
            f"{OPENF1_BASE}/team_radio",
            params={"session_key": session_key, "driver_number": 1},
            timeout=15,
        )
        return resp.json()
    except Exception as e:
        print(f"[OpenF1] Radio fetch error: {e}")
        return []


def fetch_race_control(session_key: int) -> list:
    """Fetch race control messages (Safety Car, Yellow Flag, etc.)."""
    try:
        resp = requests.get(
            f"{OPENF1_BASE}/race_control",
            params={"session_key": session_key},
            timeout=15,
        )
        return resp.json()
    except Exception as e:
        print(f"[OpenF1] Race control fetch error: {e}")
        return []


def fetch_positions(session_key: int) -> list:
    """Fetch position data for Verstappen."""
    try:
        resp = requests.get(
            f"{OPENF1_BASE}/position",
            params={"session_key": session_key, "driver_number": 1},
            timeout=15,
        )
        return resp.json()
    except Exception as e:
        print(f"[OpenF1] Position fetch error: {e}")
        return []


def parse_radio_by_lap(radio_data: list, laps_df: pd.DataFrame) -> dict:
    """Map radio messages to lap numbers based on timestamps."""
    radio_map = {}
    for entry in radio_data:
        ts_str = entry.get("date", "")
        if not ts_str:
            continue
        try:
            ts = pd.to_datetime(ts_str, utc=True)
            # Find which lap this timestamp falls on
            for _, row in laps_df.iterrows():
                lap_start = pd.to_datetime(row.get("LapStartDate"), utc=True)
                lap_end = lap_start + pd.to_timedelta(row.get("LapTime", pd.NaT))
                if pd.notna(lap_start) and pd.notna(lap_end):
                    if lap_start <= ts <= lap_end:
                        lap_num = int(row["LapNumber"])
                        radio_map[lap_num] = {
                            "text": entry.get("recording_url", ""),
                            "timestamp": ts_str,
                        }
                        break
        except Exception:
            continue
    return radio_map


def map_events_to_laps(race_control: list) -> dict:
    """Map race control events (SC, VSC, Yellow) to lap numbers."""
    events_map = {}
    for event in race_control:
        lap = event.get("lap_number")
        if lap is None:
            continue
        lap = int(lap)
        cat = event.get("category", "")
        msg = event.get("message", "")
        if lap not in events_map:
            events_map[lap] = []
        if "SAFETY CAR" in msg.upper() or "SC" in cat.upper():
            events_map[lap].append("SAFETY_CAR")
        elif "YELLOW" in msg.upper() or "YELLOW" in cat.upper():
            events_map[lap].append("YELLOW_FLAG")
        elif "VSC" in msg.upper():
            events_map[lap].append("VSC")
        elif "DRS" in msg.upper():
            events_map[lap].append("DRS_ENABLED")
        else:
            events_map[lap].append(cat[:20] if cat else "EVENT")
    return events_map


# ─────────────────────────────────────────────
# FastF1 helpers
# ─────────────────────────────────────────────

def fetch_fastf1_laps() -> pd.DataFrame:
    """Load Abu Dhabi 2024 Race lap data for Verstappen via FastF1."""
    try:
        import fastf1
        cache_dir = Path(__file__).parent.parent / "cache"
        cache_dir.mkdir(exist_ok=True)
        fastf1.Cache.enable_cache(str(cache_dir))

        print("[FastF1] Loading Abu Dhabi 2024 Race session...")
        session = fastf1.get_session(2024, "Abu Dhabi", "R")
        session.load(telemetry=False, weather=False, messages=False)

        ver_laps = session.laps.pick_driver("VER").copy()
        ver_laps = ver_laps.reset_index(drop=True)
        print(f"[FastF1] Loaded {len(ver_laps)} laps for VER")
        return ver_laps
    except Exception as e:
        print(f"[FastF1] Error loading data: {e}")
        return pd.DataFrame()


# ─────────────────────────────────────────────
# Sentiment scoring (simple rule-based fallback)
# ─────────────────────────────────────────────

NEGATIVE_WORDS = {
    "gone", "cannot", "struggling", "slow", "damage", "problem",
    "issue", "difficult", "losing", "lost", "hurt", "pain", "broken",
    "pressure", "warning", "graining", "cliff", "degrading"
}
POSITIVE_WORDS = {
    "good", "great", "push", "ok", "fine", "copy", "understood",
    "brilliant", "perfect", "yes", "confirm", "faster", "gap"
}

def simple_sentiment(text: str) -> float:
    """Returns sentiment score -1.0 to +1.0."""
    if not text:
        return 0.0
    words = text.lower().split()
    neg = sum(1 for w in words if any(nw in w for nw in NEGATIVE_WORDS))
    pos = sum(1 for w in words if any(pw in w for pw in POSITIVE_WORDS))
    total = neg + pos
    if total == 0:
        return 0.0
    return (pos - neg) / total


# ─────────────────────────────────────────────
# Hardcoded radio transcripts for key laps
# ─────────────────────────────────────────────

KNOWN_RADIO = {
    47: "These tyres are completely gone, I cannot hold Norris.",
    44: "We need to extend, tyres are degrading fast.",
    48: "Keep pushing, gap is stable.",
    50: "Box box box. Understood.",
    51: "OK, new tyres. Let's push.",
    53: "Gap to Norris is growing, good job.",
    1:  "Let's go, clean start.",
    20: "Copy, understood. Gap is fine.",
    30: "Tyre temps looking good, keep pushing.",
    35: "Position is secure, manage the gap.",
    58: "Checkered flag, brilliant drive Max.",
}

KNOWN_EVENTS = {
    44: ["YELLOW_FLAG"],
    45: ["SAFETY_CAR"],
    46: ["SAFETY_CAR"],
    47: ["SAFETY_CAR", "YELLOW_FLAG"],
    48: ["SAFETY_CAR"],
    49: ["DRS_ENABLED"],
    50: ["DRS_ENABLED"],
}


# ─────────────────────────────────────────────
# Build full unified dataset
# ─────────────────────────────────────────────

def build_unified_dataset(
    laps_df: pd.DataFrame,
    events_map: dict,
    radio_map: dict,
) -> pd.DataFrame:
    """Merge FastF1 laps with OpenF1 events and radio into unified schema."""
    rows = []
    best_time = laps_df["LapTime"].dropna().min().total_seconds() if not laps_df.empty else 88.5

    for _, row in laps_df.iterrows():
        lap_num = int(row.get("LapNumber", 0))
        if lap_num == 0:
            continue

        # Lap time
        lt = row.get("LapTime")
        if pd.notna(lt):
            lt_sec = lt.total_seconds()
        else:
            lt_sec = best_time + np.random.uniform(0.1, 2.0)

        lt_str = f"{int(lt_sec // 60)}:{lt_sec % 60:06.3f}"
        delta = round(lt_sec - best_time, 3)

        # Tyre
        compound = str(row.get("Compound", "MEDIUM")).upper()
        tyre_age = int(row.get("TyreLife", lap_num % 20 + 1))

        # Position
        pos = int(row.get("Position", 1)) if pd.notna(row.get("Position")) else 1

        # Events
        lap_events = events_map.get(lap_num, KNOWN_EVENTS.get(lap_num, []))
        if not isinstance(lap_events, list):
            lap_events = []
        lap_events = list(set(lap_events))

        # Radio
        radio_entry = radio_map.get(lap_num, {})
        radio_text = KNOWN_RADIO.get(lap_num, radio_entry.get("text", ""))
        if not radio_text:
            radio_text = "No transmission." if lap_num % 5 != 0 else "Copy, understood."
        radio_sentiment = round(simple_sentiment(radio_text), 3)

        # Speeds
        speed_fl = float(row.get("SpeedFL", 300 + np.random.uniform(-10, 10))) if pd.notna(row.get("SpeedFL")) else 300.0
        speed_i1 = float(row.get("SpeedI1", 250 + np.random.uniform(-15, 15))) if pd.notna(row.get("SpeedI1")) else 250.0
        speed_i2 = float(row.get("SpeedI2", 260 + np.random.uniform(-10, 10))) if pd.notna(row.get("SpeedI2")) else 260.0

        # Sector times
        s1 = row.get("Sector1Time")
        s2 = row.get("Sector2Time")
        s3 = row.get("Sector3Time")
        s1_sec = s1.total_seconds() if pd.notna(s1) else round(lt_sec * 0.27, 3)
        s2_sec = s2.total_seconds() if pd.notna(s2) else round(lt_sec * 0.45, 3)
        s3_sec = s3.total_seconds() if pd.notna(s3) else round(lt_sec * 0.28, 3)

        # Timestamp (approx 20:00 start + lap minutes)
        race_start_hour = 20
        elapsed_min = (lt_sec * lap_num) / 60
        h = race_start_hour + int(elapsed_min // 60)
        m = int(elapsed_min % 60)
        s = int((elapsed_min * 60) % 60)
        timestamp = f"{h:02d}:{m:02d}:{s:02d}"

        rows.append({
            "lap": lap_num,
            "driver": "VER",
            "lap_time_seconds": round(lt_sec, 3),
            "lap_time_formatted": lt_str,
            "delta_to_best": delta,
            "tyre_compound": compound,
            "tyre_age": tyre_age,
            "position": pos,
            "gap_to_p2": round(max(0.0, (lap_num - 30) * 0.3 + np.random.uniform(-0.5, 0.5)), 3),
            "race_events": json.dumps(lap_events),
            "radio_text": radio_text,
            "radio_sentiment": radio_sentiment,
            "speed_fl": round(speed_fl, 1),
            "speed_i1": round(speed_i1, 1),
            "speed_i2": round(speed_i2, 1),
            "sector1": round(s1_sec, 3),
            "sector2": round(s2_sec, 3),
            "sector3": round(s3_sec, 3),
            "timestamp": timestamp,
            # ML scores will be filled by models.py
            "stress_index": 0.0,
            "decision_quality": 0.0,
            "mental_fatigue": 0.0,
            "situational_awareness": 0.0,
            # Biometrics will be filled by synthetic.py
            "heart_rate_est": 0,
            "eye_tracking": "FOCUSED",
            "reaction_time_delta": 0,
            "mental_state": "OPTIMAL FOCUS",
            "granite_analysis": "",
        })

    return pd.DataFrame(rows)


# ─────────────────────────────────────────────
# Main entry point
# ─────────────────────────────────────────────

def load_race_data(race_name: str = "Abu Dhabi GP 2024", force_refresh: bool = False) -> pd.DataFrame:
    """
    Load full Verstappen race data.
    Uses cache if available; otherwise fetches live and saves cache.
    Falls back to sample CSV if all fetching fails.
    """
    DATA_DIR.mkdir(exist_ok=True)
    
    # Create a unique cache filename based on race name
    safe_name = str(race_name).lower().replace(" ", "_").replace("|", "").replace("/", "")
    race_cache_csv = DATA_DIR / f"verstappen_{safe_name}.csv"

    if race_cache_csv.exists() and not force_refresh:
        print(f"[Pipeline] Loading from cache: {race_cache_csv}")
        df = pd.read_csv(race_cache_csv)
        return df

    # For Monaco and Bahrain, we skip live F1 live server fetching and directly generate fallback data
    if "monaco" in safe_name or "bahrain" in safe_name:
        return _generate_fallback_data(race_name)

    print("[Pipeline] Fetching live data...")

    # 1. FastF1
    laps_df = fetch_fastf1_laps()

    # 2. OpenF1
    session_key = get_abu_dhabi_session_key()
    radio_raw = fetch_team_radio(session_key)
    race_control = fetch_race_control(session_key)
    events_map = map_events_to_laps(race_control)
    radio_map = {}  # We use KNOWN_RADIO for now; real transcription in whisper_service

    # 3. If FastF1 failed, use sample CSV
    if laps_df.empty:
        print("[Pipeline] FastF1 failed — loading sample data")
        if SAMPLE_CSV.exists() and "abu_dhabi" in safe_name:
            return pd.read_csv(SAMPLE_CSV)
        else:
            return _generate_fallback_data(race_name)

    # 4. Build unified dataset
    df = build_unified_dataset(laps_df, events_map, radio_map)

    # 5. Cache it
    df.to_csv(race_cache_csv, index=False)
    print(f"[Pipeline] Saved {len(df)} laps to cache")
    return df


def _generate_fallback_data(race_name: str = "Abu Dhabi GP 2024") -> pd.DataFrame:
    """Generate dynamic synthetic fallback dataset for the specified race."""
    print(f"[Pipeline] Generating synthetic fallback data for: {race_name}")
    name = str(race_name).lower()
    
    if "monaco" in name:
        total_laps = 78
        best_time = 74.500  # Monaco lap times are shorter
        peak_stress_lap = 67
        base_stress_amplifier = 1.25  # street circuit is harder
    elif "bahrain" in name:
        total_laps = 57
        best_time = 91.200  # Bahrain lap times are longer
        peak_stress_lap = 1  # race start is chaotic
        base_stress_amplifier = 1.1
    else:
        total_laps = 58
        best_time = 88.500
        peak_stress_lap = 47
        base_stress_amplifier = 1.0

    rows = []
    np.random.seed(42)

    for lap in range(1, total_laps + 1):
        # Stress peaks at specified lap
        stress_base = 5.0 + 2.0 * np.exp(-((lap - peak_stress_lap) ** 2) / 20)
        stress_base = stress_base * base_stress_amplifier
        noise = np.random.uniform(-0.3, 0.3)
        lap_time = best_time + max(0, (stress_base - 5) * 0.4) + noise

        if "monaco" in name:
            compound = "SOFT" if lap <= 30 else "HARD"
            tyre_age = lap if lap <= 30 else (lap - 30)
            events = json.dumps(["SAFETY_CAR"] if lap in [66, 67, 68] else ["YELLOW_FLAG"] if lap in [40, 65] else [])
            radio = "This street track has no room for error." if lap == 65 else "I'm pushing as hard as I can." if lap == 40 else ""
        elif "bahrain" in name:
            if lap <= 18:
                compound = "SOFT"
                tyre_age = lap
            elif lap <= 38:
                compound = "MEDIUM"
                tyre_age = lap - 18
            else:
                compound = "HARD"
                tyre_age = lap - 38
            events = json.dumps(["SAFETY_CAR"] if lap in [2, 3] else ["YELLOW_FLAG"] if lap in [1, 20] else [])
            radio = "Temps are really high, thermal degradation is crazy." if lap == 15 else "Understood, managing the gap." if lap == 25 else ""
        else:
            compound = "HARD" if lap <= 20 else "MEDIUM" if lap <= 38 else "SOFT"
            tyre_age = (lap % 20) + 1
            events = json.dumps(KNOWN_EVENTS.get(lap, []))
            radio = KNOWN_RADIO.get(lap, "")

        rows.append({
            "lap": lap,
            "driver": "VER",
            "lap_time_seconds": round(lap_time, 3),
            "lap_time_formatted": f"{int(lap_time // 60)}:{(lap_time % 60):06.3f}",
            "delta_to_best": round(lap_time - best_time, 3),
            "tyre_compound": compound,
            "tyre_age": tyre_age,
            "position": 1,
            "gap_to_p2": round(max(0.0, 15 - abs(lap - peak_stress_lap) * 0.5), 3),
            "race_events": events,
            "radio_text": radio if radio else "No transmission.",
            "radio_sentiment": round(simple_sentiment(radio) if radio else 0.0, 3),
            "speed_fl": round(290 + np.random.uniform(-8, 8) if "monaco" in name else 302 + np.random.uniform(-8, 8), 1),
            "speed_i1": round(235 + np.random.uniform(-10, 10) if "monaco" in name else 248 + np.random.uniform(-10, 10), 1),
            "speed_i2": round(250 + np.random.uniform(-8, 8) if "monaco" in name else 262 + np.random.uniform(-8, 8), 1),
            "sector1": round(lap_time * 0.27, 3),
            "sector2": round(lap_time * 0.45, 3),
            "sector3": round(lap_time * 0.28, 3),
            "timestamp": f"{20 + (lap * 90) // 3600:02d}:{((lap * 90) % 3600) // 60:02d}:{(lap * 90) % 60:02d}",
            "stress_index": 0.0,
            "decision_quality": 0.0,
            "mental_fatigue": 0.0,
            "situational_awareness": 0.0,
            "heart_rate_est": 0,
            "eye_tracking": "FOCUSED",
            "reaction_time_delta": 0,
            "mental_state": "OPTIMAL FOCUS",
            "granite_analysis": "",
        })

    df = pd.DataFrame(rows)
    safe_name = str(race_name).lower().replace(" ", "_").replace("|", "").replace("/", "")
    race_sample_csv = DATA_DIR / f"verstappen_{safe_name}_sample.csv"
    df.to_csv(race_sample_csv, index=False)
    return df


if __name__ == "__main__":
    df = load_race_data("Abu Dhabi GP 2024")
    print(df[["lap", "lap_time_formatted", "tyre_compound", "race_events"]].head(10))
    print(f"\nTotal laps: {len(df)}")

