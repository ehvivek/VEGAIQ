"""
core/rag_engine.py
PitMind — Retrieval Augmented Generation (RAG) Engine.

Provides real-time factual grounding for IBM Granite responses by fetching
verified data from multiple sources before every LLM call.

Sources:
  1. Ergast F1 API (api.jolpi.ca) — Official FIA race results & standings
  2. Wikipedia — Historical race context & summaries
  3. DuckDuckGo (ddgs) — General web search fallback
  4. Local DataFrame — Our own telemetry, stress, radio data
"""

import os
import requests
import pandas as pd

# SSL certificate fix for macOS Python
try:
    import certifi
    os.environ.setdefault("SSL_CERT_FILE", certifi.where())
except ImportError:
    pass

ERGAST_BASE = "https://api.jolpi.ca/ergast/f1"

# ─────────────────────────────────────────────
# 1. Ergast F1 API — Official Race Results
# ─────────────────────────────────────────────

def fetch_ergast_results(year: int = 2024, round_num: int = 24) -> str:
    """Fetch official FIA race results from the Ergast API mirror."""
    try:
        url = f"{ERGAST_BASE}/{year}/{round_num}/results.json"
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        data = r.json()

        races = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
        if not races:
            return ""

        race = races[0]
        race_name = race.get("raceName", "Unknown GP")
        results = race.get("Results", [])

        lines = [f"\n=== OFFICIAL FIA RACE RESULTS: {race_name} {year} ==="]
        for res in results[:10]:  # top 10
            pos = res.get("position", "?")
            driver = res["Driver"]
            name = f"{driver.get('givenName', '')} {driver.get('familyName', '')}"
            team = res.get("Constructor", {}).get("name", "")
            time_info = ""
            if "Time" in res:
                time_info = res["Time"].get("time", "")
            elif res.get("status", "") != "Finished":
                time_info = res.get("status", "")
            grid = res.get("grid", "?")
            lines.append(f"  P{pos}: {name} ({team}) — {time_info} [Grid: {grid}]")

        lines.append("=== END OFFICIAL RESULTS ===\n")
        return "\n".join(lines)
    except Exception as e:
        print(f"[RAG/Ergast Results] Error: {e}")
        return ""


def fetch_ergast_standings(year: int = 2024) -> str:
    """Fetch driver championship standings from the Ergast API mirror."""
    try:
        url = f"{ERGAST_BASE}/{year}/driverStandings.json"
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        data = r.json()

        standings_lists = data.get("MRData", {}).get("StandingsTable", {}).get("StandingsLists", [])
        if not standings_lists:
            return ""

        standings = standings_lists[0].get("DriverStandings", [])
        lines = [f"\n=== {year} DRIVERS' CHAMPIONSHIP STANDINGS ==="]
        for s in standings[:10]:
            pos = s.get("position", "?")
            driver = s["Driver"]
            name = f"{driver.get('givenName', '')} {driver.get('familyName', '')}"
            points = s.get("points", "0")
            wins = s.get("wins", "0")
            team = s.get("Constructors", [{}])[0].get("name", "") if s.get("Constructors") else ""
            lines.append(f"  P{pos}: {name} ({team}) — {points} pts, {wins} wins")

        lines.append("=== END STANDINGS ===\n")
        return "\n".join(lines)
    except Exception as e:
        print(f"[RAG/Ergast Standings] Error: {e}")
        return ""


def fetch_ergast_constructor_standings(year: int = 2024) -> str:
    """Fetch constructor championship standings from the Ergast API mirror."""
    try:
        url = f"{ERGAST_BASE}/{year}/constructorStandings.json"
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        data = r.json()

        standings_lists = data.get("MRData", {}).get("StandingsTable", {}).get("StandingsLists", [])
        if not standings_lists:
            return ""

        standings = standings_lists[0].get("ConstructorStandings", [])
        lines = [f"\n=== {year} CONSTRUCTORS' CHAMPIONSHIP STANDINGS ==="]
        for s in standings[:10]:
            pos = s.get("position", "?")
            name = s.get("Constructor", {}).get("name", "")
            points = s.get("points", "0")
            wins = s.get("wins", "0")
            lines.append(f"  P{pos}: {name} — {points} pts, {wins} wins")

        lines.append("=== END CONSTRUCTOR STANDINGS ===\n")
        return "\n".join(lines)
    except Exception as e:
        print(f"[RAG/Ergast Constructors] Error: {e}")
        return ""


