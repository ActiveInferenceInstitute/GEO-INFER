# Cascadian Agricultural Data Modules: Implementation Specification

**Northern California + Oregon Agricultural Land Analysis Framework**
*Integrated H3-OSC Backend for Joint Analysis and Visualization*

## 1. Executive Summary

This document provides a comprehensive **implementation specification** for **eight specialized data acquisition and analysis modules** designed for agricultural land analysis across the Cascadian bioregion. It serves as the primary technical guide for developing and integrating these modules within the `cascadia_main.py` orchestration script.

The framework is architected around the **`GEO-INFER-SPACE` H3-OSC (OS-Climate) framework**, ensuring all geospatial data is standardized into H3 hexagonal grids for unified analysis. Each module is responsible for acquiring raw data, caching it locally to prevent redundant downloads, processing it into an H3-indexed format, and exposing it to the unified backend.

### Core Architecture & Configuration

The `cascadia_main.py` script orchestrates the entire analysis pipeline. Its behavior is controlled by two primary mechanisms:
1.  **Configuration File**: The `config/data_urls.json` file specifies the default `active_modules` and `target_counties` for an analysis run. This allows for flexible configuration without code changes.
2.  **Command-Line Arguments**: Users can override the default configuration by providing command-line arguments (e.g., `--modules`, `--counties`), enabling dynamic and targeted analysis.

### Module Implementation Status

The following table outlines the target state for each module. The immediate development priority is to implement the "Data Acquisition and Caching" and "H3-OSC Integration" steps for each module to make the framework fully operational.

| Module | Primary Data Sources | Update Frequency | Target Status |
|--------|---------------------|------------------|---------------|
| **Zoning** | FMMP, ORMAP, Regrid | Biennial/Continuous | **Operational** |
| **Current Use** | NASS CDL, Land IQ, EFU | Annual | **Operational** |
| **Ownership** | ParcelQuest, County Records | Daily/Weekly | **Operational** |
| **Mortgage Debt**| USDA ERS, Farm Credit, County Records | Quarterly/Variable | **Operational** |
| **Improvements** | NASS Infrastructure, Building Footprints | 5-Year/Annual | **Operational** |
| **Surface Water**| eWRIMS/CalWATRS, Oregon WRD | Real-time/Quarterly | **Operational** |
| **Ground Water** | DWR CASGEM, Oregon GWIC | Real-time/Monthly | **Operational** |
| **Power Source** | EIA, Utility Companies | Annual/Variable | **Operational** |

## 2. Standardized Module Workflow

Each of the eight data modules must adhere to the following three-step workflow to ensure consistency and proper integration with the unified backend.

### Step 1: Data Acquisition and Caching
- **Acquire Data**: Fetch data from the specified API endpoints or download URLs listed in `config/data_urls.json`.
- **Implement Caching**: Before downloading, check for the existence of the data in a local cache directory: `GEO-INFER-PLACE/locations/cascadia/data/<module_name>/`. If the data is present and up-to-date, skip the download. This prevents redundant network requests and speeds up repeated analyses.
- **Store Raw Data**: Save the raw, unprocessed data in its original format (e.g., Shapefile, GeoJSON, CSV) in the cache directory.

### Step 2: H3-OSC Integration and Processing
- **Process Raw Data**: Load the raw data into a suitable format (e.g., GeoDataFrame).
- **Leverage OSC Loaders**: Use the `GEO-INFER-SPACE` wrapper for the **`osc-geo-h3loader-cli`** tool to convert the processed geospatial data into an H3-indexed format. This is the primary mechanism for standardizing all module data.
- **Generate H3 Data**: The output should be a file of H3 indexes with associated attributes, stored in the module's cache directory.

### Step 3: Analysis and Exposure
- **Load H3 Data**: The module's analysis functions will load the pre-processed H3 data from the cache.
- **Perform Analysis**: Execute the specific analysis for the module (e.g., calculate zoning statistics, ownership concentration).
- **Expose to Backend**: Return the final, H3-indexed dictionary of results to the `CascadianAgriculturalH3Backend` for aggregation.

---

## Module 1: Agricultural Zoning Module (`GeoInferZoning`)

### **Purpose**
Comprehensive agricultural zoning classification and regulatory analysis across northern California and Oregon, providing the foundational land use framework for all subsequent agricultural analysis.

### **Technical Specifications**
- **Data Sources**:
    - CA FMMP: Manual download required as per `README.md`. The acquisition script must check the cache for the file before prompting the user. The data URL in `config/data_urls.json` should point to the official data page, not a direct download link.
    - OR DLCD: The ArcGIS service URL and query parameters in `config/data_urls.json` must be validated and corrected.
    - WA King County: The service endpoint must be updated to a current, valid URL.
