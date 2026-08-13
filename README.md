# Technical Paper Publication Agent

An agent-guided workflow for taking a research idea to a submission-ready technical paper — and through rebuttal / camera-ready when needed.

This repository gives you:

1. **Cursor agent instructions** (`AGENTS.md` + `.cursor/rules/`) so Agent Mode behaves like a publication co-pilot
2. **A CLI workflow tool** (`paper-agent`) that tracks stages, prompts, and preflight checks
3. **Paper templates** (Markdown or LaTeX), note scaffolds, and submission checklists

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Start a new paper
python -m paper_agent init "Your Paper Title" --authors "Ada Lovelace, Alan Turing"

# See where you are
python -m paper_agent status

# Get the next-stage agent prompt
python -m paper_agent next
```

Then open the repo in Cursor and ask:

> Execute the current paper-agent stage prompt for my project.

Or paste the output of `python -m paper_agent prompt draft`.

## Workflow

| Stage | Goal |
|-------|------|
| `idea` | Contribution, claims, non-goals |
| `venue` | Target venue + format constraints |
| `literature` | Positioning and baselines |
| `outline` | Section plan + claim→evidence map |
| `draft` | Manuscript writing |
| `figures` | Figure/table plan and captions |
| `experiments` | Evaluation narrative |
| `citations` | BibTeX and claim support |
| `polish` | Clarity, anonymity, length |
| `submit` | Submission package |
| `rebuttal` | Review responses |
| `camera_ready` | Final accepted version |

Each paper lives in `papers/<slug>/` with:

```text
papers/my-paper/
  paper.yaml          # metadata + stage state
  paper.md            # or main.tex
  references.bib
  notes/              # stage worksheets
  figures/
  README.md
```

## Useful commands

```bash
python -m paper_agent list
python -m paper_agent stage outline
python -m paper_agent complete idea
python -m paper_agent set contribution "We propose ..."
python -m paper_agent set venue.name "NeurIPS"
python -m paper_agent set venue.anonymous true
python -m paper_agent check
python -m paper_agent export-prompts
python -m paper_agent prompt rebuttal
```

## Using this with Cursor

1. Open this repository in Cursor.
2. Create or select a paper project with the CLI.
3. Run `python -m paper_agent next` and ask Cursor to execute the printed prompt.
4. The agent will edit files under `papers/<slug>/` and keep `paper.yaml` updated.
5. Mark the stage done with `python -m paper_agent complete <stage>`.

See [docs/CURSOR_PLAYBOOK.md](docs/CURSOR_PLAYBOOK.md) for copy-paste Agent prompts.

The always-on rule in `.cursor/rules/paper-publication-agent.mdc` makes Cursor follow the publication workflow and integrity constraints (no fabricated citations or results).

## Integrity rules

- Do not invent citations, DOIs, or experimental numbers.
- Mark unknowns as `TODO` instead of guessing.
- Verify venue deadlines on official CFPs.
- Authors remain responsible for ethics, COI, and portal submissions.

## Development

```bash
pip install -e ".[dev]"
pytest
```
