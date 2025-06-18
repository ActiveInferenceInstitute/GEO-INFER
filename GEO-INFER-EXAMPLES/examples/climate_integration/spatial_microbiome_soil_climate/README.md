# Spatial Microbiome-Climate-Soil Integration 🧬🌍

**Multi-Scale Biological Data Fusion Using H3 Spatial Indexing**

## Learning Objectives 🎯

After completing this example, you will:
- Understand how to integrate multiple biological datasets spatially
- See the power of H3 hexagonal indexing for multi-scale biological analysis
- Learn to combine microbiome, climate, and soil data in a unified spatial framework
- Experience real-world biological data integration workflows
- Master the use of GEO-INFER-BIO and GEO-INFER-SPACE for spatial fusion

## Modules Used 🔧

### Primary Modules
- **GEO-INFER-BIO**: Biological data processing, microbiome analysis, soil data integration
- **GEO-INFER-SPACE**: H3 spatial indexing, multi-overlay visualization, OSC integration
- **GEO-INFER-DATA**: Data ingestion and validation

### Supporting Modules
- **GEO-INFER-TIME**: Temporal alignment of multi-year datasets
- **GEO-INFER-API**: Standardized access to biological and spatial services

### Integration Points
- **BIO → SPACE**: Biological data converted to H3 spatial cells
- **SPACE → BIO**: Environmental context enrichment for biological analysis
- **DATA ↔ BIO**: Real dataset ingestion and validation
- **TIME ↔ ALL**: Multi-temporal data alignment across all data types

## Real Datasets Used 📊

### 1. **Microbiome Data Sources**
- **Earth Microbiome Project (EMP)**: Global microbiome samples with GPS coordinates
  - Data: 16S rRNA sequences, taxonomic classifications, sample metadata
  - Coverage: 6 continents, 20+ biomes, 27,000+ samples
  - URL: `https://earthmicrobiome.org/`
  
- **American Gut Project**: North American human and environmental microbiomes
  - Data: Bacterial diversity, functional predictions, host metadata
  - Coverage: USA primarily, with some international samples
  - URL: `http://americangut.org/`

### 2. **Climate Data Sources**
- **WorldClim**: Global climate data at 1km resolution
  - Variables: Temperature, precipitation, seasonality indices
  - Temporal: Long-term averages and future projections
  - URL: `https://worldclim.org/`
  
- **NOAA Climate Data Online**: Weather station measurements
  - Variables: Daily temperature, precipitation, humidity
  - Coverage: Global, 1880-present
  - URL: `https://www.ncdc.noaa.gov/cdo-web/`

### 3. **Soil Data Sources**  
- **ISRIC SoilGrids**: Global soil property maps at 250m resolution
  - Variables: pH, organic carbon, texture, bulk density
  - Depth: 6 standard depth intervals (0-200cm)
  - URL: `https://soilgrids.org/`
  
- **USDA Soil Survey**: High-resolution US soil data
  - Variables: Detailed soil classifications, properties, constraints
  - Coverage: Continental United States
  - URL: `https://websoilsurvey.sc.egov.usda.gov/`

## Prerequisites ✅

### Required Modules
```bash
# Core GEO-INFER modules
pip install -e ../../../GEO-INFER-BIO
pip install -e ../../../GEO-INFER-SPACE  
pip install -e ../../../GEO-INFER-DATA
pip install -e ../../../GEO-INFER-TIME
pip install -e ../../../GEO-INFER-API

# Additional dependencies for biological data
pip install -e .[microbiome,climate,soil]  # Install with optional bio dependencies
```

### System Requirements
- Python 3.9+
- 8GB RAM minimum (16GB recommended for full datasets)
- 20GB disk space for cached data
- Internet connection for dataset downloads

### Data Requirements
- Automatic download of sample datasets (first run may take 30+ minutes)
- Full datasets require registration with some providers
- Sample data included for immediate testing

## Quick Start ⚡

### 3-Step Execution
```bash
# 1. Navigate to example directory
cd GEO-INFER-EXAMPLES/examples/climate_integration/spatial_microbiome_soil_climate

# 2. Download and prepare sample data (first time only)
python scripts/prepare_sample_data.py --region="north_america" --samples=1000

# 3. Run the spatial integration analysis
python scripts/run_spatial_integration.py --h3_resolution=7 --output_format="interactive"
```

### Expected Runtime
- **Data Preparation**: ~15 minutes (first run)
- **Spatial Integration**: ~10 minutes
- **Visualization Generation**: ~5 minutes

### Key Outputs to Observe
- `spatial_microbiome_overlay.html`: Interactive H3 hexagonal map
- `integrated_biological_data.geojson`: Spatially-indexed biological data
- `correlation_analysis.json`: Statistical relationships between datasets
- `multi_scale_analysis/`: H3 analyses at different resolutions

