# Agent
: core ## Scope
 This directory contains core components for the module. It provides 17 classes and 26 functions. ## Classes
 and Functions ### CacheSerialize
r
 Cache serialization formats. ### CacheManage
r
 Manages caching operations for GEO-INFER-OPS. **Methods**: - `get(key: str, default: Any) -> Any`: Get value from cache. - `set(key: str, value: Any, expire: Optional[int], nx: bool, xx: bool) -> bool`: Set value in cache. - `delete(key: str) -> bool`: Delete value from cache. - `exists(key: str) -> bool`: Check if key exists in cache. - `expire(key: str, seconds: int) -> bool`: Set expiration time for key. - `ttl(key: str) -> Optional[int]`: Get time to live for key. - `increment(key: str, amount: int) -> Optional[int]`: Increment value in cache. - `decrement(key: str, amount: int) -> Optional[int]`: Decrement value in cache. - `get_many(keys: List[str]) -> Dict[str, Any]`: Get multiple values from cache. - `set_many(mapping: Dict[str, Any], expire: Optional[int]) -> bool`: Set multiple values in cache. - `delete_many(keys: List[str]) -> bool`: Delete multiple values from cache. - `clear() -> bool`: Clear all cache entries with prefix. - `get_size() -> int`: Get number of cache entries with prefix. ### LoggingConfi
g
 Logging configuration. **Methods**: - `validate_log_level(cls, v)`: Validate log level. - `validate_log_format(cls, v)`: Validate log format. ### MonitoringConfi
g
 Monitoring configuration. **Methods**: - `validate_metrics_port(cls, v)`: Validate metrics port. ### TestingConfi
g
 Testing configuration. **Methods**: - `validate_coverage_threshold(cls, v)`: Validate coverage threshold. - `validate_timeout(cls, v)`: Validate timeout value. ### DockerConfi
g
 Docker configuration. **Methods**: - `validate_timeout(cls, v)`: Validate timeout value. ### KubernetesConfi
g
 Kubernetes configuration. **Methods**: - `validate_timeout(cls, v)`: Validate timeout value. ### DeploymentConfi
g
 Deployment configuration. **Methods**: - `validate_replicas(cls, v: int) -> int`: Validate replicas count. - `validate_timeout(cls, v: int) -> int`: Validate timeout value. ### TLSConfi
g
 TLS configuration. **Methods**: - `validate_file_paths(cls, v, info)`: Validate file paths. ### AuthConfi
g
 Authentication configuration. **Methods**: - `validate_token_expiry(cls, v)`: Validate token expiry. ### SecurityConfi
g
 Security configuration. ### Confi
g
 Main configuration. **Methods**: - `validate_environment(cls, v)`: Validate environment name. ### DeploymentManage
r
 Manages deployment operations for GEO-INFER-OPS. **Methods**: - `build_docker_image(tag: Optional[str]) -> bool`: Build Docker image for GEO-INFER-OPS. - `push_docker_image(registry: Optional[str]) -> bool`: Push Docker image to registry. - `deploy_kubernetes(manifest_path: Optional[str]) -> bool`: Deploy to Kubernetes using manifests. - `get_deployment_status(name: str) -> Dict`: Get status of a Kubernetes deployment. - `scale_deployment(name: str, replicas: int) -> bool`: Scale a Kubernetes deployment. - `get_pods(label_selector: Optional[str]) -> List[Dict]`: Get pods in the namespace. ### TaskStatu
s
 Task execution status. ### Tas
k
 Represents a task in the orchestration workflow. ### Orchestrato
r
 Workflow orchestrator for GEO-INFER operations. **Methods**: - `add_task(name: str, func: Callable, dependencies: Optional[List[str]], task_id: Optional[str], max_retries: int, metadata: Optional[Dict[str, Any]]) -> str`: Add a task to the workflow. - `get_task_status(task_id: str) -> Optional[Dict[str, Any]]`: Get status of a specific task. - `get_workflow_status() -> Dict[str, Any]`: Get overall workflow status. - `cancel_task(task_id: str) -> bool`: Cancel a task. - `reset_workflow() -> None`: Reset all tasks to pending status. ### SecurityManage
