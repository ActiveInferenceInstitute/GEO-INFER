# Empirical Datasets for Agricultural Land Redevelopment Analysis

This comprehensive research provides detailed information on the **key empirical datasets** required for agricultural land redevelopment analysis and strategy development in the bioregion encompassing Superior California counties and all of Oregon. These datasets can be integrated with the **geo-infer package** for sophisticated spatial analysis and modeling.

## Executive Summary

**Agricultural land redevelopment analysis requires nine critical data components** that enable comprehensive assessment and strategic planning. While robust datasets exist for most components, **mortgage debt and power source data represent the most significant data gaps** that require specialized acquisition approaches. The integration of federal, state, commercial, and open-source datasets provides the foundation for sophisticated geo-spatial analysis through platforms like the geo-infer package.

## Primary Data Categories and Sources

### 1. **Agricultural Zoned Parcels**

#### California Sources

**California Farmland Mapping & Monitoring Program (FMMP)**[1][2]
- **Access**: https://www.conservation.ca.gov/dlrp/fmmp
- **Data Format**: ESRI Geodatabases, Shapefiles, REST APIs
- **Coverage**: All target counties (Butte, Colusa, Del Norte, Glenn, Humboldt, Lake, Lassen, Mendocino, Modoc, Nevada, Plumas, Shasta, Sierra, Siskiyou, Tehama, Trinity)
- **Update Frequency**: Biennial
- **Key Features**: Important Farmland classification with minimum 10-acre mapping units[3]

**Land IQ Statewide Crop Mapping**[4]
- **Access**: Department of Water Resources partnership data
- **Spatial Resolution**: Field-by-field classification (0.5-2.0 acre minimum)
- **Coverage**: 15.4 million acres categorized into 50+ crop types
- **Accuracy**: Exceeds 98%
- **Update Frequency**: Annual (water year basis)

**Regrid Commercial Parcel Data**[5]
- **Access**: https://regrid.com/california-parcel-data
- **Coverage**: All 58 California counties
- **Data Elements**: Parcel boundaries, ownership, land values, land use codes
- **Update Frequency**: Regular updates from county assessors
- **API Access**: Available for automated data retrieval

#### Oregon Sources

**Oregon Resource Zoning Data**[6]
- **Access**: Oregon Department of Land Conservation and Development
- **Coverage**: 15.6 million acres under resource zoning
- **Data Format**: GIS-compatible spatial datasets
- **Key Features**: Exclusive Farm Use (EFU) zone classification

**ORMAP Statewide Parcel System**[7]
- **Access**: https://www.ormap.net
- **Coverage**: All Oregon counties
- **Data Elements**: Taxlots, assessor maps, parcel boundaries
- **Format**: PDF and GIS-compatible formats

**Regrid Oregon Parcel Data**[8]
- **Access**: https://regrid.com/oregon-parcel-data
- **Coverage**: All 36 Oregon counties
- **API Access**: REST APIs for systematic data extraction
- **Update Source**: County assessors and recorders offices

### 2. **Current Agricultural Use Classification**

#### Federal Datasets

**USDA NASS Cropland Data Layer (CDL)**[9][10][11]
- **Access**: https://www.nass.usda.gov/Research_and_Science/Cropland/
- **Spatial Resolution**: 30 meters
- **Temporal Coverage**: Annual (2008-present)
- **Classification**: 50+ crop-specific categories including dairy, grazing, tree crops, grains, vegetables
- **API Access**: Available through USDA APIs

**USDA Census of Agriculture**[12][13]
- **Access**: https://www.nass.usda.gov/Publications/AgCensus/
- **Frequency**: Every 5 years (most recent: 2022)
- **Geographic Granularity**: County level with detailed crop breakdowns
- **Data Elements**: Farm operations, land use types, livestock numbers

#### California-Specific Sources

**California Important Farmland Time Series**[1]
- **Temporal Coverage**: 1984-present
- **Classification System**: Prime, Statewide Importance, Unique, Local Importance
- **Web Interface**: Interactive California Important Farmland Finder
- **API Access**: Map and Feature Services for ArcGIS integration

**Land IQ Annual Crop Mapping**[4]
- **Classification Detail**: Dairy operations, grazing patterns, tree crop age/type
- **Validation**: Ground-truthed with 98%+ accuracy
- **Integration**: Compatible with Department of Water Resources systems

