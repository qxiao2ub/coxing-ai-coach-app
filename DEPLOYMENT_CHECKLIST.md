# GLIDE CoxingCoachAI — Streamlit deployment checklist

**Author:** Julia Hu

## Repository

- [ ] `app.py` is at repository root.
- [ ] `requirements.txt` is at repository root.
- [ ] `.streamlit/config.toml` is committed.
- [ ] `assets/rowing-lake.jpg` is committed.
- [ ] `data/visitor_count.json` is committed.
- [ ] `coxing_ai/visitor_counter.py` is committed.
- [ ] Do not commit `.streamlit/secrets.toml` or any token.

## Streamlit Community Cloud

- Repository: `qxiao2ub/coxing-ai-coach-app`
- Branch: `main`
- Main file: `app.py`
- Recommended Python: 3.11 or 3.12

## Persistent no-database visitor counter

For a cumulative count that survives Streamlit container restarts:

1. Create a fine-grained GitHub token limited to this repository.
2. Give it **Contents: Read and write** permission.
3. In Streamlit App settings → Secrets, add:

```toml
[github_counter]
token = "github_pat_..."
repo = "qxiao2ub/coxing-ai-coach-app"
path = "data/visitor_count.json"
branch = "usage-data"
source_branch = "main"
```

The app creates/uses the separate `usage-data` branch so visitor increments do not modify the deployed `main` branch.

If this secret is omitted, the app uses a local JSON fallback. That is convenient for testing but cannot be guaranteed to survive an ephemeral Streamlit server replacement.

## Audio transcription

No OpenAI API key is required. The first local transcription may download the selected Faster-Whisper model and can therefore take longer.
