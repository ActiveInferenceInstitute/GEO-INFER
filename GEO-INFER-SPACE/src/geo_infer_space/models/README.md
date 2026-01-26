# models
 ## Overview
 This directory contains models components. It includes 2 Python modules. ## Components
 ### config_model
s
.py Configuration models for GEO-INFER-SPACE. **Classes**: `DatabaseConfig`, `IndexingConfig`, `AnalysisConfig`, `APIConfig`, `LoggingConfig`, `CacheConfig`, `OSCConfig`, `SpaceConfig`, `PerformanceConfig` **Functions**: `convert_paths` ### data_model
s
.py Pydantic data models for spatial data structures. **Classes**: `GeometryType`, `CoordinateReferenceSystem`, `GeometryModel`, `SpatialBounds`, `SpatialIndex`, `SpatialMetadata`, `SpatialDataset`, `AnalysisResult`, `H3CellData`, `NetworkEdge`, `NetworkNode`, `SpatialNetwork` ## Usage
 See individual component documentation for usage examples. ## Integration
 This directory integrates with other module components and may be used by higher-level modules. 