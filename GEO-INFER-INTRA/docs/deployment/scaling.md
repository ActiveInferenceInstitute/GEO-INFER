# Scaling GEO-INFER

This document covers strategies for scaling GEO-INFER from single-machine development to distributed production workloads handling large geospatial datasets.

## Horizontal vs Vertical Scaling

Geospatial workloads vary widely. Raster processing is typically memory-bound and benefits from vertical scaling (more RAM per node). Vector analysis and H3 aggregation are CPU-bound and parallelize well across horizontal nodes.

| Workload Type | Bottleneck | Scaling Strategy |
|---------------|------------|------------------|
| Raster processing (DEM, satellite imagery) | Memory, I/O | Vertical: larger instances with more RAM |
| Vector analysis (spatial joins, buffering) | CPU | Horizontal: more workers |
| H3 aggregation across large regions | CPU | Horizontal: partition by H3 cell |
| Bayesian model fitting (MCMC sampling) | CPU | Horizontal: parallel chains |
| Real-time sensor ingestion | I/O, throughput | Horizontal: Kafka partitions |
| API request serving | CPU, connections | Horizontal: load-balanced instances |

## Distributed Processing

### Dask Integration

Dask extends NumPy and Pandas to out-of-core and distributed computation. GEO-INFER-MATH and GEO-INFER-SPACE operations can run on Dask clusters.

```python
import dask.dataframe as dd
import dask_geopandas
from dask.distributed import Client

# Connect to a Dask cluster
client = Client("tcp://scheduler:8786")

# Load a large GeoParquet dataset as a Dask GeoDataFrame
dgdf = dask_geopandas.read_parquet(
    "s3://geo-infer-data/parcels/*.parquet",
    npartitions=64,
)

# Spatial operation distributed across workers
buffered = dgdf.buffer(0.001)

# Compute H3 indices in parallel
def assign_h3(partition):
    import h3
    partition["h3_cell"] = partition.geometry.apply(
        lambda geom: h3.latlng_to_cell(geom.centroid.y, geom.centroid.x, res=7)
    )
    return partition

dgdf = dgdf.map_partitions(assign_h3)

# Aggregate by H3 cell
result = dgdf.groupby("h3_cell").agg({"area_sqm": "sum", "value": "mean"}).compute()
```

### Ray Integration

Ray provides distributed computing with lower overhead than Dask for certain workloads, particularly when running many independent tasks (hyperparameter tuning, Monte Carlo simulations).

```python
import ray
import numpy as np

ray.init(address="ray://cluster:10001")

@ray.remote
def run_mcmc_chain(
    chain_id: int,
    observations: np.ndarray,
    num_samples: int,
) -> np.ndarray:
    """Run a single MCMC chain for Bayesian spatial model."""
    from geo_infer_bayes.core.samplers import MetropolisHastings

    sampler = MetropolisHastings(seed=chain_id)
    samples = sampler.sample(
        observations=observations,
        num_samples=num_samples,
        burn_in=num_samples // 4,
    )
    return samples

# Run 8 MCMC chains in parallel across the Ray cluster
observations = np.load("spatial_observations.npy")
futures = [
    run_mcmc_chain.remote(i, observations, num_samples=10000)
    for i in range(8)
]
all_chains = ray.get(futures)
combined_samples = np.concatenate(all_chains, axis=0)
```

## H3 Grid Partitioning

H3 hexagonal grids provide a natural partitioning scheme for parallel spatial processing. The hierarchical structure means you can partition at a coarse resolution and process at a finer one.

```python
import h3

def partition_region(
    polygon_geojson: dict,
    partition_resolution: int = 3,
    processing_resolution: int = 7,
) -> dict[str, list[str]]:
    """Partition a region into coarse H3 cells, each containing finer cells."""
    coarse_cells = h3.geo_to_cells(polygon_geojson, res=partition_resolution)
    partitions = {}
    for coarse_cell in coarse_cells:
        fine_cells = h3.cell_to_children(coarse_cell, processing_resolution)
        partitions[coarse_cell] = list(fine_cells)
    return partitions

# Each partition can be processed by a different worker
partitions = partition_region(region_boundary, partition_resolution=3, processing_resolution=7)
print(f"{len(partitions)} partitions, ~{sum(len(v) for v in partitions.values())} total cells")
```

Distribute partitions across Dask workers:

```python
import dask

@dask.delayed
def process_partition(partition_cells: list[str], sensor_data: dict) -> dict:
    """Process a single H3 partition."""
    results = {}
    for cell in partition_cells:
        if cell in sensor_data:
            results[cell] = compute_statistics(sensor_data[cell])
    return results

# Submit all partitions for parallel processing
delayed_results = [
    process_partition(cells, sensor_data)
    for cells in partitions.values()
]
all_results = dask.compute(*delayed_results)
```

## Database Scaling

### Read Replicas

