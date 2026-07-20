"""Core package for CoxingCoachAI MVP."""

from .core import FOCUS_AREAS, DEFAULT_SCENARIO
from .feedback import generate_feedback
from .simulator import simulate_race_from_transcript
from .transcription import transcribe_audio_file

__all__ = [
    "FOCUS_AREAS",
    "DEFAULT_SCENARIO",
    "generate_feedback",
    "simulate_race_from_transcript",
    "transcribe_audio_file",
]
