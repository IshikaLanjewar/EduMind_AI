"""Ollama HTTP client used by EduMind AI."""

import base64
from typing import Optional

import requests
import streamlit as st

OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_TEXT_MODEL = "llama3.2"
DEFAULT_VISION_MODEL = "llava"


def _secret(name: str, default: str = "") -> str:
    """Read a Streamlit secret safely; local development does not require secrets.toml."""
    try:
        value = st.secrets.get(name, default)
        return str(value) if value is not None else default
    except Exception:
        return default


def _base_url() -> str:
    """Use a Streamlit Cloud Ollama URL when configured, otherwise local Ollama."""
    cloud_url = _secret("OLLAMA_URL")
    if cloud_url:
        return cloud_url.rstrip("/")

    return st.session_state.get("ollama_url", OLLAMA_BASE_URL).rstrip("/")


def _headers() -> dict:
    """Optional bearer token for a secured remote Ollama gateway."""
    token = _secret("OLLAMA_API_KEY")
    return {"Authorization": f"Bearer {token}"} if token else {}


def check_ollama_running() -> bool:
    try:
        response = requests.get(
            f"{_base_url()}/api/tags",
            headers=_headers(),
            timeout=5,
        )
        return response.ok
    except requests.RequestException:
        return False


def list_models() -> list:
    try:
        response = requests.get(
            f"{_base_url()}/api/tags",
            headers=_headers(),
            timeout=8,
        )
        response.raise_for_status()
        return [m["name"] for m in response.json().get("models", [])]
    except (requests.RequestException, ValueError, KeyError, TypeError):
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
    if not check_ollama_running():
        return (
            "❌ **Ollama is not reachable.**\n\n"
            "For local use, start Ollama with:\n```bash\nollama serve\n```\n\n"
            "For Streamlit Cloud, set the `OLLAMA_URL` secret to a secure, "
            "network-reachable Ollama endpoint."
        )

    model = (
        st.session_state.get("vision_model", DEFAULT_VISION_MODEL)
        if image_b64
        else st.session_state.get("model", DEFAULT_TEXT_MODEL)
    )

    available = list_models()
    if available and model not in available:
        match = next((m for m in available if m.startswith(model.split(":")[0])), None)
        if match:
            model = match
        else:
            return (
                f"❌ **Model `{model}` is not downloaded.**\n\n"
                f"Run:\n```bash\nollama pull {model}\n```\n\n"
                f"**Available models:** {', '.join(available) if available else 'none found'}"
            )

    system_prompt = build_system_prompt(mode, topic)
    prompt_parts = []

    for msg in history[-8:]:
        role = msg.get("role", "user")
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

    payload = {
        "model": model,
        "prompt": full_prompt,
        "system": system_prompt,
        "stream": False,
        "options": {
            "temperature": float(st.session_state.get("temperature", 0.7)),
            "num_predict": int(st.session_state.get("max_tokens", 1024)),
        },
    }

    if image_b64:
        payload["images"] = [image_b64]

    try:
        response = requests.post(
            f"{_base_url()}/api/generate",
            json=payload,
            headers=_headers(),
            timeout=180,
        )

        if response.status_code == 401:
            return "🔐 **Ollama authentication failed.** Check the `OLLAMA_API_KEY` Streamlit secret."

        if response.status_code == 404:
            return f"❌ **Model `{model}` not found on Ollama.** Run `ollama pull {model}`."

        if response.status_code == 500:
            try:
                detail = response.json().get("error", response.text[:300])
            except Exception:
                detail = response.text[:300]
            return f"❌ **Ollama server error (500).**\n\nDetails: `{detail}`"

        response.raise_for_status()
        data = response.json()
        return data.get("response", "⚠️ Empty response from Ollama.")

    except requests.exceptions.ConnectionError:
        return "❌ **Cannot connect to Ollama.** Check the configured Ollama URL."
    except requests.exceptions.Timeout:
        return "⏳ **Ollama timed out.** Try a smaller model or reduce Max Tokens."
    except requests.exceptions.RequestException as exc:
        return f"⚠️ **Ollama request failed:** {exc}"
    except Exception as exc:
        return f"⚠️ Unexpected error: {exc}"


def encode_image(uploaded_file) -> tuple:
    raw = uploaded_file.read()
    b64 = base64.b64encode(raw).decode("utf-8")
    mime = uploaded_file.type or "image/jpeg"
    return b64, mime
