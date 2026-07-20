# GEO-INFER-TEST Runner Examples

These examples use the current unified runner from the repository root.

## Run a module

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module MATH
```

## Run a category

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --category unit
uv run python GEO-INFER-TEST/run_unified_tests.py --category integration
uv run python GEO-INFER-TEST/run_unified_tests.py --category performance
```

## Narrow a failure with pytest

```bash
uv run python -m pytest -c pyproject.toml -W error \
  GEO-INFER-MATH/tests/unit -q
uv run python -m pytest -c pyproject.toml -W error \
  GEO-INFER-MATH/tests/unit/test_transforms.py -q
```

## Inspect results

```bash
python - <<'PY'
import json
from pathlib import Path

summary = Path(".geo-infer-test-results/summary.json")
if summary.exists():
    report = json.loads(summary.read_text())
    print("success:", report["success"])
    for result in report["results"]:
        print(result["name"], result["success"], result["duration"])
else:
    print("Run a GEO-INFER-TEST command first.")
PY
```

The runner treats pytest exit code 5, skipped/xfail JUnit entries, and command
failures as unsuccessful results. Do not copy fabricated pass counts into docs;
report the output from the current run.
