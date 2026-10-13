"""Loads and self-checks TTS engines. Single source of truth for backends."""
from __future__ import annotations

from dataclasses import dataclass, field

from voiceforge.config.settings import Settings
from voiceforge.engine.base import TtsEngine
from voiceforge.engine.piper_engine import PiperEngine
from voiceforge.engine.xtts_engine import XttsEngine
from voiceforge.utils.logging import get_logger

log = get_logger(__name__)

_REGISTRY = {
    "piper": lambda s: PiperEngine(s.engine.piper_model_dir, s.engine.sample_rate),
    "xtts": lambda s: XttsEngine(s.engine.xtts_model_dir),
    "kokoro": lambda s: PiperEngine(s.engine.kokoro_model_dir, s.engine.sample_rate),
}


@dataclass(slots=True)
class CheckReport:
    lines: list[str] = field(default_factory=list)
    ok: bool = True

    def add(self, line: str, ok: bool = True) -> None:
        self.lines.append(line)
        self.ok = self.ok and ok


class EngineLoader:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def load(self, name: str) -> TtsEngine:
        factory = _REGISTRY.get(name)
        if factory is None:
            raise KeyError(f"unknown engine {name!r}; known: {sorted(_REGISTRY)}")
        engine = factory(self.settings)
        engine.load()
        log.info("engine %s loaded with %d voices", engine.name, len(engine.available_voices()))
        return engine

    def self_check(self) -> CheckReport:
        report = CheckReport()
        for name in _REGISTRY:
            try:
                engine = self.load(name)
                report.add(f"[green]OK[/]  {name}: {len(engine.available_voices())} voices")
            except Exception as exc:
                report.add(f"[yellow]SKIP[/] {name}: {exc}", ok=False)
        return report