#### Oregon-Specific Sources

**Oregon Farm & Forest Land Use Reports**[14][6]
- **Coverage**: EFU and forest zone land use decisions
- **Reporting Frequency**: Biennial
- **Data Elements**: Agricultural land conversion tracking, development permits
- **Access**: Oregon Department of Land Conservation and Development

### 3. **Ownership and Lease Information**

#### Ownership Analysis Datasets

**Academic Research on California Cropland Ownership**[15][16]
- **Research Source**: University of California studies by Macaulay & Butsic
- **Key Finding**: Largest 5% of properties control 50.6% of California cropland[15]
- **Data Granularity**: Property-level analysis across all 58 counties
- **Methodology**: Parcel-level ownership aggregation with crop-specific analysis

**Commercial Parcel Ownership Data**[5][8]
- **Regrid Platform**: Comprehensive ownership details
- **Update Frequency**: Regular synchronization with county records
- **Data Elements**: Current ownership, ownership history, property characteristics
- **API Integration**: Systematic bulk data access capabilities

#### Lease Information Challenges

**Data Limitation**: Lease status information is **not consistently available** in public datasets. Private arrangements between landowners and tenants are typically not recorded in public records systems. **Alternative approaches** include:
- Agricultural census surveys (5-year intervals)
- County assessor agricultural exemption records
- Farm Service Agency participation records (limited access)

### 4. **Mortgage Debt Information**

#### **Critical Data Gap Identification**

Parcel-level mortgage debt information represents the **most significant data challenge** for agricultural land analysis. Public records typically contain limited mortgage information due to privacy protections and recording practices.

#### Available Aggregate Data

**USDA Economic Research Service Farm Debt Statistics**[17][18][19][20]
- **National Level**: $503.7 billion total farm debt (2021)[20]
- **Real Estate Component**: $344.5 billion (68% of total debt)[20]
- **Regional Breakdown**: Limited county-level granularity
- **Trend Analysis**: Historical debt-to-asset ratios and lending patterns

**Federal Reserve Agricultural Finance Data**[21][22]
- **Institutional Lending**: Farm Credit System, commercial banks, life insurance companies
- **Geographic Aggregation**: State and regional levels
- **Temporal Coverage**: Quarterly updates for lending volumes

#### Recommended Acquisition Strategies

1. **County Recorder Integration**: Direct API access to deed and mortgage recording systems
2. **Agricultural Lending Institution Partnerships**: Farm Credit System regional data sharing
3. **USDA Farm Service Agency**: Loan guarantee and direct lending program data
4. **Commercial Real Estate Services**: Agricultural property transaction databases

### 5. **Agricultural Improvements and Infrastructure**

#### Valuation Methodologies

**Agricultural Property Assessment Systems**[23][24]
- **Classification Framework**: 
  - **Class A**: Buildings and structures (depreciated replacement cost method)
  - **Class B**: Land-integrated improvements (fences, irrigation, roads)
  - **Class S**: Specialized improvements (processing facilities, storage)
  - **Permanent Crops**: Orchards and vineyards with age/condition factors

#### Infrastructure Data Sources

**USDA National Agricultural Statistics Service**[25][26][27]
- **Irrigation and Water Management Survey**: 5-year comprehensive infrastructure assessment
- **Equipment and Facility Inventory**: County-level aggregated data
- **Access**: Quick Stats database with customizable queries

**California Department of Water Resources Land and Water Use Estimates**[28]
- **Infrastructure Elements**: Irrigation systems, crop evapotranspiration equipment
- **Spatial Resolution**: Agricultural Water Management Planning areas
- **Update Frequency**: Annual estimates with 5-year comprehensive updates

**Farm Infrastructure Research Datasets**[29][30]
- **Academic Sources**: Infrastructure density and productivity correlation studies
- **Application**: Valuation models for infrastructure impact assessment
- **Methodology**: Regression analysis for infrastructure value contribution

### 6. **Surface Water Rights and Access**

#### California Water Rights Systems

**Electronic Water Rights Information Management System (eWRIMS)**[31][32][33]
- **Access**: https://www.waterboards.ca.gov/resources/data_databases/surface_water.html
- **Data Elements**: 
  - Water right permits, licenses, certificates
  - Points of diversion coordinates
  - Authorized water quantities
  - Water use reporting (monthly and annual)
