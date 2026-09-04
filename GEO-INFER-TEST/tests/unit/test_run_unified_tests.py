"""Unit tests for the unified test runner script."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
RUNNER_PATH = REPO_ROOT / "GEO-INFER-TEST" / "run_unified_tests.py"


def load_runner_module():
    spec = importlib.util.spec_from_file_location("geo_infer_run_unified_tests", RUNNER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def make_module(root: Path, name: str) -> Path:
    src_path = root / f"GEO-INFER-{name}" / "src"
    src_path.mkdir(parents=True)
    return src_path


def make_test_module(root: Path, name: str) -> Path:
    module_path = root / f"GEO-INFER-{name}"
    (module_path / "tests" / "performance").mkdir(parents=True)
    (module_path / "tests" / "unit").mkdir()
    return module_path


def test_workspace_src_paths_are_sorted(tmp_path, monkeypatch):
    runner = load_runner_module()
    b_src = make_module(tmp_path, "B")
    a_src = make_module(tmp_path, "A")
    monkeypatch.setattr(runner, "PROJECT_ROOT", tmp_path)

    assert runner.workspace_src_paths() == [a_src, b_src]


def test_subprocess_env_prepends_workspace_src_paths(tmp_path, monkeypatch):
    runner = load_runner_module()
    a_src = make_module(tmp_path, "A")
    monkeypatch.setattr(runner, "PROJECT_ROOT", tmp_path)
    monkeypatch.setenv("PYTHONPATH", "/existing/path")

    env = runner.build_subprocess_env()

    assert env["PYTHONPATH"].split(runner.os.pathsep)[:2] == [
        str(a_src),
        "/existing/path",
    ]


def test_module_discovery_ignores_non_test_files(tmp_path, monkeypatch):
    runner = load_runner_module()
    module_path = tmp_path / "GEO-INFER-SAMPLE"
    tests_path = module_path / "tests"
    tests_path.mkdir(parents=True)
    (tests_path / "conftest.py").write_text("# fixtures only\n")
    (tests_path / "README.md").write_text("Not a test file.\n")
    monkeypatch.setattr(runner, "PROJECT_ROOT", tmp_path)

    [module] = runner.discover_geo_infer_modules()

    assert module.has_tests is False


def test_unit_category_falls_back_to_root_test_files(tmp_path, monkeypatch):
    runner = load_runner_module()
    module_path = make_test_module(tmp_path, "SAMPLE")
    root_test = module_path / "tests" / "test_legacy_layout.py"
    root_test.write_text("def test_legacy_layout():\n    assert True\n")
    unit_test = module_path / "tests" / "unit" / "test_unit_layout.py"
    unit_test.write_text("def test_unit_layout():\n    assert True\n")
    tools_dir = module_path / "tests" / "tools"
    tools_dir.mkdir()
    tool_test = tools_dir / "test_tool_layout.py"
    tool_test.write_text("def test_tool_layout():\n    assert True\n")
    monkeypatch.setattr(runner, "PROJECT_ROOT", tmp_path)
    module = runner.discover_geo_infer_modules()[0]

    assert runner.category_test_paths(module, "unit") == sorted([root_test, unit_test, tool_test])
    assert runner.category_test_paths(module, "integration") == []
    assert runner.category_test_paths(module, "system") == []


def test_clean_results_dir_removes_nested_stale_artifacts(tmp_path, monkeypatch):
    runner = load_runner_module()
    results_dir = tmp_path / "results"
    stale_nested = results_dir / "old-run"
    stale_nested.mkdir(parents=True)
    (stale_nested / "summary.json").write_text("{}\n")
    (results_dir / "stale.xml").write_text("<testsuites />\n")
    monkeypatch.setattr(runner, "RESULTS_DIR", results_dir)

    runner.ensure_results_dir(clean=True)

    assert list(results_dir.iterdir()) == []


def test_run_command_passes_workspace_env(tmp_path, monkeypatch):
    runner = load_runner_module()
    src_path = make_module(tmp_path, "A")
    monkeypatch.setattr(runner, "PROJECT_ROOT", tmp_path)
    captured = {}

    def fake_run(command, **kwargs):
        captured["env"] = kwargs["env"]
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr(runner.subprocess, "run", fake_run)

    result = runner.run_command(
        [sys.executable, "-m", "pytest"],
        "sample",
        timeout=10,
        cwd=tmp_path,
        env_overrides={"COVERAGE_FILE": "/tmp/coverage-contract"},
    )

    assert result.success is True
    assert str(src_path) in captured["env"]["PYTHONPATH"]
    assert captured["env"]["COVERAGE_FILE"] == "/tmp/coverage-contract"


def test_pytest_no_tests_exit_is_a_failure(tmp_path, monkeypatch):
    runner = load_runner_module()
    monkeypatch.setattr(runner, "PROJECT_ROOT", tmp_path)

    def fake_run(command, **kwargs):
        return subprocess.CompletedProcess(
            command,
            runner.PYTEST_NO_TESTS_EXIT_CODE,
            stdout="collected 0 items\n",
            stderr="",
        )

    monkeypatch.setattr(runner.subprocess, "run", fake_run)

    result = runner.run_command(
        [sys.executable, "-m", "pytest"],
        "empty tests",
        timeout=10,
        cwd=tmp_path,
    )

    assert result.success is False
    assert "pytest collected no tests" in result.stderr


def test_non_pytest_no_tests_exit_remains_failure(tmp_path, monkeypatch):
    runner = load_runner_module()
    monkeypatch.setattr(runner, "PROJECT_ROOT", tmp_path)

    def fake_run(command, **kwargs):
        return subprocess.CompletedProcess(
            command,
            runner.PYTEST_NO_TESTS_EXIT_CODE,
            stdout="",
            stderr="",
        )

    monkeypatch.setattr(runner.subprocess, "run", fake_run)

    result = runner.run_command(["python", "script.py"], "script", timeout=10, cwd=tmp_path)

    assert result.success is False


def test_write_summary_decodes_timeout_output_bytes(tmp_path, monkeypatch):
    runner = load_runner_module()
    monkeypatch.setattr(runner, "RESULTS_DIR", tmp_path / "results")
    report = runner.SuiteReport(
        results=[
            runner.CommandResult(
                name="timed out command",
                success=False,
                duration=10.0,
                command=["python", "script.py"],
                stdout=b"partial stdout",
                stderr=b"partial stderr\xff",
            )
        ]
    )

    runner.write_summary(report)

    summary = json.loads((tmp_path / "results" / "summary.json").read_text())
    result = summary["results"][0]
    assert result["stdout_tail"] == "partial stdout"
    assert result["stderr_tail"] == "partial stderr\ufffd"


def test_performance_category_uses_canonical_directory_only(tmp_path, monkeypatch):
    runner = load_runner_module()
    module_path = make_test_module(tmp_path, "SAMPLE")
    performance_file = module_path / "tests" / "performance" / "test_benchmark.py"
    performance_file.write_text("def test_benchmark():\n    assert True\n")
    unit_file = module_path / "tests" / "unit" / "test_performance_monitor.py"
    unit_file.write_text("def test_unit_monitor():\n    assert True\n")
    monkeypatch.setattr(runner, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(runner, "ensure_results_dir", lambda clean=False: None)

    captured = []

    def fake_run(command, name, timeout, cwd=runner.PROJECT_ROOT):
        captured.append((name, command, timeout, cwd))
        return runner.CommandResult(name=name, success=True, duration=0.0, command=command)

    monkeypatch.setattr(runner, "run_command", fake_run)

    report = runner.run_performance_tests(timeout=42)

    assert report.success is True
    assert len(captured) == 1
    assert str(performance_file) in captured[0][1]
    assert str(unit_file) not in captured[0][1]


def test_coverage_category_isolates_modules_and_combines_data(tmp_path, monkeypatch):
    runner = load_runner_module()
    a_src = make_module(tmp_path, "A")
    b_src = make_module(tmp_path, "B")
    for module_name in ("A", "B"):
        test_file = tmp_path / f"GEO-INFER-{module_name}" / "tests" / "unit" / "test_sample.py"
        test_file.parent.mkdir(parents=True)
        test_file.write_text("def test_sample():\n    assert True\n")
    monkeypatch.setattr(runner, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(runner, "RESULTS_DIR", tmp_path / "results")
    runner.RESULTS_DIR.mkdir()
    stale_report = runner.RESULTS_DIR / "OLD_coverage_results.xml"
    stale_report.write_text("stale")
    captured = []

    def fake_run(
        command,
        name,
        timeout,
        cwd=runner.PROJECT_ROOT,
        env_overrides=None,
    ):
        captured.append((name, command, timeout, cwd, env_overrides))
        return runner.CommandResult(name=name, success=True, duration=0.0, command=command)

    monkeypatch.setattr(runner, "run_command", fake_run)

    report = runner.run_coverage_analysis(timeout=42)

    assert report.success is True
    assert not stale_report.exists()
    assert len(captured) == 4
    a_run, b_run, json_run, terminal_run = captured
    assert f"--cov={a_src}" in a_run[1]
    assert f"--cov={b_src}" not in a_run[1]
    assert f"--cov={b_src}" in b_run[1]
    assert f"--cov={a_src}" not in b_run[1]
    assert "--cov-append" in a_run[1] and "--cov-report=" in a_run[1]
    expected_data = str(runner.RESULTS_DIR / ".coverage")
    assert a_run[4] == {"COVERAGE_FILE": expected_data}
    assert b_run[4] == {"COVERAGE_FILE": expected_data}
    assert json_run[1][-2:] == ["-o", str(runner.RESULTS_DIR / "coverage.json")]
    assert terminal_run[1][-2:] == ["report", "--show-missing"]


def test_parse_args_fail_fast_defaults_off(monkeypatch):
    runner = load_runner_module()
    monkeypatch.setattr("sys.argv", ["run_unified_tests.py"])
    assert runner.parse_args().fail_fast is False


def test_parse_args_fail_fast_flag_enables_stopping(monkeypatch):
    runner = load_runner_module()
    monkeypatch.setattr(
        "sys.argv", ["run_unified_tests.py", "--category", "unit", "--fail-fast"]
    )
    args = runner.parse_args()
    assert args.fail_fast is True
    assert args.category == "unit"


def test_fail_fast_stops_after_first_module_failure(tmp_path, monkeypatch):
    runner = load_runner_module()
    make_module(tmp_path, "A")
    make_module(tmp_path, "B")
    for module_name in ("A", "B"):
        test_file = (
            tmp_path / f"GEO-INFER-{module_name}" / "tests" / "unit" / "test_sample.py"
        )
        test_file.parent.mkdir(parents=True)
        test_file.write_text("def test_sample():\n    assert True\n")
    monkeypatch.setattr(runner, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(runner, "ensure_results_dir", lambda clean=False: None)
    captured = []

    def fake_run(command, name, timeout, cwd=runner.PROJECT_ROOT):
        captured.append(name)
        success = not any("GEO-INFER-A" in str(part) for part in command)
        return runner.CommandResult(
            name=name, success=success, duration=0.0, command=command
        )

    monkeypatch.setattr(runner, "run_command", fake_run)

    report = runner.run_module_category_tests("unit", timeout=1, fail_fast=True)

    assert report.success is False
    assert len(captured) == 1
    assert captured[0] == "A unit tests"


def test_default_behavior_runs_all_modules_despite_failure(tmp_path, monkeypatch):
    runner = load_runner_module()
    make_module(tmp_path, "A")
    make_module(tmp_path, "B")
    for module_name in ("A", "B"):
        test_file = (
            tmp_path / f"GEO-INFER-{module_name}" / "tests" / "unit" / "test_sample.py"
        )
        test_file.parent.mkdir(parents=True)
        test_file.write_text("def test_sample():\n    assert True\n")
    monkeypatch.setattr(runner, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(runner, "ensure_results_dir", lambda clean=False: None)
    captured = []

    def fake_run(command, name, timeout, cwd=runner.PROJECT_ROOT):
        captured.append(name)
        success = not any("GEO-INFER-A" in str(part) for part in command)
        return runner.CommandResult(
            name=name, success=success, duration=0.0, command=command
        )

    monkeypatch.setattr(runner, "run_command", fake_run)

    report = runner.run_module_category_tests("unit", timeout=1, fail_fast=False)

    assert report.success is False
    assert len(captured) == 2
    assert captured[0] == "A unit tests"
    assert captured[1] == "B unit tests"
