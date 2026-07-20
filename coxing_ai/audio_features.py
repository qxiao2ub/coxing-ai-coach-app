"""Lightweight transcript feature extraction for coxing feedback."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from typing import Iterable

FILLER_WORDS = {
    "um",
    "uh",
    "like",
    "you know",
    "sort of",
    "kind of",
    "basically",
    "actually",
    "literally",
    "just",
}

TECHNICAL_TERMS = {
    "catch",
    "finish",
    "drive",
    "recovery",
    "legs",
    "swing",
    "body",
    "arms",
    "set",
    "send",
    "length",
    "ratio",
    "blade",
    "square",
    "feather",
    "split",
    "rate",
    "rhythm",
    "pressure",
}

TACTICAL_TERMS = {
    "seat",
    "bow ball",
    "walk",
    "move",
    "through",
    "open water",
    "inside",
    "outside",
    "line",
    "current",
    "wind",
    "wake",
    "500",
    "750",
    "1000",
    "last",
}

MOTIVATIONAL_TERMS = {
    "trust",
    "commit",
    "together",
    "believe",
    "now",
    "fight",
    "empty",
    "go",
    "send",
    "hold",
    "breathe",
}

COMMAND_PATTERNS: dict[str, re.Pattern[str]] = {
    "power_10": re.compile(r"\b(power|move|push)\s*(ten|10)\b", re.I),
    "rate_shift": re.compile(r"\b(rate|shift|up|bring it|take it)\s*(?:to|up)?\s*(\d{2})\b", re.I),
    "settle": re.compile(r"\b(settle|base|lengthen|race rhythm)\b", re.I),
    "sprint": re.compile(r"\b(sprint|last\s*500|empty|all out|finish it)\b", re.I),
    "technical": re.compile(r"\b(catch|finish|legs|swing|set|ratio|blade|send|length)\b", re.I),
}


@dataclass(frozen=True)
class TranscriptMetrics:
    word_count: int
    sentence_count: int
    estimated_call_count: int
    filler_count: int
    filler_rate_per_100_words: float
    technical_term_count: int
    tactical_term_count: int
    motivational_term_count: int
    detected_commands: dict[str, int]
    top_words: list[tuple[str, int]]


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _words(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z']+", text.lower())


def _count_terms(text: str, terms: Iterable[str]) -> int:
    text_norm = _normalize(text)
    total = 0
    for term in terms:
        total += len(re.findall(rf"\b{re.escape(term)}\b", text_norm))
    return total


def estimate_call_count(text: str) -> int:
    # For MVP purposes, treat sentence-like chunks and short command chunks as calls.
    chunks = [chunk.strip() for chunk in re.split(r"[.!?;\n]+", text) if chunk.strip()]
    comma_chunks = [chunk.strip() for chunk in re.split(r",", text) if chunk.strip()]
    return max(len(chunks), min(len(comma_chunks), max(1, len(_words(text)) // 8)))


def extract_transcript_metrics(text: str) -> TranscriptMetrics:
    words = _words(text)
    word_count = len(words)
    sentence_count = max(1, len([s for s in re.split(r"[.!?\n]+", text) if s.strip()])) if text.strip() else 0
    filler_count = _count_terms(text, FILLER_WORDS)
    detected_commands = {
        name: len(pattern.findall(text)) for name, pattern in COMMAND_PATTERNS.items()
    }
    meaningful_words = [w for w in words if len(w) > 3 and w not in FILLER_WORDS]
    top_words = Counter(meaningful_words).most_common(8)
    return TranscriptMetrics(
        word_count=word_count,
        sentence_count=sentence_count,
        estimated_call_count=estimate_call_count(text),
        filler_count=filler_count,
        filler_rate_per_100_words=round(100 * filler_count / max(1, word_count), 2),
        technical_term_count=_count_terms(text, TECHNICAL_TERMS),
        tactical_term_count=_count_terms(text, TACTICAL_TERMS),
        motivational_term_count=_count_terms(text, MOTIVATIONAL_TERMS),
        detected_commands=detected_commands,
        top_words=top_words,
    )


def metrics_to_dict(metrics: TranscriptMetrics) -> dict[str, object]:
    return {
        "word_count": metrics.word_count,
        "sentence_count": metrics.sentence_count,
        "estimated_call_count": metrics.estimated_call_count,
        "filler_count": metrics.filler_count,
        "filler_rate_per_100_words": metrics.filler_rate_per_100_words,
        "technical_term_count": metrics.technical_term_count,
        "tactical_term_count": metrics.tactical_term_count,
        "motivational_term_count": metrics.motivational_term_count,
        "detected_commands": metrics.detected_commands,
        "top_words": metrics.top_words,
    }
