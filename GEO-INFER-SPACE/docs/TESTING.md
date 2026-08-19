# Testing GEO-INFER-SPACE

Run the module suite from the repository root in the shared uv environment:

```bash
uv run pytest GEO-INFER-SPACE/tests/ -q
```

For focused H3 v4 regression coverage and the repository-wide API contract:

```bash
uv run pytest GEO-INFER-SPACE/tests/unit/test_h3_operations_runtime.py -q
uv run python GEO-INFER-TEST/validate_h3_active_inference_contract.py
```

Test execution is owned by pytest and `GEO-INFER-TEST/run_unified_tests.py`;
SPACE does not publish a separate test runner or migration command.
