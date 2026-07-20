"""Speech-to-text adapter for the CoxingCoachAI MVP."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .core import MAX_API_AUDIO_MB, SUPPORTED_AUDIO_EXTENSIONS


class TranscriptionError(RuntimeError):
    """Raised when transcription cannot be completed."""


def _get_openai_key() -> str | None:
    return os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_KEY")


def validate_audio_path(audio_path: str | Path) -> Path:
    path = Path(audio_path)
    if not path.exists():
        raise TranscriptionError(f"Audio file not found: {path}")
    ext = path.suffix.lower().lstrip(".")
    if ext not in SUPPORTED_AUDIO_EXTENSIONS:
        raise TranscriptionError(
            f"Unsupported audio extension '.{ext}'. Supported: {', '.join(sorted(SUPPORTED_AUDIO_EXTENSIONS))}"
        )
    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > MAX_API_AUDIO_MB:
        raise TranscriptionError(
            f"Audio file is {size_mb:.1f} MB. The default API transcription path supports up to {MAX_API_AUDIO_MB} MB."
        )
    return path


def transcribe_audio_file(
    audio_path: str | Path,
    api_key: str | None = None,
    model: str | None = None,
) -> dict[str, Any]:
    """Transcribe an audio file using OpenAI speech-to-text.

    Returns a dict with at least a `text` field. This function intentionally keeps
    the provider boundary isolated so another transcription backend can be swapped
    in later.
    """
    path = validate_audio_path(audio_path)
    api_key = api_key or _get_openai_key()
    if not api_key:
        raise TranscriptionError(
            "No API key found. Set OPENAI_API_KEY locally or add [openai].api_key to Streamlit secrets."
        )

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise TranscriptionError("Install the OpenAI package with `pip install openai`.") from exc

    client = OpenAI(api_key=api_key)
    transcription_model = model or os.getenv("OPENAI_TRANSCRIPTION_MODEL", "gpt-4o-mini-transcribe")

    with path.open("rb") as audio_file:
        result = client.audio.transcriptions.create(
            model=transcription_model,
            file=audio_file,
        )

    text = getattr(result, "text", None) or (result.get("text") if isinstance(result, dict) else "")
    return {
        "text": text.strip(),
        "model": transcription_model,
        "source_file": path.name,
    }
