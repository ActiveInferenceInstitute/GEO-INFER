---
name: geo-infer-risk
description: Geospatial risk modeling including catastrophe models, exposure analysis, and underwriting. Use when assessing spatial risk, building catastrophe models, analyzing exposure/hazard/vulnerability, or computing portfolio risk metrics.
prerequisites:
  required:
    - geo-infer-space
    - geo-infer-data
  recommended:
    - geo-infer-bayes
    - geo-infer-math
difficulty: advanced
estimated_time: 60min
examples_dir: ../GEO-INFER-EXAMPLES/examples/
---

# GEO-INFER-RISK

## Instructions

### Core Capabilities

- **Catastrophe models**: Cholesky-decomposition spatial correlation
- **Risk engine**: Moran's I, Geary C, Monte Carlo loss calculation
- **Exposure modeling**: Multi-source data loading (DB, file, stream, API)
- **Hazard modeling**: Spatial hazard assessment and mapping
- **Vulnerability**: Bayesian uncertainty quantification
- **Underwriting**: Rule-based fraud detection, env var API keys

### Key Imports

```python
from geo_infer_risk.core.risk_engine import EnhancedRiskEngine
from geo_infer_risk.core.catastrophe_models import EnhancedCatastropheModel
from geo_infer_risk.core.exposure_model import EnhancedExposureModel
from geo_infer_risk.core.hazard_model import EnhancedHazardModel
```

## Examples

Every snippet below runs against the current API.

Reproducible catastrophe simulation. The seed lives on the config, and all
draws come from the model's own generator, so a run replays exactly and never
disturbs the caller's `numpy.random` stream:

```python
from geo_infer_risk.core.catastrophe_models import (
    CatastropheConfig,
    EnhancedEarthquakeModel,
)

config = CatastropheConfig(
    simulation_years=50, spatial_correlation=False, random_seed=7
)
model = EnhancedEarthquakeModel(config=config)
model.model_parameters = {"mean_depth": 15.0}
events = model.simulate_events(200)
```

Risk metrics from an event loss table. `exposure_years` is how many years the
table spans; omit it and every per-year figure is inflated (a warning says so):

```python
import pandas as pd
from geo_infer_risk.utils.risk_metrics import (
    calculate_aal,
    calculate_pml,
    calculate_annual_aggregate_exceedance_probability,
)

losses = pd.DataFrame(
    {
        "event_id": [event["event_id"] for event in events],
        "hazard_type": ["earthquake"] * len(events),
        "loss": modelled_losses,  # one loss per event
    }
)

aal = calculate_aal(losses, exposure_years=50.0)["total"]
pml_25 = calculate_pml(losses, return_period=25, exposure_years=50.0)
aep = calculate_annual_aggregate_exceedance_probability(
    losses, threshold=5e6, num_years=20_000, random_seed=7, exposure_years=50.0
)
```

`calculate_pml` warns when the requested return period is longer than the
record can resolve; the value is then clamped to the largest observed loss and
understates the tail.

## Reproducibility

Every stochastic entry point in this module takes a `random_seed` and routes it
through `geo_infer_risk.utils.rng.resolve_rng`, which accepts `None`, an `int`,
a `SeedSequence`, a `BitGenerator`, a `numpy.random.Generator`, or a legacy
`RandomState`, and always returns a `Generator`. Consequences worth knowing:

- Passing an `int` makes a run replayable; `0` is a valid seed.
- Passing a `Generator` threads one stream through a whole pipeline.
- `None` means OS entropy, so results are *not* replayable. Calling
  `np.random.seed(...)` does not make them so: this module never reads the
  process-wide singleton, and never advances it either.
- For independent parallel streams use
  `geo_infer_risk.utils.rng.spawn_rng(seed, n)` rather than `seed`, `seed + 1`,
  ... which carries no independence guarantee.
- At boundaries that accept only an `int` seed, such as scikit-learn's
  `random_state`, use `geo_infer_risk.utils.rng.derive_int_seed`.

## Guidelines

- Production paths require configured data sources and do not fabricate risk inputs.
- Spatial correlation uses Cholesky decomposition
- Risk aggregation uses real Moran's I and Monte Carlo
- Exceedance-probability curves use the Weibull plotting position and
  interpolate loss as a function of exceedance probability; return periods
  beyond the record are clamped, not extrapolated
- Pass `exposure_years` to any per-year metric (AAL, OEP, AEP, and the
  annualized EP curve); the fallback treats the table as spanning one year
- Test: `uv run python -m pytest GEO-INFER-RISK/tests/ -v`

### Integrations

- **BAYES** → Bayesian uncertainty quantification
- **ECON** → Economic loss and insurance modeling
- **CLIMATE** → Climate-driven hazard projections
- **SPACE** → Spatial correlation of hazards
- **AG** → Crop loss risk assessment
