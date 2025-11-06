# Module Integration Guidelines

## Data Flow Patterns

- **Linear Pipeline**: Sequential processing (DATA → SPACE → TIME → ANALYSIS)
- **Hub and Spoke**: Central coordination (API as central hub)
- **Event-Driven**: Real-time responsive systems (IOT → processing → response)
- **Feedback Loops**: Active inference cycles (observation → belief update → action)

## Common Integration Points

- **OPS**: Provides orchestration for all modules
- **DATA**: Supplies data management for all analytical modules
- **API**: Exposes functionality for external integration
- **MATH**: Provides mathematical foundations for analytical modules
- **SPACE/TIME**: Supply spatial-temporal capabilities to domain modules

## Module Dependency Matrix

For the complete dependency matrix with all 30+ modules, see the main README.md at `/README.md` (section "Complete Module Dependencies Matrix").

### Core Dependencies

- **MATH**: Foundation for all analytical modules (ACT, BAYES, AI, SPM)
- **DATA**: Required by all modules that process data (SPACE, TIME, AI, domain modules)
- **SPACE**: Provides spatial capabilities to domain modules (AG, HEALTH, ECON, RISK, LOG, BIO, PLACE)
- **TIME**: Provides temporal capabilities to domain modules (AG, HEALTH, ECON, SIM, LOG, RISK, BIO)
- **ACT**: Provides Active Inference to AGENT, SIM, and decision systems
- **BAYES**: Provides Bayesian inference to ACT, AI, and statistical modules

### H3 v4 Migration Status

- ✅ **FULLY MIGRATED**: SPACE, PLACE modules use H3 v4 API exclusively
- ✅ **Updated**: Most modules have been updated to work with H3 v4
- ⏳ **Planned**: Some modules (SIM, AI) have H3 v4 migration planned

**Important**: When integrating with SPACE or PLACE modules, always use H3 v4 API methods:
- `h3.latlng_to_cell()` (not `h3.geo_to_h3()`)
- `h3.cell_to_latlng()` (not `h3.h3_to_geo()`)
- `h3.geo_to_cells()` (not deprecated v3 methods)

## Cross-Module Communication

- Use standardized data models from the models package
- Implement proper API versioning
- Support both synchronous and asynchronous communication
- Handle errors gracefully across module boundaries
- Use consistent data formats and schemas

## Integration Examples

### GEO-INFER-ACT Integration

```python
from geo_infer_agent.models.active_inference import ActiveInferenceAgent
from geo_infer_act.core.active_inference import ActiveInferenceModel

# Create agent with active inference
agent = ActiveInferenceAgent(
    state_dim=10,
    obs_dim=5,
    action_dim=3
)
```

### GEO-INFER-SPACE Integration

```python
from geo_infer_space.core.spatial_indexing import SpatialIndexingInterface
from geo_infer_space.core.analytics import SpatialAnalyticsInterface

# Use H3 backend for spatial indexing
spatial_indexer = SpatialIndexingInterface(backend='h3')
cell = spatial_indexer.latlng_to_cell(37.7749, -122.4194, 9)
```

### GEO-INFER-DATA Integration

```python
from geo_infer_data import MultiSourceDataIngestion

# Ingest data from multiple sources
ingestion = MultiSourceDataIngestion()
result = await ingestion.ingest_multi_source(
    satellite={'bbox': [-122.5, 37.7, -122.3, 37.9]},
    sensors={'time_range': '2023-01-01/2023-01-31'}
)
```

### GEO-INFER-TIME Integration

```python
from geo_infer_time import TemporalAnalyzer, TimeSeriesProcessor

# Temporal analysis for time-series data
analyzer = TemporalAnalyzer()
processor = TimeSeriesProcessor()

# Process temporal data
forecast = analyzer.forecast(
    time_series_data,
    horizon=30,
    method='arima'
)
```

### GEO-INFER-BAYES Integration

```python
from geo_infer_bayes import BayesianInference, SpatialBayesianModel

# Bayesian inference for uncertainty quantification
inference = BayesianInference()
model = SpatialBayesianModel(
    prior_distribution='gaussian',
    likelihood='spatial_gaussian_process'
)

# Perform Bayesian analysis
posterior = inference.update_beliefs(
    observations=obs_data,
    prior=prior_distribution
)
```

### GEO-INFER-AGENT Integration

```python
from geo_infer_agent.core.agent_registry import AgentRegistry
from geo_infer_agent.models.active_inference import ActiveInferenceAgent
from geo_infer_space.core.spatial_indexing import SpatialIndexingInterface

# Multi-agent system with spatial awareness
registry = AgentRegistry()
spatial_indexer = SpatialIndexingInterface(backend='h3')

# Create spatially-aware agent
agent = ActiveInferenceAgent(
    agent_id="spatial_agent_001",
    spatial_context=spatial_indexer
)
registry.register_agent(agent)
```

## Module Categories and Integration Patterns

### Analytical Core Modules
- **ACT, BAYES, AI, MATH, COG, AGENT, SPM**: Integrate through shared mathematical foundations and data models

### Spatial-Temporal Modules
- **SPACE, TIME, IOT**: Provide spatial-temporal capabilities to all domain modules
- **SPACE** (H3 v4): Fully migrated, use H3 v4 API exclusively
- **TIME**: Provides temporal analysis to domain modules
- **IOT**: Real-time sensor data integration

### Domain-Specific Modules
- **AG, HEALTH, ECON, RISK, LOG, BIO**: Depend on SPACE, TIME, DATA for spatial-temporal analysis
- Integrate with analytical modules (ACT, BAYES, AI) for advanced modeling

### Application Modules
- **APP, ART**: Consume services from all other modules
- **PLACE**: Place-based analysis integrating all modules (H3 v4 migrated)

## Integration Best Practices

1. **Check Dependencies**: Always verify module dependencies before integration
2. **Use Standard Interfaces**: Prefer standardized interfaces (SpatialIndexingInterface, etc.)
3. **Handle Errors Gracefully**: Implement proper error handling across module boundaries
4. **Respect Data Flow**: Follow established data flow patterns (see main README.md)
5. **Version Compatibility**: Ensure module versions are compatible
6. **H3 v4 Compliance**: When working with spatial data, use H3 v4 API methods

