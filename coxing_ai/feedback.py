"""Feedback generation for CoxingCoachAI."""

from __future__ import annotations

import json
import os
from typing import Any

from .audio_features import extract_transcript_metrics, metrics_to_dict
from .core import FOCUS_AREAS, PHASE_GUIDANCE


class FeedbackError(RuntimeError):
    """Raised when feedback generation fails."""


def resolve_focus_areas(selected: list[str] | None) -> dict[str, str]:
    if not selected:
        return FOCUS_AREAS.copy()
    return {key: FOCUS_AREAS[key] for key in selected if key in FOCUS_AREAS}


def build_feedback_prompt(
    transcript: str,
    selected_focus: list[str] | None,
    scenario: dict[str, Any],
    metrics: dict[str, Any],
    telemetry_summary: dict[str, Any] | None = None,
) -> str:
    focus = resolve_focus_areas(selected_focus)
    return f"""
You are an expert rowing coxswain coach. Give post-race feedback to a coxswain.

Important behavior:
- Only evaluate the selected focus areas. If all areas are provided, give general feedback.
- Prioritize transcript accuracy concerns and mention if feedback depends on improving transcript quality.
- Be specific, concrete, and coachable.
- Do not invent video-based observations. This MVP has audio/transcript and simulated telemetry only.
- Use an encouraging but honest tone.
- Include practice drills the coxswain can do off the water.

Selected focus areas:
{json.dumps(focus, indent=2)}

Scenario:
{json.dumps(scenario, indent=2)}

Phase guidance:
{json.dumps(PHASE_GUIDANCE, indent=2)}

Transcript metrics:
{json.dumps(metrics, indent=2)}

Telemetry summary:
{json.dumps(telemetry_summary or {}, indent=2)}

Transcript:
{transcript}

Return markdown with these sections:
1. Overall read
2. What worked
3. What to improve, grouped only by selected focus area
4. Three concrete rewrite examples using the user's own call style
5. Off-water practice drill
6. Next recording checklist
""".strip()


def _get_openai_key() -> str | None:
    return os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_KEY")


