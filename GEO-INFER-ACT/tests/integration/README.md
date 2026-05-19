# GEO-INFER-ACT Integration Tests

Integration tests validate ACT behavior across package boundaries and optional
spatial integrations while staying runnable in a local development environment.

## Primary Files

| File | Coverage |
| --- | --- |
| `test_integration.py` | High-level ACT integration paths. |
| `test_space_integration.py` | GEO-INFER-SPACE/H3 spatial integration contracts. |
| `test_h3_example_smoke.py` | H3 example execution and output smoke coverage. |
| `test_stigmergy.py` | Coordination/stigmergy integration behavior. |

## Commands

```bash
uv run --package geo-infer-act --extra dev python -m pytest GEO-INFER-ACT/tests/integration -q
uv run python GEO-INFER-TEST/validate_act_geospatial_contract.py
uv run python GEO-INFER-TEST/validate_h3_active_inference_contract.py
```

Integration tests are complemented by the comprehensive audit, which runs the
scenario suite and records the generated data and visualizations under
`GEO-INFER-ACT/examples/output/comprehensive_act_audit/`.
