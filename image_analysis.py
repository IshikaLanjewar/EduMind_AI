"""pages/image_analysis.py — Upload an image and ask Ollama (llava) to explain it"""

import io
import streamlit as st
from PIL import Image
from utils.claude_client import chat, encode_image
from utils.audio import render_tts_player
from components.chat_ui import render_chat_history, get_user_input


def render() -> None:
    st.markdown("## 🖼 Image Analysis")
    st.caption(
        "Upload any educational image — diagrams, textbook pages, charts, photos — "
        "and ask questions. Requires the **llava** model (`ollama pull llava`)."
    )

    col1, col2 = st.columns([1, 2])

    # ── Left column: upload + prompt suggestions ───────────────────────────────
    with col1:
        uploaded = st.file_uploader(
            "Upload Image",
            type=["jpg", "jpeg", "png", "webp"],
            help="JPG, PNG or WebP. Max ~10 MB.",
            key="img_uploader",
        )

        if uploaded is not None:
            # Read bytes once and keep them in session (JSON-serialisable)
            raw_bytes = uploaded.read()
            img = Image.open(io.BytesIO(raw_bytes))
            st.image(img, caption="Uploaded image", use_container_width=True)

            # Store base64 + raw bytes (for display) in session state
            import base64
            b64   = base64.b64encode(raw_bytes).decode("utf-8")
            mime  = uploaded.type or "image/jpeg"
            st.session_state["image_data"]   = b64
            st.session_state["image_mime"]   = mime
            st.session_state["image_bytes"]  = raw_bytes  # for thumbnail display
            st.success("✅ Image ready — type a question →")

        # Prompt suggestions
        st.markdown("**Suggested questions:**")
        suggestions = [
            "Explain everything in this image",
            "Label all components",
            "What concept does this illustrate?",
            "Describe this for a student",
            "What are the key takeaways?",
            "Create a quiz from this image",
        ]
        for s in suggestions:
            if st.button(s, key=f"sug_{s}", use_container_width=True):
                st.session_state["prefill"] = s
                st.rerun()

    # ── Right column: chat ─────────────────────────────────────────────────────
    with col2:
        render_chat_history(tts=True)

        if not st.session_state.get("image_data"):
            st.warning("⬅ Please upload an image first.")
            return

        user_input = get_user_input(
            placeholder="Ask about the uploaded image…",
            input_key="image_chat_input",
        )
        if not user_input:
            return

        # Snapshot image data before clearing
        img_b64   = st.session_state["image_data"]
        img_mime  = st.session_state["image_mime"]
        img_bytes = st.session_state.get("image_bytes")

        # Show user bubble
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)
            if img_bytes:
                st.image(img_bytes, width=120)

        # Build history
        history = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.get("messages", [])
        ]

        # Save user message (store raw bytes for history display, not PIL Image)
        st.session_state["messages"].append({
            "role":        "user",
            "content":     user_input,
            "image_bytes": img_bytes,
        })

        # Clear image from session so next upload is fresh
        st.session_state["image_data"]  = None
        st.session_state["image_mime"]  = None
        st.session_state["image_bytes"] = None

        # Call Ollama vision model
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Analysing image with llava…"):
                reply = chat(
                    user_text=user_input,
                    history=history,
                    mode="🖼 Image Analysis",
                    topic=st.session_state.get("topic", "General"),
                    image_b64=img_b64,
                    image_mime=img_mime,
                )
            st.markdown(reply)
            if st.session_state.get("tts_enabled", True):
                render_tts_player(reply)

        st.session_state["messages"].append({"role": "assistant", "content": reply})
        st.rerun()
