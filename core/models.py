"""
core/models.py
PitMind — 3 Machine Learning Models for per-lap psychological scoring.

Model 1: Stress Index (GradientBoostingRegressor)
Model 2: Decision Quality Score (RandomForestRegressor)
Model 3: Mental Fatigue Estimate (Ridge)

All models trained on synthetically generated data mirroring real F1 patterns.
"""

import os
import json
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

MODELS_DIR = Path(__file__).parent.parent / "models"
MODELS_DIR.mkdir(exist_ok=True)

STRESS_MODEL_PATH = MODELS_DIR / "stress_model.pkl"
QUALITY_MODEL_PATH = MODELS_DIR / "quality_model.pkl"
FATIGUE_MODEL_PATH = MODELS_DIR / "fatigue_model.pkl"


# ─────────────────────────────────────────────
# Training data generation
# ─────────────────────────────────────────────

def generate_training_data(n_samples: int = 2000) -> pd.DataFrame:
    """
    Generate synthetic F1 lap data for model training.
    Relationships are based on established sports psychology and F1 analytics.
    """
    np.random.seed(42)
    rows = []

    for i in range(n_samples):
        lap = np.random.randint(1, 59)
        safety_car = np.random.binomial(1, 0.08)
        yellow_flag = np.random.binomial(1, 0.12)
        vsc = np.random.binomial(1, 0.05)

        tyre_age = np.random.randint(1, 35)
        tyre_compound = np.random.choice([0, 1, 2])  # HARD=0, MEDIUM=1, SOFT=2

        # Gap dynamics
        gap_to_leader = np.random.exponential(3.0)
        gap_change_last3 = np.random.normal(0, 0.5)
        gap_shrinking = 1 if gap_change_last3 < -0.2 else 0

        # Position
        position = np.random.randint(1, 5)
        position_change = np.random.randint(-3, 3)

        # Radio
        radio_sentiment = np.random.normal(0, 0.5)
        radio_sentiment = np.clip(radio_sentiment, -1.0, 1.0)

        # Lap time vs best
        best_time = 88.5
        lap_time_delta = abs(np.random.normal(0.8, 1.2))

        # Sector deltas
        sector1_delta = np.random.normal(0.1, 0.3)
        sector2_delta = np.random.normal(0.15, 0.4)
        sector3_delta = np.random.normal(0.1, 0.25)

        # Speeds
        speed_fl = np.random.normal(302, 8)
        speed_i1 = np.random.normal(248, 10)
        speed_i2 = np.random.normal(262, 8)

        # Stint / fatigue features
        stint_lap = lap % 20 + 1
        laps_remaining = 58 - lap
        avg_speed_drop = np.random.normal(0, 2)
        sector_consistency = np.random.exponential(0.15)
        lap_time_trend_last5 = np.random.normal(0.05, 0.2)
        radio_freq = np.random.randint(0, 4)

        # ── Stress Index (0-10) ──
        stress = 5.0
        stress += safety_car * 2.5
        stress += yellow_flag * 1.2
        stress += vsc * 0.8
        stress += (tyre_age / 35) * 1.5
        stress += abs(radio_sentiment) * 1.0
        stress += gap_shrinking * 1.0
        stress += max(0, (3 - gap_to_leader)) * 0.5
        stress += (1 - laps_remaining / 58) * 0.8
        stress += np.random.normal(0, 0.4)
        stress = float(np.clip(stress, 0, 10))

        # ── Decision Quality (0-10) ──
        quality = 7.0
        quality -= lap_time_delta * 0.8
        quality -= abs(sector1_delta) * 0.4
        quality -= abs(sector2_delta) * 0.5
        quality -= abs(sector3_delta) * 0.3
        quality += (speed_fl - 295) / 10
        quality -= abs(position_change) * 0.2
        quality -= (tyre_age / 35) * 0.5
        quality += np.random.normal(0, 0.3)
        quality = float(np.clip(quality, 0, 10))

        # ── Mental Fatigue (0-10) ──
        fatigue = 4.0
        fatigue += (lap / 58) * 3.0
        fatigue += (stress * 0.3)
        fatigue += (radio_freq * 0.3)
        fatigue += (lap_time_trend_last5 * 1.5)
        fatigue += (avg_speed_drop * 0.2)
        fatigue += (sector_consistency * 2.0)
        fatigue += np.random.normal(0, 0.3)
        fatigue = float(np.clip(fatigue, 0, 10))

        # Cumulative stress proxy
        cumulative_stress = stress * (lap / 58)

        rows.append({
            # Stress features
            "gap_change_last3": gap_change_last3,
            "safety_car": safety_car,
            "yellow_flag": yellow_flag,
            "tyre_age": tyre_age,
            "tyre_compound": tyre_compound,
            "radio_sentiment": radio_sentiment,
            "position_change": position_change,
            "laps_remaining": laps_remaining,
            "gap_to_leader": gap_to_leader,
            # Quality features
            "lap_time_delta": lap_time_delta,
            "sector1_delta": sector1_delta,
            "sector2_delta": sector2_delta,
            "sector3_delta": sector3_delta,
            "speed_fl": speed_fl,
            "speed_i1": speed_i1,
            "speed_i2": speed_i2,
            "position_delta": position_change,
            # Fatigue features
            "stint_lap": stint_lap,
            "cumulative_stress": cumulative_stress,
            "radio_freq": radio_freq,
            "lap_time_trend": lap_time_trend_last5,
            "total_laps": lap,
            "avg_speed_drop": avg_speed_drop,
            "sector_consistency": sector_consistency,
            # Targets
            "stress_index": stress,
            "decision_quality": quality,
            "mental_fatigue": fatigue,
        })

    return pd.DataFrame(rows)


