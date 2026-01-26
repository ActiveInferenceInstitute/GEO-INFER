# Agent
: io ## Scope
 This directory contains io components for the module. It provides 2 classes and 5 functions. ## Classes
 and Functions ### VectorReade
r
 Reader class for vector geospatial data. **Methods**: - `read(file_path: Union[str, Path], **kwargs) -> gpd.GeoDataFrame`: Read vector data from file. ### VectorWrite
r
 Writer class for vector geospatial data. **Methods**: - `write(gdf: gpd.GeoDataFrame, file_path: Union[str, Path], **kwargs) -> None`: Write GeoDataFrame to file. ### read_vector_fil
e
 `read_vector_file(file_path: Union[str, Path], **kwargs) -> gpd.GeoDataFrame` Read vector data from file using appropriate reader. ### write_vector_fil
e
 `write_vector_file(gdf: gpd.GeoDataFrame, file_path: Union[str, Path], **kwargs) -> None` Write GeoDataFrame to file using appropriate writer. ### supported_vector_format
s
 `supported_vector_formats() -> Dict[str, str]` Get dictionary of supported vector formats. ### detect_vector_forma
t
 `detect_vector_format(file_path: Union[str, Path]) -> Optional[str]` Detect vector format from file extension. ### validate_vector_fil
e
 `validate_vector_file(file_path: Union[str, Path]) -> Dict[str, Any]` Validate vector file and return metadata. ## Capabilities
 - **2 classes** for core functionality - **5 functions** for utility operations ## Integration
 - **Location**: `GEO-INFER-SPACE/src/geo_infer_space/io` - **Type**: Directory Node 