- **Irrigation-Specific Data**: California Water Rights Irrigation Use Annual Reports[31]
- **API Access**: Downloadable CSV and spatial data formats

**CalWATRS Modernization (UPWARD Project)**[34]
- **Implementation Timeline**: 2021-ongoing
- **Enhanced Features**: Streamlined reporting, step-by-step user guidance
- **GIS Integration**: Improved spatial information access
- **Data Quality**: Modernized collection and validation systems

#### Oregon Water Rights

**Oregon Water Rights Database**[35][36]
- **Harmonized Database of Western U.S. Water Rights (HarDWR)**[35][36]
- **Coverage**: Comprehensive Oregon water rights allocation
- **Data Elements**: Priority dates, flow allocations, use categories, spatial units
- **Academic Access**: Published research datasets with water management area boundaries
- **Integration Capability**: Compatible with hydrologic modeling systems

#### Regional Water Data Integration

**National Groundwater Monitoring Network**[37]
- **Access**: USGS Office of Water Information
- **Coverage**: Federal, state, and local monitoring networks
- **Data Portal**: Interactive mapping with historical and current data
- **Variables**: Water levels, quality, lithology, well construction

### 7. **Groundwater Resources**

#### Federal Monitoring Systems

**USGS National Groundwater Monitoring Network (NGWMN)**[37]
- **Access**: https://www.drought.gov/data-maps-tools/national-groundwater-monitoring-network
- **Data Portal**: Multi-database integration with interactive mapping
- **Coverage**: Principal and Major Aquifers of the United States
- **Data Elements**: Water levels, quality, lithology, well construction

**USDA Irrigation and Water Management Surveys**[26][27]
- **Groundwater Usage Statistics**: 54% of irrigation water from on-farm wells[26]
- **Well Depth Information**: Average 241 feet (2023 data)[26]
- **Geographic Coverage**: State and county-level aggregation
- **Update Frequency**: Every 5 years with annual estimates

#### California Groundwater Data

**California Department of Water Resources Groundwater Data**[38]
- **SGMA Data Viewer**: Groundwater Sustainability Plan requirements
- **Access**: https://water.ca.gov/programs/groundwater-management/data-and-tools
- **Integration**: Department of Water Resources periodic groundwater level datasets[39]
- **Spatial Coverage**: Groundwater basin and sub-basin levels

#### Advanced Groundwater Mapping

**Satellite-Based Groundwater Abstraction Mapping**[40]
- **Research Source**: King Abdullah University of Science and Technology
- **Methodology**: Two-source energy balance model with satellite data
- **Applications**: Regional-scale groundwater abstraction quantification
- **Technical Approach**: Machine learning integration with satellite imagery

### 8. **Power Source and Energy Data**

#### **Significant Data Gap in Agricultural Energy Sources**

Agricultural power source data at the parcel level represents another **critical information challenge**. Existing datasets provide primarily aggregate information rather than farm-specific power source details.

#### Available Energy Data

**USDA Economic Research Service Agricultural Energy Statistics**[41][42][43]
- **Energy Use Categories**: Electricity, diesel, gasoline, propane, natural gas
- **Cost Analysis**: Energy expenses by farm size and commodity type[42]
- **Historical Trends**: 2001-2011 direct energy use patterns[43]
- **Data Format**: Chapter 5 tabulated datasets from Agricultural Greenhouse Gas Inventory[41]

**University Extension Energy Assessment Tools**[44][45][46]
- **Farm Energy Auditing**: Maryland, Penn State, and cooperative extension programs
- **Calculation Methodologies**: kWh usage estimation by equipment type[46]
- **Energy Efficiency Guidelines**: Equipment-specific energy consumption rates[45]

#### Renewable Energy in Agriculture

**Renewable Energy Program Databases**[47][48][49]
- **California Renewable Energy for Agriculture Program (REAP)**[49]
- **Academic Research**: Solar, wind, and biofuel adoption patterns[47]
- **Policy Support**: AgroRES project findings on renewable energy uptake barriers[48]

#### Recommended Data Acquisition Strategies

1. **Utility Company Partnerships**: Agricultural rate schedule customer analysis
2. **Solar Installation Databases**: County permitting and interconnection records
3. **USDA Rural Energy Programs**: Renewable energy grant and loan recipient data
4. **Agricultural Equipment Surveys**: Farm machinery and infrastructure inventories

### 9. **Coastal Commission and Regulatory Indicators**

