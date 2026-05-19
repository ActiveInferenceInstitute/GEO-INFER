# geo_infer_act.api

This package provides lightweight API-facing wrappers around the canonical ACT
core. The local facade is used by tests and examples; the REST client and
endpoint map are intentionally thin helpers.

## Modules

| Module | Public surface | Purpose |
| --- | --- | --- |
| `interface.py` | `ActiveInferenceInterface` | Create ACT models, update beliefs, select policies, run steps, set preferences, and return model summaries through a stable local facade. |
| `client.py` | `Client` | Minimal HTTP client for external services exposing `/models` style endpoints. |
| `endpoints.py` | `create_endpoints()` | Shared endpoint-name map for model, belief, and policy routes. |

## Local Usage

```python
import numpy as np
from geo_infer_act.api.interface import ActiveInferenceInterface

api = ActiveInferenceInterface()
api.create_model("audit", "categorical", {"state_dim": 3, "obs_dim": 3})
beliefs = api.update_beliefs("audit", {"observations": np.array([1.0, 0.0, 0.0])})
policy = api.select_policy("audit")
```

## Verification

```bash
uv run --package geo-infer-act --extra dev python -m pytest GEO-INFER-ACT/tests/unit/test_api.py -q
uv run --package geo-infer-act --extra dev python GEO-INFER-ACT/verify_comprehensive.py \
  --output-dir GEO-INFER-ACT/examples/output/comprehensive_act_audit
```

The comprehensive audit records API-facade evidence in
`examples/output/comprehensive_act_audit/method_audit/api_interface/`.
