"""Stage prompts loaded from markdown files."""

from __future__ import annotations

from pathlib import Path


def load_prompt(stage_id: str) -> str:
    package_root = Path(__file__).resolve().parent
    path = package_root / f"{stage_id}.md"
    if not path.exists():
        raise FileNotFoundError(f"No prompt for stage '{stage_id}' at {path}")
    return path.read_text(encoding="utf-8")
