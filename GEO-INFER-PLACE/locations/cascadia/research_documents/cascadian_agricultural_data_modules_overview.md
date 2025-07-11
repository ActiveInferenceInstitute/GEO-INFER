# Cascadian Agricultural Data Acquisition Modules: Comprehensive Overview

**Northern California + Oregon Agricultural Land Analysis Framework**
*Integrated H3-Based Backend for Joint Analysis and Visualization*

## Executive Summary

This document provides a comprehensive overview and **current status report** for **eight specialized data acquisition modules** designed for agricultural land analysis across the Cascadian bioregion. While the framework is architecturally sound, **all data acquisition modules are currently non-functional due to outdated data sources, broken API endpoints, and code-level bugs.**

This document has been updated to reflect the findings from a full test run on `2025-07-10`. The "Implementation Status" for each module now reflects its operational reality, and "Error Analysis" sections have been added to detail the specific failures that must be addressed to make the framework operational.

### Core Module Architecture: Current Status

| Module | Primary Data Sources | Update Frequency | Implementation Status |
|--------|---------------------|------------------|---------------------|
| **Zoning** | FMMP, ORMAP, Regrid | Biennial/Continuous | **Broken** |
| **Current Use** | NASS CDL, Land IQ, EFU | Annual | **Broken** |
| **Ownership** | ParcelQuest, County Records | Daily/Weekly | **Broken** |
| **Mortgage Debt**| USDA ERS, Farm Credit, County Records | Quarterly/Variable | **Broken** |
| **Improvements** | NASS Infrastructure, Building Footprints | 5-Year/Annual | **Broken (Code Error)** |
| **Surface Water**| eWRIMS/CalWATRS, Oregon WRD | Real-time/Quarterly | **Broken** |
| **Ground Water** | DWR CASGEM, Oregon GWIC | Real-time/Monthly | **Broken** |
| **Power Source** | EIA, Utility Companies | Annual/Variable | **Broken** |

## Module 1: Agricultural Zoning Module (`GeoInferZoning`)

### **Purpose**
Comprehensive agricultural zoning classification and regulatory analysis across northern California and Oregon, providing the foundational land use framework for all subsequent agricultural analysis.

### **Core Functionality**
- **California FMMP Integration**: Real-time access to Farmland Mapping & Monitoring Program data with Important Farmland classifications
- **Oregon EFU Analysis**: Exclusive Farm Use zoning analysis with resource protection status
- **Cross-Border Harmonization**: Standardized zoning classification system for joint analysis
- **Regulatory Tracking**: Zoning change monitoring and development pressure assessment

### **Error Analysis (2025-07-10)**
- **CA FMMP:** The script attempts to download data from dynamic URLs that are no longer valid (HTTP 404). The `README.md` correctly notes that manual download is now required, but the code does not reflect this workflow. All counties fail.
- **OR DLCD:** The ArcGIS service query returns an `HTTP 400 Bad Request`. The service URL or the query parameters are likely incorrect.
- **WA King County:** The service query returns no features, likely due to an incorrect bounding box or an outdated endpoint.

### **Technical Specifications**

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

### **Core Functionality**
- **NASS CDL Integration**: 30-meter resolution annual crop classification
- **Land IQ Crop Mapping**: California-specific high-accuracy crop identification
- **Temporal Analysis**: Multi-year land use change detection
- **Production Intensity**: Crop productivity and agricultural intensity metrics

### **Error Analysis (2025-07-10)**
- **NASS CDL:** The `nassgeodata.gmu.edu` API endpoint fails for all queries across multiple years, resulting in no data being downloaded. The script falls back through previous years and ultimately fails to acquire any raster data. The SSL certificate for the endpoint is also expired, requiring `verify=False`.

### **Technical Specifications**

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

### **Core Functionality**
- **Ownership Concentration Analysis**: Large-scale ownership pattern identification
- **Institutional Mapping**: Corporate, family, and investment ownership classification
- **Cross-Border Integration**: Unified ownership analysis across state boundaries
- **Temporal Ownership Tracking**: Ownership change and transaction analysis

### **Error Analysis (2025-07-10)**
- **CA Parcels:** The ArcGIS service query to `services.gis.ca.gov` for parcel data returns no features. The endpoint is likely outdated or requires different query parameters.

### **Technical Specifications**

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

