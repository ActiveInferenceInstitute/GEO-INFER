# Agent: integration

## Scope
This agent handles integration tests for GEO-INFER-DATA testing complete workflows from ingestion through storage and validation.

## Implementation Status

### Currently Implemented

- ✅ **test_end_to_end.py**: End-to-end integration tests for complete data management workflows

## Test Coverage

### End-to-End Workflows
- Complete ingestion → storage → validation workflows
- Multi-source data integration
- ETL pipeline execution
- API integration testing

## Running Tests

```bash
# Run integration tests
pytest tests/integration/

# Run specific test
pytest tests/integration/test_end_to_end.py

# Run with verbose output
pytest tests/integration/ -v```

## Integration

- **Location**: `GEO-INFER-DATA/tests/integration`
- **Purpose**: End-to-end workflow testing
- **Test Framework**: pytest
- **Coverage**: Complete system workflows

---

This AGENTS.md documents integration tests for GEO-INFER-DATA.
