"""components/chat_ui.py — Reusable chat display and input components"""

import streamlit as st
from utils.audio import render_tts_player


def render_chat_history(tts: bool = False) -> None:
    """Render all messages stored in st.session_state['messages']."""
    messages = st.session_state.get("messages", [])
    if not messages:
        st.info("💡 Start by typing a question below, or pick a quick-start topic!")
        return

    for idx, msg in enumerate(messages):
        role    = msg["role"]
        content = msg["content"]
        icon    = "🤖" if role == "assistant" else "👤"

        with st.chat_message(role, avatar=icon):
            # Show image thumbnail if present (stored as bytes, not PIL object)
            img_bytes = msg.get("image_bytes")
            if img_bytes:
                st.image(img_bytes, caption="Uploaded image", use_container_width=False, width=200)

            st.markdown(content)

            # TTS player for assistant messages only
            if role == "assistant" and tts and st.session_state.get("tts_enabled", True):
                render_tts_player(content)


def render_quick_starters() -> None:
    """Display quick-start prompt buttons."""
    questions = [
        "🌱 Explain photosynthesis step by step",
        "💻 How do binary numbers work?",
        "📜 What caused World War 1?",
        "📐 Teach me the Pythagorean theorem",
        "⚛️ What is quantum entanglement?",
        "🧬 Explain DNA replication",
    ]
    st.markdown("**Quick starters:**")
    cols = st.columns(3)
    for i, q in enumerate(questions):
        if cols[i % 3].button(q, use_container_width=True, key=f"qs_{i}"):
            st.session_state["prefill"] = q
            st.rerun()


def get_user_input(placeholder: str = "Ask anything…", input_key: str = "chat_input_main") -> str:
    """Render chat input and return the user's message, or '' if none submitted."""
    # Consume any prefill set by quick-start buttons
    prefill = st.session_state.pop("prefill", "")
    user_input = st.chat_input(placeholder, key=input_key)
    # chat_input returns None when empty; prefill is returned otherwise
    return user_input if user_input else prefill
