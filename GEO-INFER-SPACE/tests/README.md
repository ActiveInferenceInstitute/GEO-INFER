# GEO-INFER-SPACE Test Suite

This directory contains the comprehensive test suite for the GEO-INFER-SPACE module, organized for logical execution order and clear dependency management.

## 🧪 Test Organization

Tests are organized into four logical categories that reflect the dependency hierarchy:

### 1. **Setup Tests** (`@pytest.mark.setup`)
**Purpose**: Repository setup, OSC integration, and foundational utilities
**Files**: 
- `test_osc_scripts.py` - OSC repository setup and management scripts
- `test_osc_geo.py` - OSC-GEO integration, H3 utilities, and data loading

**Dependencies**: None (foundational)
**Execution Time**: ~30-60 seconds (includes repository cloning)

### 2. **Core Tests** (`@pytest.mark.core`)
**Purpose**: Base modules, unified backend, and core functionality
**Files**:
- `test_base_module.py` - Base analysis module functionality
- `test_core.py` - Core backend initialization and scoring
- `test_unified_backend.py` - Unified H3 backend comprehensive testing

**Dependencies**: Setup tests (requires OSC integration)
**Execution Time**: ~10-20 seconds

### 3. **Spatial Tests** (`@pytest.mark.spatial`)
**Purpose**: Data processing, spatial operations, and place analysis
**Files**:
- `test_data_integrator.py` - Multi-source data integration and CRS harmonization
- `test_spatial_processor.py` - Spatial analysis operations (buffer, proximity)
- `test_place_analyzer.py` - Place-based analysis and spatial workflows

**Dependencies**: Core tests (requires backend functionality)
**Execution Time**: ~15-25 seconds

### 4. **Reporting Tests** (`@pytest.mark.reporting`)
**Purpose**: Visualization, reporting, and dashboard generation
**Files**:
- `test_enhanced_reporting.py` - Enhanced status reporting with visualizations
- `test_visualization_engine.py` - Interactive dashboard generation

**Dependencies**: Spatial tests (requires processed data)
**Execution Time**: ~20-30 seconds

## 🚀 Running Tests

### Option 1: Run All Tests in Logical Order
```bash
# From the tests directory
python run_tests_in_order.py

# With verbose output
python run_tests_in_order.py --verbose
```

### Option 2: Run Specific Categories
```bash
# Run only setup tests
python run_tests_in_order.py --category setup

# Run only core functionality tests
python run_tests_in_order.py --category core

# Run only spatial analysis tests
python run_tests_in_order.py --category spatial

# Run only reporting tests
python run_tests_in_order.py --category reporting
```

### Option 3: Use pytest directly
```bash
# Run all tests with automatic ordering
python -m pytest

# Run specific category
python -m pytest -m setup
python -m pytest -m core
python -m pytest -m spatial
python -m pytest -m reporting

# Run with verbose output
python -m pytest -v

# Run with test durations
python -m pytest --durations=10
```

## 📊 Test Execution Flow

```
┌─────────────────┐
│   Setup Tests   │ ← Repository setup, OSC integration
│                 │
│ • OSC Scripts   │
│ • OSC-GEO       │
│ • H3 Utils      │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│   Core Tests    │ ← Base modules and backend
│                 │
│ • Base Module   │
│ • Core Backend  │
│ • Unified Backend│
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Spatial Tests  │ ← Data processing and analysis
│                 │
│ • Data Integrator│
│ • Spatial Proc  │
│ • Place Analyzer│
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Reporting Tests │ ← Visualization and output
│                 │
│ • Enhanced Rep  │
│ • Visualization │
└─────────────────┘
```

## 🔧 Test Configuration

### pytest.ini
- **Test Discovery**: Automatically finds `test_*.py` files
- **Markers**: Defines test categories (`setup`, `core`, `spatial`, `reporting`)
- **Output**: Short tracebacks, duration reporting
- **Ordering**: Automatic dependency-based ordering

### conftest.py
- **Fixtures**: Shared test fixtures and mocks
- **Ordering**: Custom test collection modification for logical execution
- **Mocking**: H3 data loader mocking for isolated testing