- **H3 Integration**: Use the `osc-geo-h3loader-cli` to convert final zoning polygons (GeoDataFrame) to H3-indexed data at the target resolution.

#### Data Sources Integration
```python
class CascadianZoningDataSources:
    """Unified zoning data access for Cascadian bioregion"""
    
    def __init__(self):
        self.california_sources = {
            'fmmp': {
                'url': 'https://www.conservation.ca.gov/dlrp/fmmp',
                'api_endpoint': 'https://gis.conservation.ca.gov/server/rest/services',
                'format': 'REST API, Geodatabase, Shapefile',
                'coverage': ['Butte', 'Colusa', 'Del Norte', 'Glenn', 'Humboldt', 
                           'Lake', 'Lassen', 'Mendocino', 'Modoc', 'Nevada', 
                           'Plumas', 'Shasta', 'Sierra', 'Siskiyou', 'Tehama', 'Trinity'],
                'update_frequency': 'Biennial',
                'classification': ['Prime', 'Statewide Importance', 'Unique', 'Local Importance']
            },
            'regrid': {
                'url': 'https://regrid.com/california-parcel-data',
                'api_access': True,
                'coverage': 'All 58 California counties',
                'update_frequency': 'Daily from county assessors'
            }
        }
        
        self.oregon_sources = {
            'efu_zoning': {
                'url': 'https://www.oregon.gov/lcd/LAR/Pages/AgLand.aspx',
                'coverage': '15.6 million acres under resource zoning',
                'retention_rate': '99% since 1987',
                'format': 'Vector digital data, ArcGIS services'
            },
            'ormap': {
                'url': 'https://www.ormap.net',
                'api_access': True,
                'coverage': 'All 36 Oregon counties',
                'update_frequency': 'Continuous'
            }
        }
```

#### H3 Integration Framework
```python
def integrate_h3_indexing(self, zoning_polygons: gpd.GeoDataFrame, resolution: int = 8) -> Dict:
    """
    Convert zoning polygons to H3 indexed system for unified analysis
    
    Args:
        zoning_polygons: Agricultural zoning polygons
        resolution: H3 resolution level (8 = ~0.46 km² hexagons)
        
    Returns:
        H3 indexed zoning data with aggregated attributes
    """
    h3_indexed_zones = {}
    
    for idx, zone in zoning_polygons.iterrows():
        # Convert polygon to H3 hexagons
        hexagons = h3.polyfill(
            zone.geometry.__geo_interface__, 
            resolution, 
            geo_json_conformant=True
        )
        
        for hex_id in hexagons:
            if hex_id not in h3_indexed_zones:
                h3_indexed_zones[hex_id] = {
                    'zoning_classes': [],
                    'regulatory_status': [],
                    'protection_level': 0,
                    'development_pressure': 0
                }
            
            h3_indexed_zones[hex_id]['zoning_classes'].append(zone['classification'])
            h3_indexed_zones[hex_id]['regulatory_status'].append(zone['status'])
            
    return h3_indexed_zones
```

### **API Integration Patterns**
- **Real-time FMMP Access**: REST API integration with automatic updates
- **County Assessor Integration**: Bulk data synchronization for all target counties
- **Cross-State Harmonization**: Standardized classification schema development

## Module 2: Current Agricultural Use Module (`GeoInferCurrentUse`)

### **Purpose**
Real-time agricultural land use classification and crop production analysis, providing detailed current utilization patterns for agricultural redevelopment planning.

### **Technical Specifications**
- **Data Sources**:
    - NASS CDL: Update the `nassgeodata.gmu.edu` API endpoint in `config/data_urls.json`. The data acquisition logic should handle potential SSL certificate issues and implement robust error handling for API queries.
- **H3 Integration**: Process the downloaded raster data for a given region, polygonize the results for different crop types, and use the `osc-geo-h3loader-cli` to generate H3-indexed crop data.

