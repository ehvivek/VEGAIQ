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

from utils.styling import inject_css, setup_sidebar, render_ibm_label, get_svg_icon, get_race_metadata
from utils.helpers import init_session_state, get_race_summary, load_chat_history, save_chat_history, DRIVERS
from core.ibm_bob import get_default_conversation
from core.data_pipeline import get_complete_driver_data

init_session_state()
inject_css()

driver_name = st.session_state.get("selected_driver", "Max Verstappen")
driver = DRIVERS.get(driver_name, DRIVERS["Max Verstappen"])
d_color = driver["color"]

with st.spinner(f"Connecting to {driver_name} telemetry..."):
    df = get_complete_driver_data(driver_name)
summary = get_race_summary(df)

# Session memory is isolated to this driver
if 'chat_driver' not in st.session_state or st.session_state.chat_driver != driver_name:
    st.session_state.messages = []
    st.session_state.chat_driver = driver_name

msg_key = f"messages_{st.session_state.selected_race}_{driver_name}"

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

    if st.button("Clear Chat History", use_container_width=True):
        st.session_state[msg_key] = get_default_conversation(st.session_state.selected_race)
        st.session_state.messages = st.session_state[msg_key]
        save_chat_history(msg_key, st.session_state.messages)
        st.rerun()

# ====== CHAT HEADER ======
st.markdown("""
<div style="height:0;overflow:visible;pointer-events:none;user-select:none;">
  <div style="position:relative;top:0;left:-0.5rem;
              font-family:'Rajdhani',sans-serif;font-weight:700;font-size:7rem;
              color:var(--text-primary);letter-spacing:0.12em;user-select:none;opacity:0.04;
              white-space:nowrap;pointer-events:none;line-height:1;">INTELLIGENCE</div>
</div>""", unsafe_allow_html=True)

sess_text = str(st.session_state.get("selected_session", "RACE")).upper()
st.markdown(f"""
<div style="padding-top:2.5rem;text-align:center;margin-bottom:0.5rem;">
  <div style="color:var(--text-primary);">{get_svg_icon("ibm", size=24, margin="0")}</div>
  <div style="font-family:'Rajdhani',sans-serif;font-size:1.6rem;font-weight:700;">IBM Granite Intelligence : {driver_name}</div>
  <div style="font-family:'Share Tech Mono',monospace;font-size:0.7rem;color:#888;
              display:flex;align-items:center;justify-content:center;gap:6px;margin-top:0.3rem;">
    <span style="width:6px;height:6px;background:{d_color};border-radius:50%;
                 display:inline-block;animation:pulse 2s infinite;"></span>
    {sess_text} Connected &middot; Analysing Telemetry Stream
  </div>
</div>""", unsafe_allow_html=True)

st.markdown(f'<div style="height:2px;background:linear-gradient(90deg,transparent,{d_color},transparent);margin:0.5rem 0 1rem;"></div>', unsafe_allow_html=True)

# ====== CHAT AREA ======
chat_col, info_col = st.columns([3, 1.2], gap="medium")

with chat_col:
    # Sync chat messages
    if msg_key not in st.session_state:
        loaded = load_chat_history(msg_key)
        if loaded:
            st.session_state[msg_key] = loaded
        else:
            st.session_state[msg_key] = get_default_conversation(st.session_state.selected_race)
    if not st.session_state.messages:
        st.session_state.messages = st.session_state[msg_key]

    messages_container = st.container()
    
    with messages_container:
        # Display existing messages
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Render audio input below the messages container
    audio_val = st.audio_input("Voice Input (Powered by Whisper)", key="audio_in")
    
    # Render chat input
    text_prompt = st.chat_input(f"Ask about {driver_name}'s psychology, stress, or performance...")
    
    prompt = None
    if text_prompt:
        prompt = text_prompt
    elif audio_val is not None:
        audio_size = len(audio_val.getvalue())
        if st.session_state.get("last_audio_size") != audio_size:
            st.session_state["last_audio_size"] = audio_size
            from core.whisper_service import transcribe_streamlit_audio
            with messages_container:
                with st.chat_message("assistant"):
                    with st.spinner("Whisper is transcribing..."):
                        res = transcribe_streamlit_audio(audio_val)
                        if res.get("text"):
                            prompt = res["text"]
                        elif res.get("error"):
                            st.error(f"Whisper Error: {res['error']}")

    if prompt:
        # Append user message and show immediately in the container
        st.session_state.messages.append({"role": "user", "content": prompt})
        with messages_container:
            with st.chat_message("user"):
                st.markdown(prompt)

            # Build response
            response = ""
            with st.chat_message("assistant"):
                with st.spinner("IBM Granite is analyzing..."):
                    try:
                        from core.granite import chat_with_driver_context
                        response = chat_with_driver_context(prompt, st.session_state.messages, driver_name)
                    except Exception as e:
                        print(f"Error calling Granite: {e}")

                    if not response:
                        response = "I'm having trouble analyzing the telemetry right now. Please try again."

                    st.markdown(response)
                    
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state[msg_key] = st.session_state.messages
        save_chat_history(msg_key, st.session_state.messages)

    st.markdown("""
<div style="font-family:'Share Tech Mono',monospace;font-size:0.55rem;
            color:#555;text-align:center;margin-top:2rem;margin-bottom:1rem;">
  Powered by IBM Granite 3.1 &middot; Assisted by IBM Bob &middot; Whisper Voice Recognition
</div>""", unsafe_allow_html=True)

with info_col:
    st.markdown(f'<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.65rem;'
                f'letter-spacing:0.15em;color:#888;margin:1rem 0 0.5rem;">SUGGESTED PROMPTS</div>',
                unsafe_allow_html=True)

    def handle_suggested_question(question):
        st.session_state.messages.append({"role": "user", "content": question})
        resp = ""
        try:
            from core.granite import chat_with_driver_context
            resp = chat_with_driver_context(question, st.session_state.messages, driver_name)
        except Exception:
            resp = "Analysis unavailable."
        st.session_state.messages.append({"role": "assistant", "content": resp})
        st.session_state[msg_key] = st.session_state.messages
        save_chat_history(msg_key, st.session_state.messages)

    suggested = [
        f"When did {driver_name} experience peak stress?",
        f"Did {driver_name}'s mental fatigue affect his lap times?",
        f"When did {driver_name} make his best decisions?",
    ]

    for i, q in enumerate(suggested):
        st.button(q, key=f"sq_{i}", use_container_width=True, on_click=handle_suggested_question, args=(q,))

    st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)

    # Race context
    meta = get_race_metadata(st.session_state.selected_race)
    st.markdown(f"""
<div style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:1rem;color:{d_color};
            margin-bottom:0.8rem;border-bottom:1px solid var(--border);padding-bottom:0.5rem;">
    {driver_name.upper()} ({driver['team']})
</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:0.9rem;color:var(--text-muted);line-height:2;">
    <div>{get_svg_icon("timer")} Avg Quality &middot; {summary.get('avg_quality', 'N/A')}/10</div>
    <div>{get_svg_icon("brain")} Peak Stress &middot; {summary.get('peak_stress', 'N/A')}/10 (Lap {summary.get('peak_lap', 'N/A')})</div>
</div>""", unsafe_allow_html=True)

# ====== FOOTER ======
st.markdown(f'<div style="height:2px;background:linear-gradient(90deg,{d_color},transparent);margin:1.5rem 0 0.5rem;"></div>', unsafe_allow_html=True)
render_ibm_label("IBM GRANITE 3.1 &middot; IBM BOB &middot; WHISPER &middot; OpenF1 + FastF1")
