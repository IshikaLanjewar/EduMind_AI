"""Multimodal mode: text + image + voice + TTS."""

import io
import base64
import streamlit as st
from PIL import Image
from claude_client import chat
from audio import render_tts_player, render_voice_input
from chat_ui import render_chat_history, get_user_input


def render() -> None:
    st.markdown("## ✨ Multimodal Mode")
    st.caption("Combine text questions, image uploads, and voice — all together.")

    col_img, col_mic, col_tts = st.columns(3)

    with col_img:
        st.markdown("**📷 Image (optional)**")
        uploaded = st.file_uploader(
            "Attach image",
            type=["jpg", "jpeg", "png", "webp"],
            label_visibility="collapsed",
            key="multi_img_uploader",
        )
        if uploaded is not None:
            raw_bytes = uploaded.read()
            img = Image.open(io.BytesIO(raw_bytes))
            st.image(img, caption="Ready", use_container_width=True)
            b64 = base64.b64encode(raw_bytes).decode("utf-8")
            mime = uploaded.type or "image/jpeg"
            st.session_state["image_data"] = b64
            st.session_state["image_mime"] = mime
            st.session_state["image_bytes"] = raw_bytes
            st.success("Image attached ✅")
        elif not st.session_state.get("image_data"):
            st.info("No image attached")

    with col_mic:
        st.markdown("**🎙 Voice Input**")
        render_voice_input()

    with col_tts:
        st.markdown("**🔊 Audio Output**")
        tts_on = st.toggle(
            "Auto-play TTS",
            value=st.session_state.get("tts_enabled", True),
            key="multi_tts_toggle",
        )
        st.session_state["tts_enabled"] = tts_on
        rate = st.slider(
            "Speed", 80, 250,
            value=st.session_state.get("voice_rate", 150),
            step=10,
            key="multi_rate_slider",
        )
        st.session_state["voice_rate"] = rate

    st.divider()

    with st.expander("💡 Quick prompts"):
        starters = [
            "Explain this image in simple terms",
            "What are the key concepts shown?",
            "Create a quiz from this topic",
            "Give me a 5-point summary",
            "Compare this to a real-world example",
            "What would a student need to memorise?",
        ]
        cols = st.columns(3)
        for i, s in enumerate(starters):
            if cols[i % 3].button(s, key=f"mm_qs_{i}", use_container_width=True):
                st.session_state["prefill"] = s
                st.rerun()

    render_chat_history(tts=True)

    user_input = get_user_input(
        placeholder="Ask anything — attach an image or paste voice transcript above…",
        input_key="multi_chat_input",
    )
    if not user_input:
        return

    has_image = bool(st.session_state.get("image_data"))
    img_b64 = st.session_state.get("image_data")
    img_mime = st.session_state.get("image_mime")
    img_bytes = st.session_state.get("image_bytes")

    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)
        if has_image and img_bytes:
            st.image(img_bytes, width=150)

    history = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.get("messages", [])
    ]

    st.session_state["messages"].append({
        "role": "user",
        "content": user_input,
        "image_bytes": img_bytes if has_image else None,
    })

    if has_image:
        st.session_state["image_data"] = None
        st.session_state["image_mime"] = None
        st.session_state["image_bytes"] = None

    with st.chat_message("assistant", avatar="🤖"):
        spinner_msg = "Processing with vision model…" if has_image else "Processing…"
        with st.spinner(spinner_msg):
            reply = chat(
                user_text=user_input,
                history=history,
                mode="✨ Multimodal",
                topic=st.session_state.get("topic", "General"),
                image_b64=img_b64 if has_image else None,
                image_mime=img_mime if has_image else None,
            )
        st.markdown(reply)
        if st.session_state.get("tts_enabled", True):
            render_tts_player(reply)

    st.session_state["messages"].append({"role": "assistant", "content": reply})
    st.rerun()
