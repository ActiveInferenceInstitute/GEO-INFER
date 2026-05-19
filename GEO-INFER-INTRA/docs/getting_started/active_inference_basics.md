# Active Inference Basics

This tutorial uses the current `GEO-INFER-ACT` API. It focuses on the canonical
Active Inference spine: a `GenerativeModel`, an `ActiveInferenceModel`,
free-energy decomposition, and expected-free-energy policy selection.

## Install

```bash
uv run --package geo-infer-act --extra dev python -c "import geo_infer_act; print(geo_infer_act.__version__)"
```

## Build A Categorical Generative Model

```python
import numpy as np

from geo_infer_act import ActiveInferenceModel, GenerativeModel

generative_model = GenerativeModel(
    "categorical",
    {
        "state_dim": 3,
        "obs_dim": 2,
    },
)

# Shape is observations x states. Each column describes p(o | s).
generative_model.observation_model = np.array(
    [
        [0.85, 0.25, 0.10],
        [0.15, 0.75, 0.90],
    ]
)

agent = ActiveInferenceModel(
    model_type="categorical",
    policy_selection_mode="deterministic",
    random_seed=7,
)
agent.set_generative_model(generative_model)
```

## Run One Perception-Action Step

```python
observation = np.array([1.0, 0.0])
result = agent.step(
    observation,
    available_actions=["survey", "restore", "monitor"],
    return_result=True,
)

print(result.beliefs)
print(result.action)
print(result.free_energy)
```

`return_result=True` returns an `ActiveInferenceStepResult`. The default
`agent.step(observation)` return remains the historical `(beliefs, action)` tuple.

## Inspect Free-Energy Terms

```python
from geo_infer_act import FreeEnergyCalculator

calculator = FreeEnergyCalculator()
breakdown = calculator.compute_categorical_free_energy(
    beliefs=np.array([0.7, 0.2, 0.1]),
    observations=np.array([0.8, 0.15, 0.05]),
    preferences=np.array([0.6, 0.25, 0.15]),
    return_breakdown=True,
)

print(breakdown.free_energy)
print(breakdown.complexity - breakdown.accuracy)
print(breakdown.entropy)
```

For categorical models, ACT reports `F = complexity - accuracy` with stable
normalization of beliefs, observations, and preferences.

## Select Policies By Expected Free Energy

```python
from geo_infer_act import PolicySelector

selector = PolicySelector(selection_mode="deterministic", random_seed=11)
policy_result = selector.select_policy(
    beliefs=np.array([0.5, 0.3, 0.2]),
    policies=[
        {"action": "survey", "expected_free_energy": -0.3},
        {"action": "wait", "expected_free_energy": 0.4},
        {"action": "restore", "expected_free_energy": 0.1},
    ],
)

print(policy_result["policy"]["action"])
print(policy_result["evaluation"])
```

Deterministic mode selects the policy with the lowest expected free energy.
Stochastic mode is the default and uses the same expected-free-energy evaluation
with a seedable random generator.

## Add H3 Spatial Context

```python
from geo_infer_space import latlng_to_cell

cell = latlng_to_cell(37.7749, -122.4194, 9)
cell_observation = {cell: np.array([1.0, 0.0])}

print(cell_observation)
```

Use H3 cells as keys for spatial observations, then route the observation arrays
through `ActiveInferenceModel` or the spatial agent utilities in `GEO-INFER-ACT`.

## Verification

```bash
uv run python GEO-INFER-TEST/validate_active_inference_contract.py
uv run --package geo-infer-act --extra dev python -m pytest GEO-INFER-ACT/tests -q
```
