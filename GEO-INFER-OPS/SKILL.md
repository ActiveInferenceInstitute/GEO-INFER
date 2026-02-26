---
name: geo-infer-ops
description: Operations, monitoring, and observability for geospatial infrastructure. Use when setting up monitoring dashboards, configuring alerts, tracking system health, or managing deployment of spatial services.
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

- **Monitoring**: System health metrics, spatial operation performance
- **Alerting**: Threshold-based and anomaly-based alerts
- **Log aggregation**: Structured log collection and querying
- **Deployment**: Configuration management for spatial services
- **Observability**: Distributed tracing for cross-module operations

### Key Imports

```python
from geo_infer_ops.core.monitoring import MonitoringEngine
from geo_infer_ops.core.alerting import AlertManager
from geo_infer_ops.core.deployment import DeploymentManager
```

## Examples

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

```python
from geo_infer_ops.core.alerting import AlertManager

alerts = AlertManager()
alerts.add_rule(
    name="high_latency",
    metric="h3_index_latency_ms",
    condition="p99 > 500",
    action="notify_slack"
)
alerts.start_watching()
```

## Guidelines

- Uses structured logging (JSON format)
- Prometheus-compatible metrics export
- Test: `uv run python -m pytest GEO-INFER-OPS/tests/ -v`

### Integrations

- **API** → Endpoint monitoring and rate limiting
- **AGENT** → Agent telemetry collection and dashboards
- **IOT** → Sensor health monitoring and alerts
- **LOG** → Logistics operation monitoring
- **SEC** → Security event aggregation
