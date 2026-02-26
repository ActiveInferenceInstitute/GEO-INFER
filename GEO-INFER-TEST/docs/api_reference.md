# GEO-INFER-TEST API Reference

Complete API reference for the `geo_infer_test` package.

## GeoInferTestRunner

**Module**: `geo_infer_test.core.test_runner`

Unified test execution engine for the GEO-INFER framework.

### Constructor

```python
GeoInferTestRunner(config: Optional[TestConfiguration] = None)
```

### TestConfiguration

```python
@dataclass
class TestConfiguration:
    project_root: Path
    module_prefix: str = "GEO-INFER-"
    timeout: int = 300
    verbose: bool = True
    coverage: bool = False
    markers: Optional[List[str]] = None
```

### Methods

#### `run_module(module_name: str) -> TestResult`

Run tests for a specific module.

| Parameter | Type | Description |
|-----------|------|-------------|
| `module_name` | `str` | Module name without prefix (e.g., `"MATH"`, `"SPACE"`) |

**Returns**: `TestResult` with pass/fail counts, duration, and output.

#### `run_all() -> Dict[str, TestResult]`

Run tests for all discovered modules.

**Returns**: Dictionary mapping module names to `TestResult` objects.

#### `run_by_category(category: str) -> Dict[str, TestResult]`

Run tests filtered by pytest marker.

| Parameter | Type | Description |
|-----------|------|-------------|
| `category` | `str` | Marker name: `"unit"`, `"integration"`, `"system"`, `"performance"` |

**Returns**: Dictionary mapping module names to `TestResult` objects.

---

## TestResult

**Module**: `geo_infer_test.models.types`

Data class representing the outcome of a test run.

```python
@dataclass
class TestResult:
    module: str
    passed: int
    failed: int
    errors: int
    skipped: int
    duration: float
    success: bool
    stdout: str
    stderr: str
```

---

## TestDiscoverer

**Module**: `geo_infer_test.core.test_discoverer`

Dynamic discovery of test files across the GEO-INFER monorepo.

### Methods

#### `discover() -> List[Dict[str, Any]]`

Scan the project root for all GEO-INFER modules with test directories.

**Returns**: List of dictionaries with keys:
- `name` (`str`): Module name (e.g., `"MATH"`).
- `path` (`str`): Full module path.
- `test_path` (`str`): Path to tests directory.
- `has_tests` (`bool`): Whether tests directory is non-empty.

---

## Validators

**Module**: `geo_infer_test.core.validators`

### BaseValidator

Abstract base class for all validators.

```python
class BaseValidator:
    def validate(self, data: Any) -> ValidationResult: ...
```

### DataQualityValidator

Validates data completeness, consistency, and accuracy.

```python
dq = DataQualityValidator()
result = dq.validate(dataset)
```

**Validation checks**:
- Completeness: percentage of non-null values.
- Value range: whether values fall within expected bounds.
- Consistency: internal consistency across related fields.

### SpatialValidator

Validates spatial data properties.

```python
sv = SpatialValidator()
result = sv.validate(geodataframe)
```

**Validation checks**:
- CRS validity and consistency.
- Bounding box within expected range.
- Geometry validity (no self-intersections, empty geometries).
- Resolution consistency.

### PerformanceValidator

Validates runtime and memory usage against thresholds.

```python
pv = PerformanceValidator()
result = pv.validate(function_result, max_duration_s=5.0, max_memory_mb=100)
```

### IoTValidator

Validates IoT sensor data streams.

```python
iot = IoTValidator()
result = iot.validate(sensor_readings)
```

**Validation checks**:
- Timestamp monotonicity and gaps.
- Value range and spike detection.
- Sensor availability and completeness.

### BayesianValidator

Validates Bayesian inference results.

```python
bv = BayesianValidator()
result = bv.validate(posterior_samples)
```

**Validation checks**:
- MCMC convergence diagnostics (R-hat).
- Effective sample size.
- Posterior predictive checks.
- Prior-posterior comparison.

### QualityController

Aggregated quality scoring across all validators.

```python
qc = QualityController()
overall = qc.run_all_validators(dataset)
```

---

## ValidationRule

**Module**: `geo_infer_test.models.types`

Rule definition for custom validation:

```python
@dataclass
class ValidationRule:
    name: str
    description: str
    check_function: Callable
    severity: str  # "error", "warning", "info"
    threshold: Optional[float] = None
```

---

## Performance Monitoring

**Module**: `geo_infer_test.core.performance_monitor`

### BenchmarkRunner

Execute and record benchmarks.

```python
benchmark = BenchmarkRunner()
result = benchmark.run(function, *args, iterations=100)
```

**Returns**: Dictionary with `mean_time`, `std_time`, `min_time`, `max_time`, `iterations`.

### LoadTester

Generate load and measure throughput.

```python
load = LoadTester()
result = load.run(endpoint, concurrent_requests=10, duration_s=30)
```

### MetricsCollector

Collect and aggregate performance metrics over time.

### PerformanceAnalyzer

Analyze performance trends and detect regressions.

---

## Module Health

**Module**: `geo_infer_test.core.module_health`

### ModuleHealthChecker

Check health status of individual modules.

```python
checker = ModuleHealthChecker()
health = checker.check("MATH")
```

**Returns**: Dictionary with import status, test count, dependency satisfaction.

### DependencyChecker

Validate inter-module dependency chains.

```python
dep_checker = DependencyChecker()
result = dep_checker.check_all()
```

### SystemValidator

Framework-wide system validation (all 44 modules).

---

## Log Integration

**Module**: `geo_infer_test.core.log_integration`

### LogIntegration

Connect test execution to logging infrastructure.

### TestLogger

Structured test execution logging.

### LogAnalyzer

Analyze test logs for patterns and trends.

---

## run_full_system_test

**Module**: `geo_infer_test.core.validators`

Convenience function to run the complete system validation:

```python
from geo_infer_test import run_full_system_test

results = run_full_system_test()
print(f"Overall system health: {results['overall_score']}")
```

---

## CLI: run_unified_tests.py

The command-line test runner at `GEO-INFER-TEST/run_unified_tests.py`.

### Usage

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py [OPTIONS]
```

### Options

| Option | Description |
|--------|-------------|
| `--module MODULE` | Run tests for a specific module |
| `--category CATEGORY` | Filter by test category (unit, integration, system, performance) |
| `--timeout SECONDS` | Per-module timeout (default: 300) |
| `--verbose` | Verbose output |
| `--json` | Output results as JSON |

### Module Discovery

The script discovers modules by scanning the project root for directories matching `GEO-INFER-*` that contain a non-empty `tests/` subdirectory.

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All tests passed |
| 1 | Some tests failed |
| 2 | Error during discovery or execution |
