"""Entry point for the voiceforge CLI. Boots the desktop app or headless pipeline."""
from __future__ import annotations

import sys
from pathlib import Path

import typer
from rich.console import Console

from voiceforge import __version__
from voiceforge.config.settings import load_settings
from voiceforge.core.forge import AudiobookForge
from voiceforge.utils.logging import configure_logging

app = typer.Typer(
    name="voiceforge",
    help="Forge multi-voice AI audiobooks from EPUB / TXT / PDF.",
    no_args_is_help=True,
)
console = Console()


@app.command()
def build(
    manuscript: Path = typer.Argument(..., exists=True, readable=True),
    out: Path = typer.Option(Path("output"), "--out", "-o", help="Output folder"),
    voice_map: Path | None = typer.Option(None, "--voice-map", help="Character->voice JSON"),
    engine: str = typer.Option("piper", "--engine", help="piper | xtts | kokoro"),
) -> None:
    """Render a manuscript to M4B using the configured voice bank."""
    settings = load_settings()
    configure_logging(settings.log_level)
    forge = AudiobookForge(settings=settings, engine_name=engine)
    result = forge.render(manuscript=manuscript, out_dir=out, voice_map=voice_map)
    console.print(f"[green]Rendered[/] {result.chapters} chapters -> {result.output_path}")


@app.command()
def check() -> None:
    """Verify environment: engines, cache, voice bank integrity."""
    from voiceforge.services.engine_loader import EngineLoader

    settings = load_settings()
    loader = EngineLoader(settings)
    report = loader.self_check()
    for line in report:
        console.print(line)
    if not report.ok:
        raise typer.Exit(code=1)


@app.command()
def version() -> None:
    console.print(f"ai-audiobook-voice-forge {__version__}")


def main() -> None:
    app()


if __name__ == "__main__":
    sys.exit(app())