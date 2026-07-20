from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from coxing_ai.audio_features import extract_transcript_metrics, metrics_to_dict
from coxing_ai.core import (
    DEFAULT_LOCAL_WHISPER_MODEL,
    DEFAULT_SCENARIO,
    FOCUS_AREAS,
    LOCAL_WHISPER_MODELS,
    MAX_LOCAL_AUDIO_MB,
    SUPPORTED_AUDIO_EXTENSIONS,
)
from coxing_ai.feedback import generate_feedback
from coxing_ai.simulator import simulate_race_from_transcript
from coxing_ai.transcription import (
    TranscriptionError,
    load_local_whisper_model,
    transcribe_audio_file,
)

st.set_page_config(
    page_title="CoxingCoachAI",
    page_icon="🚣",
    layout="wide",
)


@st.cache_resource(show_spinner=False, max_entries=1)
def get_cached_whisper_model(model_name: str) -> Any:
    """Load and cache one local model for the Streamlit server process."""
    return load_local_whisper_model(model_name)


def get_optional_openai_key() -> str | None:
    """Read an optional key for enhanced narrative feedback only."""
    env_value = os.getenv("OPENAI_API_KEY")
    if env_value:
        return env_value
    try:
        return st.secrets.get("openai", {}).get("api_key")
    except Exception:
        return None


def save_uploaded_audio(uploaded_file: Any) -> Path:
    suffix = Path(uploaded_file.name).suffix if getattr(uploaded_file, "name", None) else ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getvalue())
        return Path(tmp.name)


def scenario_form() -> dict[str, Any]:
    st.sidebar.header("Race scenario")
    distance = st.sidebar.selectbox("Race distance", [500, 1000, 1500, 2000, 5000], index=3)
    base_rate = st.sidebar.slider(
        "Base rate (SPM)", 18, 42, int(DEFAULT_SCENARIO["base_rate_spm"])
    )
    base_split = st.sidebar.slider(
        "Base split (sec / 500m)", 75, 180, int(DEFAULT_SCENARIO["base_split_seconds"])
    )
    crew_level = st.sidebar.selectbox(
        "Crew level", ["Novice", "Intermediate", "Varsity", "Elite"], index=1
    )
    boat_class = st.sidebar.selectbox("Boat class", ["8+", "4+", "4x+", "2+"], index=0)
    water_condition = st.sidebar.selectbox(
        "Water condition", ["Flat", "Light wind", "Choppy", "Headwind", "Tailwind"], index=0
    )
    race_phase = st.sidebar.selectbox(
        "Primary phase", ["Full 2k race", "Start", "Base pace", "Mid-race move", "Sprint"], index=0
    )
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


def model_selector() -> str:
    st.sidebar.header("Local transcription")
    labels = list(LOCAL_WHISPER_MODELS.keys())
    default_label = next(
        label
        for label, value in LOCAL_WHISPER_MODELS.items()
        if value == DEFAULT_LOCAL_WHISPER_MODEL
    )
    selected_label = st.sidebar.selectbox(
        "Whisper model",
        labels,
        index=labels.index(default_label),
        help=(
            "base.en is the recommended default. tiny.en is faster. small.en is "
            "more accurate but may be slow on free Streamlit hosting."
        ),
    )
    return LOCAL_WHISPER_MODELS[selected_label]


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


def display_transcription_result(result: dict[str, Any], key_prefix: str) -> None:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Model", result.get("model", "Unknown"))
    c2.metric("Language", str(result.get("language", "Unknown")).upper())
    probability = result.get("language_probability")
    c3.metric("Language confidence", f"{probability:.1%}" if probability is not None else "N/A")
    duration = result.get("duration_seconds")
    c4.metric("Audio duration", f"{duration:.1f} s" if duration is not None else "N/A")

    segments = result.get("segments") or []
    if segments:
        with st.expander("Timestamped transcription segments"):
            st.dataframe(pd.DataFrame(segments), use_container_width=True, hide_index=True)


def analyze_transcript(
    transcript: str,
    selected_focus: list[str],
    scenario: dict[str, Any],
    api_key: str | None,
    key_prefix: str,
) -> None:
    if not transcript.strip():
        st.warning("No speech was detected. Try a clearer recording or correct the transcript manually.")
        return

    st.subheader("Editable transcript")
    transcript = st.text_area(
        "Review and correct rowing terms before generating final feedback.",
        transcript,
        height=240,
        key=f"{key_prefix}_transcript_editor",
    )

    display_metrics(transcript)
    telemetry, events = simulate_race_from_transcript(transcript, scenario)

    st.subheader("Ideal-world simulated telemetry")
    c1, c2 = st.columns(2)
    with c1:
        st.caption("Stroke rate")
        st.line_chart(telemetry.set_index("meter")[["stroke_rate_spm"]])
    with c2:
        st.caption("Split; lower is faster")
        st.line_chart(telemetry.set_index("meter")[["split_seconds_per_500m"]])

    if not events.empty:
        with st.expander("Detected race events"):
            st.dataframe(events, use_container_width=True, hide_index=True)
    else:
        st.info("No explicit power-10, rate-shift, settle, or sprint event was detected.")

    telemetry_summary = {
        "min_split_seconds": float(telemetry["split_seconds_per_500m"].min()),
        "max_rate_spm": float(telemetry["stroke_rate_spm"].max()),
        "detected_event_count": int(len(events)),
    }

    st.subheader("Post-race feedback")
    if st.button("Generate feedback", type="primary", key=f"{key_prefix}_feedback_button"):
        with st.spinner("Generating focused coaching feedback..."):
            feedback = generate_feedback(
                transcript=transcript,
                selected_focus=selected_focus,
                scenario=scenario,
                telemetry_summary=telemetry_summary,
                api_key=api_key,
            )
        st.markdown(feedback)


