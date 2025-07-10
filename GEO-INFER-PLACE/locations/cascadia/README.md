# Cascadian Agricultural Land Analysis Framework

**Comprehensive Agricultural Data Analysis for Northern California + Oregon**

## Overview

This directory contains comprehensive research and implementation specifications for agricultural land analysis across the Cascadian bioregion, encompassing northern California counties and all of Oregon. The framework integrates eight specialized data acquisition modules into a unified H3-indexed backend for sophisticated agricultural land redevelopment analysis.

## Research Documents

### 📊 Data Research Foundation
- **`cascadian_agroecology_research_1.md`** (511 lines) - Empirical datasets for agricultural land redevelopment analysis covering Superior California counties and Oregon, with detailed data sources and access methods
- **`cascadian_agroecology_research_2.md`** (610 lines) - Technical specifications for geo-infer package integration with comprehensive API access methods and standardization frameworks

### 🏗️ Implementation Framework  
- **`cascadian_agricultural_data_modules_overview.md`** (1,054 lines) - **Comprehensive overview document** providing complete specifications for 8 data acquisition modules integrated into unified H3-based backend

## Target Geographic Coverage

### Northern California Counties (16)
- Butte, Colusa, Del Norte, Glenn, Humboldt, Lake, Lassen, Mendocino, Modoc, Nevada, Plumas, Shasta, Sierra, Siskiyou, Tehama, Trinity

### Oregon Counties (36) 
- All Oregon counties included for comprehensive bioregional analysis

## Eight Core Data Modules

| # | Module | Primary Purpose | Data Sources | Implementation Status |
|---|--------|----------------|--------------|---------------------|
| 1 | **Zoning** | Agricultural zoning classification | FMMP, ORMAP, Regrid | Ready for Implementation |
| 2 | **Current Use** | Real-time crop classification | NASS CDL, Land IQ, EFU | Ready for Implementation |
| 3 | **Ownership** | Ownership pattern analysis | ParcelQuest, County Records | Ready for Implementation |
| 4 | **Mortgage Debt** | Financial analysis | USDA ERS, Farm Credit | Limited Data Availability* |
| 5 | **Improvements** | Infrastructure analysis | Building Footprints, NASS | Ready for Implementation |
| 6 | **Surface Water** | Water rights analysis | eWRIMS/CalWATRS, Oregon WRD | Ready for Implementation |
| 7 | **Ground Water** | Groundwater analysis | DWR CASGEM, Oregon GWIC | Ready for Implementation |
| 8 | **Power Source** | Energy infrastructure | EIA, Utility Companies | Limited Data Availability* |

*\*Modules 4 and 8 identified as having data gaps requiring specialized acquisition strategies*

## Technical Architecture

### H3 Spatial Indexing
- **Resolution Level 8**: ~0.46 km² hexagons for optimal analysis granularity
- **Unified Backend**: `CascadianAgriculturalH3Backend` for all module integration
- **Cross-Border Analysis**: Seamless California-Oregon data harmonization

### Integration with GEO-INFER-PLACE
The framework extends existing PLACE module infrastructure:
- **PlaceAnalyzer**: Main orchestration engine
- **RealDataIntegrator**: Real-time data access
- **InteractiveVisualizationEngine**: Dashboard generation
- **API Clients**: California and Oregon data source integration

### Key Capabilities
- **Real-time Data Integration**: Continuous updates from government APIs
- **Cross-Domain Analysis**: Multi-module agricultural redevelopment scoring
- **Interactive Dashboards**: H3 hexagon-based visualization
- **Active Inference**: Uncertainty quantification and predictive modeling

## Implementation Timeline

### Phase 1: Foundation (Months 1-2)
- H3 infrastructure setup
- Zoning module (Module 1)
- Current Use module (Module 2)

### Phase 2: Core Modules (Months 3-4)
- Ownership module (Module 3)
- Surface Water module (Module 6)
- Ground Water module (Module 7)

### Phase 3: Advanced Modules (Months 5-6)
- Improvements module (Module 5)
- Mortgage Debt module (Module 4) with estimation models
- Power Source module (Module 8)

### Phase 4: Integration & Optimization (Months 7-8)
- Unified backend completion
- Cross-module analysis framework
- Comprehensive dashboard system

## Data Sources Summary

### California Primary Sources
- **California FMMP**: Farmland mapping with biennial updates
- **ParcelQuest**: Daily-updated parcel data for all 58 counties  
- **Land IQ**: High-accuracy crop mapping (98%+ accuracy)
- **eWRIMS/CalWATRS**: Water rights (transitioning July 2025)
- **DWR CASGEM**: Groundwater monitoring

### Oregon Primary Sources
- **ORMAP**: Statewide parcel system with continuous updates
- **Oregon EFU**: Exclusive Farm Use zoning (15.6M acres)
- **Oregon WRD**: Comprehensive water rights database
- **Oregon GWIC**: Groundwater Information Center

### Federal Integration
- **USDA NASS CDL**: 30-meter crop classification (2008-present)
- **USDA ERS**: Farm sector financial statistics
- **EIA**: Energy infrastructure and consumption data

