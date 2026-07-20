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

```python
from geo_infer_risk.core.risk_engine import EnhancedRiskEngine

engine = EnhancedRiskEngine()
result = engine.assess(
    hazard_raster=flood_depth,
    exposure_data=building_footprints,
    vulnerability_curve="residential_flood"
)
print(f"Expected loss: ${result.expected_loss:,.0f}")
print(f"Loss exceedance (100yr): ${result.loss_at_return_period(100):,.0f}")
```

```python
from geo_infer_risk.core.catastrophe_models import EnhancedCatastropheModel

cat_model = EnhancedCatastropheModel(peril="earthquake", region="pacific_ring")
simulations = cat_model.run_monte_carlo(n_simulations=10_000)
print(f"Mean annual loss: ${simulations.mean_annual_loss:,.0f}")
print(f"99th percentile: ${simulations.percentile(99):,.0f}")
```

## Guidelines

- Production paths require configured data sources and do not fabricate risk inputs.
- Spatial correlation uses Cholesky decomposition
- Risk aggregation uses real Moran's I and Monte Carlo
- Test: `uv run python -m pytest GEO-INFER-RISK/tests/ -v`

### Integrations

- **BAYES** → Bayesian uncertainty quantification
- **ECON** → Economic loss and insurance modeling
- **CLIMATE** → Climate-driven hazard projections
- **SPACE** → Spatial correlation of hazards
- **AG** → Crop loss risk assessment