def transcribe_widget_audio(
    uploaded_file: Any,
    model_name: str,
    state_key: str,
    button_label: str,
    button_key: str,
) -> None:
    if st.button(button_label, key=button_key):
        audio_path = save_uploaded_audio(uploaded_file)
        try:
            with st.spinner(
                f"Loading {model_name} and transcribing locally. The first run downloads the model..."
            ):
                model = get_cached_whisper_model(model_name)
                result = transcribe_audio_file(
                    audio_path,
                    model=model,
                    model_name=model_name,
                    source_name=getattr(uploaded_file, "name", None),
                )
            st.session_state[state_key] = result
            if result["text"]:
                st.success("Local transcription complete. No API key was used.")
            else:
                st.warning("Transcription completed, but no speech was detected.")
        except TranscriptionError as exc:
            st.error(str(exc))
        finally:
            try:
                audio_path.unlink(missing_ok=True)
            except Exception:
                pass


def main() -> None:
    st.title("CoxingCoachAI")
    st.caption(
        "Off-water coxswain practice with local AI transcription, focus-area feedback, "
        "and ideal-world race simulation."
    )

    scenario = scenario_form()
    selected_focus = focus_selector()
    model_name = model_selector()
    api_key = get_optional_openai_key()

    st.success(
        "Audio transcription runs locally with Faster-Whisper. No OPENAI_API_KEY is required."
    )
    st.info(
        "On free Streamlit hosting, the first transcription downloads the selected model and "
        "long recordings can take several minutes on CPU. Start with a short clip while testing."
    )
    if api_key:
        st.caption("Optional enhanced LLM feedback is enabled through Streamlit secrets.")
    else:
        st.caption("Feedback uses the included local, transparent coaching rules.")

    tab_upload, tab_record, tab_demo = st.tabs(
        ["Upload recording", "Simulated race recording", "Demo transcript"]
    )

    with tab_upload:
        st.header("Upload coxing audio")
        st.write(
            f"Supported extensions: {', '.join(sorted(SUPPORTED_AUDIO_EXTENSIONS))}. "
            f"Maximum app upload for local transcription: {MAX_LOCAL_AUDIO_MB} MB."
        )
        uploaded = st.file_uploader(
            "Upload a match or practice recording",
            type=sorted(SUPPORTED_AUDIO_EXTENSIONS),
            accept_multiple_files=False,
            key="uploaded_audio",
        )
        if uploaded:
            st.audio(uploaded)
            st.caption(f"File: {uploaded.name} | Size: {uploaded.size / (1024 * 1024):.2f} MB")
            transcribe_widget_audio(
                uploaded,
                model_name,
                "upload_result",
                "Transcribe uploaded audio locally",
                "upload_transcribe_button",
            )
        if "upload_result" in st.session_state:
            result = st.session_state["upload_result"]
            display_transcription_result(result, "upload")
            analyze_transcript(
                result["text"], selected_focus, scenario, api_key, "upload"
            )

    with tab_record:
        st.header("Record simulated race coxing")
        st.write(
            "Record a low-pressure practice call in your browser, then transcribe and analyze it."
        )
        recorded = st.audio_input(
            "Record your simulated race call",
            sample_rate=16000,
            key="recorded_audio",
        )
        typed = st.text_area(
            "Optional: paste or type a transcript for quick testing",
            height=160,
            key="typed_sim_transcript",
        )
        if recorded:
            st.audio(recorded)
            transcribe_widget_audio(
                recorded,
                model_name,
                "recorded_result",
                "Transcribe recorded session locally",
                "recorded_transcribe_button",
            )
        if typed.strip():
            analyze_transcript(typed, selected_focus, scenario, api_key, "typed")
        elif "recorded_result" in st.session_state:
            result = st.session_state["recorded_result"]
            display_transcription_result(result, "recorded")
            analyze_transcript(
                result["text"], selected_focus, scenario, api_key, "recorded"
            )

    with tab_demo:
        st.header("Demo transcript")
        sample = Path("sample_data/sample_transcript.txt")
        demo_text = sample.read_text(encoding="utf-8") if sample.exists() else ""
        analyze_transcript(demo_text, selected_focus, scenario, api_key, "demo")

    with st.expander("Current scope and future upgrades"):
        st.markdown(
            """
- Feedback is limited to the focus areas selected by the user; blank selection means general feedback.
- Local Faster-Whisper transcription is AI-based and does not require an external API key.
- The current simulator is ideal-world and transcript-command-based.
- Future versions can add catch/finish audio-event detection, oarlock and water sounds, a distance bar, 2D/3D shell animation, steering/video analysis, and user progress history.
            """
        )


if __name__ == "__main__":
    main()
