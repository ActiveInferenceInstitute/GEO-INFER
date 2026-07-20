# Writing a Strong GEO-INFER Test

This example shows a focused behavioral test for an existing module. Add tests
to the owning module, not to a new placeholder module.

## Example

```python
import numpy as np

from geo_infer_act import FreeEnergyCalculator


def test_categorical_free_energy_has_decomposable_terms():
    calculator = FreeEnergyCalculator()
    result = calculator.compute_categorical_free_energy(
        beliefs=np.array([0.7, 0.2, 0.1]),
        observations=np.array([0.8, 0.15, 0.05]),
        preferences=np.array([0.6, 0.25, 0.15]),
        return_breakdown=True,
    )

    assert np.isfinite(result.free_energy)
    assert np.isclose(
        result.free_energy,
        result.complexity - result.accuracy,
    )
```

## Test rules

- Assert observable output invariants, not only object existence.
- Use finite, small, deterministic inputs unless randomness is the subject.
- Add invalid-input tests at public boundaries.
- Use the shared `geo_infer_test.testing` assertions when they clarify a
  contract.
- Keep warnings, skips, xfails, and missing dependencies visible.
- Run the focused test, then the module gate and relevant repository validator.

```bash
uv run python -m pytest GEO-INFER-ACT/tests/unit -q
uv run python GEO-INFER-TEST/run_unified_tests.py --module ACT
uv run python GEO-INFER-TEST/validate_test_contracts.py --strict
```
