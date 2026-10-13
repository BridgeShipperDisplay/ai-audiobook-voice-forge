"""XTTS-v2 backend — zero-shot voice cloning from a reference clip."""
from __future__ import annotations

from pathlib import Path

import numpy as np

from voiceforge.engine.base import SynthesisError


class XttsEngine:
    name = "xtts"

    def __init__(self, model_dir: Path, sample_rate: int = 24_000) -> None:
        self.model_dir = Path(model_dir)
        self.sample_rate = sample_rate
        self._tts = None
        self._speaker_wavs: dict[str, str] = {}

    def load(self) -> None:
        if self._tts is not None:
            return
        try:
            from TTS.api import TTS  # type: ignore
        except ImportError as exc:
            raise SynthesisError("XTTS requires the [xtts] extra: pip install .[xtts]") from exc
        self._tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
        for profile in self.model_dir.glob("*/sample.wav"):
            self._speaker_wavs[profile.parent.name] = str(profile)

    def available_voices(self) -> list[str]:
        return sorted(self._speaker_wavs.keys())

    def synthesize(self, text: str, voice_id: str) -> np.ndarray:
        if self._tts is None:
            raise SynthesisError("XTTS not loaded")
        speaker = self._speaker_wavs.get(voice_id)
        if speaker is None:
            raise SynthesisError(f"no reference clip for voice {voice_id!r}")
        wav = self._tts.tts(text=text, speaker_wav=speaker, language="en")
        return np.asarray(wav, dtype=np.float32)

    def unload(self) -> None:
        self._tts = None