# ─────────────────────────────────────────────
# 2. Wikipedia — Historical Context
# ─────────────────────────────────────────────

def fetch_wikipedia_context(query: str) -> str:
    """Fetch a Wikipedia summary for F1 historical context."""
    try:
        import wikipedia
        summary = wikipedia.summary(query, sentences=5)
        return f"\n=== WIKIPEDIA CONTEXT ===\n{summary}\n=== END WIKIPEDIA ===\n"
    except Exception as e:
        print(f"[RAG/Wikipedia] Error: {e}")
        return ""


# ─────────────────────────────────────────────
# 3. DuckDuckGo — Web Search Fallback
# ─────────────────────────────────────────────

def fetch_web_search(query: str) -> str:
    """Perform a web search using the ddgs package."""
    try:
        from ddgs import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
        if not results:
            return ""
        lines = ["\n=== WEB SEARCH RESULTS ==="]
        for r in results:
            lines.append(f"  - {r.get('title', '')}: {r.get('body', '')}")
        lines.append("=== END WEB SEARCH ===\n")
        return "\n".join(lines)
    except Exception as e:
        print(f"[RAG/WebSearch] Error: {e}")
        return ""


# ─────────────────────────────────────────────
# 4. Local Race DataFrame — Telemetry
# ─────────────────────────────────────────────

def fetch_local_race_context(df: pd.DataFrame = None, summary: dict = None) -> str:
    """Extract key telemetry statistics from our loaded race data."""
    lines = ["\n=== LOCAL TELEMETRY DATA ==="]

    if summary:
        lines.append(f"  Average Stress Index: {summary.get('avg_stress', 'N/A')}/10")
        lines.append(f"  Peak Stress: {summary.get('peak_stress', 'N/A')}/10 on Lap {summary.get('peak_lap', 'N/A')}")
        lines.append(f"  Average Decision Quality: {summary.get('avg_quality', 'N/A')}/10")
        lines.append(f"  Average Mental Fatigue: {summary.get('avg_fatigue', 'N/A')}/10")
        lines.append(f"  Total Radio Transmissions: {summary.get('total_radio', 'N/A')}")
        lines.append(f"  Overall Psychological Score: {summary.get('overall_score', 'N/A')}/10")
        lines.append(f"  Total Laps: {summary.get('total_laps', 'N/A')}")

    if df is not None and not df.empty:
        # Find the laps with highest stress
        top_stress = df.nlargest(3, "stress_index")[["lap", "stress_index", "radio_text"]].to_dict("records")
        lines.append("  Top 3 Stress Laps:")
        for row in top_stress:
            radio = row.get("radio_text", "No transmission.")
            if radio == "No transmission.":
                radio = "(no radio)"
            else:
                radio = f'Radio: "{radio[:80]}"'
            lines.append(f"    Lap {row['lap']}: Stress {row['stress_index']}/10 — {radio}")

        # Find the laps with lowest decision quality
        low_quality = df.nsmallest(3, "decision_quality")[["lap", "decision_quality"]].to_dict("records")
        lines.append("  Lowest Decision Quality Laps:")
        for row in low_quality:
            lines.append(f"    Lap {row['lap']}: Quality {row['decision_quality']}/10")

    lines.append("=== END TELEMETRY ===\n")
    return "\n".join(lines)


# ─────────────────────────────────────────────
# Smart Router — Combines All Sources
# ─────────────────────────────────────────────

