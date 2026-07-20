# GEO-INFER-TEST API Reference

This page documents the stable programmatic surfaces used by repository tests
and local tooling. The command-line scripts remain the canonical release gate.

## Test runner

`python
from geo_infer_test import GeoInferTestRunner, TestConfiguration

config = TestConfiguration(
    modules_to_test=["SPACE"],
    test_types=["unit", "integration"],
    parallel_execution=False,
    timeout_seconds=300,
)
runner = GeoInferTestRunner(config)
discovered = runner.discover_tests()
report = runner.run_all_tests()
`

### TestConfiguration

Defined in `geo_infer_test.core.test_runner`.

| Field | Type | Meaning |
| --- | --- | --- |
| `modules_to_test` | `list[str]` | Uppercase module suffixes such as `ACT` or `SPACE`. |
| `test_types` | `list[str]` | Directory categories such as `unit`, `integration`, `performance`, or `load`. |
| `parallel_execution` | `bool` | Run discovered files through the programmatic runner concurrently. |
| `max_workers` | `int` | Executor worker limit when parallel execution is enabled. |
| `timeout_seconds` | `int` | Per-test execution timeout for the programmatic runner. |
| `fail_fast` | `bool` | Stop sequential execution after a FAIL or ERROR result. |
| `coverage_enabled` | `bool` | Retained configuration flag for coverage-aware integrations. |
| `performance_benchmarks` | `bool` | Retained configuration flag for benchmark-aware integrations. |
| `log_integration_enabled` | `bool` | Enable GEO-INFER-LOG integration for runner messages. |

### TestResult

The package exports `geo_infer_test.models.types.TestResult` for validator and
fixture results:

`python
from geo_infer_test import TestResult

result = TestResult(
    test_name="probabilities_are_normalized",
    passed=True,
    duration_seconds=0.12,
    message="ok",
    category="unit",
)
`

The internal runner also uses a richer execution result in
`geo_infer_test.core.test_runner`; consult that source before depending on
internal fields.

## Discovery

`python
from geo_infer_test.core.test_discoverer import TestDiscoverer

discoverer = TestDiscoverer()
tests = discoverer.discover_all_tests(["ACT", "SPACE"])
print(tests)
`

TestDiscoverer.SUPPORTED_TEST_TYPES currently includes `unit`,
`integration`, `performance`, `load`, and `stress`. The unified CLI uses
the narrower release categories described in [the command matrix](index.md).

## Shared assertions

`python
from geo_infer_test import (
    assert_finite,
    assert_model_contract,
    assert_probability,
    assert_seed_replay,
    assert_visualization_manifest,
)
`

Use these against real outputs. They are contract assertions, not substitutes
for behavior tests.

## CLI entry points

The `GEO-INFER-TEST/pyproject.toml` declares:

- `geo-test`
- `geo-test-runner`
- `geo-test-report`

The repository CI invokes the explicit scripts so their paths and flags remain
visible in review. Run `uv run geo-test --help` only after confirming the
corresponding CLI module and arguments in the current checkout.