## Detailed Walkthrough 📚

### Step 1: Biological Data Ingestion (GEO-INFER-BIO)

```python
from geo_infer_bio.microbiome import MicrobiomeDataLoader
from geo_infer_bio.climate import ClimateDataProcessor  
from geo_infer_bio.soil import SoilDataIntegrator

# Initialize biological data processors
microbiome_loader = MicrobiomeDataLoader()
climate_processor = ClimateDataProcessor()
soil_integrator = SoilDataIntegrator()

# Load Earth Microbiome Project samples for North America
emp_samples = microbiome_loader.load_emp_data(
    region_bbox=(-130, 25, -65, 55),  # North America bounding box
    sample_types=["soil", "sediment", "water"],
    max_samples=1000
)
print(f"Loaded {len(emp_samples)} EMP samples with coordinates")

# Load corresponding climate data
climate_data = climate_processor.load_worldclim_data(
    variables=["bio1", "bio12", "bio15"],  # Temperature, precipitation, seasonality
    coordinates=emp_samples.get_coordinates(),
    buffer_km=5  # 5km buffer around sample points
)

# Load soil properties
soil_data = soil_integrator.load_soilgrids_data(
    coordinates=emp_samples.get_coordinates(),
    properties=["phh2o", "soc", "clay", "sand"],
    depths=["0-5cm", "5-15cm"]
)
```

**Module Integration**: BIO module handles specialized biological data formats and validates spatial coordinates.

### Step 2: Spatial Indexing (GEO-INFER-SPACE)

```python
from geo_infer_space.h3_spatial import H3SpatialProcessor
from geo_infer_space.osc_geo import OSCGeoIntegrator

# Initialize H3 spatial processor
h3_processor = H3SpatialProcessor(resolution=7)  # ~5km resolution

# Convert microbiome samples to H3 cells
microbiome_h3 = h3_processor.points_to_h3_cells(
    points=emp_samples.get_coordinates(),
    data=emp_samples.get_diversity_metrics(),
    aggregation_method="mean"
)
print(f"Aggregated to {len(microbiome_h3)} H3 cells")

# Spatially join climate data to H3 cells
climate_h3 = h3_processor.raster_to_h3_cells(
    raster_data=climate_data,
    aggregation_method="mean"
)

# Spatially join soil data to H3 cells  
soil_h3 = h3_processor.raster_to_h3_cells(
    raster_data=soil_data,
    aggregation_method="mean"
)
```

**Module Integration**: SPACE module provides H3 spatial indexing that creates common spatial framework for all biological datasets.

### Step 3: Multi-Dataset Fusion

```python
from geo_infer_space.fusion import SpatialDataFusion

# Initialize spatial fusion engine
fusion_engine = SpatialDataFusion(h3_resolution=7)

# Combine all datasets in H3 spatial framework
integrated_data = fusion_engine.fuse_datasets({
    "microbiome": microbiome_h3,
    "climate": climate_h3, 
    "soil": soil_h3
}, 
spatial_join_method="h3_cell_id",
handle_missing="interpolate"
)

print(f"Integrated data covers {len(integrated_data)} H3 cells")
print(f"Variables per cell: {integrated_data.get_variable_count()}")
```

**Module Integration**: SPACE fusion capabilities combine heterogeneous biological datasets into unified spatial structure.

### Step 4: Multi-Scale Analysis

```python
# Analyze patterns at multiple H3 resolutions
resolutions = [5, 6, 7, 8]  # Continental to local scales
multi_scale_analysis = {}

for res in resolutions:
    # Re-aggregate data to different resolution
    resampled_data = h3_processor.change_resolution(
        integrated_data, 
        target_resolution=res
    )
    
    # Calculate spatial statistics
    spatial_stats = fusion_engine.calculate_spatial_statistics(
        resampled_data,
        methods=["morans_i", "spatial_correlation", "hotspots"]
    )
    
    multi_scale_analysis[f"h3_res_{res}"] = {
        "data": resampled_data,
        "statistics": spatial_stats,
        "cell_count": len(resampled_data)
    }

print("Multi-scale analysis complete")
```

### Step 5: Interactive Visualization