# Keywords that trigger specific data sources
RESULT_KEYWORDS = [
    "won", "winner", "win", "result", "gap", "position", "standing",
    "champion", "podium", "finished", "margin", "first", "second", "third",
    "p1", "p2", "p3", "p4", "p5", "p6", "norris", "sainz", "leclerc",
    "hamilton", "russell", "who came", "who won", "race result",
]

RACE_KEYWORDS = [
    "race", "grand prix", "gp", "abu dhabi", "monaco", "bahrain",
    "silverstone", "monza", "spa", "suzuka", "jeddah", "melbourne",
    "imola", "barcelona", "montreal", "zandvoort", "singapore", "austin",
    "mexico", "brazil", "las vegas", "qatar", "japan", "china", "miami",
]

STANDINGS_KEYWORDS = [
    "standing", "championship", "champion", "points", "title",
    "constructor", "team standing", "wdc", "wcc",
]


def _detect_race_round(question: str) -> tuple:
    """Detect which race the user is asking about. Returns (year, round_num)."""
    q = question.lower()
    # Map known race names to round numbers for 2024 season
    race_rounds_2024 = {
        "bahrain": 1, "saudi": 2, "jeddah": 2, "australia": 3, "melbourne": 3,
        "japan": 4, "suzuka": 4, "china": 5, "shanghai": 5, "miami": 6,
        "emilia": 7, "imola": 7, "monaco": 8, "canada": 9, "montreal": 9,
        "spain": 10, "barcelona": 10, "austria": 11, "spielberg": 11,
        "british": 12, "silverstone": 12, "hungary": 13, "budapest": 13,
        "belgium": 14, "spa": 14, "dutch": 15, "zandvoort": 15,
        "italy": 16, "monza": 16, "azerbaijan": 17, "baku": 17,
        "singapore": 18, "austin": 19, "usa": 19, "cota": 19,
        "mexico": 20, "brazil": 21, "sao paulo": 21, "interlagos": 21,
        "las vegas": 22, "qatar": 23, "losail": 23,
        "abu dhabi": 24, "yas marina": 24,
    }
    for name, rnd in race_rounds_2024.items():
        if name in q:
            return (2024, rnd)
    return (2024, 24)  # default to Abu Dhabi


def smart_context(question: str, df: pd.DataFrame = None, summary: dict = None) -> str:
    """
    Intelligent RAG router — fetches verified data from multiple sources
    based on the user's question content.

    Always injects local telemetry. Conditionally adds Ergast results,
    Wikipedia context, and web search based on keyword detection.
    """
    context_parts = []
    q = question.lower()

    # 1. ALWAYS inject local telemetry data
    context_parts.append(fetch_local_race_context(df, summary))

    # 2. If asking about race results, positions, gaps, winners
    if any(kw in q for kw in RESULT_KEYWORDS):
        year, rnd = _detect_race_round(question)
        context_parts.append(fetch_ergast_results(year, rnd))

    # 3. If asking about championship standings
    if any(kw in q for kw in STANDINGS_KEYWORDS):
        context_parts.append(fetch_ergast_standings(2024))
        context_parts.append(fetch_ergast_constructor_standings(2024))

    # 4. If asking about a specific race or GP — pull Wikipedia summary
    if any(kw in q for kw in RACE_KEYWORDS):
        year, rnd = _detect_race_round(question)
        wiki_query = question  # Use the user's question directly
        # Try to make the query more specific for Wikipedia
        for name in ["abu dhabi", "monaco", "bahrain", "silverstone", "monza"]:
            if name in q:
                wiki_query = f"2024 {name.title()} Grand Prix"
                break
        context_parts.append(fetch_wikipedia_context(wiki_query))

    # 5. ALWAYS perform a web search as safety net
    context_parts.append(fetch_web_search(question))

    combined = "\n".join([p for p in context_parts if p])

    if combined.strip():
        return (
            "\n╔══════════════════════════════════════════════╗\n"
            "║  VERIFIED DATA (Trust this over your training)  ║\n"
            "╚══════════════════════════════════════════════╝\n"
            f"{combined}"
        )
    return ""
