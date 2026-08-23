"""
EduMind AI — Multimodal Educational Assistant
Powered by Ollama (FREE — no API key required)
"""

import streamlit as st

from session import init_session
from claude_client import check_ollama_running, list_models

# Deployment marker: 2026-08-23-cloud-fix-2
# Mode modules are imported only after Ollama is available. This prevents an
# unrelated mode-module import error from stopping the whole Streamlit UI.

st.set_page_config(
    page_title="EduMind AI — Ollama",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

try:
    with open("style.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

init_session()

with st.sidebar:
    st.markdown("## 🎓 EduMind AI")
    st.markdown("*Powered by Ollama — 100% Free*")
    st.divider()

    st.markdown("### 🦙 Ollama Connection")
    try:
        secret_ollama_url = st.secrets.get("OLLAMA_URL", "")
    except Exception:
        secret_ollama_url = ""

    if secret_ollama_url:
        ollama_url = secret_ollama_url.rstrip("/")
        st.session_state["ollama_url"] = ollama_url
        st.caption("Using Ollama URL from Streamlit Secrets")
    else:
        ollama_url = st.text_input(
            "Ollama URL",
            value=st.session_state.get("ollama_url", "http://localhost:11434"),
            help="Local: http://localhost:11434. Streamlit Cloud requires a reachable remote Ollama endpoint.",
        ).rstrip("/")
        st.session_state["ollama_url"] = ollama_url

    is_running = check_ollama_running()
    available_models = list_models() if is_running else []

    if is_running:
        st.success(f"✅ Ollama running — {len(available_models)} model(s) found")
    else:
        st.warning("⚠️ Ollama not reachable")

    st.divider()

    st.markdown("### 🤖 Models")
    if available_models:
        text_model_options = available_models
        vision_options = [
            m for m in available_models
            if any(v in m.lower() for v in ["llava", "bakllava", "moondream", "minicpm", "vision"])
        ]
        if not vision_options:
            vision_options = available_models
    else:
        text_model_options = ["llama3.2", "llama3.1", "mistral", "gemma2", "phi3", "qwen2.5"]
        vision_options = ["llava", "moondream"]

    prev_text = st.session_state.get("model", text_model_options[0])
    prev_vision = st.session_state.get("vision_model", vision_options[0])
    text_idx = text_model_options.index(prev_text) if prev_text in text_model_options else 0
    vision_idx = vision_options.index(prev_vision) if prev_vision in vision_options else 0

    st.session_state["model"] = st.selectbox(
        "Text Model", text_model_options, index=text_idx,
        help="Used for Text Chat and Voice modes",
    )
    st.session_state["vision_model"] = st.selectbox(
        "Vision Model (images)", vision_options, index=vision_idx,
        help="Used in Image Analysis and Multimodal modes",
    )

    if available_models:
        st.caption(f"Installed: `{'`, `'.join(available_models)}`")

    st.divider()
    st.markdown("### 📚 Learning Mode")
    mode = st.radio(
        "Select mode",
        options=["💬 Text Chat", "🖼 Image Analysis", "🎙 Voice + TTS", "✨ Multimodal"],
        index=0,
        label_visibility="collapsed",
    )
    st.session_state["mode"] = mode

    st.divider()
    st.markdown("### 🏷 Topic Focus")
    topic = st.selectbox(
        "Topic",
        ["General", "Science", "Mathematics", "History", "Coding",
         "Language", "Art", "Physics", "Chemistry", "Biology"],
    )
    st.session_state["topic"] = topic

    st.markdown("### ⚙️ Settings")
    st.session_state["max_tokens"] = st.slider("Max response tokens", 256, 4096, 1024, 128)
    st.session_state["temperature"] = st.slider("Temperature", 0.0, 1.0, 0.7, 0.05)

    st.divider()
    if st.button("🗑 Clear Chat History", use_container_width=True):
        st.session_state["messages"] = []
        st.session_state["image_data"] = None
        st.session_state["image_mime"] = None
        st.session_state["image_bytes"] = None
        st.rerun()

    st.markdown(
        "<div style='text-align:center;font-size:11px;color:#888;margin-top:12px'>"
        "Powered by Ollama · Built with Streamlit<br>100% Free · Runs Locally</div>",
        unsafe_allow_html=True,
    )

st.markdown("<h1 class='main-title'>🎓 EduMind AI</h1>", unsafe_allow_html=True)
st.markdown(
    "<p class='subtitle'>Multimodal Educational Assistant — Text · Image · Voice · 100% Free</p>",
    unsafe_allow_html=True,
)

if not is_running:
    st.info(
        "🦙 **Ollama is not reachable.** The Streamlit interface is deployed correctly, "
        "but AI responses require a running Ollama server."
    )
    with st.expander("📖 Quick Setup Guide", expanded=True):
        st.markdown("""
### Local development
Install Ollama from [ollama.com/download](https://ollama.com/download), then run:

```bash
ollama serve
ollama pull llama3.2
ollama pull llava
```

### Streamlit Cloud
Configure an `OLLAMA_URL` secret pointing to a **secure, network-reachable Ollama server**. Do not expose an unauthenticated Ollama server publicly.
""")
else:
    if not available_models:
        st.warning("⚠️ Ollama is running but **no models are downloaded** yet.")
        st.code("ollama pull llama3.2\nollama pull llava", language="bash")
    else:
        # Lazy imports: only load the selected mode after Ollama is confirmed.
        if mode == "💬 Text Chat":
            import text_chat
            text_chat.render()
        elif mode == "🖼 Image Analysis":
            import image_analysis
            image_analysis.render()
        elif mode == "🎙 Voice + TTS":
            import voice_tts
            voice_tts.render()
        elif mode == "✨ Multimodal":
            import multimodal
            multimodal.render()