```python
from geo_infer_space.visualization import H3InteractiveMapper

# Create multi-overlay interactive map
mapper = H3InteractiveMapper()

# Add microbiome diversity overlay
mapper.add_h3_overlay(
    data=integrated_data,
    variable="shannon_diversity",
    overlay_name="Microbiome Diversity",
    color_scheme="viridis",
    opacity=0.7
)

# Add climate overlay
mapper.add_h3_overlay(
    data=integrated_data,
    variable="bio1_temperature",
    overlay_name="Mean Annual Temperature",
    color_scheme="RdYlBu_r",
    opacity=0.6
)

# Add soil pH overlay
mapper.add_h3_overlay(
    data=integrated_data,
    variable="soil_ph",
    overlay_name="Soil pH",
    color_scheme="RdBu",
    opacity=0.6
)

# Generate interactive map with layer controls
interactive_map = mapper.create_interactive_map(
    center_lat=40.0, center_lon=-95.0,  # Center on North America
    zoom_level=4,
    enable_layer_control=True,
    enable_measurement_tools=True
)

# Save map
interactive_map.save("spatial_microbiome_overlay.html")
```

**Module Integration**: SPACE visualization creates interactive maps combining all biological datasets with user-controlled overlays.

## Key Integration Patterns 🔄

### 1. **Biological Data Standardization Pattern**
```
Raw Bio Data → [BIO normalization] → [Spatial coordinates] → [H3 indexing] → Spatially-indexed Bio Data
```

### 2. **Multi-Scale Spatial Fusion Pattern**
```
[Microbiome + Climate + Soil] → [H3 aggregation] → [Multiple resolutions] → Multi-scale integrated dataset
```

### 3. **Real-time Interactive Pattern**
```
Integrated H3 Data → [Layer management] → [Interactive controls] → [Web visualization] → User exploration
```

## Advanced Features 🚀

### Statistical Correlation Analysis
```python
from geo_infer_bio.statistics import SpatialBioStatistics

bio_stats = SpatialBioStatistics()

# Calculate correlations between microbiome diversity and environmental factors
correlations = bio_stats.calculate_spatial_correlations(
    integrated_data,
    dependent_vars=["shannon_diversity", "observed_species"],
    independent_vars=["bio1_temperature", "bio12_precipitation", "soil_ph"],
    spatial_weights="h3_neighbors"
)

# Identify environmental drivers of microbiome patterns
drivers = bio_stats.identify_environmental_drivers(
    correlations,
    significance_threshold=0.05,
    spatial_autocorr_correction=True
)
```

### Ecological Niche Modeling
```python
from geo_infer_bio.ecology import NicheModeling

niche_modeler = NicheModeling()

# Model habitat suitability for specific microbial taxa
habitat_models = niche_modeler.model_microbial_niches(
    microbiome_data=emp_samples,
    environmental_data=integrated_data,
    target_taxa=["Acidobacteria", "Proteobacteria", "Actinobacteria"],
    modeling_algorithm="maxent"
)

# Project habitat suitability to H3 cells
habitat_h3 = h3_processor.project_model_predictions(
    models=habitat_models,
    target_resolution=7,
    prediction_type="habitat_suitability"
)
```

## Real Data Integration Details 📋

### Earth Microbiome Project Integration
```python
# Automatic EMP data download and processing
emp_config = {
    "data_url": "ftp://ftp.microbio.me/emp/release1/",
    "metadata_file": "emp_qiime_mapping_qc_filtered.tsv",
    "feature_table": "emp_deblur_90bp.subset_2k.rare_5000.biom",
    "taxonomy_file": "emp_deblur_90bp.subset_2k.rare_5000.tax.txt",
    "spatial_columns": ["latitude", "longitude"],
    "required_columns": ["empo_1", "empo_2", "empo_3"]  # Environmental types
}

emp_samples = microbiome_loader.load_emp_data(emp_config)
```

### Climate Data Integration
```python
# WorldClim bioclimatic variables
climate_config = {
    "variables": {
        "bio1": "Annual Mean Temperature",
        "bio2": "Mean Diurnal Range", 
        "bio12": "Annual Precipitation",
        "bio15": "Precipitation Seasonality"
    },
    "resolution": "30s",  # ~1km at equator
    "version": "2.1",
    "format": "GeoTIFF"
}

climate_data = climate_processor.load_worldclim_data(climate_config)
```

### Soil Data Integration
```python
# ISRIC SoilGrids properties
soil_config = {
    "properties": {
        "phh2o": "pH in H2O",
        "soc": "Soil Organic Carbon", 
        "clay": "Clay content",
        "sand": "Sand content",
        "bdod": "Bulk density"
    },
    "depths": ["0-5cm", "5-15cm", "15-30cm"],
    "resolution": "250m",
    "version": "2.0"
}

soil_data = soil_integrator.load_soilgrids_data(soil_config)
```

## Performance Metrics 📊

