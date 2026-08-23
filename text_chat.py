"""Text question-and-answer mode."""

import streamlit as st
from claude_client import chat
from chat_ui import render_chat_history, render_quick_starters, get_user_input


def render() -> None:
    st.markdown("## 💬 Text Chat")
    st.caption("Ask any question and get clear, structured educational explanations.")

    render_quick_starters()
    st.divider()
    render_chat_history(tts=False)

    user_input = get_user_input(
        placeholder="Ask anything you'd like to learn…",
        input_key="text_chat_input",
    )
    if not user_input:
        return

    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    history = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.get("messages", [])
    ]

    st.session_state["messages"].append({"role": "user", "content": user_input})

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking…"):
            reply = chat(
                user_text=user_input,
                history=history,
                mode="💬 Text Chat",
                topic=st.session_state.get("topic", "General"),
            )
        st.markdown(reply)

    st.session_state["messages"].append({"role": "assistant", "content": reply})
    st.rerun()