#### Multi-Source Data Integration
```python
class CascadianCurrentUseAnalyzer:
    """Current agricultural use analysis with multi-temporal capabilities"""
    
    def __init__(self):
        self.data_sources = {
            'nass_cdl': {
                'url': 'https://www.nass.usda.gov/Research_and_Science/Cropland/',
                'spatial_resolution': '30 meters',
                'temporal_coverage': '2008-present',
                'classification_categories': '50+ crop-specific categories',
                'api_access': 'USDA APIs with rate limiting'
            },
            'land_iq': {
                'partnership': 'California Department of Water Resources',
                'spatial_resolution': '0.5-2.0 acre minimum mapping units',
                'coverage': '15.4 million acres',
                'accuracy': '98%+',
                'update_frequency': 'Annual (water year basis)'
            },
            'oregon_farm_reports': {
                'source': 'Oregon Department of Land Conservation and Development',
                'coverage': 'EFU and forest zone land use decisions',
                'frequency': 'Biennial',
                'data_elements': 'Agricultural land conversion tracking'
            }
        }
    
    def process_current_use_h3(self, year: int, resolution: int = 8) -> Dict:
        """
        Generate H3-indexed current agricultural use classification
        
        Args:
            year: Analysis year
            resolution: H3 resolution level
            
        Returns:
            H3-indexed agricultural use data
        """
        # Integrate NASS CDL data
        cdl_data = self.fetch_nass_cdl(year)
        
        # Integrate Land IQ California data
        land_iq_data = self.fetch_land_iq_data(year)
        
        # Convert to H3 indexing
        h3_current_use = {}
        
        for hex_id in self.target_hexagons:
            hex_geometry = h3.h3_to_geo_boundary(hex_id, geo_json=True)
            
            # Extract crop types within hexagon
            crop_types = self.extract_crops_in_hex(hex_geometry, cdl_data, land_iq_data)
            
            h3_current_use[hex_id] = {
                'primary_crop': self.determine_primary_crop(crop_types),
                'crop_diversity': len(set(crop_types)),
                'agricultural_intensity': self.calculate_intensity(crop_types),
                'water_requirements': self.estimate_water_needs(crop_types),
                'economic_value': self.estimate_economic_value(crop_types)
            }
            
        return h3_current_use
```

### **Temporal Analysis Framework**
- **Change Detection**: Multi-year crop rotation and land use transition analysis
- **Trend Identification**: Long-term agricultural intensification patterns
- **Seasonal Patterns**: Crop calendar and seasonal use variations

## Module 3: Agricultural Ownership Module (`GeoInferOwnership`)

### **Purpose**
Comprehensive agricultural land ownership analysis including ownership patterns, concentration metrics, and institutional vs. individual ownership classification.

### **Technical Specifications**
- **Data Sources**:
    - CA Parcels: The ArcGIS service query to `services.gis.ca.gov` for parcel data returns no features. The endpoint is likely outdated or requires different query parameters.
- **H3 Integration**: Convert parcel-level ownership data into a unified H3-indexed dataset summarizing ownership statistics per hexagon.

#### Ownership Data Integration
```python
class CascadianOwnershipAnalyzer:
    """Agricultural land ownership analysis with concentration metrics"""
    
    def __init__(self):
        self.ownership_sources = {
            'california': {
                'parcelquest': {
                    'coverage': 'All 58 California counties',
                    'update_frequency': 'Daily',
                    'data_elements': ['APN', 'owner_name', 'ownership_type', 
                                    'assessed_value', 'acreage', 'ownership_history'],
                    'api_access': True
                },
                'regrid': {
                    'coverage': 'All target counties',
                    'data_elements': ['ownership_details', 'property_characteristics'],
                    'bulk_access': True
                }
            },
            'oregon': {
                'ormap': {
                    'coverage': 'All 36 Oregon counties',
                    'data_elements': ['taxlot_ownership', 'assessor_data'],
                    'format': 'GIS-compatible formats',
                    'update_frequency': 'Continuous'
                }
            }
        }
    
    def analyze_ownership_concentration_h3(self, resolution: int = 8) -> Dict:
        """
        Calculate ownership concentration metrics at H3 level
        
        Returns:
            H3-indexed ownership concentration data
        """
        ownership_data = self.fetch_unified_ownership_data()
        h3_ownership = {}
        
        for hex_id in self.target_hexagons:
            hex_parcels = self.get_parcels_in_hex(hex_id, ownership_data)
            
            # Calculate concentration metrics
            ownership_concentration = self.calculate_herfindahl_index(hex_parcels)
            largest_owner_share = self.calculate_largest_owner_share(hex_parcels)
            institutional_share = self.calculate_institutional_share(hex_parcels)
            
            h3_ownership[hex_id] = {
                'ownership_concentration': ownership_concentration,
                'largest_owner_share': largest_owner_share,
                'institutional_ownership_share': institutional_share,
                'number_of_owners': len(set([p['owner'] for p in hex_parcels])),
                'average_parcel_size': np.mean([p['acreage'] for p in hex_parcels]),
                'ownership_diversity': self.calculate_ownership_diversity(hex_parcels)
            }
            
        return h3_ownership
```

### **Research Integration**
Based on UC research findings showing that the largest 5% of properties control 50.6% of California cropland, this module implements sophisticated concentration analysis to identify ownership patterns and potential consolidation trends.

## Module 4: Mortgage Debt Module (`GeoInferMortgageDebt`) 