For read-heavy workloads (which most spatial analysis pipelines are), use PostgreSQL streaming replication to distribute reads.

```python
from sqlalchemy import create_engine

# Primary: handles writes
primary_engine = create_engine(
    "postgresql+psycopg2://user:pass@primary-db:5432/geo_infer",
    pool_size=10,
)

# Replicas: handle reads
replica_engines = [
    create_engine(
        f"postgresql+psycopg2://user:pass@replica-{i}:5432/geo_infer",
        pool_size=20,
    )
    for i in range(3)
]

import random

def get_read_engine():
    """Round-robin across read replicas."""
    return random.choice(replica_engines)

def get_write_engine():
    return primary_engine
```

### Connection Pooling with PgBouncer

PgBouncer sits between the application and PostgreSQL, multiplexing many application connections onto fewer database connections.

```ini
# pgbouncer.ini
[databases]
geo_infer = host=primary-db port=5432 dbname=geo_infer

[pgbouncer]
listen_port = 6432
listen_addr = 0.0.0.0
pool_mode = transaction
max_client_conn = 400
default_pool_size = 30
reserve_pool_size = 5
```

### Spatial Index Tuning

PostGIS spatial queries scale with proper indexing:

```sql
-- GiST index for geometry columns
CREATE INDEX idx_parcels_geom ON parcels USING GIST (geom);

-- BRIN index for large, spatially-ordered tables
CREATE INDEX idx_sensors_geom_brin ON sensor_readings USING BRIN (geom);

-- Partial index for frequently filtered subsets
CREATE INDEX idx_active_parcels_geom ON parcels USING GIST (geom)
    WHERE status = 'active';

-- Cluster the table on the spatial index for sequential scan performance
CLUSTER parcels USING idx_parcels_geom;
```

## Caching Spatial Query Results

Spatial queries that hit PostGIS or compute H3 aggregations can be cached in Redis to avoid repeated computation.

```python
import redis
import json
import hashlib

cache = redis.Redis(host="localhost", port=6379, db=0)
CACHE_TTL_SECONDS = 3600

def cache_key(query: str, params: dict) -> str:
    """Generate a deterministic cache key from query + parameters."""
    raw = f"{query}:{json.dumps(params, sort_keys=True)}"
    return f"geo:query:{hashlib.sha256(raw.encode()).hexdigest()}"

def cached_spatial_query(query: str, params: dict, engine) -> dict:
    """Execute a spatial query with Redis caching."""
    key = cache_key(query, params)
    cached = cache.get(key)
    if cached is not None:
        return json.loads(cached)

    import geopandas as gpd
    gdf = gpd.read_postgis(query, engine, params=params, geom_col="geom")
    result = json.loads(gdf.to_json())
    cache.setex(key, CACHE_TTL_SECONDS, json.dumps(result))
    return result
```

For tile-based caching (common in web map applications), cache at the tile coordinate level:

```python
def tile_cache_key(layer: str, z: int, x: int, y: int) -> str:
    return f"tile:{layer}:{z}:{x}:{y}"
```

## Memory Management for Large Rasters

Satellite imagery and high-resolution DEMs can exceed available RAM. Use windowed reading and chunked processing.

```python
import rasterio
import numpy as np
from rasterio.windows import Window

def process_raster_in_chunks(
    raster_path: str,
    chunk_height: int = 512,
    chunk_width: int = 512,
) -> np.ndarray:
    """Process a large raster in memory-efficient chunks."""
    with rasterio.open(raster_path) as src:
        result = np.zeros((src.height, src.width), dtype=np.float32)

        for row_start in range(0, src.height, chunk_height):
            for col_start in range(0, src.width, chunk_width):
                window = Window(
                    col_off=col_start,
                    row_off=row_start,
                    width=min(chunk_width, src.width - col_start),
                    height=min(chunk_height, src.height - row_start),
                )
                chunk = src.read(1, window=window).astype(np.float32)

                # Apply per-chunk computation
                processed = compute_ndvi(chunk)

                result[
                    row_start : row_start + window.height,
                    col_start : col_start + window.width,
                ] = processed

    return result
```

For Cloud-Optimized GeoTIFFs (COGs), use HTTP range requests to read only the needed tiles:

```python
with rasterio.open("https://storage.example.com/cog/landcover.tif") as src:
    # Only fetches the tiles covering this window
    window = rasterio.windows.from_bounds(
        -122.5, 47.5, -122.0, 47.8, src.transform
    )
    data = src.read(1, window=window)
```

## Kubernetes Deployment

### Deployment Manifest