## Research Findings

### Critical Data Gaps Identified
1. **Mortgage Debt Information**: Parcel-level debt data largely unavailable; requires estimation models
2. **Power Source Data**: Limited agricultural energy infrastructure data; requires utility partnerships

### Data Strengths
- Comprehensive parcel and zoning data coverage
- High-accuracy crop classification systems
- Robust water rights databases
- Detailed infrastructure datasets

### Cross-Border Harmonization Achievements
- Unified zoning classification systems
- Standardized water rights analysis
- Integrated ownership pattern analysis
- Common H3 spatial indexing framework

## Getting Started

### Prerequisites
- Existing GEO-INFER-PLACE infrastructure
- Python 3.8+ with geospatial packages
- API access credentials for real-time data sources

### Quick Start
1. Review comprehensive specifications in `cascadian_agricultural_data_modules_overview.md`
2. Begin with Phase 1 implementation (H3 infrastructure + Modules 1-2)
3. Establish API connections to primary data sources
4. Implement cross-module integration framework

### Documentation Structure
```
cascadia/
├── README.md                                          # This overview
├── cascadian_agroecology_research_1.md               # Empirical datasets research  
├── cascadian_agroecology_research_2.md               # Technical specifications
└── cascadian_agricultural_data_modules_overview.md   # Complete implementation guide
```

## Contributing

This framework provides the foundation for sophisticated agricultural land analysis across the Cascadian bioregion. Implementation should follow the GEO-INFER development principles with emphasis on:

- **No Mock Methods**: Complete, working implementations only
- **Active Inference Integration**: Uncertainty quantification and predictive modeling
- **Comprehensive Documentation**: Full API documentation and usage examples
- **Cross-Module Integration**: Unified analysis capabilities

## Contact & Support

For questions about implementation or research methodology, consult the comprehensive specifications in `cascadian_agricultural_data_modules_overview.md` or engage with the GEO-INFER development team through established channels.

---

*This framework represents a comprehensive approach to agricultural land analysis, integrating diverse data sources into a unified analytical platform capable of supporting sophisticated redevelopment strategy development across the Cascadian bioregion.* 

## California FMMP Data Integration

**Important:** The California Farmland Mapping & Monitoring Program (FMMP) GIS data is no longer available via a public REST API. You must manually download the shapefile for each county from the official FMMP website:

- https://www.conservation.ca.gov/dlrp/fmmp/Pages/county_info.aspx

Place each county's shapefile (e.g., `Butte.shp` and its associated files) in the following directory:

```
GEO-INFER-PLACE/locations/cascadia/data/fmmp/
```

The directory should contain files like:

```
data/fmmp/Butte.shp
data/fmmp/Butte.dbf
data/fmmp/Butte.shx
data/fmmp/Butte.prj
```

If a shapefile is missing, the pipeline will log an error and skip that county. Ensure you have the latest FMMP data for all counties you wish to analyze. 

## Current Agricultural Use Data Integration

The current use module requires manual download of data files due to size and access restrictions:

### NASS CDL (Cropland Data Layer)
- Download state-wide GeoTIFF for each year/state from: https://www.nass.usda.gov/Research_and_Science/Cropland/Release/index.php
- Place in: current_use/data/cdl/{year}_{state}.tif (e.g., 2024_CA.tif)

### Land IQ Crop Mapping (California)
- Obtain from: https://www.landiq.com/land-use-mapping or DWR partnerships
- Place shapefiles in: current_use/data/land_iq/{year}_{county}.shp

### Oregon EFU Reports
- Download from: https://www.oregon.gov/lcd/FF/Pages/Farm-Forest-Reports.aspx
- Convert to CSV if needed and place in: current_use/data/oregon_efu/efu_report_{year}.csv

If files are missing, the script will log instructions and skip that data source. 

## H3 Utility Functions (utils_h3.py)

A shared utility module `utils_h3.py` is provided in this directory to ensure robust, version-agnostic H3 spatial indexing across all Cascadian modules. This utility provides:

- `geo_to_h3(lat, lng, resolution)`: Converts latitude/longitude to H3 index, supporting both h3-py v3 and v4+ APIs.
- `h3_to_geo(h3_index)`: Converts H3 index to (lat, lng) tuple.
- `h3_to_geo_boundary(h3_index, geo_json=True)`: Gets the boundary of an H3 cell as a list of coordinates.
- `polyfill(geojson_polygon, resolution, geo_json=True)`: Polyfills a GeoJSON polygon to H3 indices.

**All modules must use these functions instead of direct h3-py calls** to ensure compatibility and maintainability. This refactor was implemented to address API changes between h3-py versions and to centralize error handling and logging for all H3 operations.

Example usage:
```python
from utils_h3 import geo_to_h3, h3_to_geo, h3_to_geo_boundary, polyfill

h3_index = geo_to_h3(40.0, -122.0, 8)
lat, lng = h3_to_geo(h3_index)
boundary = h3_to_geo_boundary(h3_index)
```

All modules in this directory have been updated to use this utility for all H3 conversions. 