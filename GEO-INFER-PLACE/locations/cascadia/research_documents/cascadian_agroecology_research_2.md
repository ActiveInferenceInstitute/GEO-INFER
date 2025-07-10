<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# Comprehensive Agricultural Land Redevelopment Dataset Catalog: Technical Specifications for Superior California and Oregon Bioregion Integration with geo-infer

This comprehensive analysis identifies and documents the empirical datasets available for agricultural land redevelopment analysis across the specified bioregion, encompassing Superior California counties (Butte, Colusa, Del Norte, Glenn, Humboldt, Lake, Lassen, Mendocino, Modoc, Nevada, Plumas, Shasta, Sierra, Siskiyou, Tehama, and Trinity) and all Oregon counties. The research provides detailed technical specifications for data access, integration methodologies, and compatibility protocols for the Active Inference Institute's geo-infer package.

## Executive Summary

The bioregion presents a complex agricultural landscape requiring multi-source data integration for effective redevelopment strategy. This analysis identifies **fourteen primary dataset categories** spanning parcel ownership, water rights, zoning designations, infrastructure, and financial indicators. Key findings indicate that while comprehensive parcel data exists through both commercial and public sources, successful integration requires standardized preprocessing workflows and spatial harmonization protocols. The geo-infer package provides an optimal framework for synthesizing these diverse datasets through Active Inference methodologies, enabling sophisticated pattern recognition and predictive modeling for agricultural land redevelopment decisions.

## Agricultural Parcel Data Infrastructure

### California Parcel Data Sources

**ParcelQuest California** emerges as the most comprehensive commercial source for California agricultural parcels, providing **daily-updated data** from all 58 counties directly sourced from county assessor offices[^1][^2]. The service maintains over 13 million parcel records with complete coverage of the specified Superior California counties. Technical specifications include:

- **API Endpoint**: REST API with JSON response format
- **Authentication**: Commercial API key required
- **Update Frequency**: Daily synchronization with county sources
- **Coverage**: 100% parcel coverage across target counties
- **Key Attributes**: APN, owner information, zoning designation, assessed value, acreage, improvement details

**Alternative Sources**: Individual county assessor offices provide free access to parcel data, though with varying formats and update frequencies. Nevada County offers comprehensive GIS tools through their MyNeighborhood application[^3], while other counties provide downloadable shapefiles and database exports[^4].

### Oregon Parcel Data Sources

**ORMAP (Oregon Property Tax Map)** serves as the authoritative statewide parcel dataset, maintained as a **continuously updated digital cadastral base map**[^5]. This publicly accessible resource provides comprehensive coverage across all Oregon counties with the following specifications:

- **Data Source**: Oregon Department of Revenue coordination with local jurisdictions
- **Access Method**: Public download through data.oregon.gov
- **Technical Format**: Shapefiles, GeoJSON, feature services
- **Update Protocol**: Continuous maintenance through local jurisdiction reporting
- **Spatial Accuracy**: Survey-grade precision for property boundaries

**County-Level Implementations**: Individual Oregon counties maintain enhanced datasets. Columbia County provides bi-weekly updated shape files including Tax25.mdb, taxlot25.shp, and associated attribute files[^6]. Crook County offers both open data portal access and REST services for spatial data distribution[^7].

## Land Use and Zoning Classification Systems

### California Agricultural Zoning Framework

The **California General Plan Land Use dataset** provides comprehensive zoning information across 532 of 539 jurisdictions[^8]. This state-aggregated resource underwent extensive geospatial processing, converting PDF and image-based general plans into standardized digital formats:

- **Data Coverage**: 532 jurisdictions with complete general plan data
- **Collection Period**: Late 2021 through 2022, with 2023 updates
- **Technical Format**: ESRI Geodatabases, Shapefiles, CSV, GeoJSON, KML
- **Standardization**: Contiguous areas merged, features under 4 square meters removed
- **Agricultural Categories**: Exclusive Farm Use (EFU), Agricultural Preserve, Rural Residential

**California Important Farmland Mapping** provides additional agricultural classification through the Farmland Mapping and Monitoring Program (FMMP)[^9]. This program delivers:

- **Classification System**: Prime Farmland, Unique Farmland, Farmland of Statewide Importance
- **Update Cycle**: Biennial updates with 2022 data available for target counties
- **Interactive Access**: California Important Farmland Finder with calculation capabilities
- **Time Series**: Historical data from 1984 to present for trend analysis


