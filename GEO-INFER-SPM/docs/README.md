# GEO-INFER-SPM Documentation

This directory contains comprehensive documentation for the GEO-INFER-SPM module.

## Documentation Structure

### Core Documentation
- `api_schema.yaml` - OpenAPI specification for SPM REST API endpoints
- `architecture.md` - System architecture and design decisions
- `tutorials/` - Step-by-step tutorials and walkthroughs
- `examples/` - Working code examples and use cases

### Integration Guides
- `integration_guide.md` - Integration patterns with other GEO-INFER modules
- `api_integration.md` - API integration examples and best practices

### Technical Reference
- `mathematical_framework.md` - Mathematical foundations of SPM
- `performance_guide.md` - Performance optimization and scaling
- `troubleshooting.md` - Common issues and solutions

## Key Concepts

### Statistical Parametric Mapping (SPM)
SPM extends the general linear model to continuous data fields, providing:

- **Hypothesis Testing**: Test specific predictions about spatial/temporal patterns
- **Multiple Comparison Correction**: Control family-wise error rates
- **Cluster Analysis**: Identify connected regions of significant effects
- **Uncertainty Quantification**: Provide confidence intervals and probability maps

### Active Inference Framework
The implementation grounds SPM analysis in Active Inference principles:

- **Free Energy Minimization**: Model fitting as free energy minimization
- **Bayesian Inference**: Probabilistic treatment of uncertainty
- **Perception-Action Loops**: Integration of observation and prediction

## Quick Start

### Basic Analysis Pipeline

```python
import geo_infer_spm as gispm

# 1. Load geospatial data
data = gispm.load_data("environmental_data.tif")

# 2. Create design matrix
design = gispm.create_design_matrix(data, covariates=['elevation', 'temperature'])

# 3. Fit GLM
model = gispm.fit_glm(data, design)

# 4. Test hypothesis
contrast = gispm.contrast(model, "elevation > 0")
spm_result = gispm.compute_spm(model, contrast, correction="FDR")

# 5. Visualize results
gispm.visualize_spm(spm_result, threshold=0.05)
```

### Advanced Features

```python
# Spatial autocorrelation modeling
spatial_analyzer = gispm.SpatialAnalyzer(data.coordinates)
variogram = spatial_analyzer.estimate_variogram(model.residuals)

# Bayesian uncertainty quantification
bayesian_model = gispm.BayesianSPM()
bayesian_result = bayesian_model.fit_bayesian_glm(data, design.matrix)

# Temporal trend analysis
temporal_analyzer = gispm.TemporalAnalyzer(data.time)
trends = temporal_analyzer.detect_trends(data.data, method="mann_kendall")
```

## API Reference

### Core Classes

#### SPMData
Container for geospatial data with spatial coordinates, temporal information, and covariates.

#### DesignMatrix
Specification of the general linear model design including regressors and their relationships.

#### SPMResult
Complete results from SPM analysis including model parameters, diagnostics, and statistical maps.

#### ContrastResult
Results from testing specific statistical contrasts with significance testing and correction.

### Key Functions

#### Data I/O
- `load_data()` - Load data from various geospatial formats
- `save_spm()` - Save analysis results
- `preprocess_data()` - Apply preprocessing pipelines

#### Model Fitting
- `fit_glm()` - Fit General Linear Model
- `contrast()` - Define statistical contrasts
- `compute_spm()` - Apply multiple comparison correction

#### Analysis Tools
- `SpatialAnalyzer` - Spatial autocorrelation and clustering
- `TemporalAnalyzer` - Time series analysis and trend detection
- `BayesianSPM` - Bayesian inference methods

#### Visualization
- `create_statistical_map()` - Generate SPM statistical maps
- `plot_model_diagnostics()` - Diagnostic plots
- `create_interactive_map()` - Interactive web-based visualization

## Integration with GEO-INFER Framework

### Module Dependencies
```
GEO-INFER-SPM
├── GEO-INFER-DATA    # Data management and I/O
├── GEO-INFER-SPACE   # Spatial indexing and coordinate systems
├── GEO-INFER-TIME    # Temporal sequence handling
├── GEO-INFER-BAYES   # Bayesian statistical methods
├── GEO-INFER-APP     # Visualization and interactive mapping
└── GEO-INFER-MATH    # Mathematical foundations
```

### Data Flow Patterns
1. **Raw Data** → GEO-INFER-DATA → GEO-INFER-SPM
2. **Spatial Processing** → GEO-INFER-SPACE → GEO-INFER-SPM
3. **Temporal Processing** → GEO-INFER-TIME → GEO-INFER-SPM
4. **Statistical Analysis** → GEO-INFER-SPM → Results
5. **Visualization** → GEO-INFER-SPM → GEO-INFER-APP

## Applications

### Environmental Monitoring
- Climate anomaly detection
- Pollution source identification
- Biodiversity hotspot mapping
- Land use change analysis

### Urban Analytics
- Urban growth pattern analysis
- Transportation flow modeling
- Social spatial clustering
- Infrastructure utilization mapping

### Public Health
- Disease cluster detection
- Environmental health risk mapping
- Epidemiological pattern analysis
- Exposure pathway identification

### Resource Management
- Crop yield optimization
- Water quality monitoring
- Mineral exploration
- Forest health assessment

## Performance Considerations

### Memory Management
- Process large datasets in chunks
- Use sparse matrix representations when appropriate
- Implement memory-efficient algorithms for high-resolution data

### Computational Scaling
- Parallel processing for independent analyses
- GPU acceleration for matrix operations
- Optimized algorithms for real-time analysis

### Accuracy vs Speed Trade-offs
- Choose appropriate statistical methods based on data characteristics
- Balance model complexity with computational requirements
- Use approximation methods for exploratory analysis

## Troubleshooting

### Common Issues

**High Memory Usage**
- Reduce data resolution or use spatial subsampling
- Process data in smaller temporal chunks
- Use memory-efficient preprocessing options

**Slow Computation**
- Enable parallel processing (`n_jobs=-1`)
- Use faster approximation methods
- Optimize design matrix structure

**Convergence Issues**
- Check data scaling and normalization
- Simplify model specification
- Use robust estimation methods

**False Positives/Negatives**
- Verify multiple comparison correction is appropriate
- Check spatial autocorrelation assumptions
- Validate statistical model assumptions

## Contributing

Contributions to GEO-INFER-SPM documentation are welcome. Please follow these guidelines:

1. **Code Examples**: Include working code examples with realistic data
2. **Mathematical Rigor**: Document mathematical foundations and assumptions
3. **Integration Patterns**: Show how SPM integrates with other modules
4. **Performance Notes**: Include performance considerations and benchmarks
5. **Troubleshooting**: Document common issues and solutions

## License

This documentation is part of the GEO-INFER framework and follows the same license terms.
