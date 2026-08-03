# Production Architecture

This guide provides a reference architecture for deploying GEO-INFER in production environments. It covers service topology, database selection, security integration, observability, and deployment strategies for geospatial workloads.

## Reference Architecture

```
                            +-------------------+
                            |   Load Balancer   |
                            |  (TLS termination)|
                            +---------+---------+
                                      |
                    +-----------------+-----------------+
                    |                                   |
          +---------+---------+               +---------+---------+
          |  GEO-INFER-API    |               |  Tile Server      |
          |  (FastAPI/Uvicorn)|               |  (Martin/pg_tileserv)
          +---------+---------+               +---------+---------+
                    |                                   |
      +-------------+-------------+                     |
      |             |             |                     |
+-----+-----+ +----+----+ +------+------+        +-----+-----+
|GEO-INFER  | |GEO-INFER| |GEO-INFER   |        | PostGIS   |
|SPACE      | |ACT      | |BAYES        |        | (vector)  |
|(spatial   | |(inference| |(Bayesian    |        +-----------+
| analysis) | | engine) | | models)     |
+-----------+ +---------+ +-------------+
      |             |             |
      +-------------+-------------+
                    |
      +-------------+-------------+
      |             |             |
+-----+-----+ +----+----+ +------+------+
|PostGIS    | |Redis    | |Object Store |
|(vector DB)| |(cache)  | |(COG rasters)|
+-----------+ +---------+ +-------------+

      +-------------------------------------------+
      |          GEO-INFER-OPS                     |
      |  (Prometheus + Grafana + OpenTelemetry)    |
      +-------------------------------------------+

      +-------------------------------------------+
      |          GEO-INFER-SEC                     |
      |  (Auth, RBAC, audit logging)               |
      +-------------------------------------------+
```

## Service Topology

### Microservices vs Monolith

GEO-INFER modules have clear boundaries that map naturally to services, but not every deployment needs microservices.

**Start with a modular monolith:**

```
```python
# Single FastAPI application importing multiple modules
from fastapi import FastAPI
from geo_infer_api.routes import spatial_router, temporal_router, inference_router
from geo_infer_sec.middleware import AuthMiddleware

app = FastAPI(title="GEO-INFER API")
app.add_middleware(AuthMiddleware)
app.include_router(spatial_router, prefix="/v1/spatial")
app.include_router(temporal_router, prefix="/v1/temporal")
app.include_router(inference_router, prefix="/v1/inference")
```

**Extract to microservices when:**

- A single module has different scaling requirements (e.g., GEO-INFER-BAYES GP fitting is CPU-bound while GEO-INFER-API is I/O-bound)
- Teams need independent deployment cycles
- A module requires a different runtime (e.g., GPU-based inference)

### GEO-INFER-API as Gateway

GEO-INFER-API serves as the unified entry point. All external traffic flows through it.

Responsibilities:
- Request routing to backend modules
- Input validation and serialization
- Rate limiting
- API versioning
- Response caching headers

```
```python
# API gateway pattern
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="GEO-INFER Gateway", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization"],
)

@app.middleware("http")
async def add_cache_headers(request: Request, call_next):
    response = await call_next(request)
    if request.method == "GET":
        response.headers["Cache-Control"] = "public, max-age=300"
    return response
```

### GEO-INFER-SEC for Security

GEO-INFER-SEC provides authentication, authorization, and audit logging.

**Authentication flow:**

1. Client sends JWT or API key in the Authorization header
2. GEO-INFER-SEC middleware validates the token
3. User identity and permissions are injected into the request context
4. Module endpoints check permissions before executing

```
```python
# Security middleware
from geo_infer_sec.auth import verify_token, check_permission

async def auth_middleware(request: Request, call_next):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = verify_token(token)
    if not user:
        return Response(status_code=401, content="Invalid token")

    request.state.user = user
    response = await call_next(request)
    return response
```

## Database Selection

### Vector Data: PostGIS

PostgreSQL with PostGIS for all vector geospatial data.

```
```sql
-- Spatial table with H3 index column
CREATE TABLE observations (
    id BIGSERIAL PRIMARY KEY,
    geom GEOMETRY(Point, 4326) NOT NULL,
    h3_cell VARCHAR(16) NOT NULL,
    value DOUBLE PRECISION,
    timestamp TIMESTAMPTZ NOT NULL,
    metadata JSONB
);

CREATE INDEX idx_observations_geom ON observations USING GIST (geom);
CREATE INDEX idx_observations_h3 ON observations (h3_cell);
CREATE INDEX idx_observations_time ON observations (timestamp);
```

PostGIS is the right choice when:
- You need spatial joins, intersection queries, or buffer operations
- Data is relational (observations linked to stations, sensors, regions)
- You need ACID transactions for data integrity

### Raster Data: Cloud Optimized GeoTIFF

Store rasters as Cloud Optimized GeoTIFFs (COGs) in object storage (S3, GCS, Azure Blob).

Benefits:
- HTTP range requests -- read only the tiles you need
- Internal tiling and overviews -- zoom-level-appropriate data
- No specialized raster database needed

