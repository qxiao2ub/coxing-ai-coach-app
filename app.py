from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from coxing_ai.audio_features import extract_transcript_metrics, metrics_to_dict
from coxing_ai.core import DEFAULT_SCENARIO, FOCUS_AREAS, MAX_API_AUDIO_MB, SUPPORTED_AUDIO_EXTENSIONS
from coxing_ai.feedback import generate_feedback
from coxing_ai.simulator import simulate_race_from_transcript
from coxing_ai.transcription import TranscriptionError, transcribe_audio_file

st.set_page_config(
    page_title="CoxingCoachAI MVP",
    page_icon="🚣",
    layout="wide",
)


def get_secret(name: str, default: str | None = None) -> str | None:
    # Supports both environment variables and Streamlit secrets.
    env_value = os.getenv(name)
    if env_value:
        return env_value
    try:
        if name == "OPENAI_API_KEY":
            return st.secrets.get("openai", {}).get("api_key", default)
        if name == "OPENAI_TRANSCRIPTION_MODEL":
            return st.secrets.get("openai", {}).get("transcription_model", default)
        if name == "OPENAI_FEEDBACK_MODEL":
            return st.secrets.get("openai", {}).get("feedback_model", default)
    except Exception:
        return default
    return default


def save_uploaded_audio(uploaded_file: Any) -> Path:
    suffix = Path(uploaded_file.name).suffix if getattr(uploaded_file, "name", None) else ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getvalue())
        return Path(tmp.name)


def scenario_form() -> dict[str, Any]:
    st.sidebar.header("Race scenario")
    distance = st.sidebar.selectbox("Race distance", [500, 1000, 1500, 2000, 5000], index=3)
    base_rate = st.sidebar.slider("Base rate (SPM)", min_value=18, max_value=42, value=int(DEFAULT_SCENARIO["base_rate_spm"]))
    base_split = st.sidebar.slider("Base split (sec / 500m)", min_value=75, max_value=180, value=int(DEFAULT_SCENARIO["base_split_seconds"]))
    crew_level = st.sidebar.selectbox("Crew level", ["Novice", "Intermediate", "Varsity", "Elite"], index=1)
    boat_class = st.sidebar.selectbox("Boat class", ["8+", "4+", "4x+", "2+"], index=0)
    water_condition = st.sidebar.selectbox("Water condition", ["Flat", "Light wind", "Choppy", "Headwind", "Tailwind"], index=0)
    race_phase = st.sidebar.selectbox("Primary phase", ["Full 2k race", "Start", "Base pace", "Mid-race move", "Sprint"], index=0)
    return {
        "race_distance_m": distance,
        "base_rate_spm": base_rate,
        "base_split_seconds": float(base_split),
        "crew_level": crew_level,
        "boat_class": boat_class,
        "water_condition": water_condition,
        "race_phase": race_phase,
    }


def focus_selector() -> list[str]:
    st.sidebar.header("Feedback focus")
    selected_labels = st.sidebar.multiselect(
        "Select focus areas. Leave blank for general feedback.",
        options=list(FOCUS_AREAS.values()),
        default=[],
    )
    reverse_lookup = {label: key for key, label in FOCUS_AREAS.items()}
    return [reverse_lookup[label] for label in selected_labels]


def display_metrics(transcript: str) -> None:
    metrics = extract_transcript_metrics(transcript)
    data = metrics_to_dict(metrics)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Words", data["word_count"])
    c2.metric("Estimated calls", data["estimated_call_count"])
    c3.metric("Fillers / 100 words", data["filler_rate_per_100_words"])
    c4.metric("Technical terms", data["technical_term_count"])
    with st.expander("Transcript metrics"):
        st.json(data)


def analyze_transcript(transcript: str, selected_focus: list[str], scenario: dict[str, Any], api_key: str | None) -> None:
    if not transcript.strip():
        st.warning("No transcript is available yet.")
        return

    st.subheader("Editable transcript")
    transcript = st.text_area(
        "Review and correct the transcript before final feedback.",
        transcript,
        height=220,
        key="transcript_editor",
    )

    display_metrics(transcript)
    telemetry, events = simulate_race_from_transcript(transcript, scenario)

    st.subheader("Ideal-world simulated telemetry")
    c1, c2 = st.columns(2)
    with c1:
        st.line_chart(telemetry.set_index("meter")[["stroke_rate_spm"]])
    with c2:
        st.line_chart(telemetry.set_index("meter")[["split_seconds_per_500m"]])

    if not events.empty:
        with st.expander("Detected race events"):
            st.dataframe(events, use_container_width=True)
    else:
        st.info("No explicit power-10, rate-shift, settle, or sprint event was detected in the transcript.")

    telemetry_summary = {
        "min_split_seconds": float(telemetry["split_seconds_per_500m"].min()),
        "max_rate_spm": float(telemetry["stroke_rate_spm"].max()),
        "detected_event_count": int(len(events)),
    }

    st.subheader("Post-race feedback")
    if st.button("Generate feedback", type="primary"):
        with st.spinner("Generating feedback..."):
            feedback = generate_feedback(
                transcript=transcript,
                selected_focus=selected_focus,
                scenario=scenario,
                telemetry_summary=telemetry_summary,
                api_key=api_key,
            )
        st.markdown(feedback)


