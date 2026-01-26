# Agent
: del_norte_county ## Scope
 This directory contains del_norte_county components for the module. It provides 4 classes and 1 functions. ## Classes
 and Functions ### CoastalResilienceAnalyze
r
 Coastal resilience analysis system for Del Norte County. **Methods**: - `run_analysis(temporal_range: Optional[Tuple[str, str]]) -> Dict[str, Any]`: Run coastal resilience analysis. - `get_monitoring_status() -> Dict[str, Any]`: Get current monitoring system status. ### DelNorteComprehensiveDashboar
d
 interactive dashboard for Del Norte County analysis. **Methods**: - `load_configuration() -> Dict[str, Any]`: Load Del Norte County configuration and initialize analyzers. - `fetch_real_data() -> Dict[str, Any]`: Fetch real data from California and federal APIs. - `run_comprehensive_analysis() -> Dict[str, Any]`: Run analysis across all domains. - `generate_comprehensive_dashboard() -> str`: Generate interactive dashboard with all analysis results. - `export_analysis_results() -> str`: Export analysis results to JSON. - `generate_summary_report() -> str`: Generate a summary report of the analysis. ### FireRiskAssesso
r
 Fire risk assessment system for Del Norte County. **Methods**: - `run_analysis(temporal_range: Optional[Tuple[str, str]]) -> Dict[str, Any]`: Run fire risk analysis. - `get_monitoring_status()`: Get current monitoring system status. ### ForestHealthMonito
r
 Forest health monitoring system for Del Norte County. **Methods**: - `run_analysis(temporal_range: Optional[Tuple[str, str]]) -> Dict[str, Any]`: Run forest health analysis for Del Norte County. - `get_monitoring_status() -> Dict[str, Any]`: Get current monitoring system status. ## Capabilities
 - **4 classes** for core functionality - **1 functions** for utility operations ## Integration
 - **Location**: `src/geo_infer_place/locations/del_norte_county` - **Type**: Directory Node 