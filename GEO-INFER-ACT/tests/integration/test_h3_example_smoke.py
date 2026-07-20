"""Smoke tests for the H3 Active Inference example."""

from __future__ import annotations

import importlib.util
import math
import tempfile
from pathlib import Path

import numpy as np


EXAMPLE_PATH = (
    Path(__file__).resolve().parents[2] / "examples" / "h3_active_inference.py"
)


def _load_example_module():
    spec = importlib.util.spec_from_file_location("h3_active_inference", EXAMPLE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_h3_active_inference_example_smoke_uses_temp_output_only():
    """Run the example's H3 simulation path with temporary output scope."""
    module = _load_example_module()

    with tempfile.TemporaryDirectory() as tmpdir:
        result = module.run_h3_active_inference(
            output_dir=Path(tmpdir),
            h3_resolution=7,
            timesteps=2,
            n_agents=2,
            spatial_seed=7,
        )

    assert "error" not in result
    assert result["simulation_params"]["n_cells"] > 0
    assert result["simulation_params"]["timesteps"] == 2
    assert math.isfinite(result["metrics"]["final_free_energy"])
    assert result["history"]
    for timestep in result["history"]:
        assert math.isfinite(timestep["global_metrics"]["average_free_energy"])
        for payload in timestep["cells"].values():
            beliefs = np.asarray(payload["beliefs"], dtype=float)
            assert np.all(np.isfinite(beliefs))
            assert np.all(beliefs >= 0)
            assert np.isclose(np.sum(beliefs), 1.0)
