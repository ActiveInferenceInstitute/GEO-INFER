---
name: geo-infer-time
description: Time series analysis and temporal modeling for geospatial data. Use when analyzing temporal patterns, forecasting spatial time series, detecting change points, or working with spatio-temporal datasets.
prerequisites:
  required:
    - geo-infer-math
  recommended:
    - geo-infer-data
difficulty: intermediate
estimated_time: 45min
examples_dir: ../GEO-INFER-EXAMPLES/examples/
---

# GEO-INFER-TIME

## Instructions

### Core Capabilities

- **Time series analysis**: Decomposition, trend detection, seasonality
- **Forecasting**: ARIMA, exponential smoothing, temporal GP
- **Change detection**: CUSUM, Bayesian change points, structural breaks
- **Temporal indexing**: Time-aware spatial queries, temporal resolution management
- **Spatio-temporal**: Joint analysis of spatial and temporal dimensions

### Key Imports

```python
from geo_infer_time import (
    TemporalAnalyzer, ForecastingEngine, EventDetector, TimeSeries,
    StreamProcessor, ReplayIngestAdapter, WebSocketIngestAdapter, KafkaIngestAdapter,
)
```

### Integrations

- Feed timestamped measurements from GEO-INFER-DATA or GEO-INFER-IOT into the explicit replay or live transport adapters.
- Combine temporal windows with GEO-INFER-SPACE H3 indices when records carry spatial identifiers.
- Pass processed windows to the anomaly and forecasting APIs described in the module documentation.

## Examples

```python
import asyncio
from datetime import timedelta
from geo_infer_time import ReplayIngestAdapter, StreamProcessor

processor = StreamProcessor(timedelta(minutes=1))
records = [{"timestamp": "2024-01-01T00:00:00Z", "value": 21.5}]
assert asyncio.run(processor.ingest_adapter_stream(ReplayIngestAdapter(records))) == 1
window = processor.process_window()
assert window["aggregated_value"] == 21.5
```

## Guidelines

- Select `ReplayIngestAdapter` for recorded or offline input. Network adapters connect to real services and never supply replacement measurements.
- Install the TIME `streaming` extra for WebSocket and Kafka ingestion.
- Supply explicit event timestamps; naive input means UTC and output is timezone-aware UTC.
- Read [streaming migration and delivery contracts](docs/streaming_migration.md) before changing callers.
- Run `uv run python -m pytest GEO-INFER-TIME/tests/ -v` for local verification.
- Run the explicit live Kafka service check against a disposable broker when validating network delivery.