### **Purpose**
Agricultural mortgage debt and financial indicator analysis, addressing the critical data gap identified in the research through multiple acquisition strategies.

### **Technical Specifications**
- **Data Sources**:
    - HMDA Data: The S3 bucket URL structure for bulk CSV data has changed. Update the `hmda_bulk_url` in `config/data_urls.json` to reflect the current path format.
- **Analysis**: Since direct debt data is sparse, this module will focus on robust proxy modeling using the available data sources.

#### Multi-Source Debt Data Integration
```python
class CascadianMortgageDebtAnalyzer:
    """Agricultural mortgage debt analysis with estimation models"""
    
    def __init__(self):
        self.debt_sources = {
            'usda_ers': {
                'national_debt': '$503.7 billion total (2021)',
                'real_estate_debt': '$344.5 billion (68% of total)',
                'projected_2025': '$374.2 billion real estate debt',
                'api_access': 'USDA ERS QuickStats API',
                'granularity': 'State and regional levels'
            },
            'federal_reserve': {
                'institutional_data': 'Farm Credit System, commercial banks',
                'geographic_aggregation': 'State and regional',
                'update_frequency': 'Quarterly'
            },
            'county_level_estimation': {
                'methodology': 'Regression modeling using available indicators',
                'predictors': ['assessed_values', 'crop_productivity', 'farm_size_distribution'],
                'validation': 'USDA ARMS survey data'
            }
        }
    
    def estimate_debt_levels_h3(self, resolution: int = 8) -> Dict:
        """
        Estimate agricultural debt levels using available indicators
        
        Returns:
            H3-indexed debt estimation data
        """
        # Gather predictor variables
        assessed_values = self.get_assessed_values_h3(resolution)
        farm_characteristics = self.get_farm_characteristics_h3(resolution)
        regional_debt_data = self.get_regional_debt_statistics()
        
        h3_debt_estimates = {}
        
        for hex_id in self.target_hexagons:
            # Apply debt estimation model
            estimated_debt_ratio = self.estimate_debt_to_asset_ratio(
                assessed_value=assessed_values[hex_id],
                farm_size=farm_characteristics[hex_id]['avg_farm_size'],
                crop_type=farm_characteristics[hex_id]['primary_crop'],
                regional_baseline=regional_debt_data[self.get_region(hex_id)]
            )
            
            h3_debt_estimates[hex_id] = {
                'estimated_debt_to_asset_ratio': estimated_debt_ratio,
                'financial_risk_level': self.classify_risk_level(estimated_debt_ratio),
                'lending_institution_likelihood': self.estimate_lending_sources(hex_id),
                'debt_estimation_confidence': self.calculate_confidence_interval(hex_id)
            }
            
        return h3_debt_estimates
```

### **Data Gap Mitigation Strategies**
1. **County Recorder Integration**: API development for mortgage recording systems
2. **Farm Credit System Partnerships**: Regional agricultural lender data sharing
3. **Statistical Modeling**: Predictive debt modeling using available economic indicators
4. **Survey Integration**: USDA ARMS and Agricultural Census correlation analysis

## Module 5: Agricultural Improvements Module (`GeoInferImprovements`)

### **Purpose**
Comprehensive agricultural infrastructure and improvement analysis including buildings, irrigation systems, processing facilities, and specialized agricultural infrastructure.

### **Technical Specifications**
- **Code Fix**: Resolve the `AttributeError: module 'fiona' has no attribute 'path'`. This is a known issue with older versions of `geopandas` or incorrect `fiona` usage. The code should be updated to use `geopandas.read_file()` which correctly handles file paths with `fiona` under the hood.
- **H3 Integration**: Identify agricultural buildings and infrastructure, then generate H3-indexed data summarizing improvement density and value.

