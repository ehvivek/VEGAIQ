"""
pages/3_AI_Chat.py -- PitMind AI Chat with IBM Granite
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

st.set_page_config(
    page_title="PitMind | AI Chat",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.styling import inject_css, setup_sidebar, render_ibm_label, get_svg_icon
from utils.helpers import init_session_state, get_race_data, get_race_summary
from utils.styling import get_race_metadata
from core.ibm_bob import get_default_conversation

init_session_state()
inject_css()

with st.spinner("Loading race context..."):
    df = get_race_data(st.session_state.selected_race)
summary = get_race_summary(df)

# -- Sidebar --
with st.sidebar:
    setup_sidebar()
    st.markdown("---")
    # IBM Granite info
    st.markdown("""
<div style="background:var(--bg-card);border:1px solid var(--border);border-radius:8px;padding:0.8rem;">
  <div style="display:flex;align-items:center;gap:6px;margin-bottom:0.5rem;">
    <span style="font-family:'Share Tech Mono',monospace;font-size:0.5rem;
                 color:#4A9EFF;background:var(--bg-secondary);padding:2px 6px;border-radius:3px;
                 border:1px solid var(--border);">IBM</span>
    <span style="font-family:'Rajdhani',sans-serif;font-size:0.85rem;font-weight:600;">Granite Intelligence</span>
  </div>
  <div style="font-family:'Share Tech Mono',monospace;font-size:0.6rem;color:var(--text-muted);line-height:2;">
    <div>MODEL: IBM Granite 3.1</div>
    <div>SPEC: F1 Psychology</div>
    <div>DATA: OpenF1 + FastF1</div>
  </div>
</div>""", unsafe_allow_html=True)

    # Voice input in sidebar
    st.markdown("---")
    st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.6rem;'
                'letter-spacing:0.12em;color:#888;margin-bottom:0.3rem;">🎤 VOICE INPUT</div>',
                unsafe_allow_html=True)
    audio_val = st.audio_input("Record your question", key="audio_in", label_visibility="collapsed")
    if audio_val is not None:
        audio_size = len(audio_val.getvalue())
        if st.session_state.get("last_audio_size") != audio_size:
            st.session_state["last_audio_size"] = audio_size
            from core.whisper_service import transcribe_streamlit_audio
            with st.spinner("Transcribing..."):
                res = transcribe_streamlit_audio(audio_val)
                if res.get("text"):
                    st.session_state["voice_prompt"] = res["text"]
                    st.success(f'"{res["text"]}"')
                    st.rerun()
                elif res.get("error"):
                    st.error(f"Error: {res['error']}")

# ====== CHAT HEADER ======
st.markdown("""
<div style="height:0;overflow:visible;pointer-events:none;user-select:none;">
  <div style="position:relative;top:0;left:-0.5rem;
              font-family:'Rajdhani',sans-serif;font-weight:700;font-size:7rem;
              color:var(--text-primary);letter-spacing:0.12em;user-select:none;opacity:0.04;
              white-space:nowrap;pointer-events:none;line-height:1;">INTELLIGENCE</div>
</div>""", unsafe_allow_html=True)

st.markdown(f"""
<div style="padding-top:2.5rem;text-align:center;margin-bottom:0.5rem;">
  <div style="color:var(--text-primary);">{get_svg_icon("ibm", size=24, margin="0")}</div>
  <div style="font-family:'Rajdhani',sans-serif;font-size:1.6rem;font-weight:700;">IBM Granite Intelligence</div>
  <div style="font-family:'Share Tech Mono',monospace;font-size:0.7rem;color:#888;
              display:flex;align-items:center;justify-content:center;gap:6px;margin-top:0.3rem;">
    <span style="width:6px;height:6px;background:#00C853;border-radius:50%;
                 display:inline-block;animation:pulse 2s infinite;"></span>
    Session Connected &middot; Analysing Telemetry Stream
  </div>
