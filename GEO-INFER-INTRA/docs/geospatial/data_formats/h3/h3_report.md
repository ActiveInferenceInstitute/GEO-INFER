# H3 contract report

This page is a current contract summary, not a historical migration receipt.
The repository requires `h3>=4.5.0,<5` and the current lock resolves `4.5.0`.

The release gate covers:

- real H3 point/cell conversion;
- v4 boundary, neighborhood, hierarchy, and polygon APIs;
- GeoJSON longitude/latitude ordering and closed rings;
- backend availability/version reporting;
- active-inference H3 integration;
- visualization boundary conversion and finite output checks.

Run the authoritative checks from the repository root:

```bash
uv run python GEO-INFER-TEST/validate_h3_active_inference_contract.py
uv run pytest GEO-INFER-SPACE/tests/unit/test_h3_operations_runtime.py -q --no-cov
uv run pytest GEO-INFER-IOT/tests/unit/test_ingestion.py -q --no-cov
```

Any report claiming a different H3 version, module denominator, or test result
is a historical snapshot and must not be used as a current release gate.