## 🧪 Test Types

### Unit Tests
- Test individual functions and methods
- Use mocked dependencies
- Fast execution (< 1 second each)
- Marked with `@pytest.mark.unit`

### Integration Tests
- Test cross-module interactions
- Use real OSC repositories
- Slower execution (5-30 seconds each)
- Marked with `@pytest.mark.integration`

### Setup Tests
- Test repository setup and configuration
- May involve external dependencies
- Variable execution time
- Marked with `@pytest.mark.setup`

## 📁 Test Data Management

### Temporary Data
- Tests create temporary directories and files
- Automatic cleanup in `tearDown()` methods
- Use `tmp_path` fixture for pytest-managed temp directories

### Sample Data
- Standard GeoJSON fixtures in `conftest.py`
- Realistic test geometries and properties
- Consistent coordinate reference systems

### Mock Data
- H3 data loader mocking for isolated testing
- Simulated OSC repository responses
- Controlled test environments

## 🐛 Debugging Tests

### Verbose Output
```bash
python -m pytest -v -s
```

### Run Single Test
```bash
python -m pytest tests/test_core.py::test_backend_init -v
```

### Debug with pdb
```bash
python -m pytest --pdb
```

### Test Coverage
```bash
python -m pytest --cov=geo_infer_space --cov-report=html
```

## 📈 Performance Considerations

### Test Execution Times
- **Setup Tests**: 30-60 seconds (repository operations)
- **Core Tests**: 10-20 seconds (backend operations)
- **Spatial Tests**: 15-25 seconds (data processing)
- **Reporting Tests**: 20-30 seconds (visualization)

### Optimization Tips
- Run specific categories during development
- Use `--tb=short` for faster output
- Skip integration tests with `-m "not integration"`
- Use parallel execution with `pytest-xdist`

## 🔄 Continuous Integration

### GitHub Actions
Tests are automatically run in CI with the following order:
1. Setup tests (validate environment)
2. Core tests (validate functionality)
3. Spatial tests (validate processing)
4. Reporting tests (validate output)

### Local Development
```bash
# Quick validation (core tests only)
python run_tests_in_order.py --category core

# Full validation (all tests)
python run_tests_in_order.py --verbose
```

## 📝 Adding New Tests

### Test File Naming
- Use `test_*.py` naming convention
- Group related functionality in single files
- Follow existing patterns for consistency

### Test Marking
```python
@pytest.mark.setup    # Repository setup tests
@pytest.mark.core     # Core functionality tests
@pytest.mark.spatial  # Spatial analysis tests
@pytest.mark.reporting # Reporting and visualization tests
```

### Test Organization
```python
# 1. Import statements
import pytest
from geo_infer_space.module import Class

# 2. Test class with appropriate marker
@pytest.mark.category
class TestClassName(unittest.TestCase):
    
    def setUp(self):
        # Setup test data and fixtures
        
    def tearDown(self):
        # Cleanup temporary files
        
    def test_specific_functionality(self):
        # Test implementation
```

## 🎯 Best Practices

1. **Dependency Order**: Always consider test dependencies when adding new tests
2. **Isolation**: Use mocks and fixtures to isolate test units
3. **Cleanup**: Always clean up temporary files and directories
4. **Documentation**: Include clear docstrings for test methods
5. **Real Data**: Use realistic test data that reflects actual usage patterns
6. **Error Handling**: Test both success and failure scenarios
7. **Performance**: Keep individual tests fast (< 5 seconds when possible)

## 🚨 Troubleshooting

### Common Issues

**IDE Crashes During Tests**
- Run tests incrementally by category
- Use `--tb=short` to reduce output
- Check for memory-intensive operations

**Test Dependencies**
- Ensure tests run in logical order
- Use appropriate markers for categorization
- Check fixture dependencies

**OSC Repository Issues**
- Verify OSC_REPOS_DIR environment variable
- Check network connectivity for repository cloning
- Validate repository permissions

**H3 Integration Issues**
- Verify H3 library installation
- Check H3 version compatibility (v4.x)
- Validate coordinate reference systems 