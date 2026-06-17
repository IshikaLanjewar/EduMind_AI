"""
EduMind AI — Multimodal Educational Assistant
Powered by Ollama (FREE — no API key required)
"""

import streamlit as st
from pages import text_chat, image_analysis, voice_tts, multimodal
from utils.session import init_session
from utils.claude_client import check_ollama_running, list_models

st.set_page_config(
    page_title="EduMind AI — Ollama",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

init_session()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎓 EduMind AI")
    st.markdown("*Powered by Ollama — 100% Free*")
    st.divider()

    # ── Ollama status ──────────────────────────────────────────────────────────
    st.markdown("### 🦙 Ollama Connection")
    ollama_url = st.text_input(
        "Ollama URL",
        value=st.session_state.get("ollama_url", "http://localhost:11434"),
        help="Default: http://localhost:11434",
    )
    st.session_state["ollama_url"] = ollama_url

    is_running     = check_ollama_running()
    available_models = list_models() if is_running else []

    if is_running:
        st.success(f"✅ Ollama running — {len(available_models)} model(s) found")
    else:
        st.error("❌ Ollama not running")

    st.divider()

    # ── Model selection ────────────────────────────────────────────────────────
    st.markdown("### 🤖 Models")

    # Use real installed models if available, else show sensible defaults
    if available_models:
        text_model_options = available_models
        # Vision models: prefer llava/moondream; fall back to first available
        vision_options = [m for m in available_models if any(
            v in m.lower() for v in ["llava", "bakllava", "moondream", "minicpm", "vision"]
        )]
        if not vision_options:
            vision_options = available_models   # allow any model as vision fallback
    else:
        text_model_options = ["llama3.2", "llama3.1", "mistral", "gemma2", "phi3", "qwen2.5"]
        vision_options     = ["llava", "moondream"]

    # Preserve previous selection if still valid
    prev_text   = st.session_state.get("model", text_model_options[0])
    prev_vision = st.session_state.get("vision_model", vision_options[0])

    text_idx   = text_model_options.index(prev_text)   if prev_text   in text_model_options   else 0
    vision_idx = vision_options.index(prev_vision)     if prev_vision in vision_options         else 0

    st.session_state["model"] = st.selectbox(
        "Text Model",
        text_model_options,
        index=text_idx,
        help="Used for Text Chat and Voice modes",
    )
    st.session_state["vision_model"] = st.selectbox(
        "Vision Model (images)",
        vision_options,
        index=vision_idx,
        help="Used in Image Analysis and Multimodal modes",
    )

    if available_models:
        st.caption(f"Installed: `{'`, `'.join(available_models)}`")

    st.divider()

    # ── Learning mode ──────────────────────────────────────────────────────────
    st.markdown("### 📚 Learning Mode")
    mode = st.radio(
        "Select mode",
        options=["💬 Text Chat", "🖼 Image Analysis", "🎙 Voice + TTS", "✨ Multimodal"],
        index=0,
        label_visibility="collapsed",
    )
    st.session_state["mode"] = mode

    st.divider()

    # ── Topic & settings ───────────────────────────────────────────────────────
    st.markdown("### 🏷 Topic Focus")
    topic = st.selectbox(
        "Topic",
        ["General", "Science", "Mathematics", "History", "Coding",
         "Language", "Art", "Physics", "Chemistry", "Biology"],
    )
    st.session_state["topic"] = topic

    st.markdown("### ⚙️ Settings")
    st.session_state["max_tokens"]   = st.slider("Max response tokens", 256, 4096, 1024, 128)
    st.session_state["temperature"]  = st.slider("Temperature", 0.0, 1.0, 0.7, 0.05)

    st.divider()
    if st.button("🗑 Clear Chat History", use_container_width=True):
        st.session_state["messages"]    = []
        st.session_state["image_data"]  = None
        st.rerun()

    st.markdown(
        "<div style='text-align:center;font-size:11px;color:#888;margin-top:12px'>"
        "Powered by Ollama · Built with Streamlit<br>100% Free · Runs Locally</div>",
        unsafe_allow_html=True,
    )

# ── Main header ────────────────────────────────────────────────────────────────
st.markdown("<h1 class='main-title'>🎓 EduMind AI</h1>", unsafe_allow_html=True)
st.markdown(
    "<p class='subtitle'>Multimodal Educational Assistant — Text · Image · Voice · 100% Free</p>",
    unsafe_allow_html=True,
)

# ── Ollama not running → show setup guide ──────────────────────────────────────
if not is_running:
    st.error("🦙 **Ollama is not running.** Follow the steps below to start it.")
    with st.expander("📖 Quick Setup Guide", expanded=True):
        st.markdown("""
### Step 1 — Install Ollama
Download from **[ollama.com/download](https://ollama.com/download)**

### Step 2 — Start Ollama (keep this terminal open)
```
ollama serve
```

### Step 3 — Download a model (new terminal)
```
ollama pull llama3.2
ollama pull llava
```

### Step 4 — Refresh this browser page
""")
    st.stop()

# ── No models downloaded yet ───────────────────────────────────────────────────
if not available_models:
    st.warning("⚠️ Ollama is running but **no models are downloaded** yet.")
    st.code("ollama pull llama3.2\nollama pull llava", language="bash")
    st.stop()

# ── Route to page ──────────────────────────────────────────────────────────────
if mode == "💬 Text Chat":
    text_chat.render()
elif mode == "🖼 Image Analysis":
    image_analysis.render()
elif mode == "🎙 Voice + TTS":
    voice_tts.render()
elif mode == "✨ Multimodal":
    multimodal.render()
