# CoxingCoachAI

**AI-powered off-water coxswain training** with a Streamlit interface migrated from the supplied GLIDE / Deep Frost Command UI design.

**Author:** Julia Hu  
**Advisor:** Dr. Qingyang Xiao

Live-app target: https://coxing-ai-coach.streamlit.app/  
GitHub repository: https://github.com/qxiao2ub/coxing-ai-coach-app

## What this version includes

- GLIDE dark, glassmorphism-inspired rowing interface migrated to Streamlit.
- Local Faster-Whisper transcription for `.m4a`, `.wav`, `.mp3`, `.webm`, `.mp4`, `.mpeg`, and `.mpga` recordings.
- No `OPENAI_API_KEY` required for transcription or the built-in coaching mode.
- Browser microphone recording with `st.audio_input`.
- Editable transcript review before coaching analysis.
- User-selected focus areas; leaving the list blank produces general feedback.
- Transcript metrics and rowing-command detection.
- Ideal-world race simulator for power 10s, rate shifts, settles, and sprints.
- Stroke-rate and split telemetry charts.
- Optional OpenAI-powered narrative feedback if an API key is later configured.
- Author and advisor credits in the app and repository.

## Streamlit deployment

1. Extract this ZIP.
2. Upload the **contents of this folder** to the root of `qxiao2ub/coxing-ai-coach-app`.
3. Confirm the repository root contains `app.py`, `requirements.txt`, `.streamlit/`, `coxing_ai/`, and `assets/`.
4. In Streamlit Community Cloud, choose the repository and set the app entrypoint to `app.py`.
5. No Streamlit secret is required for local transcription or local feedback.
6. The first transcription may take longer because the selected Faster-Whisper model must be downloaded into the running environment.

## Architecture

```text
Browser / Streamlit UI
        |
        +--> Uploaded audio or browser recording
        |         |
        |         +--> Local Faster-Whisper speech-to-text
        |                    |
        |                    +--> Editable transcript
        |                              |
        +------------------------------+
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

## Optional enhanced feedback

The app works without an API key. If you later want the optional LLM narrative feedback path, add this to Streamlit Secrets:

```toml
[openai]
api_key = "YOUR_KEY_HERE"
```

Never commit a real key to GitHub.

## UI migration notes

The supplied TypeScript/Tailwind concept used a **Deep Frost Command** palette, glass cards, cyan/ice accents, a coach panel, outing summary, recent-session cards, and live-rate visualization. These elements were reimplemented using Streamlit-native widgets plus custom CSS so the deployed app keeps its Python/Streamlit architecture while closely following the supplied UI.

A compact copy of the supplied reference source is kept under `ui_reference/` for design traceability. The runtime Streamlit app does **not** depend on Node, Bun, Vite, or React.

## Repository layout

```text
.
├── app.py
├── requirements.txt
├── README.md
├── DEPLOYMENT_CHECKLIST.md
├── UI_MIGRATION_NOTES.md
├── .streamlit/
│   └── config.toml
├── assets/
│   └── rowing-lake.jpg
├── coxing_ai/
│   ├── audio_features.py
│   ├── core.py
│   ├── feedback.py
│   ├── simulator.py
│   └── transcription.py
├── notebooks/
│   └── CoxingCoachAI_Local_Whisper.ipynb
├── sample_data/
│   └── sample_transcript.txt
└── ui_reference/
    ├── index.tsx
    ├── styles.css
    └── README_original_ui.md
```

## Important MVP behavior

The simulator intentionally uses the project's ideal-world assumption: performance changes are simulated from recognized calls rather than inferred from real boat sensors. Future versions can replace these assumptions with telemetry, acoustic event detection, video analysis, or connected CoxBox data.
