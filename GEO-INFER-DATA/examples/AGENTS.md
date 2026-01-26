# Agent
: examples

## Scop
e
This agent handles example scripts demonstrating GEO-INFER-DATA capabilities including API usage, data ingestion, ETL pipelines, storage operations, and data validation.

## Implementation
 Status

### Currentl
y
 Implemented

- ✅ **api_example.py**: REST API usage examples
- ✅ **basic_ingestion_example.py**: Multi-source data ingestion examples
- ✅ **etl_pipeline_example.py**: ETL pipeline workflow examples
- ✅ **storage_example.py**: Adaptive storage usage examples
- ✅ **validation_example.py**: Data validation and quality assurance examples

## Example
 Scripts

### 1
. API Example

```python
# api_example
.py
from geo_infer_data.api import DataAPI

api = DataAPI(config_path='config/local.yaml')
api.start()
# Demonstrates
 API endpoints for data access
```

### 2
. Basic Ingestion Example

```python
# basic_ingestion_example
.py
from geo_infer_data.core.ingestion import MultiSourceDataIngestion

ingestion = MultiSourceDataIngestion(
    data_sources=['satellite', 'sensors'],
    validation_enabled=True
)
# Demonstrates
 multi-source data ingestion
```

### 3
. ETL Pipeline Example

```python
# etl_pipeline_example
.py
from geo_infer_data.core.pipeline import IntelligentETLPipeline

pipeline = IntelligentETLPipeline(
    workflow_config='etl_config.yaml',
    dependency_resolution='automatic'
)
# Demonstrates
 ETL workflow execution
```

### 4
. Storage Example

```python
# storage_example
.py
from geo_infer_data.core.storage import AdaptiveDataStorage

storage = AdaptiveDataStorage(
    storage_backends=['postgresql', 'minio'],
    optimization_strategy='access_pattern_based'
)
# Demonstrates
 adaptive storage operations
```

### 5
. Validation Example

```python
# validation_example
.py
from geo_infer_data.core.validation import DataQualityManager

quality_manager = DataQualityManager(
    validation_rules='comprehensive'
)
# Demonstrates
 data quality validation
```

## Usag
e

Run examples individually:
```bash
python examples/api_example.py
python examples/basic_ingestion_example.py
python examples/etl_pipeline_example.py
python examples/storage_example.py
python examples/validation_example.py
```

## Integratio
n

- **Location**: `GEO-INFER-DATA/examples`
- **Purpose**: Demonstration scripts for data management operations
- **Used By**: Developers learning GEO-INFER-DATA capabilities

---

This AGENTS.md documents example scripts for GEO-INFER-DATA.
