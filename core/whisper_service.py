"""
core/whisper_service.py
PitMind — OpenAI Whisper audio transcription service.
Handles microphone audio input → text transcript for the AI chat page.
"""

import os
import io
import tempfile
import numpy as np
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

_whisper_model = None


def _load_whisper(model_size: str = "base"):
    """Lazy-load Whisper model (downloads ~140MB on first use)."""
    global _whisper_model
    if _whisper_model is None:
        try:
            import whisper
            import os
            import certifi
            
            # macOS Python SSL certificate fix for urllib/torch
            os.environ['SSL_CERT_FILE'] = certifi.where()

            print(f"[Whisper] Loading '{model_size}' model...")
            _whisper_model = whisper.load_model(model_size)
            print("[Whisper] Model ready.")
        except ImportError:
            print("[Whisper] openai-whisper not installed. Voice input disabled.")
            _whisper_model = None
    return _whisper_model


def transcribe_audio_bytes(audio_bytes: bytes, model_size: str = "base") -> dict:
    """
    Transcribe audio bytes (WAV/MP3/etc.) using Whisper.

    Args:
        audio_bytes: Raw audio data as bytes
        model_size: Whisper model size ('tiny', 'base', 'small', 'medium')

    Returns:
        dict with 'text', 'language', 'confidence'
    """
    model = _load_whisper(model_size)
    if model is None:
        return {"text": "", "language": "en", "confidence": 0.0, "error": "Whisper not available"}

    try:
        # Write to temp file (Whisper needs a file path)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        result = model.transcribe(tmp_path, language="en", fp16=False)
        os.unlink(tmp_path)  # cleanup

        text = result.get("text", "").strip()
        language = result.get("language", "en")

        # Estimate confidence from log probability
        segments = result.get("segments", [])
        if segments:
            avg_logprob = np.mean([s.get("avg_logprob", -1.0) for s in segments])
            confidence = round(float(np.clip(np.exp(avg_logprob), 0, 1)), 3)
        else:
            confidence = 0.5

        return {"text": text, "language": language, "confidence": confidence}

    except Exception as e:
        print(f"[Whisper] Transcription error: {e}")
        return {"text": "", "language": "en", "confidence": 0.0, "error": str(e)}


def transcribe_streamlit_audio(audio_value) -> dict:
    """
    Handle audio from Streamlit's st.audio_input() widget.
    audio_value is a BytesIO object from the Streamlit audio recorder.
    """
    if audio_value is None:
        return {"text": "", "language": "en", "confidence": 0.0}

    try:
        audio_bytes = audio_value.read() if hasattr(audio_value, "read") else bytes(audio_value)
        return transcribe_audio_bytes(audio_bytes)
    except Exception as e:
        print(f"[Whisper] Streamlit audio error: {e}")
        return {"text": "", "language": "en", "confidence": 0.0, "error": str(e)}


# ─────────────────────────────────────────────
# Text-to-Speech output
# ─────────────────────────────────────────────

def speak_text(text: str, rate: int = 160, volume: float = 0.9):
    """
    Convert text to speech using pyttsx3 (offline TTS).
    Runs in a separate thread to avoid blocking Streamlit.
    """
    import threading

    def _speak():
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty("rate", rate)
            engine.setProperty("volume", volume)
            # Prefer a female voice if available
            voices = engine.getProperty("voices")
            for v in voices:
                if "female" in v.name.lower() or "zira" in v.name.lower() or "karen" in v.name.lower():
                    engine.setProperty("voice", v.id)
                    break
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"[TTS] pyttsx3 error: {e}")

    thread = threading.Thread(target=_speak, daemon=True)
    thread.start()


def is_whisper_available() -> bool:
    """Check if Whisper is installed and loadable."""
    try:
        import whisper
        return True
    except ImportError:
        return False


def is_tts_available() -> bool:
    """Check if pyttsx3 TTS is available."""
    try:
        import pyttsx3
        return True
    except ImportError:
        return False
