"""Shared definitions for CoxingCoachAI."""

from __future__ import annotations

FOCUS_AREAS: dict[str, str] = {
    "communication_clarity": "Communication clarity and economy of words",
    "tone": "Tone and phase-appropriate intensity",
    "technical_calls": "Technical calls and rowing vocabulary",
    "rhythm_timing": "Rhythmic synchronization and call timing",
    "rate_management": "Rate management and race rhythm",
    "tactical_awareness": "Tactical awareness and race plan execution",
    "psychological_calibration": "Psychological calibration and trust-building",
}

DEFAULT_SCENARIO: dict[str, object] = {
    "race_distance_m": 2000,
    "base_rate_spm": 32,
    "base_split_seconds": 105.0,
    "boat_class": "8+",
    "crew_level": "Intermediate",
    "water_condition": "Flat",
    "race_phase": "Full 2k race",
}

PHASE_GUIDANCE: dict[str, str] = {
    "start": "Sharp, simple, high-intensity calls that establish length and rhythm.",
    "base": "Calm, repeatable, technical rhythm with minimal filler.",
    "move": "Urgent but controlled calls that state the purpose of the move.",
    "sprint": "High-energy calls with clear commitment and no panic.",
}

SUPPORTED_AUDIO_EXTENSIONS = {"mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm"}
MAX_LOCAL_AUDIO_MB = 100

LOCAL_WHISPER_MODELS: dict[str, str] = {
    "Fastest / lowest memory (tiny.en)": "tiny.en",
    "Balanced accuracy (base.en)": "base.en",
    "Higher accuracy / slower (small.en)": "small.en",
}
DEFAULT_LOCAL_WHISPER_MODEL = "base.en"
