"""
GEO-INFER Framework Unified Test Suite

This package provides comprehensive testing capabilities for all GEO-INFER modules
using a unified, modular approach with test-driven development principles.

The test suite includes:
- Unit tests for individual functions and classes
- Integration tests for cross-module interactions
- System tests for end-to-end workflows
- Performance tests for scalability validation
- API tests for external interfaces
- Geospatial-specific tests for spatial functionality
"""

__version__ = "1.0.0"
__author__ = "GEO-INFER Development Team"
__email__ = "geo-infer@activeinference.institute"

# Test categories
TEST_CATEGORIES = {
    "unit": "Unit tests for individual functions and classes",
    "integration": "Integration tests for cross-module interactions", 
    "system": "System tests for end-to-end workflows",
    "performance": "Performance tests for scalability validation",
    "api": "API tests for external interfaces",
    "geospatial": "Geospatial-specific tests for spatial functionality",
    "slow": "Tests that take a long time to run",
    "fast": "Tests that run quickly"
}

# Module test mapping
MODULE_TEST_MAPPING = {
    "ACT": ["active_inference", "belief_updates", "free_energy"],
    "SPACE": ["h3_indexing", "spatial_analysis", "geospatial_processing"],
    "TIME": ["temporal_analysis", "time_series", "dynamic_processing"],
    "DATA": ["etl_processes", "data_pipelines", "storage_optimization"],
    "AI": ["machine_learning", "neural_networks", "predictive_modeling"],
    "BAYES": ["bayesian_inference", "uncertainty_quantification", "posterior_inference"],
    "MATH": ["mathematical_foundations", "statistical_methods", "optimization"],
    "AGENT": ["intelligent_agents", "autonomous_systems", "decision_making"],
    "SIM": ["simulation_environments", "hypothesis_testing", "digital_twins"],
    "API": ["rest_services", "graphql", "external_integration"],
    "APP": ["user_interfaces", "dashboards", "mobile_apps"],
    "SEC": ["security_frameworks", "privacy_protection", "access_control"],
    "OPS": ["orchestration", "system_monitoring", "deployment"],
    "PLACE": ["location_analysis", "regional_insights", "territorial_assessment"],
    "HEALTH": ["public_health", "epidemiology", "healthcare_access"],
    "ECON": ["economic_modeling", "market_analysis", "policy_modeling"],
    "AG": ["agriculture", "precision_farming", "crop_monitoring"],
    "RISK": ["risk_modeling", "insurance", "hazard_assessment"],
    "LOG": ["logistics", "supply_chains", "route_optimization"],
    "BIO": ["bioinformatics", "spatial_omics", "ecological_modeling"],
    "IOT": ["sensor_networks", "real_time_data", "spatial_web"],
    "COG": ["cognitive_modeling", "spatial_cognition", "human_factors"],
    "CIV": ["civic_engagement", "participatory_mapping", "community_planning"],
    "PEP": ["people_management", "hr_systems", "community_relations"],
    "ORG": ["organizations", "dao_frameworks", "governance"],
    "COMMS": ["communications", "documentation", "outreach"],
    "ART": ["artistic_expression", "creative_visualization", "aesthetic_frameworks"],
    "ANT": ["complex_systems", "emergent_behavior", "swarm_dynamics"],
    "NORMS": ["compliance_modeling", "social_norms", "regulatory_frameworks"],
    "REQ": ["requirements_engineering", "system_specifications", "validation"],
    "INTRA": ["documentation", "workflows", "ontology_management"],
    "GIT": ["version_control", "repository_management", "ci_cd"],
    "TEST": ["quality_assurance", "testing_frameworks", "performance_validation"],
    "EXAMPLES": ["cross_module_demos", "tutorials", "integration_examples"],
    "SPM": ["statistical_mapping", "spatial_statistics", "field_analysis"]
}

# Test data fixtures
TEST_DATA_FIXTURES = {
    "sample_geojson": "Sample GeoJSON data for spatial testing",
    "sample_h3_indices": "Sample H3 v4 indices for spatial indexing tests",
    "sample_time_series": "Sample time series data for temporal analysis",
    "sample_remote_sensing": "Sample remote sensing data for analysis",
    "sample_iot_data": "Sample IoT sensor data for real-time processing",
    "sample_health_data": "Sample health data for epidemiological analysis",
    "sample_economic_data": "Sample economic data for modeling",
    "sample_agricultural_data": "Sample agricultural data for precision farming",
    "sample_logistics_data": "Sample logistics data for supply chain optimization",
    "sample_bioinformatics_data": "Sample bioinformatics data for spatial omics"
}

# Performance benchmarks
PERFORMANCE_BENCHMARKS = {
    "h3_processing": "H3 v4 spatial indexing performance",
    "spatial_analysis": "Geospatial analysis performance", 
    "temporal_processing": "Time series processing performance",
    "machine_learning": "ML model training and inference performance",
    "data_pipeline": "ETL and data processing performance",
    "api_response": "API response time performance",
    "memory_usage": "Memory usage optimization",
    "concurrent_processing": "Concurrent processing performance"
}

# Test configuration
TEST_CONFIG = {
    "timeout": 300,  # 5 minutes default timeout
    "memory_limit": "2GB",  # Memory limit for tests
    "parallel_workers": 4,  # Number of parallel test workers
    "retry_failed": 2,  # Number of retries for failed tests
    "coverage_threshold": 80,  # Minimum code coverage percentage
    "performance_threshold": 1.5,  # Performance regression threshold (1.5x slower)
    "geospatial_precision": 1e-6,  # Precision for geospatial comparisons
    "temporal_precision": 1e-9,  # Precision for temporal comparisons
    "numerical_precision": 1e-10  # Precision for numerical comparisons
} 