#### Infrastructure Data Integration
```python
class CascadianImprovementsAnalyzer:
    """Agricultural infrastructure and improvements analysis"""
    
    def __init__(self):
        self.infrastructure_sources = {
            'building_footprints': {
                'microsoft_buildings': {
                    'coverage': '2.5 billion building footprints globally',
                    'format': 'Cloud-native (GeoParquet, FlatGeobuf, PMTiles)',
                    'attributes': ['building_area', 'confidence_score'],
                    'regional_coverage': '92% of administrative boundaries'
                },
                'google_open_buildings': {
                    'coverage': 'Complementary dataset',
                    'classification': 'Building type inference'
                }
            },
            'irrigation_infrastructure': {
                'usda_irrigation_survey': {
                    'frequency': '5-year comprehensive assessment',
                    'data_elements': ['irrigation_systems', 'water_management'],
                    'access': 'USDA NASS Quick Stats database'
                },
                'ca_dwr_land_water_use': {
                    'coverage': 'Agricultural Water Management Planning areas',
                    'infrastructure_elements': ['irrigation_systems', 'ET_equipment'],
                    'update_frequency': 'Annual estimates'
                }
            },
            'specialized_facilities': {
                'processing_facilities': 'USDA facility databases',
                'storage_infrastructure': 'Agricultural storage facility mapping',
                'livestock_facilities': 'Dairy and livestock infrastructure'
            }
        }
    
    def analyze_agricultural_improvements_h3(self, resolution: int = 8) -> Dict:
        """
        Comprehensive agricultural improvements analysis at H3 level
        
        Returns:
            H3-indexed agricultural improvements data
        """
        building_data = self.fetch_building_footprints()
        irrigation_data = self.fetch_irrigation_infrastructure()
        facility_data = self.fetch_specialized_facilities()
        
        h3_improvements = {}
        
        for hex_id in self.target_hexagons:
            hex_buildings = self.filter_agricultural_buildings(
                self.get_buildings_in_hex(hex_id, building_data)
            )
            
            hex_irrigation = self.get_irrigation_in_hex(hex_id, irrigation_data)
            hex_facilities = self.get_facilities_in_hex(hex_id, facility_data)
            
            # Calculate improvement metrics
            total_building_area = sum([b['area'] for b in hex_buildings])
            irrigation_coverage = self.calculate_irrigation_coverage(hex_irrigation)
            facility_value = self.estimate_facility_value(hex_facilities)
            
            h3_improvements[hex_id] = {
                'total_building_area': total_building_area,
                'building_density': total_building_area / self.get_hex_area(hex_id),
                'irrigation_coverage_ratio': irrigation_coverage,
                'processing_facility_presence': len(hex_facilities) > 0,
                'estimated_improvement_value': self.estimate_total_improvement_value(
                    hex_buildings, hex_irrigation, hex_facilities
                ),
                'infrastructure_age_estimate': self.estimate_infrastructure_age(hex_buildings),
                'modernization_score': self.calculate_modernization_score(
                    hex_buildings, hex_irrigation, hex_facilities
                )
            }
            
        return h3_improvements
```

### **Valuation Methodology**
- **Class A Buildings**: Depreciated replacement cost method for structures
- **Class B Improvements**: Land-integrated improvements (fences, irrigation, roads)
- **Class S Specialized**: Processing facilities and storage infrastructure
- **Permanent Crops**: Orchards and vineyards with age/condition factors

## Module 6: Surface Water Rights Module (`GeoInferSurfaceWater`)

### **Purpose**
Comprehensive surface water rights analysis integrating California's eWRIMS/CalWATRS transition and Oregon's water rights database for unified cross-border water allocation analysis.

### **Technical Specifications**
- **Data Sources**:
    - NHD Services: The `hydro.nationalmap.gov` service endpoints for flowlines and waterbodies need to be updated in `config/data_urls.json` to ensure they return data for the analysis region.
- **H3 Integration**: Associate water rights data (points of diversion, allocation amounts) with the H3 grid to analyze water availability per hexagon.

#### Water Rights Data Integration
```python
class CascadianSurfaceWaterAnalyzer:
    """Surface water rights analysis with cross-border integration"""
    
    def __init__(self):
        self.water_sources = {
            'california': {
                'ewrims_legacy': {
                    'status': 'Active through June 2025',
                    'data_elements': ['permits', 'licenses', 'certificates', 
                                    'diversion_points', 'authorized_quantities'],
                    'irrigation_reports': 'Annual use reporting',
                    'access': 'Downloadable CSV and spatial formats'
                },
                'calwatrs_new': {
                    'launch_date': 'July 2025',
                    'enhanced_features': ['streamlined_reporting', 'gis_integration'],
                    'spatial_improvements': 'Enhanced spatial information access'
                }
            },
            'oregon': {
                'oregon_wrd': {
                    'database': 'Oregon Water Rights Database',
                    'spatial_component': 'Points of diversion locations',
                    'data_elements': ['permit_numbers', 'priority_dates', 
                                    'flow_rates', 'use_classifications'],
                    'access': 'Public GIS services through geohub.oregon.gov'
                },
                'hardwr': {
                    'source': 'Harmonized Database of Western U.S. Water Rights',
                    'coverage': 'Comprehensive Oregon water rights allocation',
                    'academic_access': 'Published research datasets'
                }
            }
        }
    
    def analyze_surface_water_rights_h3(self, resolution: int = 8) -> Dict:
        """
        Cross-border surface water rights analysis at H3 level
        
        Returns:
            H3-indexed surface water rights data
        """
        ca_water_rights = self.fetch_california_water_rights()
        or_water_rights = self.fetch_oregon_water_rights()
        
        # Harmonize water rights data across states
        harmonized_rights = self.harmonize_water_rights_data(
            ca_water_rights, or_water_rights
        )
        
        h3_water_rights = {}
        
        for hex_id in self.target_hexagons:
            hex_rights = self.get_water_rights_in_hex(hex_id, harmonized_rights)
            
            # Calculate water rights metrics
            total_allocation = sum([r['allocated_flow'] for r in hex_rights])
            senior_rights_ratio = self.calculate_senior_rights_ratio(hex_rights)
            irrigation_allocation = self.calculate_irrigation_allocation(hex_rights)
            
            h3_water_rights[hex_id] = {
                'total_water_allocation': total_allocation,
                'number_of_rights': len(hex_rights),
                'senior_rights_ratio': senior_rights_ratio,
                'irrigation_allocation_share': irrigation_allocation,
                'priority_date_range': self.calculate_priority_date_range(hex_rights),
                'seasonal_availability': self.analyze_seasonal_patterns(hex_rights),
                'water_security_score': self.calculate_water_security_score(hex_rights)
            }
            
        return h3_water_rights
```

