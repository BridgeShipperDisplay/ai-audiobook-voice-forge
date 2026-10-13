"""Layered settings: defaults -> user config -> env -> CLI overrides."""
from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_CONFIG_PATH = Path(os.environ.get("APPDATA", Path.home())) / "voiceforge" / "config.toml"


@dataclass(slots=True)
class EngineSettings:
    piper_model_dir: Path = Path("voiceforge_cache/piper")
    xtts_model_dir: Path = Path("voiceforge_cache/xtts")
    kokoro_model_dir: Path = Path("voiceforge_cache/kokoro")
    sample_rate: int = 22_050
    threads: int = max(1, (os.cpu_count() or 2) - 1)


@dataclass(slots=True)
class RenderSettings:
    chapter_pause_ms: int = 700
    paragraph_pause_ms: int = 220
    normalize_lufs: float = -16.0
    output_format: str = "m4b"
    bitrate: str = "128k"


@dataclass(slots=True)
class Settings:
    log_level: str = "INFO"
    engine: EngineSettings = field(default_factory=EngineSettings)
    render: RenderSettings = field(default_factory=RenderSettings)
    voice_bank: Path = Path("voices")
    cache_dir: Path = Path("voiceforge_cache")


def _merge_toml(settings: Settings, data: dict) -> Settings:
    if "engine" in data:
        for k, v in data["engine"].items():
            if hasattr(settings.engine, k):
                setattr(settings.engine, k, Path(v) if k.endswith("_dir") else v)
    if "render" in data:
        for k, v in data["render"].items():
            if hasattr(settings.render, k):
                setattr(settings.render, k, v)
    if "voice_bank" in data:
        settings.voice_bank = Path(data["voice_bank"])
    if "log_level" in data:
        settings.log_level = str(data["log_level"]).upper()
    return settings


def load_settings(config_path: Path | None = None) -> Settings:
    """Load settings from the user config path, applying env overrides."""
    path = config_path or DEFAULT_CONFIG_PATH
    settings = Settings()
    if path.exists():
        with path.open("rb") as fh:
            _merge_toml(settings, tomllib.load(fh))
    if env_engine := os.environ.get("VOICEFORGE_ENGINE"):
        settings.engine.piper_model_dir = settings.engine.piper_model_dir  # keep shape
    if env_cache := os.environ.get("VOICEFORGE_CACHE"):
        settings.cache_dir = Path(env_cache)
    return settings