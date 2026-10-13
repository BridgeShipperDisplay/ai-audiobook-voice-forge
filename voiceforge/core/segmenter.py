"""Deterministic chapter + paragraph segmentation for manuscripts."""
from __future__ import annotations

import re
from dataclasses import dataclass

from voiceforge.models.manuscript import Chapter, Manuscript, Paragraph

SEGMENTER_VERSION = "2026.02.1"

_CHAPTER_RE = re.compile(
    r"^\s*(?:chapter|part|book)\s+([0-9]+|[ivxlcdm]+)\b.*$",
    re.IGNORECASE | re.MULTILINE,
)


@dataclass(slots=True)
class SegmenterConfig:
    min_chapter_chars: int = 400
    min_paragraph_chars: int = 12
    keep_front_matter: bool = False


class ChapterSegmenter:
    """Splits a Manuscript into Chapter objects with paragraph granularity.

    Deterministic: same input -> same output, given same SEGMENTER_VERSION.
    """

    def __init__(self, config: SegmenterConfig | None = None) -> None:
        self.config = config or SegmenterConfig()

    def split(self, book: Manuscript) -> list[Chapter]:
        raw_text = book.full_text
        matches = list(_CHAPTER_RE.finditer(raw_text))

        if not matches:
            return [self._single_chapter(book)]

        chapters: list[Chapter] = []
        for i, m in enumerate(matches):
            start = m.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(raw_text)
            body = raw_text[start:end].strip()
            if len(body) < self.config.min_chapter_chars:
                continue
            chapters.append(
                Chapter(
                    index=len(chapters) + 1,
                    title=m.group(0).strip(),
                    paragraphs=self._paragraphs(body),
                )
            )
        return chapters or [self._single_chapter(book)]

    def _paragraphs(self, text: str) -> list[Paragraph]:
        chunks = re.split(r"\n\s*\n", text)
        out: list[Paragraph] = []
        for c in chunks:
            cleaned = " ".join(c.split())
            if len(cleaned) >= self.config.min_paragraph_chars:
                out.append(Paragraph(text=cleaned))
        return out

    def _single_chapter(self, book: Manuscript) -> Chapter:
        return Chapter(
            index=1,
            title=book.title or "Untitled",
            paragraphs=self._paragraphs(book.full_text),
        )