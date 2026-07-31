# SPACE command-line validation

The SPACE package does not currently publish H3 migration CLI entry points.
Use the repository-owned Python gates instead of invoking undocumented `gis-*`
commands:

```bash
uv run python GEO-INFER-TEST/validate_h3_active_inference_contract.py
uv run pytest GEO-INFER-SPACE/tests/unit/test_h3_operations_runtime.py -q --no-cov
uv run python GEO-INFER-TEST/rewrite_readme_agents.py --check
```

The historical migration utility at
`GEO-INFER-SPACE/tests/h3_v4_framework_upgrade.py` is an inspection/reference
script, not a safe default command: its migration mode can rewrite files.