</div>""", unsafe_allow_html=True)

st.markdown('<div style="height:2px;background:linear-gradient(90deg,transparent,#E8002D,transparent);margin:0.5rem 0 1rem;"></div>', unsafe_allow_html=True)

# ====== CHAT AREA ======
chat_col, info_col = st.columns([3, 1.2], gap="medium")

with chat_col:
    # Sync chat messages with active selected race
    msg_key = f"messages_{st.session_state.selected_race}"
    if msg_key not in st.session_state:
        st.session_state[msg_key] = get_default_conversation(st.session_state.selected_race)
    st.session_state.messages = st.session_state[msg_key]

    # ── Process voice input first (before rendering messages) ──
    prompt = None

    # Check for pending voice transcription from sidebar
    if st.session_state.get("voice_prompt"):
        prompt = st.session_state.pop("voice_prompt")

    # ── Display all messages in a container ──
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # ── Text input (Streamlit pins this to the bottom automatically) ──
    text_prompt = st.chat_input("Ask about the race, driver psychology, or performance...")
    if text_prompt:
        prompt = text_prompt

    # ── Handle prompt (from text or voice) ──
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)

        # Build response — try IBM Granite API first, fall back to smart answers
        response = ""
        try:
            from core.granite import chat_response
            response = chat_response(prompt, st.session_state.messages, context=summary)
        except Exception:
            pass

        if not response:
            from core.granite import CACHED_CHAT
            msg_lower = prompt.lower()
            response = CACHED_CHAT["default"]
            for kw, cached in CACHED_CHAT.items():
                if kw != "default" and kw in msg_lower:
                    response = cached
                    break

        with chat_container:
            with st.chat_message("assistant"):
                st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})

    st.markdown("""
<div style="font-family:'Share Tech Mono',monospace;font-size:0.55rem;
            color:#555;text-align:center;margin-top:0.5rem;">
  Powered by IBM Granite 3.1 &middot; Assisted by IBM Bob &middot; Voice Recognition
</div>""", unsafe_allow_html=True)

with info_col:
    st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.6rem;'
                'letter-spacing:0.15em;color:#888;margin-bottom:0.5rem;">SUGGESTED QUESTIONS</div>',
                unsafe_allow_html=True)

    def handle_suggested_question(question):
        st.session_state.messages.append({"role": "user", "content": question})
        resp = ""
        try:
            from core.granite import chat_response
            resp = chat_response(question, st.session_state.messages, context=summary)
        except Exception:
            pass
        if not resp:
            from core.granite import CACHED_CHAT
            q_lower = question.lower()
            resp = CACHED_CHAT["default"]
            for kw, cached in CACHED_CHAT.items():
                if kw != "default" and kw in q_lower:
                    resp = cached
                    break
        st.session_state.messages.append({"role": "assistant", "content": resp})

    questions = [
        "How did the Safety Car impact his mindset?",
        "What was his confidence trend during the race?",
        "Compare his stress levels across all laps",
        "When did Verstappen make his best decisions?",
        "How did tyre degradation affect his psychology?",
    ]

    for i, q in enumerate(questions):
        st.button(q, key=f"sq_{i}", use_container_width=True, on_click=handle_suggested_question, args=(q,))

    st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)

    # Race context
    meta = get_race_metadata(st.session_state.selected_race)
    st.markdown(f"""
<div style="background:var(--bg-card);border:1px solid var(--border);border-radius:8px;padding:0.8rem 1rem;">
  <div style="font-family:'Share Tech Mono',monospace;font-size:0.6rem;
              letter-spacing:0.12em;color:var(--text-muted);margin-bottom:0.4rem;">RACE CONTEXT</div>
  <div style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;color:var(--text-muted);line-height:2;">
    <div>{meta['flag_entity']} {st.session_state.selected_race}</div>
    <div>{get_svg_icon("car")} Verstappen &middot; P1 &middot; {meta['margin']}</div>
    <div>{get_svg_icon("trending")} Peak Stress: {summary['peak_stress']}/10 (L{summary['peak_lap']})</div>
    <div>{get_svg_icon("brain")} Avg Quality: {summary['avg_quality']}/10</div>
    <div>{get_svg_icon("headset")} Radio Events: {summary['total_radio']}</div>
  </div>
</div>""", unsafe_allow_html=True)

# ====== FOOTER ======
st.markdown('<div style="height:2px;background:linear-gradient(90deg,#E8002D,transparent);margin:1.5rem 0 0.5rem;"></div>', unsafe_allow_html=True)
render_ibm_label("IBM GRANITE 3.1 &middot; IBM BOB &middot; WHISPER &middot; OpenF1 + FastF1")