# ─────────────────────────────────────────────
# Feature sets
# ─────────────────────────────────────────────

STRESS_FEATURES = [
    "gap_change_last3", "safety_car", "yellow_flag", "tyre_age",
    "tyre_compound", "radio_sentiment", "position_change",
    "laps_remaining", "gap_to_leader",
]

QUALITY_FEATURES = [
    "lap_time_delta", "sector1_delta", "sector2_delta", "sector3_delta",
    "speed_fl", "speed_i1", "speed_i2", "position_delta", "tyre_age",
]

FATIGUE_FEATURES = [
    "stint_lap", "cumulative_stress", "radio_freq", "lap_time_trend",
    "total_laps", "avg_speed_drop", "sector_consistency",
]


# ─────────────────────────────────────────────
# Train models
# ─────────────────────────────────────────────

def train_models(force: bool = False):
    """Train all 3 models and save as .pkl files."""
    if (
        not force
        and STRESS_MODEL_PATH.exists()
        and QUALITY_MODEL_PATH.exists()
        and FATIGUE_MODEL_PATH.exists()
    ):
        print("[Models] All models already trained. Loading from disk.")
        return

    print("[Models] Generating training data...")
    df = generate_training_data(2000)

    # ── Model 1: Stress Index ──
    print("[Models] Training Model 1 — Stress Index (GradientBoostingRegressor)...")
    X_stress = df[STRESS_FEATURES]
    y_stress = df["stress_index"]
    stress_model = Pipeline([
        ("scaler", StandardScaler()),
        ("model", GradientBoostingRegressor(
            n_estimators=150, max_depth=4, learning_rate=0.08,
            subsample=0.8, random_state=42
        )),
    ])
    stress_model.fit(X_stress, y_stress)
    joblib.dump(stress_model, STRESS_MODEL_PATH)
    print(f"[Models] Stress model saved → {STRESS_MODEL_PATH}")

    # ── Model 2: Decision Quality ──
    print("[Models] Training Model 2 — Decision Quality (RandomForestRegressor)...")
    X_quality = df[QUALITY_FEATURES]
    y_quality = df["decision_quality"]
    quality_model = Pipeline([
        ("scaler", StandardScaler()),
        ("model", RandomForestRegressor(
            n_estimators=150, max_depth=6, min_samples_leaf=3,
            random_state=42, n_jobs=-1
        )),
    ])
    quality_model.fit(X_quality, y_quality)
    joblib.dump(quality_model, QUALITY_MODEL_PATH)
    print(f"[Models] Quality model saved → {QUALITY_MODEL_PATH}")

    # ── Model 3: Mental Fatigue ──
    print("[Models] Training Model 3 — Mental Fatigue (Ridge)...")
    X_fatigue = df[FATIGUE_FEATURES]
    y_fatigue = df["mental_fatigue"]
    fatigue_model = Pipeline([
        ("scaler", StandardScaler()),
        ("model", Ridge(alpha=1.0)),
    ])
    fatigue_model.fit(X_fatigue, y_fatigue)
    joblib.dump(fatigue_model, FATIGUE_MODEL_PATH)
    print(f"[Models] Fatigue model saved → {FATIGUE_MODEL_PATH}")

    print("[Models] All 3 models trained and saved.")


# ─────────────────────────────────────────────
# Load models
# ─────────────────────────────────────────────

_stress_model = None
_quality_model = None
_fatigue_model = None


def load_models():
    """Load all 3 trained models from disk."""
    global _stress_model, _quality_model, _fatigue_model
    if not (STRESS_MODEL_PATH.exists() and QUALITY_MODEL_PATH.exists() and FATIGUE_MODEL_PATH.exists()):
        train_models()
    _stress_model = joblib.load(STRESS_MODEL_PATH)
    _quality_model = joblib.load(QUALITY_MODEL_PATH)
    _fatigue_model = joblib.load(FATIGUE_MODEL_PATH)
    print("[Models] All 3 models loaded.")


# ─────────────────────────────────────────────
# Per-lap inference
# ─────────────────────────────────────────────