```yaml
# k8s/geo-infer-api.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: geo-infer-api
  namespace: geo-infer
spec:
  replicas: 3
  selector:
    matchLabels:
      app: geo-infer-api
  template:
    metadata:
      labels:
        app: geo-infer-api
    spec:
      containers:
        - name: api
          image: geo-infer/api:latest
          ports:
            - containerPort: 8000
          resources:
            requests:
              cpu: "500m"
              memory: "1Gi"
            limits:
              cpu: "2000m"
              memory: "4Gi"
          env:
            - name: GEO_INFER_DB_HOST
              value: "postgis-service"
            - name: GEO_INFER_DB_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: geo-infer-secrets
                  key: db-password
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 30
          readinessProbe:
            httpGet:
              path: /ready
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 10
```

### Horizontal Pod Autoscaler

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: geo-infer-api-hpa
  namespace: geo-infer
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: geo-infer-api
  minReplicas: 3
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

### Worker Deployment for Batch Processing

```yaml
# k8s/geo-infer-worker.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: geo-infer-worker
  namespace: geo-infer
spec:
  replicas: 5
  selector:
    matchLabels:
      app: geo-infer-worker
  template:
    spec:
      containers:
        - name: worker
          image: geo-infer/worker:latest
          resources:
            requests:
              cpu: "2000m"
              memory: "8Gi"
            limits:
              cpu: "4000m"
              memory: "16Gi"
          env:
            - name: DASK_SCHEDULER
              value: "tcp://dask-scheduler:8786"
```

## Load Balancing the API Layer

### NGINX Configuration

```nginx
upstream geo_infer_api {
    least_conn;
    server api-1:8000;
    server api-2:8000;
    server api-3:8000;
}

server {
    listen 443 ssl;
    server_name api.geo-infer.example.com;

    ssl_certificate /etc/ssl/certs/geo-infer.pem;
    ssl_certificate_key /etc/ssl/private/geo-infer.key;

    location /api/ {
        proxy_pass http://geo_infer_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_connect_timeout 10s;
        proxy_read_timeout 120s;  # spatial queries can be slow
    }

    location /api/health {
        proxy_pass http://geo_infer_api;
        proxy_read_timeout 5s;
    }
}
```

For Kubernetes, use an Ingress controller instead:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: geo-infer-ingress
  annotations:
    nginx.ingress.kubernetes.io/proxy-read-timeout: "120"
spec:
  rules:
    - host: api.geo-infer.example.com
      http:
        paths:
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: geo-infer-api
                port:
                  number: 8000
```

## Performance Benchmarks

Expected throughput for common operations on a 4-core, 16 GB RAM instance:

| Operation | Dataset Size | Time | Notes |
|-----------|-------------|------|-------|
| H3 polyfill, resolution 7 | 10,000 km2 region | ~2s | Single-threaded |
| Spatial join (point-in-polygon) | 1M points, 50K polygons | ~15s | With spatial index |
| GeoParquet read | 10M rows, 500 MB | ~8s | Columnar read |
| Gaussian Process fit | 5,000 observations | ~10s | Cholesky decomposition |
| MCMC sampling (4 chains) | 10,000 samples each | ~60s | Parallel chains |
| Raster NDVI computation | 10,000 x 10,000 pixels | ~5s | NumPy vectorized |
| PostGIS bounding box query | 100M row table | ~200ms | GiST indexed |

These numbers scale roughly linearly. Doubling the dataset doubles the time, unless the operation is already parallelized.

## Monitoring Metrics

Track these metrics to identify bottlenecks before they cause outages.

### Application Metrics

| Metric | What It Tells You | Alert Threshold |
|--------|-------------------|-----------------|
| Request latency (p50, p95, p99) | API responsiveness | p99 > 5s |
| Request rate | Traffic volume | Sustained > 80% capacity |
| Error rate (4xx, 5xx) | Failure frequency | > 1% of requests |
| Active connections | Concurrent load | > 80% of pool size |

### Infrastructure Metrics

| Metric | What It Tells You | Alert Threshold |
|--------|-------------------|-----------------|
| CPU utilization | Processing capacity | Sustained > 80% |
| Memory usage | RAM pressure | > 85% |
| Disk I/O wait | Storage bottleneck | > 20% |
| Network throughput | Bandwidth saturation | > 70% of capacity |

### Database Metrics

| Metric | What It Tells You | Alert Threshold |
|--------|-------------------|-----------------|
| Active connections | Connection pool pressure | > 80% of max |
| Query duration (p95) | Slow queries | > 1s |
| Replication lag | Read replica staleness | > 10s |
| Cache hit ratio | Index effectiveness | < 95% |

### Monitoring Stack

Use Prometheus for metrics collection and Grafana for dashboards:

```python
from prometheus_client import Counter, Histogram, start_http_server

REQUEST_COUNT = Counter(
    "geo_infer_requests_total",
    "Total request count",
    ["method", "endpoint", "status"],
)

REQUEST_LATENCY = Histogram(
    "geo_infer_request_duration_seconds",
    "Request latency in seconds",
    ["method", "endpoint"],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0],
)

# Expose metrics on port 9090
start_http_server(9090)
```
