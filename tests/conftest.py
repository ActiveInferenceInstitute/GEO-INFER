"""Fixtures for the manuscript-generator regression suite.

These tests exercise ``manuscript/generate_research_artifacts.py`` directly.
The generator is a standalone script rather than an installed package, so it is
loaded by path and registered under a stable module name (frozen dataclasses
need their defining module to be importable while the class body executes).
"""

from __future__ import annotations

import hashlib
import importlib.util
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
GENERATOR_PATH = REPO_ROOT / "manuscript" / "generate_research_artifacts.py"
GENERATOR_MODULE = "geo_infer_manuscript_generator"


def _load_generator() -> ModuleType:
    if GENERATOR_MODULE in sys.modules:
        return sys.modules[GENERATOR_MODULE]
    spec = importlib.util.spec_from_file_location(GENERATOR_MODULE, GENERATOR_PATH)
    if spec is None or spec.loader is None:  # pragma: no cover - import plumbing
        raise RuntimeError(f"cannot load generator from {GENERATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[GENERATOR_MODULE] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="session")
def generator() -> ModuleType:
    """The manuscript generator module under test."""
    return _load_generator()


@pytest.fixture(scope="session")
def repo_root() -> Path:
    """The real GEO-INFER checkout these tests measure."""
    return REPO_ROOT


@pytest.fixture(scope="session")
def repo_inventory(generator: ModuleType, repo_root: Path):
    """One measured inventory of the real checkout, shared by the suite."""
    return generator.collect_inventory(repo_root)


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    """An initialised, committed, clean git repository."""
    root = tmp_path / "checkout"
    root.mkdir()
    (root / "seed.txt").write_text("seed\n", encoding="utf-8")
    env = {
        "GIT_AUTHOR_NAME": "test",
        "GIT_AUTHOR_EMAIL": "test@example.invalid",
        "GIT_COMMITTER_NAME": "test",
        "GIT_COMMITTER_EMAIL": "test@example.invalid",
        "PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin",
        "HOME": str(tmp_path),
    }
    for args in (
        ["init", "-q", "-b", "main"],
        ["add", "-A"],
        ["commit", "-q", "-m", "seed"],
    ):
        subprocess.run(
            ["git", "-C", str(root), *args], check=True, env=env, capture_output=True
        )
    return root


def _output_tree_digest(root: Path) -> str:
    """A fingerprint of the shipped artifact tree, path and content."""
    output = root / "output"
    if not output.is_dir():
        return "absent"
    digest = hashlib.sha256()
    for path in sorted(output.rglob("*")):
        if not path.is_file():
            continue
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


@pytest.fixture(scope="session", autouse=True)
def shipped_artifacts_are_read_only(repo_root: Path):
    """Fail the session if any test rewrites the shipped ``output/`` tree.

    ``output/`` is what the repository publishes: the resolved manuscript, the
    figures, and the evidence record whose commands take minutes to produce.
    A test that runs the real generator or the real render shim against the
    real checkout rewrites all three, and a later assertion then certifies
    whatever it wrote.  Reproduced twice: ``pytest tests/`` replaced the
    eleven-group evidence bundle with a seven-group one and the suite passed.

    Every test that needs a generator run has a checkout of its own — a
    synthetic tree, ``git_repo``, or ``shim_checkout``.  This fixture is the
    gate that keeps it that way, so the rule holds for tests not yet written.
    """
    before = _output_tree_digest(repo_root)
    yield
    after = _output_tree_digest(repo_root)
    if before != after:
        pytest.fail(
            "the test session rewrote the shipped output/ tree: digest "
            f"{before[:16]} -> {after[:16]}. Run the generator against a "
            "checkout of the test's own (see the shim_checkout fixture), "
            "never against repo_root."
        )