def generate_llm_feedback(
    transcript: str,
    selected_focus: list[str] | None,
    scenario: dict[str, Any],
    telemetry_summary: dict[str, Any] | None = None,
    api_key: str | None = None,
    model: str | None = None,
) -> str:
    api_key = api_key or _get_openai_key()
    if not api_key:
        raise FeedbackError("No OpenAI API key configured.")

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise FeedbackError("Install the OpenAI package with `pip install openai`.") from exc

    metrics = metrics_to_dict(extract_transcript_metrics(transcript))
    prompt = build_feedback_prompt(transcript, selected_focus, scenario, metrics, telemetry_summary)
    client = OpenAI(api_key=api_key)
    feedback_model = model or os.getenv("OPENAI_FEEDBACK_MODEL", "gpt-4o-mini")

    response = client.chat.completions.create(
        model=feedback_model,
        messages=[
            {"role": "system", "content": "You are a precise, supportive rowing coxswain coach."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content or ""


def generate_rule_based_feedback(
    transcript: str,
    selected_focus: list[str] | None,
    scenario: dict[str, Any],
    telemetry_summary: dict[str, Any] | None = None,
) -> str:
    metrics = extract_transcript_metrics(transcript)
    focus = resolve_focus_areas(selected_focus)
    lines: list[str] = []
    lines.append("## Overall read")
    if not transcript.strip():
        lines.append("No transcript was provided, so feedback is limited. Upload or record audio, or paste a transcript for testing.")
        return "\n\n".join(lines)
    lines.append(
        f"The recording has about **{metrics.word_count} words** across roughly **{metrics.estimated_call_count} call chunks**. "
        f"Detected commands include: {metrics.detected_commands}."
    )

    lines.append("## What worked")
    if metrics.technical_term_count:
        lines.append(f"- You used rowing-specific technical language {metrics.technical_term_count} times, which helps rowers connect calls to execution.")
    if metrics.motivational_term_count:
        lines.append(f"- You included motivational or unifying language {metrics.motivational_term_count} times, which can help create commitment under pressure.")
    if metrics.detected_commands.get("power_10", 0):
        lines.append("- At least one power-10 style move was detected, giving the crew a clear action window.")
    if len(lines) == 3:
        lines.append("- The transcript gives enough material to start identifying communication habits.")

    lines.append("## What to improve")
    for key, label in focus.items():
        if key == "communication_clarity":
            if metrics.filler_rate_per_100_words > 3:
                lines.append(f"### {label}\nReduce filler. Current estimate: **{metrics.filler_rate_per_100_words} fillers per 100 words**. Replace filler with silence or one-word rhythm calls.")
            else:
                lines.append(f"### {label}\nFiller is not the main issue. Next improvement: make each call follow a compact pattern: cue, action, reason.")
        elif key == "tone":
            lines.append(f"### {label}\nMark race phases more clearly. Use calm clinical language during base pace, sharper language during moves, and intense but controlled language in the sprint.")
        elif key == "technical_calls":
            lines.append(f"### {label}\nTie technical calls to the stroke cycle. Example: instead of only saying 'send it,' specify 'legs send' or 'clean finishes' when that is the intended technical change.")
        elif key == "rhythm_timing":
            lines.append(f"### {label}\nThis MVP cannot yet verify catch/finish timing without audio-event detection. For now, practice placing short calls on consistent beats and record against a metronome or oarlock audio track.")
        elif key == "rate_management":
            lines.append(f"### {label}\nWhen shifting rate, state the target and the transition window: 'In two, shift thirty-four.' Then confirm: 'Now hold thirty-four.'")
        elif key == "tactical_awareness":
            lines.append(f"### {label}\nAdd more external context when appropriate: where the opponent is, what move is being called, and why now is the right moment.")
        elif key == "psychological_calibration":
            lines.append(f"### {label}\nBuild trust by pairing high-pressure calls with controllable actions. Example: 'Trust the rhythm, legs together, now.'")

    lines.append("## Three concrete rewrite examples")
    lines.extend(
        [
            "1. Replace: 'Go, go, come on.' With: 'Legs now. One rhythm. Walk.'",
            "2. Replace: 'We need this.' With: 'In two, power ten for bow ball. One. Two. Now.'",
            "3. Replace: 'Keep it up.' With: 'Hold thirty-four. Clean catches. Send together.'",
        ]
    )

    lines.append("## Off-water practice drill")
    lines.append(
        "Run a 3-minute simulated race script. Use a metronome at your base rate, record yourself, then cut every phrase that does not give a cue, action, or tactical reason."
    )

    lines.append("## Next recording checklist")
    lines.extend(
        [
            "- Use a quiet room or headset mic.",
            "- Say the scenario before recording: distance, rate, base split, and focus area.",
            "- Record one full move sequence: setup, execution, confirmation.",
            "- After transcription, correct any rowing terms before accepting final feedback.",
        ]
    )
    return "\n".join(lines)


def generate_feedback(
    transcript: str,
    selected_focus: list[str] | None,
    scenario: dict[str, Any],
    telemetry_summary: dict[str, Any] | None = None,
    api_key: str | None = None,
    transcription_confidence_note: str | None = None,
) -> str:
    try:
        feedback = generate_llm_feedback(
            transcript=transcript,
            selected_focus=selected_focus,
            scenario=scenario,
            telemetry_summary=telemetry_summary,
            api_key=api_key,
        )
        if transcription_confidence_note:
            feedback += f"\n\n> Transcription note: {transcription_confidence_note}"
        return feedback
    except Exception as exc:
        fallback = generate_rule_based_feedback(transcript, selected_focus, scenario, telemetry_summary)
        return fallback + f"\n\n---\nRule-based fallback used because LLM feedback was unavailable: `{exc}`"
