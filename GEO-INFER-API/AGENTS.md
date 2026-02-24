# GEO-INFER-API: Agent Capabilities

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="./README.md">📚 Module Documentation</a>
</div>

---

## Overview

The **GEO-INFER-API** module provides API infrastructure for agents, enabling RESTful services, GraphQL endpoints, and real-time streaming APIs for geospatial operations.

## Agent Capabilities

### 1. REST API Server

```python
from geo_infer_api import APIServer

# Create REST API for agents
server = APIServer()

# Register agent endpoints
@server.route("/analyze", methods=["POST"])
async def analyze_endpoint(request):
    agent = get_analysis_agent()
    result = await agent.analyze(request.data)
    return {"result": result}

# Start server
server.run(host="0.0.0.0", port=8080)```

### 2. GraphQL Interface

```python
from geo_infer_api import GraphQLServer

# Create GraphQL API
gql = GraphQLServer()

# Define schema with spatial types
gql.add_type("""
    type SpatialQuery {
        within(geometry: GeoJSON!): [Feature]
        nearby(point: Point!, radius: Float!): [Feature]
        intersects(geometry: GeoJSON!): [Feature]
    }
""")

# Start GraphQL server
gql.run(port=4000)```

### 3. Streaming API

```python
from geo_infer_api import StreamingAPI

# Create real-time streaming API
stream = StreamingAPI()

# Stream agent observations
@stream.websocket("/observations")
async def stream_observations(ws):
    agent = get_monitoring_agent()
    async for observation in agent.observe():
        await ws.send(observation.to_json())```

### 4. API Gateway

```python
from geo_infer_api import APIGateway

# Create gateway for multiple agents
gateway = APIGateway()

# Route to different agents
gateway.add_route("/spatial/*", service="spatial_agent")
gateway.add_route("/analysis/*", service="analysis_agent")
gateway.add_route("/data/*", service="data_agent")

# Add rate limiting and auth
gateway.add_middleware("rate_limit", requests_per_minute=100)
gateway.add_middleware("auth", provider="jwt")```

## Implementation Status

### Currently Implemented

| Feature | Status | Description |
|---------|--------|-------------|
| **REST API** | ✅ Ready | RESTful endpoints |
| **GraphQL** | ✅ Ready | Query language API |
| **Streaming** | ✅ Ready | WebSocket, SSE |
| **Gateway** | ✅ Ready | Routing, rate limiting |

### Aspirational/Planned Features

| Feature | Priority | Description |
|---------|----------|-------------|
| **APIAgent** | 🔮 High | Self-documenting APIs |
| **LoadBalancer** | 🔮 Medium | Intelligent routing |

## Use Cases

### Geospatial Service API

```python
from geo_infer_api import GeoServiceAPI

api = GeoServiceAPI()

# Expose spatial operations
api.expose_operations([
    "buffer", "intersect", "union", 
    "spatial_join", "geocode"])

# Auto-generate OpenAPI docs
api.generate_docs()```

---

This AGENTS.md documents how GEO-INFER-API provides API capabilities for agents.

**Last Updated**: 2026-02-24
