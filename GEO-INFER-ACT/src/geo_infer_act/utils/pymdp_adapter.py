"""pymdp 1.0.3 runtime adapter for GEO-INFER-ACT.

This module is the only production bridge from GEO-INFER active-inference
runtime code into inferactively-pymdp. It targets the JAX-first 1.0.3 API.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from importlib import metadata
from typing import Any, Dict, List, Optional
import warnings

import numpy as np

EXPECTED_PYMDP_VERSION = "1.0.3"


@dataclass
class PymdpStepResult:
    """Normalized diagnostics from one pymdp Agent perception-action step."""

    beliefs: np.ndarray
    policy_posterior: np.ndarray
    negative_expected_free_energy: np.ndarray
    selected_action_index: int
    free_energy: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_metadata(self) -> Dict[str, Any]:
        """Return JSON-safe pymdp backend metadata."""
        return {
            "backend": "inferactively-pymdp",
            "pymdp_version": self.metadata.get("pymdp_version", EXPECTED_PYMDP_VERSION),
            "h3_version": self.metadata.get("h3_version"),
            "selected_action_index": int(self.selected_action_index),
            "action_posterior": self.policy_posterior.astype(float).tolist(),
            "negative_expected_free_energy": self.negative_expected_free_energy.astype(
                float
            ).tolist(),
            "free_energy": float(self.free_energy),
            **{
                key: value
                for key, value in self.metadata.items()
                if key not in {"pymdp_version", "h3_version"}
            },
        }


def installed_pymdp_version() -> str:
    """Return the installed inferactively-pymdp distribution version."""
    return metadata.version("inferactively-pymdp")


def validate_pymdp_version(expected: str = EXPECTED_PYMDP_VERSION) -> str:
    """Fail unless the exact supported inferactively-pymdp version is installed."""
    version = installed_pymdp_version()
    if version != expected:
        raise RuntimeError(
            f"inferactively-pymdp {expected} is required; installed version is {version}"
        )
    return version


def real_h3_version_metadata() -> Dict[str, Any]:
    """Return h3-py runtime version metadata and fail if h3 is unavailable."""
    import h3  # noqa: PLC0415

    versions = h3.versions()
    return {
        "h3_version": versions.get("python"),
        "h3_c_version": versions.get("c"),
    }


def _normalize_distribution(values: Any) -> np.ndarray:
    array = np.asarray(values, dtype=float).reshape(-1)
    if array.size == 0:
        raise ValueError("pymdp distributions must not be empty")
    if not np.all(np.isfinite(array)):
        raise ValueError("pymdp distributions must contain finite values")
    array = np.maximum(array, 0.0)
    total = float(np.sum(array))
    if total <= 1e-12:
        return np.ones_like(array) / array.size
    return array / total


def _normalize_likelihood(matrix: Any) -> np.ndarray:
    array = np.asarray(matrix, dtype=float)
    if array.ndim != 2:
        raise ValueError(f"Observation model must be 2D, got shape {array.shape}")
    if not np.all(np.isfinite(array)):
        raise ValueError("Observation model must contain finite values")
    array = np.maximum(array, 1e-12)
    col_sums = np.sum(array, axis=0, keepdims=True)
    res = array / np.maximum(col_sums, 1e-12)
    return np.asarray(res, dtype=float)


def _normalize_transition(tensor: Any, state_dim: int, action_count: int) -> np.ndarray:
    array = np.asarray(tensor, dtype=float)
    if array.ndim == 2:
        array = np.repeat(array[:, :, None], action_count, axis=2)
    elif array.ndim != 3:
        raise ValueError(f"Transition model must be 2D or 3D, got shape {array.shape}")
    if array.shape[0] != state_dim or array.shape[1] != state_dim:
        array = np.repeat(np.eye(state_dim)[:, :, None], action_count, axis=2)
    if array.shape[2] != action_count:
        if array.shape[2] > action_count:
            array = array[:, :, :action_count]
        else:
            repeats = [array[:, :, idx % array.shape[2]] for idx in range(action_count)]
            array = np.stack(repeats, axis=2)
    if not np.all(np.isfinite(array)):
        raise ValueError("Transition model must contain finite values")
    array = np.maximum(array, 1e-12)
    sums = np.sum(array, axis=0, keepdims=True)
    res = array / np.maximum(sums, 1e-12)
    return np.asarray(res, dtype=float)


def _preferences_vector(values: Any, obs_dim: int) -> np.ndarray:
    if isinstance(values, dict):
        values = values.get("observations", np.ones(obs_dim) / obs_dim)
    vector = np.asarray(values, dtype=float).reshape(-1)
    if vector.size != obs_dim:
        vector = np.resize(vector, obs_dim)
    if not np.all(np.isfinite(vector)):
        vector = np.zeros(obs_dim, dtype=float)
    return vector.astype(float)


def _belief_vector(values: Any, state_dim: int) -> np.ndarray:
    if isinstance(values, dict):
        values = values.get("states", np.ones(state_dim) / state_dim)
    vector = np.asarray(values, dtype=float).reshape(-1)
    if vector.size != state_dim:
        vector = np.ones(state_dim, dtype=float) / state_dim
    return _normalize_distribution(vector)


def _coerce_action_count(value: Any, default: int = 3) -> int:
    """Return a positive action count from scalar or pymdp-style values."""
    if value is None:
        value = default
    array = np.asarray(value)
    if array.size != 1:
        raise ValueError("action_count must be a scalar or a single-item sequence")
    count = int(array.reshape(-1)[0])
    if count < 1:
        raise ValueError("action_count must be positive")
    return count


def _model_num_controls(model: Any, default: int = 3) -> int:
    """Read and normalize a model's pymdp-style control-count value."""
    value = getattr(model, "num_controls", None)
    if value is None:
        value = getattr(model, "parameters", {}).get("num_controls", default)
    return _coerce_action_count(value, default=default)