def build_feature_row(lap_data: dict, best_time: float = 88.5) -> dict:
    """Build feature dictionary from a lap data row."""
    import json

    events_raw = lap_data.get("race_events", "[]")
    if isinstance(events_raw, str):
        try:
            events = json.loads(events_raw)
        except Exception:
            events = []
    else:
        events = events_raw if isinstance(events_raw, list) else []

    safety_car = 1 if "SAFETY_CAR" in events else 0
    yellow_flag = 1 if "YELLOW_FLAG" in events else 0
    vsc = 1 if "VSC" in events else 0

    compound_map = {"HARD": 0, "MEDIUM": 1, "SOFT": 2, "INTER": 1, "WET": 0}
    tyre_compound = compound_map.get(str(lap_data.get("tyre_compound", "MEDIUM")).upper(), 1)

    lap_num = int(lap_data.get("lap", 30))
    lt = float(lap_data.get("lap_time_seconds", best_time + 1))
    tyre_age = int(lap_data.get("tyre_age", 10))
    gap = float(lap_data.get("gap_to_p2", 5.0))
    pos = int(lap_data.get("position", 1))
    radio_sent = float(lap_data.get("radio_sentiment", 0.0))

    s1 = float(lap_data.get("sector1", lt * 0.27))
    s2 = float(lap_data.get("sector2", lt * 0.45))
    s3 = float(lap_data.get("sector3", lt * 0.28))
    best_s1, best_s2, best_s3 = best_time * 0.27, best_time * 0.45, best_time * 0.28

    speed_fl = float(lap_data.get("speed_fl", 302))
    speed_i1 = float(lap_data.get("speed_i1", 248))
    speed_i2 = float(lap_data.get("speed_i2", 262))

    return {
        # Stress features
        "gap_change_last3": np.random.normal(0, 0.3) if gap < 1.0 else 0.1,
        "safety_car": safety_car,
        "yellow_flag": yellow_flag,
        "tyre_age": tyre_age,
        "tyre_compound": tyre_compound,
        "radio_sentiment": radio_sent,
        "position_change": 0,
        "laps_remaining": 58 - lap_num,
        "gap_to_leader": gap,
        # Quality features
        "lap_time_delta": max(0, lt - best_time),
        "sector1_delta": s1 - best_s1,
        "sector2_delta": s2 - best_s2,
        "sector3_delta": s3 - best_s3,
        "speed_fl": speed_fl,
        "speed_i1": speed_i1,
        "speed_i2": speed_i2,
        "position_delta": 0,
        # Fatigue features
        "stint_lap": (lap_num % 20) + 1,
        "cumulative_stress": 5.0 * (lap_num / 58),  # approx
        "radio_freq": 1 if radio_sent != 0 else 0,
        "lap_time_trend": max(0, lt - best_time) * 0.1,
        "total_laps": lap_num,
        "avg_speed_drop": max(0, 302 - speed_fl),
        "sector_consistency": abs(s1 - best_s1) + abs(s2 - best_s2) + abs(s3 - best_s3),
    }


def predict_lap(lap_data: dict, best_time: float = 88.5) -> dict:
    """Run all 3 models on a single lap. Returns {stress, quality, fatigue}."""
    global _stress_model, _quality_model, _fatigue_model
    if _stress_model is None:
        load_models()

    feats = build_feature_row(lap_data, best_time)

    stress = float(np.clip(_stress_model.predict(
        pd.DataFrame([feats])[STRESS_FEATURES])[0], 0, 10))
    quality = float(np.clip(_quality_model.predict(
        pd.DataFrame([feats])[QUALITY_FEATURES])[0], 0, 10))
    fatigue = float(np.clip(_fatigue_model.predict(
        pd.DataFrame([feats])[FATIGUE_FEATURES])[0], 0, 10))

    return {
        "stress_index": round(stress, 1),
        "decision_quality": round(quality, 1),
        "mental_fatigue": round(fatigue, 1),
    }


def predict_all_laps(df: pd.DataFrame) -> pd.DataFrame:
    """Run all 3 models on every lap in the dataframe."""
    df = df.copy()
    best_time = df["lap_time_seconds"].min() if "lap_time_seconds" in df.columns else 88.5

    print(f"[Models] Running inference on {len(df)} laps...")
    predictions = []
    for _, row in df.iterrows():
        pred = predict_lap(row.to_dict(), best_time)
        predictions.append(pred)

    pred_df = pd.DataFrame(predictions)
    df["stress_index"] = pred_df["stress_index"].values
    df["decision_quality"] = pred_df["decision_quality"].values
    df["mental_fatigue"] = pred_df["mental_fatigue"].values

    print("[Models] All laps scored.")
    return df


if __name__ == "__main__":
    train_models(force=True)
    # Quick test
    test = {
        "lap": 47, "lap_time_seconds": 89.987, "tyre_age": 18,
        "tyre_compound": "SOFT", "radio_sentiment": -0.82,
        "gap_to_p2": 0.0, "position": 1,
        "race_events": '["SAFETY_CAR", "YELLOW_FLAG"]',
        "sector1": 24.1, "sector2": 42.5, "sector3": 23.4,
        "speed_fl": 298, "speed_i1": 241, "speed_i2": 255,
    }
    scores = predict_lap(test)
    print("\nLap 47 Model Scores:")
    for k, v in scores.items():
        print(f"  {k}: {v}/10")