### **Core Functionality**
- **USDA ERS Integration**: Farm sector debt statistics and trends
- **Regional Debt Modeling**: County-level debt estimation using available indicators
- **Financial Risk Assessment**: Debt-to-asset ratio analysis and risk modeling
- **Institutional Lending Patterns**: Farm Credit System and commercial bank analysis

### **Error Analysis (2025-07-10)**
- **HMDA Data:** The script attempts to download bulk CSV data from an S3 bucket (`s3.amazonaws.com/cfpb-hmda-public`). The URLs result in `HTTP 404 Not Found` errors for multiple years and states, indicating the path structure or bucket name has changed.

### **Technical Specifications**

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

### **Core Functionality**
- **Building Footprint Analysis**: Agricultural building identification and classification
- **Irrigation Infrastructure**: Water management system mapping and valuation
- **Processing Facilities**: Agricultural processing and storage facility identification
- **Infrastructure Valuation**: Improvement value estimation and depreciation modeling

### **Error Analysis (2025-07-10)**
- **Fatal Code Error:** The module fails to run due to a Python error: `AttributeError: module 'fiona' has no attribute 'path'`. This is a code-level bug in how the `fiona` library is being used to read data and prevents any analysis for this module.

### **Technical Specifications**

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

### **Core Functionality**
- **Water Rights Integration**: Cross-state water rights database harmonization
- **Priority Date Analysis**: Water rights seniority and allocation priority mapping
- **Seasonal Allocation**: Temporal water availability and allocation patterns
- **Irrigation Use Tracking**: Agricultural water use reporting and analysis

### **Error Analysis (2025-07-10)**
- **NHD Services:** The queries to the National Hydrography Dataset (NHD) for flowlines and waterbodies (`hydro.nationalmap.gov`) return no features for the analysis bounding box. The service endpoint or expected parameters may have changed.

### **Technical Specifications**

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

### **Core Functionality**
- **Groundwater Level Monitoring**: Real-time groundwater level tracking
- **Well Density Analysis**: Agricultural well distribution and capacity analysis
- **Aquifer Mapping**: Groundwater basin and aquifer boundary integration
- **Sustainability Assessment**: Groundwater sustainability plan integration

### **Error Analysis (2025-07-10)**
- **USGS NWIS:** All batched requests to the USGS groundwater level service (`waterservices.usgs.gov/nwis/gwlevels/`) fail with an `HTTP 400 Bad Request`. This indicates the API request format (e.g., bounding box parameters) is no longer valid.

### **Technical Specifications**

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

### **Core Functionality**
- **Utility Service Territory Mapping**: Agricultural power service area identification
- **Energy Consumption Modeling**: Agricultural energy use estimation by crop type
- **Renewable Energy Integration**: On-farm renewable energy system identification
- **Grid Reliability Analysis**: Power infrastructure reliability for agricultural operations

### **Error Analysis (2025-07-10)**
- **HIFLD Service:** The query to the HIFLD ArcGIS service for transmission lines returns zero records, suggesting the endpoint is outdated or the query is incorrect.

### **Technical Specifications**

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

## Unified H3-Based Backend Architecture

### **H3 Spatial Indexing Framework**