#### California Coastal Commission Data

**Coastal Agriculture Regulatory Framework**[50][51][52]
- **Access**: https://www.coastal.ca.gov/agriculture/
- **Regulatory Documents**: Five informational guides for agricultural development permitting
- **Local Coastal Programs (LCPs)**: County and city agricultural land use policies
- **Permit Requirements**: Coastal Development Permit (CDP) specifications

**Public Data Portal**[53][54]
- **Access**: https://www.coastal.ca.gov/PDP/
- **Data Elements**: Coastal Data Management System information
- **API Integration**: REST APIs for systematic data access
- **Coverage**: Local coastal program data, permit tracking, enforcement actions

#### Agricultural Zoning Indicators

**Prime Agricultural Land Protection Status**[50][51]
- **Regulatory Framework**: Coastal Act Sections 30241 and 30242 requirements
- **Protection Levels**: Prime agricultural land maintenance mandates
- **Conversion Restrictions**: Agricultural to non-agricultural use limitations
- **Local Implementation**: County-specific agricultural protection measures

#### Regional Agricultural Zoning Examples

**Sonoma County Coastal Zone Agriculture**[52]
- **Permitted Uses**: Grazing, row crops, vineyards, orchards
- **Permit Requirements**: Coastal permits for specific agricultural activities
- **Non-Agricultural Restrictions**: Tasting rooms and visitor-serving use limitations
- **Implementation Model**: Template for regional agricultural zoning analysis

## Technical Integration Specifications

### API Access and Automation

**High-Priority API Integrations**:
1. **USDA NASS Quick Stats API**: Crop data layer and agricultural statistics
2. **California eWRIMS API**: Water rights and irrigation data
3. **Regrid Parcel APIs**: Ownership and property characteristics
4. **Oregon ORMAP API**: Parcel boundaries and assessor data

### Data Processing Requirements

**Spatial Data Standards**:
- **Coordinate Systems**: NAD83, WGS84 for cross-platform compatibility
- **File Formats**: Shapefile, GeoJSON, GeoTIFF for geo-infer integration
- **Attribute Standardization**: Consistent field naming and data types

**Temporal Data Management**:
- **Update Frequency Tracking**: Automated monitoring of source data updates
- **Version Control**: Systematic archiving of historical datasets
- **Change Detection**: Temporal analysis capabilities for land use transitions

### Data Quality and Validation

**Accuracy Assessment Protocols**:
- **Ground-Truthing**: Field validation for critical data elements
- **Cross-Reference Validation**: Multi-source data consistency checking
- **Statistical Quality Control**: Outlier detection and data integrity assessment

**Metadata Documentation**:
- **Data Lineage**: Complete source documentation and processing history
- **Update Tracking**: Systematic recording of data refresh cycles
- **Quality Metrics**: Accuracy, completeness, and currency measurements

## Implementation Recommendations

### Phased Data Acquisition Strategy

**Phase 1 (Immediate Implementation)**:
- Agricultural zoned parcels (FMMP, ORMAP, Regrid)
- Current use classification (CDL, Land IQ)
- Surface water rights (eWRIMS, HarDWR)
- Basic ownership data (parcel records)

**Phase 2 (3-6 Month Timeline)**:
- Groundwater resources (NGWMN, state databases)
- Agricultural improvements (assessment records, surveys)
- Enhanced ownership analysis (academic datasets)

**Phase 3 (6-12 Month Timeline)**:
- Mortgage debt information (institutional partnerships)
- Power source data (utility partnerships, renewable energy databases)
- Comprehensive regulatory indicator integration

### Partnership Development

**Critical Institutional Relationships**:
- **Agricultural Lending Institutions**: Farm Credit System, commercial agricultural lenders
- **Utility Companies**: Electric utilities serving rural areas, renewable energy installers
- **Academic Research Centers**: University agricultural economics and land use programs
- **Government Agencies**: County assessors, state agricultural departments

### Quality Assurance Framework

**Data Validation Protocols**:
- **Multi-Source Cross-Reference**: Validation across independent datasets
- **Temporal Consistency Checking**: Historical trend analysis for anomaly detection
- **Geographic Boundary Verification**: Spatial data integrity assessment
- **Statistical Outlier Analysis**: Automated detection of irregular data patterns

This comprehensive dataset framework provides the empirical foundation for sophisticated agricultural land redevelopment analysis and strategic planning through integration with the geo-infer package and advanced spatial analytics platforms.

