"""Stage definitions for the paper publication workflow."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Stage:
    id: str
    title: str
    summary: str
    outputs: tuple[str, ...]
    done_when: str


STAGES: tuple[Stage, ...] = (
    Stage(
        id="idea",
        title="Clarify the idea",
        summary="Define problem, contribution, claims, and non-goals.",
        outputs=("notes/idea.md",),
        done_when="One-sentence contribution and 2–4 testable claims are written.",
    ),
    Stage(
        id="venue",
        title="Choose a venue",
        summary="Pick a realistic venue and capture format constraints.",
        outputs=("notes/venue.md",),
        done_when="Target venue, track, page limit, anonymity, and deadline fields are set.",
    ),
    Stage(
        id="literature",
        title="Map related work",
        summary="Position against closest prior work and baselines.",
        outputs=("notes/literature.md", "references.bib"),
        done_when="Related-work clusters and differentiation points are documented.",
    ),
    Stage(
        id="outline",
        title="Build the outline",
        summary="Create section plan and claim→evidence map.",
        outputs=("notes/outline.md",),
        done_when="Section outline and evidence map cover every major claim.",
    ),
    Stage(
        id="draft",
        title="Draft the manuscript",
        summary="Write abstract through conclusion iteratively.",
        outputs=("paper.md",),
        done_when="All core sections exist with no major TODO blockers in the story.",
    ),
    Stage(
        id="figures",
        title="Plan figures and tables",
        summary="Design visuals that carry the main results.",
        outputs=("notes/figures.md",),
        done_when="Each key claim has a planned figure/table with a draft caption.",
    ),
    Stage(
        id="experiments",
        title="Strengthen experiments narrative",
        summary="Specify setup, metrics, ablations, and limitations.",
        outputs=("notes/experiments.md",),
        done_when="Experiment plan matches claims; limitations are explicit.",
    ),
    Stage(
        id="citations",
        title="Clean citations",
        summary="Verify BibTeX and support for strong claims.",
        outputs=("references.bib",),
        done_when="Bibliography entries are real/verifiable and claims are supported.",
    ),
    Stage(
        id="polish",
        title="Polish for submission",
        summary="Clarity, consistency, anonymity, and page budget.",
        outputs=("notes/polish.md",),
        done_when="Style pass complete; identity leaks and length issues addressed.",
    ),
    Stage(
        id="submit",
        title="Submit",
        summary="Run submission checklist and prepare portal fields.",
        outputs=("notes/submission.md",),
        done_when="Checklist complete and manuscript packaged for the venue.",
    ),
    Stage(
        id="rebuttal",
        title="Respond to reviews",
        summary="Plan and draft rebuttal after reviews arrive.",
        outputs=("notes/rebuttal.md",),
        done_when="Review points mapped to responses with evidence or revisions.",
    ),
    Stage(
        id="camera_ready",
        title="Camera-ready",
        summary="Finalize formatting, artifacts, and acknowledgments.",
        outputs=("notes/camera_ready.md",),
        done_when="Camera-ready checklist complete and final PDF validated.",
    ),
)


STAGE_BY_ID = {stage.id: stage for stage in STAGES}
STAGE_ORDER = [stage.id for stage in STAGES]


def next_incomplete(completed: list[str]) -> Stage | None:
    done = set(completed)
    for stage in STAGES:
        if stage.id not in done:
            return stage
    return None
