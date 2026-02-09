# Agent
: api

## Scope
 This directory contains api components for the module. It provides 8 classes and 0 functions.

## Classes
 and Functions

### SpatialData
 Spatial data type.

### SequenceData
 Sequence data type.

### AnalysisResult
 Analysis result type.

### VisualizationData
 Visualization data type.

### Query
 Query type.

**Methods**:
- `analyze_sequence(sequence_data: SequenceData) -> AnalysisResult`: Analyze a single sequence.
- `analyze_file(file_path: str, spatial_data_path: Optional[str]) -> List[AnalysisResult]`: Analyze sequences from a file.
- `visualize_spatial(analysis_results: List[AnalysisResult]) -> VisualizationData`: Generate spatial visualizations of analysis results.
- `health_check() -> str`: Health check query.

### SpatialData
 Spatial data model.

### SequenceData
 Sequence data model.

### AnalysisResult
 Analysis result model.

## Capabilities

- **8 classes** for core functionality

## Integration

- **Location**: `GEO-INFER-BIO/src/geo_infer_bio/api`
- **Type**: Directory Node
