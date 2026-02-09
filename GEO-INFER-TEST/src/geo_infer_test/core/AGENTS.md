# Agent
: core

## Scope
 This directory contains core components for the module. It provides 4 classes and 0 functions.

## Classes
 and Functions

### TestDiscoverer
 test discovery system for the GEO-INFER ecosystem.

**Methods**:
- `discover_all_tests(modules: List[str]) -> Dict[str, Dict[str, List[str]]]`: Discover all tests for the specified modules.
- `analyze_test_file(file_path: Path) -> Dict`: Analyze a test file to extract metadata.
- `get_test_statistics() -> Dict`: Get statistics about discovered tests.
- `find_cross_module_tests() -> List[Tuple[str, str, str]]`: Find tests that appear to test cross-module functionality.
- `validate_test_structure() -> Dict[str, List[str]]`: Validate the structure of discovered tests.

### TestConfiguration
 Configuration for test execution.

### TestResult
 Result of a test execution.

### GeoInferTestRunner
 Main test runner for the GEO-INFER ecosystem.

**Methods**:
- `discover_tests() -> Dict[str, List[str]]`: Discover all available tests across specified modules.
- `run_all_tests() -> Dict[str, Any]`: Execute all discovered tests with logging and reporting.
- `run_module_tests(module: str) -> Dict[str, Any]`: Run tests for a specific module only.
- `run_cross_module_tests() -> Dict[str, Any]`: Run tests that verify cross-module integration.

## Capabilities

- **4 classes** for core functionality

## Integration

- **Location**: `GEO-INFER-TEST/src/geo_infer_test/core`
- **Type**: Directory Node
