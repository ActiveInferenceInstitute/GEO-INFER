"""Pinned structural contracts for the GitHub Actions workflow definitions.

The workflow files are the behavioral surface of the CI-GATES items
(GS-001/002/005/006/007/008): these tests pin the YAML structure those fixes
depend on, the same way the acceptance probes grep the workflow sources.
"""

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
WORKFLOWS = REPO_ROOT / ".github" / "workflows"


def _load(name: str) -> dict:
    document = yaml.safe_load((WORKFLOWS / name).read_text(encoding="utf-8"))
    assert isinstance(document, dict)
    return document


def _trigger(document: dict) -> dict:
    # PyYAML resolves a bare `on:` key to the boolean True (YAML 1.1).
    return document.get("on", document.get(True, {}))


def _dump(job: dict) -> str:
    # A wide dump keeps wrapped line-folding from splitting markers.
    return yaml.safe_dump(job, width=10**6)


def test_ci_runs_on_release_tags_for_the_release_gate():
    """GS-002: CI must run on v* tags so the release ci-gate has a run to wait for."""
    push = _trigger(_load("ci.yml"))["push"]
    assert push["tags"] == ["v*"]


def test_release_requires_ci_gate_and_always_verifies_wheels():
    """GS-002: the release job is gated on CI success and tag builds verify."""
    release = _load("release.yml")
    assert "ci-gate" in release["jobs"]
    assert "ci-gate" in release["jobs"]["release"]["needs"]

    build_steps = [
        step
        for step in release["jobs"]["release"]["steps"]
        if step.get("name") == "Build multi-package wheels"
    ]
    assert len(build_steps) == 1
    script = build_steps[0]["run"]
    assert "'--verify'" in script
    # The inverted conditional makes tag builds (empty inputs) verify.
    assert "run_isolated_verify != 'false'" in script


def test_validate_job_runs_gates_once_outside_test_matrix():
    """GS-005: interpreter-independent gates live in one non-matrix validate job."""
    jobs = _load("ci.yml")["jobs"]
    assert "validate" in jobs
    assert "strategy" not in jobs["validate"], "gate job must not be a matrix leg"
    gate_text = _dump(jobs["validate"])
    for marker in (
        "validate_repo_contracts.py",
        "--strict-source-language --strict-import-smoke",
        "validate_skills.py --check-xrefs --warnings-fatal",
        "validate_test_contracts.py",
        "validate_model_contracts.py",
        "run_model_audit.py",
        "gitleaks detect",
        "check_coverage_floor.py",
    ):
        assert marker in gate_text, f"missing gate marker: {marker}"

    test_text = _dump(jobs["test"])
    for marker in (
        "validate_repo_contracts.py",
        "gitleaks",
        "check_coverage_floor.py",
    ):
        assert marker not in test_text, f"gate duplicated in test legs: {marker}"


def test_coverage_floor_falls_back_to_empty_tree():
    """GS-004: an unresolvable base must widen the diff, not degrade to no-op."""
    gate_text = _dump(_load("ci.yml")["jobs"]["validate"])
    assert "git hash-object -t tree /dev/null" in gate_text


def test_each_category_run_is_immediately_followed_by_its_own_retention():
    """GS-001: a category's reports upload before any later category wipes them."""
    steps = _load("ci.yml")["jobs"]["test"]["steps"]
    version_token = "${{ matrix.python-version }}"
    for index, step in enumerate(steps):
        name = step.get("name", "")
        if not (name.startswith("Run ") and name.endswith(" tests")):
            continue
        category = name[len("Run ") : -len(" tests")]
        retain = steps[index + 1].get("name", "")
        assert retain == f"Retain {category} test reports", (
            f"{name} is not immediately followed by its own retention step"
        )
        artifact = steps[index + 1]["with"]["name"]
        assert artifact == "geo-infer-" + category + "-reports-py" + version_token


def test_test_matrix_covers_all_categories_per_interpreter():
    """GS-005: every category is its own matrix leg for both interpreters."""
    matrix = _load("ci.yml")["jobs"]["test"]["strategy"]["matrix"]
    assert matrix["python-version"] == ["3.11", "3.12"]
    assert matrix["category"] == [
        "unit",
        "integration",
        "performance",
        "system",
        "h3",
    ]


def test_build_smoke_builds_wheels_in_pr_ci():
    """GS-006: the real wheel build executes on pull requests, not only on tags."""
    build = _dump(_load("ci.yml")["jobs"]["build-smoke"])
    assert "build_package_wheels.py" in build
    assert "--outdir" in build


def test_workflow_definitions_are_linted_in_ci():
    """GS-008: a workflow-lint job runs actionlint on the workflow sources."""
    lint = _dump(_load("ci.yml")["jobs"]["workflow-lint"])
    assert "actionlint" in lint


def test_gnn_interchange_only_runs_on_contract_relevant_changes():
    """GS-007: no unfiltered push/PR legs duplicate the paired interchange run."""
    trigger = _trigger(_load("gnn-interchange.yml"))
    assert "push" not in trigger
    paths = trigger["pull_request"]["paths"]
    assert "GEO-INFER-ACT/**" in paths
    assert "GEO-INFER-TEST/validate_gnn_interchange.py" in paths
    assert ".github/gnn-pair.json" in paths
    assert ".github/workflows/gnn-interchange.yml" in paths


def test_every_workflow_definition_parses():
    for workflow in sorted(WORKFLOWS.glob("*.yml")):
        document = yaml.safe_load(workflow.read_text(encoding="utf-8"))
        assert isinstance(document, dict), workflow.name
        assert "jobs" in document, workflow.name
