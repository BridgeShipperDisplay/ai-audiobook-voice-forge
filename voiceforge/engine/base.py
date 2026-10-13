"""TtsEngine protocol — every backend implements this. Pipeline refuses to load otherwise."""
from __future__ import annotations

from typing import Protocol, runtime_checkable

import numpy as np


@runtime_checkable
class TtsEngine(Protocol):
    """Contract for TTS backends.

    synthesize() returns float32 mono PCM in [-1, 1] at engine sample rate.
    Implementations must be thread-safe for sequential calls but need not
    support concurrent synthesis on the same instance.
    """

    name: str

    def load(self) -> None:
        """Load weights into memory. Idempotent."""
        ...

    def available_voices(self) -> list[str]:
        """Return voice IDs this engine can synthesize."""
        ...

    def synthesize(self, text: str, voice_id: str) -> np.ndarray:
        """Render text to float32 mono audio. Raises SynthesisError on failure."""
        ...

    def unload(self) -> None:
        """Release weights. Safe to call twice."""
        ...


class SynthesisError(RuntimeError):
    """Raised when an engine fails to render a passage."""