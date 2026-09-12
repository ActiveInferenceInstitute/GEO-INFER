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