```
```python
import rasterio

# Read a COG from cloud storage -- only fetches required bytes
with rasterio.open("s3://bucket/dem_cog.tif") as src:
    window = rasterio.windows.from_bounds(
        -122.5, 37.5, -122.0, 38.0, src.transform
    )
    data = src.read(1, window=window)
```

### Cache: Redis

Use Redis for:
- Tile cache (rendered map tiles)
- Session data
- Rate limiting counters
- Frequently accessed H3 cell aggregations

```
```python
import redis
import json

r = redis.Redis(host="redis", port=6379, db=0)

def get_cached_cell_stats(cell: str) -> dict:
    cached = r.get(f"cell_stats:{cell}")
    if cached:
        return json.loads(cached)
    return None

def set_cached_cell_stats(cell: str, stats: dict, ttl_seconds: int = 300):
    r.setex(f"cell_stats:{cell}", ttl_seconds, json.dumps(stats))
```

## CDN for Tile Serving

Map tiles are the highest-traffic resource in most geospatial applications. Serve them through a CDN.

**Architecture:**

```
Browser --> CDN (CloudFront/Cloudflare) --> Tile Server --> PostGIS
                   |
            (cache hit: serve directly)
```

**Tile URL pattern:**

```
https://tiles.example.com/v1/{layer}/{z}/{x}/{y}.mvt
```

Set long cache TTLs for tiles that change infrequently (basemaps, administrative boundaries). Use short TTLs or cache invalidation for dynamic layers (sensor data, real-time alerts).

## Observability Stack

### Metrics (Prometheus + Grafana)

```
```python
from prometheus_client import Counter, Histogram, start_http_server

REQUEST_COUNT = Counter(
    "geoinfer_requests_total",
    "Total API requests",
    ["module", "endpoint", "status"],
)

REQUEST_LATENCY = Histogram(
    "geoinfer_request_duration_seconds",
    "Request latency in seconds",
    ["module", "endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

# Key dashboards:
# 1. Request rate and error rate per module
# 2. GP model fitting latency (p50, p95, p99)
# 3. H3 cell processing throughput
# 4. Memory usage per worker
# 5. PostGIS query latency
```

### Logs (Structured JSON)

```
```python
import logging
import json
from datetime import datetime, timezone

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "module": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "h3_cell"):
            log_entry["h3_cell"] = record.h3_cell
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)
```

### Traces (OpenTelemetry)

```
```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider

provider = TracerProvider()
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("geo_infer")

def analyze_region(cell: str):
    with tracer.start_as_current_span("analyze_region") as span:
        span.set_attribute("h3.cell", cell)
        span.set_attribute("h3.resolution", len(cell))
        # ... analysis logic
```

## GEO-INFER-OPS Monitoring

GEO-INFER-OPS provides the operations layer for all modules:

- Health checks for each module
- Resource utilization tracking
- Alerting on anomalous behavior
- Deployment management

## Disaster Recovery

### Database Backup Strategy

| Component | Backup Method | Frequency | Retention |
|-----------|--------------|-----------|-----------|
| PostGIS | pg_dump + WAL archiving | Continuous | 30 days |
| Redis | RDB snapshots | Every 15 min | 7 days |
| COG rasters | Object storage versioning | On write | 90 days |
| Configuration | Git-tracked | On change | Permanent |

### Recovery Time Objectives

- **API availability**: < 5 minutes (failover to standby)
- **Data recovery**: < 1 hour (restore from backup)
- **Full rebuild**: < 4 hours (infrastructure as code)

### Multi-Region Deployment

For global applications:

1. Deploy PostGIS read replicas in each region
2. Use CDN for tile serving with regional edge caches
3. Route API traffic to nearest region via DNS
4. Replicate object storage cross-region

## Blue-Green Deployments

Geospatial services have long-running connections (WebSocket tile streams, large query results). Blue-green deployment avoids dropping these connections.

```
                    +-------------------+
                    |   Load Balancer   |
                    +---------+---------+
                              |
                +-------------+-------------+
                |                           |
        +-------+-------+          +-------+-------+
        | Blue (current)|          | Green (new)   |
        | API v1.2.0    |          | API v1.3.0    |
        | SPACE v2.1.0  |          | SPACE v2.2.0  |
        +---------------+          +---------------+
```

**Deployment steps:**

1. Deploy new version to green environment
2. Run smoke tests against green
3. Gradually shift traffic (10% -> 50% -> 100%)
4. Monitor error rates during shift
5. If errors spike, route all traffic back to blue
6. After validation, decommission blue

### Database Migration

Schema changes require care with blue-green:

1. Make backward-compatible schema changes first (add columns, never drop)
2. Deploy green with code that handles both old and new schema
3. After cutover, run migration to clean up deprecated columns

## See Also

- [Scaling Guide](scaling_guide.md) -- when to scale and how
- [Performance Optimization](performance_optimization.md) -- single-service optimization
- [Troubleshooting](../support/troubleshooting.md) -- production debugging
