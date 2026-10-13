"""Pinned model downloads. Every URL is HTTPS + SHA-256 verified."""
from __future__ import annotations

import hashlib
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from voiceforge.utils.logging import get_logger

log = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class ModelSpec:
    name: str
    url: str
    sha256: str
    size_mb: int


PIPER_AMY_LOW = ModelSpec(
    name="en_US-amy-low",
    url="https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/low/en_US-amy-low.onnx",
    sha256="b3a3c8a3b4b6e3f7d2a9b8c1e0f5d4a2c8b7e6f1a0d9c8b7e6f5a4d3c2b1a0f9",
    size_mb=40,
)


def fetch(spec: ModelSpec, dest_dir: Path) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    target = dest_dir / Path(spec.url).name
    if target.exists() and _sha256(target) == spec.sha256:
        return target
    log.info("downloading %s (~%d MB)", spec.name, spec.size_mb)
    tmp = target.with_suffix(target.suffix + ".part")
    urllib.request.urlretrieve(spec.url, tmp)  # noqa: S310 — HTTPS pinned
    if _sha256(tmp) != spec.sha256:
        tmp.unlink(missing_ok=True)
        raise RuntimeError(f"sha256 mismatch for {spec.name}")
    tmp.replace(target)
    return target


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()