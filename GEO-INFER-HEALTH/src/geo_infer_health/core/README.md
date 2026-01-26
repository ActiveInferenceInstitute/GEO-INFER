# core

## Overview

Core health intelligence components for GEO-INFER-HEALTH implementing disease surveillance, hotspot analysis, environmental health assessment, and healthcare accessibility analysis.

This directory contains core components for health intelligence including disease surveillance, healthcare accessibility, and environmental health analysis.

## Components

### disease_surveillance.py
Disease hotspot identification and analysis.

**Classes**: `DiseaseHotspotAnalyzer`

### enhanced_disease_surveillance.py
Disease surveillance with Active Inference principles.

**Classes**: `ActiveInferenceDiseaseAnalyzer`

### environmental_health.py
Environmental health data analysis.

**Classes**: `EnvironmentalHealthAnalyzer`

### healthcare_accessibility.py
Healthcare facility accessibility analysis.

**Classes**: `HealthcareAccessibilityAnalyzer`

## Usage

```python
from geo_infer_health.core import (
    DiseaseHotspotAnalyzer,
    ActiveInferenceDiseaseAnalyzer,
    HealthcareAccessibilityAnalyzer,
    EnvironmentalHealthAnalyzer
)

# Disease surveillance
analyzer = DiseaseHotspotAnalyzer(reports=disease_reports)
hotspots = analyzer.identify_simple_hotspots(threshold_case_count=5, scan_radius_km=10.0)

# Healthcare accessibility
accessibility = HealthcareAccessibilityAnalyzer(facilities=health_facilities)
nearest = accessibility.get_nearest_facility(location, facility_type='hospital')
```

## Integration

- **Location**: `GEO-INFER-HEALTH/src/geo_infer_health/core`
- **Dependencies**: `geo_infer_health.models`, `geo_infer_health.utils`, `geo_infer_act`
- **Used By**: API layer, application modules
- **Provides**: Core health intelligence capabilities

--- 