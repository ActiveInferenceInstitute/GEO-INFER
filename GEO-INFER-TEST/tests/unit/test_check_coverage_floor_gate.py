"""Regression tests for GS-293: check_coverage_floor.py must fail cleanly
(named-module message, exit 1) instead of raising KeyError when a diff-derived
module has no baseline entry."""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "GEO-INFER-TEST" / "check_coverage_floor.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("check_coverage_floor", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_unknown_module_fails_cleanly(capsys):
    """A forced module absent from the baseline must produce the clean _fail
    message naming the module, not an unhandled KeyError traceback."""
    module = _load_module()
    try:
        module.main(
            ["--base", "HEAD", "--head", "HEAD", "--modules", "GEO-INFER-DOESNOTEXIST"]
        )
    except SystemExit as exc:
        assert exc.code == 1
    else:
        raise AssertionError("gate should exit non-zero for an unknown module")
    err = capsys.readouterr().err
    assert "coverage floor gate failure" in err
    assert "GEO-INFER-DOESNOTEXIST" in err
    assert "KeyError" not in err


def test_unknown_module_via_cli_no_traceback():
    """End-to-end: the script exits 1 and prints no Python traceback."""
    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--base",
            "HEAD",
            "--head",
            "HEAD",
            "--modules",
            "GEO-INFER-DOESNOTEXIST",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 1
    assert "Traceback" not in completed.stderr
    assert "GEO-INFER-DOESNOTEXIST" in completed.stderr


def test_baseline_entries_are_dict_shaped():
    manifest = json.loads(
        (REPO_ROOT / "GEO-INFER-TEST" / "coverage_baseline.json").read_text()
    )
    assert isinstance(manifest.get("modules"), dict)


def _baseline_module() -> str:
    baseline = json.loads(
        (REPO_ROOT / "GEO-INFER-TEST" / "coverage_baseline.json").read_text()
    )
    return sorted(baseline["modules"])[0]


def test_failing_suite_during_measurement_fails_gate(monkeypatch, capsys):
    """GS-004: coverage measured while tests were failing must not pass."""
    module = _load_module()
    name = _baseline_module()

    def fake_measure(target):
        return {
            "module": target,
            "status": "measured",
            "coverage_percent": 100.0,
            "pytest_rc": 1,
            "seconds": 0.1,
        }

    monkeypatch.setattr(module, "measure_module", fake_measure)

    try:
        module.main(["--base", "HEAD", "--head", "HEAD", "--modules", name])
    except SystemExit as exc:
        assert exc.code == 1
    else:
        raise AssertionError("gate must fail when the measured suite had failures")

    captured = capsys.readouterr()
    assert "FAILED-SUITE" in captured.out
    assert "pytest rc=1" in captured.err


def test_clean_suite_measurement_passes_gate(monkeypatch, capsys):
    """GS-004: a measurement whose suite passed still passes the floor."""
    module = _load_module()
    name = _baseline_module()

    def fake_measure(target):
        return {
            "module": target,
            "status": "measured",
            "coverage_percent": 100.0,
            "pytest_rc": 0,
            "seconds": 0.1,
        }

    monkeypatch.setattr(module, "measure_module", fake_measure)

    assert module.main(["--base", "HEAD", "--head", "HEAD", "--modules", name]) == 0
    assert "FAILED-SUITE" not in capsys.readouterr().out


def test_failed_suite_verdict_prints_failing_test_names(monkeypatch, capsys):
    """A FAILED-SUITE verdict names the failing tests from the JUnit report
    instead of hiding the per-test detail behind a one-line summary."""
    module = _load_module()
    name = _baseline_module()

    def fake_measure(target):
        return {
            "module": target,
            "status": "measured",
            "coverage_percent": 100.0,
            "pytest_rc": 1,
            "failing_tests": [
                "tests.unit.test_sample::test_bad",
                "tests.unit.test_sample::test_broken",
            ],
            "seconds": 0.1,
        }

    monkeypatch.setattr(module, "measure_module", fake_measure)

    try:
        module.main(["--base", "HEAD", "--head", "HEAD", "--modules", name])
    except SystemExit as exc:
        assert exc.code == 1
    else:
        raise AssertionError("gate must fail when the measured suite had failures")

    captured = capsys.readouterr()
    assert "FAILED tests.unit.test_sample::test_bad" in captured.out
    assert "FAILED tests.unit.test_sample::test_broken" in captured.out
    assert "pytest rc=1 (2 failing tests)" in captured.err