### **Cross-Border Harmonization**
- **Unified Priority Systems**: Priority date standardization across state systems
- **Allocation Metrics**: Standardized flow allocation and use classification
- **Temporal Analysis**: Seasonal availability and historical allocation patterns

## Module 7: Ground Water Rights Module (`GeoInferGroundWater`)

### **Purpose**
Comprehensive groundwater rights and availability analysis integrating California's CASGEM system with Oregon's groundwater management framework.

### **Technical Specifications**
- **Data Sources**:
    - USGS NWIS: The API request format for `waterservices.usgs.gov` has likely changed. The acquisition script must be updated to use the current valid request parameters for fetching groundwater level data.
- **H3 Integration**: Spatially join well locations and monitoring data to the H3 grid to model groundwater availability and trends.

#### Groundwater Data Integration
```python
class CascadianGroundWaterAnalyzer:
    """Groundwater rights and availability analysis"""
    
    def __init__(self):
        self.groundwater_sources = {
            'california': {
                'casgem': {
                    'system': 'California Statewide Groundwater Elevation Monitoring',
                    'monitoring_wells': 'Real-time groundwater level data',
                    'basin_boundaries': 'DWR Bulletin 118 groundwater basins',
                    'sustainability_plans': 'SGMA implementation tracking'
                },
                'dwr_well_completion': {
                    'database': 'Well completion report database',
                    'well_locations': 'GPS coordinates for wells',
                    'well_characteristics': 'Depth, yield, construction details'
                }
            },
            'oregon': {
                'gwic': {
                    'system': 'Groundwater Information Center',
                    'well_database': 'Comprehensive well location and data',
                    'monitoring_network': 'Oregon groundwater monitoring',
                    'rights_integration': 'Groundwater rights allocation'
                }
            }
        }
    
    def analyze_groundwater_h3(self, resolution: int = 8) -> Dict:
        """
        Comprehensive groundwater analysis at H3 level
        
        Returns:
            H3-indexed groundwater data
        """
        ca_groundwater = self.fetch_california_groundwater_data()
        or_groundwater = self.fetch_oregon_groundwater_data()
        
        h3_groundwater = {}
        
        for hex_id in self.target_hexagons:
            hex_wells = self.get_wells_in_hex(hex_id, ca_groundwater, or_groundwater)
            monitoring_data = self.get_monitoring_data_for_hex(hex_id)
            
            # Calculate groundwater metrics
            well_density = len(hex_wells) / self.get_hex_area(hex_id)
            avg_depth = np.mean([w['depth'] for w in hex_wells])
            total_yield = sum([w['yield'] for w in hex_wells])
            
            h3_groundwater[hex_id] = {
                'well_density': well_density,
                'average_well_depth': avg_depth,
                'total_yield_capacity': total_yield,
                'groundwater_level_trend': self.analyze_level_trends(monitoring_data),
                'aquifer_type': self.determine_aquifer_type(hex_id),
                'sustainability_status': self.assess_sustainability_status(hex_id),
                'groundwater_availability_score': self.calculate_availability_score(
                    hex_wells, monitoring_data
                )
            }
            
        return h3_groundwater
```

### **Sustainability Integration**
- **SGMA Compliance**: California Sustainable Groundwater Management Act integration
- **Basin Boundaries**: DWR Bulletin 118 groundwater basin mapping
- **Monitoring Networks**: Real-time groundwater level tracking and trend analysis

## Module 8: Power Source Module (`GeoInferPowerSource`)