r
 Manages security operations for GEO-INFER-OPS. **Methods**: - `generate_tls_certificate(common_name: str, organization: str, country: str, days_valid: int) -> Dict[str, str]`: Generate a self-signed TLS certificate. - `generate_csr(common_name: str, organization: str, country: str, key_size: int) -> str`: Generate a Certificate Signing Request (CSR). - `generate_jwt_token(user_id: str, expires_in: int, **kwargs) -> str`: Generate a JWT token. - `verify_jwt_token(token: str) -> Dict[str, Any]`: Verify a JWT token. - `encrypt_data(data: str) -> str`: Encrypt data using Fernet symmetric encryption. - `decrypt_data(encrypted_data: str) -> str`: Decrypt data using Fernet symmetric encryption. - `generate_password_hash(password: str, salt: Optional[bytes]) -> Dict[str, bytes]`: Generate a password hash using PBKDF2. - `verify_password(password: str, stored_hash: bytes, salt: bytes) -> bool`: Verify a password against its stored hash. ### load_confi
g
 `load_config(config_file: Optional[str]) -> Config` Load configuration from file or environment variables. ### get_confi
g
 `get_config() -> Config` Get the current configuration instance. ### update_confi
g
 `update_config(config_dict: Dict[str, Any]) -> Config` Update configuration with values. ### configure_stdlib_loggin
g
 `configure_stdlib_logging(log_level: str, log_file: Optional[str]) -> None` Configure standard library logging. ### setup_loggin
g
 `setup_logging(log_level: str, json_format: bool, log_file: Optional[str]) -> None` Set up structured logging. ### get_logge
r
 `get_logger(name: str) -> structlog.stdlib.BoundLogger` Get a structured logger instance. ### reset_metric
s
 `reset_metrics() -> None` Reset all metrics. ### record_reques
t
 `record_request(method: str, endpoint: str, status: int, duration: float) -> None` Record a request metric. ### record_erro
r
 `record_error(method: str, endpoint: str, error_type: str) -> None` Record an error metric. ### record_metri
c
 `record_metric(name: str, value: float, metric_type: str, labels: Optional[Dict[str, str]]) -> None` Record a metric value. ### get_metric_valu
e
 `get_metric_value(name: str, labels: Optional[Dict[str, str]]) -> float` Get the value of a metric. ### is_port_in_us
e
 `is_port_in_use(port: int) -> bool` Check if a port is in use. ### start_metrics_serve
r
 `start_metrics_server(port: int) -> None` Start metrics server. ### instrument_ap
p
 `instrument_app(app: Any) -> None` Instrument a FastAPI application. ### setup_monitorin
g
 `setup_monitoring(app: Optional[Any], port: Optional[int], metrics_path: str) -> None` Set up monitoring. ### mock_confi
g
 `mock_config(config_dict: Dict[str, Any]) -> Generator[Config, None, None]` Mock configuration for testing. ### create_test_data_di
r
 `create_test_data_dir(prefix: str) -> str` Create a temporary directory for test data. ### create_test_clien
t
 `create_test_client(app: Any) -> TestClient` Create a test client for a FastAPI application. ### setup_testin
g
 `setup_testing(test_dir: str, coverage_report: bool, parallel: bool, timeout: Optional[int], log_level: str, json_format: bool) -> int` Set up and run tests. ### assert_response_statu
s
 `assert_response_status(response: Any, expected_status: int) -> None` Assert response status code. ### assert_response_jso
n
 `assert_response_json(response: Any, expected_json: Dict[str, Any]) -> None` Assert response JSON content. ### assert_metric_valu
e
 `assert_metric_value(metric_name: str, expected_value: Union[int, float], labels: Optional[Dict[str, str]]) -> None` Assert Prometheus metric value. ### create_test_ap
p
 `create_test_app() -> Any` Create a test FastAPI application. ### create_test_reques
t
 `create_test_request() -> Dict[str, Any]` Create a test request. ### create_test_respons
e
 `create_test_response() -> Dict[str, Any]` Create a test response. ### create_test_metri
c
 `create_test_metric(name: str, metric_type: str, labels: Optional[List[str]]) -> Union[Counter, Gauge, Histogram]` Create a test metric. ## Capabilities
 - **17 classes** for core functionality - **26 functions** for utility operations ## Integration
 - **Location**: `GEO-INFER-OPS/src/geo_infer_ops/core` - **Type**: Directory Node 