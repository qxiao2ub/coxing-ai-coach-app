# CoxingCoachAI

**AI-powered off-water coxswain training** with a Streamlit interface migrated from the supplied **GLIDE Morning Lake** UI package.

**Author:** Julia Hu

Live app: https://coxing-ai-coach.streamlit.app/  
GitHub: https://github.com/qxiao2ub/coxing-ai-coach-app

## What is included

- Morning Lake GLIDE UI migrated into Streamlit with the supplied rowing-lake imagery, light glassmorphism cards, blue/ice accents, outing summary, recent-session cards, live-rate visualization, and responsive styling.
- The complete supplied UI source is preserved under `ui_reference/glide-code-original/` for design traceability.
- Local Faster-Whisper transcription for `.m4a`, `.wav`, `.mp3`, `.webm`, `.mp4`, `.mpeg`, and `.mpga`.
- No OpenAI API key required for transcription or built-in rule-based coaching.
- Browser microphone recording with `st.audio_input`.
- Editable transcript review before analysis.
- User-selected coaching focus areas; leaving the selection blank produces general feedback.
- Rowing command/event detection and transcript metrics.
- Ideal-world race simulation for power 10s, rate shifts, settles, sprints, stroke rate, and split response.
- Post-race focused feedback.
- A visible cumulative app-visitor count in the header, training tabs, quick-start panel, floating badge, and footer.
- Author-only public credit: **Julia Hu**.

## Visitor counter: no database

The repository contains two counter modes:

1. **Persistent GitHub-file mode — recommended for deployment.** The app stores the count in `data/visitor_count.json` on a separate `usage-data` branch. This is not a database and avoids changing the deployed `main` branch on each visit.
2. **Local-file fallback.** If no GitHub token is configured, the app still counts visits in a local JSON file. This survives normal Streamlit reruns, but Streamlit Community Cloud can recreate its container, so local-only storage cannot guarantee a never-reset total.

### Enable the persistent never-reset mode

Create a **fine-grained GitHub personal access token** restricted to the `qxiao2ub/coxing-ai-coach-app` repository with **Contents: Read and write** permission. Then add the following to **Streamlit Community Cloud → App settings → Secrets**:

```toml
[github_counter]
token = "github_pat_..."
repo = "qxiao2ub/coxing-ai-coach-app"
path = "data/visitor_count.json"
branch = "usage-data"
source_branch = "main"
```

The app automatically creates `usage-data` from `main` the first time persistent counting is used. It increments once per new Streamlit browser session rather than on every widget rerun.

## Streamlit deployment

1. Extract this ZIP.
2. Upload the **contents of the extracted folder** to the root of `qxiao2ub/coxing-ai-coach-app`.
3. Confirm `app.py`, `requirements.txt`, `.streamlit/`, `coxing_ai/`, `assets/`, and `data/` are at the repository root.
4. In Streamlit Community Cloud, use `app.py` as the main file.
5. Local transcription works without secrets.
6. Add the `[github_counter]` secret above if you want the cumulative count to persist through Streamlit container replacement.
7. The first transcription can take longer because Faster-Whisper downloads the selected model.

## Architecture

```text
Browser / Streamlit Morning Lake UI
        |
        +--> Visitor session
        |       |
        |       +--> GitHub usage-data JSON counter (persistent, no DB)
        |       +--> local JSON fallback
        |
        +--> Uploaded audio or browser recording
                  |
                  +--> Local Faster-Whisper speech-to-text
                              |
                              +--> Editable transcript
                                      |
                              Transcript metrics
                                      |
                              Coxing event detector
                                      |
                              Ideal-world simulator
                              /                 \
                   Stroke-rate telemetry     Split telemetry
                              \                 /
                               Focus-constrained
                               post-race feedback
```

## Local run

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Optional enhanced narrative feedback

The app works without an OpenAI API key. If you later want the optional LLM narrative path:

```toml
[openai]
api_key = "YOUR_KEY_HERE"
```

Never commit a real token or API key to GitHub.

## Repository layout

```text
.
├── app.py
├── requirements.txt
├── README.md
├── DEPLOYMENT_CHECKLIST.md
├── UI_MIGRATION_NOTES.md
├── secrets_template.toml
├── .streamlit/
│   └── config.toml
├── assets/
│   ├── rowing-lake.jpg
│   └── favicon.ico
├── coxing_ai/
│   ├── audio_features.py
│   ├── core.py
│   ├── feedback.py
│   ├── simulator.py
│   ├── transcription.py
│   └── visitor_counter.py
├── data/
│   └── visitor_count.json
├── notebooks/
│   └── CoxingCoachAI_Local_Whisper.ipynb
├── sample_data/
│   └── sample_transcript.txt
└── ui_reference/
    ├── index.tsx
    ├── styles.css
    └── glide-code-original/   # complete supplied UI source package
```

## Current modeling assumption

The simulator intentionally uses the project’s ideal-world assumption: recognized coxing calls cause simulated performance changes rather than being validated against real boat sensors. Future versions can replace these assumptions with CoxBox telemetry, acoustic cadence detection, steering/video analysis, and longitudinal athlete/session data.
