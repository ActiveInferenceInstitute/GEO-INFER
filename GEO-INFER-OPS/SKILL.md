---
name: geo-infer-ops
description: "Operations, monitoring, and observability for geospatial infrastructure. Use when setting up Prometheus dashboards for tile server or PostGIS latency, configuring alerts on GIS service health, deploying spatial services to Kubernetes, instrumenting H3 indexing or map query performance, or adding structured logging to cross-module geospatial pipelines."
prerequisites:
  required: []
  recommended:
    - geo-infer-api
    - geo-infer-data
difficulty: intermediate
estimated_time: 45min
examples_dir: ../GEO-INFER-EXAMPLES/examples/
---

# GEO-INFER-OPS

## Instructions

### Core Capabilities

- **Monitoring**: Prometheus-compatible metrics (counters, gauges, histograms) for spatial operation performance
- **Alerting**: Threshold-based and anomaly-based alert rules with configurable actions
- **Structured logging**: JSON-formatted log collection via `structlog` with correlation IDs
- **Deployment**: Kubernetes-native configuration management, Docker image builds, and rolling updates
- **Observability**: Distributed tracing for cross-module operations
- **Caching & backup**: In-memory cache management and scheduled backup orchestration

### Workflow

1. **Configure logging** — call `setup_logging()` early to enable structured JSON output before other ops modules initialize.
2. **Register metrics** — use `MonitoringEngine` to define histograms, gauges, and counters for the spatial operations you need to track.
3. **Set alert rules** — attach `AlertManager` rules to registered metrics with conditions and notification actions.
4. **Instrument operations** — wrap spatial calls (tessellation, queries, indexing) with `monitor.timer()` context managers to capture latency.
5. **Verify metrics export** — call `monitor.export_prometheus(port=9090)` and confirm the endpoint is reachable; catch `OSError` if the port is already bound.
6. **Deploy or update** — use `DeploymentManager` to build images, push to a registry, and apply Kubernetes manifests. Always check `build_docker_image()` return value before pushing.
7. **Validate deployment** — verify the Kubernetes deployment status after `apply_manifest()` and log the outcome via structured logging.

### Key Imports

```python
from geo_infer_ops.core.monitoring import MonitoringEngine, record_request
from geo_infer_ops.core.alerting import AlertManager
from geo_infer_ops.core.deployment import DeploymentManager
from geo_infer_ops.core.logging import setup_logging, get_logger
from geo_infer_ops.core.config import get_config
```

## Examples

### Monitoring spatial operations

```python
from geo_infer_ops.core.monitoring import MonitoringEngine

monitor = MonitoringEngine()
monitor.register_metric("h3_index_latency_ms", type="histogram")
monitor.register_metric("active_queries", type="gauge")

# Record spatial operation metrics
with monitor.timer("h3_index_latency_ms"):
    cells = backend.tessellate(region, resolution=7)

monitor.gauge("active_queries", value=42)
dashboard_url = monitor.export_prometheus(port=9090)
```

### Configuring alert rules

```python
from geo_infer_ops.core.alerting import AlertManager

alerts = AlertManager()
alerts.add_rule(
    name="high_latency",
    metric="h3_index_latency_ms",
    condition="p99 > 500",
    action="notify_slack"
)
alerts.add_rule(
    name="error_spike",
    metric="http_errors_total",
    condition="rate_5m > 10",
    action="page_oncall"
)
alerts.start_watching()
```

### Deploying a spatial service

```python
from geo_infer_ops.core.deployment import DeploymentManager
from geo_infer_ops.core.logging import setup_logging, get_logger

setup_logging(log_level="INFO", json_format=True)
logger = get_logger(__name__)

deployer = DeploymentManager(namespace="geo-prod")
if deployer.build_docker_image(tag="geo-infer-api:v2.1.0"):
    deployer.push_docker_image(registry="registry.example.com")
    deployer.apply_manifest("k8s/api-deployment.yaml")
    logger.info("deployment_complete", service="geo-infer-api", version="v2.1.0")
else:
    logger.error("deployment_failed", stage="docker_build")
```

## Guidelines

### Best Practices

- Call `setup_logging()` once at startup before creating monitors or deployers — later calls are ignored due to `cache_logger_on_first_use=True`.
- Use `monitor.timer()` context managers rather than manual start/stop timing to guarantee metric recording even on exceptions.
- Keep alert condition strings simple (`p99 > 500`, `rate_5m > 10`). Complex conditions should be split into multiple rules for clarity.
- Always check `build_docker_image()` return value before pushing — a failed build returns `False` rather than raising.
- Test: `uv run python -m pytest GEO-INFER-OPS/tests/ -v`

### Error Handling

- `DeploymentManager` catches `subprocess.CalledProcessError` internally and returns `False` on build/push failures — always check the boolean result.
- Kubernetes operations raise `kubernetes.client.rest.ApiException` on cluster errors — wrap `apply_manifest` calls in try/except when deploying to uncertain environments.
- `MonitoringEngine.export_prometheus()` will fail if the port is already bound — catch `OSError` and retry on an alternate port or log the conflict.

### Edge Cases

- Re-registering a metric with the same name but different type raises a `ValueError` — check existing metrics before calling `register_metric()`.
- `setup_logging(json_format=False)` switches to console-rendered output, useful for local development but not suitable for log aggregation pipelines.
- When running outside a Kubernetes cluster, `DeploymentManager.__init__` falls back to `~/.kube/config` — ensure the file exists or handle the `ConfigException`.

### Integrations

- **API** → Endpoint monitoring via `record_request()` and rate limiting metrics
- **AGENT** → Agent telemetry collection and dashboards
- **IOT** → Sensor health monitoring and alerts
- **LOG** → Logistics operation monitoring
- **SEC** → Security event aggregation
