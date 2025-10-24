# GEO-INFER-DATA Examples

This directory contains comprehensive examples demonstrating the capabilities of the GEO-INFER-DATA module. Each example showcases different aspects of the data management system with real-world use cases.

## Examples Overview

### 1. Basic Ingestion Example (`basic_ingestion_example.py`)
**Purpose**: Demonstrates multi-source data ingestion capabilities.

**Features Demonstrated**:
- Multi-source data ingestion from satellite, sensor, and crowdsourced data
- Automatic format detection and validation
- Data quality assessment and reporting
- Parallel processing capabilities

**Use Case**: Environmental monitoring data collection from multiple sources.

**Running the Example**:
```bash
python examples/basic_ingestion_example.py
```

**Expected Output**:
- Ingested data from multiple sources
- Quality reports for each data source
- Validation results and recommendations
- Results saved to `output/ingestion_results.json`

### 2. Adaptive Storage Example (`storage_example.py`)
**Purpose**: Shows adaptive data storage with automatic optimization.

**Features Demonstrated**:
- Multiple storage backends (PostgreSQL, MinIO, Redis)
- Access pattern analysis and optimization
- Spatial and temporal querying
- Storage performance monitoring

**Use Case**: Large-scale geospatial data management with optimization.

**Running the Example**:
```bash
python examples/storage_example.py
```

**Expected Output**:
- Sample datasets stored across different backends
- Optimized queries based on access patterns
- Storage statistics and performance metrics
- Results saved to `output/` directory

### 3. Data Validation Example (`validation_example.py`)
**Purpose**: Comprehensive data validation and quality assurance.

**Features Demonstrated**:
- Multiple validation strategies (completeness, accuracy, consistency)
- Geospatial validation (geometry, coordinates, spatial reference)
- Temporal validation and quality trends
- Improvement recommendations

**Use Case**: Data quality assessment and improvement workflows.

**Running the Example**:
```bash
python examples/validation_example.py
```

**Expected Output**:
- Validation results for valid, invalid, and incomplete data
- Quality scores and issue identification
- Improvement recommendations
- Results saved to `output/validation_results.json`

### 4. API Example (`api_example.py`)
**Purpose**: REST API usage and integration patterns.

**Features Demonstrated**:
- REST API server setup and configuration
- Dataset management operations (CRUD)
- Data ingestion via API
- Search and filtering capabilities

**Use Case**: Building applications that integrate with GEO-INFER-DATA.

**Running the Example**:
```bash
python examples/api_example.py
```

**Expected Output**:
- API server interaction examples
- Dataset creation and retrieval
- Search and ingestion operations
- API metrics and health checks

### 5. ETL Pipeline Example (`etl_pipeline_example.py`)
**Purpose**: Complex ETL workflows with intelligent optimization.

**Features Demonstrated**:
- Multi-step ETL pipeline configuration
- Automatic dependency resolution
- Error recovery and intelligent retry
- Performance monitoring and bottleneck identification

**Use Case**: Automated data processing workflows.

**Running the Example**:
```bash
python examples/etl_pipeline_example.py
```

**Expected Output**:
- Configured ETL pipeline execution
- Transformation step monitoring
- Performance metrics and optimization
- Results saved to `output/etl_pipeline_results.json`

## Directory Structure

```
examples/
├── README.md                    # This documentation
├── basic_ingestion_example.py   # Multi-source data ingestion
├── storage_example.py          # Adaptive storage demonstration
├── validation_example.py       # Data validation showcase
├── api_example.py             # REST API usage
├── etl_pipeline_example.py    # ETL pipeline workflows
└── output/                    # Generated results (created automatically)
    ├── ingestion_results.json
    ├── storage_stats.json
    ├── validation_results.json
    ├── api_results.json
    └── etl_pipeline_results.json
```

## Prerequisites

### System Requirements
- Python 3.9+
- Sufficient disk space for example data
- Network access for some examples (API calls)

### Dependencies
All required dependencies are included in the GEO-INFER-DATA package:
- geopandas
- pandas
- numpy
- fastapi
- uvicorn
- requests
- shapely
- rasterio

### Optional Dependencies
For enhanced functionality:
- h3 (for H3 spatial indexing)
- rtree (for R-tree spatial indexing)
- psycopg2 (for PostgreSQL backend)
- redis (for Redis backend)

## Configuration

### Environment Variables
Set these environment variables for full functionality:

```bash
# Database connections (for storage examples)
export GEO_INFER_DB_HOST=localhost
export GEO_INFER_DB_PORT=5432
export GEO_INFER_DB_USER=geo_infer
export GEO_INFER_DB_PASSWORD=your_password
export GEO_INFER_DB_NAME=geo_infer_data

# API keys (for ingestion examples)
export SATELLITE_API_KEY=your_satellite_api_key
export WEATHER_API_KEY=your_weather_api_key

# Storage configurations
export MINIO_ENDPOINT=localhost:9000
export MINIO_ACCESS_KEY=minioadmin
export MINIO_SECRET_KEY=minioadmin
export REDIS_HOST=localhost
export REDIS_PORT=6379
```

### Configuration Files
Copy and modify example configurations:

```bash
# Copy configuration template
cp ../config/example.yaml config/local.yaml

# Edit with your settings
vim config/local.yaml
```

## Running Examples

### Individual Examples
Run each example separately to see specific functionality:

```bash
# Basic ingestion
python examples/basic_ingestion_example.py

# Storage optimization
python examples/storage_example.py

# Data validation
python examples/validation_example.py

# API integration
python examples/api_example.py

# ETL pipelines
python examples/etl_pipeline_example.py
```

### All Examples
Run all examples in sequence:

```bash
# Run all examples (requires manual execution)
for example in basic_ingestion storage validation api etl_pipeline; do
    echo "Running $example example..."
    python examples/${example}_example.py
done
```

### Development Mode
For development and testing:

```bash
# Install in development mode
pip install -e ../

# Run with debug logging
PYTHONPATH=../ python examples/basic_ingestion_example.py

# Run with profiling
python -m cProfile -s time examples/storage_example.py
```

## Understanding Results

### Output Files
Each example generates results in the `output/` directory:

1. **ingestion_results.json**: Multi-source ingestion results and quality reports
2. **storage_stats.json**: Storage performance and optimization metrics
3. **validation_results.json**: Data validation scores and recommendations
4. **api_results.json**: API interaction results and metrics
5. **etl_pipeline_results.json**: ETL execution metrics and performance data

### Log Analysis
Monitor example execution with logs:

```bash
# Run with verbose logging
python examples/basic_ingestion_example.py 2>&1 | tee ingestion.log

# Analyze performance
grep "Performance\|Time\|Memory" *.log
```

### Visualization
Some examples generate visual outputs:

```bash
# View generated datasets (if geospatial viewer available)
# Results are saved as GeoJSON, CSV, and JSON files
ls -la output/
```

## Troubleshooting

### Common Issues

#### Import Errors
```bash
# Ensure GEO-INFER-DATA is installed
pip install -e ../

# Check Python path
python -c "import geo_infer_data; print(geo_infer_data.__file__)"
```

#### Database Connection Issues
```bash
# Check database connectivity
python -c "
from geo_infer_data.core.storage import AdaptiveDataStorage
storage = AdaptiveDataStorage(['postgresql'])
print('Storage initialized successfully')
"
```

#### Memory Issues
```bash
# Reduce data size in examples
# Edit example files to use smaller datasets
# Look for n_records parameters and reduce them
```

#### API Issues
```bash
# Check API server status
curl http://localhost:8001/health

# View API logs
tail -f /var/log/geo_infer_data/api.log
```

### Performance Optimization

#### For Large Datasets
- Reduce `n_records` in example data generation
- Enable parallel processing where available
- Use appropriate storage backends for data size

#### For Limited Resources
- Use local file backend instead of databases
- Disable real-time monitoring
- Reduce logging level

### Getting Help

1. **Check Logs**: Review generated log files in `output/` or console output
2. **Test Individual Components**: Run unit tests to isolate issues
3. **Validate Configuration**: Ensure configuration files are correct
4. **Check Dependencies**: Verify all required packages are installed

## Integration with GEO-INFER Framework

These examples demonstrate integration patterns with other GEO-INFER modules:

### With GEO-INFER-SPACE
```python
from geo_infer_data.core.storage import AdaptiveDataStorage
from geo_infer_space.core.analytics import SpatialAnalyticsInterface

# Use processed data for spatial analysis
storage = AdaptiveDataStorage(['postgresql'])
analytics = SpatialAnalyticsInterface()

# Query optimized data for analysis
data = await storage.adaptive_query(spatial_bounds=bbox)
results = analytics.analyze_hotspots(data)
```

### With GEO-INFER-AI
```python
from geo_infer_data.core.ingestion import MultiSourceDataIngestion
from geo_infer_ai.core.models import AIModel

# Prepare data for AI training
ingestion = MultiSourceDataIngestion(['satellite', 'sensors'])
training_data = await ingestion.ingest_multi_source(satellite=data, sensors=sensors)

# Train AI model
model = AIModel(model_type='environmental_predictor')
model.train(training_data)
```

### With GEO-INFER-APP
```python
from geo_infer_data.api.service import DataService
from geo_infer_app.core.dashboard import Dashboard

# Create data service for application
data_service = DataService()

# Integrate with dashboard
dashboard = Dashboard()
dashboard.add_data_source(data_service)
dashboard.visualize_datasets()
```

## Contributing

To add new examples:

1. Create example script in `examples/` directory
2. Follow naming convention: `{feature}_example.py`
3. Include comprehensive docstring and comments
4. Add configuration options and error handling
5. Update this README with example description
6. Test with different configurations and data sizes

## Next Steps

After running these examples:

1. **Explore the API**: Use the REST API for application integration
2. **Customize Pipelines**: Modify ETL pipelines for your specific needs
3. **Optimize Performance**: Tune storage and processing for your data characteristics
4. **Integrate with Other Modules**: Connect with other GEO-INFER components
5. **Scale Up**: Test with larger datasets and production configurations

---

**Note**: These examples are designed to be educational and demonstrate best practices. For production use, modify configurations, add error handling, and optimize for your specific requirements.
