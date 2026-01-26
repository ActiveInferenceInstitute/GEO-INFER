# Agent
: api ## Scope
 This directory contains api components for the module. It provides 8 classes and 0 functions. ## Classes
 and Functions ### SpatialDat
a
 Spatial data type. ### SequenceDat
a
 Sequence data type. ### AnalysisResul
t
 Analysis result type. ### VisualizationDat
a
 Visualization data type. ### Quer
y
 Query type. **Methods**: - `analyze_sequence(sequence_data: SequenceData) -> AnalysisResult`: Analyze a single sequence. - `analyze_file(file_path: str, spatial_data_path: Optional[str]) -> List[AnalysisResult]`: Analyze sequences from a file. - `visualize_spatial(analysis_results: List[AnalysisResult]) -> VisualizationData`: Generate spatial visualizations of analysis results. - `health_check() -> str`: Health check query. ### SpatialDat
a
 Spatial data model. ### SequenceDat
a
 Sequence data model. ### AnalysisResul
t
 Analysis result model. ## Capabilities
 - **8 classes** for core functionality ## Integration
 - **Location**: `GEO-INFER-BIO/src/geo_infer_bio/api` - **Type**: Directory Node 