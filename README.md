# CoxingCoachAI MVP

A Colab-first and Streamlit-ready MVP for an AI-based coxswain training website app.

The app supports two core workflows:

1. Upload a coxing recording such as `.m4a`, `.mp3`, `.wav`, `.webm`, `.mp4`, `.mpeg`, or `.mpga`.
2. Record a simulated race session directly in the browser using Streamlit audio input.

The MVP prioritizes accurate transcription, focus-area-specific feedback, and an ideal-world race simulator where calls like power 10s and rate shifts are reflected in the simulated telemetry.

## MVP focus areas

Users can select any of the following focus areas before analysis:

- Communication clarity and economy of words
- Tone and phase-appropriate intensity
- Technical calls and rowing vocabulary
- Rhythmic synchronization and call timing
- Rate management and race rhythm
- Tactical awareness and race plan execution
- Psychological calibration and trust-building

If no focus areas are selected, the app produces general feedback across all areas.

## Recommended architecture

```text
Streamlit UI
  app.py
    - recording upload or browser audio input
    - focus-area selection
    - scenario settings
    - results dashboard

Core package
  coxing_ai/transcription.py
    - speech-to-text adapter
  coxing_ai/audio_features.py
    - transcript-derived metrics and command detection
  coxing_ai/simulator.py
    - ideal-world race telemetry simulator
  coxing_ai/feedback.py
    - LLM feedback with rule-based fallback
  coxing_ai/core.py
    - focus-area definitions and shared constants
```

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

## API key setup

The app can run in demo/rule-based mode without an API key, but transcription requires a speech-to-text provider.

For local development, create `.streamlit/secrets.toml` from the included template:

```toml
[openai]
api_key = "sk-your-key-here"
transcription_model = "gpt-4o-mini-transcribe"
feedback_model = "gpt-4o-mini"
```

Do not commit `.streamlit/secrets.toml` to GitHub.

## Streamlit Community Cloud deployment

1. Push this repository to GitHub.
2. In Streamlit Community Cloud, create a new app from the GitHub repository.
3. Set the entrypoint file to `app.py`.
4. Select the same Python version used during development.
5. Add the contents of `.streamlit/secrets.toml` through Streamlit Advanced settings, not in the repo.
6. Deploy.

## Colab workflow

Open `notebooks/CoxingCoachAI_MVP.ipynb` in Google Colab to test the core pipeline and export app files.

## Safety and privacy notes

- Treat uploaded audio as sensitive user data.
- Do not store recordings unless you explicitly add storage and user consent.
- Keep API keys in Streamlit secrets or environment variables.
- The MVP uses transcript-only feedback. Future versions can add deeper audio timing, cadence, 2D/3D animation, and oarlock/water sound synchronization.

## Known MVP limitations

- Browser recording through Streamlit produces a single audio clip, not a low-latency multiplayer game.
- The simulator is idealized and transcript-command-based; it does not yet model crew fatigue, weather, or imperfect execution.
- Without exact audio timestamps, call timing is estimated from transcript structure rather than measured against catch/finish sounds.
- Free hosting is not appropriate for large local AI models; use API-based transcription/feedback or a paid backend for heavier workloads.
