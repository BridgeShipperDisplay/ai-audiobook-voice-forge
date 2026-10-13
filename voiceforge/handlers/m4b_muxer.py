"""Concatenates chapter WAVs into a single M4B via ffmpeg; writes chapter index."""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import soundfile as sf

from voiceforge.config.settings import Settings
from voiceforge.utils.logging import get_logger

log = get_logger(__name__)


class M4BMuxer:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.last_duration_sec: float = 0.0

    def mux(self, chapters: list[Path], title: str, out_dir: Path) -> Path:
        if not chapters:
            raise ValueError("no chapters to mux")
        if shutil.which("ffmpeg") is None:
            raise RuntimeError("ffmpeg not on PATH — install ffmpeg 6.x and retry")

        concat_list = out_dir / "_concat.txt"
        concat_list.write_text(
            "\n".join(f"file '{c.resolve().as_posix()}'" for c in chapters),
            encoding="utf-8",
        )

        output = out_dir / f"{self._slug(title)}.m4b"
        cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-f", "concat", "-safe", "0", "-i", str(concat_list),
            "-c:a", "aac", "-b:a", self.settings.render.bitrate,
            "-movflags", "+faststart", str(output),
        ]
        subprocess.run(cmd, check=True)

        self.last_duration_sec = sum(sf.info(str(c)).duration for c in chapters)
        self._write_chapter_index(chapters, out_dir, self.last_duration_sec)
        concat_list.unlink(missing_ok=True)
        log.info("muxed %s (%.1fs)", output.name, self.last_duration_sec)
        return output

    def _write_chapter_index(self, chapters: list[Path], out_dir: Path, total: float) -> None:
        cursor = 0.0
        entries = []
        for c in chapters:
            dur = sf.info(str(c)).duration
            entries.append({"file": c.name, "start": round(cursor, 3), "duration": round(dur, 3)})
            cursor += dur
        (out_dir / "chapters.json").write_text(
            json.dumps({"total": round(total, 3), "chapters": entries}, indent=2),
            encoding="utf-8",
        )

    @staticmethod
    def _slug(title: str) -> str:
        return "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in title).strip("_") or "audiobook"