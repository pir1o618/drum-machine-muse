# Drum Machine Muse

An interactive Python practice tool built for Code in Place (CIPX 2026). As an acoustic drum hobbyist, I created this project to generate daily practice patterns across different musical styles using AI, complete with a continuous visual beat loop, synthesized pad audio, session logging, and PDF export.

## Features

- **AI Rhythm Generation:** Prompts for a musical style and generates custom practice drum patterns via `call_gpt` in `ai.py`.
- **Continuous Canvas Beat Loop:** Animates `HH (Hi-Hat)`, `SN (Snare)`, and `BD (Kick)` pads in a continuous 4/4 groove with a live beat indicator and bar counter until you decide to stop.
- **Interactive Playback & Tempo Controls:** Includes **Restart**, **Pause / Resume** (`Space`), **- Slower**, **+ Faster**, and **Continue** (`Esc` or close window).
- **Synthesized Pad Audio (Windows):** Plays short `winsound` tones per drum pad with a **Sound: ON / OFF** toggle (`M`).
- **Session Log & PDF Export:** Appends generated patterns to `drum_patterns.log` and exports selected patterns to `drum_patterns.pdf` on `exit` using Python's standard library.

## Setup

1. Keep `main.py`, `ai.py`, and the `notopenai/` package folder in the same project directory.
2. Add your Code in Place API key to `ai.py` (do not commit `ai.py` to GitHub; it is listed in `.gitignore`):

```python
API_KEY = "noai-..."
```

## Usage

Run the application from your local environment (such as VS Code on Windows):

```bash
python main.py
```

Enter a rhythm style when prompted, use the Canvas controls to practice or inspect the groove, choose whether to queue each pattern for the PDF sheet (`y`/`n`), and type `exit` to generate `drum_patterns.pdf` and quit.

Happy practicing!