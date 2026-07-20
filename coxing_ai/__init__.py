"""Core package for CoxingCoachAI."""

from .core import DEFAULT_SCENARIO, FOCUS_AREAS
from .feedback import generate_feedback
from .simulator import simulate_race_from_transcript
from .transcription import load_local_whisper_model, transcribe_audio_file

__all__ = [
    "FOCUS_AREAS",
    "DEFAULT_SCENARIO",
    "generate_feedback",
    "simulate_race_from_transcript",
    "load_local_whisper_model",
    "transcribe_audio_file",
]
