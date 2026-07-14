"""Integration coverage for local repository report generation."""

from pathlib import Path

from geo_infer_git.main import generate_report


def test_report_generation_writes_a_complete_local_artifact(tmp_path: Path) -> None:
    """Render a deterministic clone report without contacting a remote service."""
    generate_report(
        {"total_repos": 1, "success_repos": 1, "target_repos": []},
        str(tmp_path),
    )

    report = tmp_path / "clone_report.md"
    assert report.exists()
    assert "Success rate" in report.read_text(encoding="utf-8")
