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

# ====== TABS AREA ======
tab_telemetry, tab_docling = st.tabs([
    "📊 TELEMETRY PSYCH CHAT",
    "📄 F1 DOCUMENT INTELLIGENCE"
])

with tab_telemetry:
    chat_col, info_col = st.columns([3, 1.2], gap="medium")

    with chat_col:
        # Sync chat messages with active selected race
        msg_key = f"messages_{st.session_state.selected_race}"
        if msg_key not in st.session_state:
            st.session_state[msg_key] = get_default_conversation(st.session_state.selected_race)
        st.session_state.messages = st.session_state[msg_key]

        # Display messages
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Inputs
        text_prompt = st.chat_input("Ask about the race, driver psychology, or performance...")
        audio_val = st.audio_input("Voice Input (Powered by Whisper)", key="audio_in")
        
        prompt = None
        if text_prompt:
            prompt = text_prompt
        elif audio_val is not None:
            audio_size = len(audio_val.getvalue())
            if st.session_state.get("last_audio_size") != audio_size:
                st.session_state["last_audio_size"] = audio_size
                from core.whisper_service import transcribe_streamlit_audio
                with st.spinner("Whisper is transcribing..."):
                    res = transcribe_streamlit_audio(audio_val)
                    if res.get("text"):
                        prompt = res["text"]
                    elif res.get("error"):
                        st.error(f"Whisper Error: {res['error']}")

        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Build response using IBM Granite (with built-in smart fallback)
            response = ""
            try:
                from core.granite import chat_response
                response = chat_response(prompt, st.session_state.messages, context=summary)
            except Exception as e:
                print(f"[AI Chat] chat_response error: {e}")
                # Last-resort fallback
                response = (
                    f"I'm currently processing your question about the {st.session_state.selected_race}. "
                    f"Please try asking about specific laps, stress patterns, tyre strategy, or "
                    f"Verstappen's psychological performance. Powered by IBM Granite."
                )

            with st.chat_message("assistant"):
                st.markdown(response)

            st.session_state.messages.append({"role": "assistant", "content": response})

        st.markdown("""
    <div style="font-family:'Share Tech Mono',monospace;font-size:0.55rem;
                color:#555;text-align:center;margin-top:0.5rem;">
      Powered by IBM Granite 3.1 &middot; Assisted by IBM Bob &middot; Whisper Voice Recognition
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
            except Exception as e:
                print(f"[AI Chat] suggested question error: {e}")
                resp = f"Analysis in progress for: '{question}'. Powered by IBM Granite."
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

with tab_docling:
    from core.docling_service import has_docling, parse_document

    st.markdown("""
    <div style="background:var(--bg-card);border:1px solid var(--border);border-radius:12px;padding:1.2rem;margin-bottom:1rem;">
      <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
        <div>
          <span class="pm-badge pm-badge-red" style="font-size:0.55rem;padding:3px 8px;">IBM DOCLING PIPELINE</span>
          <h3 style="font-family:'Rajdhani',sans-serif;margin:0.3rem 0 0.1rem;font-size:1.5rem;font-weight:700;">F1 RAG & Document Intelligence</h3>
          <p style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;color:var(--text-muted);margin:0;">
            Upload F1 Sporting Regulations, stewards' sheets, or strategy PDFs to parse with IBM Docling and ground IBM Granite 3.1.
          </p>
        </div>
        <div style="text-align:right;">
    """, unsafe_allow_html=True)

    # Engine status badge
    if has_docling():
        st.markdown("""
          <div style="background:rgba(0,200,83,0.06);border:1px solid #00C853;border-radius:6px;padding:6px 12px;display:inline-block;text-align:center;">
            <div style="font-family:'Share Tech Mono',monospace;font-size:0.5rem;color:#00C853;font-weight:bold;">ENGINE STATUS</div>
            <div style="font-family:'Rajdhani',sans-serif;font-size:0.75rem;font-weight:700;color:#00C853;">IBM DOCLING NATIVE ACTIVE</div>
          </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
          <div style="background:rgba(74,158,255,0.06);border:1px solid #4A9EFF;border-radius:6px;padding:6px 12px;display:inline-block;text-align:center;">
            <div style="font-family:'Share Tech Mono',monospace;font-size:0.5rem;color:#4A9EFF;font-weight:bold;">ENGINE STATUS</div>
            <div style="font-family:'Rajdhani',sans-serif;font-size:0.75rem;font-weight:700;color:#4A9EFF;">IBM DOCLING STANDARD MODE</div>
          </div>
        """, unsafe_allow_html=True)

    st.markdown("</div></div></div>", unsafe_allow_html=True)

    # Two column layout
    doc_viewer_col, doc_chat_col = st.columns([1.8, 2.2], gap="large")

    with doc_viewer_col:
        st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.6rem;letter-spacing:0.15em;color:#888;margin-bottom:0.5rem;">1. UPLOAD & PARSE DOCUMENT</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Upload racing PDF, DOCX or TXT document:",
            type=["pdf", "docx", "txt", "html", "htm"],
            key="docling_uploader"
        )

        if uploaded_file is not None:
            file_bytes = uploaded_file.read()
            file_name = uploaded_file.name
            cache_key = f"parsed_{file_name}_{len(file_bytes)}"
            
            if cache_key not in st.session_state:
                with st.spinner("IBM Docling is parsing layout & extracting document structured text..."):
                    try:
                        parsed_md = parse_document(file_bytes, file_name)
                        st.session_state[cache_key] = parsed_md
                        st.toast(f"Parsed {file_name} successfully!")
                    except Exception as e:
                        st.error(f"Error parsing document: {e}")

            parsed_content = st.session_state.get(cache_key, "")
            
            if parsed_content:
                st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.6rem;letter-spacing:0.15em;color:#888;margin-top:1rem;margin-bottom:0.5rem;">PARSED DOCUMENT MARKDOWN PREVIEW</div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div style="background:var(--bg-card);border:1px solid var(--border);border-radius:8px;padding:1rem;height:350px;overflow-y:auto;font-size:0.8rem;line-height:1.6;font-family:'Rajdhani', sans-serif;white-space:pre-wrap;">
{parsed_content}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("💡 Try uploading the FIA Sporting Regulations or strategy notes to start parsing!")
            
            # Show interactive sample card
            st.markdown("""
            <div style="background:rgba(255,255,255,0.01);border:1px dashed var(--border);border-radius:8px;padding:1rem;text-align:center;margin-bottom:1rem;">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#E8002D" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
              <div style="font-family:'Rajdhani',sans-serif;font-size:0.85rem;font-weight:700;margin-top:0.4rem;color:var(--text-primary);">FIA Sporting Regulations Stint Rules.pdf</div>
              <div style="font-family:'Share Tech Mono',monospace;font-size:0.55rem;color:var(--text-muted);margin:0.1rem 0 0.6rem;">SIZE: 2.4 MB &middot; PAGES: 82 &middot; STATUS: READY</div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("DEMO: LOAD FIA REGULATIONS SAMPLE", use_container_width=True, key="load_demo_btn"):
                sample_text = """# FIA Formula One Sporting Regulations - Section 4.2: Pit Lane Stint Rules

## Article 4.2.1: Tyre Allocation and Use
During any race weekend, competitors are allocated 13 sets of dry-weather tyres, 4 sets of intermediate tyres, and 3 sets of wet-weather tyres.
- Dry-weather tyres must be returned according to the Sporting Regulations under Art. 4.2.3.
- Each driver must use at least two different dry compounds during a dry race, unless intermediate or wet tyres are used.

## Article 4.2.2: Pit Lane Speed Limit
- The speed limit in the pit lane is set at 80 km/h (50 mph) for all practice, qualifying, and race sessions, unless adjusted by the Event Stewards due to safety concerns.
- Infractions during practice sessions incur a penalty of €100 for each km/h over the limit, up to a maximum of €1,000.
- Infractions during the race incur a 5-second or 10-second time penalty, or a drive-through penalty depending on the severity of the speed breach.

## Article 4.2.3: Stint Durations & Safety
- In extreme thermal degradation scenarios, the FIA Technical Delegate may enforce a maximum stint length of 18 laps per tyre set (as seen in Qatar GP).
- Exceeding this stint length will result in an immediate referral to the Stewards and a potential disqualification under Article 10.3.5 for unscheduled tyre stress hazards."""
                st.session_state["parsed_sample_stint_rules.pdf_820"] = sample_text
                st.session_state["active_doc_key"] = "parsed_sample_stint_rules.pdf_820"
                st.session_state["active_doc_name"] = "FIA Sporting Regulations Stint Rules.pdf"
                st.rerun()

    with doc_chat_col:
        st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.6rem;letter-spacing:0.15em;color:#888;margin-bottom:0.5rem;">2. CHAT WITH DOCUMENT VIA IBM GRANITE</div>', unsafe_allow_html=True)
        
        active_doc_key = None
        active_doc_name = ""
        
        if uploaded_file is not None:
            active_doc_key = f"parsed_{uploaded_file.name}_{len(file_bytes)}"
            active_doc_name = uploaded_file.name
        elif "active_doc_key" in st.session_state:
            active_doc_key = st.session_state.active_doc_key
            active_doc_name = st.session_state.active_doc_name
            
        if active_doc_key and active_doc_key in st.session_state:
            doc_text = st.session_state[active_doc_key]
            
            doc_msg_key = f"doc_messages_{active_doc_name}"
            if doc_msg_key not in st.session_state:
                st.session_state[doc_msg_key] = [
                    {
                        "role": "assistant",
                        "content": f"I have processed **{active_doc_name}** using IBM Docling! Ask me anything about the document, technical rules, or strategy."
                    }
                ]
            
            # Message container
            doc_chat_container = st.container(height=300)
            with doc_chat_container:
                for msg in st.session_state[doc_msg_key]:
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])
            
            # Chat inputs
            doc_prompt = st.chat_input("Ask a question about the uploaded document...", key="doc_chat_input_box")
            
            if doc_prompt:
                st.session_state[doc_msg_key].append({"role": "user", "content": doc_prompt})
                st.rerun()
                
            if st.session_state[doc_msg_key][-1]["role"] == "user":
                last_user_msg = st.session_state[doc_msg_key][-1]["content"]
                with st.spinner("IBM Granite is scanning document..."):
                    from core.granite import docling_chat_response
                    doc_response = docling_chat_response(
                        last_user_msg,
                        doc_text,
                        st.session_state[doc_msg_key][:-1]
                    )
                st.session_state[doc_msg_key].append({"role": "assistant", "content": doc_response})
                st.rerun()
                
            # Controls
            st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                if st.button("CLEAR CHAT HISTORY", use_container_width=True, key="clear_doc_chat_btn"):
                    st.session_state[doc_msg_key] = [
                        {
                            "role": "assistant",
                            "content": f"I have processed **{active_doc_name}** using IBM Docling! Ask me anything about the document."
                        }
                    ]
                    st.rerun()
            with c2:
                if st.button("UNLOAD DOCUMENT", use_container_width=True, key="unload_doc_btn"):
                    if "active_doc_key" in st.session_state:
                        del st.session_state.active_doc_key
                    if "active_doc_name" in st.session_state:
                        del st.session_state.active_doc_name
                    st.rerun()
        else:
            st.info("Please upload a document on the left or load the demo sample to start talking to it.")


# ====== FOOTER ======
st.markdown('<div style="height:2px;background:linear-gradient(90deg,#E8002D,transparent);margin:1.5rem 0 0.5rem;"></div>', unsafe_allow_html=True)
render_ibm_label("IBM GRANITE 3.1 &middot; IBM BOB &middot; WHISPER &middot; OpenF1 + FastF1")
