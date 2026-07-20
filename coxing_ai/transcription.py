"""Local speech-to-text adapter for CoxingCoachAI.

This module uses Faster-Whisper on CPU and requires no API key.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .core import MAX_LOCAL_AUDIO_MB, SUPPORTED_AUDIO_EXTENSIONS


class TranscriptionError(RuntimeError):
    """Raised when local transcription cannot be completed."""


ROWING_VOCABULARY_PROMPT = (
    "This is a rowing coxswain race or practice recording. "
    "Expected vocabulary includes coxswain, coxing, CoxBox, rowing, shell, oars, "
    "oarlocks, catch, finish, drive, recovery, legs, body, arms, swing, send, "
    "length, ratio, feather, square, stroke rate, strokes per minute, split, "
    "power ten, power 10, settle, rhythm, rate shift, sprint, bow pair, stern pair, "
    "port, starboard, bow ball, walk, seats, and open water."
)


def validate_audio_path(audio_path: str | Path) -> Path:
    path = Path(audio_path)
    if not path.exists():
        raise TranscriptionError(f"Audio file not found: {path}")

    ext = path.suffix.lower().lstrip(".")
    if ext not in SUPPORTED_AUDIO_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_AUDIO_EXTENSIONS))
        raise TranscriptionError(
            f"Unsupported audio extension '.{ext}'. Supported extensions: {supported}."
        )

    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > MAX_LOCAL_AUDIO_MB:
        raise TranscriptionError(
            f"Audio file is {size_mb:.1f} MB. This app limits local transcription "
            f"uploads to {MAX_LOCAL_AUDIO_MB} MB to protect server resources."
        )
    return path


def load_local_whisper_model(model_name: str = "base.en") -> Any:
    """Load a CPU INT8 Faster-Whisper model.

    Streamlit should cache the returned object with ``st.cache_resource`` so the
    model is not reloaded on every widget interaction.
    """
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise TranscriptionError(
            "Faster-Whisper is not installed. Run `pip install faster-whisper`."
        ) from exc

    cpu_threads = max(1, min(4, os.cpu_count() or 2))
    try:
        return WhisperModel(
            model_name,
            device="cpu",
            compute_type="int8",
            cpu_threads=cpu_threads,
            num_workers=1,
        )
    except Exception as exc:
        raise TranscriptionError(
            f"Could not load local Whisper model '{model_name}': {exc}"
        ) from exc


def transcribe_audio_file(
    audio_path: str | Path,
    model: Any,
    model_name: str = "base.en",
    source_name: str | None = None,
) -> dict[str, Any]:
    """Transcribe an audio file locally with a preloaded Faster-Whisper model."""
    path = validate_audio_path(audio_path)

    try:
        segments_generator, info = model.transcribe(
            str(path),
            language="en",
            beam_size=5,
            vad_filter=True,
            vad_parameters={"min_silence_duration_ms": 500},
            condition_on_previous_text=True,
            initial_prompt=ROWING_VOCABULARY_PROMPT,
            word_timestamps=False,
        )
        segments = list(segments_generator)
    except Exception as exc:
        raise TranscriptionError(
            "Local transcription failed. Confirm that the recording is a valid, "
            f"non-corrupted audio file. Technical detail: {exc}"
        ) from exc

    transcript = " ".join(
        segment.text.strip() for segment in segments if segment.text.strip()
    ).strip()

    segment_results = [
        {
            "start_seconds": round(float(segment.start), 2),
            "end_seconds": round(float(segment.end), 2),
            "text": segment.text.strip(),
        }
        for segment in segments
        if segment.text.strip()
    ]

    language_probability = getattr(info, "language_probability", None)
    duration = getattr(info, "duration", None)
    duration_after_vad = getattr(info, "duration_after_vad", None)

    return {
        "text": transcript,
        "model": model_name,
        "device": "cpu",
        "compute_type": "int8",
        "language": getattr(info, "language", "en"),
        "language_probability": (
            round(float(language_probability), 4)
            if language_probability is not None
            else None
        ),
        "duration_seconds": round(float(duration), 2) if duration is not None else None,
        "duration_after_vad_seconds": (
            round(float(duration_after_vad), 2)
            if duration_after_vad is not None
            else None
        ),
        "segments": segment_results,
        "source_file": source_name or path.name,
    }