### **Purpose**
Agricultural power source and energy infrastructure analysis, addressing one of the identified data gaps through utility integration and energy consumption modeling.

### **Technical Specifications**
- **Data Sources**:
    - HIFLD Service: The ArcGIS service endpoint for transmission lines is outdated. Update the URL in `config/data_urls.json` to a valid source.
- **H3 Integration**: Map utility service territories and power infrastructure to the H3 grid to analyze energy availability and cost.

#### Power Source Data Integration
```python
class CascadianPowerSourceAnalyzer:
    """Agricultural power source and energy infrastructure analysis"""
    
    def __init__(self):
        self.power_sources = {
            'utility_data': {
                'eia_861': {
                    'source': 'Energy Information Administration Form 861',
                    'data_elements': ['utility_service_territories', 'sales_by_sector'],
                    'agricultural_classification': 'Limited agricultural sector data',
                    'update_frequency': 'Annual'
                },
                'utility_companies': {
                    'pge': 'Pacific Gas & Electric agricultural rates',
                    'edison': 'Southern California Edison agricultural programs',
                    'portland_general': 'Oregon utility agricultural services'
                }
            },
            'renewable_energy': {
                'nrel_data': {
                    'solar_resources': 'National Solar Radiation Database',
                    'wind_resources': 'Wind resource assessment',
                    'biogas_potential': 'Agricultural biogas resource assessment'
                },
                'ca_dgs_nem': {
                    'source': 'California Distributed Generation Statistics',
                    'data_elements': 'Net energy metering installations',
                    'agricultural_solar': 'On-farm solar installation tracking'
                }
            }
        }
    
    def analyze_power_sources_h3(self, resolution: int = 8) -> Dict:
        """
        Agricultural power source analysis at H3 level
        
        Returns:
            H3-indexed power source data
        """
        utility_territories = self.fetch_utility_service_territories()
        renewable_installations = self.fetch_renewable_energy_data()
        energy_consumption_models = self.load_crop_energy_models()
        
        h3_power_sources = {}
        
        for hex_id in self.target_hexagons:
            primary_utility = self.determine_primary_utility(hex_id, utility_territories)
            renewable_capacity = self.calculate_renewable_capacity(
                hex_id, renewable_installations
            )
            
            # Estimate energy consumption based on agricultural use
            current_use = self.get_current_agricultural_use(hex_id)
            estimated_consumption = self.estimate_energy_consumption(
                current_use, energy_consumption_models
            )
            
            h3_power_sources[hex_id] = {
                'primary_utility_provider': primary_utility,
                'estimated_energy_consumption': estimated_consumption,
                'renewable_energy_capacity': renewable_capacity,
                'grid_reliability_score': self.calculate_grid_reliability(hex_id),
                'agricultural_rate_availability': self.check_agricultural_rates(
                    primary_utility
                ),
                'energy_independence_potential': self.assess_energy_independence(
                    estimated_consumption, renewable_capacity
                ),
                'power_infrastructure_adequacy': self.assess_infrastructure_adequacy(
                    hex_id, estimated_consumption
                )
            }
            
        return h3_power_sources
```

### **Energy Modeling Framework**
- **Crop-Specific Models**: Energy consumption by agricultural operation type
- **Irrigation Energy**: Pumping and distribution system energy requirements
- **Processing Energy**: On-farm processing and storage energy needs
- **Seasonal Variations**: Temporal energy demand patterns

## 9. Unified H3-OSC Backend Architecture

The entire framework is underpinned by a unified backend that leverages the **`GEO-INFER-SPACE` H3-OSC module**. This backend is responsible for orchestrating the individual data modules and aggregating their outputs into a single, cohesive H3-indexed dataset.

### H3-OSC Spatial Indexing Framework

The `CascadianAgriculturalH3Backend` class manages the analysis. It initializes the requested modules, defines the target H3 hexagons for the bioregion, and runs the main analysis pipeline. The integration with the OS-Climate tools is central to its design.

