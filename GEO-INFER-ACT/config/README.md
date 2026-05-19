# GEO-INFER-ACT Config

This folder contains checked-in configuration examples for the ACT module.

## Files

- `example.yaml`: broader module configuration for computation, integration,
  and logging.
- `active_inference_run.yaml`: versioned scenario-run contract consumed by
  `geo-infer-act-run`, legacy example wrappers, and tests.

Run a configured scenario from the repository root:

```bash
uv run --package geo-infer-act --extra dev geo-infer-act-run \
  --config GEO-INFER-ACT/config/active_inference_run.yaml \
  --output-dir /tmp/geo-infer-act-run
```
