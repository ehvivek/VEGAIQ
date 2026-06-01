<div align="center">
  <img src="VEGAIQlogo.png" alt="VEGAIQ Logo" width="300" />
</div>

<div align="center">
  <h2>VEGAIQ — F1 Driver Psychological Analyzer</h2>
  <p><b>"Understand the mind. Beyond the data."</b></p>
  <p>The world's first public-facing F1 driver psychological analyzer — revealing the mental story inside the car that fans never get to see.</p>
</div>

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Streamlit-1.35+-FF4B4B?logo=streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/IBM_Granite-3.1-052FAD?logo=ibm&logoColor=white" alt="IBM Granite">
  <img src="https://img.shields.io/badge/scikit_learn-F7931E?logo=scikit-learn&logoColor=white" alt="scikit-learn">
  <img src="https://img.shields.io/badge/Plotly-3F4F75?logo=plotly&logoColor=white" alt="Plotly">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License">
</div>

---

## Problem Statement

F1 teams collect extensive private biometric and psychological data on their drivers — heart rate, stress levels, cognitive load, eye tracking. **Fans never see any of it.** We experience races through lap times and podium celebrations, but the real story — what happens *inside the driver's mind* under extreme pressure — remains hidden.

## Solution

**VEGAIQ** combines real F1 telemetry data, team radio analysis, synthetic biometric modeling, and IBM AI to publicly reveal the psychological story of a race, lap by lap. For the first time, fans can understand:

- When Verstappen's stress peaked and why
- How the Safety Car psychologically disrupted his race
- The relationship between mental fatigue and lap time degradation
- What his radio communications reveal about his cognitive state

## Demo: Abu Dhabi GP 2024 — Max Verstappen

VEGAIQ analyzes **Max Verstappen's complete Abu Dhabi GP 2024**, uncovering the critical **Lap 47 psychological crisis** triggered by Safety Car deployment, tyre degradation, and championship pressure.

---

## Built with IBM Technologies

<div align="center">
  <img src="https://upload.wikimedia.org/wikipedia/commons/5/51/IBM_logo.svg" alt="IBM Logo" width="120" />
</div>
<br>

| IBM Tool | Role in VEGAIQ | Integration |
|----------|----------------|-------------|
| **IBM Granite 3.1** | Primary AI brain — psychological analysis, conversational chat, sentiment analysis, report generation | `ibm-watsonx-ai` SDK via watsonx.ai API |
| **IBM Bob** | AI development assistant — used to scaffold, review, and debug code throughout development | IDE integration |
| **Langflow** | Visual AI pipeline orchestrator — connects all data sources, ML models, and AI components | Python SDK + exported workflow JSON |

### IBM Granite 3.1 Capabilities
1. **`analyze_lap()`** — Generates a multi-sentence psychological profile per lap using stress scores, radio, and race events.
2. **`chat_response()`** — Conversational answers about race psychology with multi-turn memory.
3. **`analyze_sentiment()`** — Radio transcript sentiment scoring (-1.0 to +1.0).
4. **`generate_report()`** — Comprehensive race psychological report generation.

---

## Data Sources

| Source | Type | What It Provides |
|--------|------|-----------------|
| <img src="https://img.shields.io/badge/FastF1-Python-3776AB?logo=python&logoColor=white" alt="FastF1" valign="middle"> | Python library | Lap times, sector times, speed traps, tyre data, position data |
| <img src="https://img.shields.io/badge/OpenF1-REST_API-009688?logo=openapi-initiative&logoColor=white" alt="OpenF1" valign="middle"> | REST API | Team radio timestamps, race control events (SC, Yellow, VSC) |
| <img src="https://img.shields.io/badge/OpenAI_Whisper-Speech_to_Text-412991?logo=openai&logoColor=white" alt="Whisper" valign="middle"> | Speech-to-Text | Voice input transcription for the AI chat interface |

---

## Machine Learning Models

| Model | Algorithm | Output | Key Features |
|-------|-----------|--------|-------------|
| **Stress Index** | GradientBoostingRegressor | 0-10 score/lap | Gap change, safety car, yellow flag, tyre age, radio sentiment, position change |
| **Decision Quality** | RandomForestRegressor | 0-10 score/lap | Lap time delta, sector deltas, speed trap data, position delta |
| **Mental Fatigue** | Ridge Regression | 0-10 score/lap | Stint length, cumulative stress, radio frequency, lap time trend |

