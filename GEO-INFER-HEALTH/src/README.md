# GEO-INFER-HEALTH Source Code

This directory contains the core implementation of the GEO-INFER-HEALTH module, providing geospatial applications for public health and epidemiology within the GEO-INFER framework.

## Directory Structure

```
src/
├── geo_infer_health/
│   ├── __init__.py                    # Package initialization
│   ├── api/                          # API interfaces and endpoints
│   │   └── __init__.py
│   ├── core/                         # Core health analysis components
│   │   ├── __init__.py
│   │   ├── disease_surveillance.py   # Disease monitoring and outbreak detection
│   │   ├── enhanced_disease_surveillance.py # Advanced surveillance with Active Inference
│   │   ├── environmental_health.py   # Environmental health analysis
│   │   └── healthcare_accessibility.py # Healthcare access analysis
│   ├── models/                       # Data models and schemas
│   │   ├── __init__.py
│   │   └── data_models.py            # Health data models
│   ├── utils/                        # Utility functions
│   │   ├── __init__.py
│   │   ├── advanced_geospatial.py   # Advanced geospatial utilities
│   │   ├── config.py                 # Configuration management
│   │   ├── geospatial_utils.py      # Basic geospatial utilities
│   │   └── logging.py                # Logging utilities
│   └── visualizations/               # Health data visualization
│       └── __init__.py
```

## Core Components

### Disease Surveillance Engine

**Location**: `core/disease_surveillance.py`

Real-time disease monitoring and outbreak detection:

```python
from geo_infer_health.core.disease_surveillance import DiseaseHotspotAnalyzer

# Initialize disease surveillance
surveillance = DiseaseHotspotAnalyzer(reports=disease_reports, population_data=population)

# Identify disease hotspots
hotspots = surveillance.identify_simple_hotspots(
    threshold_case_count=5,
    scan_radius_km=1.0,
    min_density_cases_per_sq_km=10.0
)

# Calculate local incidence rates
incidence_rate = surveillance.calculate_local_incidence_rate(
    center_loc=(37.7749, -122.4194),
    radius_km=2.0,
    time_window_days=7
)
```

### Enhanced Disease Surveillance

**Location**: `core/enhanced_disease_surveillance.py`

Advanced disease surveillance with Active Inference:

```python
from geo_infer_health.core.enhanced_disease_surveillance import ActiveInferenceDiseaseAnalyzer

# Initialize enhanced surveillance
enhanced_surveillance = ActiveInferenceDiseaseAnalyzer(
    reports=disease_reports,
    population_data=population
)

# Analyze with Active Inference
analysis = enhanced_surveillance.analyze_with_active_inference(
    time_window_days=7
)

# Get predictive insights
predictions = enhanced_surveillance.generate_predictions()
risk_assessment = enhanced_surveillance.assess_overall_risk()
```

### Environmental Health Analysis

**Location**: `core/environmental_health.py`

Environmental factors affecting public health:

```python
from geo_infer_health.core.environmental_health import EnvironmentalHealthAnalyzer

# Initialize environmental health analysis
env_health = EnvironmentalHealthAnalyzer(environmental_readings=env_data)

# Get environmental readings near location
readings = env_health.get_environmental_readings_near_location(
    center_loc=(37.7749, -122.4194),
    radius_km=5.0,
    parameter_name="PM2.5"
)

# Calculate average exposure
exposure = env_health.calculate_average_exposure(
    target_locations=[(37.7749, -122.4194)],
    radius_km=2.0,
    parameter_name="PM2.5",
    time_window_days=30
)
```

### Healthcare Accessibility Analysis

**Location**: `core/healthcare_accessibility.py`

Analysis of healthcare service accessibility:

```python
from geo_infer_health.core.healthcare_accessibility import HealthcareAccessibilityAnalyzer

# Initialize accessibility analysis
accessibility = HealthcareAccessibilityAnalyzer(
    facilities=health_facilities,
    population_data=population
)

# Find nearby facilities
nearby = accessibility.find_facilities_in_radius(
    center_loc=(37.7749, -122.4194),
    radius_km=10.0,
    facility_type="hospital"
)

# Get nearest facility
nearest, distance = accessibility.get_nearest_facility(
    loc=(37.7749, -122.4194),
    facility_type="emergency_care"
)
```

## API Layer

### Health API Endpoints

**Location**: `api/`

RESTful API for health data and analysis:

```python
from geo_infer_health.api import disease_surveillance_router, environmental_router, accessibility_router

# Disease surveillance endpoints
@app.post("/health/disease/reports")
async def submit_disease_report(report: DiseaseReport):
    return await submit_disease_report(report)

@app.get("/health/disease/hotspots")
async def identify_hotspots():
    return await identify_disease_hotspots()

# Environmental health endpoints
@app.post("/health/environmental/readings")
async def submit_environmental_reading(reading: EnvironmentalData):
    return await submit_environmental_reading(reading)

# Healthcare accessibility endpoints
@app.get("/health/accessibility/facilities")
async def get_health_facilities():
    return await get_all_health_facilities()
```