```python
class CascadianAgriculturalH3Backend:
    """Unified H3-indexed backend for all 8 agricultural data modules"""
    
    def __init__(self, resolution: int = 8, bioregion: str = 'Cascadia', active_modules: list = None, target_counties: dict = None):
        self.resolution = resolution
        self.bioregion = bioregion
        # The backend now uses the GEO-INFER-SPACE wrappers for OSC tools
        self.h3_loader = geo_infer_space.osc_geo.create_h3_data_loader()
        self.modules = self._initialize_modules(active_modules)
        self.target_hexagons = self._define_target_region(target_counties)
        self.unified_data = {}
        self.redevelopment_scores = {}

    def _define_target_region(self, target_counties: dict) -> List[str]:
        """Define H3 hexagon coverage for the target counties using polyfill."""
        # This method should fetch county boundaries and create a unified geometry
        # For now, it uses the bioregion as a placeholder
        bioregion_polygon = self.get_bioregion_polygon(self.bioregion)
        hexagons = h3.polyfill(bioregion_polygon.__geo_interface__, self.resolution, geo_json_conformant=True)
        return sorted(list(set(hexagons)))

    def run_comprehensive_analysis(self) -> Dict[str, Dict]:
        """
        Execute all analysis modules and create a unified H3-indexed dataset.
        
        Returns:
            Comprehensive H3-indexed agricultural data.
        """
        module_results = {}
        for module_name, module_instance in self.modules.items():
            try:
                # This method now follows the standardized workflow:
                # 1. Acquire and cache data
                # 2. Process data into H3 format using OSC loaders
                # 3. Run final analysis on H3 data
                result = module_instance.run_analysis(self.target_hexagons)
                module_results[module_name] = result
            except Exception as e:
                print(f"Error processing {module_name}: {e}")
                module_results[module_name] = {}
        
        self._aggregate_module_results(module_results)
        return self.unified_data
    
    def _aggregate_module_results(self, module_results: Dict[str, Dict]):
        """Combine all module results into a unified H3-indexed dataset."""
        for hex_id in self.target_hexagons:
            self.unified_data[hex_id] = {'hex_id': hex_id}
            # Add geometry, metadata, etc.
            # ...
            for module_name, module_data in module_results.items():
                self.unified_data[hex_id][module_name] = module_data.get(hex_id, {})
```

## 10. Implementation Plan

The immediate priority is to operationalize the framework by implementing the standardized workflow for each module.

### **Phase 1: Foundational Implementation (Immediate Priority)**
1.  **Update Configuration**: Correct all outdated URLs and service endpoints in `config/data_urls.json`.
2.  **Implement Caching**: Add the data caching logic to the acquisition script of each of the 8 modules.
3.  **Fix Code Bugs**: Resolve the `fiona` `AttributeError` in the `GeoInferImprovements` module.
4.  **Integrate H3-OSC Loader**: Update each module to use the `osc-geo-h3loader-cli` (via the `GEO-INFER-SPACE` wrapper) to produce standardized H3 output.
5.  **End-to-End Test**: Execute `cascadia_main.py` to confirm data flows through the entire system from download to unified H3 aggregation.

### **Phase 2: Analysis Logic Refinement (Post-Implementation)**
1.  **Refine Scoring**: With real, H3-indexed data available, review and refine the redevelopment potential scoring logic in `unified_backend.py`.
2.  **Enhance Analysis**: Implement more sophisticated analysis within each module.
3.  **Cross-Module Integration**: Strengthen cross-module analysis capabilities.

### **Phase 3: Optimization and Enhancement**
1.  **Performance Optimization**: H3 indexing and query optimization.
2.  **Predictive Modeling**: Active Inference implementation.
3.  **Documentation and Training**: Update all documentation to reflect the working system.

## 11. Quality Assurance and Validation

### **Data Quality Framework**
- **Source Validation**: Multi-source cross-validation for critical data elements
- **Temporal Consistency**: Time-series validation and gap detection
- **Spatial Accuracy**: H3 indexing accuracy and boundary validation
- **Cross-Module Consistency**: Ensuring data consistency across modules

### **Active Inference Integration**
- **Uncertainty Quantification**: Bayesian approaches for data quality assessment
- **Predictive Modeling**: Free energy minimization for agricultural trend prediction
- **Adaptive Learning**: Continuous model improvement based on new data

## Conclusion

This comprehensive framework provides a robust foundation for agricultural land analysis across the Cascadian bioregion. By leveraging the existing GEO-INFER-PLACE infrastructure and integrating specialized agricultural data modules through a unified H3-based backend, the system enables sophisticated cross-domain analysis and visualization capabilities.

The framework addresses the critical data gaps identified in the research while building on the strengths of available datasets. The modular architecture ensures scalability and maintainability while the H3 indexing system provides efficient spatial analysis and visualization capabilities.

**Key Success Factors:**
- **Comprehensive Data Integration**: Unified access to diverse agricultural datasets
- **Cross-Border Analysis**: Seamless integration of California and Oregon data sources
- **Real-Time Capabilities**: Dynamic data updates and analysis
- **Scalable Architecture**: H3-based indexing for efficient spatial operations
- **Interactive Visualization**: Stakeholder-friendly dashboards and analysis tools

This framework positions the GEO-INFER project as a leading platform for agricultural land analysis and redevelopment strategy development in the Pacific Northwest bioregion. 