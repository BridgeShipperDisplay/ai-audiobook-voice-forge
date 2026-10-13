"""AudiobookForge — orchestrates the full manuscript-to-M4B pipeline."""
from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

from voiceforge.config.settings import Settings
from voiceforge.core.caster import VoiceCaster
from voiceforge.core.segmenter import ChapterSegmenter
from voiceforge.handlers.chapter_renderer import ChapterRenderer
from voiceforge.handlers.m4b_muxer import M4BMuxer
from voiceforge.models.manuscript import Manuscript
from voiceforge.services.engine_loader import EngineLoader
from voiceforge.utils.logging import get_logger

log = get_logger(__name__)


@dataclass(slots=True)
class RenderResult:
    chapters: int
    output_path: Path
    duration_sec: float
    elapsed_sec: float


class AudiobookForge:
    """Top-level pipeline. Owns the engine, caster, and renderer lifecycle."""

    def __init__(self, settings: Settings, engine_name: str = "piper") -> None:
        self.settings = settings
        self.engine_name = engine_name
        self._loader = EngineLoader(settings)

    def render(
        self,
        manuscript: Path,
        out_dir: Path,
        voice_map: Path | None = None,
    ) -> RenderResult:
        started = time.perf_counter()
        log.info("ingesting manuscript %s", manuscript)
        book: Manuscript = Manuscript.from_path(manuscript)

        segmenter = ChapterSegmenter()
        chapters = segmenter.split(book)
        log.info("segmented into %d chapters", len(chapters))

        engine = self._loader.load(self.engine_name)
        caster = VoiceCaster(settings=self.settings, voice_map_path=voice_map)
        renderer = ChapterRenderer(engine=engine, caster=caster, settings=self.settings)

        out_dir.mkdir(parents=True, exist_ok=True)
        chapter_files: list[Path] = []
        for idx, chapter in enumerate(chapters, start=1):
            wav = renderer.render_chapter(chapter, out_dir=out_dir, index=idx)
            chapter_files.append(wav)

        muxer = M4BMuxer(settings=self.settings)
        final = muxer.mux(chapter_files, title=book.title, out_dir=out_dir)

        elapsed = time.perf_counter() - started
        return RenderResult(
            chapters=len(chapters),
            output_path=final,
            duration_sec=muxer.last_duration_sec,
            elapsed_sec=elapsed,
        )