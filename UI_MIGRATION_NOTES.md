# GLIDE UI Migration Notes

This repository migrates the attached GLIDE frontend concept into the Streamlit application while preserving the existing Python AI pipeline.

## Design elements carried over

- Deep teal / frost background palette.
- Cyan "ice" accent color.
- Glassmorphism cards with thin illuminated borders.
- GLIDE brand header and console navigation motif.
- Coach Anders conversation card.
- Today's outing summary with lake rowing imagery.
- Recent-session cards.
- Live crew / stroke-rate display.
- Compact monospace labels, rounded cards, and technical-console styling.

## Streamlit mappings

| Original UI concept | Streamlit implementation |
|---|---|
| React/Tailwind dashboard | Streamlit wide-layout dashboard |
| Frost cards | `st.container(border=True)` + custom CSS |
| Coach chat card | HTML/CSS presentation card |
| Session setup | Native selectboxes, sliders, multiselect, and expander |
| Recent sessions | HTML/CSS cards |
| Live crew bars | HTML/CSS rate visualization |
| Training workflow | Streamlit tabs |
| Upload interaction | `st.file_uploader` |
| Microphone input | `st.audio_input` |
| Telemetry visualization | `st.line_chart` |
| AI feedback | Existing Python feedback engine |

The runtime does not require React, Vite, Node, or Bun. This is intentional so Streamlit Community Cloud can launch the app directly from `app.py`.
