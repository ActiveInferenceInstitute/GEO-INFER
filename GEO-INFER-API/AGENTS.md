# GEO-INFER-API: API Framework

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="../GEO-INFER-INTRA/README.md">📚 Documentation</a>
</div>

---

## Overview


The GEO-INFER-API module provides foundational RESTful and GraphQL API capabilities that enable agent communication, coordination, and external service integration. This module serves as the communication backbone for the multi-agent ecosystem.

## Implementation Status

**⚠️ Important Note**: This document describes both **implemented** and **aspirational** features. Features marked with 🔮 are planned/aspirational and not yet implemented.

### Currently Implemented

- ✅ **REST API Framework**: FastAPI-based endpoints for all modules
- ✅ **Authentication & Authorization**: JWT-based security
- ✅ **Rate Limiting**: Request throttling and quota management
- ✅ **WebSocket Support**: Real-time bidirectional communication

### Aspirational/Planned Features

- 🔮 **GraphQL API**: Flexible query interface
- 🔮 **gRPC Support**: High-performance inter-service communication
- 🔮 **Agent-to-Agent Protocol**: Standardized FIPA-ACL messaging

## Agent Capabilities Supported

### 1. Agent Communication Interface

API provides the communication layer for agent interactions:

```python
from geo_infer_api import AgentAPIClient

# Agent communication client
client = AgentAPIClient(
    base_url="http://localhost:8000",
    agent_id="agent_001",
    auth_token=jwt_token
)

# Send message to another agent
response = client.send_message(
    to_agent="agent_002",
    message_type="coordination",
    payload={'task': 'data_collection', 'area': region}
)

# Receive messages
messages = client.receive_messages()
```

### 2. External Service Integration

API enables agents to interact with external data sources and services:

```python
from geo_infer_api import ExternalServiceClient

# External service integration
service = ExternalServiceClient()

# Fetch satellite imagery
imagery = service.fetch_satellite_data(
    bbox=bounding_box,
    date_range=time_window,
    product='sentinel-2'
)

# Query weather services
weather = service.fetch_weather_forecast(
    location=coordinates,
    horizon_days=7
)
```

### 3. Real-Time Agent Coordination

WebSocket support enables real-time agent coordination:

```python
from geo_infer_api import AgentWebSocket

# Real-time agent connection
ws = AgentWebSocket(
    url="ws://localhost:8000/agents",
    agent_id="agent_001"
)

# Subscribe to coordination events
ws.subscribe("coordination_channel")

# Broadcast status
ws.broadcast({
    'type': 'status_update',
    'position': current_position,
    'task_status': 'active'
})
```

## Integration Status

| Capability | Status | Description |
|------------|--------|-------------|
| **REST Endpoints** | ✅ Ready | Full CRUD operations for all modules |
| **Authentication** | ✅ Ready | JWT-based agent authentication |
| **WebSocket** | ✅ Ready | Real-time communication |
| **Rate Limiting** | ✅ Ready | Quota management |
| **GraphQL** | 🔮 Planned | Flexible query interface |
| **gRPC** | 🔮 Planned | High-performance RPC |
| **FIPA-ACL** | 🔮 Planned | Agent communication language |

---

This AGENTS.md file documents how the GEO-INFER-API module provides communication infrastructure for the intelligent agent ecosystem.
