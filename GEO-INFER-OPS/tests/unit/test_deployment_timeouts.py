"""Timeout-contract tests for DeploymentManager docker operations (PL-02/GS19-44).

Both docker build and push must pass a configurable timeout to subprocess.run
and return False (not raise) when the subprocess exceeds it.
"""

import subprocess
import time

import pytest

from geo_infer_ops.core.config import Config
from geo_infer_ops.core.deployment import DeploymentManager


def _manager() -> DeploymentManager:
    config = Config()
    config.deployment.docker.build_timeout = 1
    config.deployment.docker.push_timeout = 1
    return DeploymentManager(config)


@pytest.fixture()
def hanging_run(monkeypatch):
    """Replace subprocess.run with a real hanging process under the passed timeout."""
    recorded_timeouts = []
    real_run = subprocess.run

    def fake_run(cmd, **kwargs):
        recorded_timeouts.append(kwargs.get("timeout"))
        return real_run(["sleep", "30"], timeout=kwargs.get("timeout"))

    monkeypatch.setattr("geo_infer_ops.core.deployment.subprocess.run", fake_run)
    return recorded_timeouts


def test_build_timeout_returns_false_within_bound(hanging_run):
    started = time.monotonic()
    assert _manager().build_docker_image("wave-test-tag") is False
    assert time.monotonic() - started < 30
    assert hanging_run == [1]


def test_push_timeout_returns_false_within_bound(hanging_run):
    started = time.monotonic()
    assert _manager().push_docker_image("localhost") is False
    assert time.monotonic() - started < 30
    assert hanging_run == [1]


def test_build_passes_configured_timeout_on_success(monkeypatch):
    recorded_timeouts = []

    def fast_run(cmd, **kwargs):
        recorded_timeouts.append(kwargs.get("timeout"))
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr("geo_infer_ops.core.deployment.subprocess.run", fast_run)
    assert _manager().build_docker_image("wave-test-tag") is True
    assert recorded_timeouts == [1]
