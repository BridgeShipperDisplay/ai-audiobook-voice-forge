# Contributing to ai-audiobook-voice-forge

Thanks for wanting to forge some voices. This repo is a Windows desktop tool
that turns EPUB / TXT / PDF manuscripts into multi-voice audiobooks using
local TTS engines (Piper, XTTS-v2, Coqui, Kokoro) plus an optional cloud
fallback.

## Ground rules

- Python 3.11+ only. We test on 3.11 and 3.12.
- All TTS engines live behind the `TtsEngine` protocol in
  `voiceforge/engine/base.py`. If your engine doesn't implement it, the
  pipeline will not load the voice.
- Keep voice banks portable. A voice profile is a folder with a
  `profile.json` + `embeddings.npz` + reference `sample.wav` at 22.05 kHz
  mono. Nothing else.
- Chapter segmentation must be deterministic given the same input file.
  If you change segmentation logic, bump `SEGMENTER_VERSION` in
  `voiceforge/core/segmenter.py` and add a regression fixture.

## Dev setup

```powershell
git clone https://github.com/<you>/ai-audiobook-voice-forge
cd ai-audiobook-voice-forge
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .[dev]
python -m voiceforge.bootstrap --check
```

`--check` downloads a 40 MB Piper reference voice (en_US-amy-low) into
`voiceforge_cache/` and renders a 3-second test clip. If that works, your
environment is good.

## Pull requests

- One feature per PR. No drive-by reformatting.
- Add a test under `tests/` for any engine or segmenter change.
- Run `pytest -q` and `ruff check .` before pushing.
- If you add a new engine, update `docs` in the docstring, not a separate
  markdown file. We keep docs next to code.

## Voice profile submissions

We accept community voice profiles under `voices/community/`. Profile must
include a signed `LICENSE.txt` stating the voice owner consented to
redistribution. No cloning of real people without written consent gets
merged. Ever.