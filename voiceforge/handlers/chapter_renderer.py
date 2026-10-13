"""Renders a single Chapter to a WAV using the loaded engine and caster."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import soundfile as sf

from voiceforge.config.settings import Settings
from voiceforge.core.caster import VoiceCaster
from voiceforge.engine.base import TtsEngine
from voiceforge.models.manuscript import Chapter
from voiceforge.utils.audio import crossfade, silence
from voiceforge.utils.logging import get_logger

log = get_logger(__name__)


class ChapterRenderer:
    def __init__(self, engine: TtsEngine, caster: VoiceCaster, settings: Settings) -> None:
        self.engine = engine
        self.caster = caster
        self.settings = settings
        self.sample_rate = settings.engine.sample_rate

    def render_chapter(self, chapter: Chapter, out_dir: Path, index: int) -> Path:
        segments: list[np.ndarray] = []
        full_text = " ".join(p.text for p in chapter.paragraphs)
        casting = self.caster.assign(full_text, self.engine.available_voices())

        gap = silence(self.settings.render.paragraph_pause_ms, self.sample_rate)

        for para in chapter.paragraphs:
            voice_id = self._voice_for(para.text, casting)
            audio = self.engine.synthesize(para.text, voice_id=voice_id)
            segments.append(audio)
            segments.append(gap)

        merged = crossfade(segments, self.sample_rate, fade_ms=40)
        out_path = out_dir / f"chapter_{index:03d}.wav"
        sf.write(str(out_path), merged, self.sample_rate, subtype="PCM_16")
        log.debug("wrote %s (%.1fs)", out_path.name, len(merged) / self.sample_rate)
        return out_path

    def _voice_for(self, text: str, casting) -> str:
        for name, assignment in casting.assignments.items():
            if name.lower() in text.lower():
                return assignment.voice_id
        return casting.narrator_voice