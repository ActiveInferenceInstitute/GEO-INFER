# GEO-INFER Testing Guide

## Overview
This document provides instructions for running tests across the GEO-INFER ecosystem. The testing infrastructure includes:
- Module-specific unit tests
- Cross-module integration tests
- Performance benchmarks
- Coverage analysis

## Test Execution

### 1. Running Individual Module Tests
```bash
# Navigate to module directory
cd GEO-INFER-<MODULE_NAME>

# Execute tests
./tests/run_tests.sh
```

### 2. Running All Tests via Unified Runner
```bash
# Navigate to GEO-INFER-TEST
cd GEO-INFER-TEST

# Execute full test suite
python run_unified_tests.py
```

### 3. Running Specific Test Categories
```bash
# Run only unit tests
python run_unified_tests.py --category unit

# Run performance tests
python run_unified_tests.py --category performance

# Test specific module (e.g., AGENT)
python run_unified_tests.py --module AGENT
```

### 4. Running Cross-Module Integration Tests
```bash
# Execute only integration tests
python run_unified_tests.py --category integration
```

## Test Reports
After test execution, results are available in:
- `test-results/` directory
- JUnit XML reports for CI integration
- HTML reports for visual inspection
- Coverage reports showing code coverage metrics

## Adding New Tests
1. **Module Tests**: Add test files to `GEO-INFER-<MODULE>/tests/`
   - Follow naming convention: `test_*.py`
   - Include `__init__.py` in test directories

2. **Integration Tests**: Add to `GEO-INFER-TEST/tests/integration/`
   - Test interactions between modules
   - Use mocks for external dependencies

3. **Performance Tests**: Mark tests with `@pytest.mark.performance`
   - Include in `test_performance.py` files

## Troubleshooting
- **Missing Dependencies**: Install requirements from `tests/requirements-test.txt`
- **Test Failures**: Check `test-results/` for detailed logs
- **Environment Issues**: Use the virtual environment in `venv/` created by `run_tests.sh`