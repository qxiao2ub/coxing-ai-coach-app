# Streamlit Deployment Checklist — GLIDE / CoxingCoachAI

**Author:** Julia Hu  
**Advisor:** Dr. Qingyang Xiao

1. Extract the ZIP archive.
2. Upload the contents of `CoxingCoachAI_GLIDE_UI_GitHub_Repo` to the repository root.
3. Confirm `app.py` is at the root.
4. Confirm `requirements.txt`, `coxing_ai/`, `assets/`, and `.streamlit/config.toml` are committed.
5. In Streamlit Community Cloud, choose `app.py` as the entrypoint.
6. No API key is required for Faster-Whisper transcription or local coaching feedback.
7. Start with `tiny.en` if Community Cloud memory is tight; use `base.en` for the balanced default.
8. The first local transcription can be slower while the Whisper model is downloaded.
9. Do not commit real API keys. If optional LLM feedback is used, configure it in Streamlit Secrets.
10. Test upload, browser recording, demo transcript, charts, and feedback after deployment.