```python
class CascadianAgriculturalH3Backend:
    """Unified H3-indexed backend for all 8 agricultural data modules"""
    
    def __init__(self, resolution: int = 8, bioregion: str = 'Cascadia'):
        self.resolution = resolution
        self.bioregion = bioregion
        self.modules = {
            'zoning': geo_infer_zoning.GeoInferZoning(resolution),
            'current_use': geo_infer_current_use.GeoInferCurrentUse(resolution),
            'ownership': geo_infer_ownership.GeoInferOwnership(resolution),
            'mortgage_debt': geo_infer_mortgage_debt.GeoInferMortgageDebt(resolution),
            'improvements': geo_infer_improvements.GeoInferImprovements(resolution),
            'surface_water': geo_infer_surface_water.GeoInferSurfaceWater(resolution),
            'ground_water': geo_infer_ground_water.GeoInferGroundWater(resolution),
            'power_source': geo_infer_power_source.GeoInferPowerSource(resolution)
        }
        self.target_hexagons = self._define_target_region()
        self.unified_data = {}
        self.redevelopment_scores = {}

    def _define_target_region(self) -> List[str]:
        """Define H3 hexagon coverage for the bioregion using polyfill."""
        bioregion_polygon = self.get_bioregion_polygon(self.bioregion)
        hexagons = polyfill(bioregion_polygon, self.resolution)
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
                # Each module should have a standardized 'run_analysis' method
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

### **Cross-Module Analysis Framework**

```python
class CascadianCrossModuleAnalyzer:
    """Cross-module analysis and integration capabilities"""
    
    def __init__(self, backend: CascadianAgriculturalH3Backend):
        self.backend = backend
    
    def calculate_agricultural_redevelopment_potential(self) -> Dict[str, float]:
        """
        Calculate comprehensive agricultural redevelopment potential scores.
        
        Returns:
            Redevelopment potential scores for each hexagon.
        """
        # This logic is now encapsulated within the backend
        return self.backend.calculate_agricultural_redevelopment_potential()

    def identify_agricultural_clusters(self) -> Dict[str, List[str]]:
        """
        Identify clusters of similar agricultural characteristics.
        
        Returns:
            Dictionary mapping cluster types to lists of hexagon IDs.
        """
        # This would use the backend's unified_data attribute
        features = []
        hex_ids = []
        
        for hex_id, hex_data in self.backend.unified_data.items():
            features.append(self.extract_feature_vector(hex_data))
            hex_ids.append(hex_id)
        
        # Apply clustering algorithm
        # ...
        return {} # Placeholder
```

## Visualization and Dashboard Integration

### **Interactive Dashboard Framework**

The dashboard generation is now a method of the `CascadianAgriculturalH3Backend`, simplifying its creation.

```python
class CascadianAgriculturalH3Backend:
    # ... (other methods)

    def generate_interactive_dashboard(self, output_path: str):
        """
        Generates an interactive Folium dashboard with multiple data overlays.
        
        Args:
            output_path: Path to save the HTML dashboard file.
        """
        map_center = self.get_map_center()
        dashboard_map = folium.Map(location=map_center, zoom_start=7)

        # Create feature groups for togglable layers
        redevelopment_layer = folium.FeatureGroup(name="Redevelopment Potential", show=True)
        zoning_layer = folium.FeatureGroup(name="Zoning", show=False)
        # ... other layers for current use, water, etc.

        # Populate layers with data from self.unified_data and self.redevelopment_scores
        for h3_index, hex_data in self.unified_data.items():
            # Add polygons to each layer with relevant popups and styling
            # ...
            pass
            
        # Add layers to map
        redevelopment_layer.add_to(dashboard_map)
        zoning_layer.add_to(dashboard_map)
        # ...
        
        # Add layer control
        folium.LayerControl().add_to(dashboard_map)
        
        dashboard_map.save(output_path)
        print(f"Dashboard saved to {output_path}")

# Example usage in main script:
# backend = CascadianAgriculturalH3Backend()
# backend.run_comprehensive_analysis()
# backend.calculate_agricultural_redevelopment_potential()
# backend.generate_interactive_dashboard("./dashboard.html")
```

## Implementation Timeline and Priorities: **REVISED**

The original timeline is no longer valid. The immediate priority is **system-wide repair and data source validation.**

### **Phase 1: Triage and Repair (Immediate Priority)**
1.  **Fix Data Sources:** Investigate and update every broken API endpoint and download URL identified in the "Error Analysis" sections for all 8 modules. Update `config/data_urls.json`.
2.  **Fix Code Bugs:** Resolve the `AttributeError` in the `GeoInferImprovements` module.
3.  **Validate Data Loading:** Ensure each module can successfully load real, non-mock data into a GeoDataFrame or appropriate data structure.
4.  **Full Pipeline Test:** Execute `cascadia_main.py` to confirm data flows through the entire system without crashing.

### **Phase 2: Analysis Logic Refinement (Post-Repair)**
1.  **Refine Scoring:** With real data available, review and refine the redevelopment potential scoring logic in `unified_backend.py`.
2.  **Enhance Analysis:** Implement more sophisticated analysis within each module now that data is accessible.
3.  **Cross-Module Integration**: Strengthen cross-module analysis capabilities.

### **Phase 3: Optimization and Enhancement**
1.  **Performance Optimization**: H3 indexing and query optimization.
2.  **Predictive Modeling**: Active Inference implementation.
3.  **Stakeholder Integration**: Community engagement features.
4.  **Documentation and Training**: Update all documentation to reflect the working system.

## Quality Assurance and Validation

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