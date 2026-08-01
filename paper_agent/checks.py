"""Lightweight preflight checks for a paper project."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .state import PaperProject


@dataclass
class CheckResult:
    level: str  # ok | warn | error
    code: str
    message: str


TODO_RE = re.compile(r"\bTODO\b", re.IGNORECASE)
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
GITHUB_RE = re.compile(r"https?://github\.com/[\w.-]+/[\w.-]+", re.IGNORECASE)


def _manuscript_path(project: PaperProject) -> Path | None:
    if project.format == "latex":
        path = project.path / "main.tex"
    else:
        path = project.path / "paper.md"
    return path if path.exists() else None


def run_checks(project: PaperProject) -> list[CheckResult]:
    results: list[CheckResult] = []

    manuscript = _manuscript_path(project)
    if manuscript is None:
        results.append(
            CheckResult("error", "missing_manuscript", "Manuscript file not found.")
        )
        return results

    text = manuscript.read_text(encoding="utf-8")
    todo_count = len(TODO_RE.findall(text))
    if todo_count:
        results.append(
            CheckResult(
                "warn",
                "todos_remaining",
                f"Found {todo_count} TODO marker(s) in {manuscript.name}.",
            )
        )
    else:
        results.append(CheckResult("ok", "todos_remaining", "No TODO markers in manuscript."))

    if not project.contribution.strip():
        results.append(
            CheckResult(
                "warn",
                "missing_contribution",
                "paper.yaml contribution is empty.",
            )
        )
    else:
        results.append(CheckResult("ok", "missing_contribution", "Contribution is set."))

    if not project.venue.name.strip():
        results.append(
            CheckResult("warn", "missing_venue", "No venue selected in paper.yaml.")
        )
    else:
        results.append(
            CheckResult("ok", "missing_venue", f"Venue set to {project.venue.name}.")
        )

    bib = project.path / "references.bib"
    if not bib.exists() or not bib.read_text(encoding="utf-8").strip():
        results.append(
            CheckResult("warn", "empty_bib", "references.bib is missing or empty.")
        )
    else:
        bib_text = bib.read_text(encoding="utf-8")
        entry_count = len(re.findall(r"^@", bib_text, flags=re.MULTILINE))
        if entry_count == 0:
            results.append(
                CheckResult(
                    "warn",
                    "empty_bib",
                    "references.bib has no BibTeX entries yet.",
                )
            )
        else:
            results.append(
                CheckResult("ok", "empty_bib", f"Bibliography has {entry_count} entr(y/ies).")
            )

    if project.venue.anonymous:
        leaks = []
        if EMAIL_RE.search(text):
            leaks.append("email address")
        if GITHUB_RE.search(text):
            leaks.append("GitHub URL")
        ack = re.search(r"acknowledg(e)?ments?", text, flags=re.IGNORECASE)
        if ack:
            leaks.append("acknowledgments section")
        if leaks:
            results.append(
                CheckResult(
                    "error",
                    "anonymity_leak",
                    "Possible anonymity leaks: " + ", ".join(leaks) + ".",
                )
            )
        else:
            results.append(
                CheckResult("ok", "anonymity_leak", "No obvious anonymity leaks detected.")
            )

    # Stage completeness soft check
    important = ["idea", "venue", "outline", "draft"]
    missing = [s for s in important if s not in project.completed_stages]
    if missing:
        results.append(
            CheckResult(
                "warn",
                "stages_incomplete",
                "Core stages not marked complete: " + ", ".join(missing) + ".",
            )
        )
    else:
        results.append(
            CheckResult("ok", "stages_incomplete", "Core stages marked complete.")
        )

    return results
