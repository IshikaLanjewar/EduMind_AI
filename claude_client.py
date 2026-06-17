"""utils/claude_client.py — Ollama backend (compatible with all Ollama versions)"""

import base64
import requests
from typing import Optional
import streamlit as st

OLLAMA_BASE_URL   = "http://localhost:11434"
DEFAULT_TEXT_MODEL   = "llama3.2"
DEFAULT_VISION_MODEL = "llava"


def _base_url() -> str:
    return st.session_state.get("ollama_url", OLLAMA_BASE_URL).rstrip("/")


def check_ollama_running() -> bool:
    try:
        requests.get(f"{_base_url()}/api/tags", timeout=4)
        return True
    except Exception:
        return False


def list_models() -> list:
    try:
        r = requests.get(f"{_base_url()}/api/tags", timeout=5)
        r.raise_for_status()
        return [m["name"] for m in r.json().get("models", [])]
    except Exception:
        return []


def build_system_prompt(mode: str, topic: str) -> str:
    topic_note = f" Focus on the subject: {topic}." if topic != "General" else ""
    base = {
        "💬 Text Chat": (
            "You are EduMind AI, an expert educational tutor. "
            "Explain concepts clearly with examples, analogies, and step-by-step reasoning. "
            "Use markdown for structure."
        ),
        "🖼 Image Analysis": (
            "You are EduMind AI with vision capabilities. "
            "Analyse images thoroughly — identify components, explain concepts, "
            "and teach the viewer. Use markdown headers and bullet points."
        ),
        "🎙 Voice + TTS": (
            "You are EduMind AI speaking to a student. "
            "Be conversational and clear. Avoid heavy markdown — this will be read aloud."
        ),
        "✨ Multimodal": (
            "You are EduMind AI, a comprehensive multimodal educational assistant. "
            "Combine image analysis with broad knowledge. Use headers, bullets, and code blocks."
        ),
    }
    return base.get(mode, base["💬 Text Chat"]) + topic_note


def chat(
    user_text: str,
    history: list,
    mode: str,
    topic: str,
    image_b64: Optional[str] = None,
    image_mime: Optional[str] = None,
) -> str:
    """Send message to Ollama using /api/generate (most compatible endpoint)."""

    if not check_ollama_running():
        return (
            "❌ **Ollama is not running.**\n\n"
            "Open a terminal and run:\n```\nollama serve\n```\n"
            "Then refresh this page."
        )

    # Choose model
    if image_b64:
        model = st.session_state.get("vision_model", DEFAULT_VISION_MODEL)
    else:
        model = st.session_state.get("model", DEFAULT_TEXT_MODEL)

    # Verify the model exists locally
    available = list_models()
    if available and model not in available:
        # Try to find a close match (e.g. "llama3.2" vs "llama3.2:latest")
        match = next((m for m in available if m.startswith(model.split(":")[0])), None)
        if match:
            model = match
        else:
            return (
                f"❌ **Model `{model}` is not downloaded.**\n\n"
                f"Run this in your terminal:\n```\nollama pull {model}\n```\n\n"
                f"**Available models:** {', '.join(available) if available else 'none found'}"
            )

    system_prompt = build_system_prompt(mode, topic)

    # ── Build full prompt string for /api/generate ─────────────────────────
    # This endpoint is the most stable across all Ollama versions.
    prompt_parts = []

    # Add conversation history as formatted text
    for msg in history[-8:]:
        role    = msg.get("role", "user")
        content = msg.get("content", "")
        if isinstance(content, list):
            content = " ".join(
                b.get("text", "") for b in content if isinstance(b, dict)
            )
        if role == "user":
            prompt_parts.append(f"User: {content}")
        elif role == "assistant":
            prompt_parts.append(f"Assistant: {content}")

    prompt_parts.append(f"User: {user_text}")
    prompt_parts.append("Assistant:")

    full_prompt = "\n".join(prompt_parts)

    # ── Payload for /api/generate ──────────────────────────────────────────
    payload: dict = {
        "model":  model,
        "prompt": full_prompt,
        "system": system_prompt,
        "stream": False,
        "options": {
            "temperature": float(st.session_state.get("temperature", 0.7)),
            "num_predict": int(st.session_state.get("max_tokens", 1024)),
        },
    }

    # Add image for vision models
    if image_b64:
        payload["images"] = [image_b64]

    try:
        response = requests.post(
            f"{_base_url()}/api/generate",
            json=payload,
            timeout=180,
        )

        # Show helpful error for bad status codes
        if response.status_code == 404:
            return (
                f"❌ **Model `{model}` not found on Ollama.**\n\n"
                f"Run:\n```\nollama pull {model}\n```"
            )
        if response.status_code == 500:
            detail = ""
            try:
                detail = response.json().get("error", response.text[:300])
            except Exception:
                detail = response.text[:300]
            return (
                f"❌ **Ollama server error (500).**\n\n"
                f"Details: `{detail}`\n\n"
                f"**Try these fixes:**\n"
                f"1. Make sure the model is fully downloaded: `ollama pull {model}`\n"
                f"2. Restart Ollama: close and reopen, or run `ollama serve`\n"
                f"3. Try a different model in the sidebar"
            )

        response.raise_for_status()
        data = response.json()
        return data.get("response", "⚠️ Empty response from Ollama.")

    except requests.exceptions.ConnectionError:
        return (
            "❌ **Cannot connect to Ollama.**\n\n"
            "Run `ollama serve` in a terminal and keep it open."
        )
    except requests.exceptions.Timeout:
        return (
            "⏳ **Ollama timed out.**\n\n"
            "The model is taking too long. Try:\n"
            "- A smaller model (e.g. `phi3` or `llama3.2`)\n"
            "- Reducing Max Tokens in sidebar\n"
            "- Closing other heavy apps to free RAM"
        )
    except Exception as exc:
        return f"⚠️ Unexpected error: {exc}"


def encode_image(uploaded_file) -> tuple:
    """Encode UploadedFile → (base64_string, mime_type)."""
    raw  = uploaded_file.read()
    b64  = base64.b64encode(raw).decode("utf-8")
    mime = uploaded_file.type or "image/jpeg"
    return b64, mime
