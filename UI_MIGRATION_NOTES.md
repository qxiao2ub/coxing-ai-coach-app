# UI migration notes — GLIDE Morning Lake

The attached GLIDE UI package was a TypeScript/TanStack/Tailwind design. The deployment target remains Python + Streamlit, so the design was translated into Streamlit-native layout and custom CSS while retaining the app’s working AI pipeline.

## Preserved design elements

- GLIDE wordmark and compact navigation treatment.
- Morning-lake photographic background and fixed-cover visual treatment.
- Light translucent glass cards with blue/ice accents.
- Ambient radial glow layers.
- Upload-recording call to action.
- Today’s outing / training profile card.
- Three summary metrics.
- Recent-session cards.
- Live crew / target-rate bar visualization.
- Responsive mobile behavior.
- Monospace uppercase micro-labels and rounded UI surfaces.

The original supplied source package is kept intact under `ui_reference/glide-code-original/` except for the uploaded `.git` pointer file, which is intentionally omitted from the distributable repository.

## Functional additions layered onto the design

- Local Faster-Whisper transcription.
- Upload and browser-recording workflows.
- Editable transcript and timestamped segments.
- Focus-area coaching.
- Transcript metrics and call detection.
- Ideal-world telemetry simulator.
- Post-race feedback.
- Author-only credit for Julia Hu.
- Cumulative visitor counter shown throughout the app.
- Optional GitHub-branch persistence for the visitor counter without using a database.
