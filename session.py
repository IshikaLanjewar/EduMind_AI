"""utils/session.py — Session state initialisation helpers"""

import streamlit as st


def init_session() -> None:
    """Initialise all session-state keys with safe defaults."""
    defaults = {
        "messages": [],
        "mode": "💬 Text Chat",
        "topic": "General",
        "ollama_url": "http://localhost:11434",
        "model": "llama3.2",
        "vision_model": "llava",
        "max_tokens": 1024,
        "temperature": 0.7,
        "image_data": None,
        "image_mime": None,
        "tts_enabled": True,
        "voice_rate": 150,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
