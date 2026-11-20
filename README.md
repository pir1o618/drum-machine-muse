# Drum Machine Muse

An interactive Python practice tool for Code in Place (CIPX) that generates custom drum patterns with AI, animates a continuous 4/4 beat on a `tkinter.Canvas` window with synthesized pad sounds on Windows, logs sessions, and exports selected patterns to a PDF practice sheet.

## Features

- **AI Rhythm Generation:** Prompts for a musical style and generates practice drum patterns via `call_gpt` in `ai.py`.
- **Continuous Canvas Beat Loop:** Animates `HH (Hi-Hat)`, `SN (Snare)`, and `BD (Kick)` pads in a continuous 4/4 groove with a live beat indicator and bar counter until you decide to stop.
- **Interactive Playback & Tempo Controls:** Includes **Restart**, **Pause / Resume** (`Space`), **- Slower**, **+ Faster**, and **Continue** (`Esc` or close window).
- **Synthesized Pad Audio (Windows):** Plays short `winsound` tones per drum pad with a **Sound: ON / OFF** toggle (`M`).
- **Session Log & PDF Export:** Appends generated patterns to a session log file and exports selected patterns to `drum_patterns.pdf` on `exit` using Python's standard library.

## Setup

1. Keep `main.py`, `ai.py`, and the `notopenai/` package folder in the same project directory.
2. Add your Code in Place API key to `ai.py` (do not commit `ai.py` to GitHub; it is listed in `.gitignore`):

```python
API_KEY = "noai-..."