def _extract_agent_belief(qs: List[Any]) -> np.ndarray:
    if not qs:
        raise ValueError("pymdp returned no posterior states")
    array = np.asarray(qs[0], dtype=float)
    if array.ndim >= 1:
        array = array.reshape(-1, array.shape[-1])[-1]
    return _normalize_distribution(array)


def _scalar_free_energy(info: Dict[str, Any]) -> float:
    for key in ("vfe", "free_energy", "F"):
        if key in info:
            array = np.asarray(info[key], dtype=float)
            finite = array[np.isfinite(array)]
            if finite.size:
                return float(np.mean(finite))
    components = info.get("vfe_components")
    if isinstance(components, dict):
        values = []
        for value in components.values():
            array = np.asarray(value, dtype=float)
            values.extend(array[np.isfinite(array)].reshape(-1).tolist())
        if values:
            return float(np.mean(values))
    return 0.0


def run_pymdp_step(
    *,
    observation: Any,
    observation_model: Any,
    transition_model: Any,
    preferences: Any,
    prior: Any,
    action_count: int = 3,
    random_seed: int = 0,
    action_selection: str = "deterministic",
) -> PymdpStepResult:
    """Run one real pymdp 1.0.3 categorical perception-policy step."""
    action_count = _coerce_action_count(action_count)
    version = validate_pymdp_version()
    h3_versions = real_h3_version_metadata()

    import jax.numpy as jnp  # noqa: PLC0415
    import jax.random as jr  # noqa: PLC0415
    from pymdp.agent import Agent  # noqa: PLC0415

    observation_vector = _normalize_distribution(observation)
    obs_model = _normalize_likelihood(observation_model)
    obs_dim, state_dim = obs_model.shape
    if observation_vector.size != obs_dim:
        if observation_vector.size == state_dim or obs_dim == 1:
            state_dim = int(observation_vector.size)
            obs_dim = int(observation_vector.size)
            obs_model = np.eye(state_dim, dtype=float)
        else:
            raise ValueError(
                "Observation dimension does not match pymdp observation model: "
                f"{observation_vector.size} != {obs_dim}"
            )
    trans_model = _normalize_transition(transition_model, state_dim, action_count)
    preference_vector = _preferences_vector(preferences, obs_dim)
    prior_vector = _belief_vector(prior, state_dim)

    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="A JAX array is being set as static!*",
            category=UserWarning,
        )
        agent = Agent(
            A=[jnp.asarray(obs_model)],
            B=[jnp.asarray(trans_model)],
            C=[jnp.asarray(preference_vector)],
            D=[jnp.asarray(prior_vector)],
            num_controls=[action_count],
            categorical_obs=True,
            batch_size=1,
            policy_len=1,
            action_selection=action_selection,
            sampling_mode="marginal",
        )
    qs, info = agent.infer_states(
        [jnp.asarray(observation_vector.reshape(1, -1))],
        empirical_prior=agent.D,
        return_info=True,
    )
    q_pi, neg_efe = agent.infer_policies(qs)
    rng_key = jr.split(jr.PRNGKey(int(random_seed)), agent.batch_size)
    action = agent.sample_action(q_pi, rng_key=rng_key)

    q_pi_np = np.asarray(q_pi, dtype=float).reshape(-1)
    neg_efe_np = np.asarray(neg_efe, dtype=float).reshape(-1)
    selected = int(np.asarray(action).reshape(-1)[0])
    selected %= max(1, len(q_pi_np))

    return PymdpStepResult(
        beliefs=_extract_agent_belief(qs),
        policy_posterior=_normalize_distribution(q_pi_np),
        negative_expected_free_energy=neg_efe_np,
        selected_action_index=selected,
        free_energy=_scalar_free_energy(info),
        metadata={
            "pymdp_version": version,
            **h3_versions,
            "action_count": action_count,
            "categorical_obs": True,
            "policy_len": 1,
            "batch_size": 1,
        },
    )


def run_model_step(
    model: Any,
    observation: Any,
    *,
    action_count: Optional[int] = None,
    random_seed: int = 0,
    prior: Any = None,
) -> PymdpStepResult:
    """Run pymdp inference for a GEO-INFER categorical GenerativeModel."""
    if getattr(model, "model_type", None) != "categorical":
        raise ValueError("pymdp adapter currently supports categorical models")
    controls = _coerce_action_count(
        action_count if action_count is not None else _model_num_controls(model)
    )
    return run_pymdp_step(
        observation=observation,
        observation_model=getattr(model, "observation_model"),
        transition_model=getattr(model, "transition_model"),
        preferences=getattr(model, "preferences", None),
        prior=prior if prior is not None else getattr(model, "beliefs", None),
        action_count=controls,
        random_seed=random_seed,
    )
