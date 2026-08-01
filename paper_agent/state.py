"""Paper project state stored in paper.yaml."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from .workflow import STAGE_ORDER


ROOT = Path(__file__).resolve().parent.parent
PAPERS_DIR = ROOT / "papers"


def slugify(title: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", title.strip().lower()).strip("-")
    return slug or "untitled-paper"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass
class Venue:
    name: str = ""
    track: str = ""
    deadline: str = ""
    page_limit: str = ""
    anonymous: bool | None = None
    template: str = ""
    url: str = ""


@dataclass
class PaperProject:
    title: str
    slug: str
    authors: list[str] = field(default_factory=list)
    abstract_blurb: str = ""
    contribution: str = ""
    venue: Venue = field(default_factory=Venue)
    current_stage: str = "idea"
    completed_stages: list[str] = field(default_factory=list)
    format: str = "markdown"  # markdown | latex
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)
    notes: dict[str, str] = field(default_factory=dict)

    @property
    def path(self) -> Path:
        return PAPERS_DIR / self.slug

    @property
    def yaml_path(self) -> Path:
        return self.path / "paper.yaml"

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PaperProject":
        venue_data = data.get("venue") or {}
        venue = Venue(**{k: venue_data.get(k, getattr(Venue(), k)) for k in Venue().__dict__})
        return cls(
            title=data.get("title", "Untitled"),
            slug=data.get("slug") or slugify(data.get("title", "Untitled")),
            authors=list(data.get("authors") or []),
            abstract_blurb=data.get("abstract_blurb", ""),
            contribution=data.get("contribution", ""),
            venue=venue,
            current_stage=data.get("current_stage", "idea"),
            completed_stages=list(data.get("completed_stages") or []),
            format=data.get("format", "markdown"),
            created_at=data.get("created_at", utc_now()),
            updated_at=data.get("updated_at", utc_now()),
            notes=dict(data.get("notes") or {}),
        )

    def save(self) -> None:
        self.updated_at = utc_now()
        self.path.mkdir(parents=True, exist_ok=True)
        (self.path / "notes").mkdir(exist_ok=True)
        self.yaml_path.write_text(
            yaml.safe_dump(self.to_dict(), sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )

    @classmethod
    def load(cls, slug: str) -> "PaperProject":
        path = PAPERS_DIR / slug / "paper.yaml"
        if not path.exists():
            raise FileNotFoundError(f"No paper project found at {path}")
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return cls.from_dict(data)

    def mark_complete(self, stage_id: str) -> None:
        if stage_id not in STAGE_ORDER:
            raise ValueError(f"Unknown stage: {stage_id}")
        if stage_id not in self.completed_stages:
            self.completed_stages.append(stage_id)
        # Advance current stage to the next incomplete one when possible.
        for sid in STAGE_ORDER:
            if sid not in self.completed_stages:
                self.current_stage = sid
                break
        else:
            self.current_stage = STAGE_ORDER[-1]

    def set_stage(self, stage_id: str) -> None:
        if stage_id not in STAGE_ORDER:
            raise ValueError(f"Unknown stage: {stage_id}")
        self.current_stage = stage_id


def list_projects() -> list[PaperProject]:
    if not PAPERS_DIR.exists():
        return []
    projects: list[PaperProject] = []
    for path in sorted(PAPERS_DIR.iterdir()):
        if path.is_dir() and (path / "paper.yaml").exists():
            projects.append(PaperProject.load(path.name))
    return projects


def resolve_project(slug: str | None = None) -> PaperProject:
    projects = list_projects()
    if not projects:
        raise FileNotFoundError(
            "No paper projects found. Run: python -m paper_agent init \"Your Title\""
        )
    if slug:
        return PaperProject.load(slug)
    if len(projects) == 1:
        return projects[0]
    # Prefer the most recently updated project.
    return sorted(projects, key=lambda p: p.updated_at, reverse=True)[0]