### Expected Performance by Dataset Size
| Dataset Size | H3 Resolution | Processing Time | Memory Usage | Output Size |
|--------------|---------------|-----------------|--------------|-------------|
| 1K samples   | 7 (~5km)      | ~5 minutes      | ~2GB         | ~50MB       |
| 5K samples   | 7 (~5km)      | ~15 minutes     | ~4GB         | ~200MB      |
| 25K samples  | 6 (~20km)     | ~45 minutes     | ~8GB         | ~500MB      |

### Scalability Considerations
```python
# For large datasets, use streaming processing
from geo_infer_bio.streaming import StreamingMicrobiomeProcessor

stream_processor = StreamingMicrobiomeProcessor(
    chunk_size=1000,
    parallel_workers=4,
    memory_limit_gb=8
)

# Process in chunks to handle memory constraints
for chunk in stream_processor.process_emp_data_chunks(emp_config):
    chunk_h3 = h3_processor.points_to_h3_cells(chunk)
    # Merge chunks progressively
```

## Extensions & Variations 🌱

### Add Phylogenetic Analysis
```python
# Extend with phylogenetic community structure
from geo_infer_bio.phylogenetics import PhylogeneticDiversity

phylo_analyzer = PhylogeneticDiversity()
phylo_metrics = phylo_analyzer.calculate_spatial_phylodiversity(
    integrated_data,
    tree_file="emp_reference_tree.nwk"
)
```

### Include Functional Predictions
```python
# Add predicted functional profiles
from geo_infer_bio.functional import FunctionalPrediction

func_predictor = FunctionalPrediction()
functional_profiles = func_predictor.predict_kegg_pathways(
    microbiome_data=emp_samples,
    method="PICRUSt2"
)
```

### Multi-Temporal Analysis
```python
# Extend with time-series analysis
from geo_infer_time import TemporalBioAnalyzer

temporal_analyzer = TemporalBioAnalyzer()
temporal_trends = temporal_analyzer.analyze_microbiome_trends(
    multi_year_data=microbiome_time_series,
    climate_data=climate_time_series,
    trend_methods=["mann_kendall", "theil_sen"]
)
```

## Troubleshooting 🛠️

### Common Data Issues

**Large File Downloads**
```python
# Configure download resume and progress tracking
from geo_infer_bio.download import ResumeableDownloader

downloader = ResumeableDownloader(
    chunk_size_mb=10,
    max_retries=3,
    progress_bar=True
)
```

**Memory Issues with Large Datasets**
```python
# Use data chunking for memory management
from geo_infer_data import ChunkedDataProcessor

chunked_processor = ChunkedDataProcessor(
    max_memory_gb=4,
    chunk_overlap=0.1  # 10% overlap between chunks
)
```

**Missing Spatial Coordinates**
```python
# Handle samples with missing coordinates
from geo_infer_bio.spatial import CoordinateImputation

coord_imputer = CoordinateImputation()
completed_coords = coord_imputer.impute_missing_coordinates(
    samples_with_missing_coords,
    method="environmental_similarity"
)
```

## Validation & Quality Control ✅

### Data Quality Checks
```python
# Built-in quality control
from geo_infer_bio.quality import BiologicalDataValidator

validator = BiologicalDataValidator()

# Validate microbiome data
microbiome_qc = validator.validate_microbiome_data(
    emp_samples,
    checks=["coordinate_validity", "taxonomic_consistency", "sample_completeness"]
)

# Validate spatial integration
spatial_qc = validator.validate_spatial_integration(
    integrated_data,
    checks=["coverage_completeness", "spatial_autocorrelation", "outlier_detection"]
)
```

### Statistical Validation
```python
# Cross-validation of integration results
from geo_infer_bio.validation import CrossValidation

cv_validator = CrossValidation(n_folds=5)
validation_results = cv_validator.validate_spatial_integration(
    integrated_data,
    methods=["spatial_cv", "temporal_holdout"]
)
```

## What's Next? 🌟

### Recommended Follow-up Examples
1. **Functional Microbiome Mapping**: Extend with metabolic pathway analysis
2. **Phylogeographic Analysis**: Add evolutionary perspectives
3. **Multi-Kingdom Integration**: Include fungi, protists, and viruses
4. **Anthropocene Impact Assessment**: Analyze human influence on microbiomes

### Research Applications
- **Global Change Biology**: Track microbiome responses to climate change
- **Conservation Biology**: Identify microbial diversity hotspots
- **Agricultural Applications**: Optimize soil microbiome for crop health
- **Human Health**: Link environmental microbiomes to human health outcomes

---

**🎯 Success Indicator**: You should now understand how to integrate multiple biological datasets spatially and see the power of H3 indexing for multi-scale biological analysis!

**⚡ Key Innovation**: This example demonstrates **minimal orchestration** of powerful BIO and SPACE capabilities to create sophisticated spatial biological analyses without novel algorithmic development. 