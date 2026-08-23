"""Image analysis mode using an Ollama vision model."""

import io
import base64
import streamlit as st
from PIL import Image
from claude_client import chat
from audio import render_tts_player
from chat_ui import render_chat_history, get_user_input


def render() -> None:
    st.markdown("## 🖼 Image Analysis")
    st.caption(
        "Upload an educational image — diagrams, textbook pages, charts, or photos — "
        "and ask questions. Requires a vision model such as **llava**."
    )

    col1, col2 = st.columns([1, 2])

    with col1:
        uploaded = st.file_uploader(
            "Upload Image",
            type=["jpg", "jpeg", "png", "webp"],
            help="JPG, PNG or WebP. Max ~10 MB.",
            key="img_uploader",
        )

        if uploaded is not None:
            raw_bytes = uploaded.read()
            img = Image.open(io.BytesIO(raw_bytes))
            st.image(img, caption="Uploaded image", use_container_width=True)
            b64 = base64.b64encode(raw_bytes).decode("utf-8")
            mime = uploaded.type or "image/jpeg"
            st.session_state["image_data"] = b64
            st.session_state["image_mime"] = mime
            st.session_state["image_bytes"] = raw_bytes
            st.success("✅ Image ready — type a question →")

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

        img_b64 = st.session_state["image_data"]
        img_mime = st.session_state["image_mime"]
        img_bytes = st.session_state.get("image_bytes")

        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)
            if img_bytes:
                st.image(img_bytes, width=120)

        history = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.get("messages", [])
        ]

        st.session_state["messages"].append({
            "role": "user",
            "content": user_input,
            "image_bytes": img_bytes,
        })

        st.session_state["image_data"] = None
        st.session_state["image_mime"] = None
        st.session_state["image_bytes"] = None

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Analysing image with vision model…"):
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
