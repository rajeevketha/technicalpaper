"""CLI for the technical paper publication agent."""

from __future__ import annotations

import argparse
import sys

from . import __version__
from .checks import run_checks
from .project import init_project
from .prompts import load_prompt
from .state import list_projects, resolve_project
from .workflow import STAGE_BY_ID, STAGE_ORDER, STAGES, next_incomplete


def _print(msg: str = "") -> None:
    print(msg)


def cmd_init(args: argparse.Namespace) -> int:
    authors = [a.strip() for a in (args.authors or "").split(",") if a.strip()]
    try:
        project = init_project(
            args.title,
            authors=authors,
            fmt=args.format,
            slug=args.slug,
        )
    except FileExistsError as exc:
        _print(f"error: {exc}")
        return 1

    _print(f"Created paper project: {project.path}")
    _print(f"Current stage: {project.current_stage}")
    _print()
    _print("Next:")
    _print(f"  python -m paper_agent prompt {project.current_stage} --slug {project.slug}")
    _print("Then ask Cursor to execute that prompt against the paper folder.")
    return 0


def cmd_list(_: argparse.Namespace) -> int:
    projects = list_projects()
    if not projects:
        _print("No paper projects yet. Create one with:")
        _print('  python -m paper_agent init "Your Paper Title"')
        return 0
    for project in projects:
        _print(
            f"- {project.slug}: {project.title} "
            f"[stage={project.current_stage}, done={len(project.completed_stages)}/{len(STAGES)}]"
        )
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    project = resolve_project(args.slug)
    _print(f"Title: {project.title}")
    _print(f"Slug: {project.slug}")
    _print(f"Format: {project.format}")
    _print(f"Path: {project.path}")
    _print(f"Contribution: {project.contribution or '(unset)'}")
    venue = project.venue.name or "(unset)"
    _print(f"Venue: {venue}")
    if project.venue.deadline:
        _print(f"Deadline: {project.venue.deadline}")
    _print(f"Current stage: {project.current_stage}")
    _print()
    _print("Stages:")
    for stage in STAGES:
        mark = "x" if stage.id in project.completed_stages else " "
        current = " <-" if stage.id == project.current_stage else ""
        _print(f"  [{mark}] {stage.id:14} {stage.title}{current}")
    nxt = next_incomplete(project.completed_stages)
    _print()
    if nxt:
        _print(f"Next recommended: {nxt.id} — {nxt.summary}")
        _print(f"Done when: {nxt.done_when}")
    else:
        _print("All stages marked complete.")
    return 0


def cmd_next(args: argparse.Namespace) -> int:
    project = resolve_project(args.slug)
    stage = STAGE_BY_ID.get(project.current_stage) or next_incomplete(project.completed_stages)
    if stage is None:
        _print("All stages complete. Use camera_ready or start a new paper.")
        return 0

    _print(f"Stage: {stage.id} — {stage.title}")
    _print(stage.summary)
    _print(f"Done when: {stage.done_when}")
    _print("Expected outputs:")
    for output in stage.outputs:
        path = project.path / output
        exists = "exists" if path.exists() else "missing"
        _print(f"  - {output} ({exists})")
    _print()
    _print("Agent prompt:")
    _print("-" * 72)
    _print(load_prompt(stage.id if stage.id != "submit" else "submit"))
    _print("-" * 72)
    _print()
    _print("Ask Cursor to execute the prompt above for this project.")
    _print(
        f"When finished: python -m paper_agent complete {stage.id} --slug {project.slug}"
    )
    return 0


def cmd_stage(args: argparse.Namespace) -> int:
    project = resolve_project(args.slug)
    stage_id = args.stage_id
    if stage_id not in STAGE_BY_ID:
        _print(f"error: unknown stage '{stage_id}'")
        _print("Valid stages: " + ", ".join(STAGE_ORDER))
        return 1
    project.set_stage(stage_id)
    project.save()
    _print(f"Current stage set to '{stage_id}' for {project.slug}")
    return cmd_next(argparse.Namespace(slug=project.slug))


def cmd_complete(args: argparse.Namespace) -> int:
    project = resolve_project(args.slug)
    stage_id = args.stage_id
    if stage_id not in STAGE_BY_ID:
        _print(f"error: unknown stage '{stage_id}'")
        return 1
    project.mark_complete(stage_id)
    project.save()
    _print(f"Marked '{stage_id}' complete for {project.slug}")
    nxt = next_incomplete(project.completed_stages)
    if nxt:
        _print(f"Next stage: {nxt.id} — {nxt.title}")
    else:
        _print("All stages complete.")
    return 0


def cmd_prompt(args: argparse.Namespace) -> int:
    stage_id = args.stage_id
    # allow alias
    if stage_id == "submission":
        stage_id = "submit"
    if stage_id not in STAGE_BY_ID and stage_id != "submit":
        _print(f"error: unknown stage '{args.stage_id}'")
        return 1
    prompt_id = "submit" if stage_id == "submit" else stage_id
    text = load_prompt(prompt_id)
    if args.slug or not args.raw:
        try:
            project = resolve_project(args.slug)
            header = (
                f"Project: {project.title} ({project.slug})\n"
                f"Path: {project.path}\n"
                f"Current stage: {project.current_stage}\n\n"
            )
            _print(header + text)
            return 0
        except FileNotFoundError:
            if args.slug:
                raise
    _print(text)
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    project = resolve_project(args.slug)
    results = run_checks(project)
    errors = 0
    warns = 0
    for item in results:
        prefix = item.level.upper()
        _print(f"[{prefix}] {item.code}: {item.message}")
        if item.level == "error":
            errors += 1
        elif item.level == "warn":
            warns += 1
    _print()
    _print(f"Summary: {errors} error(s), {warns} warning(s)")
    return 1 if errors else 0


