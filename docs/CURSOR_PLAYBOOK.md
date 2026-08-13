# Cursor playbook

How to use this repo as a publication agent inside Cursor.

## 1. Create your paper project

```bash
pip install -e .
python3 -m paper_agent init "My Real Paper Title" --authors "Your Name"
python3 -m paper_agent next
```

## 2. Run a stage with Cursor Agent

In Cursor chat / Agent mode:

> Read `AGENTS.md`. Run the current stage from `python3 -m paper_agent next` for my paper and edit the files under `papers/<slug>/`. Do not invent citations or results.

Or:

> Execute `@papers/<slug>/agent_prompts/outline.md` on this project.

Tip: run `python3 -m paper_agent export-prompts` once so stage prompts are local to the paper folder.

## 3. Advance the workflow

After a stage looks good:

```bash
python3 -m paper_agent complete outline
python3 -m paper_agent next
```

## 4. Preflight before submission

```bash
python3 -m paper_agent check
```

Ask Cursor:

> Fix every warning/error from `python3 -m paper_agent check` that can be fixed in the manuscript or notes. Leave author-only ethics/COI items for me.

## Good prompts by phase

- **Stuck on novelty:** execute the `literature` prompt and force a closest-work table.
- **Bloated draft:** execute `polish` and ask for page-budget cuts without removing limitations.
- **Reviews in:** paste reviews into `notes/rebuttal.md`, then execute the `rebuttal` prompt.
