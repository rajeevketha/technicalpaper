"""Create and scaffold paper projects from templates."""

from __future__ import annotations

from pathlib import Path
import shutil

from .state import PAPERS_DIR, PaperProject, slugify
from .workflow import STAGE_BY_ID


TEMPLATE_ROOT = Path(__file__).resolve().parent / "templates"


def _render(text: str, mapping: dict[str, str]) -> str:
    for key, value in mapping.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def init_project(
    title: str,
    *,
    authors: list[str] | None = None,
    fmt: str = "markdown",
    slug: str | None = None,
) -> PaperProject:
    authors = authors or []
    slug = slug or slugify(title)
    project_dir = PAPERS_DIR / slug
    if project_dir.exists():
        raise FileExistsError(f"Paper project already exists: {project_dir}")

    project = PaperProject(
        title=title,
        slug=slug,
        authors=authors,
        format=fmt if fmt in {"markdown", "latex"} else "markdown",
    )
    project.path.mkdir(parents=True)
    (project.path / "notes").mkdir()
    (project.path / "figures").mkdir()

    mapping = {
        "title": title,
        "authors": ", ".join(authors) if authors else "Anonymous",
    }

    # Manuscript template
    if project.format == "latex":
        tex = _render((TEMPLATE_ROOT / "main.tex").read_text(encoding="utf-8"), mapping)
        (project.path / "main.tex").write_text(tex, encoding="utf-8")
    else:
        md = _render((TEMPLATE_ROOT / "paper.md").read_text(encoding="utf-8"), mapping)
        (project.path / "paper.md").write_text(md, encoding="utf-8")

    shutil.copy(TEMPLATE_ROOT / "references.bib", project.path / "references.bib")

    notes_src = TEMPLATE_ROOT / "notes"
    for note in notes_src.glob("*.md"):
        target = project.path / "notes" / note.name
        target.write_text(note.read_text(encoding="utf-8"), encoding="utf-8")

    # README for the paper folder
    (project.path / "README.md").write_text(
        "\n".join(
            [
                f"# {title}",
                "",
                "This folder is managed by the Technical Paper Publication Agent.",
                "",
                "## Quick commands",
                "",
                "```bash",
                f"python -m paper_agent status --slug {slug}",
                f"python -m paper_agent next --slug {slug}",
                f"python -m paper_agent prompt idea --slug {slug}",
                f"python -m paper_agent check --slug {slug}",
                "```",
                "",
                "Open the prompt for the current stage in Cursor and ask the agent to execute it.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    project.notes = {
        stage_id: f"notes/{stage_id}.md"
        for stage_id in STAGE_BY_ID
        if (project.path / "notes" / f"{stage_id}.md").exists()
    }
    # stage file names that differ slightly
    project.notes["submit"] = "notes/submission.md"
    project.save()
    return project