def test_failed_suite_verdict_truncates_long_failure_lists(monkeypatch, capsys):
    """Failure lists longer than 20 names are bounded in the verdict."""
    module = _load_module()
    name = _baseline_module()

    def fake_measure(target):
        return {
            "module": target,
            "status": "measured",
            "coverage_percent": 100.0,
            "pytest_rc": 1,
            "failing_tests": [
                f"tests.unit.test_sample::test_bad_{index}" for index in range(25)
            ],
            "seconds": 0.1,
        }

    monkeypatch.setattr(module, "measure_module", fake_measure)

    try:
        module.main(["--base", "HEAD", "--head", "HEAD", "--modules", name])
    except SystemExit as exc:
        assert exc.code == 1
    else:
        raise AssertionError("gate must fail when the measured suite had failures")

    out = capsys.readouterr().out
    printed = [line for line in out.splitlines() if line.startswith("  FAILED ")]
    assert len(printed) == 20
    assert "... and 5 more failing tests" in out


def _fake_git_diff(monkeypatch, name_only_output: str, per_file_output: str):
    """Patch subprocess.run used by _changed_modules: the name-only diff
    returns ``name_only_output``; per-file ``-U0`` diffs return
    ``per_file_output``."""

    def fake_run(cmd, **kwargs):
        if "-U0" in cmd:
            return subprocess.CompletedProcess(
                cmd, 0, stdout=per_file_output, stderr=""
            )
        return subprocess.CompletedProcess(cmd, 0, stdout=name_only_output, stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)


def test_version_only_bump_excluded_from_remeasurement(monkeypatch):
    """GS19-01: a module whose only src change is its __version__ literal is
    not re-measured by the gate."""
    module = _load_module()
    name_only = "GEO-INFER-AGENT/src/geo_infer_agent/__init__.py\n"
    version_hunk = (
        "--- a/GEO-INFER-AGENT/src/geo_infer_agent/__init__.py\n"
        "+++ b/GEO-INFER-AGENT/src/geo_infer_agent/__init__.py\n"
        '+__version__ = "0.3.0"\n'
        '-__version__ = "0.2.1"\n'
    )
    _fake_git_diff(monkeypatch, name_only, version_hunk)
    assert module._changed_modules("base", "head") == set()


def test_content_change_still_remeasured(monkeypatch):
    """GS19-01: non-version changes keep the module in the re-measurement set."""
    module = _load_module()
    name_only = "GEO-INFER-AGENT/src/geo_infer_agent/__init__.py\n"
    content_hunk = (
        "--- a/GEO-INFER-AGENT/src/geo_infer_agent/__init__.py\n"
        "+++ b/GEO-INFER-AGENT/src/geo_infer_agent/__init__.py\n"
        "+import os\n"
        "-import sys\n"
    )
    _fake_git_diff(monkeypatch, name_only, content_hunk)
    assert module._changed_modules("base", "head") == {"GEO-INFER-AGENT"}


def test_failed_suite_measurement_retried_once(monkeypatch, capsys):
    """GS19-01: one bounded retry of a FAILED-SUITE measurement absorbs a
    transient flake; a clean retry passes the gate."""
    module = _load_module()
    name = _baseline_module()
    calls: list[str] = []

    def fake_measure(target):
        calls.append(target)
        if len(calls) == 1:
            return {
                "module": target,
                "status": "measured",
                "coverage_percent": 100.0,
                "pytest_rc": 1,
                "failing_tests": ["tests.unit.test_sample::test_flaky"],
                "seconds": 0.1,
            }
        return {
            "module": target,
            "status": "measured",
            "coverage_percent": 100.0,
            "pytest_rc": 0,
            "seconds": 0.1,
        }

    monkeypatch.setattr(module, "measure_module", fake_measure)
    assert module.main(["--base", "HEAD", "--head", "HEAD", "--modules", name]) == 0
    assert len(calls) == 2
    out = capsys.readouterr().out
    assert "retrying once" in out
    assert "FAILED-SUITE" not in out


def test_failed_suite_retry_exhausted_fails_gate(monkeypatch, capsys):
    """GS19-01: a measurement that still fails after the retry fails the gate."""
    module = _load_module()
    name = _baseline_module()
    calls: list[str] = []

    def fake_measure(target):
        calls.append(target)
        return {
            "module": target,
            "status": "measured",
            "coverage_percent": 100.0,
            "pytest_rc": 1,
            "failing_tests": ["tests.unit.test_sample::test_bad"],
            "seconds": 0.1,
        }

    monkeypatch.setattr(module, "measure_module", fake_measure)
    try:
        module.main(["--base", "HEAD", "--head", "HEAD", "--modules", name])
    except SystemExit as exc:
        assert exc.code == 1
    else:
        raise AssertionError("gate must fail when the retry also fails")
    assert len(calls) == 2
    captured = capsys.readouterr()
    assert "FAILED-SUITE" in captured.out
    assert "pytest rc=1 (1 failing tests)" in captured.err
