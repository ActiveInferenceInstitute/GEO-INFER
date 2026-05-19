# GEO-INFER-ACT Examples

This directory contains thin script wrappers around package-owned Active
Inference runners in `geo_infer_act.runners`. The wrappers keep the historical
example filenames runnable while the real scenario logic, configuration,
schemas, data export, and visualization guarantees live in the package.

## Available Examples

| Example | Canonical scenario | Description |
|---------|--------------------|-------------|
| [`simple_model.py`](simple_model.py) | `simple` | Basic categorical Active Inference |
| [`modern_active_inference.py`](modern_active_inference.py) | `modern` | Modern perception-action diagnostics |
| [`h3_active_inference.py`](h3_active_inference.py) | `h3` | Real H3 v4 spatial inference |
| [`spatial_inference_demo.py`](spatial_inference_demo.py) | `spatial` | Spatially framed belief dynamics |
| [`urban_planning.py`](urban_planning.py) | `urban_planning` | Urban-planning policy diagnostics |
| [`ecological_model.py`](ecological_model.py) | `ecological` | Ecological belief and free-energy dynamics |

## Free Energy Calculations

### Variational Free Energy (VFE)

VFE measures the divergence between beliefs and observations. Lower VFE = better model fit.

**Core implementations:**

- [`core/free_energy.py`](../src/geo_infer_act/core/free_energy.py) - `FreeEnergyCalculator` class
- [`core/spatial_agent.py`](../src/geo_infer_act/core/spatial_agent.py) - `_compute_spatial_free_energy()` for H3 cells
- [`utils/math.py`](../src/geo_infer_act/utils/math.py) - `compute_free_energy_categorical()` utility

### Expected Free Energy (EFE)

EFE guides action selection by balancing epistemic (information-seeking) and pragmatic (goal-directed) value.

**Core implementations:**

- [`core/policy_selection.py`](../src/geo_infer_act/core/policy_selection.py) - `compute_expected_free_energy()`
- [`core/spatial_agent.py`](../src/geo_infer_act/core/spatial_agent.py) - `spatial_action()` for spatial policies
- [`utils/math.py`](../src/geo_infer_act/utils/math.py) - `compute_expected_free_energy()` utility

## Running Examples

```bash
# Run all examples with a suite manifest
uv run --package geo-infer-act --extra dev geo-infer-act-examples \
  --output-dir /tmp/geo-infer-act-examples

# Run quick subset (simple_model + spatial_inference_demo)
uv run --package geo-infer-act --extra dev python GEO-INFER-ACT/examples/run_all_examples.py \
  --quick --output-dir /tmp/geo-infer-act-quick

# Run one configured scenario
uv run --package geo-infer-act --extra dev geo-infer-act-run \
  --scenario h3 \
  --config GEO-INFER-ACT/config/active_inference_run.yaml \
  --output-dir /tmp/geo-infer-act-h3 \
  --seed 42 \
  --timesteps 8

# Individual examples
uv run --package geo-infer-act --extra dev python GEO-INFER-ACT/examples/simple_model.py --output-dir /tmp/act-simple
uv run --package geo-infer-act --extra dev python GEO-INFER-ACT/examples/modern_active_inference.py --output-dir /tmp/act-modern
uv run --package geo-infer-act --extra dev python GEO-INFER-ACT/examples/h3_active_inference.py --output-dir /tmp/act-h3
uv run --package geo-infer-act --extra dev python GEO-INFER-ACT/examples/spatial_inference_demo.py --output-dir /tmp/act-spatial
uv run --package geo-infer-act --extra dev python GEO-INFER-ACT/examples/urban_planning.py --output-dir /tmp/act-urban
uv run --package geo-infer-act --extra dev python GEO-INFER-ACT/examples/ecological_model.py --output-dir /tmp/act-ecological
```

Each scenario writes:

- `manifest.json`: schema version, package version, config provenance,
  generated files, metrics, and validation status.
- `data/full_history.json`: step-level beliefs, observations, actions,
  policies, and free-energy values from `ActiveInferenceAnalyzer`.
- `data/step_metrics.csv`: scenario-normalized tabular diagnostics.
- `data/h3_cells.csv`, `data/h3_cells.geojson`, and
  `data/h3_diagnostics.json`: geospatial cell outputs for `h3` and `spatial`.
- `analysis/*.json`: summary and analyzer diagnostics.
- `visualizations/*`: at least one validated plot unless `--no-visualizations`
  is explicitly passed. Geospatial runs include H3 cell maps, FE/EFE
  evolution, entropy/coherence trends, and an interactive HTML map.
- `visualizations/*.metadata.json` and `visualizations/*.data.csv` or
  `visualizations/*.data.json`: per-figure provenance and plotted-data sidecars.
  PNG files embed the same ACT metadata in the image metadata; HTML maps embed a
  structured JSON metadata block.

The schema files live under `src/geo_infer_act/schemas/`:
`run_config.schema.json`, `run_manifest.schema.json`,
`step_metrics.schema.json`, and `h3_diagnostics.schema.json`.

For `h3` and `spatial`, the examples are smoke tests for the package
geospatial contract: real H3 v4 cells, normalized beliefs, finite VFE/EFE
diagnostics, GIS-ready cell outputs, manifest-referenced visualizations, and
schema-backed data files. The manifest records each artifact's type, MIME type,
SHA-256 digest, sidecar links, plotted metrics, source data files, description,
and alt text.

The script contract is validated with:

```bash
uv run python GEO-INFER-TEST/validate_act_script_orchestration.py
uv run python GEO-INFER-TEST/validate_act_geospatial_contract.py
```

## Documentation Links

For theoretical background on VFE and EFE calculations, see:

- [Free Energy Principle](../docs/free_energy_principle.md) - VFE/EFE theory and equations
- [Mathematical Framework](../docs/mathematical_framework.md) - Detailed mathematical formulations
- [Active Inference Overview](../docs/active_inference_overview.md) - Conceptual introduction
- [Geospatial Applications](../docs/geospatial_applications.md) - Spatial AI applications

## Integration

GEO-INFER-ACT integrates with:

- **SPACE**: Spatial Active Inference models
- **AGENT**: Active Inference agents
- **ANT**: Swarm intelligence with Active Inference
- **BAYES**: Bayesian belief updating

See `GEO-INFER-EXAMPLES` for cross-module integration examples.