### Oregon Agricultural Land Protection Framework

Oregon's **Exclusive Farm Use (EFU) zoning** system provides the primary agricultural land protection mechanism. The 2023 Oregon Zoning dataset encompasses 229 local jurisdictions[^10]:

- **Statewide Coverage**: Digital framework with standardized classification
- **EFU Protection**: 15.6 million acres under resource zoning (99% retention since 1987)[^11]
- **Classification System**: Agricultural Lands Definition based on NRCS soil classifications
- **Data Availability**: Vector digital data through ArcGIS sharing services

**Specialized Agricultural Designations**: Oregon's system includes Mixed Farm-Forest zones and Agricultural-Residential categories, providing nuanced classification for diverse agricultural operations[^12][^13].

![Technical Integration Architecture for Agricultural Land Redevelopment Analysis with geo-infer Package](https://ppl-ai-code-interpreter-files.s3.amazonaws.com/web/direct-files/c6e95593f59e77f0a1989cf8d4edaf53/fd8557f7-4328-4233-ab8a-1142edee2a0d/d5c8d37f.png)

Technical Integration Architecture for Agricultural Land Redevelopment Analysis with geo-infer Package

## Water Rights and Hydrological Data Systems

### California Water Rights Infrastructure

**eWRIMS (Electronic Water Rights Information Management System)** historically served as California's primary water rights database, though it's being replaced by **CalWATRS (California Water Accounting, Tracking, and Reporting System)** as of July 2025[^14]. The transition presents both challenges and opportunities:

- **Legacy System**: eWRIMS contains comprehensive historical records through June 2025
- **New System**: CalWATRS launches July 2025 with enhanced functionality
- **Data Elements**: Water right holder information, priority dates, flow rates, points of diversion
- **Spatial Component**: GIS web mapping application for geographic analysis
- **Access Protocol**: Public database with search capabilities by owner, watershed, county

**California Water Rights Detailed Summary Lists** provide comprehensive tabular data[^15]:

- **Update Frequency**: Regular updates through 2024
- **Format**: CSV downloads with complete water rights inventory
- **Technical Specifications**: Includes enforcement actions and use reporting data


### Oregon Water Rights Framework

**Oregon Water Rights Database** maintains comprehensive statewide coverage through the Oregon Water Resources Department[^16]. Technical specifications include:

- **Spatial Coverage**: Point of diversion locations with associated rights data
- **Data Elements**: Permit numbers, priority dates, flow rates, use classifications
- **Access Method**: Public GIS services through geohub.oregon.gov
- **Update Protocol**: Regular maintenance with current data standards
- **Integration**: Compatible with ORMAP parcel framework for spatial analysis

**Water Rights Points of Diversion** dataset provides precise spatial locations[^17]:

- **Coverage**: All current individually held water rights
- **Exclusions**: Irrigation district rights, applications, temporary transfers
- **Format**: Shapefile and feature service formats
- **Documentation**: Comprehensive metadata and compilation procedures


## Agricultural Census and Production Data

### USDA NASS Data Infrastructure

**Census of Agriculture** provides the foundational agricultural statistics framework, conducted every five years with comprehensive county-level data[^18][^19]. The 2022 Census represents the most current comprehensive dataset:

- **Data Scope**: Farm operations, land use, operator characteristics, production practices
- **Geographic Coverage**: All counties in target bioregion
- **Confidentiality**: Individual operation data protected, aggregated totals published
- **Farm Definition**: Operations with \$1,000 or more in agricultural products (current since 1974)

**NASS QuickStats API** enables real-time access to agricultural production data[^20][^21]:

- **API Endpoint**: quickstats.nass.usda.gov/api
- **Authentication**: Free API key required
- **Query Parameters**: Commodity, geographic level, time period, statistic type
- **Rate Limits**: 50,000 records maximum per request
- **Data Categories**: Production, yield, value, acreage by commodity type

**Technical Implementation for R Users**: The rnassqs package provides streamlined API access[^21][^22]:

```
# Installation and authentication
install.packages("rnassqs")
nassqs_auth(key = "<API_KEY>")

# Example query for target counties
params <- list(
  commodity_desc = "CORN", 
  year = 2022,
  state_alpha = c("CA", "OR"),
  agg_level_desc = "COUNTY"
)
```


### Cropland Data Layer Integration

**USDA NASS Cropland Data Layer (CDL)** provides annual 30-meter resolution crop classification[^23][^24]:

- **Spatial Resolution**: 30-meter pixel classification
- **Temporal Coverage**: Annual updates from 2008 forward
- **Classification System**: Crop-specific land cover with 100+ categories
- **Data Sources**: Satellite imagery, FSA Common Land Unit data, ground reference data
- **Format**: GeoTIFF raster data with associated metadata


## Mortgage Debt and Financial Indicators

### Farm Sector Financial Data

**USDA Economic Research Service (ERS)** maintains comprehensive farm sector financial statistics[^25][^26]. Key datasets include:

**Farm Sector Balance Sheet Data**:

- **Real Estate Debt**: Expected \$374.2 billion in 2025 (3.9% increase)[^25]
- **Non-Real Estate Debt**: Projected \$187.6 billion in 2025
- **Historical Trends**: 87.5% increase in real estate debt since 2009 (inflation-adjusted)[^27]
- **Update Frequency**: Quarterly forecasts with annual comprehensive reports

**Farm Business Debt Analysis** (2012-2021)[^28]:

- **Total Farm Debt**: \$503.7 billion in 2021 (34% increase from 2012)
- **Real Estate Component**: \$344.5 billion (68% of total debt)
- **Geographic Distribution**: State and regional breakdowns available
- **Lending Sources**: Farm Credit System provides 47% of real estate loans


### Commercial Mortgage Databases

**FHFA Public Use Database** provides mortgage-level data for government-sponsored enterprises[^29]:

- **Data Elements**: LTV ratios, DTI ratios, borrower demographics, census tract locations
- **Geographic Scope**: Census tract level aggregation
- **Update Frequency**: Annual releases with expanded HMDA-compatible data
- **Access Format**: CSV downloads with comprehensive metadata


## Building Improvements and Infrastructure Data

### Building Footprint Datasets

**Microsoft/Google Open Buildings Dataset** provides the most comprehensive building footprint coverage[^30]:

- **Scale**: 2.5 billion building footprints globally
- **Regional Coverage**: 92% of Level 0 administrative boundaries
- **Technical Format**: Cloud-native formats (GeoParquet, FlatGeobuf, PMTiles)
- **Attributes**: Building area, confidence scores, source attribution
- **Update Protocol**: Periodic updates with latest imagery analysis

**Commercial Alternatives** include ATTOM Data and LightBox building footprints[^31][^32]:

- **ATTOM Coverage**: 187 million buildings nationwide
- **AI Processing**: Advanced algorithms using aerial imagery and LiDAR
- **Parcel Integration**: Geospatially matched to property boundaries
- **Attributes**: Building area, height, number of stories, elevation data


### Property Improvement Datasets

**NAHB Remodeling Expenditures** provides ZIP-code level improvement spending data[^33][^34]:

- **Geographic Scope**: 26,000+ ZIP codes nationally
- **Data Elements**: Home improvement spending, homeowner education, income levels
- **Format**: Microsoft Excel spreadsheets
- **Historical Data**: Multiple years available for trend analysis


## Surface Water and Groundwater Resources

### USGS Water Data Infrastructure

**USGS National Water Information System (NWIS)** provides comprehensive hydrological monitoring[^35]:

- **Site Coverage**: 1.5 million monitoring sites across all states
- **Data Types**: Stream flow, groundwater levels, water quality parameters
- **Real-Time Access**: Current conditions with historical archives
- **API Access**: RESTful web services for automated data retrieval
- **Geographic Tools**: Interactive mapping with site selection capabilities

**National Ground-Water Monitoring Network** offers specialized groundwater data[^36]:

- **Network Structure**: Federal, state, and local monitoring partnerships
- **Data Portal**: Web-based mapping application with analysis tools
- **Parameters**: Water levels, quality indicators, well construction details
- **Funding**: USGS Cooperative Agreements with data providers


### State-Specific Water Monitoring

**California Water Data Integration**: Multiple agencies contribute to comprehensive coverage:

- **State Water Board**: Surface water rights and quality monitoring
- **DWR**: Groundwater monitoring and SGMA compliance data
- **Regional Boards**: Local water quality and use data

**Oregon Water Resources Framework**:

- **OWRD**: Comprehensive water rights and use monitoring
- **Real-Time Data**: Stream flow and water level monitoring
- **Integration**: Compatible with ORMAP spatial framework


## Power Infrastructure and Energy Data

### Utility Infrastructure Mapping

**Electric Utility GIS Systems** vary by provider but follow standardized frameworks[^37][^38][^39]:

- **Asset Categories**: Transmission lines, distribution systems, substations, service territories
- **Data Standards**: ESRI utility data models with standardized symbology
- **Access Protocols**: Varies by utility (public, restricted, commercial licensing)
- **Integration Capabilities**: Compatible with standard GIS formats and web services

**Power Source Analysis Requirements**:

- **Grid Connection**: Transmission and distribution line proximity analysis
- **Renewable Resources**: Solar irradiance and wind resource mapping
- **Infrastructure Capacity**: Substation capacity and expansion potential
- **Service Territory**: Utility service area boundaries and rate structures

![Technical Implementation: ParcelQuest Data Integration with geo-infer Package](https://ppl-ai-code-interpreter-files.s3.amazonaws.com/web/direct-files/c6e95593f59e77f0a1989cf8d4edaf53/5f53f5ad-dd1a-4c3a-b877-2fcd4e147f12/ca35ada5.png)

Technical Implementation: ParcelQuest Data Integration with geo-infer Package

## Technical Integration Specifications for geo-infer Package

### Data Standardization Framework

The Active Inference Institute's geo-infer package requires standardized input formats for optimal performance. Essential preprocessing steps include:

**Spatial Harmonization**:

- **Coordinate System**: Standardize to common projection (recommended: NAD83 UTM appropriate zone)
- **Geometry Validation**: Remove invalid polygons, fix topology errors
- **Spatial Resolution**: Align datasets to common spatial grid for analysis

**Attribute Standardization**:

- **Naming Conventions**: Consistent field naming across datasets
- **Data Types**: Standardize numeric formats, date/time representations
- **Classification Systems**: Harmonize zoning codes and land use categories
- **Null Value Handling**: Consistent missing data representation


### Integration Architecture

**Data Pipeline Components**:

1. **Acquisition Layer**: API connections and data retrieval protocols
2. **Preprocessing Layer**: Data cleaning, validation, and standardization
3. **Integration Layer**: Spatial joins, attribute matching, and fusion algorithms
4. **Analysis Layer**: geo-infer Active Inference framework implementation
5. **Output Layer**: Results formatting and visualization

**Quality Assurance Protocols**:

- **Completeness Metrics**: Data coverage assessment by geographic area
- **Accuracy Validation**: Cross-reference with authoritative sources
- **Temporal Consistency**: Ensure data currency across integrated datasets
- **Metadata Management**: Comprehensive lineage and quality documentation


### Active Inference Implementation

**Bayesian Framework Integration**:

- **Prior Knowledge**: Incorporate domain expertise about agricultural land use patterns
- **Evidence Updates**: Process new data through Active Inference updating mechanisms
- **Uncertainty Quantification**: Maintain probability distributions for key parameters
- **Decision Making**: Optimize agricultural land redevelopment strategies under uncertainty

**Spatial Modeling Capabilities**:

- **Pattern Recognition**: Identify optimal agricultural land use configurations
- **Predictive Analytics**: Forecast future land use changes and impacts
- **Risk Assessment**: Evaluate development risks across multiple scenarios
- **Resource Optimization**: Balance competing objectives for land use allocation


## Implementation Recommendations

### Priority Dataset Integration Sequence

**Phase 1: Foundation Datasets**

1. **Parcel Boundaries**: ORMAP (Oregon) and ParcelQuest (California)
2. **Agricultural Zoning**: State zoning datasets with EFU classifications
3. **Water Rights**: eWRIMS/CalWATRS (California) and OWRD (Oregon)

**Phase 2: Enhanced Attribution**

1. **Agricultural Census**: NASS Census and QuickStats integration
2. **Cropland Classification**: CDL annual datasets
3. **Building Infrastructure**: Open Buildings or commercial footprint data

**Phase 3: Specialized Analysis Layers**

1. **Financial Indicators**: Farm debt and mortgage data integration
2. **Hydrological Data**: USGS monitoring network integration
3. **Power Infrastructure**: Utility-specific GIS data acquisition

### Data Access and Licensing Considerations

**Public Domain Resources**: NASS data, USGS water data, and Oregon state datasets require no licensing fees but mandate proper attribution.

**Commercial Data Sources**: ParcelQuest and building footprint providers require commercial licensing agreements with usage restrictions and rate limiting.

**State and Local Data**: California county data varies by jurisdiction, with some requiring data sharing agreements for bulk access.

### Technical Infrastructure Requirements

**Computing Resources**: Large-scale spatial analysis requires substantial memory and processing capabilities, particularly for statewide parcel integration.

**Storage Architecture**: Recommend cloud-based spatial databases with versioning capabilities for dataset management.

**API Management**: Implement rate limiting and caching strategies for commercial API access optimization.

## Conclusion

The comprehensive dataset catalog identified through this analysis provides robust empirical foundations for agricultural land redevelopment strategy in the Superior California and Oregon bioregion. The integration of fourteen primary dataset categories through the geo-infer package framework enables sophisticated Active Inference modeling capabilities, supporting evidence-based decision making for agricultural land optimization.

Key success factors for implementation include establishing standardized data preprocessing workflows, maintaining comprehensive quality assurance protocols, and developing phased integration strategies that prioritize foundational datasets while gradually incorporating specialized analytical layers. The technical specifications and access protocols documented in this analysis provide the necessary framework for successful geo-infer package integration, enabling advanced agricultural land redevelopment analysis across the target bioregion.

The Active Inference framework offers particular advantages for this application domain, providing principled approaches to uncertainty quantification, multi-objective optimization, and adaptive decision making under complex spatial and temporal constraints. Through systematic integration of the identified datasets with geo-infer capabilities, stakeholders can develop sophisticated understanding of agricultural land redevelopment opportunities while maintaining rigorous scientific standards for analysis and decision support.

<div style="text-align: center">⁂</div>

[^1]: https://www.parcelquest.com

[^2]: https://www.esri.com/partners/parcelquest-a2T5x000006aecHEAQ?srsltid=AfmBOopTHM1ib_E_CPi_ZUxd8YdaJhnP0i5ufLg7Y_hCV0sxJcRhOZdu

[^3]: https://www.nevadacountyca.gov/182/Maps-Parcel-Data

[^4]: https://www.placer.ca.gov/Faq.aspx?QID=471

[^5]: https://catalog.data.gov/dataset/ormap-the-oregon-property-tax-map

[^6]: https://www.columbiacountyor.gov/departments/Assessor/CartographyandGeographicInformationSystem

[^7]: https://co.crook.or.us/gis/page/gis-data

[^8]: https://lab.data.ca.gov/dataset/california-general-plan-land-use

[^9]: https://www.conservation.ca.gov/dlrp/fmmp

[^10]: https://www.arcgis.com/sharing/rest/content/items/72416393747c4cdf9110920656f90f83/info/metadata/metadata.xml?format=default\&output=html

[^11]: https://www.oregon.gov/lcd/FF/Documents/Farm_Forest_Report_2022_2023.pdf

[^12]: https://www.fsl.orst.edu/pnwerc/wrb/Atlas_web_compressed/6.LandUse_Cover/6c.zoning_web.pdf

[^13]: https://www.oregonlegislature.gov/committees/2019I1-HAGLU/Reports/2018-2019 DLCD Farm Forest Report.pdf

[^14]: https://www.waterboards.ca.gov/waterrights/water_issues/programs/ewrims/

[^15]: https://catalog.data.gov/dataset/california-water-rights-list-detail-summary-list

[^16]: https://catalog.data.gov/dataset/water-rights

[^17]: https://databasin.org/datasets/fd9fc5a515bc430fb9cb6443698d6aea/

[^18]: https://www.usda.gov/about-usda/news/blog/2022/09/02/census-agriculture-collects-thousands-data-points-critical-us-ag

[^19]: https://en.wikipedia.org/wiki/United_States_Census_of_Agriculture

[^20]: https://quickstats.nass.usda.gov/api

[^21]: https://docs.ropensci.org/rnassqs/

[^22]: https://cran.r-project.org/web/packages/rnassqs/rnassqs.pdf

[^23]: https://data.nass.usda.gov/Research_and_Science/Cropland/metadata/metadata_or23.htm

[^24]: https://water.usgs.gov/catalog/datasets/ef517a23-cfe4-4af1-846c-017d20f0832e/

[^25]: http://www.ers.usda.gov/topics/farm-economy/farm-sector-income-finances/assets-debt-and-wealth

[^26]: https://www.farmprogress.com/management/farm-sector-real-estate-debt-hits-record-high

[^27]: https://www.ers.usda.gov/data-products/charts-of-note/chart-detail?chartId=106426

[^28]: https://ageconsearch.umn.edu/record/344131/files/eib-273.pdf

[^29]: https://www.fhfa.gov/data/pudb

[^30]: https://gee-community-catalog.org/projects/global_buildings/

[^31]: https://www.lightboxre.com/data/building-footprints/

[^32]: https://www.attomdata.com/data/boundaries-data/building-footprint/

[^33]: https://storefront.nahb.org/product/40446

[^34]: http://storefront.nahb.org/product/37057

[^35]: https://waterdata.usgs.gov/or/nwis

[^36]: https://www.usgs.gov/apps/ngwmn/

[^37]: https://www.adesso.de/en/news/blog/grid-and-analytics-geoinformation-systems-gis-and-digital-twins-for-low-voltage-power-grids-in-the-energy-industry.jsp

[^38]: https://www.giscloud.com/blog/gis-for-electric-utilities/

[^39]: https://www.esri.com/en-us/industries/utilities

[^40]: https://www.nass.usda.gov/Research_and_Science/Cropland/metadata/metadata_or21.htm

[^41]: https://sonomacounty.ca.gov/administrative-support-and-fiscal-services/clerk-recorder-assessor-registrar-of-voters/assessor/assessor-maps

[^42]: https://www.fao.org/geospatial/resources/tools/agro-maps/ru/

[^43]: https://ucanr.edu/statewide-program/informatics-and-gis-program/finding-and-using-parcel-data-california

[^44]: https://www.eea.europa.eu/en/datahub/datahubitem-view/a0aacdd2-46b2-485a-ac49-162936d84395

[^45]: https://extension.oregonstate.edu/business-economics/rural-development/oregon-agriculture-numbers-part-1-total-farms-farmland-acres

[^46]: https://essd.copernicus.org/articles/13/5951/2021/

[^47]: https://maps.conservation.ca.gov/dlrp/WilliamsonAct/

[^48]: https://regrid.com/california-parcel-data

[^49]: https://www.oregon.gov/lcd/UP/Documents/202200201_HB%202918_Surplus_Lands_Database_Legislative_Report.pdf

[^50]: https://www.reddit.com/r/gis/comments/3lznnn/california_county_assessor_parcel_data/

[^51]: https://data.ca.gov/dataset/california-important-farmland-2020

[^52]: https://www.tid.org/wp-content/uploads/2023/11/IB-Water-Rights-CMUA.pdf

[^53]: https://www.azwater.gov/news/articles/2019-04-01

[^54]: https://catalog.data.gov/dataset/california-water-rights-enforcement-actions

[^55]: https://www.oregon.gov/OWRD/programs/regulation/Pages/default.aspx

[^56]: https://www.tceq.texas.gov/permitting/water_rights/wr-permitting/wrwud

[^57]: https://www.azwater.gov/news/articles/2019-14-03

[^58]: https://www.law.berkeley.edu/wp-content/uploads/2021/07/Piloting-a-Water-Rights-Information-System-for-California-July-2021.pdf

[^59]: https://pubs.usgs.gov/sir/2006/5205/section9.html

[^60]: https://www.waterboards.ca.gov/resources/data_databases/

[^61]: https://catalog.data.gov/dataset/california-water-rights-water-use-reported-df8b0

[^62]: https://legal-planet.org/2015/07/07/a-water-rights-database-for-californias-future/

[^63]: https://pmc.ncbi.nlm.nih.gov/articles/PMC11156903/

[^64]: https://internetofwater.org/blog/unveiling-westdaat-a-breakthrough-for-water-rights-data-management-in-the-western-united-states

[^65]: https://www.edf.org/sites/default/files/documents/edf_california_sgma_allocations.pdf

[^66]: https://en.wikipedia.org/wiki/Agricultural_zoning

[^67]: https://www.youtube.com/watch?v=l-utQJXq-eQ

[^68]: https://maps.conservation.ca.gov/planning/

[^69]: https://www.codepublishing.com/CA/RanchoCordova/html/RanchoCordova23/RanchoCordova23307.html

[^70]: https://www.reddit.com/r/gis/comments/16175kp/zoning_data_for_municipalities_in_ca/

[^71]: https://www.oregon.gov/lcd/TGM/Documents/ModelCode/ART2_OMC_ed3.1.pdf

[^72]: https://www.numberanalytics.com/blog/mastering-agricultural-zoning-regulations-agm-470

[^73]: https://belonging.berkeley.edu/california-zoning-atlas

[^74]: https://flypix.ai/blog/agricultural-zoning/

[^75]: https://github.com/OtheringBelonging/CAZoning

[^76]: https://pgplanning.org/development-process/zoning-applications/guide-to-zoning-categories/rural-and-agricultural-zones/

[^77]: https://www.esri.com/content/dam/esrisites/en-us/media/ebooks/g509879-gis-anchor-grid-ebk-8-19.pdf?srsltid=AfmBOooFPLmUzaowWnC81NDx6vY3ZCW9xp1lpfEls86UaQcaS5uvZITK

[^78]: https://carto.com/spatial-data-catalog/real-estate-data

[^79]: https://fred.stlouisfed.org/series/MDOTHFRAFAMCTPFP

[^80]: https://figshare.com/articles/dataset/CityPropStats_Property_statistics_by_building_age_1910-2020_for_795_core-based_statistical_areas_in_the_United_States/28395488

[^81]: https://fred.stlouisfed.org/tags/series?t=agriculture%3Bdebt%3Busa

[^82]: https://ag.purdue.edu/commercialag/home/wp-content/uploads/2022/10/20221004_Langemeier_USFarmSectorBalanceSheet.pdf

[^83]: https://regrid.com/building-footprints

[^84]: http://www.ers.usda.gov/data-products/charts-of-note/chart-detail?chartId=106426

[^85]: https://usda.library.cornell.edu/concern/publications/fq977t769?locale=en

[^86]: https://brightdata.com/products/datasets/real-estate

[^87]: http://sites.research.google/gr/open-buildings/

[^88]: https://github.com/ActiveInferenceInstitute

[^89]: https://github.com/NRCan/geo-inference

[^90]: https://pypi.org/project/mcaapi/

[^91]: https://www.youtube.com/watch?v=nT11dSbr6QE

[^92]: https://github.com/MarjanAsgari/geo-inference-dask

[^93]: https://github.com/foxbatcs/mcaapi

[^94]: https://www.activeinference.institute

[^95]: https://github.com/networkdynamics/geoinference

[^96]: https://github.com/ottinger/ok-assessor-scraper

[^97]: https://ucanr.edu/blog/topics-subtropics/article/check-it-out-usda-state-and-county-ag-profiles

[^98]: https://www.mdpi.com/1099-4300/27/1/62

[^99]: https://github.com/NRCan/geo-deep-learning/issues/565

[^100]: https://www.taxnetusa.com/data/web-service-api/

[^101]: https://farmlandinfo.org/statistics/census-of-agriculture/

[^102]: https://pdfs.semanticscholar.org/4eb5/2dd3d55ace27c5d868d7a3f5e9f7546525e4.pdf

[^103]: https://github.com/inlab-geo/cofi

[^104]: https://apify.com/adrian_horning/mclennan-county-tax-assessor-api/api/python

[^105]: https://dem.ri.gov/media/76966/download

[^106]: https://www.nass.usda.gov/developer/index.php

[^107]: https://www.nass.usda.gov/Quick_Stats/

[^108]: https://www.reddit.com/r/learnpython/comments/1dz8v75/trying_to_access_usda_nass_api_with_no_success/

[^109]: https://www.nass.usda.gov/Help/index.php

[^110]: https://app.regrid.com/us/ca/san

[^111]: https://catalog.data.gov/dataset/quick-stats-agricultural-database-api

[^112]: http://www.ers.usda.gov/developer/geospatial-apis/nass-map-service-documentation

[^113]: https://guides.lib.berkeley.edu/gis/California

[^114]: https://app.regrid.com/us/or

[^115]: https://gis.santaclaracounty.gov/access-countywide-gis-map-data

[^116]: https://researchguides.uoregon.edu/gis/data

[^117]: https://cran.r-project.org/package=rnassqs
