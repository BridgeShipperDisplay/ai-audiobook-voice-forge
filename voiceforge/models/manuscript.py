"""Manuscript ingestion: EPUB / TXT / PDF into a normalized text model."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class Paragraph:
    text: str


@dataclass(slots=True)
class Chapter:
    index: int
    title: str
    paragraphs: list[Paragraph] = field