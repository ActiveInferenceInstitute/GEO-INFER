"""Unit tests for the unified test runner script."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
RUNNER_PATH = REPO_ROOT / "GEO-INFER-TEST" / "run_unified_tests.py"


def load_runner_module():
    spec = importlib.util.spec_from_file_location(
        "geo_infer_run_unified_tests", RUNNER_PATH
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def make_module(root: Path, name: str) -> Path:
    src_path = root / f"GEO-INFER-{name}" / "src"
    src_path.mkdir(parents=True)
    return src_path


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
    )

    assert result.success is True
    assert str(src_path) in captured["env"]["PYTHONPATH"]


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
