# Agent: performance

## Scope
This agent handles performance tests and benchmarks for GEO-INFER-DATA operations.

## Implementation Status

### Currently Implemented

- ✅ **test_benchmarks.py**: Performance benchmarks for data operations

## Performance Tests

### Benchmark Coverage
- Data ingestion performance
- Storage operation performance
- Query performance
- Validation performance
- ETL pipeline performance

## Running Tests

```bash
# Run performance tests
pytest tests/performance/

# Run with profiling
pytest tests/performance/ --profile

# Run specific benchmark
pytest tests/performance/test_benchmarks.py::test_ingestion_benchmark
```

## Integration

- **Location**: `GEO-INFER-DATA/tests/performance`
- **Purpose**: Performance benchmarking and validation
- **Test Framework**: pytest with profiling support

---

This AGENTS.md documents performance tests for GEO-INFER-DATA.