[1] https://www.conservation.ca.gov/dlrp/fmmp
[2] https://www.conservation.ca.gov/dlrp/fmmp/Documents/fmmp/pubs/2016-2018/FCR/FCR_1618_Report.pdf
[3] https://maps.conservation.ca.gov/agriculture/
[4] https://www.landiq.com/land-use-mapping
[5] https://regrid.com/california-parcel-data
[6] https://www.oregon.gov/lcd/FF/Documents/Farm_Forest_Report_2022_2023.pdf
[7] https://www.ormap.net
[8] https://regrid.com/oregon-parcel-data
[9] https://www.nass.usda.gov/Research_and_Science/Cropland/metadata/metadata_ca21.htm
[10] https://data.nass.usda.gov/Research_and_Science/Cropland/metadata/metadata_or22.htm
[11] https://water.usgs.gov/catalog/datasets/ef517a23-cfe4-4af1-846c-017d20f0832e/
[12] https://www.nass.usda.gov/Publications/AgCensus/2022/Full_Report/Volume_1,_Chapter_2_County_Level/California/
[13] https://farmland.org/blog/2022-census-of-agriculture-california
[14] https://www.oregonlegislature.gov/committees/2019I1-HAGLU/Reports/2018-2019%20DLCD%20Farm%20Forest%20Report.pdf
[15] https://californiaagriculture.org/api/v1/articles/108763-ownership-characteristics-and-crop-selection-in-california-cropland.pdf
[16] https://escholarship.org/content/qt25s7k7s7/qt25s7k7s7.pdf
[17] http://www.ers.usda.gov/data-products/charts-of-note/chart-detail?chartId=106426
[18] https://www.statista.com/statistics/274649/mortgage-debt-outstanding-on-us-farm-property/
[19] https://sgp.fas.org/crs/misc/R46768.pdf
[20] https://www.ers.usda.gov/publications/pub-details?pubid=109411&v=7019
[21] https://fred.stlouisfed.org/series/MDOTHFRAFAMCTPFP
[22] https://fred.stlouisfed.org/tags/series?t=agriculture%3Bdebt%3Busa
[23] https://www.co.cheyenne.co.us/assets/pdfs/agricultural_valuation_guide_2024.pdf
[24] https://www.in.gov/dlgf/files/bk1ch2-4.pdf
[25] https://www.nass.usda.gov/datasets
[26] https://www.nass.usda.gov/Newsroom/2024/10-31-2024.php
[27] https://cropwatch.unl.edu/2024/2023-irrigation-and-water-management-data-now-available/
[28] https://water.ca.gov/Programs/Water-Use-And-Efficiency/Land-And-Water-Use/Agricultural-Land-And-Water-Use-Estimates
[29] https://data.mendeley.com/datasets/2fs98x4mky/1
[30] https://aaronhall.com/agricultural-farm-valuation-7-factors-that-determine-your-selling-price/
[31] https://catalog.data.gov/dataset/california-water-rights-irrigation-use-annual-reports-02298/resource/238269e8-e5b3-4988-bbdd-b83948342cc0
[32] https://data.ca.gov/eu/dataset/california-water-rights-water-use-reported/resource/621c31ae-7ea0-4915-b7dc-dfcb7efc77b9
[33] https://www.waterboards.ca.gov/resources/data_databases/surface_water.html
[34] https://www.waterboards.ca.gov/upward/
[35] https://pmc.ncbi.nlm.nih.gov/articles/PMC11156903/
[36] https://www.osti.gov/dataexplorer/biblio/dataset/2475303
[37] https://www.drought.gov/data-maps-tools/national-groundwater-monitoring-network
[38] https://water.ca.gov/programs/groundwater-management/data-and-tools
[39] https://catalog.data.gov/dataset/?res_format=CSV&tags=groundwater&_tags_limit=0&page=1
[40] https://hess.copernicus.org/articles/24/5251/2020/hess-24-5251-2020.pdf
[41] https://agdatacommons.nal.usda.gov/articles/dataset/Data_from_Chapter_5_Energy_Use_in_Agriculture_U_S_Agriculture_and_Forestry_Greenhouse_Gas_Inventory_1990-2018/24667737
[42] https://www.ers.usda.gov/data-products/charts-of-note/chart-detail?chartId=80047
[43] http://www.ers.usda.gov/data-products/charts-of-note/chart-detail?chartId=76766
[44] https://extension.umd.edu/resource/understanding-farm-energy-fs-1138
[45] https://extension.umd.edu/ensp.umd.edu/resource/understanding-farm-energy-fs-1138
[46] https://fmec.coop/farm-energy-estimator
[47] https://extension.psu.edu/harnessing-renewable-energy-a-sustainable-future-for-farming
[48] https://www.interregeurope.eu/find-policy-solutions/stories/renewable-energy-sustainable-agriculture
[49] https://www.energy.ca.gov/programs-and-topics/programs/renewable-energy-agriculture-program
[50] https://www.coastal.ca.gov/agriculture/
[51] https://documents.coastal.ca.gov/assets/agriculture/Informational%20Guide%20for%20Agricultural%20Development%209.29.2017.pdf
[52] https://content.govdelivery.com/attachments/CASONOMA/2019/11/15/file_attachments/1325867/LCP%20Fact%20Sheet%20Agriculture.pdf
[53] https://www.coastal.ca.gov/PDP/
[54] https://www.coastal.ca.gov/open-data/
[55] https://nationalaglawcenter.org/californias-attempt-to-restrict-foreign-agricultural-land-investments/
[56] https://catalog.data.gov/dataset/crop-index-model-9beba
[57] https://www.cdfa.ca.gov/agvision/docs/agricultural_loss_and_conservation.pdf
[58] https://ucanr.edu/statewide-program/informatics-and-gis-program/finding-and-using-parcel-data-california
[59] https://www.youtube.com/watch?v=PAWGbbUBlKQ
[60] https://www.ppic.org/publication/agricultural-land-use-in-california/
[61] https://data.ca.gov/dataset/california-important-farmland-2020
[62] https://farmlandinfo.org/wp-content/uploads/sites/2/2025/05/advancing-equitable-agricultural-land-tenure.pdf
[63] https://www.boe.ca.gov/proptaxes/agricultural_lands.htm
[64] https://extension.oregonstate.edu/business-economics/rural-development/oregon-agriculture-numbers-part-1-total-farms-farmland-acres
[65] https://www.oregon.gov/eis/geo/OGIC%20Approved%20Stewardship%20Plans/StatewideLandUseStewardshipPlan_v0_3_2021.pdf
[66] https://dryfarming.org/map/
[67] https://www.fbn.com/acre-vision/plat-map/OR
[68] https://www.nass.usda.gov/Statistics_by_State/Oregon/index.php
[69] https://www.oregon.gov/deq/wq/programs/pages/dwp-maps.aspx
[70] https://tools.oregonexplorer.info/geocortex/essentials/oe/rest/sites/renewable_energy/map/mapservices/85
[71] https://app.regrid.com/us/or
[72] https://geohub.oregon.gov/search?categories=land+use+land+cover
[73] https://oregonaitc.org/resources/oregon-resources/oregon-map/
[74] https://ir.library.oregonstate.edu/concern/datasets/jd473392m
[75] https://www.oregon.gov/dsl/lands/pages/maps-inventory.aspx
[76] https://www.oregon.gov/ODA/Documents/Publications/Administration/AgStatsDirectory.pdf
[77] https://landmapper.ecotrust.org/landmapper
[78] https://catalog.data.gov/dataset/?q=geo.data&metadata_type=geospatial&res_format=HTML&_bureauCode_limit=0&_res_format_limit=0&organization_type=State+Government
[79] https://swoopfunding.com/us/sectors/agricultural-mortgage/
[80] https://www.kansascityfed.org/research/economic-bulletin/interest-expenses-on-farmland-debt-could-challenge-farm-profitability/
[81] https://www.finder.com/uk/mortgages/commercial-mortgage-rates/agricultural-mortgage
[82] https://m.farms.com/ag-industry-news/navigating-farm-mortgages-023.aspx
[83] https://www.ers.usda.gov/data-products/charts-of-note/chart-detail?chartId=109431
[84] https://swoopfunding.com/au/sectors/agricultural-mortgage/
[85] https://www.agriculture.gov.au/abares/research-topics/surveys/farm-debt
[86] https://www.nobroker.in/blog/loan-against-agricultural-land/
[87] http://www.ers.usda.gov/topics/farm-economy/farm-sector-income-finances/assets-debt-and-wealth
[88] https://www.ers.usda.gov/data-products/charts-of-note/chart-detail?chartId=106426
[89] https://agamerica.com/land-loans/
[90] https://fred.stlouisfed.org/tags/series?t=agriculture%3Bloans
[91] https://www.kansascityfed.org/agriculture/agfinance-updates/farm-real-estate-debt-builds/
[92] https://www.bankrate.com/uk/mortgages/mortgages-for-land/
[93] http://www.ers.usda.gov/data-products/major-land-uses
[94] https://pure.iiasa.ac.at/id/eprint/18253/1/essd-14-4397-2022.pdf
[95] https://saiv.org.za/buying-a-farm-a-valuers-perspective-improvements/
[96] http://www.ers.usda.gov/amber-waves/2024/september/global-changes-in-agricultural-production-productivity-and-resource-use-over-six-decades
[97] https://farmlandinfo.org/data-and-statistics/
[98] https://github.com/ricber/digital-agriculture-datasets
[99] https://www.rliland.com/Voices/The-Voices-of-Land-blog/ArticleID/337/How-to-Improve-the-Value-of-Your-Farm-Part-Two
[100] https://dagshub.com/datasets/agriculturevision/
[101] https://www.fao.org/statistics/highlights-archive/highlights-detail/land-statistics-and-indicators-(2000-2020).-global--regional-and-country-trends/en
[102] https://www.cisa.gov/resources-tools/resources/mapping-your-infrastructure-datasets-infrastructure-identification
[103] https://www.gunnisoncounty.org/695/Valuation-of-Agricultural-Property
[104] https://cropwatch.unl.edu/2024/usda-gather-farm-conservation-data-improve-programs-and-services/
[105] https://catalog.data.gov/dataset/?tags=agriculture-and-farming&_tags_limit=0
[106] https://www.bgs.ac.uk/groundwater/flooding/datasets/
[107] https://www.fao.org/aquastat/en/databases/maindatabase/
[108] https://www.nature.com/articles/s41597-024-04185-0
[109] https://www.ppic.org/publication/water-use-in-californias-agriculture/
[110] https://www.agriculture.gov.au/abares/research-topics/water/trends-in-water-entitlement-holdings-and-trade
[111] https://agridata.ec.europa.eu/Qlik_Downloads/Water-Quality-sources.htm
[112] https://catalog.data.gov/dataset/?q=consumer&_tags_limit=0&tags=groundwater
[113] https://www.earthdata.nasa.gov/topics/human-dimensions/agriculture-production
[114] http://www.ers.usda.gov/data-products
[115] https://www.edengreen.com/blog-collection/renewable-energy-vertical-farming
[116] https://catalog.data.gov/dataset/?res_format=CSV&organization_type=Federal+Government&organization=usda-gov&publisher=Agricultural+Research+Service
[117] https://www.fas.scot/downloads/practical-guide-monitoring-energy-use/
[118] https://www.weforum.org/stories/2023/10/agriculture-farmers-renewable-energy/
[119] https://www.innovatiana.com/en/post/ai-datasets-for-agriculture
[120] https://www.irena.org/-/media/Files/IRENA/Agency/Publication/2021/Nov/IRENA_FAO_Renewables_Agrifood_2021.pdf
[121] https://www.earthdata.nasa.gov/topics/human-dimensions/agriculture-production/data-access-tools
[122] https://datarade.ai/data-categories/agricultural-data
[123] https://www.eia.gov/electricity/data/browser/
[124] https://www.fao.org/geospatial/resources/tools/agro-maps/en/
[125] https://www.usda.gov/about-usda/news/blog/open-agricultural-data-your-fingertips
[126] https://www.coastal.ca.gov
[127] https://www.fao.org/geospatial/resources/detail/en/c/1629356/
[128] https://www.eea.europa.eu/en/datahub/datahubitem-view/a0aacdd2-46b2-485a-ac49-162936d84395
[129] https://www.foodchainid.com/agriculture/
[130] https://essd.copernicus.org/articles/13/5951/2021/
[131] https://www.ars.usda.gov/research/datasets/
[132] https://www.fao.org/gaez/en
[133] https://agridata.ec.europa.eu/extensions/DataPortal/home.html
[134] https://www.farmers.gov/data
[135] https://www.nrcs.usda.gov/sites/default/files/2023-07/CZSS-FY23-Annual-Report.pdf