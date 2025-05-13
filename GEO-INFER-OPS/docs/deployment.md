# GEO-INFER-OPS Deployment Guide

This document provides instructions for deploying the GEO-INFER-OPS module in various environments.

## Development Deployment

For local development, you can run the module directly:

```bash
# Install dependencies
pip install -e .

# Run the module
python -m geo_infer_ops.app
```

## Docker Deployment

Build and run using Docker:

```bash
# Build the Docker image
docker build -t geo-infer-ops:latest .

# Run the container
docker run -p 8000:8000 -p 9090:9090 -v $(pwd)/config:/app/config geo-infer-ops:latest
```

## Docker Compose Deployment

For a complete local environment with monitoring:

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

## Kubernetes Deployment

Deploy to a Kubernetes cluster:

```bash
# Apply the Kubernetes manifests
kubectl apply -f deployment/kubernetes/

# Check the deployment status
kubectl get pods -n geo-infer

# Port forward to access the API locally
kubectl port-forward svc/geo-infer-ops 8000:8000 -n geo-infer
```

## Environment Variables

Configure the module using environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| GEO_INFER_OPS_CONFIG | Path to configuration file | config/local.yaml |
| GEO_INFER_OPS_LOGGING_LEVEL | Log level | INFO |
| GEO_INFER_OPS_SERVICE_PORT | Service port | 8000 |
| GEO_INFER_OPS_MONITORING_ENABLED | Enable Prometheus metrics | true |

## Health Checks

The service exposes a health endpoint at `/health` that returns HTTP 200 when the service is healthy.

## Monitoring

Prometheus metrics are available at `/metrics` and can be visualized in Grafana.
The docker-compose setup includes pre-configured Prometheus and Grafana instances. 