def main() -> None:
    st.title("CoxingCoachAI MVP")
    st.caption("Post-race AI feedback for coxswains, with upload, browser recording, focus-area selection, and ideal-world simulated race telemetry.")

    scenario = scenario_form()
    selected_focus = focus_selector()
    api_key = get_secret("OPENAI_API_KEY")
    transcription_model = get_secret("OPENAI_TRANSCRIPTION_MODEL", "gpt-4o-mini-transcribe")

    if not api_key:
        st.info(
            "No OpenAI API key is configured. You can still test the demo transcript and rule-based feedback, "
            "but real audio transcription requires a key in Streamlit secrets."
        )

    tab_upload, tab_record, tab_demo = st.tabs(["Upload recording", "Simulated race recording", "Demo transcript"])

    with tab_upload:
        st.header("Upload coxing audio")
        st.write(
            f"Supported MVP extensions: {', '.join(sorted(SUPPORTED_AUDIO_EXTENSIONS))}. "
            f"Keep API transcription files under {MAX_API_AUDIO_MB} MB."
        )
        uploaded = st.file_uploader(
            "Upload a match or practice recording",
            type=sorted(SUPPORTED_AUDIO_EXTENSIONS),
            accept_multiple_files=False,
        )
        if uploaded:
            st.audio(uploaded)
            if st.button("Transcribe uploaded audio"):
                audio_path = save_uploaded_audio(uploaded)
                try:
                    with st.spinner("Transcribing audio..."):
                        result = transcribe_audio_file(audio_path, api_key=api_key, model=transcription_model)
                    st.session_state["upload_transcript"] = result["text"]
                    st.success(f"Transcription complete with {result['model']}.")
                except TranscriptionError as exc:
                    st.error(str(exc))
                finally:
                    try:
                        audio_path.unlink(missing_ok=True)
                    except Exception:
                        pass
            if "upload_transcript" in st.session_state:
                analyze_transcript(st.session_state["upload_transcript"], selected_focus, scenario, api_key)

    with tab_record:
        st.header("Record simulated race coxing")
        st.write("Use this for low-pressure off-water practice. Record your race call, transcribe it, and compare it to the ideal-world simulation.")
        recorded = st.audio_input("Record your simulated race call", sample_rate=16000)
        typed = st.text_area("Optional: paste or type a transcript for quick testing", height=160, key="typed_sim_transcript")
        if recorded:
            st.audio(recorded)
            if st.button("Transcribe recorded session"):
                audio_path = save_uploaded_audio(recorded)
                try:
                    with st.spinner("Transcribing recorded session..."):
                        result = transcribe_audio_file(audio_path, api_key=api_key, model=transcription_model)
                    st.session_state["recorded_transcript"] = result["text"]
                    st.success(f"Transcription complete with {result['model']}.")
                except TranscriptionError as exc:
                    st.error(str(exc))
                finally:
                    try:
                        audio_path.unlink(missing_ok=True)
                    except Exception:
                        pass
        if typed.strip():
            analyze_transcript(typed, selected_focus, scenario, api_key)
        elif "recorded_transcript" in st.session_state:
            analyze_transcript(st.session_state["recorded_transcript"], selected_focus, scenario, api_key)

    with tab_demo:
        st.header("Demo transcript")
        sample = Path("sample_data/sample_transcript.txt")
        demo_text = sample.read_text(encoding="utf-8") if sample.exists() else ""
        analyze_transcript(demo_text, selected_focus, scenario, api_key)

    with st.expander("MVP notes"):
        st.markdown(
            """
- Feedback only uses selected focus areas. If none are selected, all focus areas are used.
- The current simulator is ideal-world and transcript-command-based.
- Future versions can add catch/finish audio detection, oarlock/water sound tracks, distance bars, 2D/3D shell animation, and more realistic crew response models.
            """
        )


if __name__ == "__main__":
    main()
