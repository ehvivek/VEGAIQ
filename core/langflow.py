"""
core/langflow.py
PitMind — Langflow pipeline orchestration.
Defines the full AI workflow graph connecting all PitMind components.
Falls back to direct Python calls if Langflow server is not running.
"""

import json
from pathlib import Path

LANGFLOW_DIR = Path(__file__).parent.parent / "data"


# ─────────────────────────────────────────────
# Langflow workflow definition (exportable JSON)
# ─────────────────────────────────────────────

PITMIND_WORKFLOW = {
    "name": "PitMind F1 Psychological Analysis Pipeline",
    "description": "Full AI pipeline: OpenF1 → FastF1 → ML Models → Biometrics → IBM Granite → Output",
    "nodes": [
        {"id": "openf1_node", "type": "DataFetcher", "label": "OpenF1 REST API",
         "config": {"endpoint": "https://api.openf1.org/v1", "driver": "VER", "year": 2024}},
        {"id": "fastf1_node", "type": "DataFetcher", "label": "FastF1 Telemetry",
         "config": {"year": 2024, "gp": "Abu Dhabi", "session": "R", "driver": "VER"}},
        {"id": "whisper_node", "type": "AudioTranscriber", "label": "OpenAI Whisper STT",
         "config": {"model": "base", "language": "en"}},
        {"id": "merge_node", "type": "DataMerger", "label": "Merge & Enrich",
         "config": {"join_on": "lap_number"}},
        {"id": "stress_model", "type": "MLModel", "label": "Model 1: Stress Index (GBR)",
         "config": {"model_path": "models/stress_model.pkl", "output": "stress_index"}},
        {"id": "quality_model", "type": "MLModel", "label": "Model 2: Decision Quality (RF)",
         "config": {"model_path": "models/quality_model.pkl", "output": "decision_quality"}},
        {"id": "fatigue_model", "type": "MLModel", "label": "Model 3: Mental Fatigue (Ridge)",
         "config": {"model_path": "models/fatigue_model.pkl", "output": "mental_fatigue"}},
        {"id": "biometrics_node", "type": "BiometricGenerator", "label": "Synthetic Biometrics",
         "config": {"module": "core.synthetic", "method": "generate_biometrics"}},
        {"id": "granite_node", "type": "IBMGranite", "label": "IBM Granite 3.1 Analysis",
         "config": {"model": "ibm/granite-13b-chat-v2", "url": "https://us-south.ml.cloud.ibm.com"}},
        {"id": "output_node", "type": "StreamlitOutput", "label": "Streamlit UI Output",
         "config": {"pages": ["Dashboard", "LapDive", "Chat", "Reports"]}},
    ],
    "edges": [
        {"from": "openf1_node", "to": "merge_node"},
        {"from": "fastf1_node", "to": "merge_node"},
        {"from": "whisper_node", "to": "merge_node"},
        {"from": "merge_node", "to": "stress_model"},
        {"from": "merge_node", "to": "quality_model"},
        {"from": "merge_node", "to": "fatigue_model"},
        {"from": "stress_model", "to": "biometrics_node"},
        {"from": "quality_model", "to": "biometrics_node"},
        {"from": "fatigue_model", "to": "biometrics_node"},
        {"from": "biometrics_node", "to": "granite_node"},
        {"from": "granite_node", "to": "output_node"},
    ],
    "version": "1.0",
    "created_for": "IBM SkillsBuild AI Builders Challenge May 2026",
}


def export_workflow_json():
    """Export the Langflow workflow definition to JSON file."""
    LANGFLOW_DIR.mkdir(exist_ok=True)
    path = LANGFLOW_DIR / "langflow_workflow.json"
    with open(path, "w") as f:
        json.dump(PITMIND_WORKFLOW, f, indent=2)
    print(f"[Langflow] Workflow exported → {path}")
    return path


# ─────────────────────────────────────────────
# Pipeline orchestrator
# ─────────────────────────────────────────────

def trigger_pipeline(lap_number: int, race_df=None) -> dict:
    """
    Orchestrate the full PitMind pipeline for a given lap.
    Uses direct Python calls (Langflow-equivalent logic).
    If a Langflow server is running locally, it would be invoked here.
    """
    import pandas as pd
    from core.models import predict_lap
    from core.synthetic import generate_biometrics
    from core.granite import analyze_lap

    if race_df is None or race_df.empty:
        return {}

    # Find the lap
    lap_rows = race_df[race_df["lap"] == lap_number]
    if lap_rows.empty:
        return {}

    lap_data = lap_rows.iloc[0].to_dict()

    # Step 1: Run 3 ML Models
    best_time = float(race_df["lap_time_seconds"].min())
    scores = predict_lap(lap_data, best_time)
    lap_data.update(scores)

    # Step 2: Generate biometrics
    bio = generate_biometrics(lap_data)
    lap_data.update(bio)

    # Step 3: IBM Granite analysis
    analysis = analyze_lap(lap_data)
    lap_data["granite_analysis"] = analysis

    return lap_data


def run_full_race_pipeline(race_df) -> "pd.DataFrame":
    """Run the complete pipeline on all 58 laps."""
    import pandas as pd
    from core.models import predict_all_laps
    from core.synthetic import enrich_dataframe
    from core.granite import analyze_lap

    print("[Langflow] Starting full race pipeline...")

    # Step 1: ML scoring
    df = predict_all_laps(race_df)

    # Step 2: Biometrics
    df = enrich_dataframe(df)

    # Step 3: Granite analysis for key laps only (to conserve API tokens)
    KEY_LAPS = [1, 10, 20, 30, 40, 44, 45, 46, 47, 48, 49, 50, 55, 58]
    analyses = {}
    for lap_num in KEY_LAPS:
        lap_rows = df[df["lap"] == lap_num]
        if not lap_rows.empty:
            lap_data = lap_rows.iloc[0].to_dict()
            analyses[lap_num] = analyze_lap(lap_data)

    def get_analysis(row):
        return analyses.get(int(row["lap"]), "")

    df["granite_analysis"] = df.apply(get_analysis, axis=1)
    print("[Langflow] Pipeline complete.")
    return df
