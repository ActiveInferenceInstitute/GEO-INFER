# core
 ## Overview
 This directory contains core components. It includes 8 Python modules. ## Components
 ### cach
e
.py Caching management for GEO-INFER-OPS. **Classes**: `CacheSerializer`, `CacheManager` ### confi
g
.py Configuration management module. **Classes**: `LoggingConfig`, `MonitoringConfig`, `TestingConfig`, `DockerConfig`, `KubernetesConfig`, `DeploymentConfig`, `TLSConfig`, `AuthConfig`, `SecurityConfig`, `Config` **Functions**: `load_config`, `get_config`, `update_config` ### deploymen
t
.py Deployment management for GEO-INFER-OPS. **Classes**: `DeploymentManager` ### loggin
g
.py Logging configuration module. **Functions**: `configure_stdlib_logging`, `setup_logging`, `get_logger` ### monitorin
g
.py Monitoring configuration module. **Functions**: `reset_metrics`, `record_request`, `record_error`, `record_metric`, `get_metric_value`, `is_port_in_use`, `start_metrics_server`, `instrument_app`, `setup_monitoring` ### orchestrato
r
.py Orchestration engine for GEO-INFER-OPS. **Classes**: `TaskStatus`, `Task`, `Orchestrator` ### securit
y
.py Security management for GEO-INFER-OPS. **Classes**: `SecurityManager` ### testin
g
.py Testing configuration module. **Functions**: `mock_config`, `create_test_data_dir`, `create_test_client`, `setup_testing`, `assert_response_status`, `assert_response_json`, `assert_metric_value`, `create_test_app`, `create_test_request`, `create_test_response`, `create_test_metric` ## Usage
 See individual component documentation for usage examples. ## Integration
 This directory integrates with other module components and may be used by higher-level modules. 