from paper_agent.checks import run_checks
from paper_agent.cli import main
from paper_agent.project import init_project
from paper_agent.state import PaperProject, list_projects


def test_init_project_markdown(tmp_path, monkeypatch):
    monkeypatch.setattr("paper_agent.state.PAPERS_DIR", tmp_path)
    monkeypatch.setattr("paper_agent.project.PAPERS_DIR", tmp_path)

    project = init_project("A Study of Fast Widgets", authors=["Ada Lovelace"], fmt="markdown")
    assert project.path.exists()
    assert (project.path / "paper.md").exists()
    assert (project.path / "references.bib").exists()
    assert (project.path / "notes" / "idea.md").exists()
    assert (project.path / "paper.yaml").exists()

    loaded = PaperProject.load(project.slug)
    assert loaded.title == "A Study of Fast Widgets"
    assert loaded.current_stage == "idea"


def test_cli_status_and_complete(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("paper_agent.state.PAPERS_DIR", tmp_path)
    monkeypatch.setattr("paper_agent.project.PAPERS_DIR", tmp_path)

    assert main(["init", "CLI Paper", "--slug", "cli-paper"]) == 0
    assert main(["status", "--slug", "cli-paper"]) == 0
    out = capsys.readouterr().out
    assert "CLI Paper" in out
    assert "idea" in out

    assert main(["complete", "idea", "--slug", "cli-paper"]) == 0
    project = PaperProject.load("cli-paper")
    assert "idea" in project.completed_stages
    assert project.current_stage == "venue"

    assert main(["set", "venue.name", "ExampleConf", "--slug", "cli-paper"]) == 0
    assert main(["set", "venue.anonymous", "true", "--slug", "cli-paper"]) == 0
    project = PaperProject.load("cli-paper")
    assert project.venue.name == "ExampleConf"
    assert project.venue.anonymous is True


def test_checks_detect_todo_and_anonymity(tmp_path, monkeypatch):
    monkeypatch.setattr("paper_agent.state.PAPERS_DIR", tmp_path)
    monkeypatch.setattr("paper_agent.project.PAPERS_DIR", tmp_path)

    project = init_project("Anon Paper", fmt="markdown", slug="anon-paper")
    project.venue.anonymous = True
    project.contribution = "We propose X"
    project.venue.name = "TestConf"
    project.save()

    manuscript = project.path / "paper.md"
    manuscript.write_text(
        "# Anon Paper\n\nContact ada@example.com\nSee https://github.com/org/repo\n",
        encoding="utf-8",
    )
    # add a bib entry
    (project.path / "references.bib").write_text(
        "@article{Test2024,\n  title={T},\n  author={A},\n  year={2024}\n}\n",
        encoding="utf-8",
    )

    results = {r.code: r for r in run_checks(project)}
    assert results["anonymity_leak"].level == "error"
    assert results["todos_remaining"].level == "ok"


def test_list_projects(tmp_path, monkeypatch):
    monkeypatch.setattr("paper_agent.state.PAPERS_DIR", tmp_path)
    monkeypatch.setattr("paper_agent.project.PAPERS_DIR", tmp_path)
    assert list_projects() == []
    init_project("One", slug="one")
    init_project("Two", slug="two")
    assert [p.slug for p in list_projects()] == ["one", "two"]
