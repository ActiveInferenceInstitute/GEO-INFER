# Realms API Testing Guide

## Overview

The `test_realms_api.py` script provides comprehensive testing for all documented Realms API endpoints. It validates responses against the provided JSON schema and generates detailed reports.

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Ensure you have the schema file in the same directory
ls realm_schema.json
```

## Usage

### Basic Usage
```bash
# Run all tests with default parameters
python test_realms_api.py

# Run with custom schema file
python test_realms_api.py --schema /path/to/realm_schema.json

# Quick test mode (fewer test cases)
python test_realms_api.py --quick
```

### Advanced Options
```bash
# Custom search terms
python test_realms_api.py --search-terms "Forest" "Ocean" "Park"

# Custom realm IDs to test
python test_realms_api.py --realm-ids 2188 6472 8155

# Custom timeout
python test_realms_api.py --timeout 60

# Combined options
python test_realms_api.py --quick --search-terms "Avana" --realm-ids 2188
```

## What Gets Tested

### 1. Search Realms by Name
- **Endpoint**: `GET https://api.guardiansofearth.io/realms`
- **Tests**: Multiple search terms with various parameters
- **Validates**: Response structure, required fields, data types

### 2. Get All Realms
- **Endpoint**: `GET https://portal.biosmart.life/api/v1/contest/109/regions.json`
- **Tests**: Pagination, sorting by ID and bioscore
- **Validates**: Schema compliance, data consistency

### 3. Get Realm by ID
- **Endpoint**: `GET https://portal.biosmart.life/api/v1/region/{id}`
- **Tests**: Multiple realm IDs (extracted from previous tests)
- **Validates**: Full schema compliance, ID matching

### 4. Error Cases
- **Tests**: Invalid IDs, malformed parameters, edge cases
- **Validates**: Proper error handling and status codes

## Output

The script generates:

1. **Console Output**: Real-time progress and summary
2. **Log File**: `realms_api_test_YYYYMMDD_HHMMSS.log`
3. **Results File**: `realms_api_test_results_YYYYMMDD_HHMMSS.json`

### Example Output
```
🚀 Starting Comprehensive Realms API Testing
============================================================
Testing: Search Realms by Name
============================================================
✓ GET https://api.guardiansofearth.io/realms - 200 (0.45s)
  Found 2 results for 'Avana'

📊 TEST SUMMARY REPORT
================================================================================
Total Tests:    15
Passed:         14
Failed:         1
Success Rate:   93.3%
Total Duration: 12.34s

📈 ENDPOINT BREAKDOWN:
  search_by_name: 5/5 (100.0%)
  get_all_realms: 6/6 (100.0%)
  get_realm_by_id: 3/4 (75.0%)
```

## Schema Validation

The script validates all responses against `realm_schema.json`:
- Checks data types for all fields
- Validates required fields are present
- Ensures proper structure for arrays and objects
- Reports any schema violations

## Error Handling

- **Network Issues**: Timeout, connection errors
- **HTTP Errors**: 4xx, 5xx status codes  
- **Data Issues**: Invalid JSON, schema violations
- **Rate Limiting**: Built-in delays between requests

## Customization

To test additional scenarios, modify the script:

```python
# Add custom search terms
search_terms = ["YourCustomTerm", "AnotherTerm"]

# Add custom realm IDs
realm_ids = [1234, 5678, 9012]

# Add custom test cases
test_cases = [
    {'name': 'custom_test', 'params': {'limit': 100}}
]
```

## Troubleshooting

### Common Issues

1. **Schema file not found**
   ```bash
   # Ensure schema file exists
   ls realm_schema.json
   ```

2. **Network timeouts**
   ```bash
   # Increase timeout
   python test_realms_api.py --timeout 60
   ```

3. **API rate limiting**
   - The script includes delays between requests
   - Reduce test scope with `--quick` option

4. **Authentication errors**
   - Currently no authentication is documented
   - If needed, modify the script to add API keys/tokens

### What You Need to Know

To use this script effectively, you may need:

1. **API Keys/Authentication**: Not documented but may be required
2. **Rate Limits**: Unknown - script includes basic rate limiting
3. **Base URL Changes**: URLs are hardcoded from documentation
4. **Additional Endpoints**: Script only tests documented endpoints

## Next Steps

If the API requires authentication or has undocumented endpoints, you'll need to provide:

- API keys or authentication tokens
- Additional endpoint URLs
- Rate limiting information
- Error response format documentation 