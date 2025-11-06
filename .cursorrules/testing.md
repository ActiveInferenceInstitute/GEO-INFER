# Testing Requirements

## Unit Testing

- Test all public methods and functions
- Include edge cases and error conditions
- Use appropriate test data that reflects real-world scenarios
- Mock external dependencies, but never internal logic
- Test mathematical correctness of algorithms

## Integration Testing

- Test cross-module interactions
- Validate data flow between modules
- Test API endpoints comprehensively
- Ensure configuration loading works correctly
- Test with real data samples

## Performance Testing

- Benchmark critical algorithms
- Test with realistic data volumes
- Identify and optimize bottlenecks
- Monitor memory usage patterns
- Test scalability with large datasets

## Test Organization

Tests should be organized in the `tests/` directory:
- `tests/unit/` - Unit tests for individual components
- `tests/integration/` - Integration tests for cross-module interactions
- `tests/performance/` - Performance benchmarks and tests

## Running Tests

```bash
# Run all tests
uv run pytest tests/

# Run specific test file
uv run pytest tests/unit/test_core.py

# Run with coverage
uv run pytest tests/ --cov=geo_infer_module --cov-report=html
```

