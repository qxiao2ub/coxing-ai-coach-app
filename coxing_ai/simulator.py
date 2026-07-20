"""Ideal-world race simulator for coxing calls."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class RaceEvent:
    meter: int
    event_type: str
    description: str
    rate_delta: float = 0.0
    split_delta: float = 0.0
    duration_m: int = 150


def _split_sentences(text: str) -> list[str]:
    chunks = re.split(r"[.!?\n]+", text)
    expanded: list[str] = []
    for chunk in chunks:
        expanded.extend([c.strip() for c in chunk.split(",") if c.strip()])
    return expanded or [text.strip()]


def extract_race_events(text: str, race_distance_m: int) -> list[RaceEvent]:
    chunks = _split_sentences(text)
    if not chunks or not text.strip():
        return []

    events: list[RaceEvent] = []
    for idx, chunk in enumerate(chunks):
        meter = int((idx / max(1, len(chunks) - 1)) * race_distance_m)
        lower = chunk.lower()

        power_match = re.search(r"\b(power|move|push)\s*(ten|10)\b", lower)
        if power_match:
            events.append(
                RaceEvent(
                    meter=meter,
                    event_type="power_10",
                    description="Power 10 detected; ideal-world split improves for the next segment.",
                    rate_delta=1.0,
                    split_delta=-2.0,
                    duration_m=250,
                )
            )

        rate_match = re.search(r"\b(?:rate|shift|up|take it|bring it)\s*(?:to|up)?\s*(\d{2})\b", lower)
        if rate_match:
            target_rate = float(rate_match.group(1))
            events.append(
                RaceEvent(
                    meter=meter,
                    event_type="rate_shift",
                    description=f"Rate shift detected toward {target_rate:.0f} spm.",
                    rate_delta=target_rate,  # interpreted as absolute target in simulator
                    split_delta=-1.0 if target_rate >= 34 else 0.5,
                    duration_m=300,
                )
            )

        if re.search(r"\b(settle|base|lengthen|race rhythm)\b", lower):
            events.append(
                RaceEvent(
                    meter=meter,
                    event_type="settle",
                    description="Settle/rhythm call detected; rate returns toward base while split stabilizes.",
                    rate_delta=0.0,
                    split_delta=0.0,
                    duration_m=300,
                )
            )

        if re.search(r"\b(sprint|last\s*500|empty|finish it|all out)\b", lower):
            events.append(
                RaceEvent(
                    meter=max(meter, int(race_distance_m * 0.75)),
                    event_type="sprint",
                    description="Sprint call detected; ideal-world rate and boat speed increase.",
                    rate_delta=3.0,
                    split_delta=-3.0,
                    duration_m=max(250, int(race_distance_m * 0.25)),
                )
            )
    return events


def _event_effect(event: RaceEvent, meter: int) -> tuple[float, float]:
    start = event.meter
    end = event.meter + event.duration_m
    if meter < start or meter > end:
        return 0.0, 0.0
    # Smooth decay through the event window.
    progress = (meter - start) / max(1, event.duration_m)
    strength = 0.35 + 0.65 * math.cos(progress * math.pi / 2)
    return event.rate_delta * strength, event.split_delta * strength


def simulate_race_from_transcript(
    transcript: str,
    scenario: dict[str, object] | None = None,
    step_m: int = 100,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    scenario = scenario or {}
    race_distance_m = int(scenario.get("race_distance_m", 2000))
    base_rate = float(scenario.get("base_rate_spm", 32))
    base_split = float(scenario.get("base_split_seconds", 105.0))

    events = extract_race_events(transcript, race_distance_m)
    meters = list(range(0, race_distance_m + 1, step_m))
    rows = []
    current_rate = base_rate

    for meter in meters:
        rate = base_rate
        split = base_split
        active_events = []
        for event in events:
            if event.event_type == "rate_shift" and event.meter <= meter <= event.meter + event.duration_m:
                rate = max(rate, float(event.rate_delta))
                split += event.split_delta
                active_events.append(event.event_type)
            elif event.event_type == "settle" and event.meter <= meter <= event.meter + event.duration_m:
                rate = base_rate
                active_events.append(event.event_type)
            else:
                rate_delta, split_delta = _event_effect(event, meter)
                rate += rate_delta
                split += split_delta
                if rate_delta or split_delta:
                    active_events.append(event.event_type)
        current_rate = 0.65 * current_rate + 0.35 * rate
        rows.append(
            {
                "meter": meter,
                "stroke_rate_spm": round(current_rate, 1),
                "split_seconds_per_500m": round(max(70.0, split), 1),
                "active_events": ", ".join(sorted(set(active_events))) or "base",
            }
        )

    telemetry = pd.DataFrame(rows)
    events_df = pd.DataFrame(
        [
            {
                "meter": event.meter,
                "event_type": event.event_type,
                "description": event.description,
                "duration_m": event.duration_m,
            }
            for event in events
        ]
    )
    return telemetry, events_df