def cmd_set(args: argparse.Namespace) -> int:
    project = resolve_project(args.slug)
    key = args.key
    value = args.value

    if key == "contribution":
        project.contribution = value
    elif key == "abstract_blurb":
        project.abstract_blurb = value
    elif key == "format":
        if value not in {"markdown", "latex"}:
            _print("error: format must be markdown or latex")
            return 1
        project.format = value
    elif key.startswith("venue."):
        field = key.split(".", 1)[1]
        if field == "anonymous":
            lowered = value.lower()
            if lowered in {"true", "yes", "1"}:
                project.venue.anonymous = True
            elif lowered in {"false", "no", "0"}:
                project.venue.anonymous = False
            else:
                _print("error: venue.anonymous must be true/false")
                return 1
        elif hasattr(project.venue, field):
            setattr(project.venue, field, value)
        else:
            _print(f"error: unknown venue field '{field}'")
            return 1
    elif key == "authors":
        project.authors = [a.strip() for a in value.split(",") if a.strip()]
    else:
        _print(
            "error: supported keys: contribution, abstract_blurb, format, authors, "
            "venue.name, venue.track, venue.deadline, venue.page_limit, "
            "venue.anonymous, venue.template, venue.url"
        )
        return 1

    project.save()
    _print(f"Updated {key} for {project.slug}")
    return 0


def cmd_export_prompt_pack(args: argparse.Namespace) -> int:
    """Write all stage prompts into the paper folder for offline/Cursor use."""
    project = resolve_project(args.slug)
    out_dir = project.path / "agent_prompts"
    out_dir.mkdir(exist_ok=True)
    for stage_id in STAGE_ORDER:
        prompt_id = "submit" if stage_id == "submit" else stage_id
        (out_dir / f"{stage_id}.md").write_text(load_prompt(prompt_id), encoding="utf-8")
    _print(f"Wrote prompt pack to {out_dir}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="paper-agent",
        description="Technical paper publication agent — from idea to camera-ready.",
    )
    parser.add_argument("--version", action="version", version=f"paper-agent {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Create a new paper project")
    p_init.add_argument("title", help="Paper title")
    p_init.add_argument("--authors", default="", help="Comma-separated authors")
    p_init.add_argument(
        "--format",
        choices=["markdown", "latex"],
        default="markdown",
        help="Manuscript format",
    )
    p_init.add_argument("--slug", default=None, help="Optional folder slug")
    p_init.set_defaults(func=cmd_init)

    p_list = sub.add_parser("list", help="List paper projects")
    p_list.set_defaults(func=cmd_list)

    p_status = sub.add_parser("status", help="Show project workflow status")
    p_status.add_argument("--slug", default=None)
    p_status.set_defaults(func=cmd_status)

    p_next = sub.add_parser("next", help="Show the next stage and agent prompt")
    p_next.add_argument("--slug", default=None)
    p_next.set_defaults(func=cmd_next)

    p_stage = sub.add_parser("stage", help="Jump to a workflow stage")
    p_stage.add_argument("stage_id", choices=STAGE_ORDER)
    p_stage.add_argument("--slug", default=None)
    p_stage.set_defaults(func=cmd_stage)

    p_complete = sub.add_parser("complete", help="Mark a stage complete")
    p_complete.add_argument("stage_id", choices=STAGE_ORDER)
    p_complete.add_argument("--slug", default=None)
    p_complete.set_defaults(func=cmd_complete)

    p_prompt = sub.add_parser("prompt", help="Print an agent prompt for a stage")
    p_prompt.add_argument("stage_id", help="Stage id (idea, venue, draft, ...)")
    p_prompt.add_argument("--slug", default=None)
    p_prompt.add_argument(
        "--raw",
        action="store_true",
        help="Print prompt only, without project header",
    )
    p_prompt.set_defaults(func=cmd_prompt)

    p_check = sub.add_parser("check", help="Run submission preflight checks")
    p_check.add_argument("--slug", default=None)
    p_check.set_defaults(func=cmd_check)

    p_set = sub.add_parser("set", help="Set a metadata field on the paper project")
    p_set.add_argument("key")
    p_set.add_argument("value")
    p_set.add_argument("--slug", default=None)
    p_set.set_defaults(func=cmd_set)

    p_export = sub.add_parser(
        "export-prompts", help="Write all stage prompts into the paper folder"
    )
    p_export.add_argument("--slug", default=None)
    p_export.set_defaults(func=cmd_export_prompt_pack)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except FileNotFoundError as exc:
        _print(f"error: {exc}")
        return 1
    except Exception as exc:  # pragma: no cover - safety net for CLI
        _print(f"error: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
