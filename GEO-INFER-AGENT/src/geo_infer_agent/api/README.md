# api
 ## Overview
 This directory contains api components. It includes 4 Python modules. ## Components
 ### agent_endpoint
s
.py REST API endpoints for the GEO-INFER-AGENT system. **Classes**: `AgentCreate`, `AgentAction`, `AgentMessage`, `AgentResponse` **Functions**: `start_api_server` ### interfac
e
.py Unified interface for external systems to interact with agents. **Classes**: `AgentInterface` ### messagin
g
.py Agent-to-agent messaging interface for GEO-INFER-AGENT. **Classes**: `Message`, `MessagingService` ### telemetr
y
.py Telemetry module for GEO-INFER-AGENT. **Classes**: `MetricType`, `Metric`, `CounterMetric`, `GaugeMetric`, `HistogramMetric`, `TimerMetric`, `TelemetryService` ## Usage
 See individual component documentation for usage examples. ## Integration
 This directory integrates with other module components and may be used by higher-level modules. 