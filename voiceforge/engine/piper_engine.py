"""Piper backend — fast, CPU-only, best default for long books."""
from __future__ import annotations

from pathlib import Path

import numpy as np

from voiceforge.engine.base import SynthesisError


class PiperEngine:
    name = "piper"

    def __init__(self, model_dir: Path, sample_rate: int = 22_050) -> None:
        self.model_dir = Path(model_dir)
        self.sample_rate = sample_rate
        self._voices: dict[str, object] = {}

    def load(self) -> None:
        if self._voices:
            return
        try:
            from piper.voice import PiperVoice  # type: ignore
        except ImportError as exc:  # pragma: no cover
            raise SynthesisError("piper-tts not installed: pip install piper-tts") from exc

        for onnx in self.model_dir.glob("*.onnx"):
            voice_id = onnx.stem
            self._voices[voice_id] = PiperVoice.load(str(onnx), config_path=str(onnx) + ".json")

    def available_voices(self) -> list[str]:
        return sorted(self._voices.keys())

    def synthesize(self, text: str, voice_id: str) -> np.ndarray:
        if voice_id not in self._voices:
            voice_id = next(iter(self._voices), "")
        if not voice_id:
            raise SynthesisError("no piper voices loaded")
        voice = self._voices[voice_id]
        chunks: list[np.ndarray] = []
        for chunk in voice.synthesize(text):  # type: ignore[attr-defined]
            chunks.append(np.frombuffer(chunk.audio_int16_bytes, dtype=np.int16).astype(np.float32) / 32768.0)
        if not chunks:
            return np.zeros(0, dtype=np.float32)
        return np.concatenate(chunks)

    def unload(self) -> None:
        self._voices.clear()