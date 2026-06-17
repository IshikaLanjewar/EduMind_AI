"""pages/voice_tts.py — Voice input + Text-to-Speech responses"""

import streamlit as st
from utils.claude_client import chat
from utils.audio import render_tts_player, render_voice_input
from components.chat_ui import render_chat_history, get_user_input


def render() -> None:
    st.markdown("## 🎙 Voice + Text-to-Speech")
    st.caption(
        "Use the mic widget to speak your question, then paste the transcript below. "
        "AI responses are played back automatically via Text-to-Speech."
    )

    # ── Voice Settings ────────────────────────────────────────────────────────
    with st.expander("🔊 TTS Settings", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            tts_on = st.toggle(
                "Enable TTS auto-play",
                value=st.session_state.get("tts_enabled", True),
                key="voice_tts_toggle",
            )
            st.session_state["tts_enabled"] = tts_on

            rate = st.slider(
                "Speaking speed",
                min_value=80, max_value=250, value=st.session_state.get("voice_rate", 150), step=10,
                help="80 = slow, 150 = normal, 250 = fast",
                key="voice_rate_slider",
            )
            st.session_state["voice_rate"] = rate
        with c2:
            st.info(
                "**Tips:**\n"
                "- Voice input works best in **Chrome** or **Edge**\n"
                "- Allow microphone when prompted\n"
                "- TTS uses your browser's built-in speech engine"
            )

    st.divider()

    # ── Voice Input Widget ────────────────────────────────────────────────────
    st.markdown("### 🎤 Step 1 — Speak Your Question")
    render_voice_input()

    st.markdown("### 💬 Step 2 — Paste Transcript & Send")
    st.caption("Copy the transcript from the widget above and paste it into the chat box below.")

    st.divider()

    # ── Chat History ──────────────────────────────────────────────────────────
    render_chat_history(tts=True)

    user_input = get_user_input(
        placeholder="Paste voice transcript here, or just type…",
        input_key="voice_chat_input",
    )
    if not user_input:
        return

    # Show user bubble
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    # Build history before saving
    history = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.get("messages", [])
    ]

    st.session_state["messages"].append({"role": "user", "content": user_input})

    # Get AI response
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Generating response…"):
            reply = chat(
                user_text=user_input,
                history=history,
                mode="🎙 Voice + TTS",
                topic=st.session_state.get("topic", "General"),
            )
        st.markdown(reply)
        # Always render TTS player in voice mode
        render_tts_player(reply)

    st.session_state["messages"].append({"role": "assistant", "content": reply})
    st.rerun()
