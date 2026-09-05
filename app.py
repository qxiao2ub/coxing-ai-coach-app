from __future__ import annotations

import base64
import os
import tempfile
from html import escape
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
    page_title="GLIDE | AI Coxing Coach | Julia Hu",
    page_icon="🚣",
    layout="wide",
    initial_sidebar_state="collapsed",
)

APP_ROOT = Path(__file__).resolve().parent
LAKE_IMAGE = APP_ROOT / "assets" / "rowing-lake.jpg"


@st.cache_resource(show_spinner=False, max_entries=1)
def get_cached_whisper_model(model_name: str) -> Any:
    """Load and cache one local Faster-Whisper model per server process."""
    return load_local_whisper_model(model_name)


def get_optional_openai_key() -> str | None:
    """Read an optional API key for enhanced narrative feedback only."""
    env_value = os.getenv("OPENAI_API_KEY")
    if env_value:
        return env_value
    try:
        return st.secrets.get("openai", {}).get("api_key")
    except Exception:
        return None


def image_data_uri(path: Path) -> str:
    if not path.exists():
        return ""
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"


def format_split(seconds: float) -> str:
    seconds = max(0.0, float(seconds))
    minutes = int(seconds // 60)
    remainder = int(round(seconds - minutes * 60))
    if remainder == 60:
        minutes += 1
        remainder = 0
    return f"{minutes}:{remainder:02d}"


def inject_glide_css() -> None:
    st.markdown(
        """
<style>
:root {
  --glide-bg: #07323c;
  --glide-bg-deep: #041f28;
  --glide-frost: rgba(10, 72, 82, 0.66);
  --glide-frost-strong: rgba(12, 82, 94, 0.82);
  --glide-line: rgba(95, 208, 255, 0.20);
  --glide-line-strong: rgba(95, 208, 255, 0.42);
  --glide-ice: #5fd0ff;
  --glide-ink: #f7f1e8;
  --glide-muted: #9bc4c6;
  --glide-green: #76e6c0;
}

html, body, [class*="css"] {
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.stApp,
[data-testid="stAppViewContainer"] {
  color: var(--glide-ink);
  background:
    radial-gradient(80% 60% at 82% -8%, rgba(95, 208, 255, 0.18), transparent 55%),
    radial-gradient(75% 55% at 6% 112%, rgba(44, 72, 103, 0.58), transparent 60%),
    linear-gradient(155deg, #07323c 0%, #062c37 50%, #041f28 100%);
  background-attachment: fixed;
}

[data-testid="stHeader"] {
  background: transparent;
}

[data-testid="stToolbar"] {
  opacity: 0.25;
}

section[data-testid="stSidebar"] {
  display: none;
}

.block-container {
  max-width: 1180px;
  padding-top: 1.05rem;
  padding-bottom: 2rem;
}

h1, h2, h3, h4 {
  letter-spacing: -0.02em;
}

p, label, .stMarkdown, [data-testid="stCaptionContainer"] {
  color: var(--glide-ink);
}

[data-testid="stCaptionContainer"] p,
.stCaption,
small {
  color: var(--glide-muted) !important;
}

.glide-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 10px 2px 20px 2px;
}

.glide-brand {
  display: flex;
  align-items: center;
  gap: 13px;
  min-width: 270px;
}

.glide-logo {
  width: 42px;
  height: 42px;
  display: grid;
  place-items: center;
  border-radius: 14px;
  background: linear-gradient(145deg, rgba(14, 86, 98, 0.95), rgba(7, 50, 60, 0.95));
  border: 1px solid var(--glide-line);
  box-shadow: inset 0 1px 0 rgba(255,255,255,.08), 0 12px 28px rgba(0,0,0,.20);
  color: var(--glide-ice);
  font-size: 21px;
  font-weight: 800;
}

.glide-brand-name {
  font-size: 24px;
  font-weight: 800;
  letter-spacing: .08em;
  line-height: 1;
}

.glide-kicker,
.glide-nav,
.glide-status,
.glide-eyebrow,
.glide-mini-label,
.glide-footer {
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
  text-transform: uppercase;
  letter-spacing: .16em;
}

.glide-kicker {
  margin-top: 5px;
  font-size: 10px;
  color: var(--glide-muted);
}

.glide-nav {
  display: flex;
  gap: 24px;
  font-size: 10px;
  color: var(--glide-muted);
  white-space: nowrap;
}

.glide-nav span:first-child {
  color: var(--glide-ice);
}

.glide-status {
  display: flex;
  align-items: center;
  gap: 9px;
  font-size: 10px;
  color: var(--glide-muted);
  white-space: nowrap;
}

.glide-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: var(--glide-ice);
  box-shadow: 0 0 0 5px rgba(95,208,255,.08), 0 0 22px rgba(95,208,255,.55);
  animation: glide-breathe 1.8s ease-in-out infinite;
}

@keyframes glide-breathe {
  0%,100% { opacity:.55; transform:scale(1); }
  50% { opacity:1; transform:scale(1.15); }
}

@keyframes glide-rise {
  from { opacity:0; transform:translateY(12px); }
  to { opacity:1; transform:none; }
}

.glide-card {
  position: relative;
  overflow: hidden;
  border-radius: 26px;
  border: 1px solid var(--glide-line);
  background: linear-gradient(145deg, rgba(11, 76, 87, .66), rgba(7, 48, 59, .56));
  box-shadow: 0 22px 60px rgba(0,0,0,.20), inset 0 1px 0 rgba(255,255,255,.045);
  backdrop-filter: blur(18px);
  animation: glide-rise .65s cubic-bezier(.22,.61,.36,1) both;
}

.glide-card::before {
  content:"";
  position:absolute;
  top:0; left:0; right:0;
  height:1px;
  background:linear-gradient(90deg, transparent, rgba(95,208,255,.72), transparent);
}

.glide-card-pad {
  padding: 22px;
}

.glide-coach-head {
  display:flex;
  gap:12px;
  align-items:center;
}

.glide-avatar {
  width:42px;
  height:42px;
  display:grid;
  place-items:center;
  border-radius:999px;
  background:rgba(95,208,255,.12);
  border:1px solid rgba(95,208,255,.28);
  color:var(--glide-ice);
  font-weight:800;
  font-size:18px;
}

.glide-title {
  font-size:16px;
  font-weight:750;
  line-height:1.1;
}

.glide-eyebrow {
  margin-top:4px;
  font-size:9px;
  color:var(--glide-ice);
}

.glide-time {
  margin-left:auto;
  font-family:"SFMono-Regular", Consolas, monospace;
  color:var(--glide-muted);
  font-size:9px;
  text-transform:uppercase;
  letter-spacing:.13em;
}

.glide-chat {
  margin-top:18px;
  display:grid;
  gap:11px;
}

.glide-bubble {
  max-width:92%;
  padding:12px 14px;
  border-radius:17px;
  font-size:13px;
  line-height:1.58;
  color:rgba(247,241,232,.92);
}

.glide-bubble.user {
  margin-left:auto;
  max-width:84%;
  background:rgba(95,208,255,.10);
  border-bottom-right-radius:5px;
}

.glide-bubble.coach {
  background:rgba(47, 112, 119, .25);
  border-bottom-left-radius:5px;
}

.glide-accent { color:var(--glide-ice); font-weight:700; }

.glide-listening {
  margin-top:17px;
  padding:12px 14px;
  border-radius:16px;
  border:1px solid var(--glide-line);
  background:rgba(3,31,39,.36);
  font-family:"SFMono-Regular", Consolas, monospace;
  font-size:10px;
  text-transform:uppercase;
  letter-spacing:.13em;
  color:var(--glide-muted);
}

.glide-chip-row {
  display:flex;
  flex-wrap:wrap;
  gap:8px;
  margin-top:13px;
}

.glide-chip {
  padding:7px 11px;
  border-radius:999px;
  background:rgba(54,119,127,.24);
  border:1px solid rgba(95,208,255,.09);
  color:rgba(247,241,232,.82);
  font-size:11px;
}

.glide-section-head {
  display:flex;
  align-items:flex-end;
  justify-content:space-between;
  gap:15px;
  margin-bottom:14px;
}

.glide-section-head h2 {
  margin:3px 0 0 0;
  font-size:28px;
  line-height:1;
  color:var(--glide-ink);
}

.glide-mini-label {
  font-size:9px;
  color:var(--glide-muted);
}

.glide-reviewed {
  color:var(--glide-ice);
  font-family:"SFMono-Regular", Consolas, monospace;
  text-transform:uppercase;
  letter-spacing:.12em;
  font-size:9px;
}

.glide-stat-grid {
  display:grid;
  grid-template-columns:repeat(3, 1fr);
  gap:10px;
}

.glide-stat {
  padding:12px;
  border-radius:14px;
  background:rgba(3,31,39,.32);
  border:1px solid var(--glide-line);
}

.glide-stat .value {
  margin-top:4px;
  font-size:24px;
  font-weight:780;
}

.glide-stat .unit {
  color:var(--glide-muted);
  font-size:11px;
  font-weight:500;
}

.glide-lake {
  width:100%;
  height:215px;
  object-fit:cover;
  margin-top:13px;
  border-radius:17px;
  border:1px solid rgba(255,255,255,.05);
  filter:saturate(.84) contrast(1.03) brightness(.88);
}

.glide-side-card {
  padding:18px;
  border-radius:24px;
  border:1px solid var(--glide-line);
  background:rgba(9,70,80,.55);
  box-shadow:0 18px 45px rgba(0,0,0,.18);
  margin-bottom:14px;
}

.glide-session-row {
  display:flex;
  align-items:center;
  gap:10px;
  padding:10px;
  margin-top:8px;
  border-radius:15px;
  background:rgba(3,31,39,.32);
  border:1px solid rgba(95,208,255,.11);
}

.glide-session-icon {
  width:36px;
  height:36px;
  border-radius:12px;
  display:grid;
  place-items:center;
  background:rgba(95,208,255,.10);
  color:var(--glide-ice);
  font-weight:800;
}

.glide-session-title { font-size:12px; font-weight:700; }
.glide-session-meta { margin-top:2px; color:var(--glide-muted); font-size:9px; font-family:monospace; text-transform:uppercase; letter-spacing:.08em; }
.glide-arrow { margin-left:auto; color:var(--glide-muted); }

.glide-live {
  display:flex;
  align-items:flex-end;
  justify-content:space-between;
  min-height:105px;
}

.glide-bars {
  height:80px;
  display:flex;
  gap:6px;
  align-items:flex-end;
}

.glide-bar {
  width:8px;
  border-radius:999px;
  background:rgba(80,150,156,.48);
}

.glide-bar.hot {
  background:var(--glide-ice);
  box-shadow:0 0 20px rgba(95,208,255,.38);
}

.glide-rate {
  font-size:43px;
  font-weight:850;
  line-height:1;
  text-align:right;
}

.glide-rate-label {
  margin-top:4px;
  color:var(--glide-ice);
  font-family:monospace;
  text-transform:uppercase;
  letter-spacing:.12em;
  font-size:9px;
}

/* Native Streamlit glass panels */
div[data-testid="stVerticalBlockBorderWrapper"] {
  background:linear-gradient(145deg, rgba(11,76,87,.66), rgba(7,48,59,.58));
  border:1px solid var(--glide-line) !important;
  border-radius:26px !important;
  box-shadow:0 22px 60px rgba(0,0,0,.19), inset 0 1px 0 rgba(255,255,255,.04);
  backdrop-filter:blur(18px);
}

[data-testid="stMetric"] {
  background:rgba(3,31,39,.26);
  border:1px solid rgba(95,208,255,.12);
  border-radius:15px;
  padding:12px 14px;
}

[data-testid="stMetricLabel"] { color:var(--glide-muted); }
[data-testid="stMetricValue"] { color:var(--glide-ink); }

.stButton > button,
.stDownloadButton > button {
  border-radius:14px !important;
  border:1px solid rgba(95,208,255,.42) !important;
  background:linear-gradient(135deg, #69dafd, #42bfe8) !important;
  color:#04232b !important;
  font-weight:800 !important;
  box-shadow:0 10px 28px rgba(16,171,220,.17);
}

.stButton > button:hover,
.stDownloadButton > button:hover {
  border-color:#8ce5ff !important;
  filter:brightness(1.05);
}

[data-baseweb="select"] > div,
[data-baseweb="input"] > div,
textarea,
[data-testid="stFileUploaderDropzone"],
[data-testid="stAudioInput"] {
  background:rgba(3,31,39,.40) !important;
  border-color:rgba(95,208,255,.18) !important;
  border-radius:15px !important;
  color:var(--glide-ink) !important;
}

[data-testid="stFileUploaderDropzone"] {
  border-style:dashed !important;
}

[data-baseweb="tag"] {
  background:rgba(95,208,255,.13) !important;
  color:var(--glide-ink) !important;
  border:1px solid rgba(95,208,255,.18) !important;
}

button[data-baseweb="tab"] {
  color:var(--glide-muted) !important;
  font-family:monospace !important;
  text-transform:uppercase;
  letter-spacing:.08em;
}

button[data-baseweb="tab"][aria-selected="true"] {
  color:var(--glide-ice) !important;
}

[data-baseweb="tab-highlight"] {
  background-color:var(--glide-ice) !important;
}

[data-testid="stExpander"] {
  border:1px solid rgba(95,208,255,.13) !important;
  border-radius:15px !important;
  background:rgba(3,31,39,.20);
}

[data-testid="stAlert"] {
  border-radius:16px;
  border:1px solid rgba(95,208,255,.15);
}

hr {
  border-color:rgba(95,208,255,.12) !important;
}

.glide-console-title {
  margin:24px 0 8px 0;
  padding:18px 20px;
  border-radius:22px;
  background:linear-gradient(90deg, rgba(95,208,255,.08), rgba(95,208,255,.02));
  border:1px solid rgba(95,208,255,.13);
}

.glide-console-title h2 { margin:0; font-size:29px; }
.glide-console-title p { margin:6px 0 0 0; color:var(--glide-muted); font-size:12px; }

.glide-footer {
  display:flex;
  flex-wrap:wrap;
  justify-content:space-between;
  gap:12px;
  padding:20px 2px 4px;
  margin-top:16px;
  border-top:1px solid rgba(95,208,255,.12);
  color:var(--glide-muted);
  font-size:9px;
}

@media (max-width: 850px) {
  .glide-nav { display:none; }
  .glide-status { display:none; }
  .glide-header { padding-bottom:12px; }
  .glide-stat-grid { grid-template-columns:1fr; }
  .glide-lake { height:170px; }
}
</style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    st.markdown(
        """
<div class="glide-header">
  <div class="glide-brand">
    <div class="glide-logo">G</div>
    <div>
      <div class="glide-brand-name">GLIDE</div>
      <div class="glide-kicker">CoxingCoachAI · Julia Hu · Advisor Dr. Qingyang Xiao</div>
    </div>
  </div>
  <div class="glide-nav"><span>Console</span><span>Sessions</span><span>Calls</span><span>Progress</span></div>
  <div class="glide-status"><span class="glide-dot"></span><span>On the water</span></div>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_coach_card() -> None:
    st.markdown(
        """
<div class="glide-card">
  <div class="glide-card-pad">
    <div class="glide-coach-head">
      <div class="glide-avatar">A</div>
      <div>
        <div class="glide-title">Coach Anders</div>
        <div class="glide-eyebrow">Ready · AI coxing coach</div>
      </div>
      <div class="glide-time">off-water lab</div>
    </div>
    <div class="glide-chat">
      <div class="glide-bubble user">We're running flat water at the lake. Walk me through a calm start to 32.</div>
      <div class="glide-bubble coach">Good. Set the body first — long and controlled to the catch. Count the build so the crew hears it: <span class="glide-accent">“Easy… easy… building at four.”</span> Then establish length before asking for more.</div>
      <div class="glide-bubble coach">At race rhythm, use a deliberate <span class="glide-accent">“Breathe.”</span> between calls. Let the boat find its glide, then make the next instruction matter.</div>
    </div>
    <div class="glide-listening">● &nbsp; Local AI is ready for your recording</div>
    <div class="glide-chip-row">
      <span class="glide-chip">Calm start</span><span class="glide-chip">Power 10</span><span class="glide-chip">Rate shift</span><span class="glide-chip">Settle</span><span class="glide-chip">Sprint</span>
    </div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def session_setup() -> tuple[dict[str, Any], list[str], str, str | None]:
    with st.container(border=True):
        st.markdown("### Session setup")
        st.caption("Configure the ideal-world race model and the feedback you want to improve.")

        distance = st.selectbox(
            "Race distance",
            [500, 1000, 1500, 2000, 5000],
            index=3,
            key="race_distance",
        )

        c1, c2 = st.columns(2)
        with c1:
            base_rate = st.slider(
                "Base rate (SPM)",
                18,
                42,
                int(DEFAULT_SCENARIO["base_rate_spm"]),
                key="base_rate",
            )
        with c2:
            base_split = st.slider(
                "Split (sec / 500m)",
                75,
                180,
                int(DEFAULT_SCENARIO["base_split_seconds"]),
                key="base_split",
            )

        selected_labels = st.multiselect(
            "Feedback focus",
            options=list(FOCUS_AREAS.values()),
            default=[],
            placeholder="Leave blank for general feedback",
            key="focus_areas",
        )
        reverse_lookup = {label: key for key, label in FOCUS_AREAS.items()}
        selected_focus = [reverse_lookup[label] for label in selected_labels]

        labels = list(LOCAL_WHISPER_MODELS.keys())
        default_label = next(
            label
            for label, value in LOCAL_WHISPER_MODELS.items()
            if value == DEFAULT_LOCAL_WHISPER_MODEL
        )
        selected_label = st.selectbox(
            "Local speech model",
            labels,
            index=labels.index(default_label),
            help="base.en is the balanced default. tiny.en is faster; small.en is more accurate but heavier.",
            key="whisper_model",
        )
        model_name = LOCAL_WHISPER_MODELS[selected_label]

        with st.expander("Crew & water configuration"):
            crew_level = st.selectbox(
                "Crew level",
                ["Novice", "Intermediate", "Varsity", "Elite"],
                index=1,
                key="crew_level",
            )
            boat_class = st.selectbox(
                "Boat class", ["8+", "4+", "4x+", "2+"], index=0, key="boat_class"
            )
            water_condition = st.selectbox(
                "Water condition",
                ["Flat", "Light wind", "Choppy", "Headwind", "Tailwind"],
                index=0,
                key="water_condition",
            )
            race_phase = st.selectbox(
                "Primary phase",
                ["Full 2k race", "Start", "Base pace", "Mid-race move", "Sprint"],
                index=0,
                key="race_phase",
            )

        api_key = get_optional_openai_key()
        if api_key:
            st.success("Local transcription + optional LLM narrative feedback enabled.")
        else:
            st.info("No API key needed: local Faster-Whisper + local coaching rules are active.")

    scenario = {
        "race_distance_m": distance,
        "base_rate_spm": base_rate,
        "base_split_seconds": float(base_split),
        "crew_level": crew_level,
        "boat_class": boat_class,
        "water_condition": water_condition,
        "race_phase": race_phase,
    }
    return scenario, selected_focus, model_name, api_key


def render_outing_card(scenario: dict[str, Any], selected_focus: list[str]) -> None:
    img = image_data_uri(LAKE_IMAGE)
    focus_text = str(len(selected_focus)) if selected_focus else "ALL"
    distance = int(scenario["race_distance_m"])
    split = format_split(float(scenario["base_split_seconds"]))
    rate = int(scenario["base_rate_spm"])
    water = escape(str(scenario["water_condition"]))
    crew = escape(str(scenario["crew_level"]))
    image_html = f'<img class="glide-lake" src="{img}" alt="Rowing shell gliding across a calm lake">' if img else ""

    st.markdown(
        f"""
<div class="glide-card" style="margin-top:4px;">
  <div class="glide-card-pad">
    <div class="glide-section-head">
      <div>
        <div class="glide-mini-label">Today's training profile</div>
        <h2>{water} water · {distance/1000:g}k</h2>
      </div>
      <div class="glide-reviewed">Ready · {crew}</div>
    </div>
    <div class="glide-stat-grid">
      <div class="glide-stat"><div class="glide-mini-label">Base rate</div><div class="value">{rate} <span class="unit">spm</span></div></div>
      <div class="glide-stat"><div class="glide-mini-label">Base split</div><div class="value">{split} <span class="unit">/500</span></div></div>
      <div class="glide-stat"><div class="glide-mini-label">Focus areas</div><div class="value">{focus_text} <span class="unit">selected</span></div></div>
    </div>
    {image_html}
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_recent_and_live(scenario: dict[str, Any]) -> None:
    rate = int(scenario["base_rate_spm"])
    normalized = max(0, min(100, (rate - 18) / 24 * 100))
    heights = [36, 49, 63, max(72, int(45 + normalized * 0.47)), 57, 31]
    bars = "".join(
        f'<div class="glide-bar {"hot" if i == 3 else ""}" style="height:{h}%"></div>'
        for i, h in enumerate(heights)
    )

    st.markdown(
        """
<div class="glide-side-card">
  <div class="glide-section-head" style="margin-bottom:8px;">
    <div class="glide-mini-label">Recent sessions</div><div class="glide-reviewed">3 examples</div>
  </div>
  <div class="glide-session-row"><div class="glide-session-icon">S</div><div><div class="glide-session-title">Sprint review · Headwater</div><div class="glide-session-meta">22m · 6 calls flagged</div></div><div class="glide-arrow">→</div></div>
  <div class="glide-session-row"><div class="glide-session-icon">C</div><div><div class="glide-session-title">Conditioning · Tempo row</div><div class="glide-session-meta">45m · transcript</div></div><div class="glide-arrow">→</div></div>
  <div class="glide-session-row"><div class="glide-session-icon">R</div><div><div class="glide-session-title">Race plan · Sectionals</div><div class="glide-session-meta">saved · 4k build</div></div><div class="glide-arrow">→</div></div>
</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
<div class="glide-side-card">
  <div class="glide-mini-label">Live crew target</div>
  <div class="glide-live">
    <div class="glide-bars">{bars}</div>
    <div><div class="glide-rate">{rate}</div><div class="glide-rate-label">target rate</div></div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def save_uploaded_audio(uploaded_file: Any) -> Path:
    suffix = Path(uploaded_file.name).suffix if getattr(uploaded_file, "name", None) else ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getvalue())
        return Path(tmp.name)


def display_metrics(transcript: str) -> None:
    metrics = extract_transcript_metrics(transcript)
    data = metrics_to_dict(metrics)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Words", data["word_count"])
    c2.metric("Estimated calls", data["estimated_call_count"])
    c3.metric("Fillers / 100", data["filler_rate_per_100_words"])
    c4.metric("Technical terms", data["technical_term_count"])

    commands = data.get("detected_commands", {})
    active = [name.replace("_", " ").title() for name, count in commands.items() if count]
    if active:
        st.caption("Detected call types · " + " · ".join(active))

    with st.expander("Detailed transcript metrics"):
        st.json(data)


def display_transcription_result(result: dict[str, Any]) -> None:
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

    st.markdown("#### Transcript & analysis")
    transcript = st.text_area(
        "Review and correct rowing terms before generating final feedback.",
        transcript,
        height=220,
        key=f"{key_prefix}_transcript_editor",
    )

    display_metrics(transcript)
    telemetry, events = simulate_race_from_transcript(transcript, scenario)

    st.markdown("#### Ideal-world race telemetry")
    c1, c2 = st.columns(2)
    with c1:
        st.caption("Stroke rate · SPM")
        st.line_chart(telemetry.set_index("meter")[["stroke_rate_spm"]])
    with c2:
        st.caption("Split · seconds / 500m · lower is faster")
        st.line_chart(telemetry.set_index("meter")[["split_seconds_per_500m"]])

    if not events.empty:
        with st.expander("Detected race events"):
            st.dataframe(events, use_container_width=True, hide_index=True)
    else:
        st.info("No explicit power-10, rate-shift, settle, or sprint event was detected in this transcript.")

    telemetry_summary = {
        "min_split_seconds": float(telemetry["split_seconds_per_500m"].min()),
        "max_rate_spm": float(telemetry["stroke_rate_spm"].max()),
        "detected_event_count": int(len(events)),
    }

    st.markdown("#### Post-race coaching")
    feedback_state_key = f"{key_prefix}_feedback"
    if st.button("Generate focused feedback", type="primary", key=f"{key_prefix}_feedback_button"):
        with st.spinner("Reviewing your calls, race phase, and selected focus areas..."):
            st.session_state[feedback_state_key] = generate_feedback(
                transcript=transcript,
                selected_focus=selected_focus,
                scenario=scenario,
                telemetry_summary=telemetry_summary,
                api_key=api_key,
            )

    if feedback_state_key in st.session_state:
        st.markdown(st.session_state[feedback_state_key])


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
                f"Loading {model_name} and transcribing locally. The first run may download the model..."
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
                st.success("Local transcription complete. No transcription API key was used.")
            else:
                st.warning("Transcription completed, but no speech was detected.")
        except TranscriptionError as exc:
            st.error(str(exc))
        finally:
            try:
                audio_path.unlink(missing_ok=True)
            except Exception:
                pass


def render_console(
    scenario: dict[str, Any],
    selected_focus: list[str],
    model_name: str,
    api_key: str | None,
) -> None:
    st.markdown(
        """
<div class="glide-console-title">
  <div class="glide-mini-label">Training console</div>
  <h2>Upload · Simulate · Analyze · Improve</h2>
  <p>Transcription runs locally with Faster-Whisper. Feedback is limited to your selected focus areas; leave focus blank for a full review.</p>
</div>
        """,
        unsafe_allow_html=True,
    )

    tab_upload, tab_record, tab_demo = st.tabs(
        ["Upload recording", "Simulated race", "Demo transcript"]
    )

    with tab_upload:
        with st.container(border=True):
            st.markdown("### Upload coxing audio")
            st.caption(
                f"Supported: {', '.join(sorted(SUPPORTED_AUDIO_EXTENSIONS))} · "
                f"Local upload limit: {MAX_LOCAL_AUDIO_MB} MB"
            )
            uploaded = st.file_uploader(
                "Drop a match or practice recording",
                type=sorted(SUPPORTED_AUDIO_EXTENSIONS),
                accept_multiple_files=False,
                key="uploaded_audio",
            )
            if uploaded:
                st.audio(uploaded)
                st.caption(f"{uploaded.name} · {uploaded.size / (1024 * 1024):.2f} MB")
                transcribe_widget_audio(
                    uploaded,
                    model_name,
                    "upload_result",
                    "Transcribe uploaded audio",
                    "upload_transcribe_button",
                )

            if "upload_result" in st.session_state:
                result = st.session_state["upload_result"]
                display_transcription_result(result)
                analyze_transcript(result["text"], selected_focus, scenario, api_key, "upload")

    with tab_record:
        with st.container(border=True):
            st.markdown("### Simulated race recording")
            st.caption("Practice in a low-pressure environment and analyze the call immediately afterward.")
            recorded = st.audio_input(
                "Record your simulated race call",
                sample_rate=16000,
                key="recorded_audio",
            )
            typed = st.text_area(
                "Or paste/type a transcript for rapid simulator testing",
                height=130,
                key="typed_sim_transcript",
            )
            if recorded:
                st.audio(recorded)
                transcribe_widget_audio(
                    recorded,
                    model_name,
                    "recorded_result",
                    "Transcribe recorded session",
                    "recorded_transcribe_button",
                )
            if typed.strip():
                analyze_transcript(typed, selected_focus, scenario, api_key, "typed")
            elif "recorded_result" in st.session_state:
                result = st.session_state["recorded_result"]
                display_transcription_result(result)
                analyze_transcript(result["text"], selected_focus, scenario, api_key, "recorded")

    with tab_demo:
        with st.container(border=True):
            st.markdown("### Demo transcript")
            st.caption("Try the full analysis pipeline without uploading an audio file.")
            sample = APP_ROOT / "sample_data" / "sample_transcript.txt"
            demo_text = sample.read_text(encoding="utf-8") if sample.exists() else ""
            analyze_transcript(demo_text, selected_focus, scenario, api_key, "demo")


def main() -> None:
    inject_glide_css()
    render_header()

    top_left, top_right = st.columns([7, 5], gap="medium")
    with top_left:
        render_coach_card()
    with top_right:
        scenario, selected_focus, model_name, api_key = session_setup()

    st.write("")
    lower_left, lower_right = st.columns([7, 5], gap="medium")
    with lower_left:
        render_outing_card(scenario, selected_focus)
    with lower_right:
        render_recent_and_live(scenario)

    render_console(scenario, selected_focus, model_name, api_key)

    with st.expander("Current scope & future upgrades"):
        st.markdown(
            """
- **Current AI:** local Faster-Whisper speech-to-text, transcript feature extraction, command/event detection, ideal-world telemetry simulation, and focus-constrained coaching feedback.
- **Current simulator:** power-10, rate-shift, settle, sprint, race-distance, stroke-rate, split, crew-level, boat-class, water-condition, and race-phase inputs.
- **Planned audio intelligence:** catch/finish timing, oarlock/water sound analysis, cadence synchronization, and richer prosody/tone analysis.
- **Planned visual intelligence:** distance meter, 2D/3D shell animation, steering/line analysis, tactical video understanding, and longitudinal progress history.
            """
        )

    st.markdown(
        """
<div class="glide-footer">
  <span>GLIDE · rhythm, breath, sync · CoxingCoachAI</span>
  <span>Author Julia Hu · Advisor Dr. Qingyang Xiao</span>
</div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
