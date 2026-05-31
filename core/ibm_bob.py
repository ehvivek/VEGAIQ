"""
core/ibm_bob.py
PitMind — IBM Bob conversational memory layer.

NOTE: IBM Bob is a developer IDE tool (not a public chat API).
This module implements a ConversationMemory class that:
1. Maintains multi-turn conversation history
2. Injects full race context into every Granite call
3. Is branded as "IBM Bob assisted" in the UI (Bob was used to develop this project)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime


@dataclass
class Message:
    role: str          # "user" or "assistant"
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))


class ConversationMemory:
    """
    Manages multi-turn conversation history with full race context injection.
    IBM Bob was used as the AI development assistant to build PitMind.
    This class simulates Bob's contextual memory model for the chat interface.
    """

    def __init__(self, race_context: Dict[str, Any] = None):
        self.messages: List[Message] = []
        self.race_context: Dict[str, Any] = race_context or {}
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._init_system_knowledge()

    def _init_system_knowledge(self):
        """Pre-load race knowledge into conversation context."""
        self.race_knowledge = {
            "race": "Abu Dhabi GP 2024",
            "driver": "Max Verstappen (VER)",
            "team": "Red Bull Racing",
            "result": "P6",
            "win_margin": "+38.457s",
            "total_laps": 58,
            "peak_stress_lap": 47,
            "peak_stress_score": 9.1,
            "critical_events": ["Safety Car Lap 45-49", "Yellow Flag Lap 44 & 47"],
            "tyre_strategy": "HARD (1-20) → MEDIUM (21-38) → SOFT (39-58)",
            "radio_count": 14,
            "avg_stress": 5.8,
            "avg_quality": 6.4,
            "avg_fatigue": 5.8,
            "overall_psych_score": 7.6,
        }

    def add_user_message(self, content: str):
        """Add a user message to history."""
        self.messages.append(Message(role="user", content=content))

    def add_assistant_message(self, content: str):
        """Add an assistant message to history."""
        self.messages.append(Message(role="assistant", content=content))

    def get_history(self) -> List[Dict]:
        """Return conversation history as list of dicts for Granite."""
        return [{"role": m.role, "content": m.content} for m in self.messages]

    def get_context_dict(self) -> Dict[str, Any]:
        """Return race context for injection into Granite prompts."""
        return {
            **self.race_knowledge,
            **self.race_context,
            "conversation_turns": len(self.messages),
        }

    def clear(self):
        """Reset conversation history."""
        self.messages = []

    def get_summary(self) -> str:
        """Get a text summary of the conversation so far."""
        if not self.messages:
            return "No conversation yet."
        topics = []
        for m in self.messages:
            if m.role == "user" and len(m.content) > 10:
                topics.append(m.content[:50])
        return f"Session {self.session_id} — {len(self.messages)} messages covering: {', '.join(topics[:3])}"

    def to_dict(self) -> Dict:
        """Serialize conversation for storage."""
        return {
            "session_id": self.session_id,
            "messages": [{"role": m.role, "content": m.content, "ts": m.timestamp}
                         for m in self.messages],
            "race_context": self.race_context,
        }


# ─────────────────────────────────────────────
# Pre-loaded conversation starters
# ─────────────────────────────────────────────

DEFAULT_CONVERSATION = [
    {
        "role": "assistant",
        "content": (
            "Hello! I'm IBM Granite Intelligence, powered by IBM Granite 3.1 and assisted by IBM Bob. "
            "I can analyse Max Verstappen's psychological states, stress patterns, decision quality, "
            "and more from the Abu Dhabi GP 2024. What would you like to know?"
        ),
    },
    {
        "role": "user",
        "content": "When was Verstappen most stressed?",
    },
    {
        "role": "assistant",
        "content": (
            "Verstappen's peak stress occurred on Lap 47, with a stress score of 9.1 out of 10. "
            "This coincided with the Safety Car deployment on Lap 45 and a severe tyre degradation phase "
            "on 18-lap-old Soft compounds. IBM Granite analysis identifies this as the race's defining "
            "psychological crisis — a multi-factor cognitive overload event."
        ),
    },
    {
        "role": "user",
        "content": "Did pressure affect his lap times?",
    },
    {
        "role": "assistant",
        "content": (
            "Yes. Between Laps 45-50, Verstappen's average lap time dropped by 0.812s compared to his "
            "race baseline. The Safety Car restart on cold Soft tyres compounded psychological stress, "
            "degrading decision quality from 6.8 to 5.2/10. IBM Granite correlates this directly with "
            "a mental fatigue spike reaching 7.4/10 — high enough to measurably impact fine motor control."
        ),
    },
    {
        "role": "user",
        "content": "What caused the breakdown at lap 47?",
    },
    {
        "role": "assistant",
        "content": (
            "Three converging factors created cognitive overload: (1) Safety Car deployment disrupting "
            "tyre temperature management at a critical stint phase, (2) cold-tyre restart with Norris "
            "closing rapidly in P2, and (3) championship-level internal pressure amplifying stakes. "
            "IBM Granite's Lap 47 analysis shows decision quality hit its race minimum of 5.2/10, "
            "accompanied by estimated erratic eye tracking and a heart rate peak of 167 BPM. "
            "Verstappen's own radio — 'These tyres are completely gone' — confirms the acute awareness "
            "of his compromised situation."
        ),
    },
]


def get_default_conversation(race_name: str = "Abu Dhabi GP 2024") -> List[Dict]:
    """Return the pre-loaded conversation for initial chat display adjusted for the race."""
    name = str(race_name).lower()
    if "monaco" in name:
        return [
            {
                "role": "assistant",
                "content": (
                    "Hello! I'm IBM Granite Intelligence, powered by IBM Granite 3.1 and assisted by IBM Bob. "
                    "I can analyse Max Verstappen's psychological states, stress patterns, decision quality, "
                    "and more from the Monaco GP 2024. What would you like to know?"
                ),
            },
            {
                "role": "user",
                "content": "When was Verstappen most stressed?",
            },
            {
                "role": "assistant",
                "content": (
                    "Verstappen's peak stress in Monaco occurred on Lap 67, reaching 9.6 out of 10. "
                    "This was triggered by the Safety Car deployment on the tight, unforgiving street track, "
                    "requiring extreme concentration under intense pressure. IBM Granite analysis identifies this "
                    "as the race's defining psychological crisis."
                ),
            },
            {
                "role": "user",
                "content": "How did the Monaco track layout affect his cognitive fatigue?",
            },
            {
                "role": "assistant",
                "content": (
                    "Monaco's tight street layout created a higher baseline fatigue rate (avg 6.2/10) compared to Abu Dhabi. "
                    "The continuous high-downforce demand and zero-margin-for-error corners meant Verstappen's mental fatigue "
                    "scaled upward by 0.35 points per lap, culminating in high cognitive load by stint end."
                ),
            },
        ]
    elif "bahrain" in name:
        return [
            {
                "role": "assistant",
                "content": (
                    "Hello! I'm IBM Granite Intelligence, powered by IBM Granite 3.1 and assisted by IBM Bob. "
                    "I can analyse Max Verstappen's psychological states, stress patterns, decision quality, "
                    "and more from the Bahrain GP 2024. What would you like to know?"
                ),
            },
            {
                "role": "user",
                "content": "When was Verstappen most stressed?",
            },
            {
                "role": "assistant",
                "content": (
                    "Verstappen's peak stress in Bahrain occurred on Lap 1 during the chaotic start sequence, "
                    "reaching 8.7 out of 10. Thermal tyre degradation concerns and hot temperatures amplified "
                    "strategic anxiety, which stabilized once he cleared the field. IBM Granite identifies this "
                    "as a typical high-stakes launch phase stressor."
                ),
            },
            {
                "role": "user",
                "content": "What was the main psychological challenge in Bahrain?",
            },
            {
                "role": "assistant",
                "content": (
                    "The primary psychological challenge was thermal tyre management. Verstappen had to consciously "
                    "repress his instinct to push aggressively to manage the high-degradation Soft-to-Hard tire stints. "
                    "IBM Granite analysis highlights his average decision quality remained high at 7.6/10 despite "
                    "elevated ambient heat."
                ),
            },
        ]
    else:
        return DEFAULT_CONVERSATION.copy()

