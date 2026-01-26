# Agent: core

## Scope
This agent handles core health intelligence components for GEO-INFER-HEALTH implementing disease surveillance, hotspot analysis, environmental health assessment, and healthcare accessibility analysis.

## Implementation Status

### Currently Implemented

- ✅ **DiseaseHotspotAnalyzer**: Disease hotspot identification and analysis
- ✅ **ActiveInferenceDiseaseAnalyzer**: Disease surveillance using Active Inference principles
- ✅ **EnvironmentalHealthAnalyzer**: Environmental health data analysis
- ✅ **HealthcareAccessibilityAnalyzer**: Healthcare facility accessibility analysis

## Agent Capabilities

### 1. Disease Surveillance

```python
from geo_infer_health.core import DiseaseHotspotAnalyzer, ActiveInferenceDiseaseAnalyzer

# Basic hotspot analysis
analyzer = DiseaseHotspotAnalyzer(reports=disease_reports, population_data=population)
hotspots = analyzer.identify_simple_hotspots(
    threshold_case_count=5,
    scan_radius_km=10.0,
    min_density_cases_per_sq_km=0.5
)

# Calculate incidence rate
incidence_rate, total_cases, population = analyzer.calculate_local_incidence_rate(
    center_loc=location,
    radius_km=10.0,
    time_window_days=30
)

# Active Inference-based analysis
ai_analyzer = ActiveInferenceDiseaseAnalyzer(reports=disease_reports)
ai_results = ai_analyzer.analyze_with_active_inference(time_window_days=30)
```

### 2. Healthcare Accessibility

```python
from geo_infer_health.core import HealthcareAccessibilityAnalyzer

analyzer = HealthcareAccessibilityAnalyzer(facilities=health_facilities)

# Find nearest facility
nearest = analyzer.get_nearest_facility(
    loc=patient_location,
    facility_type='hospital',
    required_services=['emergency', 'surgery']
)

# Find facilities in radius
facilities = analyzer.find_facilities_in_radius(
    center_loc=location,
    radius_km=25.0,
    facility_type='clinic'
)
```

### 3. Environmental Health

```python
from geo_infer_health.core import EnvironmentalHealthAnalyzer

analyzer = EnvironmentalHealthAnalyzer(environmental_data=env_data)

# Get environmental readings
readings = analyzer.get_environmental_readings_near_location(
    center_loc=location,
    radius_km=5.0,
    parameter_name='pm2.5',
    start_time=start_date,
    end_time=end_date
)

# Calculate average exposure
exposure = analyzer.calculate_average_exposure(
    target_locations=locations,
    radius_km=5.0,
    parameter_name='pm2.5',
    time_window_days=30
)
```

## Key Classes

### DiseaseHotspotAnalyzer
Analyzes disease reports to identify hotspots and calculate incidence rates.

**Key Methods**:
- `get_cases_in_radius(center_loc, radius_km) -> List[DiseaseReport]`
- `calculate_local_incidence_rate(center_loc, radius_km, time_window_days) -> Tuple[float, int, int]`
- `identify_simple_hotspots(threshold_case_count, scan_radius_km, min_density) -> List[Dict]`
- `simulate_sir_model(initial_infected, population, beta, gamma, days) -> Dict[str, List[float]]`

### ActiveInferenceDiseaseAnalyzer
Disease surveillance using Active Inference principles for probabilistic reasoning.

**Key Methods**:
- `analyze_with_active_inference(time_window_days) -> Dict[str, Any]`
- `calculate_reproduction_number(serial_interval_days, window_days) -> Dict[str, Any]`
- `generate_risk_map_data(grid_resolution_km, bbox) -> Dict[str, Any]`

### HealthcareAccessibilityAnalyzer
Analyzes accessibility to healthcare facilities.

**Key Methods**:
- `find_facilities_in_radius(center_loc, radius_km, facility_type, required_services) -> List[HealthFacility]`
- `get_nearest_facility(loc, facility_type, required_services) -> Optional[Tuple[HealthFacility, float]]`
- `calculate_facility_to_population_ratio(area_id, facility_type) -> Optional[Dict[str, Any]]`

### EnvironmentalHealthAnalyzer
Analyzes environmental data in relation to health.

**Key Methods**:
- `get_environmental_readings_near_location(center_loc, radius_km, parameter_name, start_time, end_time) -> List[EnvironmentalData]`
- `calculate_average_exposure(target_locations, radius_km, parameter_name, time_window_days) -> Dict[str, Optional[float]]`

## Integration

- **Location**: `GEO-INFER-HEALTH/src/geo_infer_health/core`
- **Dependencies**: `geo_infer_health.models`, `geo_infer_health.utils`, `geo_infer_act` for Active Inference
- **Used By**: API layer, application modules
- **Provides**: Core health intelligence capabilities for disease surveillance, healthcare accessibility, and environmental health

---

This AGENTS.md documents core health intelligence components for GEO-INFER-HEALTH.
