# Agent
: api ## Scope
 This directory contains api components for the module. It provides 12 classes and 5 functions. ## Classes
 and Functions ### DescriptiveStatsReques
t
 Request model for descriptive statistics. ### DescriptiveStatsRespons
e
 Response model for descriptive statistics. ### AutocorrelationReques
t
 Request model for autocorrelation analysis. ### AutocorrelationRespons
e
 Response model for autocorrelation analysis. ### HotspotAnalysisReques
t
 Request model for hot spot analysis. ### HotspotAnalysisRespons
e
 Response model for hot spot analysis. ### ClusteringReques
t
 Request model for clustering analysis. ### ClusteringRespons
e
 Response model for clustering analysis. ### InterpolationReques
t
 Request model for spatial interpolation. ### InterpolationRespons
e
 Response model for spatial interpolation. ### SpatialDatase
t
 Model for spatial dataset. ### SpatialAnalysisAP
I
 Provides high-level methods for spatial analysis by encapsulating **Methods**: - `autocorrelation_analysis(values: np.ndarray, coordinates: np.ndarray, method: str, **kwargs) -> Dict[str, Any]`: Perform spatial autocorrelation analysis using the specified method. - `point_pattern_analysis(points: np.ndarray, method: str, **kwargs) -> Dict[str, Any]`: Perform point pattern analysis using the specified method. - `spatial_interpolation(known_points: np.ndarray, known_values: np.ndarray, query_points: np.ndarray, method: str, **kwargs) -> np.ndarray`: Perform spatial interpolation to estimate values at unsampled locations. - `distance_matrix(points1: np.ndarray, points2: Optional[np.ndarray], method: str, **kwargs) -> np.ndarray`: Calculate a distance matrix between two sets of points. - `descriptive_statistics(values: np.ndarray, coordinates: Optional[np.ndarray]) -> Dict[str, Any]`: Calculate descriptive statistics for spatial data. - `calculate_descriptive_stats(request_data: Dict[str, Any]) -> Dict[str, Any]`: Calculate descriptive spatial statistics (API endpoint). - `calculate_autocorrelation(request_data: Dict[str, Any]) -> Dict[str, Any]`: Calculate spatial autocorrelation (API endpoint). - `analyze_hotspots(request_data: Dict[str, Any]) -> Dict[str, Any]`: Analyze hot spots (API endpoint). - `perform_clustering(request_data: Dict[str, Any]) -> Dict[str, Any]`: Perform spatial clustering (API endpoint). - `create_flask_app() -> Flask`: Create Flask application with API endpoints. ### health_chec
k
 `health_check()` Health check endpoint. ### descriptive_stats_endpoin
t
 `descriptive_stats_endpoint()` Descriptive spatial statistics endpoint. ### autocorrelation_endpoin
t
 `autocorrelation_endpoint()` Spatial autocorrelation analysis endpoint. ### hotspots_endpoin
t
 `hotspots_endpoint()` Hot spot analysis endpoint. ### clustering_endpoin
t
 `clustering_endpoint()` Spatial clustering analysis endpoint. ## Capabilities
 - **12 classes** for core functionality - **5 functions** for utility operations ## Integration
 - **Location**: `GEO-INFER-MATH/src/geo_infer_math/api` - **Type**: Directory Node 