## Data Models

### Health Data Models

**Location**: `models/data_models.py`

Comprehensive data models for health applications:

```python
from geo_infer_health.models.data_models import (
    Location, HealthFacility, DiseaseReport,
    PopulationData, EnvironmentalData
)

# Create location
location = Location(latitude=37.7749, longitude=-122.4194)

# Create health facility
facility = HealthFacility(
    facility_id="HOSP_001",
    name="General Hospital",
    facility_type="hospital",
    location=location,
    capacity=500
)

# Create disease report
report = DiseaseReport(
    report_id="RPT_001",
    disease_code="COVID-19",
    location=location,
    report_date=datetime.now(),
    case_count=5
)

# Create population data
population = PopulationData(
    area_id="ZIP_94102",
    population_count=25000
)

# Create environmental data
env_data = EnvironmentalData(
    data_id="ENV_001",
    parameter_name="PM2.5",
    value=15.5,
    unit="μg/m³",
    location=location,
    timestamp=datetime.now()
)
```

## Utility Functions

### Advanced Geospatial Utilities

**Location**: `utils/advanced_geospatial.py`

Advanced geospatial operations for health analysis:

```python
from geo_infer_health.utils.advanced_geospatial import (
    haversine_distance, create_bounding_box, spatial_clustering
)

# Calculate distance between locations
distance = haversine_distance((37.7749, -122.4194), (37.7849, -122.4094))

# Create bounding box
bbox = create_bounding_box((37.7749, -122.4194), distance_km=10.0)

# Perform spatial clustering
clusters = spatial_clustering(
    locations=health_facility_locations,
    eps_km=2.0,
    min_samples=3
)
```

### Configuration Management

**Location**: `utils/config.py`

Configuration management for health module:

```python
from geo_infer_health.utils.config import load_config, get_config_value

# Load health configuration
config = load_config('config/health_config.yaml')

# Get configuration values
api_port = get_config_value(config, 'api.port', 8001)
database_url = get_config_value(config, 'database.url')
```

### Geospatial Utilities

**Location**: `utils/geospatial_utils.py`

Basic geospatial utilities:

```python
from geo_infer_health.utils.geospatial_utils import haversine_distance, create_bounding_box

# Calculate distance
distance = haversine_distance(loc1, loc2)

# Create bounding box
bbox = create_bounding_box(center, distance_km)
```

### Logging Utilities

**Location**: `utils/logging.py`

Structured logging for health applications:

```python
from geo_infer_health.utils.logging import setup_logging, get_logger

# Setup logging
setup_logging(level="INFO", json_format=True, log_file="health.log")

# Get logger
logger = get_logger("health_analysis")
logger.info("Starting health analysis", location="San Francisco")
```

## Integration Points

The HEALTH module integrates with other GEO-INFER modules:

- **GEO-INFER-SPACE**: Spatial analysis for disease mapping and accessibility
- **GEO-INFER-TIME**: Temporal analysis for disease trends and forecasting
- **GEO-INFER-DATA**: Data management for health datasets
- **GEO-INFER-BIO**: Bioinformatics integration for genetic epidemiology
- **GEO-INFER-AI**: Machine learning for predictive health modeling
- **GEO-INFER-API**: RESTful interfaces for health data access

## Development Guidelines

### Adding New Health Analysis Features

1. Define data models in `models/data_models.py`
2. Implement analysis logic in appropriate `core/` module
3. Add API endpoints in `api/` directory
4. Create comprehensive tests
5. Update documentation

### Code Style

- Follow PEP 8 conventions
- Use type hints for all function parameters and return values
- Include comprehensive docstrings
- Write unit tests for all new functionality
- Follow established patterns from existing modules

### Testing

Run the health test suite:
```bash
python -m pytest tests/
```

Run specific component tests:
```bash
python -m pytest tests/core/test_disease_surveillance.py
```

## Dependencies

Core dependencies managed through main GEO-INFER framework:

- `geopandas`: Geospatial data handling
- `shapely`: Geometric operations
- `pandas`: Data manipulation and analysis
- `numpy`: Numerical computations
- `scipy`: Scientific computing
- `matplotlib`: Visualization
- `fastapi`: API framework
- `pydantic`: Data validation

## Configuration

Configure health module in `config/health_config.yaml`:

```yaml
health:
  data_sources:
    disease_reports: "data/disease_reports.csv"
    health_facilities: "data/health_facilities.geojson"
    population_data: "data/population.geojson"
    environmental_data: "data/environmental.csv"

  analysis:
    default_radius_km: 5.0
    default_time_window_days: 7
    min_case_count: 3
    max_density_threshold: 50.0

  api:
    host: "0.0.0.0"
    port: 8003

  visualization:
    default_resolution: "1km"
    output_format: "png"
    color_scheme: "viridis"
```

## Performance Considerations

- Use spatial indexing for large datasets
- Implement efficient clustering algorithms
- Cache frequently accessed spatial data
- Optimize database queries for health data
- Monitor memory usage with large epidemiological datasets
