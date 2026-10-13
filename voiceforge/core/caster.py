"""Character detection + voice assignment."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from voiceforge.config.settings import Settings
from voiceforge.utils.logging import get_logger

log = get_logger(__name__)

_DIALOGUE_RE = re.compile(r'[“"]([^”"]{4,})[”"]')
_SPEAKER_RE = re.compile(r"^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:said|asked|replied|whispered)")


@dataclass(slots=True)
class VoiceAssignment:
    character: str
    voice_id: str
    confidence: float


@dataclass(slots=True)
class CastingResult:
    narrator_voice: str = "narrator_default"
    assignments: dict[str, VoiceAssignment] = field(default_factory=dict)


class VoiceCaster:
    """Assigns voices to detected characters. Explicit voice_map wins."""

    def __init__(self, settings: Settings, voice_map_path: Path | None = None) -> None:
        self.settings = settings
        self.explicit: dict[str, str] = {}
        if voice_map_path and voice_map_path.exists():
            self.explicit = json.loads(voice_map_path.read_text(encoding="utf-8"))

    def detect_characters(self, text: str) -> list[str]:
        found: dict[str, int] = {}
        for m in _SPEAKER_RE.finditer(text):
            name = m.group(1)
            found[name] = found.get(name, 0) + 1
        ranked = sorted(found.items(), key=lambda kv: kv[1], reverse=True)
        return [name for name, count in ranked if count >= 3]

    def assign(self, text: str, available_voices: list[str]) -> CastingResult:
        result = CastingResult()
        for name in self.detect_characters(text):
            if name in self.explicit:
                result.assignments[name] = VoiceAssignment(name, self.explicit[name], 1.0)
                continue
            voice = self._pick_voice(name, available_voices)
            if voice:
                result.assignments[name] = VoiceAssignment(name, voice, 0.55)
        log.info("cast %d characters", len(result.assignments))
        return result

    def _pick_voice(self, name: str, pool: list[str]) -> str | None:
        if not pool:
            return None
        idx = hash(name) % len(pool)
        return pool[idx]