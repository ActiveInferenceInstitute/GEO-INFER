# GEO-INFER-SPACE Examples

This directory contains working examples for H3 v4 spatial indexing and
geospatial analysis. H3 examples use
`SpatialIndexingInterface(backend="h3")`, the same contract consumed by
GEO-INFER-ACT H3 Active Inference methods.

For Active Inference runs, SPACE supplies the real H3 v4 cell contract and ACT
owns the manifest, diagnostics, visualization metadata, and figure sidecar
outputs. The canonical output contract is
[`GEO-INFER-ACT/docs/geospatial_applications.md`](../../GEO-INFER-ACT/docs/geospatial_applications.md).

## Available Examples

| Example | Purpose |
| --- | --- |
| `h3_comprehensive_examples.py` | H3 v4 cell operations, hierarchies, and spatial queries |
| `h3_integration_examples.py` | H3 v4 usage with other GEO-INFER modules |
| `h3_advanced_applications.py` | H3 v4 clustering, interpolation, and analysis |
| `multiple_dispatch_demo.py` | Backend-agnostic spatial operations with dispatcher selection |
| `nested_orchestrator_examples.py` | Complex spatial analysis workflows using nested orchestrators |

## Running Examples

```bash
uv run --package geo-infer-space --extra dev python GEO-INFER-SPACE/examples/h3_comprehensive_examples.py
uv run --package geo-infer-space --extra dev python GEO-INFER-SPACE/examples/h3_integration_examples.py
uv run --package geo-infer-space --extra dev python GEO-INFER-SPACE/examples/h3_advanced_applications.py
uv run --package geo-infer-space --extra dev python GEO-INFER-SPACE/examples/multiple_dispatch_demo.py
uv run --package geo-infer-space --extra dev python GEO-INFER-SPACE/examples/nested_orchestrator_examples.py
```

## H3 Contract Validation

```bash
uv run python GEO-INFER-TEST/validate_h3_active_inference_contract.py
uv run --package geo-infer-space --extra dev python -m pytest GEO-INFER-SPACE/tests -q --tb=short
```

## Integration

GEO-INFER-SPACE integrates with:

- `TIME`: spatio-temporal analysis
- `DATA`: spatial data management
- `AI`: spatial feature engineering
- Domain modules: shared spatial analysis for module-specific applications

See `GEO-INFER-EXAMPLES` for cross-module integration examples.