*All models are trained on 2,000 synthetically generated F1 lap records mirroring real race patterns using `scikit-learn`.*

---

## Synthetic Biometrics

> **Disclosure:** Heart rate, eye tracking, reaction time, and mental state estimates are **modeled from real performance telemetry** using established sports psychology stress indicators. They are NOT directly measured biometric data. This is a standard methodology when direct biometric measurement is unavailable, used widely in sports science research.

| Biometric | Calculation Basis |
|-----------|------------------|
| **Heart Rate (BPM)** | Base 145 + safety car shock + tyre degradation + radio sentiment + gap pressure |
| **Mental State** | Derived from Stress Index threshold classification |
| **Eye Tracking** | Stress-correlated gaze stability estimation |
| **Reaction Time** | Cognitive load degradation model (ms vs baseline) |

---

## Application Pages

### Home
Cinematic landing page with driver showcase, race selector, Yas Marina SVG track map, and race statistics.

### Dashboard
Race overview with 4 metric cards, race timeline table with color-coded stress levels, dual-axis psychological trace chart, and IBM Granite analysis.

### Lap Dive
The most detailed page — lap-by-lap navigation with cognitive load bars, biometric sparklines, key events timeline, radio transcript terminal, zoomed chart, and sector breakdown.

### AI Chat
IBM Granite Intelligence conversational interface with Whisper voice input, pre-loaded conversation, suggested questions, and race context panel.

### Reports
Comprehensive psychological report with gauge chart, executive summary, key insight quote, events donut chart, P1 outcome display, and PDF export.

---

## Quick Start

### Prerequisites
- Python 3.10+
- IBM Cloud account with watsonx.ai access

### Installation

```bash
# Clone the repository
git clone https://github.com/ehvivek/VEGAIQ.git
cd VEGAIQ

# Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
```

### Configuration

Edit `.env` with your credentials:
```
IBM_API_KEY=your_ibm_cloud_api_key
IBM_PROJECT_ID=your_watsonx_project_id
OPENAI_API_KEY=your_openai_key  # optional for Whisper
```

### Run

```bash
streamlit run app.py
```

The app will launch at `http://localhost:8507` (or similar).

> **Note:** The app works without API keys using cached/fallback responses for all IBM Granite features. API keys enable live AI generation.

---

## Project Structure

```text
VEGAIQ/
├── app.py                      # Home page (landing)
├── pages/
│   ├── 1_Dashboard.py          # Race dashboard
│   ├── 2_Lap_Dive.py           # Lap deep dive
│   ├── 3_AI_Chat.py            # IBM Granite chat
│   └── 4_Reports.py            # Race reports + PDF
├── core/
│   ├── data_pipeline.py        # FastF1 + OpenF1 data fetching
│   ├── synthetic.py            # Biometric generation
│   ├── models.py               # 3 ML models (GBR + RF + Ridge)
│   ├── granite.py              # IBM Granite integration
│   ├── ibm_bob.py              # Conversation memory
│   ├── langflow.py             # Pipeline orchestration
│   └── whisper_service.py      # Voice transcription
├── utils/
│   ├── charts.py               # All Plotly chart functions
│   ├── styling.py              # CSS theme system
│   └── helpers.py              # Shared utilities
├── data/
│   └── langflow_workflow.json  # Langflow pipeline export
├── models/                     # Trained .pkl files (auto-generated)
├── .streamlit/config.toml      # Streamlit dark theme config
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Team

| Member |
|--------|
| [Vivek Kumar](https://github.com/ehvivek) |
| [Camila Paraguacuto](https://github.com/cparaguacuto02) |

---

## IBM SkillsBuild AI Builders Challenge — May 2026

This project was built for the **IBM SkillsBuild AI Builders Challenge**. It demonstrates:
- Real-world application of **IBM Granite 3.1** for domain-specific analysis
- Integration of multiple IBM tools (Granite + Bob + Langflow)
- Novel use case: F1 driver psychology analysis using publicly available data
- Professional-grade Streamlit UI with dark/light theme

---

## License

MIT License — see [LICENSE](LICENSE) for details.

<div align="center">
  <br>
  <b>VEGAIQ</b> · Powered by IBM Granite · Data: OpenF1 + FastF1<br>
  <i>"Understand the mind. Beyond the data."</i>
</div>
