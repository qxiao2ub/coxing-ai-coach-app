# CoxingCoachAI — No-Key Streamlit Edition

CoxingCoachAI is an off-water coxswain training MVP. Users can upload a race or practice recording, record a simulated race call in the browser, review the locally generated transcript, select feedback focus areas, inspect ideal-world simulated telemetry, and generate post-race coaching feedback.

## Important change in this edition

**Audio transcription no longer requires `OPENAI_API_KEY`.** The app uses Faster-Whisper locally on the Streamlit server with CPU INT8 inference.

An OpenAI key is optional and is used only for enhanced LLM-written feedback. Without a key, the app automatically uses the included local coaching-rule engine.

## Features

- Upload `.m4a`, `.mp3`, `.wav`, `.webm`, `.mp4`, `.mpeg`, or `.mpga` recordings.
- Record a simulated race call with the browser microphone.
- Local Faster-Whisper speech-to-text with rowing vocabulary prompting.
- Timestamped transcription segments and an editable transcript.
- User-selected feedback focus areas; blank selection produces general feedback.
- Transcript metrics for filler rate, estimated calls, technical language, and detected commands.
- Ideal-world telemetry simulation for power 10s, rate shifts, settles, and sprints.
- Rule-based no-key feedback, with optional LLM feedback when a key is configured.
- Included Google Colab notebook for local transcription and pipeline experimentation.

## Repository structure

```text
.
├── app.py
├── requirements.txt
├── README.md
├── LICENSE
├── .gitignore
├── .streamlit/
│   └── config.toml
├── coxing_ai/
│   ├── __init__.py
│   ├── audio_features.py
│   ├── core.py
│   ├── feedback.py
│   ├── simulator.py
│   └── transcription.py
├── notebooks/
│   └── CoxingCoachAI_Local_Whisper.ipynb
└── sample_data/
    └── sample_transcript.txt
```

## Run locally

Use Python 3.11 or 3.12.

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

macOS/Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

The first transcription downloads the selected Whisper model. Subsequent transcriptions reuse the cached model while the app process remains active.

## Deploy on Streamlit Community Cloud

1. Extract this zip file.
2. Create a new GitHub repository.
3. Upload **the contents of the extracted folder** so that `app.py` and `requirements.txt` are at the repository root.
4. Commit the files to the `main` branch.
5. In Streamlit Community Cloud, create a new app from the repository.
6. Set the entrypoint to `app.py`.
7. In Advanced settings, select **Python 3.11** or **Python 3.12**.
8. No secrets are needed for transcription.
9. Deploy.

## Model selection

The sidebar offers:

- `tiny.en`: fastest and lowest memory.
- `base.en`: recommended balance and default.
- `small.en`: better accuracy but slower and more resource intensive.

On free Streamlit hosting, begin with `base.en` and short recordings. If the app is slow or reaches resource limits, switch to `tiny.en`.

## Optional enhanced feedback

To enable LLM-written feedback, add this in Streamlit Advanced settings → Secrets:

```toml
[openai]
api_key = "your-key"
```

This is optional. Do not commit `.streamlit/secrets.toml` to GitHub.

## Privacy and safety

- Uploaded recordings are written only to a temporary file for transcription and are deleted afterward.
- This starter app does not include permanent recording storage or user accounts.
- Inform users how recordings are processed before adding data persistence.
- The simulator is idealized; it is not a safety, navigation, or on-water steering system.

## Current limitations

- Free Streamlit hosting uses CPU, so long audio may take several minutes to transcribe.
- The first transcription downloads the model and is slower than later requests.
- Call timing is inferred from transcription segments; the app does not yet detect catches, finishes, or oarlock sounds directly.
- Tactical steering and line analysis require future video/computer-vision features.
