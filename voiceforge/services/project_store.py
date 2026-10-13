"""Persist/restore a .vfp project file (voice map, engine, cache pointers)."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass(slots=True)
class VoiceForgeProject:
    manuscript: str = ""
    engine: str = "piper"
    voice_map: dict[str, str] = field(default_factory=dict)
    narrator_voice: str = "narrator_default"
    schema: int = 1

    def save(self, path: Path) -> None:
        path.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "VoiceForgeProject":
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})