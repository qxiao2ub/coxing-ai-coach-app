# Streamlit Deployment Checklist

- [ ] Extract the zip.
- [ ] Upload the extracted folder contents to the root of a GitHub repository.
- [ ] Confirm `app.py`, `requirements.txt`, and `.streamlit/config.toml` are committed.
- [ ] Create a Streamlit Community Cloud app.
- [ ] Select the GitHub repository and `main` branch.
- [ ] Set the entrypoint file to `app.py`.
- [ ] Select Python 3.11 or 3.12 in Advanced settings.
- [ ] Leave Secrets blank unless optional LLM feedback is desired.
- [ ] Deploy and wait for dependencies to install.
- [ ] First test the Demo transcript tab.
- [ ] Next test a 15–30 second `.m4a` clip with `base.en`.
- [ ] If resource use is high, choose `tiny.en` in the sidebar.
